"""
Sistema de ancoragem de autoestudos às instruções para extração via API.

Usa algoritmo de pontuação multi-fator:
- Professor (+3.0 pontos)
- Proximidade de sort (+1.5 - 0.1 × delta)
- Similaridade de título (+2.0 × similaridade)
"""

from typing import Optional, Tuple, List, Dict, Any
from difflib import SequenceMatcher


def title_similarity(title1: str, title2: str) -> float:
    """
    Calcula similaridade entre dois títulos.
    
    Args:
        title1: Primeiro título
        title2: Segundo título
        
    Returns:
        Score de similaridade entre 0 e 1
    """
    if not title1 or not title2:
        return 0.0
    
    # Normaliza: lowercase e remove caracteres especiais
    t1 = title1.lower().strip()
    t2 = title2.lower().strip()
    
    return SequenceMatcher(None, t1, t2).ratio()


def calculate_anchor_score(
    card: Dict[str, Any], 
    encontro: Dict[str, Any]
) -> Tuple[float, str, str]:
    """
    Calcula score de ancoragem entre um card e um encontro.
    
    Fatores de pontuação:
    - Professor: +3.0 se match exato
    - Proximidade de sort: +1.5 - 0.1 × delta (se card vem depois)
    - Similaridade de título: +2.0 × similaridade
    
    Args:
        card: Card de autoestudo/atividade
        encontro: Card de encontro candidato
        
    Returns:
        Tupla (score, método_string, confiança)
    """
    score = 0.0
    method_parts = []
    confidence = "low"
    
    # Fator 1: Professor (+3.0)
    card_prof = (card.get("professor") or "").lower().strip()
    encontro_prof = (encontro.get("professor") or "").lower().strip()
    
    if card_prof and encontro_prof and card_prof == encontro_prof:
        score += 3.0
        method_parts.append("professor")
        confidence = "high"
    
    # Fator 2: Proximidade de sort (+1.5 - 0.1 × delta)
    card_sort = card.get("sort", 999)
    encontro_sort = encontro.get("sort", 0)
    delta = card_sort - encontro_sort
    
    if delta > 0:  # Card vem depois do encontro
        proximity_score = max(0.0, 1.5 - 0.1 * delta)
        score += proximity_score
        method_parts.append(f"sort_prox={proximity_score:.2f}")
        
        if confidence == "low":
            confidence = "medium"
    else:  # Card vem antes (penaliza)
        score -= 0.5
        method_parts.append("before=-0.5")
    
    # Fator 3: Similaridade de título (+2.0 × sim)
    similarity = title_similarity(
        card.get("titulo", ""), 
        encontro.get("titulo", "")
    )
    score += 2.0 * similarity
    method_parts.append(f"sim={similarity:.2f}")
    
    if similarity >= 0.4 and confidence != "high":
        confidence = "medium"
    
    method_string = ",".join(method_parts)
    
    return score, method_string, confidence


def find_best_encontro(
    card: Dict[str, Any], 
    encontros: List[Dict[str, Any]]
) -> Optional[Tuple[Dict[str, Any], float, str, str]]:
    """
    Encontra o melhor encontro para ancorar um autoestudo.
    
    Args:
        card: Card de autoestudo/atividade
        encontros: Lista de encontros candidatos
        
    Returns:
        Tupla (encontro, score, método, confiança) ou None
    """
    if not encontros:
        return None
    
    best_score = -1e9
    best_encontro = None
    best_method = ""
    best_confidence = "low"
    
    for encontro in encontros:
        score, method, confidence = calculate_anchor_score(card, encontro)
        
        if score > best_score:
            best_score = score
            best_encontro = encontro
            best_method = method
            best_confidence = confidence
    
    if best_encontro and best_score > 0:
        return best_encontro, best_score, best_method, best_confidence
    
    return None


