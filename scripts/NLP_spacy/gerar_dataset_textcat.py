import json

# Caminhos de entrada e saída
CAMINHO_ENTRADA = "output/legislacao_resumida_topicos.json"
CAMINHO_SAIDA = "output/dataset_legislacao_textcat.jsonl"

# Carrega os dados resumidos por zona e tópico
with open(CAMINHO_ENTRADA, "r", encoding="utf-8") as f:
    dados = json.load(f)

# Lista para armazenar os exemplos rotulados
exemplos = []

# Percorre zona → tópicos → frases
for zona, topicos in dados.items():
    for topico, frases in topicos.items():
        for frase in frases:
            frase_limpa = frase.strip().replace("\n", " ")
            if len(frase_limpa) < 1000:  # ignora trechos gigantes
                exemplos.append({
                    "text": frase_limpa,
                    "label": topico
                })

# Salva no formato JSONL (um por linha)
with open(CAMINHO_SAIDA, "w", encoding="utf-8") as f:
    for exemplo in exemplos:
        json.dump(exemplo, f, ensure_ascii=False)
        f.write("\n")

print(f"✅ Dataset gerado com {len(exemplos)} exemplos em '{CAMINHO_SAIDA}'")
