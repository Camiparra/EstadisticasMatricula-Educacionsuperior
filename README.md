# Análisis de Matrícula — Educación Superior Colombia

Aplicación web de análisis exploratorio de la matrícula en educación superior
en Colombia, construida con **Flask + Bootstrap**, usando datos abiertos del
Ministerio de Educación Nacional (MEN/SNIES).

---

## Tabla de contenido

- [Integrantes y responsabilidad](#integrantes-y-responsabilidad-principal)
- [Conjunto de datos](#conjunto-de-datos)
- [Despliegue local rápido](#despliegue-local-rápido)
- [Ejecución manual (sin scripts)](#ejecución-manual-sin-scripts)
- [Despliegue en Render](#despliegue-en-render)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Estado actual](#estado-actual)
- [Cómo contribuir](#cómo-contribuir)

---

## Integrantes y responsabilidad principal

| # | Integrante | Correo | Responsabilidad técnica | Dimensión asignada |
|---|------------|--------|---------------------------|----------------------|
| 1 | Camila Parra Berrio | cparrab@ucundinamarca.edu.co | Administración del repositorio (estructura, ramas, revisión de PRs) | Poblacional |
| 2 | Jonathan David Chavarro Segura | jdchavarro@ucundinamarca.edu.co | Estructura del proyecto Flask + Bootstrap | Territorial |
| 3 | Nicolas Suarez Rativa | nsuarezr@ucundinamarca.edu.co | Preparación y publicación en Render | Temporal |
| 4 | Richard Ludim Barajas Parrado | rlbarajas@ucundinamarca.edu.co | Informe técnico en PDF | Relacional y multivariada |

---

## Conjunto de datos

| Campo | Valor |
|---|---|
| **Nombre** | MEN Estadísticas Matrícula por Municipios ES |
| **Tema** | Matrícula en educación superior |
| **Población estudiada** | Estudiantes matriculados en programas de educación superior en Colombia, agregados por municipio y año |
| **Entidad que publica** | Ministerio de Educación Nacional (MEN) — Sistema Nacional de Información de la Educación Superior (SNIES) |
| **URL original** | https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data |
| **Archivo en el repo** | `data/MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv` |
| **Registros** | 19.618 filas (+ encabezado) |
| **Cobertura temporal** | 2005 a 2021 (variable `AÑO`) |
| **Cobertura territorial** | 36 departamentos, 1.834 municipios |
| **Formato** | CSV, separado por comas, comillas en cada valor, miles con punto (`.`) |

### Columnas del archivo

| Columna | Tipo | Rol en el análisis |
|---|---|---|
| `AÑO` | numérica (año) | Variable **temporal** |
| `Código delDepartamento` | texto/código | Identificador territorial |
| `Nombre del Departamento` | categórica | Variable **territorial** (nivel departamento) |
| `Código delMunicipio` | texto/código | Identificador territorial |
| `Nombre del Municipio` | categórica | Variable **territorial** (nivel municipio) |
| `TECNICA PROFESIONAL` | numérica | Matriculados en nivel técnico profesional |
| `TECNOLOGICA` | numérica | Matriculados en nivel tecnológico |
| `UNIVERSITARIA` | numérica | Matriculados en nivel universitario |
| `ESPECIALIZACION` | numérica | Matriculados en especialización |
| `MAESTRIA` | numérica | Matriculados en maestría |
| `DOCTORADO` | numérica | Matriculados en doctorado |
| `IES CON OFERTA` | numérica | Cantidad de instituciones de educación superior con oferta en ese municipio/año |

### Nota técnica importante

El archivo viene en **formato ancho**: cada nivel de formación (técnica,
tecnológica, universitaria, etc.) es su propia columna numérica, en vez de
tener una sola columna categórica tipo "nivel de formación" con su
respectiva columna de matriculados. `components/datos.py` ya se encarga de
limpiar y preparar estas columnas para las cuatro dimensiones; cada
integrante consume los datos ya procesados desde ahí (por ejemplo,
`components/temporal.py` para la dimensión temporal).

---

## Despliegue local rápido

### Requisitos previos

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Python | 3.10 | [python.org/downloads](https://www.python.org/downloads/) |
| Git *(solo si vas a clonar)* | cualquiera | [git-scm.com](https://git-scm.com/) |

> **Windows:** al instalar Python marca **"Add Python to PATH"**.
> **Linux/macOS:** instala también `python3-venv` (`sudo apt install python3-venv` en Debian/Ubuntu).

Clona el repositorio (si no lo tienes ya) y ejecuta el script de tu sistema operativo:

```bash
git clone https://github.com/Camiparra/EstadisticasMatricula-Educacionsuperior.git
cd EstadisticasMatricula-Educacionsuperior
```

**Windows (PowerShell o CMD):**

```bat
setup.bat
```

**Linux / macOS (Terminal):**

```bash
chmod +x setup.sh
./setup.sh
```

El script crea el entorno virtual, instala las dependencias de
`requirements.txt` y arranca la app. Abre tu navegador en
**http://127.0.0.1:5000**. Para detenerla, presiona `Ctrl+C`.

---

## Ejecución manual (sin scripts)

Si prefieres no usar los scripts o tienes algún conflicto:

```bash
# 1. Crear entorno virtual
python -m venv venv          # Windows
python3 -m venv venv         # Linux/macOS

# 2. Activar el entorno virtual
venv\Scripts\activate        # Windows CMD/PowerShell
source venv/bin/activate     # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Lanzar la aplicación
python app.py
```

Abre **http://127.0.0.1:5000** en el navegador.

---

## Despliegue en Render

La aplicación está lista para desplegarse en [Render](https://render.com/) (PaaS gratuito), de dos formas:

### Opción A — Blueprint (recomendada, usa `render.yaml`)

1. Crea una cuenta en [render.com](https://render.com/) o inicia sesión con GitHub.
2. En el dashboard: **New +** → **Blueprint**.
3. Selecciona el repositorio `EstadisticasMatricula-Educacionsuperior`.
4. Render detecta `render.yaml` automáticamente y configura el build (`pip install -r requirements.txt`) y el arranque (`gunicorn app:app`) sin pasos adicionales.
5. Espera a que termine el build; el servicio queda en una URL tipo `https://tu-app.onrender.com`.

### Opción B — Web Service manual

1. **New +** → **Web Service** → conecta el repositorio.
2. Configura:

| Campo | Valor |
|---|---|
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | Free |

3. **Create Web Service**.

> `requirements.txt` ya incluye `gunicorn` (servidor WSGI de producción) y `matplotlib` (usado por la dimensión temporal para generar las gráficas en el servidor).

---

## Estructura del repositorio

```
.
├── README.md
├── CONTRIBUTING.md          # reglas de ramas, commits y pull requests
├── LICENSE
├── .gitignore
├── setup.bat                # script de setup para Windows
├── setup.sh                 # script de setup para Linux/macOS
├── app.py                   # entrada principal de Flask
├── requirements.txt         # dependencias Python
├── render.yaml               # Blueprint de despliegue en Render
├── .python-version
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── components/               # lógica reutilizable del backend
│   ├── datos.py               # carga y limpieza del CSV
│   ├── temporal.py            # datos y gráficas (matplotlib) de la dimensión temporal
│   └── sitio.py                # metadatos de dimensiones e integrantes
├── data/                      # dataset CSV (MEN/SNIES)
├── docs/                      # evidencias e insumos para el informe técnico
├── static/
│   ├── css/                    # hojas de estilo
│   ├── js/                     # scripts del frontend
│   └── img/
└── templates/                # vistas Jinja2
    ├── base.html
    ├── index.html
    ├── 404.html
    ├── dimensiones/
    └── partials/
```

---

## Estado actual

- [x] Repositorio creado y estructura inicial definida
- [x] Rama principal `main` configurada
- [x] Reglas de integración documentadas (`CONTRIBUTING.md`)
- [x] Dataset descargado y validado (19.618 registros, cumple los requisitos mínimos)
- [x] Aplicación Flask base + componentes listos
- [x] Scripts de despliegue local (`setup.bat` / `setup.sh`)
- [x] Dimensión temporal desarrollada (Integrante 3)
- [ ] Dimensiones poblacional, territorial y multivariada desarrolladas
- [ ] Aplicación publicada en Render
- [ ] Informe técnico en PDF

---

## Cómo contribuir

Lee **[CONTRIBUTING.md](./CONTRIBUTING.md)** antes de programar: ahí están las
convenciones de ramas (`feature/dimension-<nombre>`), formato de commits
(`feat:`, `fix:`, `docs:`…) y el proceso de pull requests.

```bash
git checkout -b feature/dimension-<tu-dimension>
```
