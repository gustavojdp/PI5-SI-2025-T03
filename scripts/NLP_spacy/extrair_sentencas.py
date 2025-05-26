import json
import spacy

nlp = spacy.load("pt_core_news_sm")

# Carrega o conteúdo do JSON
with open("output/documento_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

conteudo = " ".join(data["conteudo"])

# Processa com spaCy
doc = nlp(conteudo)
sentencas = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

print(f"✅ Total de sentenças extraídas: {len(sentencas)}")

# Salva para rotulação
with open("output/sentencas_para_rotular.json", "w", encoding="utf-8") as f:
    json.dump(sentencas, f, indent=2, ensure_ascii=False)
