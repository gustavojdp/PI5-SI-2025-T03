import os
import re
import json
from collections import defaultdict
from pymongo import MongoClient
from geopy.geocoders import GoogleV3
import spacy
from spacy.matcher import Matcher

# Configurações globais
GOOGLE_API_KEY = "AIzaSyDM59RDQwNKWBOVqjjKhva8cdHGrwu9gEQ"
MONGO_URI = 'mongodb+srv://pi5:remanejamento123@pi5.lytfpix.mongodb.net/'
LEGISLACAO_PATH = "output/documento_completo_limpo.json"

# CAMINHO PARA SEU MODELO TREINADO
MODELO_TREINADO_PATH = "modelo_zonas_urbanas"  

# Inicialização do spaCy com modelo treinado
def carregar_modelo_nlp():
    """Carrega o modelo spaCy - prioriza o modelo treinado"""
    try:
        # Primeiro tenta carregar seu modelo treinado
        if os.path.exists(MODELO_TREINADO_PATH):
            print(f"🧠 Carregando modelo treinado: {MODELO_TREINADO_PATH}")
            
            # Verifica se o config.cfg existe e corrige se necessário
            config_path = os.path.join(MODELO_TREINADO_PATH, "config.cfg")
            if os.path.exists(config_path):
                # OPÇÃO 1: Tentar corrigir
                corrigir_config_spacy(config_path)
                
                # OPÇÃO 2: Se ainda falhar, recriar do zero
                try:
                    nlp = spacy.load(MODELO_TREINADO_PATH)
                    print("✅ Modelo treinado carregado com sucesso!")
                    return nlp, True
                except Exception as e2:
                    print(f"⚠️ Correção simples falhou: {e2}")
                    print("🔄 Recriando config.cfg...")
                    recriar_config_spacy(config_path)
                    nlp = spacy.load(MODELO_TREINADO_PATH)
                    print("✅ Modelo treinado carregado após recriar config!")
                    return nlp, True
            else:
                # Se não existe config.cfg, cria um
                print("📝 Criando config.cfg...")
                recriar_config_spacy(config_path)
                nlp = spacy.load(MODELO_TREINADO_PATH)
                print("✅ Modelo treinado carregado com novo config!")
                return nlp, True
                
        else:
            print(f"⚠️ Modelo treinado não encontrado em: {MODELO_TREINADO_PATH}")
            print("📦 Tentando carregar modelo padrão...")
            
    except Exception as e:
        print(f"❌ Erro ao carregar modelo treinado: {e}")
        print("📦 Tentando carregar modelo padrão...")
    
    # Fallback para modelo padrão
    try:
        nlp = spacy.load("pt_core_news_sm")
        print("✅ Modelo padrão pt_core_news_sm carregado")
        return nlp, False  # False indica que é modelo padrão
    except OSError:
        print("⚠️ Modelo pt_core_news_sm não encontrado. Execute: python -m spacy download pt_core_news_sm")
        return None, False

def corrigir_config_spacy(config_path):
    """Corrige o arquivo config.cfg do spaCy"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # CORREÇÃO: Remove as aspas ao redor da lista para que seja interpretada como lista Python
        # Padrão antigo (INCORRETO): pipeline = "["sentencizer", "textcat_multilabel"]"
        # Padrão novo (CORRETO): pipeline = ["sentencizer", "textcat_multilabel"]
        
        # Remove aspas duplas ao redor da definição da lista
        content = re.sub(
            r'pipeline\s*=\s*"?\[.*?\]"?.*',
            'pipeline = ["sentencizer", "textcat_multilabel"]',
            content
        )
        
        # Remove comentários que podem estar causando problemas
        content = re.sub(
            r'pipeline\s*=\s*\[.*?\]\s*#.*',
            'pipeline = ["sentencizer", "textcat_multilabel"]',
            content
        )
        
        # Salva o arquivo corrigido
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("🔧 Arquivo config.cfg corrigido")
        
    except Exception as e:
        print(f"⚠️ Erro ao corrigir config.cfg: {e}")

# ALTERNATIVA: Função para recriar o config.cfg do zero
def recriar_config_spacy(config_path):
    """Recria o arquivo config.cfg com configuração válida"""
    try:
        config_content = """[nlp]
lang = "pt"
pipeline = ["sentencizer", "textcat_multilabel"]
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000

[tokenizer]
@tokenizers = "spacy.Tokenizer.v1"

[vectors]
@vectors = "spacy.Vectors.v1"

[components]

[components.sentencizer]
factory = "sentencizer"

[components.textcat_multilabel]
factory = "textcat_multilabel"

[corpora]

[training]

[pretraining]
"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("🔧 Arquivo config.cfg recriado")
        
    except Exception as e:
        print(f"⚠️ Erro ao recriar config.cfg: {e}")

