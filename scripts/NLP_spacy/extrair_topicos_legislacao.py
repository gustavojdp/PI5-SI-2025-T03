import json
import spacy
from collections import defaultdict
from dicionario_zonas import dicionario_zonas

nlp = spacy.load("pt_core_news_sm")

# Carrega os trechos brutos por zona
with open("output/zonas_legislacao_extraida.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Lista de zonas reconhecidas
zonas_siglas = list(dicionario_zonas.keys())

# Estrutura resumida
resumo_por_zona = defaultdict(lambda: {
    "uso_permitido": [],
    "altura_maxima": [],
    "densidade_maxima": [],
    "parcelamento": [],
    "observacoes": []
})

# Palavras-chave por categoria
palavras_chave = {
    "uso_permitido": ["uso permitido", "permitido", "poderá", "autorizado"],
    "altura_maxima": ["altura máxima", "limite de altura", "até", "edificação com altura"],
    "densidade_maxima": ["densidade habitacional", "uh/ha", "unidades habitacionais"],
    "parcelamento": ["lote", "parcelamento", "mínima", "área mínima"],
    "observacoes": ["EIV", "RIV", "exceção", "condição", "deverá", "obrigatório", "facultativo"]
}

# Classifica a sentença com base em palavras-chave
def classificar_sentenca(sentenca):
    texto = sentenca.lower()
    for categoria, termos in palavras_chave.items():
        if any(termo in texto for termo in termos):
            return categoria
    return "observacoes"

# Filtra sentenças que mencionam outras zonas além da atual
def menciona_outras_zonas(sentenca, zona_atual):
    mencionadas = [z for z in zonas_siglas if z in sentenca and z != zona_atual]
    return len(mencionadas) > 0

# Processa zona por zona
for zona, trechos in legislacoes.items():
    for trecho in trechos:
        doc = nlp(trecho)
        for sent in doc.sents:
            texto = sent.text.strip()

            # Filtra ruído e sentenças irrelevantes
            if len(texto) < 15 or texto.lower() in palavras_chave.keys():
                continue

            # Ignora sentenças que misturam zonas
            if menciona_outras_zonas(texto, zona):
                continue

            categoria = classificar_sentenca(texto)
            resumo_por_zona[zona][categoria].append(texto)

# Salva o resultado final
with open("output/legislacao_resumida_topicos.json", "w", encoding="utf-8") as f:
    json.dump(resumo_por_zona, f, indent=2, ensure_ascii=False)

print("✅ Legislação reorganizada por tópicos e salva em 'output/legislacao_resumida_topicos.json'")
