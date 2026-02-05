"""
Extração de seções/semanas via API do AdaLove.
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

from ...api.client import AdaLoveAPIClient
from ...api.endpoints import Endpoints


async def extract_sections_and_weeks(
    client: AdaLoveAPIClient,
    section_uuid: str,
    logger: logging.Logger
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extrai todas as atividades de uma seção e organiza por semana (folderCaption).
    
    IMPORTANTE: A API do AdaLove não tem endpoint separado para semanas.
    As atividades vêm todas juntas em /sections/{uuid}/userdata e são
    organizadas pelo campo `folderCaption` (ex: "Semana 01").
    
    Args:
        client: Cliente HTTP autenticado
        section_uuid: UUID da seção/turma
        logger: Logger
    
    Returns:
        Dicionário {nome_semana: [atividades]}
    """
    logger.info(f"📥 Extraindo atividades da seção {section_uuid}...")
    
    try:
        endpoint = Endpoints.section_userdata(section_uuid)
        data = await client.get(endpoint)
        
        activities = data.get("activities", [])
        logger.info(f"   📊 {len(activities)} atividades encontradas")
        
        # Organizar por folderCaption (semana)
        weeks = defaultdict(list)
        for activity in activities:
            folder = activity.get("folderCaption", "Outros")
            weeks[folder].append(activity)
        
        logger.info(f"   📁 {len(weeks)} semanas/pastas encontradas:")
        for week_name, week_activities in sorted(weeks.items()):
            logger.info(f"      - {week_name}: {len(week_activities)} atividades")
        
        return dict(weeks)
    
    except Exception as e:
        logger.error(f"❌ Erro ao extrair atividades: {e}")
        raise


async def extract_available_sections(
    client: AdaLoveAPIClient,
    logger: logging.Logger
) -> List[Dict[str, Any]]:
    """
    Extrai lista de seções/turmas disponíveis para o usuário.
    
    Args:
        client: Cliente HTTP autenticado
        logger: Logger
    
    Returns:
        Lista de seções com uuid, caption, etc.
    """
    logger.info("📥 Extraindo seções disponíveis...")
    
    try:
        data = await client.get(Endpoints.SECTIONS)
        
        sections = data if isinstance(data, list) else data.get("sections", [])
        logger.info(f"   📊 {len(sections)} seções encontradas")
        
        return sections
    
    except Exception as e:
        logger.error(f"❌ Erro ao extrair seções: {e}")
        raise
