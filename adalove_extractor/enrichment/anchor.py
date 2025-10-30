"""
Sistema de ancoragem de autoestudos às instruções correspondentes.

Usa algoritmo de pontuação multi-fator:
- Professor (+3.0 pontos)
- Data (+3.0 pontos)
- Similaridade de título (+2.0 × similaridade)
- Proximidade posicional (+1.5 - 0.1 × distância)

NOTA: Migrado para usar nova taxonomia (card_type) ao invés de campos legados.
"""

from typing import Optional, Tuple, Dict
from ..utils.text import title_similarity


class AnchorEngine:
    """
    Motor de ancoragem de autoestudos às instruções.
    
    Responsável por encontrar a melhor instrução relacionada a cada autoestudo
    usando pontuação multi-fator.
    """
    
    def __init__(self, previous_anchors: Optional[Dict[str, Tuple[str, str]]] = None):
        """
        Inicializa o motor de ancoragem.
        
        Args:
            previous_anchors: Mapa de ancoragens anteriores {card_id: (parent_id, parent_title)}
                             para preservar ancoragens já estabelecidas
        """
        self.previous_anchors = previous_anchors or {}
    
    def anchor_autoestudos(self, cards: list[dict], logger) -> list[dict]:
        """
        Ancora autoestudos às suas instruções correspondentes por semana.
        
        Args:
            cards: Lista de dicionários com dados dos cards
            logger: Logger para registrar processo
            
        Returns:
            Lista de cards com campos de ancoragem preenchidos
        """
        # Agrupa cards por semana
        weeks = {}
        for card in cards:
            week_num = card.get("semana_num") or -1
            weeks.setdefault(week_num, []).append(card)
        
        # Processa cada semana independentemente
        for week_num, week_cards in weeks.items():
            # Ordena por índice e título
            week_cards.sort(key=lambda c: (int(c.get("indice") or 0), c.get("titulo") or ""))
            
            # Identifica instruções da semana (encontros de orientação e instrução)
            instructions = [c for c in week_cards if c.get("card_type") in ["encontro_orientacao", "encontro_instrucao"]]
            
            # Ancora cada autoestudo/atividade ponderada
            for card in week_cards:
                if card.get("card_type") not in ["autoestudo", "projeto"] and not card.get("is_avaliativo"):
                    continue
                
                # Preserva ancoragem anterior se existir
                if card.get("id") in self.previous_anchors:
                    parent_id, parent_title = self.previous_anchors[card["id"]]
                    card["parent_instruction_id"] = parent_id
                    card["parent_instruction_title"] = parent_title
                    card["anchor_method"] = "preserved_previous"
                    card["anchor_confidence"] = "locked"
                    continue
                
                # Encontra melhor instrução
                best_match = self._find_best_instruction(card, instructions)
                
                if best_match:
                    instruction, score, method, confidence = best_match
                    card["parent_instruction_id"] = instruction.get("id")
                    card["parent_instruction_title"] = instruction.get("titulo")
                    card["anchor_method"] = method
                    card["anchor_confidence"] = confidence
        
        return cards
    
    def _find_best_instruction(
        self, 
        card: dict, 
        instructions: list[dict]
    ) -> Optional[Tuple[dict, float, str, str]]:
        """
        Encontra a melhor instrução para ancorar um autoestudo.
        
        Args:
            card: Card de autoestudo/atividade
            instructions: Lista de instruções candidatas
            
        Returns:
            Tupla (instrução, score, método, confiança) ou None
        """
        if not instructions:
            return None
        
        best_score = -1e9
        best_instruction = None
        best_method = ""
        best_confidence = "low"
        
        for instruction in instructions:
            score, method, confidence = self._calculate_anchor_score(card, instruction)
            
            if score > best_score:
                best_score = score
                best_instruction = instruction
                best_method = method
                best_confidence = confidence
        
        if best_instruction:
            return best_instruction, best_score, best_method, best_confidence
        
        return None
    
    def _calculate_anchor_score(
        self, 
        card: dict, 
        instruction: dict
    ) -> Tuple[float, str, str]:
        """
        Calcula score de ancoragem entre um card e uma instrução.
        
        Fatores de pontuação:
        - Professor: +3.0 se match exato
        - Data: +3.0 se mesma data
        - Similaridade de título: +2.0 × similaridade
        - Proximidade posicional: +1.5 - 0.1 × distância (se card vem depois)
        
        Args:
            card: Card de autoestudo/atividade
            instruction: Card de instrução candidata
            
        Returns:
            Tupla (score, método_string, confiança)
        """
        score = 0.0
        method_parts = []
        confidence = "low"
        
        # Fator 1: Professor (+3.0)
        if (card.get("professor") and instruction.get("professor") and 
            card["professor"].lower() == instruction["professor"].lower()):
            score += 3.0
            method_parts.append("professor")
            confidence = "high"
        
        # Fator 2: Data (+3.0)
        if (card.get("data_ddmmaaaa") and instruction.get("data_ddmmaaaa") and
            card["data_ddmmaaaa"] == instruction["data_ddmmaaaa"]):
            score += 3.0
            method_parts.append("same_date")
            confidence = "high"
        
        # Fator 3: Similaridade de título (+2.0 × sim)
        similarity = title_similarity(
            card.get("titulo") or "", 
            instruction.get("titulo") or ""
        )
        score += 2.0 * similarity
        method_parts.append(f"sim={similarity:.2f}")
        
        if similarity >= 0.5 and confidence != "high":
            confidence = "medium"
        
        # Fator 4: Proximidade posicional (+1.5 - 0.1 × delta)
        card_index = int(card.get("indice") or 0)
        instr_index = int(instruction.get("indice") or 0)
        delta = card_index - instr_index
        
        if delta >= 0:  # Card vem depois da instrução
            proximity_score = max(0.0, 1.5 - 0.1 * delta)
            score += proximity_score
            method_parts.append(f"prev_prox={proximity_score:.2f}")
            
            if confidence == "low":
                confidence = "medium"
        else:  # Card vem antes (penaliza levemente)
            score -= 0.2
            method_parts.append("after=-0.2")
        
        method_string = ",".join(method_parts)
        
        return score, method_string, confidence








