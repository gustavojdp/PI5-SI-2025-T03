import os
import requests
import geopandas as gpd
from shapely.geometry import Point
import pymongo
from bson import json_util
import json
from pyproj import Transformer
import matplotlib.pyplot as plt
from shapely.validation import make_valid

# Configurações
SHAPEFILE_DIR = r"C:\Users\55119\Downloads\ZonaCps"
SHAPEFILE_BASENAME = "ZonaCps"
SHAPEFILE_PATH = os.path.join(SHAPEFILE_DIR, f"{SHAPEFILE_BASENAME}.shp")
MONGO_URI = "mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/"
DB_NAME = "PI5"
COLLECTION_NAME = "coordenadas"

def verificar_arquivos_shapefile():
    """Verifica se todos os arquivos do shapefile existem"""
    extensions = ['.shp', '.shx', '.dbf']
    missing = []
    
    for ext in extensions:
        file_path = os.path.join(SHAPEFILE_DIR, f"{SHAPEFILE_BASENAME}{ext}")
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        raise FileNotFoundError(f"Arquivos do shapefile faltando: {', '.join(missing)}")
    
    return True

def carregar_mapa():
    try:
        verificar_arquivos_shapefile()
        os.environ['SHAPE_RESTORE_SHX'] = 'YES'
        
        gdf = gpd.read_file(SHAPEFILE_PATH)
        
        if gdf.empty:
            raise ValueError("Shapefile carregado mas está vazio")
            
        gdf['geometry'] = gdf['geometry'].apply(
            lambda geom: make_valid(geom) if not geom.is_valid else geom
        )
        
        if not gdf.crs:
            gdf.crs = 'EPSG:4326'
        
        print("\nShapefile carregado com sucesso!")
        print(f"Colunas disponíveis: {gdf.columns.tolist()}")
        return gdf
        
    except Exception as e:
        print(f"\nErro ao carregar shapefile: {str(e)}")
        raise

def get_mongo_connection():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[DB_NAME]
        return db
    except Exception as e:
        raise Exception(f"Erro ao conectar ao MongoDB: {str(e)}")

def buscar_lat_long_cep(cep):
    cep = ''.join(filter(str.isdigit, cep))
    if len(cep) != 8:
        raise ValueError("CEP deve conter 8 dígitos")

    try:
        viacep_url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(viacep_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "erro" in data:
            raise ValueError("CEP não encontrado no ViaCEP")

        endereco = f"{data.get('bairro', '')}, {data.get('localidade', '')}, {data.get('uf', '')}, Brasil"
        nominatim_url = f"https://nominatim.openstreetmap.org/search?q={endereco.replace(' ', '%20')}&format=json"
        response_geo = requests.get(nominatim_url, headers={'User-Agent': 'PI5-Academic-Project/1.0'}, timeout=10)
        response_geo.raise_for_status()
        
        geo_data = response_geo.json()
        if not geo_data:
            raise ValueError("Endereço não encontrado no Nominatim")

        primeiro_resultado = geo_data[0]
        return float(primeiro_resultado['lat']), float(primeiro_resultado['lon'])

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro na requisição HTTP: {str(e)}")

def consulta_zoneamento_por_cep(cep):
    try:
        print(f"\nIniciando consulta para CEP: {cep}")
        
        # 1. Obter coordenadas
        lat, lon = buscar_lat_long_cep(cep)
        print(f"Coordenadas encontradas: Latitude={lat}, Longitude={lon}")

        # 2. Carregar shapefile
        gdf = carregar_mapa()
        
        # 3. Criar ponto
        ponto = Point(lon, lat)
        
        # 4. Encontrar zona mais próxima
        gdf['distancia'] = gdf.geometry.distance(ponto)
        zona = gdf.nsmallest(1, 'distancia')
        
        print(f"\nZona mais próxima encontrada a {zona.iloc[0]['distancia']:.2f} graus")
        
        # 5. Criar identificador único baseado nas colunas disponíveis
        tipo_zona = zona.iloc[0]['TIPO']
        mergulho = zona.iloc[0]['MERGULHO']
        id_zona = f"{tipo_zona}_{mergulho}"
        
        print(f"Tipo da zona: {tipo_zona}")
        print(f"Mergulho: {mergulho}")
        print(f"ID gerado: {id_zona}")

        # 6. Consultar MongoDB
        db = get_mongo_connection()
        collection = db[COLLECTION_NAME]
        
        # Tenta encontrar por qualquer campo que contenha o tipo ou mergulho
        resultado = collection.find_one({
            "$or": [
                {"TIPO": {"$regex": tipo_zona, "$options": "i"}},
                {"MERGULHO": mergulho},
                {"NOME": {"$regex": tipo_zona, "$options": "i"}},
                {"DESCRICAO": {"$regex": tipo_zona, "$options": "i"}}
            ]
        })
        
        if not resultado:
            raise ValueError(f"Nenhuma informação encontrada no MongoDB para esta zona")
            
        print("\nInformações da zona:")
        print(json.dumps(resultado, indent=2, default=json_util.default))
        
        # Visualização
        fig, ax = plt.subplots(figsize=(12, 10))
        gdf.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.5)
        gpd.GeoSeries([ponto]).plot(ax=ax, color='red', markersize=100, label='CEP')
        zona.plot(ax=ax, color='blue', alpha=0.7, edgecolor='darkblue', label='Zona Encontrada')
        plt.title(f"Localização do CEP {cep}\nZona: {tipo_zona}")
        plt.legend()
        plt.show()
        
        return resultado
        
    except Exception as e:
        print(f"\n⚠ Erro na consulta: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        cep = input("Digite o CEP (apenas números): ").strip()
        resultado = consulta_zoneamento_por_cep(cep)
        
        if resultado:
            print("\nConsulta concluída com sucesso!")
        else:
            print("\nConsulta não retornou resultados.")
            
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário")
    except Exception as e:
        print(f"\nErro fatal: {str(e)}")