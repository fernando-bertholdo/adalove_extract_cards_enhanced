"""
Autenticação na plataforma AdaLove via Google OAuth.
"""

import logging
from playwright.async_api import Page


async def login_adalove(
    page: Page, 
    login: str, 
    senha: str,
    logger: logging.Logger
) -> bool:
    """
    Realiza login no AdaLove com tentativa automática e fallback manual.
    
    Fluxo:
    1. Clica em "Entrar com o Google"
    2. Preenche email/senha (se campos estiverem visíveis)
    3. Aguarda redirecionamento para AdaLove
    4. Se falhar, solicita intervenção manual
    
    Args:
        page: Página do Playwright
        login: Email de login
        senha: Senha
        logger: Logger para mensagens
        
    Returns:
        True se login bem-sucedido
        
    Example:
        >>> await login_adalove(page, "user@example.com", "pass123", logger)
        True
    """
    logger.info("🔑 Fazendo login...")
    
    try:
        # Tenta login automático
        botao_google = page.get_by_role("button", name="Entrar com o Google")
        
        if await botao_google.is_visible(timeout=10000):
            await botao_google.click()
            await page.wait_for_timeout(3000)
            
            # Se redirecionou para Google OAuth
            if "accounts.google.com" in page.url:
                logger.info("   📧 Preenchendo credenciais...")
                
                # Preenche email
                try:
                    email_field = page.locator("input[type='email']").first
                    await email_field.fill(login)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(3000)
                except Exception:
                    pass
                
                # Preenche senha
                try:
                    senha_field = page.locator("input[type='password']").first
                    await senha_field.fill(senha)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(5000)
                except Exception:
                    pass
        
        # Verifica se chegou no AdaLove
        for _ in range(20):
            await page.wait_for_timeout(1000)
            if "adalove.inteli.edu.br" in page.url and "/login" not in page.url:
                logger.info("✅ Login realizado!")
                return True
        
        # Fallback manual
        logger.warning("⚠️ Login automático falhou - intervenção manual")
        print("\n🤚 Complete o login manualmente se necessário")
        input("⏸️ Pressione Enter quando estiver logado: ")
        logger.info("✅ Login confirmado pelo usuário")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False








