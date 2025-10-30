"""
Utilitários gerais do sistema de extração.
"""

from .hash import compute_hash
from .text import normalize_title, title_similarity

__all__ = ["compute_hash", "normalize_title", "title_similarity"]








