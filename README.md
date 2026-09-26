# Análisis de Población — Datos Abiertos Colombia

Repositorio del proyecto de análisis exploratorio de una población colombiana,
usando un conjunto de datos del Portal Nacional de Datos Abiertos, integrado
en una aplicación Flask + Bootstrap.

> Este README se irá completando a medida que el equipo avance. Por ahora
> contiene solo lo necesario para arrancar: estructura del repositorio,
> integrantes y estado del proyecto.

## Integrantes y responsabilidad principal

| # | Integrante | Correo | Responsabilidad técnica | Dimensión asignada |
|---|------------|--------|---------------------------|----------------------|
| 1 | Camila Parra Berrio | cparrab@ucundinamarca.edu.co | Administración del repositorio (estructura, ramas, revisión de PRs) | Poblacional |
| 2 | Jonathan David Chavarro Segura | jdchavarro@ucundinamarca.edu.co | Estructura del proyecto Flask + Bootstrap | Territorial |
| 3 | Nicolas Suarez Rativa | nsuarezr@ucundinamarca.edu.co | Preparación y publicación en Render | Temporal |
| 4 | Richard Ludim Barajas Parrado | rlbarajas@ucundinamarca.edu.co | Informe técnico en PDF | Relacional y multivariada |

## Conjunto de datos

| Campo | Valor |
|---|---|
| Nombre | MEN Estadísticas Matrícula por Municipios ES |
| Tema | Matrícula en educación superior |
| Población estudiada | Estudiantes matriculados en programas de educación superior en Colombia, agregados por municipio y año |
| Entidad que publica | Ministerio de Educación Nacional (MEN) — Sistema Nacional de Información de la Educación Superior (SNIES) |
| URL original | https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data |
| Archivo en el repo | `data/MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv` |
| Registros | 19.618 filas (+ encabezado) |
| Cobertura temporal | 2005 a 2021 (variable `AÑO`) |
| Cobertura territorial | 36 departamentos, 1.834 municipios |
| Formato | CSV, separado por comas, comillas en cada valor, miles con punto (`.`) |

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
respectiva columna de matriculados. Esto cumple igual los requisitos de la
guía (hay variable territorial, temporal y numérica de sobra), pero **para
la dimensión poblacional y la multivariada conviene "despivotar" el archivo**
(pasar de ancho a largo, con `pandas.melt`) para obtener una columna
categórica real `nivel_formacion` y una columna numérica `matriculados`.
Esto se resolverá en la fase de desarrollo de Flask (Integrante 2 / config.py),
no es necesario hacerlo ahora.

## Estructura del repositorio (esqueleto inicial)

```
.
├── README.md
├── CONTRIBUTING.md        # reglas para la integración del trabajo (leer antes de programar)
├── LICENSE
├── .gitignore
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── components/            # lógica reutilizable del backend (Integrante 2 la irá llenando)
├── data/                  # aquí va el dataset descargado (no se versiona hasta confirmarlo)
├── docs/                  # evidencias e insumos para el informe técnico (Integrante 4)
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── templates/             # vistas HTML de la app Flask
```

Las carpetas están vacías por ahora (marcadas con `.gitkeep`); cada integrante
las irá poblando desde su propia rama según el flujo descrito en
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Estado actual

- [x] Repositorio creado y estructura inicial definida
- [x] Rama principal `main` configurada
- [x] Reglas de integración documentadas (`CONTRIBUTING.md`)
- [ ] Colaboradores agregados al repositorio
- [x] Dataset descargado y validado (19.618 registros, cumple los requisitos mínimos)
- [ ] Aplicación Flask desarrollada por dimensión
- [ ] Aplicación publicada en Render
- [ ] Informe técnico en PDF

## Cómo empezar (para cualquier integrante)

```bash
git clone <URL-del-repositorio>
cd <carpeta-del-repositorio>
git checkout -b feature/dimension-<tu-dimension>
```

Antes de programar, lee **[CONTRIBUTING.md](./CONTRIBUTING.md)**: ahí están las
reglas de ramas, commits y pull requests que el Integrante 1 debe verificar
en cada revisión.
