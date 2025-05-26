import json
import random

# Carregar o JSON de legislação
with open("output/legislacao_por_zona_completa.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

zonas = list(legislacoes.keys())

# Frases base para perguntas, serão combinadas com os códigos
perguntas_base = [
    "Quais são as regras da {}?",
    "Me diga a legislação da {}.",
    "Qual é a altura máxima permitida na {}?",
    "Que tipos de uso são permitidos na {}?",
    "Quais as diretrizes de ocupação da {}?",
    "Me informe os parâmetros urbanísticos da {}.",
    "O que pode ser construído na {}?",
    "Quais os recuos obrigatórios na {}?",
    "Como funciona o adensamento na {}?",
    "O que a lei diz sobre lotes na {}?",
    "Quais os limites de densidade na {}?",
    "O que é permitido na zona {}?",
    "Quais os usos não permitidos na {}?",
    "Me diga os afastamentos mínimos da {}.",
    "Qual a metragem mínima de lote na {}?"
]

# Gerar dataset
train_data = []

for zona in zonas:
    for frase in perguntas_base:
        texto = frase.format(zona)
        cats = {z: 0.0 for z in zonas}
        cats[zona] = 1.0
        train_data.append({"text": texto, "cats": cats})

# Salvar em JSON
with open("output/train_data_legislacao_zonas.json", "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

print("✅ train_data salvo com sucesso com", len(train_data), "exemplos.")
