"""
Módulo de automação de navegador com Playwright.
"""

from .auth import login_adalove
from .navigator import navigate_to_academic_life, discover_weeks, close_modal_if_open

__all__ = [
    "login_adalove",
    "navigate_to_academic_life", 
    "discover_weeks",
    "close_modal_if_open"
]








