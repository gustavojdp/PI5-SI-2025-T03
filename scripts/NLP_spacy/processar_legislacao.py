# pip install spacy
# python -m spacy download pt_core_news_sm


import json
import spacy
from collections import defaultdict

# Carrega o modelo spaCy (usar pt_core_news_sm)
nlp = spacy.load("pt_core_news_sm")

# Carrega os trechos legislativos por zona
with open("output/zonas_legislacao_extraida.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Estrutura para armazenar resultados resumidos
resumo_por_zona = defaultdict(lambda: {
    "uso_permitido": [],
    "observacoes": [],
    "altura_maxima": [],
    "densidade_maxima": [],
})

# Regras básicas de extração (poderão ser refinadas depois)
def classificar_trecho(trecho, zona):
    doc = nlp(trecho)
    texto = doc.text.lower()

    if "uso" in texto and any(palavra in texto for palavra in ["permitido", "permitida", "permitidos"]):
        resumo_por_zona[zona]["uso_permitido"].append(trecho.strip())
    elif "altura" in texto and "máxima" in texto:
        resumo_por_zona[zona]["altura_maxima"].append(trecho.strip())
    elif "densidade" in texto and "habitacional" in texto:
        resumo_por_zona[zona]["densidade_maxima"].append(trecho.strip())
    else:
        resumo_por_zona[zona]["observacoes"].append(trecho.strip())

# Processa cada zona
for zona, trechos in legislacoes.items():
    for trecho in trechos:
        classificar_trecho(trecho, zona)

# Salva o resultado resumido
with open("output/legislacao_resumida_por_zona.json", "w", encoding="utf-8") as f:
    json.dump(resumo_por_zona, f, indent=2, ensure_ascii=False)

print("✅ Resumo da legislação por zona salvo em 'output/legislacao_resumida_por_zona.json'")
