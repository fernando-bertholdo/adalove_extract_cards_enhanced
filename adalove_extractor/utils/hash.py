"""
Utilitários para geração de hashes de integridade.
"""

import hashlib
from typing import Optional


def compute_hash(*fields: Optional[str]) -> str:
    """
    Gera um hash estável (SHA1) a partir de campos-chave do registro.
    
    Usado para detectar mudanças entre execuções e identificar duplicatas.
    
    Args:
        *fields: Campos a serem concatenados para o hash (geralmente titulo, data, professor)
        
    Returns:
        Hash SHA1 hexadecimal (40 caracteres)
        
    Example:
        >>> compute_hash("Workshop Python", "24/04/2025", "João Silva")
        "93fa506122e2fa6d..."
    """
    concatenated = "|".join([f or "" for f in fields])
    return hashlib.sha1(concatenated.encode("utf-8")).hexdigest()








