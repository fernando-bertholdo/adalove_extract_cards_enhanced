"""
Utilitários para manipulação e comparação de texto.
"""

import re


def normalize_title(title: str) -> str:
    """
    Normaliza títulos para comparação, removendo ruído e padronizando formato.
    
    Remove:
    - Prefixos como "Autoestudo", "Instrução", "Workshop"
    - Números após "autoestudo"
    - Pontuação e caracteres especiais
    - Espaços múltiplos
    
    Args:
        title: Título a ser normalizado
        
    Returns:
        Título normalizado (lowercase, apenas palavras-chave)
        
    Example:
        >>> normalize_title("Autoestudo 1 - Python Básico!")
        "python basico"
    """
    if not title:
        return ""
    
    # Converte para lowercase
    normalized = title.lower()
    
    # Remove prefixos comuns
    normalized = re.sub(r"autoestudo\s*\d*", "", normalized)
    normalized = re.sub(
        r"instru[cç][aã]o|encontro|workshop|sprint|review|retrospective", 
        "", 
        normalized
    )
    
    # Remove pontuação mantendo acentos
    normalized = re.sub(r"[^a-z0-9áâãàéêíóôõúç\s]", " ", normalized)
    
    # Remove espaços múltiplos
    normalized = re.sub(r"\s+", " ", normalized).strip()
    
    return normalized


def title_similarity(title_a: str, title_b: str) -> float:
    """
    Calcula similaridade entre dois títulos usando Jaccard similarity de tokens.
    
    Retorna um valor entre 0.0 (totalmente diferente) e 1.0 (idêntico).
    
    Args:
        title_a: Primeiro título
        title_b: Segundo título
        
    Returns:
        Score de similaridade (0.0 a 1.0)
        
    Example:
        >>> title_similarity("Autoestudo Python", "Workshop Python")
        0.5  # Compartilham "python"
    """
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)
    
    if not norm_a or not norm_b:
        return 0.0
    
    # Jaccard similarity de tokens
    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())
    
    if not tokens_a or not tokens_b:
        return 0.0
    
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    
    return intersection / union if union > 0 else 0.0








