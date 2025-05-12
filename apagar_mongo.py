from pymongo import MongoClient

client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

print("Conectado ao banco:", db.name)
print("Coleção usada:", collection.name)
print("Total de documentos na coleção:", collection.count_documents({}))

resultado = collection.delete_many({})
print(f"✅ {resultado.deleted_count} documentos removidos da coleção 'coordenadas'.")
