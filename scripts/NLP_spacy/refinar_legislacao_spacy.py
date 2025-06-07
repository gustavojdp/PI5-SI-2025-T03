import os
import re
import json
from collections import defaultdict
from pymongo import MongoClient
from shapely.geometry import shape, Point
from geopy.geocoders import GoogleV3
import spacy

# Configurações globais
GOOGLE_API_KEY = "AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ"  # Chave temporária para desenvolvimento
MONGO_URI = 'mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/'
LEGISLACAO_PATH = "output/documento_completo_limpo.json"

# Dicionário de zonas otimizado
ZONAS_INFO = {
    "ZR": {"nome": "Zona Residencial", "tipo": "residencial", "hierarquia": 1},
    "ZM1": {"nome": "Zona Mista 1", "tipo": "mista", "densidade": "baixa", "hierarquia": 2},
    "ZC4": {"nome": "Zona Central 4", "tipo": "central", "densidade": "alta", "hierarquia": 3},
    # Adicione todas as outras zonas conforme necessário
    "DEFAULT": {"nome": "Zona não catalogada", "tipo": "indefinida"}
}

# Carrega modelo spaCy
nlp = spacy.load("pt_core_news_sm")

# Palavras-chave melhoradas
palavras_chave = {
    "uso_permitido": r"(uso permitido|permitido|autorizado)",
    "altura_maxima": r"(altura máxima|limite vertical|altura edificação)",
    "densidade_maxima": r"(densidade habitacional|uh/ha|unidades por hectare)",
    "parcelamento": r"(parcelamento|área mínima|testada|loteamento)",
    "recuos_afastamentos": r"(recuo|afastamento|distanciamento|divisa)",
    "observacoes": r"(condição|restrição|observação|EIV|RIV)"
}

def get_zona_info(codigo):
    """Obtém informações estruturadas sobre a zona"""
    return ZONAS_INFO.get(codigo, ZONAS_INFO["DEFAULT"])

def carregar_legislacao():
    """Carrega o documento legislativo com cache"""
    with open(LEGISLACAO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extrair_parametros(texto, codigo_zona):
    """Extrai apenas os parâmetros numéricos relevantes"""
    padroes = {
        "densidade": rf"{codigo_zona}.*?(\d+uh/ha.*?\d+uh/ha)",
        "área": rf"{codigo_zona}.*?(\d+\.?\d*m²|\d+\.?\d* metros quadrados)",
        "altura": rf"{codigo_zona}.*?(\d+\.?\d*m|\d+\.?\d* metros)",
        "CA": rf"{codigo_zona}.*?(CA\s*[=:]\s*\d+\.?\d*)"
    }
    
    for parametro, padrao in padroes.items():
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1)
    return texto[:150] + "..." if len(texto) > 150 else texto

def consultar_legislacao_por_zona(codigo_zona):
    """Consulta otimizada com filtros rigorosos"""
    documento = carregar_legislacao()
    resultado = defaultdict(list)
    
    for bloco in documento:
        texto = str(bloco)
        if not texto.strip():
            continue
            
        doc = nlp(texto)
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Filtros rigorosos
            if (len(sent_text) < 20 or 
                not any(token.pos_ == "VERB" for token in sent) or
                "exemplo" in sent_text.lower()):
                continue
                
            # Verifica menção específica à zona
            if not re.search(rf'\b{codigo_zona}\b(?!-)', sent_text):
                continue
                
            # Classifica e processa o texto
            categoria = classificar_sentenca(sent_text)
            texto_processado = extrair_parametros(sent_text, codigo_zona)
            resultado[categoria].append(texto_processado)
            
    return resultado

def classificar_sentenca(texto):
    """Classificação melhorada com regex"""
    for categoria, padrao in palavras_chave.items():
        if re.search(padrao, texto, re.IGNORECASE):
            return categoria
    return "observacoes"

def obter_coordenadas_cep(cep):
    """Geocoding com tratamento de erros"""
    try:
        geolocator = GoogleV3(api_key=GOOGLE_API_KEY)
        location = geolocator.geocode(f"{cep}, Campinas, SP", timeout=10)
        return (location.latitude, location.longitude, location.address) if location else None
    except Exception as e:
        print(f"❌ Erro na geolocalização: {e}")
        return None

