import os
import re
import json
from collections import defaultdict
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import spacy

GOOGLE_API_KEY = "AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ"
MONGO_URI = 'mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/'
LEGISLACAO_PATH = "output/documento_completo_limpo.json"

ZONAS_INFO = {
    "ZR": {"nome": "Zona Residencial", "tipo": "residencial", "hierarquia": 1},
    "ZM1": {"nome": "Zona Mista 1", "tipo": "mista", "densidade": "baixa", "hierarquia": 2},
    "ZC4": {"nome": "Zona Central 4", "tipo": "central", "densidade": "alta", "hierarquia": 3},
    "DEFAULT": {"nome": "Zona não catalogada", "tipo": "indefinida"}
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
model_path = os.path.join(BASE_DIR, "models", "model-ngram3-v2", "model-best")
nlp = spacy.load(model_path)
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")
print("✅ Modelo carregado com sentencizer ativo.")

def get_zona_info(codigo):
    return ZONAS_INFO.get(codigo, ZONAS_INFO["DEFAULT"])

def carregar_legislacao():
    with open(LEGISLACAO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extrair_parametros(texto, codigo_zona):
    padroes = {
        "Densidade": r"(\d{1,4}\s*uh/ha)",
        "Área Mínima": r"(área mínima.*?(?:\d{1,3}(?:\.\d{3})*,?\d*\s*m²))",
        "Testada": r"(testada mínima.*?\d{1,2},?\d*\s*m)",
        "Altura": r"(altura (?:máxima|mínima).*?(?:\d{1,2},?\d*)\s*m)",
        "CA": r"(coeficiente de aproveitamento.*?\d+[,\.]\d*)",
        "Taxa": r"(taxa de ocupação.*?\d{1,3}%)",
        "EFP": r"(EFP.*?(?:obrigatório|opcional|exigido))",
        "APG": r"(Área de Planejamento e Gestão.*?[A-Z]{2,4})",
        "Exceções": r"(exceto para.*?(?:HU|comercial|residencial))"
    }
    
    parametros = []
    for nome, padrao in padroes.items():
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            parametros.append(f"{nome}: {match.group(1)}")
    
    # Se encontrar parâmetros, retorna eles + texto completo
    if parametros:
        return " | ".join(parametros) + f"\n   📄 Texto completo: {texto}"
    return texto  # Retorna o texto completo sem cortes

def menciona_somente_zona_alvo(sentenca, codigo_zona):
    zonas = [
        "ZR", "ZM1", "ZM2", "ZM4", "ZC2", "ZC4", "ZAE A", "ZAE B", "ZAE C",
        "ZAE-A", "ZAE-B", "ZAE-C", "ZAE-A-BG", "ZAE-C-BG",
        "ZM1-A-BG", "ZM1-B-BG", "ZM1-C-BG", "ZR-A", "ZR-B"
    ]
    outras_zonas = [z for z in zonas if z != codigo_zona and re.search(rf'\b{z}\b', sentenca)]
    return not outras_zonas

def classificar_relevancia(texto):
    termos_chave = {
        "obrigatório": 3,
        "proibido": 3,
        "exceção": 2,
        "permitido": 1,
        "pode": 1
    }
    return sum(peso for termo, peso in termos_chave.items() if termo in texto.lower())

def consultar_legislacao_por_zona(codigo_zona):
    documento = carregar_legislacao()
    resultado = defaultdict(list)
    for bloco in documento:
        texto = str(bloco)
        if not texto.strip():
            continue
        doc = nlp(texto)
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if len(sent_text) < 20 or "exemplo" in sent_text.lower():
                continue
            if not re.search(rf'\b{codigo_zona}\b(?!-)', sent_text):
                continue
            doc_sent = nlp(sent_text)
            score = doc_sent.cats.get(codigo_zona, 0)
            if score > 0.5 or menciona_somente_zona_alvo(sent_text, codigo_zona):
                texto_processado = extrair_parametros(sent_text, codigo_zona)
                resultado[codigo_zona].append(texto_processado)
    return resultado

def obter_coordenadas_cep(cep):
    try:
        geolocator = GoogleV3(api_key=GOOGLE_API_KEY)
        location = geolocator.geocode(f"{cep}, Campinas, SP", timeout=10)
        return (location.latitude, location.longitude, location.address) if location else None
    except Exception as e:
        print(f"❌ Erro na geolocalização: {e}")
        return None

def localizar_zona(lat, lon):
    client = MongoClient(MONGO_URI)
    collection = client['PI5']['coordenadas']
    ponto = {"type": "Point", "coordinates": [lon, lat]}
    return collection.find_one({"geometry": {"$geoIntersects": {"$geometry": ponto}}})

def formatar_item_legislativo(texto, codigo_zona):
    # Primeiro: preservar o texto original sem modificações desnecessárias
    texto = texto.strip()
    
    # Destacar o código da zona (sem alterar a estrutura)
    texto = re.sub(
        rf'\b{codigo_zona}\b', 
        f'【{codigo_zona}】', 
        texto,
        flags=re.IGNORECASE
    )
    
    # Identificar e formatar fórmulas matemáticas primeiro
    formulas = re.findall(r'([A-Za-z]{2,}\s*=.+?)(?=[;.]|$)', texto)
    for formula in formulas:
        texto = texto.replace(
            formula, 
            f"\n   🧮 Fórmula: {formula.strip()}"
        )
    
    # Quebras de linha apenas para itens de lista
    texto = re.sub(
        r'([IVX]+)\s*-\s*([A-Z])', 
        r'\n   \1 - \2', 
        texto
    )
    
    return texto

def processar_formulas(texto):
    # Identifica e formata melhor as fórmulas matemáticas
    formulas = re.findall(r'([A-Za-z]+\s*[=<>].*?(?:[.;]|$))', texto)
    for formula in formulas:
        texto = texto.replace(formula, f"\n   🧮 Fórmula: {formula.strip()}")
    return texto

def formatar_saida(trechos, codigo_zona):
    saida = []
    for topico, itens in trechos.items():
        itens_unicos = list(dict.fromkeys(itens))[:5]  # Limitar a 5 itens sem cortar
        
        if not itens_unicos:
            continue
            
        saida.append(f"\n📌 {topico.replace('_', ' ').title()}:")
        for i, item in enumerate(itens_unicos, 1):
            item_formatado = formatar_item_legislativo(item, codigo_zona)
            saida.append(f"  {i}. {item_formatado}")
    
    if not saida:
        return "⚠️ Nenhum dispositivo legal específico encontrado"
    
    return "\n".join([
        "\nℹ️ LEGENDA: DENS=Densidade | ALT=Altura | CA=Coef.Aproveitamento",
        *saida
    ])

def main():
    cep = input("Digite o CEP (formato 13000-000): ").strip()
    try:
        coordenadas = obter_coordenadas_cep(cep)
        if not coordenadas:
            print("\n❌ Geolocalização não encontrada para o CEP")
            return
        lat, lon, endereco = coordenadas
        print(f"\n🔎 Endereço encontrado: {endereco.split(',')[0]}")
        print(f"📍 Coordenadas: {lat:.6f}, {lon:.6f}")
        zona = localizar_zona(lat, lon)
        if not zona:
            print("\n❌ Zona urbana não identificada")
            return
        codigo = zona.get("properties", {}).get("duos", "INDEFINIDO")
        zona_info = get_zona_info(codigo)
        print(f"\n✅ Zona Identificada: {zona_info['nome']} ({codigo})")
        print(f"📋 Tipo: {zona_info['tipo'].capitalize()}")
        if 'densidade' in zona_info:
            print(f"📊 Densidade: {zona_info['densidade'].capitalize()}")
        trechos = consultar_legislacao_por_zona(codigo)
        print("\n📜 Dispositivos Legais Relevantes:")
        print(formatar_saida(trechos, codigo))
    except Exception as e:
        print(f"\n⚠️ Erro: {str(e)}")

if __name__ == "__main__":
    main()
