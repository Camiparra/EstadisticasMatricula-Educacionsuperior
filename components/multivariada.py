"""Datos, indicadores y visualizaciones de la dimensión multivariada."""

import base64
from functools import lru_cache
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .datos import NIVELES, SIN_IDENTIFICAR, cargar_datos

TODOS = "Todos"
TOTAL = "total"
COLOR = "#9b59b6"
GRIS = "#6c757d"
COLORES_NIVELES = {
    "tecnica_profesional": "#0072B2",
    "tecnologica": "#E69F00",
    "universitaria": "#009E73",
    "especializacion": "#D55E00",
    "maestria": "#CC79A7",
    "doctorado": "#56B4E9",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": GRIS,
    "axes.labelcolor": GRIS,
    "text.color": GRIS,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
    "axes.grid": True,
    "grid.color": GRIS,
    "grid.alpha": 0.2,
    "axes.axisbelow": True,
})


@lru_cache
def opciones_multivariadas():
    """Valores válidos para los filtros del tablero."""
    df = cargar_datos()
    departamentos = sorted(
        departamento
        for departamento in df["departamento"].unique()
        if departamento != SIN_IDENTIFICAR
    )
    anios = sorted(int(anio) for anio in df["anio"].unique())
    return {
        "departamentos": [TODOS, *departamentos],
        "niveles": {TOTAL: "Todos los niveles", **NIVELES},
        "anios": anios,
    }


def _miles(valor, decimales=0):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _porcentaje(valor, decimales=1):
    signo = "+" if valor > 0 else ""
    return f"{signo}{_miles(valor, decimales)} %"


def _figura_a_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _sin_datos(fig, ax, mensaje="Sin datos para la selección actual"):
    ax.clear()
    ax.text(0.5, 0.5, mensaje, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    return _figura_a_base64(fig)


def _serie_niveles(df, departamento, anio_inicio, anio_fin):
    filtrado = df[df["anio"].between(anio_inicio, anio_fin)]
    if departamento != TODOS:
        filtrado = filtrado[filtrado["departamento"] == departamento]
    return filtrado


def _grafica_cruce(df, niveles):
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    largo = df.melt(
        id_vars=["anio", "departamento"],
        value_vars=list(NIVELES),
        var_name="nivel_formacion",
        value_name="matriculados",
    )
    largo["nivel_formacion"] = largo["nivel_formacion"].map(NIVELES)
    if niveles:
        largo = largo[largo["nivel_formacion"].isin(niveles)]
    tabla = largo.pivot_table(
        index="departamento",
        columns="nivel_formacion",
        values="matriculados",
        aggfunc="sum",
        fill_value=0,
    )
    if tabla.empty:
        return _sin_datos(fig, ax)

    tabla = tabla.reindex(columns=niveles)
    tabla = tabla.loc[tabla.sum(axis=1).nlargest(12).index]
    tabla = tabla.sort_values(by=list(tabla.columns), ascending=True)
    imagen = ax.imshow(tabla.to_numpy(), aspect="auto", cmap="Purples")
    ax.set_xticks(np.arange(len(tabla.columns)), labels=tabla.columns, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(tabla.index)), labels=tabla.index)
    ax.set_xlabel("Nivel de formación")
    ax.set_ylabel("Departamento")
    barra = fig.colorbar(imagen, ax=ax, fraction=0.035, pad=0.03)
    barra.set_label("Matrícula acumulada")
    barra.ax.yaxis.set_major_formatter(lambda valor, _: _miles(valor))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


def _interpretar_cruce(df, niveles, periodo):
    largo = df.melt(
        id_vars=["anio", "departamento"],
        value_vars=list(NIVELES),
        var_name="nivel_formacion",
        value_name="matriculados",
    )
    largo["nivel_formacion"] = largo["nivel_formacion"].map(NIVELES)
    if niveles:
        largo = largo[largo["nivel_formacion"].isin(niveles)]
    cruces = (
        largo.groupby(["departamento", "nivel_formacion"])["matriculados"]
        .sum()
        .sort_values(ascending=False)
    )
    total = float(cruces.sum())
    if cruces.empty or total == 0:
        return "No hay matrícula registrada para esta combinación de filtros."

    (departamento, nivel), valor = cruces.index[0], float(cruces.iloc[0])
    participacion = valor / total * 100
    if len(cruces) == 1:
        return (
            f"En esta selección solo queda una combinación departamento-nivel: "
            f"{departamento} · {nivel}, con {_miles(valor)} matrículas acumuladas."
        )
    return (
        f"En {periodo}, la mayor concentración está en {departamento}, nivel "
        f"{nivel}: {_miles(valor)} matrículas ({participacion:.1f} % del total "
        "de la selección). Este cruce concentra la mayor parte del volumen "
        "observado frente a las demás combinaciones."
    )


