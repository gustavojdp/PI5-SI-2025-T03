import spacy
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import json
from dicionario_zonas import dicionario_zonas

# Carrega o modelo spaCy treinado para classificar zonas (ex: ZC2, ZM1, etc)
modelo_spacy = spacy.load("modelos/spacy_zonas_refinado")

# Carrega legislações por zona
with open("output/legislacao_por_zona_completa.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

# Conexão com MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Função para obter coordenadas do CEP
def obter_coordenadas_cep(cep):
    endereco = f"{cep}, Campinas, SP"
    print(f"Endereço enviado para geocodificação: {endereco}")
    geolocator = GoogleV3(api_key="AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ")
    try:
        location = geolocator.geocode(endereco)
        if location:
            return location.latitude, location.longitude, endereco
    except Exception as e:
        print(f"Erro ao consultar coordenadas: {e}")
    return None

# Função para identificar a zona pela pergunta usando spaCy com threshold
def identificar_zona_por_texto(pergunta, threshold=0.6):
    doc = modelo_spacy(pergunta)
    zona_predita = max(doc.cats, key=doc.cats.get)
    confianca = doc.cats[zona_predita]
    if confianca < threshold:
        return None, confianca
    return zona_predita, confianca

# Entrada do usuário
pergunta = input("Digite sua pergunta (ex: Quais as leis da ZC2?)\n> ")

# Primeiro tenta identificar a zona pela pergunta
zona_textual, confianca = identificar_zona_por_texto(pergunta)

if zona_textual:
    print(f"\n Zona identificada na pergunta: {zona_textual}")
else:
    print(f"\n Nenhuma zona válida foi identificada com confiança suficiente")

# Depois pede o CEP para confirmar se a zona textual bate com a geográfica
cep = input("Digite o CEP (somente números): ")
coordenadas = obter_coordenadas_cep(cep)

if not coordenadas:
    print("\n Não foi possível obter as coordenadas para o CEP informado.")
else:
    lat, lon, endereco = coordenadas
    print(f"\n Endereço encontrado: {endereco}")
    print(f" Coordenadas aproximadas: lat={lat}, lon={lon}\n")

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

        print(f" Zona geográfica identificada: {nome} ({codigo})")

        if zona_textual and codigo != zona_textual:
            print(f" A zona identificada na pergunta ({zona_textual}) difere da zona geográfica ({codigo}).")

        trechos = legislacoes.get(codigo)
        if trechos:
            print("\n Trechos legislativos da zona:")
            for topico, frases in trechos.items():
                print(f"\n {topico.replace('_', ' ').capitalize()}:")
                for i, frase in enumerate(frases[:3], 1):
                    print(f"  {i}. {frase.strip()}")
        else:
            print(" Nenhuma legislação associada à zona encontrada.")
    else:
        print(" Nenhuma zona encontrada para essas coordenadas.")
