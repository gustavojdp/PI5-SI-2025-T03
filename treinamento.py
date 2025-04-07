#from pymongo import MongoClient
#import re
#import json
#from bson import json_util

# Conectar ao MongoDB
#url = "mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/?retryWrites=true&w=majority&appName=PI5"
#client = MongoClient(url)
#db = client["PI5"]
#collection = db["SHP"]

#docs = collection.find()

#TRAIN_DATA = []

#for doc in docs:
    #props = doc.get("properties", {})
    #texto = " ".join(f"{key}: {value}" for key, value in props.items())

    # Procura padrões tipo ZCOR_1, ZEIS_2, etc.
    #for match in re.finditer(r"\bZ[A-Z]+(?:_[0-9a-zA-Z]+)?\b", texto):
        #start, end = match.span()
        #TRAIN_DATA.append((texto, {"entities": [(start, end, "ZONA")]}))
        #break  # Um exemplo por texto já basta
    
#for i, doc in enumerate(collection.find().limit(5)):
    #props = doc.get("properties", {})
    #print(f"Documento {i+1} - Propriedades:")
    #for key, value in props.items():
        #print(f"  {key}: {value}")
    #print("\n" + "-"*30 + "\n")


# Visualiza exemplo
#print(TRAIN_DATA[:5])

#print(texto[0])

#doc = collection.find_one()
#print(json_util.dumps(doc, indent=2, ensure_ascii=False))