def _interpretar_evolucion(df, niveles):
    if df.empty:
        return "No hay datos anuales para esta selección."
    columnas = list(NIVELES) if len(niveles) > 1 else [
        next(clave for clave, nombre in NIVELES.items() if nombre == niveles[0])
    ]
    anual = df.groupby("anio")[columnas].sum().sort_index()
    if anual.empty:
        return "No hay datos anuales para esta selección."

    inicio = anual.iloc[0]
    fin = anual.iloc[-1]
    total_inicio = float(inicio.sum())
    total_fin = float(fin.sum())
    if total_inicio:
        cambio = (total_fin / total_inicio - 1) * 100
        tendencia_total = (
            f"El total pasó de {_miles(total_inicio)} a {_miles(total_fin)} "
            f"({_porcentaje(cambio)})"
        )
    else:
        tendencia_total = (
            f"El total pasó de {_miles(total_inicio)} a {_miles(total_fin)}"
        )

    pico = anual.sum(axis=1).idxmax()
    total_pico = float(anual.loc[pico].sum())
    if len(columnas) == 1:
        nivel = NIVELES[columnas[0]]
        return (
            f"{nivel}: {tendencia_total} entre {int(anual.index[0])} y "
            f"{int(anual.index[-1])}; su máximo del periodo fue {_miles(total_pico)} "
            f"en {int(pico)}."
        )

    acumulado = anual.sum().sort_values(ascending=False)
    nivel_mayor = acumulado.index[0]
    participacion = float(acumulado.iloc[0] / acumulado.sum() * 100) if acumulado.sum() else 0
    crecimiento = []
    for columna in columnas:
        valor_inicio = float(inicio[columna])
        valor_fin = float(fin[columna])
        if valor_inicio:
            crecimiento.append((valor_fin / valor_inicio - 1, columna))
    mayor_crecimiento = max(crecimiento, default=None)
    mensaje_crecimiento = (
        f" El mayor crecimiento porcentual entre los niveles fue "
        f"{NIVELES[mayor_crecimiento[1]]} "
        f"({_porcentaje(mayor_crecimiento[0] * 100)})."
        if mayor_crecimiento
        else ""
    )
    return (
        f"{tendencia_total} para los niveles seleccionados. {NIVELES[nivel_mayor]} "
        f"acumuló la mayor matrícula ({participacion:.1f} %); el máximo agregado "
        f"anual se registró en {int(pico)} ({_miles(total_pico)})."
        f"{mensaje_crecimiento}"
    )


def _grafica_evolucion(df, niveles):
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    if df.empty:
        return _sin_datos(fig, ax)
    columnas = (
        list(NIVELES)
        if len(niveles) > 1
        else [next(clave for clave, nombre in NIVELES.items() if nombre == niveles[0])]
    )
    serie = df.groupby("anio")[columnas].sum().sort_index()
    if serie.empty:
        return _sin_datos(fig, ax)
    for nivel in columnas:
        etiqueta = NIVELES[nivel]
        ax.plot(
            serie.index,
            serie[nivel],
            marker="o",
            markersize=3,
            linewidth=2,
            color=COLORES_NIVELES[nivel],
            label=etiqueta,
        )
    ax.set_xlabel("Año")
    ax.set_ylabel("Matrícula")
    ax.yaxis.set_major_formatter(lambda valor, _: _miles(valor))
    ax.set_xticks(serie.index)
    ax.tick_params(axis="x", rotation=45)
    if len(columnas) > 1:
        ax.legend(frameon=False, ncol=2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig)


def _resumen_municipal(df, columna):
    por_anio = (
        df.groupby(
            ["cod_departamento", "departamento", "cod_municipio", "municipio", "anio"],
            as_index=False,
        )
        .agg(matriculados=(columna, "sum"), ies=("ies_con_oferta", "max"))
    )
    if por_anio.empty:
        return por_anio
    por_anio["matricula_por_ies"] = por_anio["matriculados"] / por_anio["ies"]
    return (
        por_anio.groupby(
            ["cod_departamento", "departamento", "cod_municipio", "municipio"],
            as_index=False,
        )
        .agg(
            matricula_promedio=("matriculados", "mean"),
            ies_promedio=("ies", "mean"),
            matricula_por_ies=("matricula_por_ies", "mean"),
        )
    )


