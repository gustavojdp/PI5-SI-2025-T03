
import json
from pymongo import MongoClient

# Conectar ao MongoDB
client = MongoClient("mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/")
db = client["campinas"]
collection = db["zonas"]

# Limpar coleção antes de importar (opcional)
collection.delete_many({})

# Carregar GeoJSON
with open("D:/P.I.5/campinas_zoneamento/campinas_zoneamento.geojson", encoding="utf-8") as f:
    data = json.load(f)

# Inserir no Mongo
for feature in data["features"]:
    doc = {
        "nome_zona": feature["properties"]["nome_zona"],
        "codigo_zona": feature["properties"]["codigo_zona"],
        "geometry": feature["geometry"],
        "type": "Feature"
    }
    collection.insert_one(doc)

print("✅ Base de zonas de Campinas importada com sucesso!")
