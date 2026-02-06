"""
Navegação e interação com a plataforma AdaLove.
"""

import logging
from playwright.async_api import Page


async def navigate_to_academic_life(page: Page, logger: logging.Logger) -> None:
    """
    Navega para a página principal (academic-life) e fecha popups.
    
    Args:
        page: Página do Playwright
        logger: Logger para mensagens
    """
    logger.info("🏠 Navegando para academic-life...")
    
    await page.goto("https://adalove.inteli.edu.br/academic-life")
    await page.wait_for_timeout(3000)
    
    # Fecha popup de faltas se aparecer
    try:
        fechar_btn = page.locator("button:has-text('Fechar')").first
        if await fechar_btn.is_visible(timeout=3000):
            await fechar_btn.click()
            await page.wait_for_timeout(2000)
            logger.info("✅ Popup fechado")
    except Exception:
        pass
    
    logger.info("✅ Página academic-life carregada")


async def discover_weeks(page: Page, logger: logging.Logger) -> list[str]:
    """
    Descobre automaticamente todas as semanas visíveis na turma atual.
    
    Args:
        page: Página do Playwright
        logger: Logger para mensagens
        
    Returns:
        Lista de nomes de semanas encontradas (ex: ["Semana 01", "Semana 02"])
    """
    logger.info("🔍 Descobrindo semanas disponíveis...")
    
    try:
        await page.wait_for_timeout(3000)
        
        # Procura elementos com texto "Semana NN"
        elementos_semana = page.locator("text=/Semana \\d+/i")
        count = await elementos_semana.count()
        
        semanas_encontradas = []
        
        if count > 0:
            logger.info(f"   🔍 Encontradas {count} semanas")
            
            for i in range(count):
                try:
                    elemento = elementos_semana.nth(i)
                    texto = await elemento.text_content()
                    if texto and texto.strip():
                        semanas_encontradas.append(texto.strip())
                except Exception:
                    continue
        
        # Remove duplicatas e ordena
        semanas_unicas = sorted(list(set(semanas_encontradas)))
        
        if not semanas_unicas:
            # Fallback para semanas padrão
            logger.warning("⚠️ Usando semanas padrão (1-10)")
            semanas_unicas = [f"Semana {i:02d}" for i in range(1, 11)]
        
        logger.info(f"📊 {len(semanas_unicas)} semanas descobertas:")
        for semana in semanas_unicas:
            logger.info(f"   📅 {semana}")
            
        return semanas_unicas
        
    except Exception as e:
        logger.error(f"❌ Erro ao descobrir semanas: {e}")
        return [f"Semana {i:02d}" for i in range(1, 11)]


async def close_modal_if_open(page: Page, logger: logging.Logger) -> None:
    """
    Fecha modal do card se estiver aberto, usando múltiplas estratégias.
    
    Tenta (em ordem):
    1. Botões de fechar explícitos (aria-label close/fechar)
    2. Click no backdrop (fundo escurecido)
    3. Click fora do diálogo (usando bounding box)
    4. Pressionar ESC múltiplas vezes
    5. Click no canto do body
    
    Args:
        page: Página do Playwright
        logger: Logger para mensagens
    """
    try:
        modal = page.locator("[role='dialog']").first
        modal_exists = False
        
        try:
            modal_exists = await modal.count() > 0
        except Exception:
            modal_exists = False
            
        backdrop_exists = await page.locator(".MuiBackdrop-root").count() > 0
        
        if modal_exists or backdrop_exists:
            # Estratégia 1: Botões de fechar explícitos
            selectors = [
                "[role='dialog'] button[aria-label='close' i]",
                "[role='dialog'] button[aria-label*='close' i]",
                "[role='dialog'] button[aria-label='fechar' i]",
                "[role='dialog'] button[aria-label*='fechar' i]",
                "[role='dialog'] button.MuiIconButton-root",
                "button:has-text('Fechar')",
                "button:has-text('Close')",
            ]
            
            closed = False
            for selector in selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.count() > 0 and await btn.is_visible(timeout=300):
                        await btn.click()
                        closed = True
                        break
                except Exception:
                    continue
            
            # Estratégia 2: Click no backdrop
            if not closed:
                try:
                    backdrop = page.locator(".MuiBackdrop-root").first
                    if await backdrop.count() > 0:
                        await backdrop.click(position={"x": 5, "y": 5})
                        await page.wait_for_timeout(200)
                        closed = True
                except Exception:
                    pass
            
            # Estratégia 3: Click fora do modal
            if not closed:
                try:
                    box = await modal.bounding_box()
                    if box:
                        x = max(2, int(box["x"]) - 10)
                        y = max(2, int(box["y"]) - 10)
                        await page.mouse.click(x, y)
                        await page.wait_for_timeout(250)
                        closed = True
                except Exception:
                    pass
            
            # Estratégia 4: ESC múltiplas vezes
            for _ in range(3):
                try:
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(200)
                except Exception:
                    pass
            
            # Estratégia 5: Click no body
            try:
                await page.click("body", position={"x": 2, "y": 2})
                await page.wait_for_timeout(250)
            except Exception:
                pass
            
            # Aguarda modal sumir (best-effort)
            try:
                await modal.wait_for(state="hidden", timeout=2000)
            except Exception:
                try:
                    await modal.wait_for(state="detached", timeout=1000)
                except Exception:
                    logger.debug("Modal pode ainda estar aberto; prosseguindo")
                    
    except Exception:
        pass








