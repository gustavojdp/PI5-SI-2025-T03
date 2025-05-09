import fitz  # PyMuPDF
import json

# Caminho do PDF
caminho_pdf = "D:\\P.I.5\\Lei-complementar-208-2018-Campinas-SP.pdf"

# Abrir o PDF e extrair texto
with fitz.open(caminho_pdf) as doc:
    texto_completo = ""
    for pagina in doc:
        texto_completo += pagina.get_text()

# Salvar texto em JSON
with open('documento_completo.json', 'w', encoding='utf-8') as f:
    json.dump({"conteudo": texto_completo}, f, ensure_ascii=False, indent=2)

print("✅ Texto completo salvo em 'documento_completo.json'")
