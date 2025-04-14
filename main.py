import spacy
from spacy.matcher import Matcher
import re
from mongo_connection import get_shp_data

# Carrega o modelo treinado
nlp = spacy.load("output/model-best")

# Inicializa o Matcher com o vocabulário do spaCy
matcher = Matcher(nlp.vocab)

# Define padrões para zona e subprefeitura
padrao_zona = [
    [{"LOWER": "zona"}, {"IS_ALPHA": True}],  # Ex: Zona Mista
    [{"LOWER": "zona"}, {"IS_UPPER": True}],  # Ex: Zona ZPR
    [{"TEXT": {"REGEX": "^Z[A-Z]{1,5}(-\d)?$"}}]  # Ex: ZPI-2 ou ZC
]

# Adiciona padrões ao Matcher
matcher.add("ZONA", padrao_zona)

def extrair_dados(texto):
    doc = nlp(texto)
    dados = {}

    # Captura por Matcher com prioridade ao último match
    matches = matcher(doc)
    zona_detectada = None

    # Extração de zonas compostas pelo matcher
    for match_id, start, end in matches:
        span = doc[start:end]
        zona_detectada = span.text  # sobrescreve com o último

    if zona_detectada:
        dados["zona"] = zona_detectada

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

    print("\n🧩 Dados extraídos para consulta:")
    dados = extrair_dados(texto)
    print(dados)

    # Simulando a consulta no MongoDB
    consultar_mongo_simulado(dados)

if __name__ == "__main__":
    while True:
        texto_exemplo = input("Digite um texto de zoneamento para análise (digite 'sair' para encerrar):\n> ")
        if texto_exemplo.lower() == "sair":
            print("Programa encerrado!")
            break
        analisar_texto(texto_exemplo)
