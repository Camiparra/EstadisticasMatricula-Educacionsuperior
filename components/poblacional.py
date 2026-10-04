import base64
from functools import lru_cache
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from .datos import NIVELES, SIN_IDENTIFICAR, cargar_datos
from .sitio import buscar_dimension

TODOS = "Todos"
COLOR = buscar_dimension("poblacional")[0]["color"]
GRIS = "#6c757d"

# Rangos de tamaño de matrícula por municipio (tercera gráfica).
LIMITES_TAMANO = [0, 1_000, 10_000, 100_000, float("inf")]
ETIQUETAS_TAMANO = ["Menos de 1.000", "1.000 a 9.999", "10.000 a 99.999", "100.000 o más"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": GRIS,
    "axes.labelcolor": GRIS,
    "text.color": GRIS,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
    "axes.grid": True,
    "grid.color": GRIS,
    "grid.alpha": 0.25,
    "axes.axisbelow": True,
})


def _miles(valor):
    return f"{valor:,.0f}".replace(",", ".")


def _porcentaje(parte, total):
    if not total:
        return "0,0 %"
    return f"{parte / total * 100:.1f} %".replace(".", ",")


def _figura_a_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _grafica_vacia():
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    ax.axis("off")
    ax.text(0.5, 0.5, "Sin datos para esta selección", ha="center", va="center",
            fontsize=12, color=GRIS)
    return _figura_a_base64(fig)


def _barras_horizontales(etiquetas, valores, total):
    if not len(valores) or max(valores) <= 0:
        return _grafica_vacia()
    fig, ax = plt.subplots(figsize=(6.4, max(2.6, 0.4 * len(etiquetas) + 0.9)))
    posiciones = list(range(len(etiquetas)))
    ax.barh(posiciones, valores, color=COLOR, height=0.65)
    ax.set_yticks(posiciones)
    ax.set_yticklabels(etiquetas)
    ax.invert_yaxis()
    ax.set_xlim(0, max(valores) * 1.5)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.xaxis.set_major_formatter(lambda v, _: _miles(v))
    ax.grid(axis="y", visible=False)
    for posicion, valor in zip(posiciones, valores):
        ax.annotate(f"{_miles(valor)} ({_porcentaje(valor, total)})", (valor, posicion),
                    xytext=(4, 0), textcoords="offset points", va="center",
                    fontsize=8.5, color=GRIS)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


def _barras_verticales(etiquetas, valores):
    if not sum(valores):
        return _grafica_vacia()
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    barras = ax.bar(etiquetas, valores, color=COLOR, width=0.6)
    ax.set_ylim(0, max(valores) * 1.18)
    ax.set_ylabel("Municipios")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", visible=False)
    for barra, valor in zip(barras, valores):
        ax.annotate(_miles(valor), (barra.get_x() + barra.get_width() / 2, valor),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    fontsize=9, color=GRIS)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


@lru_cache
def opciones_poblacionales():
    """Años y departamentos disponibles, para llenar los filtros."""
    df = cargar_datos()
    anios = [TODOS, *[str(int(a)) for a in sorted(df["anio"].unique())]]
    departamentos = sorted(d for d in df["departamento"].unique() if d != SIN_IDENTIFICAR)
    return {"anios": anios, "departamentos": [TODOS, *departamentos]}


def _calcular(df):
    """Totales por nivel, por municipio y por rango de tamaño para un conjunto de filas."""
    total = float(df["matricula_total"].sum())
    por_nivel = df[list(NIVELES)].sum().sort_values(ascending=False)

    con_codigo = df[df["cod_municipio"].notna()]
    por_municipio = (con_codigo.groupby("cod_municipio")["matricula_total"]
                     .sum().sort_values(ascending=False))
    nombres = con_codigo.groupby("cod_municipio")["municipio"].first()

    if por_municipio.empty:
        conteo = pd.Series(0, index=ETIQUETAS_TAMANO)
    else:
        rangos = pd.cut(por_municipio, bins=LIMITES_TAMANO, right=False,
                        labels=ETIQUETAS_TAMANO)
        conteo = rangos.value_counts().reindex(ETIQUETAS_TAMANO, fill_value=0)

    grandes = por_municipio[por_municipio >= LIMITES_TAMANO[3]]
    return {
        "total": total,
        "por_nivel": por_nivel,
        "por_municipio": por_municipio,
        "nombres": nombres,
        "conteo": conteo.astype(int),
        "n_grandes": len(grandes),
        "matricula_grandes": float(grandes.sum()),
    }


