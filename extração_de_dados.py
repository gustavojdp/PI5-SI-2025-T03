import fitz  # PyMuPDF
import json

# Caminho do PDF
pdf_path = "C:\\Users\\PC Gamer\\Documents\\PI5\\codigo_de_obras_ilustrado.pdf"

# Função para extrair dados do PDF
def extrair_dados_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    
    texto_completo = ""
    
    for pagina_num in range(doc.page_count):
        pagina = doc.load_page(pagina_num)
        texto_completo += pagina.get_text()
    
    return texto_completo

# Função para salvar os dados extraídos em JSON
def salvar_dados_json(texto):
    dados = {
        "texto": texto,
        "leis": encontrar_leis(texto)  # A função 'encontrar_leis' que já discutimos
    }
    
    with open("dados_extraidos.json", "w") as f:
        json.dump(dados, f, indent=4)

# Função para encontrar leis usando regex
def encontrar_leis(texto):
    import re
    padrao = r"Lei(?: [Cc]omplementar)?(?: nº)? ?\d+[\.\d]*/\d{4}"
    leis = re.findall(padrao, texto)
    return leis

# Extração e salvamento
texto_extraido = extrair_dados_pdf(pdf_path)
salvar_dados_json(texto_extraido)

print("Dados extraídos e salvos com sucesso!")
