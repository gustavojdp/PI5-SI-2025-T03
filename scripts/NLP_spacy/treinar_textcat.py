import spacy
from spacy.util import minibatch
from spacy.training.example import Example
import random
import json
import os

# Caminhos
CAMINHO_JSONL = "output/dataset_legislacao_textcat.jsonl"
CAMINHO_MODELO = "modelos/spacy_legislacao_textcat"

# Carrega os dados do JSONL
def carregar_dados(caminho):
    dados = []
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            obj = json.loads(linha.strip())
            dados.append((obj["text"], {"cats": {obj["label"]: 1.0}}))
    return dados

# Dados
dados = carregar_dados(CAMINHO_JSONL)
random.shuffle(dados)

# Separa em treino e validação (80/20)
treino = dados[:int(0.8 * len(dados))]
valid = dados[int(0.8 * len(dados)):]

# Cria o pipeline
nlp = spacy.blank("pt")

# Adiciona o componente TextCategorizer com configuração simples
textcat = nlp.add_pipe("textcat", last=True)

# Adiciona as categorias encontradas
categorias = list({label for _, ex in dados for label in ex["cats"]})
for cat in categorias:
    textcat.add_label(cat)

# Otimizador
optimizer = nlp.begin_training()

# Treinamento
for epoca in range(10):
    losses = {}
    random.shuffle(treino)  # Copia baralhada
    batches = minibatch(treino, size=8)
    for batch in batches:
        textos, anotacoes = zip(*batch)
        exemplos = [Example.from_dict(nlp.make_doc(t), a) for t, a in batch]
        nlp.update(exemplos, drop=0.2, losses=losses)
    print(f"Época {epoca + 1} - Loss: {losses['textcat']:.4f}")

# Salva o modelo
os.makedirs(CAMINHO_MODELO, exist_ok=True)
nlp.to_disk(CAMINHO_MODELO)
print(f"✅ Modelo salvo em '{CAMINHO_MODELO}'")