def tablero_poblacional(anio, departamento):
    """Indicadores, gráficas e interpretaciones para la combinación de filtros elegida."""
    opciones = opciones_poblacionales()
    if anio not in opciones["anios"]:
        anio = TODOS
    if departamento not in opciones["departamentos"]:
        departamento = TODOS

    df = cargar_datos()
    if anio != TODOS:
        df = df[df["anio"] == int(anio)]
    if departamento != TODOS:
        df = df[df["departamento"] == departamento]

    r = _calcular(df)
    total, por_nivel, por_municipio = r["total"], r["por_nivel"], r["por_municipio"]
    top10 = por_municipio.head(10)
    conteo = r["conteo"]
    primero, ultimo = opciones["anios"][1], opciones["anios"][-1]
    periodo = (f"Suma de todos los años ({primero}–{ultimo})" if anio == TODOS
               else f"Año {anio}")

    if total > 0:
        nivel_1, nivel_2, nivel_ultimo = por_nivel.index[0], por_nivel.index[1], por_nivel.index[-1]
        codigo_1 = top10.index[0]
        nombre_1 = r["nombres"][codigo_1]
        n_municipios = len(por_municipio)
        pequenos = int(conteo.iloc[0] + conteo.iloc[1])

        indicadores = {
            "total": {"valor": _miles(total), "etiqueta": "Matrícula total", "detalle": periodo},
            "nivel": {"valor": NIVELES[nivel_1], "etiqueta": "Nivel predominante",
                      "detalle": f"{_porcentaje(por_nivel.iloc[0], total)} de la matrícula"},
            "municipio": {"valor": nombre_1, "etiqueta": "Municipio con mayor matrícula",
                          "detalle": f"{_porcentaje(top10.iloc[0], total)} de la matrícula"},
        }

        interpretaciones = {
            "niveles": (
                f"{NIVELES[nivel_1]} concentra {_porcentaje(por_nivel.iloc[0], total)} de la "
                f"matrícula y {NIVELES[nivel_2].lower()} aporta {_porcentaje(por_nivel.iloc[1], total)}. "
                f"El nivel con menos matrícula es {NIVELES[nivel_ultimo].lower()}, "
                f"con {_porcentaje(por_nivel.iloc[-1], total)}."
            ),
            "municipios": (
                f"{nombre_1} lidera con {_porcentaje(top10.iloc[0], total)} de la matrícula. "
                + (f"Los {len(top10)} municipios del gráfico suman "
                   f"{_porcentaje(top10.sum(), total)}." if len(top10) > 1 else "")
            ).strip(),
            "tamanos": (
                f"De {_miles(n_municipios)} municipios con registros, {r['n_grandes']} "
                f"({_porcentaje(r['n_grandes'], n_municipios)}) tienen 100.000 matriculados o más "
                f"y reúnen {_porcentaje(r['matricula_grandes'], total)} de la matrícula; "
                f"{pequenos} ({_porcentaje(pequenos, n_municipios)}) tienen menos de 10.000."
            ),
        }
    else:
        sin_datos = {"valor": "—", "detalle": "Sin datos para esta selección"}
        indicadores = {
            "total": {**sin_datos, "etiqueta": "Matrícula total"},
            "nivel": {**sin_datos, "etiqueta": "Nivel predominante"},
            "municipio": {**sin_datos, "etiqueta": "Municipio con mayor matrícula"},
        }
        interpretaciones = {k: "Sin datos para esta selección." for k in ("niveles", "municipios", "tamanos")}

    tabla = [
        {"nivel": NIVELES[clave], "matricula": _miles(valor),
         "porcentaje": _porcentaje(valor, total)}
        for clave, valor in por_nivel.items()
    ]

    return {
        "indicadores": indicadores,
        "interpretaciones": interpretaciones,
        "tabla": tabla,
        "imagenes": {
            "niveles": _barras_horizontales(
                [NIVELES[c] for c in por_nivel.index], list(por_nivel.values), total),
            "municipios": _barras_horizontales(
                [r["nombres"][c] for c in top10.index], list(top10.values), total),
            "tamanos": _barras_verticales(ETIQUETAS_TAMANO, [int(v) for v in conteo.values]),
        },
        "conocimientos": conocimientos_poblacionales(),
    }


