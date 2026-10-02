# Dimensión poblacional

## Responsable

Integrante 1

## Fuente de datos

Ministerio de Educación Nacional (MEN), estadísticas de matrícula por municipio.

El dataset contiene información de matrícula de educación superior por municipio para el periodo 2005-2021.

## Indicadores poblacionales

### Indicador 1. Matrícula total por año

Mide la cantidad total de estudiantes matriculados en educación superior para cada año. Se obtiene sumando los seis niveles de formación: técnica profesional, tecnológica, universitaria, especialización, maestría y doctorado.

### Indicador 2. Matrícula por nivel de formación

Compara la cantidad de estudiantes matriculados en cada nivel de formación y permite ver cómo se distribuye la matrícula entre los niveles de educación superior.

### Indicador 3. Matrícula total por municipio

Mide la cantidad total de estudiantes matriculados en cada municipio durante el periodo analizado y permite observar las diferencias territoriales.

## Visualizaciones

Los tres indicadores se representarán mediante visualizaciones que permitan identificar tendencias, distribuciones y diferencias territoriales.

## Filtros interactivos

Los tableros incluirán como mínimo los siguientes filtros:

- Año
- Departamento

## Consideraciones sobre los datos

Las columnas de matrícula usan el punto como separador de miles, y algunos valores traen además coma decimal, por lo que se convirtieron antes de hacer los cálculos.

La columna "Nombre del Departamento" contiene códigos de departamento en los registros revisados, por lo que el filtro por departamento se hizo con el código.

El archivo original traía registros repetidos: el mismo municipio y año aparecía dos veces con exactamente los mismos valores, pero con el nombre escrito distinto (por ejemplo, "BOGOTÁ D.C." y "Bogotá, D.C."). Por eso los totales de la primera versión estaban inflados en los años 2005-2020. Se eliminaron las filas repetidas comparando año, código del municipio y todos los valores de matrícula. Se pasó de 19.618 a 9.989 filas y el resultado se guardó en `data/matricula_limpia.csv`.

## Resultados

### Indicador 1. Matrícula total por año

| Año | Matrícula total |
|---:|---:|
| 2005 | 1.196.690 |
| 2006 | 1.281.681 |
| 2007 | 1.362.509 |
| 2008 | 1.491.531 |
| 2009 | 1.593.211 |
| 2010 | 1.674.021 |
| 2011 | 1.859.692 |
| 2012 | 1.929.587 |
| 2013 | 2.092.891 |
| 2014 | 2.220.652 |
| 2015 | 2.293.550 |
| 2016 | 2.394.434 |
| 2017 | 2.446.314 |
| 2018 | 2.440.367 |
| 2019 | 2.396.250 |
| 2020 | 2.355.603 |
| 2021 | 2.448.271 |

La matrícula pasó de 1.196.690 en 2005 a 2.448.271 en 2021, es decir, se duplicó en el periodo. El valor más alto es el de 2021, aunque casi igual al de 2017.

### Indicador 2. Matrícula por nivel de formación

Matrícula acumulada durante el periodo 2005-2021:

| Nivel de formación | Matrícula acumulada |
|---|---:|
| Universitaria | 21.393.992 |
| Tecnológica | 8.107.942 |
| Técnica profesional | 1.876.352 |
| Especialización | 1.328.761 |
| Maestría | 703.621 |
| Doctorado | 66.585 |

La formación universitaria concentra cerca del 64 % de la matrícula acumulada y la tecnológica cerca del 24 %. Doctorado es el nivel con menos matrícula.

### Indicador 3. Matrícula por municipio

El cálculo se hizo con el código del municipio como identificador, para que las diferentes formas de escribir un nombre no se cuenten como municipios distintos.

Los diez municipios con mayor matrícula acumulada son:

| Municipio | Matrícula acumulada |
|---|---:|
| Bogotá D.C. | 10.739.236 |
| Medellín | 3.609.838 |
| Cali | 1.847.369 |
| Barranquilla | 1.745.912 |
| Bucaramanga | 1.468.865 |
| Cartagena de Indias | 1.022.205 |
| Pereira | 633.773 |
| Manizales | 632.345 |
| San José de Cúcuta | 591.760 |
| Ibagué | 583.790 |

Bogotá concentra cerca de la tercera parte de la matrícula acumulada, y los diez municipios de la tabla suman más de dos terceras partes. La matrícula está muy concentrada en las grandes ciudades.

## Observaciones

- La matrícula crece de forma sostenida entre 2005 y 2017.
- Entre 2017 y 2021 se mantiene alrededor de 2,4 millones, con una baja leve en 2019 y 2020 y una recuperación en 2021.
- La matrícula universitaria es la más grande, seguida por la tecnológica.
- La matrícula se concentra en pocos municipios, sobre todo Bogotá y Medellín.

## Limitaciones y nota metodológica

La matrícula acumulada corresponde a la suma de los registros del periodo 2005-2021 y no representa el número de estudiantes únicos, porque una misma persona se cuenta en cada año que está matriculada.

Algunos municipios aparecen más de una vez en el mismo año con valores distintos (por ejemplo, con distinto número de IES). No se tomaron como duplicados y se sumaron, porque parecen reportes parciales del mismo municipio. Por eso una fila del dataset no equivale a un municipio.

Dos registros de 2012 (Bogotá y Cartagena) traen valores con decimales, lo cual no tiene sentido en una cantidad de personas. Se dejaron tal cual porque la diferencia en el total es menor a una persona, y por eso el total de 2012 se muestra redondeado.

## Estado

Indicadores calculados con los datos limpios. Pendiente desarrollar las visualizaciones, los filtros y la interpretación en el tablero.