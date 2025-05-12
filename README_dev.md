# 📘 Documentação Técnica - PI5

Este documento detalha os scripts do projeto, suas funções e localizações.

---

## 📂 scripts/importacao

- `importar_zonas_shp.py`  
  Lê arquivos `.shp` da pasta `shapefiles/` e insere os polígonos no banco `PI5.coordenadas`.

---

## 📂 scripts/processamento

- `extrair_pdf_texto.py`  
  Extrai o texto do PDF do plano diretor de Campinas e salva como `documento_completo.json`.

- `processar_legislacao_nlp.py`  
  Lê o JSON extraído e realiza processamento de linguagem natural (NLP) para associar leis às zonas.

---

## 📂 scripts/consultas

- `consultar_zona_por_cep.py`  
  Consulta um CEP, converte para coordenadas e verifica em qual zona ele cai com base na collection `coordenadas` ou `zonas`.

---

## 📂 main.py

Script de testes gerais. Pode ser usado para integrar os passos anteriores em um fluxo só.

---

## Dados de entrada

- `dados/pdf/`: PDF original do plano diretor
- `dados/geojson/`: Mapa de zoneamento já estruturado
- `dados/shapefiles/`: Shapefiles geográficos originais

## Dados de saída

- `output/documento_completo.json`: texto cru do PDF
- `output/zonas_legislacao_filtradas.json`: leis por zona extraídas via NLP

