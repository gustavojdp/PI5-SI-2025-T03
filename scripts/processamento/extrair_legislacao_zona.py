import json
from collections import defaultdict
import re
from dicionario_zonas import dicionario_zonas

# Caminho para o arquivo de texto da LC 208/2018
CAMINHO_JSON = "documento_completo.json"

# Carrega o JSON do texto completo com fallback de decodificação
with open(CAMINHO_JSON, "rb") as f:
    documento = json.loads(f.read().decode("utf-8", errors="replace"))

paginas = documento.get("conteudo", [])
legislacoes_por_zona = defaultdict(list)

# Procura cada sigla de zona em cada página
total_paginas = len(paginas)
for i, pagina in enumerate(paginas):
    for sigla in dicionario_zonas:
        padrao = rf"\b{re.escape(sigla)}\b"
        if re.search(padrao, pagina, re.IGNORECASE):
            legislacoes_por_zona[sigla].append(f"[Página {i+1}]\n" + pagina.strip())

# Salva os resultados em um novo JSON
with open("zonas_legislacao_extraida.json", "w", encoding="utf-8") as f:
    json.dump(legislacoes_por_zona, f, indent=2, ensure_ascii=False)

print("✅ Extração concluída. Arquivo 'zonas_legislacao_extraida.json' gerado.")