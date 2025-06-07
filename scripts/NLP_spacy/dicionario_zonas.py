dicionario_zonas = {
    # Zonas Residenciais
    "ZR": {"nome": "Zona Residencial", "tipo": "residencial", "hierarquia": 1},
    
    # Zonas Mistas
    "ZM1": {"nome": "Zona Mista 1", "tipo": "mista", "densidade": "baixa", "hierarquia": 2},
    "ZM2": {"nome": "Zona Mista 2", "tipo": "mista", "densidade": "média", "hierarquia": 2},
    "ZM3": {"nome": "Zona Mista 3", "tipo": "mista", "densidade": "alta", "hierarquia": 2},
    
    # Zonas Centrais
    "ZC1": {"nome": "Zona Central 1", "tipo": "central", "hierarquia": 3},
    "ZC2": {"nome": "Zona Central 2", "tipo": "central", "hierarquia": 3},
    "ZC4": {"nome": "Zona Central 4", "tipo": "central", "hierarquia": 3},
    
    # Zonas Econômicas
    "ZAE-A": {"nome": "Zona de Atividades Econômicas A", "tipo": "econômica", "intensidade": "leve"},
    "ZAE-B": {"nome": "Zona de Atividades Econômicas B", "tipo": "econômica", "intensidade": "pesada"},
    
    # Zonas Especiais
    "ZIS": {"nome": "Zona de Interesse Social", "tipo": "especial", "caracteristica": "social"},
    "ZEIS": {"nome": "Zona Especial de Interesse Social", "tipo": "especial", "caracteristica": "social"},
    
    # Padrão para zonas não mapeadas
    "DEFAULT": {"nome": "Zona não catalogada", "tipo": "indefinida"}
}

# Função de acesso seguro
def get_zona_info(codigo):
    return dicionario_zonas.get(codigo, dicionario_zonas["DEFAULT"])

# Exemplo de uso:
# nome_zona = get_zona_info("ZC4")["nome"]
# tipo_zona = get_zona_info("ZC4")["tipo"]