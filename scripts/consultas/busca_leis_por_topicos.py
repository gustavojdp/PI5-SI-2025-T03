import requests
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import Nominatim
import time
import json
from dicionario_zonas import dicionario_zonas

# Carrega a legislação por tópicos
with open("output/legislacao_resumida_topicos.json", "r", encoding="utf-8") as f:
    legislacao_topicos = json.load(f)

# Função para buscar coordenadas a partir de um CEP
def obter_coordenadas_cep(cep):
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if response.status_code != 200:
        return None
    data = response.json()
    if "erro" in data:
        return None

    # Tentativa com todos os dados
    endereco = f"{data.get('logradouro', '')}, {data.get('bairro', '')}, {data.get('localidade', '')}, {data.get('uf', '')}"
    geolocator = Nominatim(user_agent="pi5")
    time.sleep(1)
    location = geolocator.geocode(endereco)

    # Fallback com menos dados se falhar
    if not location:
        endereco = f"{data.get('localidade', '')}, {data.get('uf', '')}"
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
        codigo = props.get("duos") or "Não especificado"
        nome = dicionario_zonas.get(codigo, "Nome não identificado")

        print(f"✅ Zona encontrada: {nome} ({codigo})\n")

        info = legislacao_topicos.get(codigo)
        if info:
            for topico, sentencas in info.items():
                sent_filtradas = [s for s in sentencas if codigo in s or nome.lower() in s.lower()]
                if sent_filtradas:
                    print(f"🔹 {topico.replace('_', ' ').capitalize()}:\n")
                    for s in sent_filtradas[:3]:
                        s_limpo = s.strip().replace("\n", " ").strip()
                        print(f"• {s_limpo}\n")
        else:
            print("⚠️ Nenhuma legislação estruturada encontrada para essa zona.")
    else:
        print("❌ Nenhuma zona encontrada para essas coordenadas.")
