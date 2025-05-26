from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import json
import spacy
from dicionario_zonas import dicionario_zonas

# Carregar modelo multilabel treinado (substitua o caminho pelo local do seu modelo)
nlp = spacy.load("models/spacy_textcat/model-best")

# Adiciona o componente sentencizer para definir sentenças (necessário para doc.sents)
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

# Dicionário das zonas relacionadas para ampliar o filtro
zonas_relacionadas = {
    "ZC2": ["zc2", "zc4", "zm1"],
    "ZC4": ["zc4", "zc2", "zm1"],
    "ZM1": ["zm1", "zc2", "zc4"],
    "ZM2": ["zm2"],
    "ZM4": ["zm4"],
    # Adicione outras zonas e seus grupos relacionados se necessário
}

# Função para obter coordenadas a partir do CEP
def obter_coordenadas_cep(cep):
    endereco = f"{cep}, Campinas, SP"
    print(f"Endereço enviado para geocodificação: {endereco}")

    geolocator = GoogleV3(api_key="AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ")
    try:
        location = geolocator.geocode(endereco)
    except Exception as e:
        print(f"Erro ao consultar coordenadas: {e}")
        return None

    if location:
        return location.latitude, location.longitude, endereco
    return None

# Função para filtrar sentenças usando o modelo multilabel treinado
def filtrar_sentencas_por_modelo(texto, codigo_zona):
    texto = texto.replace("\n", " ").replace("\r", " ")
    doc = nlp(texto)
    sentencas_filtradas = []

    lista_zonas = zonas_relacionadas.get(codigo_zona, [codigo_zona.lower()])

    for sent in doc.sents:
        doc_sent = nlp(sent.text)
        cats = doc_sent.cats  # Dicionário {zona: probabilidade}

        # Verifica se alguma das zonas relacionadas está com probabilidade alta (ex: >= 0.7)
        if any(cats.get(z.lower(), 0) >= 0.7 for z in lista_zonas):
            sentencas_filtradas.append(sent.text.strip())

    # Se nenhuma sentença passou no filtro, retorna todas para não perder informação
    if not sentencas_filtradas:
        sentencas_filtradas = [sent.text.strip() for sent in doc.sents]

    # Remove sentenças muito curtas (menos de 20 caracteres)
    sentencas_filtradas = [s for s in sentencas_filtradas if len(s) > 20]

    return sentencas_filtradas

# Conexão com o MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Carrega a legislação da zona
with open("output/legislacao_por_zona_completa.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

cep = input("Digite o CEP (somente números): ")
coordenadas = obter_coordenadas_cep(cep)

if not coordenadas:
    print("\n❌ Não foi possível obter as coordenadas para o CEP informado.")
else:
    lat, lon, endereco = coordenadas
    print(f"\n🔎 Endereço encontrado: {endereco}")
    print(f"📍 Coordenadas aproximadas: lat={lat}, lon={lon}\n")

    ponto = Point(lon, lat)
    zona_encontrada = None

    for doc in collection.find():
        geom = doc.get("geometry")
        if geom:
            polygon = shape(geom)
            if polygon.contains(ponto):
                zona_encontrada = doc
                break

    if zona_encontrada:
        props = zona_encontrada.get("properties", {})
        codigo = props.get("duos") or "Não especificado"
        nome = dicionario_zonas.get(codigo, "Nome não identificado")

        print(f"✅ Zona encontrada: {nome} ({codigo})\n")

        trechos = legislacoes.get(codigo)
        if trechos:
            print("🔍 Trechos legislativos da zona (filtrados via NLP):")
            for topico, frases in trechos.items():
                texto_completo = " ".join(frases)
                sentencas_filtradas = filtrar_sentencas_por_modelo(texto_completo, codigo)
                print(f"\n🔸 {topico.replace('_', ' ').capitalize()}:")
                for i, frase in enumerate(sentencas_filtradas[:3], 1):
                    print(f"  {i}. {frase}")
        else:
            print("⚠️ Nenhuma legislação associada à zona encontrada.")
    else:
        print("❌ Nenhuma zona encontrada para essas coordenadas.")
