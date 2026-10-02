import pandas as pd

df = pd.read_csv("data/matricula_limpia.csv",
                 dtype={"Código delMunicipio": str, "Código delDepartamento": str})

niveles = ["TECNICA PROFESIONAL", "TECNOLOGICA", "UNIVERSITARIA",
           "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"]


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


# Filas con valores decimales
raros = df[(df[niveles] % 1 != 0).any(axis=1)]
print("Filas con decimales:", len(raros))
print(raros.to_string())
print()

df["TOTAL"] = df[niveles].sum(axis=1)

print("Indicador 1: matrícula total por año")
for anio, v in df.groupby("AÑO")["TOTAL"].sum().items():
    print(anio, fmt(v))
print()

print("Indicador 2: matrícula acumulada por nivel de formación")
for nivel, v in df[niveles].sum().sort_values(ascending=False).items():
    print(nivel, fmt(v))
print()

print("Indicador 3: 10 municipios con mayor matrícula acumulada")
nombres = df.groupby("Código delMunicipio")["Nombre del Municipio"].first()
top = df.groupby("Código delMunicipio")["TOTAL"].sum().nlargest(10)
for codigo, v in top.items():
    print(nombres[codigo], fmt(v))