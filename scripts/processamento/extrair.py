import fitz  # PyMuPDF
import json

caminho_pdf = "D:/P.I.5/Lei-complementar-208-2018-Campinas-SP.pdf"

with fitz.open(caminho_pdf) as doc:
    paginas = [pagina.get_text() for pagina in doc]

with open("documento_completo.json", "w", encoding="utf-8") as f:
    json.dump({"conteudo": paginas}, f, ensure_ascii=False, indent=2)

print("✅ Extração concluída com sucesso!")
