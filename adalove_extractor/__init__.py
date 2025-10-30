"""
Adalove Extract Cards Enhanced

Sistema modular de extração automatizada de cards educacionais da plataforma AdaLove
com enriquecimento inteligente de dados.
"""

__version__ = "3.0.0"
__author__ = "Fernando Bertholdo"

from .models.card import Card
from .models.enriched_card import EnrichedCard

__all__ = ["Card", "EnrichedCard", "__version__"]








