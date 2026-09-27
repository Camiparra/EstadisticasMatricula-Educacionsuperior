"""Carga y limpieza del conjunto de datos de matrícula (MEN - SNIES).

Todas las dimensiones deben leer los datos desde este módulo para trabajar
sobre la misma versión limpia del archivo:

    from components.datos import cargar_datos, cargar_datos_largo

Problemas del CSV original que se corrigen aquí:

1. Las cifras usan punto como separador de miles ("63.098") y algunas traen
   decimales con coma ("129.516,5").
2. El archivo contiene dos bloques repetidos: casi todas las filas de 2005 a
   2020 aparecen dos veces, a veces con el nombre del municipio escrito
   distinto ("BOGOTÁ D.C." / "BOGOTA D.C."). Se eliminan las filas idénticas
   en año, código de municipio y cifras.
3. Los códigos DANE vienen sin cero a la izquierda en algunas filas ("5" y
   "05" para Antioquia) y la columna "Nombre del Departamento" trae el código,
   no el nombre.
4. Hay filas con "-" como departamento y municipio ("NO IDENTIFICADO").

Algunos municipios tienen dos filas distintas en el mismo año; no son
duplicados (sus cifras difieren), así que se conservan y deben sumarse al
agrupar.
"""

from functools import cache
from pathlib import Path

import pandas as pd

RUTA_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv"
)

# Columna original -> nombre usado en el código.
COLUMNAS = {
    "AÑO": "anio",
    "Código delDepartamento": "cod_departamento",
    "Código delMunicipio": "cod_municipio",
    "Nombre del Municipio": "municipio",
    "TECNICA PROFESIONAL": "tecnica_profesional",
    "TECNOLOGICA": "tecnologica",
    "UNIVERSITARIA": "universitaria",
    "ESPECIALIZACION": "especializacion",
    "MAESTRIA": "maestria",
    "DOCTORADO": "doctorado",
    "IES CON OFERTA": "ies_con_oferta",
}

# Columna de cada nivel de formación -> nombre legible (orden de menor a mayor nivel).
NIVELES = {
    "tecnica_profesional": "Técnica profesional",
    "tecnologica": "Tecnológica",
    "universitaria": "Universitaria",
    "especializacion": "Especialización",
    "maestria": "Maestría",
    "doctorado": "Doctorado",
}

# Códigos DANE de departamento (DIVIPOLA).
DEPARTAMENTOS = {
    "05": "Antioquia",
    "08": "Atlántico",
    "11": "Bogotá D.C.",
    "13": "Bolívar",
    "15": "Boyacá",
    "17": "Caldas",
    "18": "Caquetá",
    "19": "Cauca",
    "20": "Cesar",
    "23": "Córdoba",
    "25": "Cundinamarca",
    "27": "Chocó",
    "41": "Huila",
    "44": "La Guajira",
    "47": "Magdalena",
    "50": "Meta",
    "52": "Nariño",
    "54": "Norte de Santander",
    "63": "Quindío",
    "66": "Risaralda",
    "68": "Santander",
    "70": "Sucre",
    "73": "Tolima",
    "76": "Valle del Cauca",
    "81": "Arauca",
    "85": "Casanare",
    "86": "Putumayo",
    "88": "San Andrés, Providencia y Santa Catalina",
    "91": "Amazonas",
    "94": "Guainía",
    "95": "Guaviare",
    "97": "Vaupés",
    "99": "Vichada",
}

SIN_IDENTIFICAR = "No identificado"


def _a_numero(serie):
    """Convierte "129.516,5" -> 129516.5 (miles con punto, decimales con coma)."""
    texto = serie.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto)


def _normalizar_codigo(serie, largo):
    """Rellena con ceros a la izquierda ("5" -> "05"); "-" pasa a vacío."""
    return serie.where(serie != "-").str.zfill(largo)


@cache
def _leer_csv():
    return pd.read_csv(RUTA_CSV, dtype=str)


@cache
def cargar_datos():
    """Datos limpios en formato ancho: una fila por municipio y año.

    Columnas: anio, cod_departamento, departamento, cod_municipio, municipio,
    una columna por nivel de formación (ver NIVELES), ies_con_oferta y
    matricula_total.

    El resultado se guarda en caché: no modificar el DataFrame devuelto, usar
    ``.copy()`` si se necesita transformarlo.
    """
    df = _leer_csv().rename(columns=COLUMNAS)[list(COLUMNAS.values())]

    df["anio"] = df["anio"].astype(int)
    for columna in [*NIVELES, "ies_con_oferta"]:
        df[columna] = _a_numero(df[columna])

    df["cod_departamento"] = _normalizar_codigo(df["cod_departamento"], 2)
    df["cod_municipio"] = _normalizar_codigo(df["cod_municipio"], 5)

    # Quitar el bloque repetido: misma fila salvo por la escritura del nombre.
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "municipio"])

    # Un solo nombre por municipio (el más frecuente) para agrupar sin variantes.
    nombres = df.groupby("cod_municipio")["municipio"].agg(lambda s: s.mode().iloc[0])
    df["municipio"] = df["cod_municipio"].map(nombres).fillna(SIN_IDENTIFICAR)

    df["departamento"] = df["cod_departamento"].map(DEPARTAMENTOS).fillna(SIN_IDENTIFICAR)
    df["matricula_total"] = df[list(NIVELES)].sum(axis=1)

    orden = ["anio", "cod_departamento", "departamento", "cod_municipio", "municipio",
             *NIVELES, "ies_con_oferta", "matricula_total"]
    return df[orden].sort_values(["anio", "cod_municipio"]).reset_index(drop=True)


@cache
def cargar_datos_largo():
    """Datos limpios en formato largo: una fila por municipio, año y nivel.

    Columnas: anio, cod_departamento, departamento, cod_municipio, municipio,
    ies_con_oferta, nivel_formacion (nombre legible) y matriculados.
    """
    df = cargar_datos()
    largo = df.melt(
        id_vars=["anio", "cod_departamento", "departamento", "cod_municipio",
                 "municipio", "ies_con_oferta"],
        value_vars=list(NIVELES),
        var_name="nivel_formacion",
        value_name="matriculados",
    )
    largo["nivel_formacion"] = largo["nivel_formacion"].map(NIVELES)
    return largo


@cache
def resumen_general():
    """Cifras generales del conjunto de datos para la página de inicio."""
    crudo = _leer_csv()
    df = cargar_datos()
    serie = df.groupby("anio")["matricula_total"].sum().round().astype(int)

    primero, ultimo = serie.iloc[0], serie.iloc[-1]
    return {
        "filas_originales": len(crudo),
        "filas_duplicadas": len(crudo) - len(df),
        "registros": len(df),
        "anio_inicial": int(serie.index[0]),
        "anio_final": int(serie.index[-1]),
        "anios": len(serie),
        "municipios": df.loc[df["cod_municipio"].notna(), "cod_municipio"].nunique(),
        "departamentos": df.loc[df["cod_departamento"].notna(), "cod_departamento"].nunique(),
        "niveles": len(NIVELES),
        "matricula_final": int(ultimo),
        "crecimiento_pct": float((ultimo - primero) / primero * 100),
        "serie": [{"anio": int(a), "matricula": int(m)} for a, m in serie.items()],
    }
