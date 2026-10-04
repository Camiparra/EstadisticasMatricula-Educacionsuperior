"""Dimensión territorial (Integrante 2): cálculos, gráficas y textos del tablero.

Todo sale del conjunto de datos limpio (``components.datos``): nada se escribe
a mano en la plantilla. Así, cada cifra que ve la persona en la página sale del
mismo cálculo que explicamos en ``docs/territorial/indicadores.md``.

Qué hay aquí:

* ``opciones_territoriales()``      -> años y departamentos para los filtros.
* ``tablero_territorial(a, d)``     -> indicadores, gráficas, tabla, lectura y
                                       «cómo se calculó» para un año y un
                                       departamento (o «Todos»).
* ``conocimientos_territoriales()`` -> los 3 conocimientos evidentes, la
                                       decisión y la limitación, con cifras
                                       calculadas del último año.
* ``generar_evidencias()``          -> guarda gráficas (PNG) y tablas (CSV) en
                                       ``docs/territorial/evidencias/``.

Para generar las evidencias desde la raíz del proyecto:

    python -m components.territorial

Decisiones de método (las mismas del documento de la dimensión):

* El análisis es de UN año a la vez (por defecto el último). No se suma el
  periodo completo porque la matrícula acumulada repite estudiantes y porque
  el número de municipios con datos cambia mucho entre años.
* Se excluyen las filas «No identificado» (sin departamento ni municipio).
* Los municipios se agrupan por CÓDIGO, no por nombre, y se suman sus filas
  del mismo año (algunos municipios tienen más de una fila por año).
"""

import base64
import unicodedata
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import matplotlib
import pandas as pd
from matplotlib.figure import Figure

from .datos import NIVELES, SIN_IDENTIFICAR, cargar_datos
from .sitio import buscar_dimension

TODOS = "Todos"
COLOR = buscar_dimension("territorial")[0]["color"]
GRIS = "#6c757d"
GRIS_CLARO = "#b8c2cc"

TOP = 10                      # cuántos territorios se muestran en los rankings
UMBRAL_MUNICIPIO_PEQUENO = 500  # «municipio pequeño»: menos de 500 matriculados
UMBRAL_DEPTO_GRANDE = 50_000    # «departamento grande»: más de 50.000 matriculados
POSGRADO = ["especializacion", "maestria", "doctorado"]
N_MENORES = 5                   # cuántos departamentos «más pequeños» se muestran

# Rangos de matrícula para clasificar municipios (límite inferior incluido).
# Los municipios no van en un «top 5 de menores» porque decenas empatan con
# 1 matriculado y el orden entre ellos sería arbitrario.
RANGOS_MUNICIPIO = [
    ("Menos de 10", 0, 10),
    ("10 a 99", 10, 100),
    ("100 a 499", 100, 500),
    ("500 a 999", 500, 1_000),
    ("1.000 a 9.999", 1_000, 10_000),
    ("10.000 o más", 10_000, float("inf")),
]

RUTA_EVIDENCIAS = Path(__file__).resolve().parent.parent / "docs" / "territorial" / "evidencias"

# De menor a mayor nivel de formación (mismo orden que NIVELES).
COLORES_NIVEL = ["#9be3d3", "#4fcfb4", "#18bc9c", "#12917a", "#0d6654", "#083d33"]
TEXTO_CLARO_SOBRE = {0, 1}    # segmentos claros: el número va en oscuro

NOMBRES_CORTOS = {
    "San Andrés, Providencia y Santa Catalina": "San Andrés y Providencia",
}
_MINUSCULAS = {"de", "del", "la", "las", "los", "el", "y", "e"}

# temporal.py cambia matplotlib.rcParams de forma global (por ejemplo activa la
# cuadrícula), así que aquí fijamos explícitamente lo que NO queremos heredar.
ESTILO = {
    "axes.grid": False,
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": GRIS,
    "axes.labelcolor": GRIS,
    "text.color": GRIS,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
}


# --------------------------------------------------------------------------
# Formato de textos y números (formato colombiano: 1.234,5)
# --------------------------------------------------------------------------

def _miles(valor, decimales=0):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _pct(valor, decimales=1):
    # Espacio de no separación: el «%» nunca queda solo al cortar el renglón.
    return f"{valor:.{decimales}f}\u00a0%".replace(".", ",")


def _nombre(texto):
    """«SAN JOSÉ DE CÚCUTA» -> «San José de Cúcuta»; «BOGOTÁ D.C.» -> «Bogotá D.C.»"""
    palabras = []
    for i, palabra in enumerate(str(texto).lower().split()):
        if "." in palabra:
            palabras.append(palabra.upper())
        elif i > 0 and palabra in _MINUSCULAS:
            palabras.append(palabra)
        else:
            palabras.append(palabra.capitalize())
    return " ".join(palabras)


def _corto(departamento):
    return NOMBRES_CORTOS.get(departamento, departamento)


def _sin_tildes(texto):
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode()


# --------------------------------------------------------------------------
# Cálculos sobre los datos
# --------------------------------------------------------------------------

def _por_departamento(df):
    serie = df.groupby("departamento")["matricula_total"].sum()
    return serie[serie > 0].sort_values(ascending=False, kind="stable")


def _por_municipio(df):
    """Matrícula por municipio (índice: código y nombre), de mayor a menor."""
    serie = df.groupby(["cod_municipio", "municipio"])["matricula_total"].sum()
    return serie[serie > 0].sort_values(ascending=False, kind="stable")