def criar_modelo_spacy_basico():
    """Cria um modelo spaCy básico para análise urbana se não existir"""
    if os.path.exists(MODELO_TREINADO_PATH):
        return
    
    print("🏗️ Criando modelo spaCy básico para análise urbana...")
    
    try:
        # Carrega modelo base
        nlp = spacy.load("pt_core_news_sm")
        
        # Adiciona matcher personalizado
        matcher = Matcher(nlp.vocab)
        
        # Padrões específicos para legislação urbana
        padroes_legislacao = {
            "ZONA": [
                [{"TEXT": {"REGEX": r"^Z[A-Z]+\d*$"}}],  # ZR, ZM1, ZC2, etc.
                [{"LOWER": "zona"}, {"IS_ALPHA": True}]
            ],
            "USO_PERMITIDO": [
                [{"LOWER": {"IN": ["uso", "atividade"]}}, {"LOWER": {"IN": ["permitido", "autorizado"]}}],
                [{"LOWER": {"IN": ["hmv", "hcsei", "csei"]}}]
            ],
            "PARAMETRO_NUMERICO": [
                [{"IS_DIGIT": True}, {"LOWER": {"IN": ["m²", "m", "uh/ha", "metros"]}}],
                [{"LOWER": "ca"}, {"IS_DIGIT": True}]
            ]
        }
        
        for label, patterns in padroes_legislacao.items():
            try:
                matcher.add(label, patterns)
            except Exception as e:
                print(f"⚠️ Erro ao adicionar padrão {label}: {e}")
        
        # Salva o modelo
        os.makedirs(MODELO_TREINADO_PATH, exist_ok=True)
        nlp.to_disk(MODELO_TREINADO_PATH)
        
        print(f"✅ Modelo básico criado em: {MODELO_TREINADO_PATH}")
        
    except Exception as e:
        print(f"❌ Erro ao criar modelo básico: {e}")

# Carrega o modelo
nlp, eh_modelo_treinado = carregar_modelo_nlp()

# Se não conseguiu carregar, tenta criar um básico
if not nlp:
    criar_modelo_spacy_basico()
    nlp, eh_modelo_treinado = carregar_modelo_nlp()

# Dicionário expandido de zonas
ZONAS_INFO = {
    "ZR": {"nome": "Zona Residencial", "tipo": "residencial", "densidade": "baixa"},
    "ZM1": {"nome": "Zona Mista 1", "tipo": "mista", "densidade": "baixa"},
    "ZM2": {"nome": "Zona Mista 2", "tipo": "mista", "densidade": "média"},
    "ZM4": {"nome": "Zona Mista 4", "tipo": "mista", "densidade": "alta"},
    "ZC2": {"nome": "Zona de Centralidade 2", "tipo": "central", "densidade": "média"},
    "ZC4": {"nome": "Zona de Centralidade 4", "tipo": "central", "densidade": "alta"},
    "ZAE": {"nome": "Zona de Atividades Especiais", "tipo": "especial", "densidade": "variável"},
    "ZPI": {"nome": "Zona de Preservação e Interesse", "tipo": "preservação", "densidade": "baixa"},
    "ZIS": {"nome": "Zona de Interesse Social", "tipo": "social", "densidade": "média"},
    "DEFAULT": {"nome": "Zona não catalogada", "tipo": "indefinida", "densidade": "não definida"}
}

