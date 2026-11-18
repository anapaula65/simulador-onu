import pandas as pd
import ast
from itertools import combinations

# 1. Mapeo de códigos a nombres
paises_dict = {
    'US': 'Estados Unidos', 'RU': 'Rusia', 'CN': 'China', 'FR': 'Francia', 'GB': 'Reino Unido',
    'DZ': 'Argelia', 'EC': 'Ecuador', 'GY': 'Guyana', 'JP': 'Japón', 'MT': 'Malta',
    'MZ': 'Mozambique', 'KR': 'República de Corea', 'SL': 'Sierra Leona', 'SI': 'Eslovenia', 'CH': 'Suiza'
}

print("Leyendo el archivo parquet...")
df = pd.read_parquet('data/train-00000-of-00001-63e70a4e57b07742.parquet')

# Buscar la columna de votos (suele llamarse 'votes' o similar)
col_votos = 'Vote' 

if col_votos not in df.columns:
    print("¡Atención! Las columnas son:", df.columns)
    print("Cambia el nombre en la variable 'col_votos' por el correcto.")
    exit()

# Convertir strings a diccionarios si es necesario
def parse_votes(v):
    if isinstance(v, str):
        return ast.literal_eval(v)
    return v

df[col_votos] = df[col_votos].apply(parse_votes)

# 2. Calcular afinidades
afinidades = []
paises_codigos = list(paises_dict.keys())

for p1, p2 in combinations(paises_codigos, 2):
    matches = 0
    mismatches = 0
    
    for _, row in df.iterrows():
        votos = row[col_votos]
        if isinstance(votos, dict) and p1 in votos and p2 in votos:
            v1 = votos[p1]
            v2 = votos[p2]
            # Ignorar si alguno no votó (absent)
            if v1 in ['yes', 'no', 'abstain'] and v2 in ['yes', 'no', 'abstain']:
                if v1 == v2:
                    matches += 1
                else:
                    mismatches += 1
                    
    total = matches + mismatches
    if total > 0:
        afinidad = (matches - mismatches) / total
        afinidad_escalada = (afinidad + 1) / 2
    else:
        afinidad_escalada = 0.5
        
    afinidades.append({
        'pais_a': paises_dict[p1],
        'pais_b': paises_dict[p2],
        'valor': round(afinidad_escalada, 3)
    })

# 3. Guardar a CSV
df_afinidad = pd.DataFrame(afinidades)
df_afinidad.to_csv('data/afinidad_real.csv', index=False)
print("¡Listo! Archivo data/afinidad_real.csv generado con éxito.")