def _perfil(df):
    """Porcentaje de cada nivel de formación dentro de la matrícula del grupo."""
    suma = df[list(NIVELES)].sum()
    return suma / suma.sum() * 100 if suma.sum() else suma


def _posgrado(perfil):
    return float(perfil[POSGRADO].sum())


def _rangos_municipios(por_muni):
    """Cuántos municipios hay en cada rango de matrícula (lista de dicts)."""
    total = len(por_muni)
    filas = []
    for nombre, minimo, maximo in RANGOS_MUNICIPIO:
        n = int(((por_muni >= minimo) & (por_muni < maximo)).sum())
        filas.append({"rango": nombre, "municipios": n,
                      "pct": n / total * 100 if total else 0.0,
                      "pequeno": maximo <= UMBRAL_MUNICIPIO_PEQUENO})
    return filas


def _lista(nombres):
    """['a', 'b', 'c'] -> 'a, b y c'"""
    nombres = list(nombres)
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


@lru_cache
def opciones_territoriales():
    """Años y departamentos disponibles, para llenar los filtros."""
    df = cargar_datos()
    anios = sorted(int(a) for a in df["anio"].unique())
    departamentos = sorted(
        (d for d in df["departamento"].unique() if d != SIN_IDENTIFICAR),
        key=_sin_tildes,
    )
    return {"anios": anios, "anio_final": anios[-1], "departamentos": [TODOS, *departamentos]}


# --------------------------------------------------------------------------
# Gráficas (matplotlib sin pyplot: seguras para varias solicitudes a la vez)
# --------------------------------------------------------------------------

def _a_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", transparent=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _a_archivo(fig, ruta):
    fig.savefig(ruta, format="png", dpi=160, bbox_inches="tight",
                facecolor="white", transparent=False)


def _limpiar_ejes(ax, quitar_x=True):
    for lado in ("top", "right", "bottom" if quitar_x else "left"):
        ax.spines[lado].set_visible(False)
    if quitar_x:
        ax.set_xticks([])
    ax.tick_params(length=0)


def _figura_vacia(mensaje, titulo=None):
    with matplotlib.rc_context(ESTILO):
        fig = Figure(figsize=(6.4, 2.0))
        ax = fig.subplots()
        ax.text(0.5, 0.5, mensaje, ha="center", va="center", fontsize=11)
        ax.set_axis_off()
        if titulo:
            ax.set_title(titulo, loc="left", fontweight="bold")
    return fig


def _figura_barras(etiquetas, valores, textos, colores, titulo=None):
    """Barras horizontales con un texto al final de cada barra (de mayor a menor)."""
    with matplotlib.rc_context(ESTILO):
        fig = Figure(figsize=(6.4, 0.34 * len(etiquetas) + 0.9))
        ax = fig.subplots()
        posiciones = list(range(len(etiquetas)))
        ax.barh(posiciones, valores, color=colores, height=0.68)
        ax.set_yticks(posiciones, etiquetas)
        ax.invert_yaxis()
        ax.set_xlim(0, max(valores) * 1.38)
        _limpiar_ejes(ax)
        for y, v, texto in zip(posiciones, valores, textos):
            ax.annotate(texto, (v, y), xytext=(5, 0), textcoords="offset points",
                        va="center", fontsize=8.5)
        if titulo:
            ax.set_title(titulo, loc="left", fontweight="bold")
        fig.tight_layout()
    return fig


def _grafica_departamentos(por_depto, total, seleccion, titulo=None):
    top = list(por_depto.head(TOP).index)
    if seleccion != TODOS and seleccion in por_depto.index and seleccion not in top:
        top.append(seleccion)
    etiquetas, valores, textos, colores = [], [], [], []
    for depto in top:
        puesto = list(por_depto.index).index(depto) + 1
        pct = por_depto[depto] / total * 100
        etiquetas.append(_corto(depto) if puesto <= TOP else f"{_corto(depto)} (puesto {puesto})")
        valores.append(pct)
        textos.append(_pct(pct))
        resaltar = seleccion == TODOS or depto == seleccion
        colores.append(COLOR if resaltar else GRIS_CLARO)
    return _figura_barras(etiquetas, valores, textos, colores, titulo)


def _grafica_municipios(por_muni, total, titulo=None):
    top = por_muni.head(TOP)
    etiquetas = [_nombre(nombre) for (_, nombre) in top.index]
    valores = list(top.values)
    textos = [f"{_miles(v)} ({_pct(v / total * 100)})" for v in valores]
    return _figura_barras(etiquetas, valores, textos, [COLOR] * len(valores), titulo)


def _grafica_perfil(filas, titulo=None):
    """Barras apiladas al 100 %: cada fila es un territorio y cada color, un nivel."""
    with matplotlib.rc_context(ESTILO):
        fig = Figure(figsize=(6.4, 0.55 * len(filas) + 1.5))
        ax = fig.subplots()
        posiciones = list(range(len(filas)))
        acumulado = [0.0] * len(filas)
        for i, (clave, nombre) in enumerate(NIVELES.items()):
            valores = [float(perfil[clave]) for _, perfil in filas]
            ax.barh(posiciones, valores, left=acumulado, height=0.62, label=nombre,
                    color=COLORES_NIVEL[i], edgecolor="white", linewidth=0.6)
            for y, v, inicio in zip(posiciones, valores, acumulado):
                if v >= 5:
                    ax.text(inicio + v / 2, y, f"{v:.0f}".replace(".", ","), ha="center",
                            va="center", fontsize=8,
                            color="#0b3d33" if i in TEXTO_CLARO_SOBRE else "white")
            acumulado = [a + v for a, v in zip(acumulado, valores)]
        ax.set_yticks(posiciones, [etiqueta for etiqueta, _ in filas])
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        _limpiar_ejes(ax)
        ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.02), ncol=3, frameon=False,
                  fontsize=8.5, handlelength=1.1, columnspacing=1.2)
        if titulo:
            ax.set_title(titulo, loc="left", fontweight="bold")
        fig.tight_layout()
    return fig


