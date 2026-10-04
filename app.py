"""Aplicación Flask del análisis de matrícula en educación superior (MEN - SNIES).

Punto de entrada del proyecto. Las vistas HTML viven en ``templates/``, los
recursos estáticos (CSS, JS, imágenes) en ``static/`` y la lógica reutilizable
(carga de datos, información del sitio) en ``components/``.

Ejecución local:
    python app.py
"""

from flask import Flask, render_template, request

from components.datos import resumen_general
from components.multivariada import opciones_multivariadas, tablero_multivariado
from components.temporal import opciones_temporales, tablero_temporal
from components.territorial import conocimientos_territoriales, opciones_territoriales, tablero_territorial
from components.sitio import (
    DATASET,
    DIMENSIONES,
    INTEGRANTES,
    REPOSITORIO,
    SECCIONES_DIMENSION,
    buscar_dimension,
    integrante,
)

app = Flask(__name__)


@app.template_filter("miles")
def formato_miles(valor, decimales=0):
    """Formato colombiano: 2448271 -> "2.448.271"; 104.58 -> "104,6"."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


@app.context_processor
def datos_del_sitio():
    # Disponibles en todas las plantillas (menú, pie de página, etc.).
    return {"dimensiones": DIMENSIONES, "dataset": DATASET, "repositorio": REPOSITORIO}


def render_dimension(slug, **contexto):
    """Renderiza el tablero de una dimensión con su menú lateral.

    Cada dimensión puede enviar sus propios datos (indicadores, gráficas,
    filtros) como argumentos adicionales en ``contexto``.
    """
    dimension, anterior, siguiente = buscar_dimension(slug)
    return render_template(
        f"dimensiones/{slug}.html",
        dimension=dimension,
        anterior=anterior,
        siguiente=siguiente,
        responsable=integrante(dimension["integrante"]),
        secciones=SECCIONES_DIMENSION,
        **contexto,
    )


@app.route("/")
def inicio():
    return render_template(
        "index.html",
        resumen=resumen_general(),
        integrantes=INTEGRANTES,
    )


# Rutas de las cuatro dimensiones. Cada integrante agrega en su función el
# procesamiento de datos de su tablero y lo envía a render_dimension().

@app.route("/dimension/poblacional")
def poblacional():
    return render_dimension("poblacional")


@app.route("/dimension/territorial")
def territorial():
    opciones = opciones_territoriales()
    anio = request.args.get("anio", type=int, default=opciones["anio_final"])
    departamento = request.args.get("departamento", "Todos")
    return render_dimension(
        "territorial",
        opciones=opciones,
        # tablero_territorial corrige año o departamento inválidos y devuelve
        # la selección final en tablero["seleccion"].
        tablero=tablero_territorial(anio, departamento),
        saberes=conocimientos_territoriales(),
    )


@app.route("/dimension/temporal")
def temporal():
    opciones = opciones_temporales()
    seleccion = {
        "departamento": request.args.get("departamento", "Todos"),
        "nivel": request.args.get("nivel", "total"),
    }
    return render_dimension(
        "temporal",
        opciones=opciones,
        seleccion=seleccion,
        tablero=tablero_temporal(seleccion["departamento"], seleccion["nivel"]),
    )


@app.route("/dimension/multivariada")
def multivariada():
    opciones = opciones_multivariadas()
    seleccion = {
        "departamento": request.args.get("departamento", "Todos"),
        "nivel": request.args.get("nivel", "total"),
        "anio_inicio": request.args.get("anio_inicio", str(opciones["anios"][0])),
        "anio_fin": request.args.get("anio_fin", str(opciones["anios"][-1])),
    }
    try:
        anio_inicio = int(seleccion["anio_inicio"])
    except ValueError:
        anio_inicio = opciones["anios"][0]
    try:
        anio_fin = int(seleccion["anio_fin"])
    except ValueError:
        anio_fin = opciones["anios"][-1]
    tablero = tablero_multivariado(
        seleccion["departamento"],
        seleccion["nivel"],
        anio_inicio,
        anio_fin,
    )
    return render_dimension(
        "multivariada",
        opciones=opciones,
        seleccion=tablero["seleccion"],
        tablero=tablero,
    )


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
