import glob
import re
import pandas as pd

ruta = glob.glob("data/MEN_ESTADISTICAS*")[0]
df = pd.read_csv(ruta, dtype=str)
df.columns = [c.strip() for c in df.columns]

niveles = ["TECNICA PROFESIONAL", "TECNOLOGICA", "UNIVERSITARIA",
           "ESPECIALIZACION", "MAESTRIA", "DOCTORADO"]


def a_numero(x):
    if pd.isna(x):
        return 0
    x = str(x).strip()
    # formato 129.516,5 -> punto de miles y coma decimal
    if "," in x:
        return float(x.replace(".", "").replace(",", "."))
    # punto como separador de miles: 63.098 -> 63098
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", x):
        return int(x.replace(".", ""))
    # valores como 70 o 70.0
    return float(x)


for c in niveles + ["IES CON OFERTA"]:
    df[c] = df[c].map(a_numero)
df["AÑO"] = df["AÑO"].astype(int)

# cuántos valores traen decimales (en matrícula no deberían existir)
for c in niveles:
    print(c, "- valores con decimales:", len(df[df[c] % 1 != 0]))
print()

cols = ["AÑO", "Código delMunicipio"] + niveles + ["IES CON OFERTA"]
limpio = df.drop_duplicates(subset=cols)

print("Filas originales:", len(df))
print("Filas limpias:", len(limpio))
print()
print("Registros por año:")
print(limpio.groupby("AÑO").size())
print()
print("Matrícula total por año:")
print(limpio.groupby("AÑO")[niveles].sum().sum(axis=1))
print()

rep = limpio[limpio.duplicated(subset=["AÑO", "Código delMunicipio"], keep=False)]
rep = rep.sort_values(["AÑO", "Código delMunicipio"])
print("Filas que aún repiten año + municipio:", len(rep))
print(rep.head(12).to_string())

limpio.to_csv("data/matricula_limpia.csv", index=False, encoding="utf-8-sig")