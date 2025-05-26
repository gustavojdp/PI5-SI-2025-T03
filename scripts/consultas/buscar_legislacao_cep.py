from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import json
from dicionario_zonas import dicionario_zonas

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
            print("🔍 Trechos legislativos da zona:")
            for topico, frases in trechos.items():
                print(f"\n🔸 {topico.replace('_', ' ').capitalize()}:")
                for i, frase in enumerate(frases[:3], 1):
                    print(f"  {i}. {frase.strip()}")
        else:
            print("⚠️ Nenhuma legislação associada à zona encontrada.")
    else:
        print("❌ Nenhuma zona encontrada para essas coordenadas.")
