import json
import spacy
from collections import defaultdict

nlp = spacy.load("pt_core_news_sm")

# Carrega os trechos brutos por zona
with open("output/zonas_legislacao_extraida.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Estrutura resumida
resumo_por_zona = defaultdict(lambda: {
    "uso_permitido": [],
    "altura_maxima": [],
    "densidade_maxima": [],
    "parcelamento": [],
    "observacoes": []
})

# Palavras-chave por categoria (simplificadas e adaptáveis)
palavras_chave = {
    "uso_permitido": ["uso permitido", "permitido", "poderá", "autorizado"],
    "altura_maxima": ["altura máxima", "limite de altura", "até", "edificação com altura"],
    "densidade_maxima": ["densidade habitacional", "uh/ha", "unidades habitacionais"],
    "parcelamento": ["lote", "parcelamento", "mínima", "área mínima"],
    "observacoes": ["EIV", "RIV", "exceção", "condição", "deverá", "obrigatório", "facultativo"]
}

# Função de classificação com base nas palavras-chave
def classificar_sentenca(sentenca):
    texto = sentenca.lower()
    for categoria, palavras in palavras_chave.items():
        for termo in palavras:
            if termo in texto:
                return categoria
    return "observacoes"

# Processa zona por zona
for zona, trechos in legislacoes.items():
    for trecho in trechos:
        doc = nlp(trecho)
        for sent in doc.sents:
            categoria = classificar_sentenca(sent.text)
            resumo_por_zona[zona][categoria].append(sent.text.strip())

# Salva o novo resumo estruturado
with open("output/legislacao_resumida_topicos.json", "w", encoding="utf-8") as f:
    json.dump(resumo_por_zona, f, indent=2, ensure_ascii=False)

print("✅ Legislação reorganizada por tópicos e salva em 'output/legislacao_resumida_topicos.json'")