def _grafica_menores(menores, total, seleccion, rangos, ambito, titulo=None):
    """Dos paneles: los departamentos con menos matrícula y los municipios por rango."""
    with matplotlib.rc_context(ESTILO):
        n_a, n_b = len(menores), len(rangos)
        fig = Figure(figsize=(6.4, 0.3 * (n_a + n_b) + 1.9))
        ax_a, ax_b = fig.subplots(2, 1, gridspec_kw={"height_ratios": [n_a, n_b], "hspace": 0.32})

        # Panel A: los N departamentos con menos matrícula (nacional)
        nombres = [_corto(d) for d in menores.index]
        valores = list(menores.values)
        esta = seleccion in menores.index
        colores = [COLOR if (not esta or d == seleccion) else GRIS_CLARO for d in menores.index]
        posiciones = list(range(n_a))
        ax_a.barh(posiciones, valores, color=colores, height=0.66)
        ax_a.set_yticks(posiciones, nombres)
        ax_a.set_xlim(0, max(valores) * 1.35)
        for y, v in zip(posiciones, valores):
            ax_a.annotate(f"{_miles(v)} ({_pct(v / total * 100, 2)})", (v, y), xytext=(5, 0),
                          textcoords="offset points", va="center", fontsize=8.5)
        ax_a.invert_yaxis()
        _limpiar_ejes(ax_a)
        ax_a.set_title(f"Los {n_a} departamentos con menos matrícula del país", loc="left",
                       fontsize=9.5, fontweight="bold")

        # Panel B: cuántos municipios hay en cada rango de matrícula
        etiquetas = [r["rango"] for r in rangos]
        conteos = [r["municipios"] for r in rangos]
        posiciones = list(range(n_b))
        ax_b.barh(posiciones, conteos, height=0.66,
                  color=[COLOR if r["pequeno"] else GRIS_CLARO for r in rangos])
        ax_b.set_yticks(posiciones, etiquetas)
        ax_b.set_xlim(0, max(max(conteos), 1) * 1.38)
        for y, r in zip(posiciones, rangos):
            ax_b.annotate(f"{_miles(r['municipios'])} ({_pct(r['pct'], 0)})",
                          (r["municipios"], y), xytext=(5, 0), textcoords="offset points",
                          va="center", fontsize=8.5)
        ax_b.invert_yaxis()
        _limpiar_ejes(ax_b)
        ax_b.set_title(f"Municipios {ambito} por tamaño (verde: menos de "
                       f"{_miles(UMBRAL_MUNICIPIO_PEQUENO)})", loc="left", fontsize=9.5,
                       fontweight="bold")
        if titulo:
            fig.suptitle(titulo, x=0.01, ha="left", fontweight="bold", fontsize=11)
        fig.subplots_adjust(left=0.30, right=0.97, top=0.88 if titulo else 0.93, bottom=0.03)
    return fig


# --------------------------------------------------------------------------
# Tablero: lo que consume la página según el año y el departamento elegidos
# --------------------------------------------------------------------------

def _normalizar(anio, departamento):
    opciones = opciones_territoriales()
    if anio not in opciones["anios"]:
        anio = opciones["anio_final"]
    if departamento not in opciones["departamentos"]:
        departamento = TODOS
    return anio, departamento


def tablero_territorial(anio=None, departamento=TODOS):
    """Indicadores, gráficas, tabla y textos para el año y departamento elegidos."""
    anio, departamento = _normalizar(anio, departamento)
    return _tablero(anio, departamento)


