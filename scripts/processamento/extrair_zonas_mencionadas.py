import json
import re

# Carregar texto extraído do plano diretor
with open('output/documento_completo.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    texto = data.get("conteudo", "")

# Padrões para encontrar menções a zonas no meio do texto
padroes = [
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [0-9]+)\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [A-Z])\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+)\s*[-:]?\s*(Z[A-Z0-9 ]{1,6})',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+)\s*\((Z[A-Z0-9 ]{1,6})\)',
    r'\b(Zona [A-ZÁÂÉÍÓÚÃÕÇa-zç]+ [A-Z])\s*\((Z[A-Z0-9 ]{1,6})\)'
]

regex_zonas = re.compile(
    r'(Zona(?: de)?(?: [A-ZÁÂÉÍÓÚÃÕÇa-zç]+){1,4})\s*[-–:]?\s*(Z[A-Z0-9]{1,4}(?: [A-Z])?)'
)

# Extração
zonas_extraidas = {}
for match in regex_zonas.finditer(texto):
    grupos = [g for g in match.groups() if g]
    if len(grupos) >= 2:
        nome, codigo = grupos[0].strip(), grupos[1].strip()
        zonas_extraidas[codigo] = nome

# Salvar resultado
with open('output/zonas_extraidas_lista.json', 'w', encoding='utf-8') as f:
    json.dump(zonas_extraidas, f, ensure_ascii=False, indent=2)

print(f"✅ Zonas únicas extraídas: {len(zonas_extraidas)} e salvas em 'output/zonas_extraidas_lista.json'")
