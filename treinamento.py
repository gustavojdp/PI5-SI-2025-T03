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

import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
import fitz  # PyMuPDF
import re
import torch


print(torch.cuda.is_available())  # Deve retornar: True
print(torch.cuda.get_device_name(0))  # Nome da sua GPU


# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Função para encontrar zonas no texto
def find_zonas(text):
    # Exemplo: padrões comuns de zona como ZR, ZC, ZPI, etc.
    pattern = r'\b(ZR|ZC|ZPI|ZEU|ZEMP|ZIS|ZIU|ZOD|ZCOR|ZDE|ZMP|ZP|ZRM)\b'
    matches = [(m.start(), m.end(), "ZONA") for m in re.finditer(pattern, text)]
    return matches

# Função para preparar os dados para o spaCy
def prepare_training_data(text, entities):
    nlp = spacy.blank("pt")  # ou "en" se o texto estiver em inglês
    doc = nlp.make_doc(text)

    # Garante que não tenha sobreposição de entidades
    spans = [doc.char_span(start, end, label=label) for start, end, label in entities]
    spans = [span for span in spans if span is not None]
    filtered = filter_spans(spans)
    doc.ents = filtered

    doc_bin = DocBin()
    doc_bin.add(doc)
    return doc_bin

# Caminho do PDF
pdf_path = "C:/Users/bruno/Downloads/texto de lei pdf.pdf"

# Passo 1: Extrair texto
texto = extract_text_from_pdf(pdf_path)

# Passo 2: Encontrar entidades
entidades = find_zonas(texto)

# Passo 3: Preparar dados de treino
doc_bin = prepare_training_data(texto, entidades)

# Passo 4: Salvar em disco
doc_bin.to_disk("zona_train.spacy")

print("Dados de treinamento salvos em 'zona_train.spacy'. Agora você pode treinar com spaCy.")



