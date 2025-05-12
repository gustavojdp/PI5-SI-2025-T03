import spacy
import json

# Carregar o modelo treinado
modelo = spacy.load("modelos/spacy_legislacao_textcat")

# Carregar o arquivo de legislações extraídas
with open("zonas_legislacao_extraida_atualizado.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Função para obter a resposta
def obter_resposta(pergunta):
    # Processa a pergunta com spaCy
    doc = modelo(pergunta)
    
    # Exibe a categoria com a maior probabilidade
    categoria = max(doc.cats, key=doc.cats.get)
    print(f"Categoria identificada: {categoria}")

    # Busca a resposta no JSON
    resposta = []
    
    # Agora, vamos fazer uma busca direta para ver se encontramos a categoria nas zonas
    for zona, trechos in legislacoes.items():
        if categoria in zona.lower():  # Verifica se a zona contém a categoria
            for trecho in trechos:  # Percorre os trechos da zona
                if categoria in trecho.lower():  # Verifica se o trecho corresponde à categoria
                    resposta.append(trecho)

    return resposta

# Loop para interação com o usuário
while True:
    # Pergunta ao usuário
    pergunta = input("\nDigite sua pergunta (ou 'sair' para encerrar): ")
    
    if pergunta.lower() == 'sair':
        print("Saindo...")
        break

    resposta = obter_resposta(pergunta)
    
    if resposta:
        print("\nResposta encontrada:")
        for trecho in resposta:  # Exibe os trechos encontrados
            print(f"- {trecho}")
    else:
        print("\nDesculpe, não encontrei uma resposta relevante.")
