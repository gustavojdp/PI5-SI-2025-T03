import pymongo
from bson import json_util
import json

# Função para conectar ao MongoDB
def get_mongo_connection():
    client = pymongo.MongoClient("mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/")  # Conexão com MongoDB
    db = client["PI5"]  # Banco de dados PI5
    return db

# Função para acessar a coleção SHP e pegar documentos
def get_shp_data():
    db = get_mongo_connection()  # Conectar ao banco de dados
    collection = db["SHP"]  # Acessar a coleção SHP
    
    # Realizar uma consulta para pegar todos os documentos
    documentos = collection.find()  # Aqui você pode usar filtros para pegar dados específicos

    # Exibir os dados em formato JSON para ver como estão estruturados
    for doc in documentos:
        print(json.dumps(doc, indent=2, default=json_util.default))

if __name__ == "__main__":
    get_shp_data()
