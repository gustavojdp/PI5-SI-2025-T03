import json
import spacy
import re

# Carregar o modelo spaCy para segmentação
nlp = spacy.load("pt_core_news_sm")

# Carrega o JSON da legislação (ajuste o caminho conforme seu arquivo)
with open("output/legislacao_por_zona_completa.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Lista de zonas para classificar (todas as chaves do JSON)
zonas = list(legislacoes.keys())

# Função para detectar zonas presentes no texto de uma sentença
def detectar_zonas_na_sentenca(sentenca, zonas):
    sentenca_lower = sentenca.lower()
    resultado = {}
    for zona in zonas:
        # Verifica se o código da zona aparece na sentença (case insensitive)
        # Exemplo: "ZM1", "ZC4", "ZR-A", etc
        if zona.lower() in sentenca_lower:
            resultado[zona] = True
        else:
            resultado[zona] = False
    return resultado

# Abrir arquivo para escrita do dataset JSONL
with open("dataset_train.jsonl", "w", encoding="utf-8") as out_file:
    total_sentencas = 0
    for zona, topicos in legislacoes.items():
        for topico, textos in topicos.items():
            # Junta os textos do tópico para segmentar sentenças
            texto_completo = " ".join(textos).replace("\n", " ").replace("\r", " ")
            doc = nlp(texto_completo)
            for sent in doc.sents:
                sent_text = sent.text.strip()
                # Ignora sentenças muito curtas
                if len(sent_text) < 20:
                    continue
                cats = detectar_zonas_na_sentenca(sent_text, zonas)
                exemplo = {
                    "text": sent_text,
                    "cats": cats
                }
                out_file.write(json.dumps(exemplo, ensure_ascii=False) + "\n")
                total_sentencas += 1

print(f"Dataset criado com {total_sentencas} sentenças anotadas.")
