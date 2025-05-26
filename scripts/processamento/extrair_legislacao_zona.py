import json
from collections import defaultdict
import re
from dicionario_zonas import dicionario_zonas

# Caminho para o arquivo de texto da LC 208/2018
CAMINHO_JSON = "D:\\P.I.5\\campinas_zoneamento\\output\\documento_completo.json"

# Carrega o JSON do texto completo com fallback de decodificação
with open(CAMINHO_JSON, "rb") as f:
    documento = json.loads(f.read().decode("utf-8", errors="replace"))

paginas = documento.get("conteudo", [])
legislacoes_por_zona = defaultdict(list)

# Adiciona novos tópicos de interesse para extração
topicos_adicionais = [
    "densidade", "parcelamento", "regras de uso", "observações adicionais", "tipologia", "restrições", "normas específicas"
]

# Procura cada sigla de zona em cada página
total_paginas = len(paginas)
for i, pagina in enumerate(paginas):
    for sigla in dicionario_zonas:
        padrao = rf"\b{re.escape(sigla)}\b"
        if re.search(padrao, pagina, re.IGNORECASE):
            legislacoes_por_zona[sigla].append(f"[Página {i+1}]\n" + pagina.strip())

    # Busca por novos tópicos adicionais nas páginas
    for topico in topicos_adicionais:
        if re.search(rf"{re.escape(topico)}", pagina, re.IGNORECASE):
            legislacoes_por_zona[f"{topico}_adicional"].append(f"[Página {i+1}]\n" + pagina.strip())

# Salva os resultados em um novo JSON
with open("zonas_legislacao_extraida_atualizado.json", "w", encoding="utf-8") as f:
    json.dump(legislacoes_por_zona, f, indent=2, ensure_ascii=False)

print("✅ Extração concluída. Arquivo 'zonas_legislacao_extraida_atualizado.json' gerado.")

zonas_extraidas = set(legislacoes_por_zona.keys())
zonas_esperadas = set(dicionario_zonas.keys())
faltando = zonas_esperadas - zonas_extraidas
print(f"⚠️ Zonas sem legislação extraída: {faltando}")
