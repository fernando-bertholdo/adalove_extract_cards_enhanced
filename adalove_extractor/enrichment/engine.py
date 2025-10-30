"""
Motor principal de enriquecimento de dados.

Orquestra todos os processos de enriquecimento:
- Normalização temporal
- Detecção de professor
- Classificação
- Ancoragem
- Normalização de URLs
- Geração de hash
"""

from typing import Optional, Dict, Tuple
import logging

from .normalizer import (
    extract_date_time,
    parse_week_number,
    calculate_sprint,
    normalize_urls_pipe,
    extract_data_hora_components,
    is_sincrono,
    detect_known_names,
)
from .anchor import AnchorEngine
from ..utils.hash import compute_hash


class EnrichmentEngine:
    """
    Motor de enriquecimento que transforma cards brutos em cards enriquecidos.
    
    Adiciona campos derivados aos campos básicos extraídos:
    - Normalização temporal (semana_num, sprint, data_hora_iso, etc.)
    - Detecção de professor (com fallback heurístico)
    - Classificação baseada em card_type (nova taxonomia)
    - Ancoragem de autoestudos às instruções
    - Normalização de URLs
    - Hash de integridade
    
    NOTA: Usa nova taxonomia (card_type, is_avaliativo) como primária,
    mantendo campos legados (is_autoestudo, is_instrucao) para compatibilidade.
    """
    
    def __init__(
        self, 
        logger: Optional[logging.Logger] = None,
        previous_anchors: Optional[Dict[str, Tuple[str, str]]] = None
    ):
        """
        Inicializa o motor de enriquecimento.
        
        Args:
            logger: Logger para registrar processo (opcional)
            previous_anchors: Ancoragens anteriores a preservar
        """
        self.logger = logger or logging.getLogger(__name__)
        self.anchor_engine = AnchorEngine(previous_anchors)
    
    def enrich_cards(self, cards_data: list[dict]) -> list[dict]:
        """
        Enriquece uma lista de cards com todos os campos derivados.
        
        Args:
            cards_data: Lista de dicionários com dados brutos dos cards
            
        Returns:
            Lista de dicionários com campos enriquecidos
        """
        self.logger.info("🔧 Enriquecendo registros (ancoragem robusta, normalizações)...")
        
        # Faz cópia para não modificar originais
        enriched = [dict(card) for card in cards_data]
        
        # 1. Detecção de nomes conhecidos (primeira passagem)
        known_names = detect_known_names(enriched)
        
        # 2. Enriquecimento individual de cada card
        for card in enriched:
            self._enrich_single_card(card, known_names)
        
        # 3. Ancoragem (requer todos os cards enriquecidos)
        enriched = self.anchor_engine.anchor_autoestudos(enriched, self.logger)
        
        return enriched
    
    def _enrich_single_card(self, card: dict, known_names: list[str]) -> None:
        """
        Enriquece um card individual com campos derivados.
        
        Modifica o dicionário in-place.
        
        Args:
            card: Dicionário do card a enriquecer
            known_names: Lista de nomes frequentes detectados
            
        Deprecated Fields:
            Campos legados mantidos para compatibilidade (serão removidos em v4.0):
            - is_autoestudo: Use card_type == "autoestudo"
            - is_instrucao: Use card_type in ["encontro_orientacao", "encontro_instrucao"]
            - is_atividade_ponderada: Use is_avaliativo
        """
        # === Normalização temporal ===
        card["semana_num"] = parse_week_number(card.get("semana"))
        card["sprint"] = calculate_sprint(card["semana_num"])
        
        # Extrai data/hora do texto combinado
        combined_text = "\n".join([
            card.get("titulo") or "",
            card.get("descricao") or "",
            card.get("texto_completo") or ""
        ])
        iso, date_str, time_str = extract_date_time(combined_text)
        
        # Logging quando fallback de data/hora é usado
        if not card.get("data_hora") and iso:
            self.logger.debug(f"   📅 Fallback data/hora: {date_str} {time_str} (extraído do texto)")
        
        card["data_hora_iso"] = iso
        card["data_ddmmaaaa"] = date_str
        card["hora_hhmm"] = time_str
        
        # === Detecção de professor ===
        # Professor já foi extraído no card.py, apenas manter compatibilidade
        if not card.get("professor"):
            # Fallback para detecção heurística se não foi extraído
            fallback_prof = self._guess_professor_fallback(
                card.get("texto_completo") or "", 
                known_names
            )
            if fallback_prof:
                self.logger.debug(f"   👨‍🏫 Fallback professor: {fallback_prof}")
                card["professor"] = fallback_prof
        
        # === Classificação já foi feita deterministicamente no card.py ===
        # Apenas garantir que os campos estão presentes
        card_type = card.get("card_type", "outros")
        is_encontro = card.get("is_encontro", False)
        is_sincrono = card.get("is_sincrono", False)
        is_avaliativo = card.get("is_avaliativo", False)
        
        # Manter campos legados por compatibilidade (DEPRECATED em v4.0)
        card["is_autoestudo"] = (card_type == "autoestudo")
        card["is_instrucao"] = is_encontro
        card["is_atividade_ponderada"] = is_avaliativo
        
        # Warning de depreciação (log apenas 1x por execução)
        if not hasattr(self, '_deprecation_warned'):
            self.logger.warning(
                "⚠️  DEPRECIAÇÃO: Campos 'is_autoestudo', 'is_instrucao', 'is_atividade_ponderada' "
                "serão removidos em v4.0. Use 'card_type' e 'is_avaliativo'."
            )
            self._deprecation_warned = True
        
        self.logger.debug(f"   🏷️ Tipo: {card_type} | Encontro: {is_encontro} | Síncrono: {is_sincrono} | Avaliativo: {is_avaliativo}")
        
        # === Normalização de URLs ===
        links_normalized = normalize_urls_pipe(card.get("links") or "")
        materiais_normalized = normalize_urls_pipe(card.get("materiais") or "")
        arquivos_normalized = normalize_urls_pipe(card.get("arquivos") or "")
        
        card["links_urls"] = " | ".join(links_normalized) if links_normalized else ""
        card["materiais_urls"] = " | ".join(materiais_normalized) if materiais_normalized else ""
        card["arquivos_urls"] = " | ".join(arquivos_normalized) if arquivos_normalized else ""
        
        card["num_links"] = len(links_normalized)
        card["num_materiais"] = len(materiais_normalized)
        card["num_arquivos"] = len(arquivos_normalized)
        
        # === Hash de integridade ===
        card["record_hash"] = compute_hash(
            card.get("titulo"),
            card.get("data_ddmmaaaa"),
            card.get("professor")
        )

    def _guess_professor_fallback(self, texto: str, known_names: list[str]) -> str:
        """
        Fallback para detecção heurística de professor.
        Usado apenas quando professor não foi extraído deterministicamente.
        """
        import re
        
        # Regex para nome completo
        name_pattern = re.compile(
            r"^[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+"
            r"(\s+[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+){1,}$"
        )
        
        for line in texto.splitlines():
            line = line.strip()
            if name_pattern.match(line) and line in known_names:
                return line
        
        return ""







