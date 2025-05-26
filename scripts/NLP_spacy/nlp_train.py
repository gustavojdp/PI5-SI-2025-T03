import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import json
import os

# Caminho para seu arquivo JSON
caminho_json = "output/train_data_zonas_expandido.json"

# Verifica se o arquivo existe
if not os.path.exists(caminho_json):
    raise FileNotFoundError(f"Arquivo {caminho_json} não encontrado.")

# Carrega os dados de treinamento
with open(caminho_json, "r", encoding="utf-8") as f:
    train_data_json = json.load(f)

# Converte para o formato spaCy: (text, {"cats": {...}})
train_data = [(item["text"], {"cats": item["cats"]}) for item in train_data_json]

# Cria modelo spaCy vazio para português
nlp = spacy.blank("pt")

# Adiciona componente de classificação de texto
textcat = nlp.add_pipe("textcat")
textcat.cfg["exclusive_classes"] = True
textcat.cfg["architecture"] = "bow"

# Adiciona as labels
labels = list(train_data[0][1]["cats"].keys())
for label in labels:
    textcat.add_label(label)

# Inicia o treinamento
optimizer = nlp.begin_training()
n_iter = 30

print("Iniciando treinamento...")
for i in range(n_iter):
    random.shuffle(train_data)
    losses = {}
    batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.5))
    for batch in batches:
        examples = []
        for text, annotations in batch:
            doc = nlp.make_doc(text)
            examples.append(Example.from_dict(doc, annotations))
        nlp.update(examples, sgd=optimizer, losses=losses)
    print(f"Iteração {i+1}/{n_iter} - Losses: {losses}")

# Salva o modelo
output_dir = "modelos/spacy_zonas"
nlp.to_disk(output_dir)
print(f"✅ Modelo salvo em: {output_dir}")
