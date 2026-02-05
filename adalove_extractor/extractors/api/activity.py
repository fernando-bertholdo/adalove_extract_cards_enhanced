"""
Extração de atividades/cards via API do AdaLove.

Este módulo implementa a extração de dados de atividades usando a API REST,
mantendo 100% de paridade com a extração via Playwright.
"""

import logging
from typing import List, Optional, Dict, Any

from ...api.client import AdaLoveAPIClient
from ...api.endpoints import Endpoints
from ...models.card import Card, CardType
from ...models.card_types import get_card_type_from_icon, is_encontro_type


async def extract_activities_from_section(
    client: AdaLoveAPIClient,
    section_uuid: str,
    section_name: str,
    logger: logging.Logger
) -> List[Card]:
    """
    Extrai todas as atividades de uma seção via API.
    
    Args:
        client: Cliente HTTP autenticado
        section_uuid: UUID da seção
        section_name: Nome da seção (ex: "Semana 01")
        logger: Logger
    
    Returns:
        Lista de Cards extraídos e enriquecidos
    """
    logger.info(f"📥 Extraindo atividades da {section_name} via API...")
    
    try:
        # Buscar atividades da API
        endpoint = Endpoints.section_activities(section_uuid)
        data = await client.get(endpoint)
        
        # Parse response
        activities_data = data.get("activities", [])
        logger.info(f"   📊 {len(activities_data)} atividades encontradas")
        
        cards = []
        for idx, activity_data in enumerate(activities_data):
            try:
                card = _convert_api_activity_to_card(
                    activity_data,
                    section_name,
                    idx,
                    logger
                )
                if card:
                    cards.append(card)
            except Exception as e:
                logger.error(f"   ❌ Erro ao processar atividade {idx}: {e}")
                continue
        
        logger.info(f"   ✅ {len(cards)} cards extraídos com sucesso")
        return cards
    
    except Exception as e:
        logger.error(f"❌ Erro ao extrair atividades da {section_name}: {e}")
        raise


def _convert_api_activity_to_card(
    activity_data: dict,
    semana: str,
    indice: int,
    logger: logging.Logger
) -> Optional[Card]:
    """
    Converte dados da API para modelo Card.
    
    IMPORTANTE: Mantém paridade com extração Playwright:
    - Mesmos campos (20+ campos)
    - Mesma categorização (5 tipos de cards)
    - Mesmo enriquecimento
    
    Args:
        activity_data: Dados da atividade da API
        semana: Nome da semana
        indice: Índice da atividade
        logger: Logger
    
    Returns:
        Card ou None se erro
    """
    try:
        # Identificar tipo do card pelo ícone
        icon_id = activity_data.get("icon_id", "")
        card_type = get_card_type_from_icon(icon_id)
        
        # Extrair campos básicos
        titulo = activity_data.get("title", "")
        descricao = activity_data.get("description", "")
        
        # Texto completo
        if titulo and descricao:
            texto_completo = f"{titulo}\\n\\n{descricao}"
        else:
            texto_completo = titulo or descricao
        
        # Campos condicionais baseados no tipo
        data_hora = None
        professor = None
        assuntos_relacionados = []
        conteudos_relacionados = []
        is_sincrono = False
        is_avaliativo = False
        
        # Data/hora para encontros e avaliações
        if card_type in ["encontro_instrucao", "encontro_orientacao", "avaliacao"]:
            scheduled_at = activity_data.get("scheduled_at")
            if scheduled_at:
                data_hora = str(scheduled_at)
                is_sincrono = True
        
        # Professor para autoestudo, encontros, avaliações
        if card_type in ["autoestudo", "encontro_instrucao", "encontro_orientacao", "avaliacao"]:
            professor = activity_data.get("professor_name")
        
        # Assuntos relacionados para autoestudo e encontros
        if card_type in ["autoestudo", "encontro_instrucao", "encontro_orientacao"]:
            assuntos_relacionados = activity_data.get("related_subjects", [])
        
        # Conteúdos relacionados apenas para autoestudo
        if card_type == "autoestudo":
            conteudos_relacionados = activity_data.get("related_contents", [])
        
        # Atividade ponderada para projeto e avaliação
        if card_type in ["projeto", "avaliacao"]:
            is_avaliativo = activity_data.get("is_graded", False)
        
        # Taxonomia
        is_encontro = is_encontro_type(card_type)
        
        # Materiais e links
        links_str, materiais_str, arquivos_str = _extract_materials(
            activity_data.get("materials", []),
            activity_data.get("links", []),
            activity_data.get("files", [])
        )
        
        # Tipo heurístico (legado)
        tipo = _map_card_type_to_legacy_tipo(card_type)
        
        # Criar Card
        card = Card(
            semana=semana,
            indice=indice + 1,
            id=activity_data.get("uuid", ""),
            titulo=titulo,
            descricao=descricao,
            tipo=tipo,
            texto_completo=texto_completo,
            data_hora=data_hora,
            professor=professor,
            links=links_str,
            materiais=materiais_str,
            arquivos=arquivos_str,
            card_type=card_type,
            is_encontro=is_encontro,
            is_sincrono=is_sincrono,
            is_avaliativo=is_avaliativo,
            assuntos_relacionados=assuntos_relacionados,
            conteudos_relacionados=conteudos_relacionados
        )
        
        logger.debug(f"   ✅ Card {indice+1}: {titulo} ({card_type})")
        return card
    
    except Exception as e:
        logger.error(f"   ❌ Erro ao converter atividade: {e}")
        return None


