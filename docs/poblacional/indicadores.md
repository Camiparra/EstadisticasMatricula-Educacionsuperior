# Dimension poblacional

## Responsable

Integrante 1

## Fuente de datos

Ministerio de Educacion Nacional (MEN), estadisticas de matricula por municipio.

El dataset contiene informacion de matricula de educacion superior por municipio para el periodo 2005-2021.

## Indicadores poblacionales

### Indicador 1. Matricula total por año

Mide la cantidad total de estudiantes matriculados en educacion superior para cada año.

La matricula total se obtiene sumando los siguientes niveles de formacion:

- Tecnica profesional
- Tecnologica
- Universitaria
- Especializacion
- Maestria
- Doctorado

Este indicador permite observar la evolucion de la matricula a traves del tiempo.

### Indicador 2. Matricula por nivel de formacion

Compara la cantidad de estudiantes matriculados en cada nivel de formacion:

- Tecnica profesional
- Tecnologica
- Universitaria
- Especializacion
- Maestria
- Doctorado

Este indicador permite identificar como se distribuye la matricula entre los diferentes niveles de educacion superior.

### Indicador 3. Matricula total por municipio

Mide la cantidad total de estudiantes matriculados en cada municipio durante el periodo analizado.

Este indicador permite observar la distribucion territorial de la matricula y las diferencias entre municipios.

## Visualizaciones

Los tres indicadores se representaran mediante visualizaciones que permitan identificar tendencias, distribuciones y diferencias territoriales.

## Filtros interactivos

Los tableros incluiran como minimo los siguientes filtros:

- Año
- Departamento

## Consideraciones sobre los datos

Las columnas de matricula utilizan el punto como separador de miles en los registros del archivo. Por esta razon, los valores deben convertirse correctamente antes de realizar las operaciones y visualizaciones.

La columna "Nombre del Departamento" contiene codigos de departamento en los registros revisados, por lo que esta caracteristica debe tenerse en cuenta durante la limpieza y el analisis.

## Estado

Indicadores definidos. Pendiente desarrollar las visualizaciones, filtros e interpretacion de resultados.

## Resultados iniciales

### Indicador 1. Matricula total por año

La matricula total calculada para cada año es:

| Año | Matricula total |
|---:|---:|
| 2005 | 2.393.380 |
| 2006 | 2.563.362 |
| 2007 | 2.725.018 |
| 2008 | 2.983.062 |
| 2009 | 3.186.422 |
| 2010 | 3.348.042 |
| 2011 | 3.719.384 |
| 2012 | 2.766.502 |
| 2013 | 4.185.782 |
| 2014 | 4.441.304 |
| 2015 | 4.587.100 |
| 2016 | 4.788.868 |
| 2017 | 4.892.628 |
| 2018 | 4.880.734 |
| 2019 | 4.792.500 |
| 2020 | 4.711.206 |
| 2021 | 2.448.271 |

El valor mas alto del periodo se presenta en 2017, con 4.892.628 matriculas registradas.

### Indicador 2. Matricula por nivel de formacion

La matricula acumulada durante el periodo 2005-2021 es:

| Nivel de formacion | Matricula acumulada |
|---|---:|
| Universitaria | 40.388.421 |
| Tecnologica | 15.339.173 |
| Tecnica profesional | 3.678.606 |
| Especializacion | 2.546.736 |
| Maestria | 1.334.433 |
| Doctorado | 126.196 |

La formacion universitaria concentra la mayor cantidad de matriculas registradas en el periodo, mientras que doctorado presenta la menor cantidad.

### Indicador 3. Matricula por municipio

Para evitar duplicaciones causadas por diferentes formas de escritura del nombre de un municipio, el calculo se realizo utilizando el codigo del municipio como identificador.

Los diez municipios con mayor matricula acumulada son:

| Municipio | Matricula acumulada |
|---|---:|
| Bogota D.C. | 19.622.795 |
| Medellin | 6.969.681 |
| Cali | 3.567.797 |
| Barranquilla | 3.368.937 |
| Bucaramanga | 2.840.590 |
| Cartagena de Indias | 1.902.117 |
| Manizales | 1.222.797 |
| Pereira | 1.222.693 |
| San Jose de Cucuta | 1.141.300 |
| Ibague | 1.129.117 |

Los resultados muestran una concentracion importante de la matricula acumulada en municipios con grandes centros urbanos y amplia oferta de educacion superior.

## Observaciones iniciales

- La matricula presenta una tendencia general de crecimiento entre 2005 y 2017, aunque existen variaciones en algunos años.
- La matricula universitaria representa la mayor cantidad acumulada entre los niveles de formacion analizados.
- La matricula esta concentrada en un grupo reducido de municipios, especialmente Bogota y Medellin.
- El valor registrado para 2021 presenta una disminucion considerable frente a los años inmediatamente anteriores. El dataset por si solo no permite establecer la causa de esta variacion.

## Nota metodologica

Los valores de matricula fueron interpretados considerando el punto como separador de miles, de acuerdo con el formato indicado en la documentacion del dataset.

La matricula acumulada por municipio corresponde a la suma de los registros del periodo 2005-2021 y no representa el numero de estudiantes unicos.

El codigo del municipio se utilizo como identificador para evitar que diferentes formas de escritura del mismo municipio fueran tratadas como entidades diferentes.