def _grafica_municipios(resumen):
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    if resumen.empty:
        return _sin_datos(fig, ax), 0, 0.0

    q1 = resumen["matricula_por_ies"].quantile(0.25)
    q3 = resumen["matricula_por_ies"].quantile(0.75)
    limite = q3 + 1.5 * (q3 - q1)
    inusuales = resumen["matricula_por_ies"] > limite
    ax.scatter(
        resumen.loc[~inusuales, "ies_promedio"],
        resumen.loc[~inusuales, "matricula_promedio"],
        s=24,
        alpha=0.55,
        color="#9b82b0",
        label="Dentro del rango",
    )
    if inusuales.any():
        ax.scatter(
            resumen.loc[inusuales, "ies_promedio"],
            resumen.loc[inusuales, "matricula_promedio"],
            s=34,
            alpha=0.85,
            color="#d35400",
            label="Posible valor inusual",
        )
        destacados = resumen.loc[inusuales].nlargest(5, "matricula_por_ies")
        for fila in destacados.itertuples():
            ax.annotate(
                fila.municipio.title(),
                (fila.ies_promedio, fila.matricula_promedio),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7,
            )
    ax.set_xlabel("IES con oferta promedio por año")
    ax.set_ylabel("Matrícula promedio por año")
    ax.xaxis.set_major_formatter(lambda valor, _: _miles(valor, 1))
    ax.yaxis.set_major_formatter(lambda valor, _: _miles(valor))
    ax.legend(frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return _figura_a_base64(fig), int(inusuales.sum()), float(limite)


def tablero_multivariado(
    departamento,
    nivel,
    anio_inicio,
    anio_fin,
):
    """Calcula el tablero completo a partir del CSV limpio y los filtros."""
    opciones = opciones_multivariadas()
    if departamento not in opciones["departamentos"]:
        departamento = TODOS
    if nivel not in opciones["niveles"]:
        nivel = TOTAL
    if anio_inicio not in opciones["anios"]:
        anio_inicio = opciones["anios"][0]
    if anio_fin not in opciones["anios"]:
        anio_fin = opciones["anios"][-1]
    if anio_inicio > anio_fin:
        anio_inicio, anio_fin = anio_fin, anio_inicio

    niveles = list(NIVELES.values()) if nivel == TOTAL else [NIVELES[nivel]]
    columna = "matricula_total" if nivel == TOTAL else nivel
    datos = _serie_niveles(cargar_datos(), departamento, anio_inicio, anio_fin)
    largo = datos.melt(
        id_vars=["anio", "departamento"],
        value_vars=list(NIVELES),
        var_name="nivel_formacion",
        value_name="matriculados",
    )
    largo["nivel_formacion"] = largo["nivel_formacion"].map(NIVELES)
    largo_todos_niveles = largo
    if nivel != TOTAL:
        largo = largo[largo["nivel_formacion"] == NIVELES[nivel]]

    total = int(round(datos[columna].sum()))
    municipios = int(datos["cod_municipio"].nunique())
    cruces = (
        largo.groupby(["anio", "departamento", "nivel_formacion"])["matriculados"]
        .sum()
        .sort_values(ascending=False)
    )
    if cruces.empty:
        mayor_cruce = {"valor": "—", "etiqueta": "Cruce de mayor matrícula", "detalle": "Sin registros en la selección"}
        hallazgo_cruce = "No hay registros para la combinación de filtros elegida."
        evidencia_cruce = "No se encontraron combinaciones con matrícula en este periodo."
    else:
        (anio_cruce, depto_cruce, nivel_cruce), valor_cruce = cruces.index[0], cruces.iloc[0]
        mayor_cruce = {
            "valor": _miles(valor_cruce),
            "etiqueta": "Cruce de mayor matrícula",
            "detalle": f"{nivel_cruce} · {depto_cruce} · {anio_cruce}",
        }
        hallazgo_cruce = (
            f"La combinación de mayor matrícula fue {nivel_cruce} en {depto_cruce} "
            f"durante {anio_cruce}, con {_miles(valor_cruce)} registros."
        )
        evidencia_cruce = mayor_cruce["detalle"] + f": {_miles(valor_cruce)}."

    resumen_municipal = _resumen_municipal(datos, columna)
    if resumen_municipal.empty:
        municipio_top = None
        texto_municipio = "No hay datos municipales en la selección."
        outliers = 0
        limite_outlier = 0.0
        correlacion = None
    else:
        municipio_top = resumen_municipal.nlargest(1, "matricula_por_ies").iloc[0]
        texto_municipio = (
            f"{municipio_top['municipio'].title()} ({municipio_top['departamento']}): "
            f"{_miles(municipio_top['matricula_por_ies'])} matriculados promedio por IES-año."
        )
        q1 = resumen_municipal["matricula_por_ies"].quantile(0.25)
        q3 = resumen_municipal["matricula_por_ies"].quantile(0.75)
        limite_outlier = float(q3 + 1.5 * (q3 - q1))
        outliers = int((resumen_municipal["matricula_por_ies"] > limite_outlier).sum())
        variables_varian = (
            resumen_municipal["ies_promedio"].nunique() > 1
            and resumen_municipal["matricula_promedio"].nunique() > 1
        )
        correlacion = (
            float(resumen_municipal["ies_promedio"].corr(resumen_municipal["matricula_promedio"]))
            if len(resumen_municipal) > 1 and variables_varian
            else None
        )

    composicion = (
        largo_todos_niveles.groupby("nivel_formacion")["matriculados"]
        .sum()
        .sort_values(ascending=False)
    )
    if composicion.empty or composicion.sum() == 0:
        nivel_top = "Sin datos"
        participacion_top = 0.0
    else:
        nivel_top = str(composicion.index[0])
        participacion_top = float(composicion.iloc[0] / composicion.sum() * 100)

    if correlacion is None:
        texto_correlacion = "No se puede calcular una asociación con menos de dos municipios."
    else:
        if abs(correlacion) < 0.2:
            fuerza = "prácticamente no hay asociación lineal"
        elif abs(correlacion) < 0.5:
            fuerza = "la asociación lineal es débil"
        elif abs(correlacion) < 0.8:
            fuerza = "la asociación lineal es moderada"
        else:
            fuerza = "la asociación lineal es fuerte"
        sentido = "positiva" if correlacion > 0 else "negativa"
        texto_correlacion = (
            f"{fuerza} entre el promedio de IES y el de matrícula "
            f"(r de Pearson = {correlacion:.2f}, {sentido})."
        )

    periodo = f"{anio_inicio}–{anio_fin}"
    lugar = "todo el país" if departamento == TODOS else departamento
    nivel_texto = opciones["niveles"][nivel].lower()
    return {
        "seleccion": {
            "departamento": departamento,
            "nivel": nivel,
            "anio_inicio": anio_inicio,
            "anio_fin": anio_fin,
        },
        "indicadores": {
            "matricula": {
                "valor": _miles(total),
                "etiqueta": "Matrícula acumulada",
                "detalle": f"{nivel_texto} · {lugar} · {periodo}",
            },
            "municipios": {
                "valor": _miles(municipios),
                "etiqueta": "Municipios con registros",
                "detalle": f"En la selección {periodo}",
            },
            "cruce": mayor_cruce,
        },
        "imagenes": {
            "cruce": _grafica_cruce(datos, niveles),
            "evolucion": _grafica_evolucion(datos, niveles),
            "municipios": _grafica_municipios(resumen_municipal)[0],
        },
        "interpretaciones": {
            "cruce": _interpretar_cruce(datos, niveles, periodo),
            "evolucion": _interpretar_evolucion(datos, niveles),
            "municipios": (
                (
                    f"No se registró matrícula para los municipios de {lugar} "
                    f"en {periodo}, así que no es posible comparar sus promedios "
                    "de matrícula por IES."
                    if resumen_municipal.empty
                    or resumen_municipal["matricula_promedio"].sum() == 0
                    else
                    f"En {lugar}, {texto_correlacion} El municipio con mayor "
                    f"matrícula promedio por IES-año es {texto_municipio} "
                    f"Se señalan {outliers} municipios sobre el umbral de "
                    f"{_miles(limite_outlier)}; conviene validarlos antes de "
                    "interpretarlos como brechas."
                )
            ),
        },
        "conocimientos": {
            "cruce": {
                "hallazgo": hallazgo_cruce,
                "evidencia": evidencia_cruce,
            },
            "composicion": {
                "nivel": nivel_top,
                "participacion": participacion_top,
                "evidencia": (
                    f"El nivel con mayor participación es {nivel_top}, con "
                    f"{participacion_top:.1f} %; ver el mapa de calor y los indicadores."
                ),
                "hallazgo": (
                    f"{nivel_top} aporta la mayor participación ({participacion_top:.1f} %) "
                    f"de la matrícula considerada en {lugar} durante {periodo}."
                    if composicion.sum() else "No hay matrícula registrada en el periodo seleccionado."
                ),
            },
            "inusuales": {
                "municipio": texto_municipio,
                "cantidad": outliers,
                "umbral": _miles(limite_outlier),
                "hallazgo": (
                    f"Se identifican {outliers} municipios por encima del umbral intercuartílico "
                    f"de {_miles(limite_outlier)} matriculados promedio por IES-año."
                    if outliers
                    else "Ningún municipio supera el umbral intercuartílico de matrícula por IES-año."
                ),
            },
        },
    }