def anchor_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ancora autoestudos/projetos aos encontros correspondentes.
    
    Args:
        cards: Lista de cards ordenados por sort
        
    Returns:
        Lista de cards com campos de ancoragem preenchidos
    """
    # Identifica encontros (type 1=orientação, 2=instrução)
    encontros = [
        c for c in cards 
        if c.get("card_type") in ["encontro_orientacao", "encontro_instrucao"]
    ]
    
    # Ancora cada autoestudo/projeto
    for card in cards:
        card_type = card.get("card_type", "")
        is_ponderada = card.get("is_ponderada", False)
        
        # Só ancora autoestudos, projetos e ponderadas
        if card_type not in ["autoestudo", "projeto", "avaliacao"] and not is_ponderada:
            continue
        
        # Encontra melhor encontro
        result = find_best_encontro(card, encontros)
        
        if result:
            encontro, score, method, confidence = result
            card["ancora_encontro_titulo"] = encontro.get("titulo")
            card["ancora_encontro_sort"] = encontro.get("sort")
            card["ancora_metodo"] = method
            card["ancora_confianca"] = confidence
            card["ancora_score"] = round(score, 2)
    
    return cards


def organize_by_encontros(cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Organiza cards agrupando autoestudos sob seus encontros.
    Usa data como chave do objeto encontro e título como chave do autoestudo.
    
    Estrutura de saída:
    {
        "encontros": {
            "2026-03-26": {
                "dia_semana": "Quinta-feira",
                "titulo": "Métricas de Código...",
                "tipo": "encontro_instrucao",
                "professor": "Fernando",
                "autoestudos": {
                    "Teoria 1: Teste de software": {
                        "descricao": "...",
                        "professor": "...",
                        ...
                    }
                }
            }
        },
        "sem_ancora": [...]
    }
    """
    from datetime import datetime
    from collections import OrderedDict
    
    # Mapa de dias da semana em português
    DIAS_SEMANA = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    
    def parse_date(date_str):
        """Extrai data (sem horário) e dia da semana."""
        if not date_str:
            return "sem_data", None, "9999-99-99"
        try:
            # Formato: "2026-03-26T07:00:00.000Z"
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            data_apenas = dt.strftime("%Y-%m-%d")
            dia_semana = DIAS_SEMANA.get(dt.weekday(), "")
            return data_apenas, dia_semana, data_apenas
        except:
            return "sem_data", None, "9999-99-99"
    
    # Primeiro, ordena por sort para ancoragem correta
    cards_ordenados = sorted(cards, key=lambda c: c.get("sort", 999))
    
    # Ancora todos
    cards_ancorados = anchor_cards(cards_ordenados)
    
    # Separa encontros e outros
    encontros_temp = []  # Lista temporária para ordenação
    autoestudos_por_encontro = {}
    sem_ancora = []
    
    for card in cards_ancorados:
        card_type = card.get("card_type", "")
        
        if card_type in ["encontro_orientacao", "encontro_instrucao"]:
            data_apenas, dia_semana, sort_key = parse_date(card.get("data_hora"))
            
            encontro_entry = {
                "_data": data_apenas,  # Para usar como chave
                "_sort_key": sort_key,  # Para ordenação
                "_sort": card.get("sort"),  # Para referência de ancoragem
                "dia_semana": dia_semana,
                "titulo": card.get("titulo"),
                "tipo": card_type,
                "professor": card.get("professor"),
                "assuntos_relacionados": card.get("assuntos_relacionados", []),
                "conteudos_relacionados": card.get("conteudos_relacionados", []),
                "is_ponderada": card.get("is_ponderada", False),
                "autoestudos": {}  # Agora é um dicionário com título como chave
            }
            encontros_temp.append(encontro_entry)
            autoestudos_por_encontro[card.get("sort")] = encontro_entry
        else:
            # Tenta adicionar ao encontro ancorado
            ancora_sort = card.get("ancora_encontro_sort")
            if ancora_sort and ancora_sort in autoestudos_por_encontro:
                titulo_autoestudo = card.get("titulo", "Sem título")
                autoestudos_por_encontro[ancora_sort]["autoestudos"][titulo_autoestudo] = {
                    "descricao": card.get("descricao"),
                    "professor": card.get("professor"),
                    "conteudos_relacionados": card.get("conteudos_relacionados", []),
                    "assuntos_relacionados": card.get("assuntos_relacionados", []),
                    "is_ponderada": card.get("is_ponderada", False),
                    "ancora_metodo": card.get("ancora_metodo"),
                    "ancora_confianca": card.get("ancora_confianca")
                }
            else:
                sem_ancora.append(card)
    
    # Ordena encontros por DATA
    encontros_temp.sort(key=lambda e: e.get("_sort_key", "9999-99-99"))
    
    # Converte lista para dicionário ordenado com data como chave
    encontros_dict = OrderedDict()
    for encontro in encontros_temp:
        data_key = encontro.pop("_data")
        encontro.pop("_sort_key", None)
        encontro.pop("_sort", None)
        encontros_dict[data_key] = encontro
    
    return {
        "encontros": dict(encontros_dict),
        "sem_ancora": sem_ancora
    }


