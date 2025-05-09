import json
from pymongo import MongoClient

# Conexão MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Carrega o JSON com as zonas extraídas
with open('output/zonas_legislacao_filtradas.json', encoding='utf-8') as f:
    zonas_legislacao = json.load(f)

count = 0

for chave in zonas_legislacao.keys():
    if '-' not in chave:
        continue

    nome_zona, codigo_zona = map(str.strip, chave.split('-'))

    result = collection.update_many(
        {
            "$or": [
                {"properties.duos": codigo_zona},
                {"properties.DUOS": codigo_zona}
            ]
        },
        {
            "$set": {
                "properties.codigo_zona": codigo_zona,
                "properties.nome_zona": nome_zona
            }
        }
    )
    count += result.modified_count

print(f"✅ Total de zonas atualizadas com base em DUOS: {count}")
