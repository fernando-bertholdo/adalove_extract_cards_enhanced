"""
Extração de cards por semana.
"""

import logging
from playwright.async_api import Page

from .card import extract_card_data


async def extract_week_cards(
    page: Page,
    week_name: str,
    logger: logging.Logger
) -> list[dict]:
    """
    Extrai todos os cards de uma semana específica.
    
    Args:
        page: Página do Playwright
        week_name: Nome da semana (ex: "Semana 01")
        logger: Logger para mensagens
        
    Returns:
        Lista de dicionários com dados dos cards
    """
    logger.info(f"📋 Extraindo: {week_name}")
    
    try:
        # Procura e clica na semana
        semana_element = page.get_by_text(week_name, exact=False).first
        
        if await semana_element.is_visible(timeout=10000):
            await semana_element.click()
            await page.wait_for_timeout(3000)
            
            # Procura cards
            cards = page.locator("[data-rbd-draggable-id]")
            count = await cards.count()
            
            if count > 0:
                logger.info(f"   ✅ {count} cards encontrados")
                
                cards_data = []
                for i in range(count):
                    try:
                        card = cards.nth(i)
                        card_info = await extract_card_data(
                            card, i, week_name, page, logger
                        )
                        
                        if card_info:
                            cards_data.append(card_info)
                            
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro no card {i+1}: {e}")
                        continue
                
                logger.info(f"   📊 {len(cards_data)} cards processados com sucesso")
                return cards_data
            else:
                logger.warning(f"   ❌ Nenhum card encontrado em {week_name}")
                return []
        else:
            logger.warning(f"   ❌ Semana não encontrada: {week_name}")
            return []
            
    except Exception as e:
        logger.error(f"   ❌ Erro ao processar {week_name}: {e}")
        return []








