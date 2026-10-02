"""Dimensión temporal (Integrante 3): datos e indicadores.

Las tres gráficas se generan con matplotlib a partir del conjunto de datos
limpio (``components.datos``), como PNG codificado en base64 — no son
archivos de imagen sueltos, se recalculan en cada solicitud según los dos
filtros (departamento y nivel de formación).
"""

import base64
from functools import lru_cache
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .datos import NIVELES, SIN_IDENTIFICAR, cargar_datos
from .sitio import buscar_dimension

TODOS = "Todos"
TOTAL = "total"
NIVELES_TABLERO = {TOTAL: "Todos los niveles", **NIVELES}
COLOR = buscar_dimension("temporal")[0]["color"]
GRIS = "#6c757d"

# Tres periodos comparados en la tercera gráfica.
PERIODOS = [(2005, 2011), (2011, 2017), (2017, 2021)]

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


@lru_cache
def opciones_temporales():
    """Departamentos y niveles disponibles, para llenar los filtros."""
    df = cargar_datos()
    departamentos = sorted(
        d for d in df["departamento"].unique() if d != SIN_IDENTIFICAR
    )
    return {"departamentos": [TODOS, *departamentos], "niveles": NIVELES_TABLERO}


def _figura_a_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _miles(valor, decimales=0):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _pct(valor, con_signo=True):
    if valor is None:
        return "—"
    signo = "+" if con_signo and valor > 0 else ""
    return f"{signo}{valor:.1f} %".replace(".", ",")


def _grafica_linea(anios, serie):
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.fill_between(anios, serie, color=COLOR, alpha=0.15, linewidth=0)
    ax.plot(anios, serie, color=COLOR, linewidth=2.5, marker="o", markersize=3.5)
    ax.set_ylim(bottom=0)
    ax.set_xticks(anios[::2])
    ax.yaxis.set_major_formatter(lambda v, _: _miles(v) if v else "0")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


def _grafica_barras(etiquetas, valores, mostrar_valor=True):
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    colores = [COLOR if v is None or v >= 0 else "#e74c3c" for v in valores]
    barras = ax.bar(etiquetas, [v if v is not None else 0 for v in valores],
                     color=colores, width=0.6 if len(etiquetas) <= 4 else 0.75)
    ax.axhline(0, color=GRIS, linewidth=1)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f} %".replace(".", ","))
    if len(etiquetas) > 8:
        ax.set_xticks(etiquetas[::2])
    else:
        plt.setp(ax.get_xticklabels(), rotation=0 if len(etiquetas) <= 4 else 90)

    # Margen extra arriba/abajo para que las etiquetas de valor no choquen
    # con la cuadrícula ni con las etiquetas del eje X.
    validos = [v for v in valores if v is not None]
    if validos:
        arriba, abajo = max(validos + [0]), min(validos + [0])
        colchon = max((arriba - abajo) * 0.18, 1)
        ax.set_ylim(abajo - colchon, arriba + colchon)

    if mostrar_valor:
        for barra, valor in zip(barras, valores):
            if valor is None:
                continue
            y = barra.get_height()
            ax.annotate(_pct(valor), (barra.get_x() + barra.get_width() / 2, y),
                        xytext=(0, 4 if y >= 0 else -14), textcoords="offset points",
                        ha="center", fontsize=8.5, color=GRIS)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


def tablero_temporal(departamento, nivel):
    """Indicadores, gráficas y tabla para la combinación de filtros elegida."""
    opciones = opciones_temporales()
    if departamento not in opciones["departamentos"]:
        departamento = TODOS
    if nivel not in NIVELES_TABLERO:
        nivel = TOTAL

    df = cargar_datos()
    if departamento != TODOS:
        df = df[df["departamento"] == departamento]
    columna = "matricula_total" if nivel == TOTAL else nivel

    anios = sorted(int(a) for a in cargar_datos()["anio"].unique())
    por_anio = df.groupby("anio")[columna].sum().reindex(anios, fill_value=0)
    serie = [int(round(v)) for v in por_anio]

    variaciones = [None]
    for i in range(1, len(serie)):
        variaciones.append(None if serie[i - 1] == 0 else (serie[i] / serie[i - 1] - 1) * 100)

    crecimiento_total = None if not serie[0] else (serie[-1] / serie[0] - 1) * 100
    validos = [(i, v) for i, v in enumerate(variaciones) if v is not None]
    mejor = max(validos, key=lambda par: par[1]) if validos else None

    indicadores = {
        "ultimo": {"valor": _miles(serie[-1]), "etiqueta": f"Matrícula en {anios[-1]}",
                   "detalle": "Último año disponible"},
        "crecimiento": {"valor": _pct(crecimiento_total),
                         "etiqueta": f"Crecimiento {anios[0]}–{anios[-1]}",
                         "detalle": (f"Frente a {_miles(serie[0])} en {anios[0]}" if serie[0]
                                     else f"Sin matrícula en {anios[0]}")},
        "mayor": ({"valor": str(anios[mejor[0]]), "etiqueta": "Año de mayor aumento",
                    "detalle": f"{_pct(mejor[1])} frente a {anios[mejor[0] - 1]}"}
                   if mejor else
                   {"valor": "—", "etiqueta": "Año de mayor aumento", "detalle": "Sin datos suficientes"}),
    }

    periodos_valores = []
    for inicio, fin in PERIODOS:
        if inicio in anios and fin in anios:
            a, b = serie[anios.index(inicio)], serie[anios.index(fin)]
            periodos_valores.append(None if not a or not b else ((b / a) ** (1 / (fin - inicio)) - 1) * 100)
        else:
            periodos_valores.append(None)

    tabla = [
        {"anio": a, "valor": _miles(v), "variacion": _pct(var)}
        for a, v, var in zip(anios, serie, variaciones)
    ]

    return {
        "indicadores": indicadores,
        "tabla": tabla,
        "imagenes": {
            "linea": _grafica_linea(anios, serie),
            "variacion": _grafica_barras(anios, variaciones, mostrar_valor=False),
            "periodos": _grafica_barras([f"{i}–{f}" for i, f in PERIODOS], periodos_valores),
        },
    }
