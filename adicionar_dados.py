import spacy
from spacy.tokens import DocBin

# Carregar o arquivo .spacy existente
doc_bin = DocBin().from_disk("dados_legislacao.spacy")

# Carregar o modelo spaCy (pode ser o modelo treinado ou em branco)
nlp = spacy.load("output/model-best")

# Exemplo de novo texto para adicionar
texto_novo = "A Zona Comercial do bairro Y foi definida pela Lei nº 12345/2020."

# Criar um doc do spaCy com o novo texto
doc = nlp(texto_novo)

# Definir as entidades a serem anotadas (posição inicial e final, e rótulo)
# Exemplo de anotações para as entidades "Zona Comercial" e "Lei nº 12345/2020"
ents = [
    (texto_novo.find("Zona Comercial"), texto_novo.find("Zona Comercial") + len("Zona Comercial"), "ZONA"),
    (texto_novo.find("Lei nº 12345/2020"), texto_novo.find("Lei nº 12345/2020") + len("Lei nº 12345/2020"), "LEI")
]

# Adicionar as entidades ao doc
doc.ents = [doc.char_span(start, end, label=label) for start, end, label in ents]

# Adicionar o doc ao DocBin
doc_bin.add(doc)

# Salvar novamente o arquivo .spacy com os novos exemplos
doc_bin.to_disk("dados_legislacao.spacy")

print("Novos dados adicionados com sucesso!")
