import os
import geopandas as gpd

pasta = "D:/P.I.5/Mapa-1-SHP/ShapeCom_Vetos"  

# Lista todos os arquivos .shp da pasta
arquivos_shp = [f for f in os.listdir(pasta) if f.endswith(".shp")]

print("Shapefiles encontrados:")
for nome_arquivo in arquivos_shp:
    print("-", nome_arquivo)

# Para cada shapefile, abrir e mostrar colunas e amostra
for nome_arquivo in arquivos_shp:
    print("\nLendo:", nome_arquivo)
    caminho_completo = os.path.join(pasta, nome_arquivo)
    
    try:
        gdf = gpd.read_file(caminho_completo)
        print("Colunas disponíveis:", gdf.columns.tolist())
        print("Amostra de dados:")
        print(gdf.head(3))
    except Exception as e:
        print("Erro ao ler:", nome_arquivo)
        print("Motivo:", e)
