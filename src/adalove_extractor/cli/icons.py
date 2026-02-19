#!/usr/bin/env python3
"""
Sistema de ícones adaptativo para CLI.
Detecta terminal capabilities e usa NerdFonts quando disponível.
"""

import os
import sys
from dataclasses import dataclass
from typing import Literal

IconSet = Literal["nerd", "emoji"]


@dataclass
class Icons:
    """Classe de ícones com suporte a NerdFonts e emoji fallback."""
    
    # Status
    check: str
    uncheck: str
    warning: str
    error: str
    success: str
    
    # Files & Folders
    folder: str
    file_edit: str
    file_empty: str
    document: str
    
    # Actions
    download: str
    view: str
    exit: str
    back: str
    
    # Status indicators
    status_ok: str
    status_warning: str
    status_error: str
    status_none: str
    
    # Educational
    calendar: str
    teacher: str
    weight: str
    question: str
    clipboard: str
    
    # Branding
    rocket: str
    robot: str


# NerdFonts icon set (requires Nerd Font in terminal)
NERD_ICONS = Icons(
    # Status
    check="\uf14a",      # nf-fa-check_square
    uncheck="\uf096",    # nf-fa-square_o
    warning="\uf071",    # nf-fa-warning
    error="\uf057",      # nf-fa-times_circle
    success="\uf058",    # nf-fa-check_circle
    
    # Files & Folders
    folder="\uf07b",     # nf-fa-folder
    file_edit="\uf0f6",  # nf-fa-file_text_o
    file_empty="\uf016", # nf-fa-file_o
    document="\uf0f6",   # nf-fa-file_text
    
    # Actions
    download="\uf019",   # nf-fa-download
    view="\uf06e",       # nf-fa-eye
    exit="\uf08b",       # nf-fa-sign_out
    back="\uf060",       # nf-fa-arrow_left
    
    # Status indicators
    status_ok="\uf111",     # nf-fa-circle (green)
    status_warning="\uf111", # nf-fa-circle (yellow)
    status_error="\uf111",   # nf-fa-circle (red)
    status_none="\uf10c",    # nf-fa-circle_o
    
    # Educational
    calendar="\uf073",   # nf-fa-calendar
    teacher="\uf19d",    # nf-fa-graduation_cap
    weight="\uf24e",     # nf-fa-balance_scale
    question="\uf059",   # nf-fa-question_circle
    clipboard="\uf0ea",  # nf-fa-clipboard
    
    # Branding
    rocket="\uf135",     # nf-fa-rocket
    robot="\uf17b",      # nf-fa-android
)


# Emoji fallback (works everywhere)
EMOJI_ICONS = Icons(
    # Status
    check="✅",
    uncheck="⬜",
    warning="⚠️",
    error="❌",
    success="✅",
    
    # Files & Folders
    folder="📁",
    file_edit="📝",
    file_empty="📭",
    document="📄",
    
    # Actions
    download="📥",
    view="👁️",
    exit="❌",
    back="←",
    
    # Status indicators
    status_ok="🟢",
    status_warning="🟡",
    status_error="🔴",
    status_none="⚪",
    
    # Educational
    calendar="📅",
    teacher="👨‍🏫",
    weight="⚖️",
    question="❓",
    clipboard="📋",
    
    # Branding
    rocket="🚀",
    robot="🤖",
)


def detect_nerd_font_support() -> bool:
    """
    Detecta se o terminal suporta NerdFonts.
    
    Verifica:
    - TERM_PROGRAM (iTerm2, WezTerm, etc.)
    - WT_SESSION (Windows Terminal)
    - POWERLINE_FONT env var
    - LC_TERMINAL (Apple Terminal com Powerlevel10k)
    
    IMPORTANTE: VSCode terminal não renderiza NerdFont Unicode corretamente,
    mesmo com Powerlevel10k configurado. Usa emojis para VSCode.
    """
    # VSCode terminal: sempre usa emojis (não renderiza \ufXXX corretamente)
    term_program = os.getenv("TERM_PROGRAM", "").lower()
    if "vscode" in term_program:
        return False
    
    # Windows Terminal
    if os.getenv("WT_SESSION"):
        return True
    
    # iTerm2, WezTerm, Alacritty, Kitty
    if term_program in ("iterm.app", "wezterm", "alacritty", "kitty"):
        return True
    
    # Explicit powerline/nerd font indicator
    if os.getenv("POWERLINE_FONT") or os.getenv("NERD_FONT"):
        return True
    
    # Powerlevel10k (but not in VSCode, checked above)
    if os.getenv("POWERLEVEL9K_MODE") or os.getenv("P9K_SSH"):
        return True
    
    # Check for common Nerd Font terminal emulators on macOS
    lc_term = os.getenv("LC_TERMINAL", "").lower()
    if lc_term and "iterm" in lc_term:
        return True
    
    # Default to emoji for safety
    return False


def get_icons() -> Icons:
    """Retorna o set de ícones apropriado para o terminal atual."""
    if detect_nerd_font_support():
        return NERD_ICONS
    return EMOJI_ICONS


# Global icon instance
icons = get_icons()
