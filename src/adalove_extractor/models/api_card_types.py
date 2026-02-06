"""
Mapeamento de tipos de cards da API para nomes legíveis.

Este módulo contém o mapeamento determinístico dos IDs numéricos
de tipo de atividade retornados pela API para nomes legíveis.
"""

# Mapeamento de type (int) para nome interno
API_TYPE_TO_NAME = {
    1: "encontro_orientacao",
    2: "encontro_instrucao",
    11: "autoestudo",
    21: "projeto",
    31: "avaliacao"
}

# Mapeamento de type (int) para nome em português
API_TYPE_TO_PORTUGUESE = {
    1: "Encontro de Orientação",
    2: "Encontro de Instrução",
    11: "Autoestudo",
    21: "Desenvolvimento de Projetos",
    31: "Avaliação e Pesquisa"
}

# Características por tipo
API_TYPE_CHARACTERISTICS = {
    1: {  # Encontro de Orientação
        "has_date": True,
        "has_professor": False,
        "has_related_content": False,
        "has_grade_weight": True,
    },
    2: {  # Encontro de Instrução
        "has_date": True,
        "has_professor": True,
        "has_related_content": False,
        "has_grade_weight": False,
    },
    11: {  # Autoestudo
        "has_date": False,
        "has_professor": True,
        "has_related_content": True,
        "has_grade_weight": False,
        "has_basic_activity_url": True,
    },
    21: {  # Projeto
        "has_date": False,
        "has_professor": False,
        "has_related_content": False,
        "has_grade_weight": True,
    },
    31: {  # Avaliação
        "has_date": False,
        "has_professor": False,
        "has_related_content": False,
        "has_grade_weight": False,
    }
}


def get_type_name(api_type: int) -> str:
    """
    Retorna o nome interno do tipo de card.
    
    Args:
        api_type: ID numérico do tipo (1, 2, 11, 21, 31)
        
    Returns:
        Nome interno do tipo ou "outros" se não reconhecido
    """
    return API_TYPE_TO_NAME.get(api_type, "outros")


def get_type_portuguese(api_type: int) -> str:
    """
    Retorna o nome em português do tipo de card.
    
    Args:
        api_type: ID numérico do tipo
        
    Returns:
        Nome em português do tipo
    """
    return API_TYPE_TO_PORTUGUESE.get(api_type, "Outro")


def get_type_characteristics(api_type: int) -> dict:
    """
    Retorna as características esperadas para um tipo de card.
    
    Args:
        api_type: ID numérico do tipo
        
    Returns:
        Dicionário com características do tipo
    """
    return API_TYPE_CHARACTERISTICS.get(api_type, {})


def should_fetch_details(api_type: int) -> bool:
    """
    Determina se um tipo de atividade precisa de fetch de detalhes adicionais.
    
    Autoestudos (type=11) geralmente têm conteúdos relacionados e links,
    então são candidatos para buscar dados adicionais.
    
    Args:
        api_type: ID numérico do tipo
        
    Returns:
        True se deve buscar detalhes adicionais
    """
    chars = get_type_characteristics(api_type)
    return chars.get("has_related_content", False)