# Padrões spaCy para categorização mais precisa
PADROES_SPACY = {
    "uso_permitido": [
        [{"LOWER": {"IN": ["uso", "atividade", "função"]}}, {"LOWER": {"IN": ["permitido", "autorizado", "admitido"]}}],
        [{"LOWER": "permitido"}, {"LOWER": {"IN": ["o", "a"]}}, {"LOWER": {"IN": ["uso", "atividade"]}}],
        [{"LOWER": {"IN": ["tipos", "categorias"]}}, {"LOWER": "de"}, {"LOWER": "uso"}],
        [{"LOWER": {"IN": ["hmv", "hcsei", "csei"]}}, {"LOWER": {"IN": ["permitido", "autorizado"]}}]
    ],
    "altura_maxima": [
        [{"LOWER": "altura"}, {"LOWER": {"IN": ["máxima", "limite", "permitida"]}}],
        [{"LOWER": {"IN": ["gabarito", "pavimentos", "andares"]}}],
        [{"LOWER": "limite"}, {"LOWER": "vertical"}],
        [{"IS_DIGIT": True}, {"LOWER": {"IN": ["metros", "m", "pavimentos"]}}]
    ],
    "densidade": [
        [{"LOWER": {"IN": ["densidade", "coeficiente"]}}, {"LOWER": {"IN": ["populacional", "aproveitamento"]}}],
        [{"LOWER": "ca"}, {"IS_DIGIT": True}],
        [{"LOWER": "uh"}, {"LOWER": "/"}, {"LOWER": "ha"}],
        [{"IS_DIGIT": True}, {"LOWER": "uh"}, {"LOWER": "/"}, {"LOWER": "ha"}]
    ],
    "parcelamento": [
        [{"LOWER": {"IN": ["área", "lote"]}}, {"LOWER": {"IN": ["mínima", "mínimo"]}}],
        [{"LOWER": {"IN": ["testada", "frente"]}}, {"LOWER": "mínima"}],
        [{"LOWER": "parcelamento"}, {"LOWER": "do"}, {"LOWER": "solo"}],
        [{"IS_DIGIT": True}, {"LOWER": {"IN": ["m²", "metros", "quadrados"]}}]
    ],
    "recuos": [
        [{"LOWER": {"IN": ["recuo", "afastamento"]}}, {"LOWER": {"IN": ["frontal", "lateral", "fundo"]}}],
        [{"LOWER": "distância"}, {"LOWER": {"IN": ["mínima", "da"]}}, {"LOWER": "divisa"}],
        [{"LOWER": "facultativo"}]
    ],
    "restricoes": [
        [{"LOWER": {"IN": ["restrição", "condição", "exigência"]}}, {"LOWER": {"IN": ["especial", "adicional"]}}],
        [{"LOWER": {"IN": ["eiv", "riv"]}}, {"LOWER": {"IN": ["obrigatório", "necessário"]}}],
        [{"LOWER": "estudo"}, {"LOWER": "de"}, {"LOWER": "impacto"}],
        [{"LOWER": {"IN": ["proibido", "vedado", "não", "permitido"]}}]
    ]
}

def inicializar_matcher():
    """Inicializa o Matcher do spaCy com padrões específicos"""
    if not nlp:
        return None
    
    matcher = Matcher(nlp.vocab)
    
    for categoria, padroes in PADROES_SPACY.items():
        try:
            matcher.add(categoria.upper(), padroes)
        except Exception as e:
            print(f"⚠️ Erro ao adicionar padrão {categoria}: {e}")
    
    return matcher

def categorizar_com_modelo_treinado(texto):
    """
    Usa o modelo treinado para categorização se disponível
    """
    if not nlp or not eh_modelo_treinado:
        return None
    
    try:
        doc = nlp(texto)
        
        # Se seu modelo tem um componente de classificação customizado
        if hasattr(doc, 'cats') and doc.cats: 
            categoria_principal = max(doc.cats, key=doc.cats.get)
            confianca = doc.cats[categoria_principal]
            
            # Só usa se a confiança for alta
            if confianca > 0.5:
                return categoria_principal
        
        # Se seu modelo usa entidades nomeadas (NER)
        if doc.ents:
            for ent in doc.ents:
                if ent.label_ in ["USO_PERMITIDO", "ALTURA_MAXIMA", "DENSIDADE", "PARCELAMENTO", "RECUOS", "RESTRICOES"]:
                    return ent.label_.lower()
        
        # Se seu modelo usa componente customizado
        if hasattr(doc._, 'categoria_urbana'):
            return doc._.categoria_urbana
            
    except Exception as e:
        print(f"⚠️ Erro na classificação com modelo treinado: {e}")
    
    return None

def categorizar_dispositivo_spacy(texto, matcher):
    """Categoriza usando modelo treinado primeiro, depois fallback"""
    if not nlp:
        return categorizar_dispositivo_regex(texto)
    
    # PRIMEIRA TENTATIVA: Modelo treinado
    if eh_modelo_treinado:
        categoria_treinada = categorizar_com_modelo_treinado(texto)
        if categoria_treinada:
            return categoria_treinada
    
    # SEGUNDA TENTATIVA: Matcher com padrões
    if matcher:
        try:
            doc = nlp(texto)
            matches = matcher(doc)
            
            if matches:
                match_id, start, end = matches[0]
                categoria = nlp.vocab.strings[match_id].lower()
                return categoria
        except Exception as e:
            print(f"⚠️ Erro no matcher: {e}")
    
    # TERCEIRA TENTATIVA: Regex (fallback)
    return categorizar_dispositivo_regex(texto)

def extrair_entidades_treinadas(texto):
    """
    Extrai entidades específicas usando o modelo treinado
    """
    if not nlp or not eh_modelo_treinado:
        return {}
    
    try:
        doc = nlp(texto)
        entidades = {}
        
        for ent in doc.ents:
            if ent.label_ not in entidades:
                entidades[ent.label_] = []
            entidades[ent.label_].append({
                'texto': ent.text,
                'inicio': ent.start_char,
                'fim': ent.end_char,
                'confianca': getattr(ent, 'confidence', None)
            })
        
        return entidades
        
    except Exception as e:
        print(f"⚠️ Erro na extração de entidades: {e}")
        return {}

