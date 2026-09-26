# Carpeta /data

## Archivo actual

`MEN_ESTADISTICAS_MATRICULA_POR_MUNICIPIOS_ES_20260925.csv`

Matrícula de educación superior por municipio, publicado por el Ministerio
de Educación Nacional (MEN). Descargado de:
https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS_ES/y9ga-zwzy/about_data

- **Registros:** 19.618 filas
- **Columnas:** 12 (`AÑO`, códigos y nombres de departamento/municipio, 6
  niveles de formación como columnas numéricas, e `IES CON OFERTA`)
- **Cobertura temporal:** 2005–2021
- **Cobertura territorial:** 36 departamentos, 1.834 municipios
- **Formato:** CSV con comillas, separador coma, miles con punto (`.`)

Ficha completa y detalle de columnas en el `README.md` de la raíz del
repositorio, sección "Conjunto de datos".

## Pendiente para la fase de desarrollo (Integrante 2)

Al construir `config.py`, tener en cuenta que el archivo viene en **formato
ancho** (un nivel de formación por columna). Para que las dimensiones
poblacional y multivariada tengan una variable categórica real (`nivel_formacion`)
y no seis columnas numéricas sueltas, conviene transformar el archivo a
formato largo con `pandas.melt` antes de calcular indicadores y gráficas, por
ejemplo:

```python
id_vars = ["AÑO", "Nombre del Departamento", "Nombre del Municipio"]
value_vars = ["TECNICA PROFESIONAL", "TECNOLOGICA", "UNIVERSITARIA",
              "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"]
df_largo = df.melt(id_vars=id_vars, value_vars=value_vars,
                    var_name="nivel_formacion", value_name="matriculados")
```

(Esto es solo referencia para cuando se arme `app.py` — no es necesario
hacerlo en esta etapa de estructura del repositorio.)
