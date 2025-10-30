"""
Mapeamentos de tipos de cards baseados em ícones.

Este módulo contém os mapeamentos determinísticos para identificar
tipos de cards baseado nos ícones SVG presentes no modal.
"""

# Mapeamento canônico de ícones para tipos
ICON_TO_CARD_TYPE = {
    "book-open-reader-solido": "autoestudo",
    "user-group-solido": "encontro_orientacao",
    "chalkboard-user-solido": "encontro_instrucao",
    "square-code-solido": "projeto",
    "user-pen-solido": "avaliacao"
}

# Campos esperados por tipo de card
CARD_TYPE_FIELDS = {
    "autoestudo": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": True,
        "has_data_hora": False,
        "has_professor": True,
        "has_atividade_ponderada": False  # Pode ter, mas não é obrigatório
    },
    "encontro_orientacao": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": False
    },
    "encontro_instrucao": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": False
    },
    "projeto": {
        "has_assuntos_relacionados": False,
        "has_conteudos_relacionados": False,
        "has_data_hora": False,
        "has_professor": False,
        "has_atividade_ponderada": True  # SEMPRE tem
    },
    "avaliacao": {
        "has_assuntos_relacionados": False,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": True
    }
}

def get_card_type_from_icon(icon_id: str) -> str:
    """
    Retorna o tipo de card baseado no ID do ícone.
    
    Args:
        icon_id: ID do ícone SVG (ex: "book-open-reader-solido")
        
    Returns:
        Tipo do card ou "outros" se não reconhecido
    """
    return ICON_TO_CARD_TYPE.get(icon_id, "outros")

def get_expected_fields(card_type: str) -> dict:
    """
    Retorna os campos esperados para um tipo de card.
    
    Args:
        card_type: Tipo do card
        
    Returns:
        Dicionário com campos esperados
    """
    return CARD_TYPE_FIELDS.get(card_type, {})

def is_encontro_type(card_type: str) -> bool:
    """
    Verifica se o tipo de card é um encontro.
    
    Args:
        card_type: Tipo do card
        
    Returns:
        True se for encontro_orientacao ou encontro_instrucao
    """
    return card_type in ["encontro_orientacao", "encontro_instrucao"]

def should_extract_field(card_type: str, field_name: str) -> bool:
    """
    Verifica se um campo deve ser extraído para um tipo de card.
    
    Args:
        card_type: Tipo do card
        field_name: Nome do campo
        
    Returns:
        True se o campo deve ser extraído
    """
    expected_fields = get_expected_fields(card_type)
    return expected_fields.get(field_name, False)

