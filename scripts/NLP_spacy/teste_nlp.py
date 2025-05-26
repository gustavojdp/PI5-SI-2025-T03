import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import json
import random

# Carrega os dados de treinamento gerados
with open("output/train_data_legislacao_zonas.json", "r", encoding="utf-8") as f:
    train_data_json = json.load(f)

train_data = [(item["text"], {"cats": item["cats"]}) for item in train_data_json]

# Cria modelo spaCy vazio para português
nlp = spacy.blank("pt")

# Adiciona o pipeline de classificação
textcat = nlp.add_pipe("textcat_multilabel", last=True)

for label in train_data[0][1]["cats"].keys():
    textcat.add_label(label)

# Inicia o treinamento
nlp.initialize()

n_iter = 30
for i in range(n_iter):
    random.shuffle(train_data)
    losses = {}
    batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.5))
    for batch in batches:
        examples = [Example.from_dict(nlp.make_doc(text), ann) for text, ann in batch]
        nlp.update(examples, losses=losses)
    print(f"Iteração {i+1}/{n_iter} - Losses: {losses}")

# Salvar modelo
output_dir = "modelos/spacy_zonas_refinado"
nlp.to_disk(output_dir)
print(f"✅ Modelo salvo em {output_dir}")
