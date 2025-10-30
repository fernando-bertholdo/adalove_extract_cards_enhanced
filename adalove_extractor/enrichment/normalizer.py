"""
Normalizações de dados (datas, URLs, etc.) e funções auxiliares de parsing.

Consolidado com funções anteriormente em classifier.py para reduzir
complexidade de módulos e melhorar coesão.
"""

import re
from datetime import datetime
from typing import Optional, Tuple


# Regex para detecção de data/hora no formato brasileiro
DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})h?", re.IGNORECASE)

# Regex para URLs válidas
HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)

# Regex para detecção de nome completo
NAME_CANDIDATE_RE = re.compile(
    r"^[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+"
    r"(\s+[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+){1,}$"
)


def extract_date_time(
    text: str, 
    tz_offset: str = "-03:00"
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extrai data e hora de um texto e retorna em múltiplos formatos.
    
    Procura padrão "dd/mm/aaaa - HH:MM" no texto.
    
    Args:
        text: Texto onde procurar (título, descrição, corpo)
        tz_offset: Fuso horário para o formato ISO (padrão: Brasília)
        
    Returns:
        Tupla (iso_datetime, data_ddmmaaaa, hora_hhmm) ou (None, None, None)
        
    Example:
        >>> extract_date_time("Encontro dia 24/04/2025 - 14:00")
        ("2025-04-24T14:00:00-03:00", "24/04/2025", "14:00")
    """
    if not text:
        return None, None, None
        
    match = DATE_RE.search(text)
    if not match:
        return None, None, None
        
    date_str = match.group(1)  # dd/mm/aaaa
    time_str = match.group(2)  # HH:MM
    
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        iso = dt.strftime("%Y-%m-%dT%H:%M:00") + tz_offset
        return iso, date_str, time_str
    except Exception:
        return None, None, None


def parse_week_number(week_name: str) -> Optional[int]:
    """
    Extrai número da semana de um nome como "Semana 01" ou "Semana 10".
    
    Args:
        week_name: Nome da semana
        
    Returns:
        Número da semana (int) ou None se não encontrar
        
    Example:
        >>> parse_week_number("Semana 07")
        7
    """
    week_re = re.compile(r"Semana\s*(\d+)", re.IGNORECASE)
    match = week_re.search(week_name or "")
    return int(match.group(1)) if match else None


def calculate_sprint(week_num: Optional[int]) -> Optional[int]:
    """
    Calcula número do sprint a partir da semana.
    
    Sprint = ceil(week_num / 2)
    - Semanas 1-2 = Sprint 1
    - Semanas 3-4 = Sprint 2
    - etc.
    
    Args:
        week_num: Número da semana
        
    Returns:
        Número do sprint ou None
        
    Example:
        >>> calculate_sprint(7)
        4  # Semana 7 = Sprint 4
    """
    if week_num is None:
        return None
    return -(-week_num // 2)  # ceil division


def normalize_urls_pipe(raw_urls: str) -> list[str]:
    """
    Normaliza lista de URLs em formato pipe-separated.
    
    Remove:
    - Texto descritivo antes do URL ("Material: ", "Link: ")
    - URLs inválidas (não http/https)
    - Duplicatas (preservando ordem)
    
    Args:
        raw_urls: String com URLs separadas por " | "
        
    Returns:
        Lista de URLs normalizadas
        
    Example:
        >>> normalize_urls_pipe("Material: https://example.com | Link: https://test.com")
        ["https://example.com", "https://test.com"]
    """
    if not raw_urls:
        return []
        
    urls = []
    for part in [x.strip() for x in raw_urls.split("|") if x.strip()]:
        # Remove prefixo descritivo se houver
        if ":" in part:
            part = part.split(":", 1)[1].strip()
            
        # Valida se é URL http/https
        if HTTP_RE.match(part):
            urls.append(part)
    
    # Remove duplicatas preservando ordem
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            
    return unique_urls


def extract_data_hora_components(data_hora: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrai componentes de data e hora de uma string.
    
    Args:
        data_hora: String no formato "DD/MM/AAAA - HH:MM"
        
    Returns:
        Tupla: (data, hora) ou (None, None) se não encontrar
        
    Example:
        >>> extract_data_hora_components("15/10/2025 - 14:30")
        ("15/10/2025", "14:30")
    """
    if not data_hora:
        return None, None
        
    match = DATE_RE.search(data_hora)
    if match:
        return match.group(1), match.group(2)
    
    return None, None


def is_sincrono(data_hora: Optional[str]) -> bool:
    """
    Determina se um card é síncrono baseado na presença de data/hora.
    
    Args:
        data_hora: String de data/hora ou None
        
    Returns:
        True se tem data/hora (é síncrono)
    """
    return bool(data_hora)


def detect_known_names(cards_data: list[dict]) -> list[str]:
    """
    Detecta nomes que aparecem com frequência nos cards.
    
    Usado para melhorar detecção de professor (reduz falsos positivos).
    
    Args:
        cards_data: Lista de dicionários com dados dos cards
        
    Returns:
        Lista de nomes que aparecem em ≥2 cards
        
    Example:
        >>> cards = [{"texto_completo": "...João Silva"}, {"texto_completo": "...João Silva"}]
        >>> detect_known_names(cards)
        ["João Silva"]
    """
    name_counter = {}
    
    for card in cards_data:
        text = card.get("texto_completo") or ""
        
        for line in text.splitlines():
            line = line.strip()
            
            # Valida se parece um nome completo
            if NAME_CANDIDATE_RE.match(line):
                name_counter[line] = name_counter.get(line, 0) + 1
    
    # Retorna nomes que aparecem em pelo menos 2 cards
    return [name for name, count in name_counter.items() if count >= 2]








