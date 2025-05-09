import os
import geopandas as gpd
from pymongo import MongoClient

# Conexão com MongoDB
client = MongoClient('mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/')
db = client['PI5']
collection = db['coordenadas']

# Caminho da pasta principal
base_path = r'D:/P.I.5/shapefiles_campinas/'

# Loop pelas subpastas
count_total = 0
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.shp'):
            caminho_shp = os.path.join(root, file)
            try:
                gdf = gpd.read_file(caminho_shp)
                gdf = gdf.to_crs(epsg=4326)
                gdf = gdf[gdf.geometry.notnull()]
                for _, row in gdf.iterrows():
                    feature = {
                        'type': 'Feature',
                        'geometry': row['geometry'].__geo_interface__,
                        'properties': row.drop('geometry').to_dict()
                    }
                    collection.insert_one(feature)
                    count_total += 1
                print(f"✅ Importado: {file} com {len(gdf)} feições")
            except Exception as e:
                print(f"⚠️ Erro ao processar {file}: {e}")

print(f"\n🎯 Total de documentos inseridos: {count_total}")