def localizar_zona(lat, lon):
    """Consulta otimizada ao MongoDB"""
    client = MongoClient(MONGO_URI)
    collection = client['PI5']['coordenadas']
    ponto = {"type": "Point", "coordinates": [lon, lat]}
    return collection.find_one({"geometry": {"$geoIntersects": {"$geometry": ponto}}})

def formatar_texto_legislativo(texto, codigo_zona, max_len=500):
    """Formata o texto legislativo para exibição limpa"""
    # 1. Remove quebras de linha múltiplas e espaços excessivos
    texto = ' '.join(texto.split())
    
    # 2. Destaca a zona mencionada
    texto = re.sub(rf'\b{codigo_zona}\b', f'**{codigo_zona}**', texto)
    
    # 3. Encontra o ponto de corte natural mais próximo
    if len(texto) > max_len:
        # Tenta encontrar um ponto final próximo ao limite
        corte = texto.rfind('.', 0, max_len)
        if corte == -1:
            corte = texto.rfind(';', 0, max_len)
        if corte == -1:
            corte = texto.rfind(' ', 0, max_len)
        texto = texto[:corte] + " [...]" if corte != -1 else texto[:max_len] + "..."
    
    # 4. Remove enumerações muito longas
    if texto.count(';') > 3:
        partes = [p for p in texto.split(';') if codigo_zona in p]
        texto = ';'.join(partes[:2]) + (' [...]' if len(partes) > 2 else '')
    
    return texto

def formatar_item_legislativo(texto, codigo_zona):
    """Formata cada item legislativo para destacar informações-chave"""
    # 1. Remove espaços múltiplos e quebras de linha
    texto = ' '.join(texto.split())
    
    # 2. Extrai apenas os parágrafos que mencionam a zona específica
    if ';' in texto and texto.count(';') > 2:
        partes = [p.strip() for p in texto.split(';') if codigo_zona in p]
        if partes:
            texto = '; '.join(partes[:2]) + (' [...]' if len(partes) > 2 else '')
    
    # 3. Extrai valores numéricos e parâmetros importantes
    padroes = [
        (r'(\d+\.?\d*\s*uh/ha)', 'Densidade: {}'),
        (r'(\d+\.?\d*\s*m²)', 'Área: {}'),
        (r'(CA\s*[=:]\s*\d+\.?\d*)', 'Coef. Aproveitamento: {}'),
        (r'(testada\s*mínima\s*\d+\.?\d*\s*m)', 'Testada: {}')
    ]
    
    for padrao, formato in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return formato.format(match.group(1))
    
    # 4. Truncamento inteligente se necessário
    if len(texto) > 150:
        corte = texto.find('.', 100)
        if corte == -1:
            corte = texto.find(';', 100)
        texto = texto[:corte+1 if corte != -1 else 120] + ' [...]'
    
    return texto

def formatar_saida(trechos, codigo_zona):
    """Gera a saída formatada agrupando por tópicos"""
    saida = []
    for topico, itens in trechos.items():
        itens_unicos = list(dict.fromkeys(itens))[:3]  # Remove duplicatas e limita a 3 itens
        
        if not itens_unicos:
            continue
            
        saida.append(f"\n🔹 {topico.replace('_', ' ').title()}:")
        for i, item in enumerate(itens_unicos, 1):
            item_formatado = formatar_item_legislativo(item, codigo_zona)
            # Destaca a zona mencionada
            item_formatado = re.sub(rf'\b{codigo_zona}\b', f'**{codigo_zona}**', item_formatado)
            saida.append(f"  {i}. {item_formatado}")
    
    return "\n".join(saida) if saida else "⚠️ Nenhum dispositivo específico encontrado"

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
        
        # Exibe informações da zona
        print(f"\n✅ Zona Identificada: {zona_info['nome']} ({codigo})")
        print(f"📋 Tipo: {zona_info['tipo'].capitalize()}")
        if 'densidade' in zona_info:
            print(f"📊 Densidade: {zona_info['densidade'].capitalize()}")
        
        # Consulta e exibe a legislação
        trechos = consultar_legislacao_por_zona(codigo)
        print("\n📜 Dispositivos Legais Relevantes:")
        print(formatar_saida(trechos, codigo))
        
    except Exception as e:
        print(f"\n⚠️ Erro: {str(e)}")

if __name__ == "__main__":
    main()