@lru_cache(maxsize=256)
def _tablero(anio, departamento):
    todo = cargar_datos()
    del_anio = todo[todo["anio"] == anio]
    df = del_anio[del_anio["departamento"] != SIN_IDENTIFICAR]
    excluidos = len(del_anio) - len(df)

    por_depto = _por_departamento(df)
    total_nac = float(por_depto.sum())
    n_deptos = len(por_depto)
    ranking = list(por_depto.index)

    todos = departamento == TODOS
    ambito = df if todos else df[df["departamento"] == departamento]
    por_muni = _por_municipio(ambito)
    total_amb = float(por_muni.sum())
    seleccion = {"anio": anio, "departamento": departamento}
    donde = "el país" if todos else departamento

    base = {
        "seleccion": seleccion,
        "titulo_municipios": ("Los 10 municipios con más matrícula del país" if todos
                              else f"Municipios con más matrícula en {departamento}"),
        "traza": {"variables": VARIABLES_USADAS},
    }

    # ---- Caso sin registros (algunos departamentos no aparecen en ciertos años)
    if total_amb == 0:
        aviso = f"{departamento} no tiene matrícula registrada en {anio}."
        vacia = _a_base64(_figura_vacia("Sin registros para esta selección"))
        base.update({
            "vacio": True,
            "indicadores": {
                "k1": {"valor": "—", "etiqueta": "Participación en el país", "detalle": aviso},
                "k2": {"valor": "—", "etiqueta": "Municipio principal", "detalle": "Sin datos"},
                "k3": {"valor": "0", "etiqueta": "Municipios con matrícula", "detalle": "Sin datos"},
            },
            "reparto": [], "tabla": [], "tabla_menores": [], "tabla_rangos": [], "lectura": aviso,
            "interpretaciones": {"departamentos": aviso, "municipios": aviso, "perfil": aviso,
                                 "menores": aviso},
            "imagenes": {"departamentos": _a_base64(
                _grafica_departamentos(por_depto, total_nac, TODOS)),
                "municipios": vacia, "perfil": vacia, "menores": vacia},
        })
        base["traza"]["pasos"] = [f"Se filtró el año {anio} y el departamento {departamento}: "
                                  "no hay registros con matrícula."]
        return base

    # ---- Cifras municipales dentro del ámbito elegido
    pct_muni = por_muni / total_amb * 100
    acumulado = pct_muni.cumsum()
    n_muni = len(por_muni)
    mediana = float(por_muni.median())
    n_pequenos = int((por_muni < UMBRAL_MUNICIPIO_PEQUENO).sum())
    n_para_80 = min(int((acumulado < 80).sum()) + 1, n_muni)
    top10_pct = float(pct_muni.head(TOP).sum())
    principal = _nombre(por_muni.index[0][1])
    principal_pct = float(pct_muni.iloc[0])
    segundo = _nombre(por_muni.index[1][1]) if n_muni > 1 else None

    # ---- Territorios con menos matrícula
    menores = por_depto.sort_values(kind="stable").head(N_MENORES)      # de menor a mayor
    nombres_menores = [_corto(d) for d in menores.index]
    suma_menores = float(menores.sum())
    pct_menores = suma_menores / total_nac * 100
    rangos = _rangos_municipios(por_muni)
    n_menos_100 = rangos[0]["municipios"] + rangos[1]["municipios"]
    minimo = float(por_muni.min())
    n_en_minimo = int((por_muni == por_muni.min()).sum())
    ambito_txt = "del país" if todos else f"de {_corto(departamento)}"

    # ---- Cifras departamentales
    pct_depto = por_depto / total_nac * 100
    lider, pct_lider = ranking[0], float(pct_depto.iloc[0])
    top5 = float(pct_depto.head(5).sum())
    ultimo, pct_ultimo = ranking[-1], float(pct_depto.iloc[-1])

    perfil_nac, perfil_amb = _perfil(df), _perfil(ambito)
    pos_nac, pos_amb = _posgrado(perfil_nac), _posgrado(perfil_amb)

    # ---- Indicadores
    if todos:
        k1 = {"valor": _pct(pct_lider), "etiqueta": "Participación del departamento líder",
              "detalle": f"{lider}: {_miles(por_depto.iloc[0])} matriculados"}
        k2 = {"valor": _pct(top10_pct), "etiqueta": "Peso de los 10 municipios principales",
              "detalle": f"Entre {_miles(n_muni)} municipios con matrícula"}
    else:
        puesto = ranking.index(departamento) + 1
        pct_dep = float(pct_depto[departamento])
        k1 = {"valor": _pct(pct_dep), "etiqueta": f"Participación de {_corto(departamento)} en el país",
              "detalle": f"Puesto {puesto} de {n_deptos} departamentos"}
        k2 = {"valor": _pct(principal_pct), "etiqueta": f"{principal} dentro del departamento",
              "detalle": ("Único municipio con matrícula del departamento" if n_muni == 1
                          else "Municipio con más matrícula del departamento")}
    k3 = {"valor": _miles(n_muni), "etiqueta": "Municipios con matrícula",
          "detalle": f"Mediana: {_miles(mediana)} matriculados por municipio"}

    # ---- Barra de reparto (los más grandes y «resto»)
    if todos:
        reparto = [{"nombre": _corto(d), "pct": float(p)} for d, p in pct_depto.head(5).items()]
        reparto.append({"nombre": "Resto del país", "pct": 100 - top5, "resto": True})
    else:
        reparto = [{"nombre": _corto(departamento), "pct": float(pct_depto[departamento])},
                   {"nombre": "Resto del país", "pct": 100 - float(pct_depto[departamento]),
                    "resto": True}]

    # ---- Textos de interpretación (cambian con los filtros)
    if todos:
        lectura = (f"En {anio}, {lider} concentra el {_pct(pct_lider)} de la matrícula del país y los "
                   f"cinco primeros departamentos suman {_pct(top5)}. Solo {n_para_80} de los "
                   f"{_miles(n_muni)} municipios con matrícula reúnen el 80 %, y {_miles(n_pequenos)} "
                   f"tienen menos de {_miles(UMBRAL_MUNICIPIO_PEQUENO)} matriculados.")
        i_deptos = (f"{lider} lidera con {_pct(pct_lider)} y los cinco primeros suman {_pct(top5)}. "
                    f"En el otro extremo, {ultimo} tiene apenas {_pct(pct_ultimo, 2)} "
                    f"({_miles(por_depto.iloc[-1])} matriculados).")
        i_muni = (f"Los {min(TOP, n_muni)} municipios principales suman {_pct(top10_pct)} del país. "
                  f"{principal} va primero ({_pct(principal_pct)}) y {segundo} segundo "
                  f"({_pct(float(pct_muni.iloc[1]))}).")
        grandes = list(por_depto.head(5).index)
        pos_grandes = {d: _posgrado(_perfil(df[df["departamento"] == d])) for d in grandes}
        mas = max(pos_grandes, key=pos_grandes.get)
        menos = min(pos_grandes, key=pos_grandes.get)
        i_perfil = (f"En el país, el {_pct(float(perfil_nac['universitaria']), 0)} de la matrícula es universitaria "
                    f"y el {_pct(float(perfil_nac['tecnologica']), 0)} tecnológica; el posgrado pesa "
                    f"{_pct(pos_nac)}. Entre los cinco departamentos más grandes, {mas} tiene más "
                    f"posgrado ({_pct(pos_grandes[mas])}) y {menos} menos ({_pct(pos_grandes[menos])}).")
        filas_perfil = [("Nacional", perfil_nac)] + [
            (_corto(d), _perfil(df[df["departamento"] == d])) for d in grandes]
    else:
        puesto = ranking.index(departamento) + 1
        pct_dep = float(pct_depto[departamento])
        if puesto == 1:
            i_deptos = (f"{departamento} es el departamento con más matrícula ({_pct(pct_dep)} del país); "
                        f"le sigue {ranking[1]} con {_pct(float(pct_depto.iloc[1]))}.")
        else:
            i_deptos = (f"{departamento} ocupa el puesto {puesto} de {n_deptos} con {_pct(pct_dep)} de la "
                        f"matrícula del país; el líder, {lider}, tiene {_pct(pct_lider)}.")
        if n_muni == 1 and principal == departamento:
            i_muni = (f"{departamento} es a la vez ciudad y departamento, así que toda su matrícula "
                      "está en un único municipio.")
        elif n_muni == 1:
            i_muni = f"En {departamento} solo hay un municipio con matrícula ({principal})."
        else:
            i_muni = (f"En {departamento}, {principal} reúne el {_pct(principal_pct)} de la matrícula "
                      f"del departamento y {_miles(n_pequenos)} de sus {_miles(n_muni)} municipios "
                      f"tienen menos de {_miles(UMBRAL_MUNICIPIO_PEQUENO)} matriculados.")
        dif = pos_amb - pos_nac
        frase_pos = (f"Su posgrado pesa {_pct(pos_amb)}, {_miles(abs(dif), 1)} puntos "
                     f"{'más' if dif >= 0 else 'menos'} que el promedio nacional ({_pct(pos_nac)}).")
        i_perfil = (f"En {departamento}, el {_pct(float(perfil_amb['universitaria']), 0)} de la matrícula es "
                    f"universitaria y el {_pct(float(perfil_amb['tecnologica']), 0)} tecnológica. " + frase_pos)
        lectura = (f"En {anio}, {departamento} aporta el {_pct(pct_dep)} de la matrícula nacional "
                   f"(puesto {puesto} de {n_deptos}). {i_muni} {frase_pos}")
        filas_perfil = [("Nacional", perfil_nac), (_corto(departamento), perfil_amb)]

    # ---- Interpretación de la gráfica 4
    registran = (f"{_miles(n_en_minimo)} registran apenas {_miles(minimo)}" if n_en_minimo > 1
                 else f"el más pequeño tiene {_miles(minimo)}")
    if todos:
        i_menores = (f"Los cinco departamentos con menos matrícula ({_lista(nombres_menores)}) suman "
                     f"{_miles(suma_menores)} matriculados, solo el {_pct(pct_menores, 2)} del país; "
                     f"{nombres_menores[0]} es el último con {_miles(menores.iloc[0])}. Entre los "
                     f"municipios, {_miles(n_menos_100)} de {_miles(n_muni)} tienen menos de 100 "
                     f"matriculados y {registran}.")
    else:
        if departamento in menores.index:
            inicio = (f"{departamento} es uno de los cinco departamentos con menos matrícula del país "
                      f"({_miles(por_depto[departamento])}).")
        else:
            inicio = (f"{departamento} no está entre los cinco con menos matrícula del país; los más "
                      f"pequeños son {_lista(nombres_menores)}.")
        if n_muni > 1:
            fin = (f" Dentro de {departamento}, {_miles(n_menos_100)} de sus {_miles(n_muni)} municipios "
                   f"tienen menos de 100 matriculados y {registran}.")
        else:
            fin = " Como solo tiene un municipio con matrícula, no hay rangos que comparar."
        i_menores = inicio + fin

    # ---- Tablas de los territorios con menos matrícula
    tabla_menores = [
        {"puesto": f"{n_deptos - i} de {n_deptos}", "departamento": d, "valor": _miles(v), "pct": _pct(v / total_nac * 100, 2)}
        for i, (d, v) in enumerate(menores.items())
    ]
    tabla_rangos = [{"rango": r["rango"], "municipios": _miles(r["municipios"]),
                     "pct": _pct(r["pct"], 1)} for r in rangos]

    # ---- Tabla de los municipios principales
    depto_de = ambito.drop_duplicates("cod_municipio").set_index("cod_municipio")["departamento"]
    tabla = [
        {"puesto": i + 1, "municipio": _nombre(nombre), "departamento": depto_de.get(cod, ""),
         "valor": _miles(valor), "pct": _pct(float(pct_muni.iloc[i])),
         "acumulado": _pct(float(acumulado.iloc[i]))}
        for i, ((cod, nombre), valor) in enumerate(por_muni.head(TOP).items())
    ]

    # ---- Cómo se calculó (con las cifras reales de esta selección)
    pasos = [f"Se tomó el año {anio}: {_miles(len(del_anio))} registros"
             + (f", de los que se descartaron {excluidos} sin departamento identificado." if excluidos
                else ".")]
    pasos.append("En cada registro se sumaron los seis niveles de formación y así se obtuvo la "
                 "matrícula total.")
    pasos.append(f"Se agrupó por departamento y por código de municipio, sumando las filas del mismo "
                 f"municipio. La matrícula del país es {_miles(total_nac)}.")
    if todos:
        pasos.append("Se calculó el porcentaje de cada territorio sobre el total del país y se "
                     "ordenó de mayor a menor.")
    else:
        pasos.append(f"Se aplicó el filtro «{departamento}» ({_miles(total_amb)} matriculados) y se "
                     "calculó su porcentaje sobre el país y el de cada municipio sobre el departamento.")
    pasos.append(f"Se acumularon los porcentajes de los municipios para ver cuántos reúnen el 80 % "
                 f"({n_para_80} en {donde}) y se contaron los de menos de "
                 f"{_miles(UMBRAL_MUNICIPIO_PEQUENO)} matriculados ({_miles(n_pequenos)}).")
    pasos.append(f"Para ver los territorios más pequeños se ordenaron los departamentos de menor a mayor "
                 f"(los {N_MENORES} últimos) y los municipios se clasificaron por rangos de matrícula, "
                 "porque muchos empatan con 1 matriculado y un «top» de municipios sería arbitrario.")
    pasos.append("Para el perfil se calculó el porcentaje de cada nivel y se sumaron especialización, "
                 "maestría y doctorado como «posgrado».")

    base["traza"]["pasos"] = pasos
    base.update({
        "vacio": False,
        "indicadores": {"k1": k1, "k2": k2, "k3": k3},
        "reparto": reparto,
        "lectura": lectura,
        "interpretaciones": {"departamentos": i_deptos, "municipios": i_muni, "perfil": i_perfil,
                             "menores": i_menores},
        "tabla_menores": tabla_menores,
        "tabla_rangos": tabla_rangos,
        "tabla": tabla,
        "imagenes": {
            "departamentos": _a_base64(_grafica_departamentos(por_depto, total_nac, departamento)),
            "municipios": _a_base64(_grafica_municipios(por_muni, total_amb)),
            "perfil": _a_base64(_grafica_perfil(filas_perfil)),
            "menores": _a_base64(_grafica_menores(menores, total_nac, departamento, rangos,
                                                  ambito_txt)),
        },
    })
    return base


