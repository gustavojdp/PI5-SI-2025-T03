import requests
from pymongo import MongoClient
from shapely.geometry import shape, Point
import time

# Conexão com MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Função para obter coordenadas a partir de um CEP
def cep_para_coordenadas(cep):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={cep}&country=Brazil&format=json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resposta = requests.get(url, headers=headers)

    if resposta.status_code == 200 and resposta.json():
        dados = resposta.json()[0]
        return float(dados['lat']), float(dados['lon'])
    return None, None

# Entrada do usuário
cep = input("Digite o CEP (somente números): ").strip()

# Buscar endereço via ViaCEP (opcional, apenas exibição)
via_cep = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
endereco_str = (
    f"{via_cep.get('logradouro', '')}, {via_cep.get('bairro', '')}, "
    f"{via_cep.get('localidade', '')}, {via_cep.get('uf', '')}"
)

# Obter coordenadas
lat, lon = cep_para_coordenadas(cep)

if not lat or not lon:
    print("❌ Não foi possível obter coordenadas para o CEP informado.")
    exit()

print(f"\n🔎 Endereço encontrado: {endereco_str}")
print(f"📍 Coordenadas aproximadas: lat={lat}, lon={lon}")

# Verificar se ponto está dentro de algum polígono
ponto = Point(lon, lat)
zona_encontrada = None

for doc in collection.find():
    try:
        geo = doc.get("geometry")
        if geo:
            poligono = shape(geo)
            if poligono.contains(ponto):
                zona_encontrada = doc
                break
    except:
        continue

# Exibir resultado
if zona_encontrada:
    nome = zona_encontrada.get("nome_zona") or zona_encontrada.get("Nome") or "Não especificado"
    codigo = zona_encontrada.get("codigo_zona") or zona_encontrada.get("Codigo") or "Não especificado"
    print("\n✅ Zona encontrada:")
    print(f"Nome: {nome}")
    print(f"Código: {codigo}")
else:
    print("⚠️ Nenhuma zona encontrada para essa localização.")
