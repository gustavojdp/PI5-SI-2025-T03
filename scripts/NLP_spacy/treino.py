import spacy
from spacy.util import minibatch
from spacy.training import Example
import random
import json
import os

# Caminho do dataset e do modelo
CAMINHO_JSONL = "dataset_train_categorias.jsonl"
CAMINHO_MODELO = "modelo_zonas_urbanas"

# 1. Cria modelo em branco para português
nlp = spacy.blank("pt")

# 2. Adiciona o sentencizer
nlp.add_pipe("sentencizer")

# 3. Adiciona o textcat_multilabel
textcat = nlp.add_pipe("textcat_multilabel", last=True)

# 4. Lê labels do dataset
labels = set()
with open(CAMINHO_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        cats = json.loads(line)["cats"]
        for label in cats:
            labels.add(label)

# 5. Adiciona as labels ao textcat
for label in labels:
    textcat.add_label(label)

# 6. Carrega os dados de treino
train_data = []
with open(CAMINHO_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        train_data.append((item["text"], {"cats": item["cats"]}))

# 7. Inicializa o otimizador
optimizer = nlp.initialize()

# 8. Treinamento
for i in range(50):  # Número de épocas
    random.shuffle(train_data)
    losses = {}
    batches = minibatch(train_data, size=8)
    for batch in batches:
        examples = []
        for text, ann in batch:
            doc = nlp.make_doc(text)
            examples.append(Example.from_dict(doc, ann))
        nlp.update(examples, sgd=optimizer, losses=losses)
    print(f"🧠 Época {i+1} - Perda: {losses['textcat_multilabel']:.4f}")

# 9. Salva o modelo no diretório
if os.path.exists(CAMINHO_MODELO):
    import shutil
    shutil.rmtree(CAMINHO_MODELO)

nlp.to_disk(CAMINHO_MODELO)
print(f"✅ Modelo salvo em: {CAMINHO_MODELO}")