VARIABLES_USADAS = [
    {"nombre": "Año", "tipo": "Temporal", "uso": "Filtro: elige el año que se analiza."},
    {"nombre": "Código del departamento", "tipo": "Territorial",
     "uso": "Identifica el departamento (el nombre se saca de la lista DANE)."},
    {"nombre": "Código y nombre del municipio", "tipo": "Territorial",
     "uso": "Agrupa por municipio sin duplicar nombres escritos distinto."},
    {"nombre": "Seis niveles de formación", "tipo": "Numérica",
     "uso": "Técnica profesional, tecnológica, universitaria, especialización, maestría y doctorado."},
    {"nombre": "Matrícula total", "tipo": "Numérica (derivada)",
     "uso": "Suma de los seis niveles; base de todos los porcentajes."},
]


# --------------------------------------------------------------------------
# Conocimientos evidentes, decisión y limitación (último año, con cifras reales)
# --------------------------------------------------------------------------

@lru_cache
def conocimientos_territoriales():
    """Los tres conocimientos evidentes con la estructura que pide la guía."""
    anio = opciones_territoriales()["anio_final"]
    todo = cargar_datos()
    df = todo[(todo["anio"] == anio) & (todo["departamento"] != SIN_IDENTIFICAR)]

    por_depto = _por_departamento(df)
    total = float(por_depto.sum())
    pct_depto = por_depto / total * 100
    por_muni = _por_municipio(df)
    pct_muni = por_muni / total * 100
    acumulado = pct_muni.cumsum()
    n_muni = len(por_muni)
    n_80 = int((acumulado < 80).sum()) + 1
    mediana = float(por_muni.median())
    n_peq = int((por_muni < UMBRAL_MUNICIPIO_PEQUENO).sum())
    minimo = float(por_muni.min())
    n_minimo = int((por_muni == por_muni.min()).sum())
    principales = [_nombre(n) for (_, n) in por_muni.head(4).index]
    razon = float(por_muni.iloc[0]) / mediana

    # Perfil de los departamentos grandes
    grandes = por_depto[por_depto >= UMBRAL_DEPTO_GRANDE].index
    perfiles = {d: _perfil(df[df["departamento"] == d]) for d in grandes}
    pos = {d: _posgrado(p) for d, p in perfiles.items()}
    tec = {d: float(p["tecnologica"]) for d, p in perfiles.items()}
    perfil_nac = _perfil(df)
    mas_pos, menos_pos = max(pos, key=pos.get), min(pos, key=pos.get)
    mas_tec = max(tec, key=tec.get)

    lista = [
        {
            "pregunta": "¿Qué tan concentrada está la matrícula en pocos territorios?",
            "variables": "Año, departamento, municipio y matrícula total (suma de los seis niveles).",
            "procedimiento": f"Se filtró {anio}, se sumó la matrícula por departamento y por municipio, "
                             "se calculó el porcentaje sobre el total nacional y se acumuló de mayor a menor.",
            "evidencia": "Gráficas 1 y 2 e indicadores de participación y concentración (filtro «Todos»).",
            "hallazgo": f"{por_depto.index[0]} reúne el {_pct(float(pct_depto.iloc[0]))} de la matrícula, "
                        f"los cinco primeros departamentos el {_pct(float(pct_depto.head(5).sum()))} y "
                        f"solo {n_80} municipios llegan al 80 %.",
            "interpretacion": f"La matrícula está muy concentrada en pocas ciudades grandes "
                              f"({', '.join(principales[:-1])} y {principales[-1]}); la mayor parte del "
                              "territorio aporta muy poco.",
            "utilidad": "Ayuda a ver dónde está la capacidad instalada y dónde haría falta llevar "
                        "oferta (programas regionales, sedes o virtualidad).",
            "limitacion": "Es matrícula registrada por municipio: no dice dónde vive el estudiante ni "
                          "si viaja a estudiar a otra ciudad.",
        },
        {
            "pregunta": "¿Cómo se reparte la matrícula entre los municipios más pequeños?",
            "variables": "Año, municipio y matrícula total.",
            "procedimiento": f"Se sumó la matrícula por municipio en {anio}, se calculó la mediana y se "
                             f"contaron los municipios con menos de {_miles(UMBRAL_MUNICIPIO_PEQUENO)} matriculados.",
            "evidencia": "Indicador «Municipios con matrícula» (con la mediana), gráfica 2, gráfica 4 "
                         "(municipios por rango de matrícula) y tabla de datos.",
            "hallazgo": f"{_miles(n_peq)} de {_miles(n_muni)} municipios ({_pct(n_peq / n_muni * 100, 0)}) "
                        f"tienen menos de {_miles(UMBRAL_MUNICIPIO_PEQUENO)} matriculados, la mediana es "
                        f"de {_miles(mediana)}"
                        + (f" y {_miles(n_minimo)} registran apenas {_miles(minimo)}." if n_minimo > 1 else "."),
            "interpretacion": f"{principales[0]} tiene unas {_miles(round(razon, -2))} veces la matrícula "
                              "del municipio típico: la desigualdad entre municipios grandes y pequeños "
                              "es enorme.",
            "utilidad": "Permite identificar municipios con muy poca presencia de educación superior "
                        "para pensar en apoyos o programas a distancia.",
            "limitacion": "Un municipio con poca matrícula puede ser simplemente pequeño o estar cerca de "
                          "una ciudad grande; sin población por municipio no se sabe cuál es el caso.",
        },
        {
            "pregunta": "¿Los departamentos grandes tienen la misma mezcla de niveles de formación?",
            "variables": "Año, departamento y la matrícula de los seis niveles.",
            "procedimiento": f"Con los departamentos de más de {_miles(UMBRAL_DEPTO_GRANDE)} matriculados "
                             f"en {anio} se calculó el porcentaje de cada nivel, se agrupó especialización, "
                             "maestría y doctorado como posgrado y se comparó con el promedio nacional.",
            "evidencia": "Gráfica 3 (perfil por nivel de formación).",
            "hallazgo": f"{mas_pos} tiene {_pct(pos[mas_pos])} de posgrado y {menos_pos} solo "
                        f"{_pct(pos[menos_pos])} (país: {_pct(_posgrado(perfil_nac))}); {mas_tec} tiene "
                        f"{_pct(tec[mas_tec])} en tecnológica frente a {_pct(float(perfil_nac['tecnologica']))} "
                        "del país.",
            "interpretacion": "Los departamentos grandes no se parecen entre sí: unos se inclinan hacia "
                              "los posgrados y otros hacia la formación tecnológica.",
            "utilidad": "Sirve para ajustar la oferta a cada territorio, por ejemplo reforzar posgrados "
                        "donde casi no existen.",
            "limitacion": f"Solo se compararon departamentos de más de {_miles(UMBRAL_DEPTO_GRANDE)} "
                          "matriculados y los datos no explican si la diferencia viene de la demanda, de "
                          "las instituciones o de cómo se registran los programas.",
        },
    ]

    # Departamentos con menos matrícula (para la decisión)
    bajos = por_depto.sort_values(kind="stable").head(N_MENORES)
    nombres_bajos = [f"{_corto(d)} ({_miles(v)})" for d, v in bajos.items()]
    decision = {
        "texto": "Como la matrícula está tan concentrada, el Ministerio y las instituciones podrían "
                 "priorizar un estudio para ampliar la oferta (extensión o virtual) en los "
                 "departamentos con menos matrícula, cruzándolo antes con su población.",
        "sustento": f"{por_depto.index[0]} concentra {_pct(float(pct_depto.iloc[0]))} de la matrícula, "
                    f"mientras {_lista(nombres_bajos)} apenas suman "
                    f"{_miles(bajos.sum())} matriculados en {anio} (gráfica 4).",
    }

    # Cobertura: cuántos municipios con datos hay en cada año (limitación)
    por_anio = (todo[todo["departamento"] != SIN_IDENTIFICAR]
                .groupby("anio")["cod_municipio"].nunique())
    cobertura = {"max": int(por_anio.max()), "max_anio": int(por_anio.idxmax()),
                 "min": int(por_anio.min()), "min_anio": int(por_anio.idxmin())}

    return {"anio": anio, "lista": lista, "decision": decision, "cobertura": cobertura}


