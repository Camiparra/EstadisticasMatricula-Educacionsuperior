# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the development server (http://127.0.0.1:5000)
python app.py

# Install dependencies
pip install -r requirements.txt
```

There are no tests, no linting configuration, and no build step. Bootstrap is loaded from a CDN — no frontend tooling required.

## Architecture

**Entry point**: `app.py` — a single-file Flask app. It defines four routes (`/dimension/poblacional`, `/dimension/territorial`, `/dimension/temporal`, `/dimension/multivariada`) plus the home route (`/`). All four dimension routes call `render_dimension(slug, **contexto)`, which looks up the dimension metadata and renders `templates/dimensiones/<slug>.html`.

**`components/` — shared backend logic:**
- `datos.py`: loads, cleans, and caches the CSV. The two public functions are `cargar_datos()` (wide format) and `cargar_datos_largo()` (long/melted format). Both are `@cache`-decorated — never modify the returned DataFrame in place; call `.copy()` first. `resumen_general()` computes aggregate stats for the home page.
- `sitio.py`: pure configuration — `DIMENSIONES` list, `INTEGRANTES`, `DATASET`, `SECCIONES_DIMENSION`, and helper functions `buscar_dimension(slug)` and `integrante(numero)`. A change here affects every template that uses the context processor.

**Data (`data/`)**: one CSV file, `MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv`. 19,618 rows, 2005–2021, 36 departments, 1,834 municipalities, 6 enrollment level columns. Known quirks handled in `datos.py`:
- Thousands separator is `.` (not comma); decimals use `,`.
- The raw file contains a near-duplicate block of rows (same data, different municipality name spelling) — deduplication is done on all columns except `municipio`.
- `Nombre del Departamento` contains the DANE code, not the name; the mapping lives in `DEPARTAMENTOS` dict.
- Some rows have `"-"` as department/municipality code ("NO IDENTIFICADO").

**Template convention**: each dimension has a template at `templates/dimensiones/<slug>.html` and a route function in `app.py` that calls `render_dimension(slug)`. To add data to a dimension's template, compute it in its route function and pass it as keyword arguments to `render_dimension()`.

**Column naming**: `datos.py` renames CSV columns to snake_case aliases defined in `COLUMNAS`. Always use these aliases (`anio`, `cod_departamento`, `departamento`, `cod_municipio`, `municipio`, `tecnica_profesional`, `tecnologica`, `universitaria`, `especializacion`, `maestria`, `doctorado`, `ies_con_oferta`, `matricula_total`). The long-format DataFrame adds `nivel_formacion` and `matriculados`.

## Branch and PR conventions

One branch per dimension (see `CONTRIBUTING.md`). No direct pushes to `main`. PR template is in `.github/PULL_REQUEST_TEMPLATE.md`. The reviewer is Integrante 1 (Camila Parra).

Commit format: `tipo: descripción corta en minúsculas` — types are `feat`, `fix`, `style`, `docs`, `chore`.
