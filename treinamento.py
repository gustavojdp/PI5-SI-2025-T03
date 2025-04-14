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

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Função para encontrar zonas no texto
def find_zonas(text):
    pattern = r'\b(ZR|ZC|ZPI|ZEU|ZEMP|ZIS|ZIU|ZOD|ZCOR|ZDE|ZMP|ZP|ZRM)\b'
    matches = [(m.start(), m.end(), "ZONA") for m in re.finditer(pattern, text)]
    return matches

# Função para criar um Doc com entidades
def create_doc(nlp, text, entities):
    doc = nlp.make_doc(text)
    spans = [doc.char_span(start, end, label=label) for start, end, label in entities]
    spans = [span for span in spans if span is not None]
    filtered = filter_spans(spans)
    doc.ents = filtered
    return doc

# Inicializa o idioma
nlp = spacy.blank("pt")
doc_bin = DocBin()

# Lista de caminhos de PDFs
pdf_paths = [
    "C:/Users/bruno/Downloads/texto de lei pdf.pdf",
    "C:/Users/bruno/Downloads/PlanoDiretorEstratégico.pdf"  
]

# Processa cada PDF
for path in pdf_paths:
    print(f"Processando: {path}")
    texto = extract_text_from_pdf(path)
    entidades = find_zonas(texto)
    doc = create_doc(nlp, texto, entidades)
    doc_bin.add(doc)

# Salva o arquivo final combinado
doc_bin.to_disk("zona_train.spacy")
print("Todos os dados de treinamento salvos em 'zona_train.spacy'")