# --------------------------------------------------------------------------
# Evidencias para el informe: python -m components.territorial
# --------------------------------------------------------------------------

def _guardar_csv(df, ruta):
    # Separador «;» y coma decimal para que Excel en español lo abra en columnas.
    df.to_csv(ruta, index=False, sep=";", decimal=",", encoding="utf-8-sig")


def generar_evidencias(carpeta=RUTA_EVIDENCIAS):
    """Guarda gráficas y tablas del último año en ``docs/territorial/evidencias/``."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    anio = opciones_territoriales()["anio_final"]

    todo = cargar_datos()
    df = todo[(todo["anio"] == anio) & (todo["departamento"] != SIN_IDENTIFICAR)]
    por_depto = _por_departamento(df)
    total = float(por_depto.sum())
    por_muni = _por_municipio(df)
    pct_muni = por_muni / total * 100

    # Gráficas
    _a_archivo(_grafica_departamentos(por_depto, total, TODOS,
               f"Participación de los departamentos en la matrícula, {anio}"),
               carpeta / f"01_participacion_departamentos_{anio}.png")
    _a_archivo(_grafica_municipios(por_muni, total,
               f"Los 10 municipios con más matrícula, {anio}"),
               carpeta / f"02_top_municipios_{anio}.png")
    grandes = list(por_depto.head(5).index)
    filas = [("Nacional", _perfil(df))] + [
        (_corto(d), _perfil(df[df["departamento"] == d])) for d in grandes]
    _a_archivo(_grafica_perfil(filas, f"Perfil por nivel de formación (%), {anio}"),
               carpeta / f"03_perfil_niveles_{anio}.png")

    menores = por_depto.sort_values(kind="stable").head(N_MENORES)
    rangos = _rangos_municipios(por_muni)
    _a_archivo(_grafica_menores(menores, total, TODOS, rangos, "del país",
               f"Territorios con menos matrícula, {anio}"),
               carpeta / f"08_territorios_menor_matricula_{anio}.png")

    # Tablas
    deptos = pd.DataFrame({
        "departamento": por_depto.index, "matricula": por_depto.values.round(0).astype(int),
        "porcentaje": (por_depto.values / total * 100).round(2),
        "porcentaje_acumulado": (por_depto.values / total * 100).cumsum().round(2),
    })
    _guardar_csv(deptos, carpeta / f"04_tabla_departamentos_{anio}.csv")

    nombres = df.drop_duplicates("cod_municipio").set_index("cod_municipio")["departamento"]
    munis = pd.DataFrame({
        "puesto": range(1, 21),
        "municipio": [_nombre(n) for (_, n) in por_muni.head(20).index],
        "departamento": [nombres.get(c, "") for (c, _) in por_muni.head(20).index],
        "matricula": por_muni.head(20).values.round(0).astype(int),
        "porcentaje": pct_muni.head(20).values.round(2),
        "porcentaje_acumulado": pct_muni.cumsum().head(20).values.round(2),
    })
    _guardar_csv(munis, carpeta / f"05_tabla_top_municipios_{anio}.csv")

    perfil = pd.DataFrame(
        {d: _perfil(df[df["departamento"] == d]) for d in por_depto[por_depto >= UMBRAL_DEPTO_GRANDE].index}
    ).T.rename(columns=NIVELES)
    perfil.insert(0, "matricula", por_depto[perfil.index].round(0))
    perfil["posgrado"] = perfil[[NIVELES[c] for c in POSGRADO]].sum(axis=1)
    perfil.loc["Nacional"] = [total, *_perfil(df).values, _posgrado(_perfil(df))]
    perfil = perfil.round(2)
    perfil["matricula"] = perfil["matricula"].round(0).astype(int)
    _guardar_csv(perfil.rename_axis("departamento").reset_index(),
                 carpeta / f"06_perfil_departamentos_{anio}.csv")

    _guardar_csv(pd.DataFrame({
        "puesto_desde_el_ultimo": range(1, len(menores) + 1),
        "departamento": menores.index, "matricula": menores.values.round(0).astype(int),
        "porcentaje": (menores.values / total * 100).round(3)}),
        carpeta / f"09_cinco_departamentos_menores_{anio}.csv")
    _guardar_csv(pd.DataFrame({
        "rango_de_matricula": [r["rango"] for r in rangos],
        "municipios": [r["municipios"] for r in rangos],
        "porcentaje": [round(r["pct"], 2) for r in rangos]}),
        carpeta / f"10_municipios_por_rango_{anio}.csv")

    cobertura = (todo[todo["departamento"] != SIN_IDENTIFICAR]
                 .groupby("anio").agg(municipios_con_registro=("cod_municipio", "nunique"),
                                      matricula_total=("matricula_total", "sum")).round(0).astype(int))
    _guardar_csv(cobertura.reset_index(), carpeta / "07_cobertura_municipios_por_anio.csv")

    # Resumen en texto: las cifras que se citan en el documento
    saberes = conocimientos_territoriales()
    t = tablero_territorial(anio, TODOS)
    lineas = [f"RESUMEN TERRITORIAL {anio}", "=" * 40, ""]
    lineas += [f"{k['etiqueta']}: {k['valor']} ({k['detalle']})" for k in t["indicadores"].values()]
    lineas += ["", "Lectura:", t["lectura"], "", "Territorios con menos matrícula:",
               t["interpretaciones"]["menores"], "", "Conocimientos evidentes:"]
    lineas += [f"{i}. {c['hallazgo']}" for i, c in enumerate(saberes["lista"], 1)]
    lineas += ["", "Decisión:", saberes["decision"]["texto"], saberes["decision"]["sustento"], "",
               "Cómo se calculó:"] + [f"- {p}" for p in t["traza"]["pasos"]]
    (carpeta / "00_resumen_cifras.txt").write_text("\n".join(lineas), encoding="utf-8")
    return sorted(p.name for p in carpeta.iterdir() if not p.name.startswith("."))


if __name__ == "__main__":
    archivos = generar_evidencias()
    print(f"Listo. Se guardaron {len(archivos)} archivos en {RUTA_EVIDENCIAS}:")
    for nombre in archivos:
        print("  -", nombre)
    print()
    print((RUTA_EVIDENCIAS / "00_resumen_cifras.txt").read_text(encoding="utf-8"))