def _extract_materials(
    materials: List[dict],
    links: List[dict],
    files: List[dict]
) -> tuple[str, str, str]:
    """
    Extrai e categoriza materiais, links e arquivos.
    
    Mantém formato compatível com Playwright:
    - links: "Texto: URL | Texto: URL"
    - materiais: "Texto: URL | Texto: URL"
    - arquivos: "Texto: URL | Texto: URL"
    
    Args:
        materials: Lista de materiais da API
        links: Lista de links da API
        files: Lista de arquivos da API
    
    Returns:
        Tupla (links_str, materiais_str, arquivos_str)
    """
    links_list = []
    materiais_list = []
    arquivos_list = []
    
    # Processar materials
    for material in materials:
        url = material.get("url", "")
        text = material.get("title", "Link")
        
        if not url:
            continue
        
        # Categorizar por tipo de URL
        if "drive.google.com" in url or "docs.google.com" in url:
            materiais_list.append(f"{text}: {url}")
        elif any(url.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"]):
            arquivos_list.append(f"{text}: {url}")
        else:
            links_list.append(f"{text}: {url}")
    
    # Processar links
    for link in links:
        url = link.get("url", "")
        text = link.get("text", "Link")
        
        if url:
            links_list.append(f"{text}: {url}")
    
    # Processar files
    for file in files:
        url = file.get("url", "")
        text = file.get("name", "Arquivo")
        
        if url:
            arquivos_list.append(f"{text}: {url}")
    
    return (
        " | ".join(links_list) if links_list else "",
        " | ".join(materiais_list) if materiais_list else "",
        " | ".join(arquivos_list) if arquivos_list else ""
    )


def _map_card_type_to_legacy_tipo(card_type: str) -> str:
    """
    Mapeia card_type para campo 'tipo' legado.
    
    Mantém compatibilidade com código existente.
    
    Args:
        card_type: Tipo do card (autoestudo, encontro, etc.)
    
    Returns:
        Tipo legado (Material, Atividade, etc.)
    """
    mapping = {
        "autoestudo": "Material",
        "encontro_instrucao": "Atividade",
        "encontro_orientacao": "Atividade",
        "projeto": "Projeto",
        "avaliacao": "Avaliação",
        "atividade_customizada": "Atividade",
        "outros": "Outros"
    }
    return mapping.get(card_type, "Outros")
