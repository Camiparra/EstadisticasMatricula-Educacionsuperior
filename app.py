"""Aplicación Flask del análisis de matrícula en educación superior (MEN - SNIES).

Punto de entrada del proyecto. Las vistas HTML viven en ``templates/`` y los
recursos estáticos (CSS, JS, imágenes) en ``static/``.

Ejecución local:
    python app.py
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "Análisis de matrícula en educación superior - aplicación en construcción"


if __name__ == "__main__":
    app.run(debug=True)
