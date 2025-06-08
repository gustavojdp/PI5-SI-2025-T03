from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import spacy
import json
from dicionario_zonas import dicionario_zonas

app = Flask(__name__)
CORS(app)  # Habilita CORS para o front-end acessar

nlp = spacy.load("pt_core_news_sm")

# Conexão com MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Dicionário de zonas relacionadas
zonas_relacionadas = {
    "ZC2": ["zc2", "zc4", "zm1"],
    "ZC4": ["zc4", "zc2", "zm1"],
    "ZM1": ["zm1", "zc2", "zc4"],
    "ZM2": ["zm2"],
    "ZM4": ["zm4"]
}

# Carrega legislação por zona
with open("output/legislacao_por_zona_completa.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Função para buscar coordenadas pelo CEP
def obter_coordenadas_cep(cep):
    endereco = f"{cep}, Campinas, SP"
    geolocator = GoogleV3(api_key="AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ")
    try:
        location = geolocator.geocode(endereco)
    except Exception:
        return None
    if location:
        return location.latitude, location.longitude, location.address
    return None

# Função de filtragem com spaCy
def filtrar_sentencas_por_zonas(texto, codigo_zona):
    texto = texto.replace("\n", " ").replace("\r", " ")
    doc = nlp(texto)
    sentencas_filtradas = []
    lista_zonas = zonas_relacionadas.get(codigo_zona, [codigo_zona.lower()])
    for sent in doc.sents:
        sent_lower = sent.text.lower()
        if any(zona in sent_lower for zona in lista_zonas):
            sentencas_filtradas.append(sent.text.strip())
    if not sentencas_filtradas:
        sentencas_filtradas = [sent.text.strip() for sent in doc.sents]
    return [s for s in sentencas_filtradas if len(s) > 20]

# Rota principal
@app.route('/buscar', methods=['GET'])
def buscar_por_cep():
    cep = request.args.get('cep')
    if not cep:
        return jsonify({"erro": "CEP não informado"}), 400

    coordenadas = obter_coordenadas_cep(cep)
    if not coordenadas:
        return jsonify({"erro": "Coordenadas não encontradas"}), 404

    lat, lon, endereco = coordenadas
    ponto = Point(lon, lat)
    zona_encontrada = None

    for doc in collection.find():
        geom = doc.get("geometry")
        if geom and shape(geom).contains(ponto):
            zona_encontrada = doc
            break

    if not zona_encontrada:
        return jsonify({"erro": "Zona não encontrada"}), 404

    props = zona_encontrada.get("properties", {})
    codigo = props.get("duos") or "Não especificado"
    nome = dicionario_zonas.get(codigo, "Nome não identificado")

    trechos = legislacoes.get(codigo)
    legislacao_formatada = {}
    if trechos:
        for topico, frases in trechos.items():
            texto_completo = " ".join(frases)
            sentencas_filtradas = filtrar_sentencas_por_zonas(texto_completo, codigo)
            legislacao_formatada[topico] = sentencas_filtradas[:3]

    return jsonify({
        "cep": cep,
        "endereco": endereco,
        "coordenadas": {"lat": lat, "lon": lon},
        "zona": {"codigo": codigo, "nome": nome},
        "legislacao": legislacao_formatada
    })

if __name__ == '__main__':
    app.run(debug=True)