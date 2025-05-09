import json
import re

# Abrir e ler o arquivo
with open('output/documento_completo.json', 'r', encoding='utf-8') as file:
    conteudo = file.read()

# Se for JSON válido, tentar extrair texto
try:
    data = json.loads(conteudo)
    if isinstance(data, list):
        texto = ' '.join([str(item.get('texto', '')) for item in data])
    else:
        texto = str(data)
except json.JSONDecodeError:
    texto = conteudo

# Combinar múltiplos padrões
padroes = [
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [0-9]+)\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [A-Z])\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+)\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+)\s*\((Z[A-Z0-9 ]{1,6})\)',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [A-Z])\s*\((Z[A-Z0-9 ]{1,6})\)',
]

regex_zona = re.compile('|'.join(padroes))

# Extrair todas as zonas
ocorrencias = list(regex_zona.finditer(texto))
zonas_legislacao = {}

for i, match in enumerate(ocorrencias):
    grupos = [g for g in match.groups() if g]
    if len(grupos) < 2:
        continue
    nome_completo, codigo = grupos[0], grupos[1]
    inicio = match.end()
    fim = ocorrencias[i + 1].start() if i + 1 < len(ocorrencias) else len(texto)
    trecho = texto[inicio:fim].strip()
    zonas_legislacao[f"{nome_completo.strip()} - {codigo.strip()}"] = trecho[:2000]

# Salvar resultado
with open('zonas_legislacao_filtradas.json', 'w', encoding='utf-8') as out:
    json.dump(zonas_legislacao, out, ensure_ascii=False, indent=2)

print(f"✅ Zonas detectadas: {len(zonas_legislacao)} e salvas em 'zonas_legislacao_filtradas.json'")
