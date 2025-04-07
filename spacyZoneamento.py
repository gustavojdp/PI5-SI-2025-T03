import spacy
from spacy.matcher import Matcher
import re

# Carrega o modelo em português
nlp = spacy.load("pt_core_news_sm")

# Inicializa o Matcher com o vocabulário do spaCy
matcher = Matcher(nlp.vocab)

# Define padrões para zona e subprefeitura
padrao_zona = [
    [{"LOWER": "zona"}, {"IS_ALPHA": True}],  # Ex: Zona Mista
    [{"LOWER": "zona"}, {"IS_UPPER": True}],  # Ex: Zona ZPR
    [{"TEXT": {"REGEX": "^Z[A-Z]{1,5}(-\d)?$"}}]  # Ex: ZPI-2 ou ZC
]

padrao_subprefeitura = [
    [{"LOWER": "subprefeitura"}, {"LOWER": {"IN": ["da", "de"]}}, {"IS_TITLE": True}],
    [{"LOWER": "subprefeitura"}, {"LOWER": {"IN": ["da", "de"]}}, {"IS_TITLE": True}, {"IS_TITLE": True}]
]

# Adiciona padrões ao Matcher
matcher.add("ZONA", padrao_zona)
matcher.add("SUBPREFEITURA", padrao_subprefeitura)

def extrair_dados(texto):
    doc = nlp(texto)
    dados = {}

    # Captura por Matcher com prioridade ao último match
    matches = matcher(doc)
    zona_detectada = None
    subpref_detectada = None

    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]

        if label == "ZONA":
            zona_detectada = span.text  # sobrescreve com o último
        elif label == "SUBPREFEITURA":
            subpref_detectada = span.text  # sobrescreve com o último

    if zona_detectada:
        dados["zona"] = zona_detectada
    if subpref_detectada:
        nome = subpref_detectada.replace("Subprefeitura da ", "").replace("Subprefeitura de ", "")
        dados["subprefeitura"] = nome

    # Captura de LEI via regex no texto bruto
    padrao = r"Lei(?: [Cc]omplementar)?(?: nº)? ?\d+[\.\d]*/\d{4}"
    encontrado = re.search(padrao, texto)
    if encontrado:
        dados["lei"] = encontrado.group()

    return dados

def consultar_mongo_simulado(filtros):
    print("\n🔍 Consulta simulada ao MongoDB com base em:")
    for chave, valor in filtros.items():
        print(f" - {chave}: {valor}")

def analisar_texto(texto):
    doc = nlp(texto)

    print("\n🔍 Tokens e lemas:")
    for token in doc:
        print(f"{token.text} → {token.lemma_}")

    print("\n🏷️ Entidades nomeadas:")
    for ent in doc.ents:
        print(f"{ent.text} ({ent.label_})")

    print("\n🧠 Classes gramaticais:")
    for token in doc:
        print(f"{token.text}: {token.pos_}")

    print("\n🧩 Correspondências do Matcher:")
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        print(f"{nlp.vocab.strings[match_id]}: {span.text}")

    dados = extrair_dados(texto)
    print("\n📦 Dados extraídos para consulta:")
    print(dados)

    consultar_mongo_simulado(dados)

if __name__ == "__main__":
    while True:
        texto_exemplo = input("Digite um texto de zoneamento para análise (digite 'sair' para encerrar):\n> ")
        if texto_exemplo.lower() == "sair":
            print("Programa encerrado!")
            break
        analisar_texto(texto_exemplo)