def get_zona_info(codigo):
    """Retorna informações da zona"""
    return ZONAS_INFO.get(codigo, ZONAS_INFO["DEFAULT"])

def carregar_legislacao():
    """Carrega o documento legislativo"""
    try:
        with open(LEGISLACAO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {LEGISLACAO_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON: {LEGISLACAO_PATH}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar legislação: {e}")
        return []

def is_dispositivo_especifico_zona(sentenca, codigo_zona_target):
    """
    Verifica se o dispositivo se aplica especificamente à zona consultada
    """
    # Lista de todas as zonas conhecidas
    todas_zonas = list(ZONAS_INFO.keys())[:-1]  # Remove 'DEFAULT'
    outras_zonas = [z for z in todas_zonas if z != codigo_zona_target]
    
    # Verifica se a sentença menciona a zona target
    if not re.search(rf'\b{re.escape(codigo_zona_target)}\b', sentenca, re.IGNORECASE):
        return False
    
    # Padrões que indicam aplicação específica à zona
    padroes_especificos = [
        rf'na\s+{re.escape(codigo_zona_target)}\b[^,]*?:',
        rf'para\s+.*?{re.escape(codigo_zona_target)}\b[^,]*?:',
        rf'{re.escape(codigo_zona_target)}\s*[^,]*?\s*:',
        rf'inseridos?\s+na\s+{re.escape(codigo_zona_target)}\b',
        rf'{re.escape(codigo_zona_target)}\s+com\s+(CA|coeficiente)',
        rf'zona.*?{re.escape(codigo_zona_target)}\b.*?:',
        rf'{re.escape(codigo_zona_target)}\s*[-–]\s*[^:]*?:'
    ]
    
    # Se encontrar padrão específico, é válido
    for padrao in padroes_especificos:
        if re.search(padrao, sentenca, re.IGNORECASE):
            return True
    
    # Verifica se é apenas uma enumeração
    zonas_mencionadas = []
    for zona in outras_zonas + [codigo_zona_target]:
        if re.search(rf'\b{re.escape(zona)}\b', sentenca, re.IGNORECASE):
            zonas_mencionadas.append(zona)
    
    # Se menciona muitas zonas, verifica contexto específico
    if len(zonas_mencionadas) >= 3:
        contexto_especifico = re.search(
            rf'{re.escape(codigo_zona_target)}\b[^;,]*?(?::|será|deverá|com|e\s+\**{re.escape(codigo_zona_target)}\**)',
            sentenca, re.IGNORECASE
        )
        return contexto_especifico is not None
    
    return True

def extrair_fragmento_especifico(sentenca, codigo_zona):
    """
    Extrai apenas o fragmento da sentença que se refere especificamente à zona
    """
    # Padrões para extrair fragmentos específicos
    padroes_fragmento = [
        rf'(na\s+{re.escape(codigo_zona)}\b[^;]*?)(?:[;]|$)',
        rf'(para\s+.*?{re.escape(codigo_zona)}\b[^;]*?)(?:[;]|$)',
        rf'({re.escape(codigo_zona)}\s+[^;]*?)(?:[;]|$)',
        rf'(inseridos?\s+na\s+{re.escape(codigo_zona)}\b[^;]*?)(?:[;]|$)',
        rf'(zona.*?{re.escape(codigo_zona)}\b[^;]*?)(?:[;]|$)'
    ]
    
    for padrao in padroes_fragmento:
        match = re.search(padrao, sentenca, re.IGNORECASE)
        if match:
            fragmento = match.group(1).strip()
            fragmento = re.sub(r'[,;]+$', '', fragmento)
            return fragmento
    
    return sentenca

def normalizar_texto(texto):
    """Normaliza texto para comparação (remove espaços extras, converte para minúsculo)"""
    texto_normalizado = re.sub(r'\s+', ' ', texto.strip().lower())
    # Remove números de lista/índice no início
    texto_normalizado = re.sub(r'^\d+\.\s*', '', texto_normalizado)
    # Remove asteriscos e formatação
    texto_normalizado = re.sub(r'\*+', '', texto_normalizado)
    return texto_normalizado

def dispositivos_sao_similares(disp1, disp2, threshold=0.85):
    """Verifica se dois dispositivos são similares (para remoção de duplicatas)"""
    norm1 = normalizar_texto(disp1)
    norm2 = normalizar_texto(disp2)
    
    # Se um texto contém o outro quase completamente
    if len(norm1) > len(norm2):
        maior, menor = norm1, norm2
    else:
        maior, menor = norm2, norm1
    
    # Calcula similaridade por sobreposição de palavras
    palavras_menor = set(menor.split())
    palavras_maior = set(maior.split())
    
    if len(palavras_menor) == 0:
        return False
    
    intersecao = len(palavras_menor.intersection(palavras_maior))
    similaridade = intersecao / len(palavras_menor)
    
    return similaridade >= threshold

def remover_duplicatas_similares(dispositivos_lista):
    """Remove dispositivos duplicados ou muito similares"""
    if not dispositivos_lista:
        return []
    
    dispositivos_unicos = []
    
    for dispositivo in dispositivos_lista:
        dispositivo_limpo = re.sub(r'\s+', ' ', dispositivo.strip())
        
        # Verifica se é muito curto ou inválido
        if len(dispositivo_limpo) < 20:
            continue
        
        # Verifica similaridade com dispositivos já adicionados
        eh_similar = False
        for existente in dispositivos_unicos:
            if dispositivos_sao_similares(dispositivo_limpo, existente):
                eh_similar = True
                break
        
        if not eh_similar:
            dispositivos_unicos.append(dispositivo_limpo)
    
    return dispositivos_unicos

def extrair_dispositivos_zona(codigo_zona):
    """Extrai dispositivos específicos da zona com remoção de duplicatas"""
    documento = carregar_legislacao()
    if not documento:
        return defaultdict(list)
        
    dispositivos = defaultdict(list)
    matcher = inicializar_matcher()
    
    print(f"🔍 Analisando {len(documento)} blocos de legislação...")
    
    for i, bloco in enumerate(documento):
        if i % 100 == 0 and i > 0:
            print(f"   Processados {i}/{len(documento)} blocos...")
            
        texto_completo = str(bloco)
        
        # Verifica se o bloco menciona a zona
        if not re.search(rf'\b{re.escape(codigo_zona)}\b', texto_completo, re.IGNORECASE):
            continue
        
        # Segmentação de sentenças
        if nlp:
            try:
                doc = nlp(texto_completo)
                sentencas = [sent.text.strip() for sent in doc.sents]
            except Exception as e:
                print(f"⚠️ Erro no processamento NLP: {e}")
                sentencas = re.split(r'(?<=[.!?])\s+', texto_completo)
        else:
            sentencas = re.split(r'(?<=[.!?])\s+', texto_completo)
        
        for sentenca in sentencas:
            sentenca = sentenca.strip()
            
            if not is_dispositivo_especifico_zona(sentenca, codigo_zona):
                continue
            
            fragmento = extrair_fragmento_especifico(sentenca, codigo_zona)
            
            # USA O MODELO TREINADO AQUI!
            categoria = categorizar_dispositivo_spacy(fragmento, matcher)
            
            # Extrai entidades se modelo treinado disponível
            if eh_modelo_treinado:
                entidades = extrair_entidades_treinadas(fragmento)
                if entidades:
                    print(f"🎯 Entidades encontradas: {list(entidades.keys())}")
            
            fragmento_limpo = limpar_sentenca_spacy(fragmento, codigo_zona)
            
            if fragmento_limpo and len(fragmento_limpo) > 15:
                dispositivos[categoria].append(fragmento_limpo)
    
    # Remove duplicatas de cada categoria
    dispositivos_limpos = defaultdict(list)
    for categoria, lista in dispositivos.items():
        dispositivos_limpos[categoria] = remover_duplicatas_similares(lista)
    
    return dispositivos_limpos

def categorizar_dispositivo_regex(texto):
    """Fallback para categorização com regex"""
    palavras_chave = {
        "uso_permitido": r"(uso permitido|permitido|autorizado|uso do solo|tipos de uso|atividades permitidas|hmv|hcsei|csei)",
        "altura_maxima": r"(altura máxima|limite vertical|altura edificação|gabarito|pavimentos|\d+\s*metros|\d+\s*m\b)",
        "densidade": r"(densidade|uh/ha|unidades por hectare|coeficiente de aproveitamento|CA|índice|\d+uh/ha)",
        "parcelamento": r"(área mínima|testada|lote mínimo|frente mínima|parcelamento|\d+,\d+\s*m²|\d+\s*m²)",
        "recuos": r"(recuo|afastamento|distância|divisa|facultativo)",
        "restricoes": r"(restrição|condição|observação|EIV|RIV|estudo|exigência|proibido|vedado|não permitido)"
    }
    
    texto_lower = texto.lower()
    
    for categoria, padrao in palavras_chave.items():
        if re.search(padrao, texto_lower):
            return categoria
    
    return "outros_dispositivos"

def limpar_sentenca_spacy(sentenca, codigo_zona):
    """Limpa sentença usando spaCy para melhor processamento"""
    if not nlp:
        return limpar_sentenca_regex(sentenca, codigo_zona)
    
    try:
        doc = nlp(sentenca)
        
        tokens_limpos = []
        for token in doc:
            if not token.is_space and not (token.is_punct and token.text in "()[]{}"):
                tokens_limpos.append(token.text)
        
        sentenca_limpa = " ".join(tokens_limpos)
        sentenca_limpa = re.sub(rf'\b{re.escape(codigo_zona)}\b', f'**{codigo_zona}**', 
                               sentenca_limpa, flags=re.IGNORECASE)
        
        return sentenca_limpa.strip()
    except Exception as e:
        print(f"⚠️ Erro na limpeza com spaCy: {e}")
        return limpar_sentenca_regex(sentenca, codigo_zona)

def limpar_sentenca_regex(sentenca, codigo_zona):
    """Fallback para limpeza com regex"""
    sentenca = re.sub(r'\s+', ' ', sentenca.strip())
    sentenca = re.sub(r'^[^\w]*', '', sentenca)
    sentenca = re.sub(rf'\b{re.escape(codigo_zona)}\b', f'**{codigo_zona}**', 
                     sentenca, flags=re.IGNORECASE)
    
    return sentenca

def formatar_dispositivo(dispositivo):
    """Formata um dispositivo individual para melhor legibilidade"""
    # Remove espaços extras
    dispositivo = re.sub(r'\s+', ' ', dispositivo.strip())
    
    # Destaca números e unidades de medida
    dispositivo = re.sub(r'(\d+)\s*(m²|m|ha|uh)', r'\1 \2', dispositivo)
    
    # Formata listas (I -, II -, etc.)
    dispositivo = re.sub(r'(^|\s)([IVXLCDM]+)\s*-\s*', r'\1\2. ', dispositivo)
    
    return dispositivo

def extrair_parametros_numericos(dispositivos):
    """Extrai parâmetros numéricos específicos dos dispositivos"""
    parametros = {
        "area_minima": None,
        "area_maxima": None,
        "testada_minima": None,
        "ca_minimo": None,
        "ca_maximo": None,
        "densidade_minima": None,
        "densidade_maxima": None,
        "altura_maxima": None
    }
    
    todas_sentencas = []
    for categoria_lista in dispositivos.values():
        todas_sentencas.extend(categoria_lista)
    
    texto_completo = " ".join(todas_sentencas)
    
    # Padrões para extração de valores numéricos
    padroes_numericos = {
        "area_minima": [
            r'área.*?mínima.*?(\d+(?:[,\.]\d+)?)\s*m²',
            r'(\d+(?:[,\.]\d+)?)\s*m².*?área.*?mínima',
            r'lote.*?mínimo.*?(\d+(?:[,\.]\d+)?)\s*m²'
        ],
        "area_maxima": [
            r'área.*?máxima.*?(\d+(?:[,\.]\d+)?(?:\.\d+)?)\s*m²',
            r'(\d+(?:[,\.]\d+)?)\s*m².*?área.*?máxima',
            r'e\s+(\d{4,}(?:[,\.]\d+)?)\s*m²',
            r'(\d+\.\d+,\d+)\s*m²'
        ],
        "testada_minima": [
            r'testada.*?mínima.*?(\d+(?:[,\.]\d+)?)\s*m',
            r'(\d+(?:[,\.]\d+)?)\s*m.*?testada.*?mínima',
            r'frente.*?mínima.*?(\d+(?:[,\.]\d+)?)\s*m'
        ],
        "densidade_minima": [
            r'(\d+)\s*uh\s*/\s*ha.*?(?:mínima|mínimo)',
            r'densidade.*?mínima.*?(\d+)\s*uh\s*/\s*ha',
            r'(\d+)\s*unidades.*?por.*?hectare.*?mínima'
        ],
        "densidade_maxima": [
            r'(\d+(?:\.\d+)?)\s*uh\s*/\s*ha.*?(?:máxima|máximo)',
            r'densidade.*?máxima.*?(\d+(?:\.\d+)?)\s*uh\s*/\s*ha',
            r'e\s+(\d+(?:\.\d+)?)\s*uh\s*/\s*ha',
            r'(\d+(?:\.\d+)?)\s*unidades.*?por.*?hectare.*?máxima'
        ],
        "altura_maxima": [
            r'altura.*?(?:máxima|limite).*?(\d+(?:[,\.]\d+)?)\s*m',
            r'(\d+(?:[,\.]\d+)?)\s*metros.*?altura',
            r'até.*?(\d+(?:[,\.]\d+)?)\s*m.*?altura',
            r'gabarito.*?(\d+(?:[,\.]\d+)?)\s*m'
        ],
        "ca_minimo": [
            r'CA.*?(?:mín|básico).*?(\d+(?:[,\.]\d+)?)',
            r'coeficiente.*?mínimo.*?(\d+(?:[,\.]\d+)?)'
        ],
        "ca_maximo": [
            r'CA.*?(?:máx|máximo).*?(\d+(?:[,\.]\d+)?)',
            r'coeficiente.*?máximo.*?(\d+(?:[,\.]\d+)?)'
        ]
    }
    
    # Processamento para cada parâmetro
    for param, padroes_lista in padroes_numericos.items():
        valores_encontrados = []
        
        for padrao in padroes_lista:
            matches = re.findall(padrao, texto_completo, re.IGNORECASE)
            for match in matches:
                try:
                    valor_limpo = match.replace('.', '').replace(',', '.')
                    if valor_limpo.count('.') > 1:
                        partes = valor_limpo.split('.')
                        if len(partes[-1]) <= 2:
                            valor_limpo = ''.join(partes[:-1]) + '.' + partes[-1]
                        else:
                            valor_limpo = ''.join(partes)
                    
                    valor_numerico = float(valor_limpo)
                    valores_encontrados.append(valor_numerico)
                except (ValueError, AttributeError):
                    continue
        
        if valores_encontrados:
            if 'minima' in param or 'minimo' in param:
                parametros[param] = min(valores_encontrados)
            elif 'maxima' in param or 'maximo' in param:
                parametros[param] = max(valores_encontrados)
            else:
                parametros[param] = valores_encontrados[0]
    
    return parametros

def formatar_resultado_melhorado(dispositivos, codigo_zona):
    """Gera resultado bem formatado e organizado - VERSÃO SEM DUPLICATAS"""
    zona_info = get_zona_info(codigo_zona)
    resultado = []
    
    # Cabeçalho elegante
    resultado.append(f"\n🏛️ LEGISLAÇÃO URBANA - {zona_info['nome']} ({codigo_zona})")
    resultado.append("=" * 70)
    resultado.append(f"📊 Densidade: {zona_info['densidade']} | Tipo: {zona_info['tipo']}")
    
    # Análise de complexidade
    total_dispositivos = sum(len(lista) for lista in dispositivos.values())
    if total_dispositivos > 0:
        resultado.append(f"🧠 Análise NLP: {total_dispositivos} dispositivos únicos identificados")
    
    # Extração de parâmetros numéricos
    parametros = extrair_parametros_numericos(dispositivos)
    
    # Seção de Parâmetros Principais
    if any(parametros.values()):
        resultado.append(f"\n📋 PARÂMETROS PRINCIPAIS:")
        resultado.append("-" * 40)
        
        if parametros["area_minima"]:
            resultado.append(f"• Área mínima do lote: {parametros['area_minima']:,.0f} m²")
        
        if parametros["area_maxima"] and parametros["area_maxima"] != parametros["area_minima"]:
            resultado.append(f"• Área máxima do lote: {parametros['area_maxima']:,.0f} m²")
        
        if parametros["testada_minima"]:
            resultado.append(f"• Testada mínima: {parametros['testada_minima']:g} metros")
        
        if parametros["ca_minimo"]:
            resultado.append(f"• Coeficiente de Aproveitamento mínimo: {parametros['ca_minimo']:g}")
        if parametros["ca_maximo"] and parametros["ca_maximo"] != parametros["ca_minimo"]:
            resultado.append(f"• Coeficiente de Aproveitamento máximo: {parametros['ca_maximo']:g}")
        
        # Densidade
        if parametros["densidade_minima"] or parametros["densidade_maxima"]:
            densidade_texto = "• Densidade habitacional: "
            if parametros["densidade_minima"] and parametros["densidade_maxima"]:
                if parametros["densidade_minima"] == parametros["densidade_maxima"]:
                    densidade_texto += f"{parametros['densidade_minima']:g} uh/ha"
                else:
                    densidade_texto += f"{parametros['densidade_minima']:g} uh/ha (mín.) a {parametros['densidade_maxima']:g} uh/ha (máx.)"
            elif parametros["densidade_minima"]:
                densidade_texto += f"{parametros['densidade_minima']:g} uh/ha (mín.)"
            else:
                densidade_texto += f"{parametros['densidade_maxima']:g} uh/ha (máx.)"
            resultado.append(densidade_texto)
        
        if parametros["altura_maxima"]:
            resultado.append(f"• Altura máxima: {parametros['altura_maxima']:g} metros")
    
    # Categorias organizadas por prioridade
    categorias_ordem = [
        ('uso_permitido', '✅ USOS PERMITIDOS'),
        ('parcelamento', '📐 PARCELAMENTO DO SOLO'),
        ('densidade', '📊 DENSIDADE E APROVEITAMENTO'),
        ('altura_maxima', '🏗️ ALTURA E GABARITO'),
        ('recuos', '↔️ RECUOS E AFASTAMENTOS'),
        ('restricoes', '⚠️ RESTRIÇÕES E CONDIÇÕES'),
        ('outros_dispositivos', '📋 OUTRAS DISPOSIÇÕES')
    ]
    
    dispositivos_exibidos = 0
    
    for categoria, titulo in categorias_ordem:
        if categoria not in dispositivos or not dispositivos[categoria]:
            continue
        
        resultado.append(f"\n{titulo}")
        resultado.append("-" * (len(titulo) - 4))
        
        # Remove duplicatas e limita a 8 itens por categoria
        itens_categoria = list(set(dispositivos[categoria]))[:8]
        
        for i, dispositivo in enumerate(itens_categoria, 1):
            dispositivo_formatado = dispositivo.strip()
            dispositivo_formatado = re.sub(r'\*{3,}', '**', dispositivo_formatado)
            
            if len(dispositivo_formatado) > 20:
                resultado.append(f"{i}. {dispositivo_formatado}")
                dispositivos_exibidos += 1  # Conta cada dispositivo exibido
        
        if len(dispositivos[categoria]) > 8:
            resultado.append(f"   💡 Mais {len(dispositivos[categoria])-8} dispositivos encontrados nesta categoria")
    
    # Rodapé informativo
    resultado.append(f"\n" + "=" * 70)
    resultado.append(f"📊 RESUMO: {dispositivos_exibidos} dispositivos exibidos para {codigo_zona} (de {total_dispositivos} únicos)")
    resultado.append(f"🧠 Processamento: Análise com remoção de duplicatas")
    resultado.append(f"💡 Resultados específicos para a zona consultada")
    resultado.append("=" * 70)
    
    return "\n".join(resultado)

def obter_coordenadas_cep(cep):
    """Geocodificação com Google API"""
    try:
        geolocator = GoogleV3(api_key=GOOGLE_API_KEY, timeout=10)
        location = geolocator.geocode(f"{cep}, Campinas, SP")
        if location:
            return (location.latitude, location.longitude, location.address)
        return None
    except Exception as e:
        print(f"⚠️ Erro na geocodificação: {e}")
        return None

def localizar_zona(lat, lon):
    """Consulta zona no MongoDB"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        collection = client['PI5']['coordenadas']
        ponto = {"type": "Point", "coordinates": [lon, lat]}
        resultado = collection.find_one({"geometry": {"$geoIntersects": {"$geometry": ponto}}})
        client.close()
        return resultado
    except Exception as e:
        print(f"⚠️ Erro ao consultar zona: {e}")
        return None

def validar_cep(cep):
    """Valida formato do CEP"""
    cep_limpo = re.sub(r'[^\d]', '', cep)
    
    if len(cep_limpo) != 8:
        return None
    
    return cep_limpo

def main():
    print("=" * 60)
    print("CONSULTA LEGISLAÇÃO URBANA - CAMPINAS/SP")
    print("🧠 Sistema Inteligente com Processamento NLP")
    print("=" * 60)
    
    cep_input = input("\nDigite o CEP (formato: 12345678 ou 12345-678): ").strip()
    
    try:
        cep = validar_cep(cep_input)
        if not cep:
            print("❌ CEP inválido. Use 8 dígitos (exemplo: 13000000).")
            return
        
        print("\n🔍 Localizando endereço...")
        coordenadas = obter_coordenadas_cep(cep)
        if not coordenadas:
            print("❌ Endereço não encontrado. Verifique o CEP informado.")
            return
        
        lat, lon, endereco = coordenadas
        endereco_simplificado = endereco.split(',')[0] if ',' in endereco else endereco
        print(f"📍 {endereco_simplificado}")
        
        print("🛰️ Identificando zona...")
        zona = localizar_zona(lat, lon)
        if not zona:
            print("❌ Zona não identificada. Verifique se o endereço está em Campinas/SP.")
            return
        
        codigo_zona = zona.get("properties", {}).get("duos", "INDEFINIDO")
        zona_info = get_zona_info(codigo_zona)
        
        print(f"✅ ZONA: {zona_info['nome']} ({codigo_zona})")
        print(f"\n📖 Analisando legislação específica para {codigo_zona}...")
        
        dispositivos = extrair_dispositivos_zona(codigo_zona)
        
        if not any(dispositivos.values()):
            print(f"⚠️ Nenhum dispositivo específico encontrado para a zona {codigo_zona}")
            print("💡 Isso pode indicar regulamentação genérica ou zona sem regras específicas.")
            return
            
        resultado = formatar_resultado_melhorado(dispositivos, codigo_zona)
        print(resultado)
        
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"⚠️ Erro inesperado: {str(e)}")
    
    print("\n✅ Consulta concluída com sucesso!")

if __name__ == "__main__":
    main()