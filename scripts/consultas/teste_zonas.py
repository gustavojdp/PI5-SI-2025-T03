import requests
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import Nominatim
import time
from dicionario_zonas import dicionario_zonas

# Função para buscar coordenadas a partir de um CEP
def obter_coordenadas_cep(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if response.status_code != 200:
        return None
    data = response.json()
    if "erro" in data:
        return None

    endereco = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}"
    geolocator = Nominatim(user_agent="pi5")
    time.sleep(1)
    location = geolocator.geocode(endereco)
    if location:
        return location.latitude, location.longitude, endereco
    return None

# Conecta ao MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Entrada do usuário
cep = input("Digite o CEP (somente números): ")
coordenadas = obter_coordenadas_cep(cep)

if not coordenadas:
    print("❌ Não foi possível obter as coordenadas para o CEP informado.")
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
        codigo = props.get("duos") or props.get("DUOS") or props.get("Duos") or "Não especificado"
        nome = dicionario_zonas.get(codigo, "Nome não identificado")

        print("✅ Zona encontrada:")
        print(f"Código: {codigo}")
        print(f"Nome: {nome}")
    else:
        print("❌ Nenhuma zona encontrada para essas coordenadas.")