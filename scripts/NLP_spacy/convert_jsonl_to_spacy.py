import spacy
from spacy.tokens import DocBin
import json

nlp = spacy.blank("pt")  # Modelo vazio só para criar Docs
doc_bin = DocBin()

with open("dataset_train.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        example = json.loads(line)
        text = example["text"]
        cats = example["cats"]

        doc = nlp.make_doc(text)
        doc.cats = cats  # Anotações de categorias

        doc_bin.add(doc)

doc_bin.to_disk("dataset_train.spacy")
print("Arquivo dataset_train.spacy criado com sucesso.")
