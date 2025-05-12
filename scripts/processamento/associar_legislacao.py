import json
from pymongo import MongoClient

# Caminho para o arquivo de legislações extraídas
CAMINHO_JSON = "output/zonas_legislacao_extraida.json"

# Carrega os dados do JSON
with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Conecta ao MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Atualiza os documentos com a legislação correspondente
atualizados = 0
nao_encontrados = []

for codigo_zona, trechos in legislacoes.items():
    resultado = collection.update_many(
        {"properties.duos": codigo_zona},
        {"$set": {"properties.legislacao": trechos}}
    )
    if resultado.matched_count > 0:
        atualizados += resultado.modified_count
    else:
        nao_encontrados.append(codigo_zona)

print(f"✅ {atualizados} documentos atualizados com a legislação.")
if nao_encontrados:
    print("⚠️ Zonas não encontradas no MongoDB:", nao_encontrados)