@lru_cache
def conocimientos_poblacionales():
    """Los tres conocimientos evidentes, calculados a escala nacional (todos los años)."""
    r = _calcular(cargar_datos())
    total, niveles, municipios = r["total"], r["por_nivel"], r["por_municipio"]
    top10 = municipios.head(10)
    n_municipios = len(municipios)
    pequenos = int(r["conteo"].iloc[0] + r["conteo"].iloc[1])
    posgrados = niveles["especializacion"] + niveles["maestria"] + niveles["doctorado"]
    nombre_1 = r["nombres"][municipios.index[0]]

    def p(clave):
        return _porcentaje(niveles[clave], total)

    return {
        1: dict(
            pregunta="¿Qué niveles de formación concentran la matrícula?",
            variables="Los seis niveles de formación: técnica profesional, tecnológica, universitaria, especialización, maestría y doctorado.",
            procedimiento="Se sumó la matrícula de cada nivel en todos los años y municipios y se calculó su porcentaje sobre el total.",
            evidencia="Gráfica 1 e indicador «Nivel predominante».",
            hallazgo=f"La formación universitaria concentra {p('universitaria')} de la matrícula acumulada y la tecnológica {p('tecnologica')}.",
            interpretacion=f"La educación superior se concentra en el pregrado: especialización, maestría y doctorado reúnen solo {_porcentaje(posgrados, total)} y el doctorado apenas {p('doctorado')}.",
            utilidad="Sirve para decidir dónde reforzar la oferta si se busca diversificar hacia programas técnicos, tecnológicos y de posgrado.",
            limitacion="Es matrícula acumulada de varios años: una persona se cuenta cada año que está matriculada, y los datos no dicen cuántos terminan sus estudios.",
        ),
        2: dict(
            pregunta="¿Se concentra la matrícula en pocos municipios?",
            variables="Código y nombre del municipio y matrícula total.",
            procedimiento="Se sumó la matrícula por código de municipio, se ordenó de mayor a menor y se calculó la participación de los diez primeros.",
            evidencia="Gráfica 2 e indicador «Municipio con mayor matrícula».",
            hallazgo=f"{nombre_1} concentra {_porcentaje(municipios.iloc[0], total)} de la matrícula acumulada y los diez municipios con más matrícula reúnen {_porcentaje(top10.sum(), total)}.",
            interpretacion="La oferta de educación superior está muy ligada a las grandes ciudades: la mayor parte de la matrícula depende de muy pocos municipios.",
            utilidad="Ayuda a priorizar sedes regionales, becas o programas a distancia en los territorios con menos matrícula.",
            limitacion="El conjunto no trae la población de cada municipio, así que no se puede medir cobertura (qué proporción de las personas accede a la educación superior).",
        ),
        3: dict(
            pregunta="¿Cómo se reparten los municipios según el tamaño de su matrícula?",
            variables="Código del municipio y matrícula total.",
            procedimiento="Se sumó la matrícula por municipio y se clasificó cada uno en cuatro rangos de tamaño.",
            evidencia="Gráfica 3 e interpretación del rango «100.000 o más».",
            hallazgo=f"{r['n_grandes']} municipios ({_porcentaje(r['n_grandes'], n_municipios)}) tienen 100.000 matriculados o más y reúnen {_porcentaje(r['matricula_grandes'], total)} de la matrícula, mientras {pequenos} ({_porcentaje(pequenos, n_municipios)}) tienen menos de 10.000.",
            interpretacion="La distribución es muy desigual: un grupo reducido de municipios reúne la mayor parte de la matrícula.",
            utilidad="Permite distinguir los municipios grandes, que sostienen el sistema, de los pequeños, donde una oferta nueva tendría más impacto relativo.",
            limitacion="Un municipio sin registros no aparece, y el número de municipios con datos cambia de un año a otro, por lo que la clasificación depende de los años incluidos.",
        ),
        "resumen": {
            "top10": _porcentaje(top10.sum(), total),
            "universitaria": p("universitaria"),
        },
    }