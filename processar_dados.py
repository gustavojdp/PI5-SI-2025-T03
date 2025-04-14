import spacy
from spacy.tokens import DocBin
import json

# Carregar o modelo spaCy
nlp = spacy.blank("pt")  # Usando um modelo spaCy em branco

# Carregar os dados extraídos do arquivo JSON
with open("dados_extraidos.json", "r") as f:
    dados_extraidos = json.load(f)

# Criar o arquivo DocBin para salvar os dados no formato spaCy
doc_bin = DocBin()

# Iterar pelos dados extraídos
for texto in dados_extraidos["texto"]:
    # Criar um documento spaCy com o novo texto
    doc = nlp(texto)

    # Definir as entidades (Aqui você pode adicionar leis extraídas)
    ents = []
    for lei in dados_extraidos["leis"]:
        start = texto.find(lei)
        end = start + len(lei)
        
        # Verificar se o span é válido e se start e end são posições válidas
        if start != -1 and end != -1 and start < len(texto) and end <= len(texto):
            span = doc.char_span(start, end, label="LEI")
            if span is not None:  # Só adiciona se o span for válido
                ents.append(span)

    # Adicionar as entidades ao doc
    doc.ents = ents  # Adiciona as entidades ao doc

    # Adicionar o doc ao DocBin
    doc_bin.add(doc)

# Salvar os dados de treinamento no arquivo .spacy
doc_bin.to_disk("dados_legislacao.spacy")

print("Arquivo .spacy gerado com sucesso!")
