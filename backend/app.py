from flask import Flask, request, jsonify
import spacy
import json

app = Flask(__name__)

# Carregar modelo treinado do spaCy
modelo = spacy.load("modelos/spacy_legislacao_textcat")

# Carregar o arquivo de legislações extraídas
with open("output/legislacao_resumida_topicos.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

def obter_resposta(pergunta):
    doc = modelo(pergunta)
    categoria = max(doc.cats, key=doc.cats.get)

    resposta = []
    for zona, trechos in legislacoes.items():
        if categoria in trechos:
            for trecho in trechos[categoria]:
                resposta.append(trecho)
    return resposta

@app.route('/chat', methods=['POST'])
def chat():
    pergunta = request.json.get('pergunta')
    resposta = obter_resposta(pergunta)
    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
