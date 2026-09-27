"""Información fija del sitio: dimensiones, secciones de cada tablero,
integrantes y ficha del conjunto de datos.

Se usa desde las rutas y las plantillas (menú, página de inicio, menú lateral),
así que cualquier cambio aquí se refleja en todo el sitio.
"""

DIMENSIONES = [
    {
        "slug": "poblacional",
        "numero": 1,
        "titulo": "Dimensión poblacional",
        "corto": "Poblacional",
        "icono": "bi-people-fill",
        "color": "#3498db",
        "pregunta": "¿Cómo está compuesta y distribuida la población analizada "
                    "según sus principales características?",
        "resumen": "Composición de la matrícula por nivel de formación: grupos "
                   "predominantes, minoritarios y su participación.",
        "integrante": 1,
        "analiza": [
            "Cantidad total de registros.",
            "Categorías principales.",
            "Porcentaje de participación por categoría.",
            "Grupos predominantes y minoritarios.",
            "Distribución de las variables principales.",
            "Características generales de la población.",
        ],
    },
    {
        "slug": "territorial",
        "numero": 2,
        "titulo": "Dimensión territorial",
        "corto": "Territorial",
        "icono": "bi-geo-alt-fill",
        "color": "#18bc9c",
        "pregunta": "¿Cómo se distribuye la población y sus principales "
                    "características entre los territorios disponibles?",
        "resumen": "Departamentos y municipios con mayor y menor matrícula, "
                   "concentraciones y diferencias entre territorios.",
        "integrante": 2,
        "analiza": [
            "Distribución por departamento y municipio.",
            "Territorios con mayor y menor cantidad de registros.",
            "Participación porcentual de cada territorio.",
            "Concentraciones territoriales.",
            "Diferencias entre territorios.",
            "Comportamientos particulares de algunas zonas.",
        ],
    },
    {
        "slug": "temporal",
        "numero": 3,
        "titulo": "Dimensión temporal",
        "corto": "Temporal",
        "icono": "bi-graph-up-arrow",
        "color": "#f39c12",
        "pregunta": "¿Cómo ha cambiado el comportamiento de la población "
                    "durante el periodo disponible?",
        "resumen": "Evolución año a año entre 2005 y 2021: aumentos, "
                   "disminuciones y cambios importantes.",
        "integrante": 3,
        "analiza": [
            "Evolución por año.",
            "Periodos con mayor y menor cantidad de registros.",
            "Aumentos y disminuciones.",
            "Cambios importantes.",
            "Posibles comportamientos repetitivos.",
            "Comparación entre periodos.",
        ],
    },
    {
        "slug": "multivariada",
        "numero": 4,
        "titulo": "Dimensión relacional y multivariada",
        "corto": "Multivariada",
        "icono": "bi-diagram-3-fill",
        "color": "#9b59b6",
        "pregunta": "¿Qué diferencias o relaciones evidentes pueden identificarse "
                    "al analizar conjuntamente tres o más variables?",
        "resumen": "Cruces entre nivel de formación, territorio y año: "
                   "combinaciones frecuentes y casos inusuales.",
        "integrante": 4,
        "analiza": [
            "Relaciones entre variables.",
            "Diferencias entre grupos.",
            "Cruce de tres o más variables.",
            "Combinaciones con mayor cantidad de registros.",
            "Comportamientos particulares por categoría, territorio o periodo.",
            "Posibles casos inusuales.",
        ],
    },
]

# Secciones mínimas de cada tablero (requisitos de la guía del proyecto).
# El id se usa como ancla en la página y en el menú lateral.
SECCIONES_DIMENSION = [
    {"id": "pregunta", "titulo": "Pregunta de análisis", "icono": "bi-question-circle"},
    {"id": "variables", "titulo": "Variables utilizadas", "icono": "bi-table"},
    {"id": "filtros", "titulo": "Filtros", "icono": "bi-funnel"},
    {"id": "indicadores", "titulo": "Indicadores", "icono": "bi-speedometer2"},
    {"id": "visualizaciones", "titulo": "Visualizaciones", "icono": "bi-bar-chart-line"},
    {"id": "conocimientos", "titulo": "Conocimientos evidentes", "icono": "bi-lightbulb"},
    {"id": "limitacion", "titulo": "Limitación", "icono": "bi-exclamation-triangle"},
    {"id": "decision", "titulo": "Decisión sustentada", "icono": "bi-signpost-split"},
]

INTEGRANTES = [
    {
        "numero": 1,
        "nombre": "Camila Parra Berrio",
        "iniciales": "CP",
        "responsabilidad": "Administración del repositorio y revisión de pull requests",
        "dimension": "poblacional",
    },
    {
        "numero": 2,
        "nombre": "Jonathan David Chavarro Segura",
        "iniciales": "JC",
        "responsabilidad": "Estructura del proyecto Flask y diseño con Bootstrap",
        "dimension": "territorial",
    },
    {
        "numero": 3,
        "nombre": "Nicolas Suarez Rativa",
        "iniciales": "NS",
        "responsabilidad": "Preparación y publicación de la aplicación",
        "dimension": "temporal",
    },
    {
        "numero": 4,
        "nombre": "Richard Ludim Barajas Parrado",
        "iniciales": "RB",
        "responsabilidad": "Elaboración del informe técnico",
        "dimension": "multivariada",
    },
]

DATASET = {
    "nombre": "MEN Estadísticas Matrícula por Municipios ES",
    "entidad": "Ministerio de Educación Nacional (MEN) — SNIES",
    "url": "https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data",
    "poblacion": "Estudiantes matriculados en programas de educación superior en "
                 "Colombia, agregados por municipio y año.",
    "formato": "CSV",
}

REPOSITORIO = "https://github.com/Camiparra/EstadisticasMatricula-Educacionsuperior"


def buscar_dimension(slug):
    """Devuelve la dimensión con ese slug junto con la anterior y la siguiente."""
    for i, dimension in enumerate(DIMENSIONES):
        if dimension["slug"] == slug:
            anterior = DIMENSIONES[i - 1] if i > 0 else None
            siguiente = DIMENSIONES[i + 1] if i < len(DIMENSIONES) - 1 else None
            return dimension, anterior, siguiente
    raise KeyError(slug)


def integrante(numero):
    return next(i for i in INTEGRANTES if i["numero"] == numero)
