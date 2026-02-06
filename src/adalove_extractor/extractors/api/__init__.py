"""
Módulo de extração via API do AdaLove.

Fornece funções para extrair dados de seções e atividades
usando requisições HTTP diretas à API REST.
"""

from .section import extract_available_sections, extract_sections_and_weeks
from .activity import extract_activities_from_section

__all__ = [
    "extract_available_sections",
    "extract_sections_and_weeks",
    "extract_activities_from_section",
]
