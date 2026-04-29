"""
Gerenciamento de autenticação via AWS Cognito OAuth2.

Este módulo lida com a autenticação do usuário via Google OAuth
e obtenção de tokens do AWS Cognito para acesso à API do AdaLove.
"""

import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
from rich.console import Console

from .exceptions import AuthenticationError, TokenExpiredError
from pathlib import Path
import json

# Timeout para autenticação OAuth (segundos)
AUTH_TIMEOUT_SECONDS = 120



class CognitoAuthenticator:
    """
    Gerencia autenticação via AWS Cognito OAuth2.
    
    Estratégia:
    - Usa Playwright APENAS para autenticação (obter token)
    - Token é reutilizado para todas as requisições HTTP
    - Refresh de token quando necessário
    """
    
    def __init__(self):
        self.cognito_url = "https://adalove.auth.us-east-2.amazoncognito.com"
        self.adalove_url = "https://adalove.inteli.edu.br"
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_file = Path(".token_cache")
        self.logger = logging.getLogger(__name__)
        
        # Tentar carregar token existente
        self.load_token()
    
    async def authenticate_google_oauth(
        self, 
        login: str, 
        senha: str,
        timeout_seconds: int = AUTH_TIMEOUT_SECONDS
    ) -> str:
        """
        Autentica via Google OAuth e obtém token Cognito.
        
        Usa Playwright para simular o fluxo de login e capturar
        o token de autenticação armazenado no navegador.
        
        Args:
            login: Email do usuário
            senha: Senha do usuário
            timeout_seconds: Timeout em segundos (padrão: 60)
            
        Returns:
            Token de acesso Cognito
            
        Raises:
            AuthenticationError: Se autenticação falhar ou timeout
        """
        console = Console()
        self.logger.info("🔐 Iniciando autenticação via Google OAuth...")
        console.print(f"[dim]⏱️  Timeout de autenticação: {timeout_seconds}s[/dim]")
        
        try:
            return await asyncio.wait_for(
                self._perform_oauth_login(login, senha),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            error_msg = f"Autenticação excedeu o timeout de {timeout_seconds}s. Pode ser necessário renovar manualmente."
            self.logger.error(f"⏰ {error_msg}")
            console.print(f"[bold red]⏰ TIMEOUT:[/bold red] {error_msg}")
            console.print("[yellow]💡 Dica: Tente limpar o cache (.token_cache) e reiniciar.[/yellow]")
            raise AuthenticationError(error_msg)
    
    async def _perform_oauth_login(self, login: str, senha: str) -> str:
        """Executa o fluxo de login OAuth (chamado internamente com timeout)."""
        console = Console()
        
        async with async_playwright() as p:
            # Headless configurável via env var (debug: ADALOVE_HEADLESS=false)
            import os
            # Padrão não-headless para auth interativa: usuário precisa ver o browser para 2FA
            headless = os.getenv("ADALOVE_HEADLESS", "false").lower() != "false"
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navegar para AdaLove
                console.print("[dim]   🌐 Acessando AdaLove...[/dim]")
                await page.goto(self.adalove_url)
                await page.wait_for_timeout(2000)
                
                # Clicar em "Entrar com o Google"
                console.print("[dim]   🔘 Logando com OAuth Google...[/dim]")
                await page.get_by_role("button", name="Entrar com o Google").click()
                await page.wait_for_timeout(3000)
                
                # Preencher credenciais Google
                if "accounts.google.com" in page.url:
                    console.print("[dim]   📧 Preenchendo credenciais...[/dim]")
                    # Email
                    email_field = page.locator("input[type='email']").first
                    await email_field.fill(login)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(3000)
                    
                    # Senha
                    senha_field = page.locator("input[type='password']").first
                    await senha_field.fill(senha)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(5000)
                
                # Aguardar redirecionamento para AdaLove ou detectar 2FA
                console.print("[dim]   ⏳ Aguardando redirecionamento...[/dim]")
                
                # Verificar se há prompt de 2FA (verificação adicional)
                two_fa_detected = False
                for attempt in range(120):  # 2 minutos máximo
                    await page.wait_for_timeout(1000)
                    
                    # Detectar tela de verificação do Google
                    current_url = page.url
                    page_content = await page.content()
                    
                    # Debug: log URL changes
                    if attempt % 10 == 0:
                        self.logger.info(f"[2FA Check {attempt}/120] URL: {current_url[:80]}...")
                    
                    # challenge/pwd = senha errada (não é 2FA)
                    is_wrong_password = (
                        "challenge/pwd" in current_url.lower() or
                        "signin/rejected" in current_url.lower() or
                        "Wrong password" in page_content or
                        "senha incorreta" in page_content.lower()
                    )

                    if is_wrong_password:
                        import sys
                        print("\n\n" + "="*60, file=sys.stderr)
                        print("❌ SENHA INCORRETA!", file=sys.stderr)
                        print("="*60, file=sys.stderr)
                        print("A senha informada no .env não corresponde à conta Google.", file=sys.stderr)
                        print("  • Atualize SENHA= no arquivo .env", file=sys.stderr)
                        print("  • Feche a janela do navegador", file=sys.stderr)
                        print("="*60 + "\n", file=sys.stderr)
                        raise AuthenticationError("Senha incorreta. Atualize SENHA= no arquivo .env.")

                    # Detectar 2FA real: challenge/selection, challenge/totp, etc (nunca challenge/pwd)
                    is_2fa_page = (
                        ("challenge" in current_url.lower() and "challenge/pwd" not in current_url.lower()) or
                        "verifyidentitychallenge" in current_url.lower() or
                        "Verify it's you" in page_content or
                        "verify your identity" in page_content.lower() or
                        "confirm it's you" in page_content.lower()
                    )

                    if is_2fa_page:
                        if not two_fa_detected:
                            two_fa_detected = True
                            # Trazer janela do browser para frente para o usuário interagir
                            await page.bring_to_front()
                            import sys
                            print("\n\n" + "="*60, file=sys.stderr)
                            print("🔐 VERIFICAÇÃO EM DUAS ETAPAS DETECTADA!", file=sys.stderr)
                            print("="*60, file=sys.stderr)
                            print("👆 Complete a verificação NA JANELA DO NAVEGADOR que abriu.", file=sys.stderr)
                            print("  • Insira o código ou aprove a solicitação no app Google", file=sys.stderr)
                            print("  • A extração continua automaticamente após confirmar", file=sys.stderr)
                            print("  • Timeout em 2 minutos", file=sys.stderr)
                            print("="*60 + "\n", file=sys.stderr)
                            self.logger.warning("⚠️ Aguardando verificação 2FA na janela do navegador...")
                        
                        # Mostrar progresso a cada 10s
                        if attempt % 10 == 0 and attempt > 0:
                            remaining = 120 - attempt
                            print(f"⏳ Aguardando 2FA... ({remaining}s restantes)", file=sys.stderr)
                        continue
                    
                    # Verificou com sucesso e redirecionou
                    if "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
                        if two_fa_detected:
                            import sys
                            print("\n✅ Verificação 2FA completada!\n", file=sys.stderr)
                            self.logger.info("✅ Verificação 2FA bem-sucedida")
                        break
                    
                    # Limite de tentativas sem 2FA
                    if not two_fa_detected and attempt > 20:
                        break
                
                # Capturar token do localStorage ou cookies
                token = await self._extract_token_from_page(page)
                
                if not token:
                    raise AuthenticationError("Token não encontrado após autenticação")
                
                self.token = token
                self.save_token(token)
                self.logger.info("✅ Autenticação bem-sucedida!")
                console.print("[bold green]   ✅ Token obtido com sucesso![/bold green]")
                
                return token
                
            except AuthenticationError:
                raise
            except Exception as e:
                self.logger.error(f"❌ Erro na autenticação: {e}")
                raise AuthenticationError(f"Falha na autenticação: {e}")
            
            finally:
                await browser.close()

    def save_token(self, token: str):
        """Salva token em arquivo de cache."""
        try:
            with open(self.token_file, 'w') as f:
                f.write(token)
            self.logger.debug("💾 Token salvo no cache")
        except Exception as e:
            self.logger.warning(f"⚠️ Falha ao salvar token no cache: {e}")

    def load_token(self):
        """Carrega token do arquivo de cache."""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    token = f.read().strip()
                    if token and len(token) > 20: # Validação básica
                        self.token = token
                        self.logger.info("📂 Token carregado do cache")
            except Exception as e:
                self.logger.warning(f"⚠️ Falha ao ler token do cache: {e}")

    
    async def _extract_token_from_page(self, page: Page) -> Optional[str]:
        """
        Extrai token de autenticação da página.
        
        IMPORTANTE: A API do AdaLove usa **accessToken** do AWS Cognito,
        não o idToken. O idToken resulta em erro 401.
        
        Tenta múltiplas estratégias:
        1. localStorage - accessToken do Cognito
        2. localStorage - idToken do Cognito (fallback)
        3. sessionStorage
        4. Cookies
        
        Args:
            page: Página do Playwright
            
        Returns:
            Token de acesso ou None
        """
        # Estratégia 1: accessToken do Cognito (PRIORITÁRIO)
        try:
            token = await page.evaluate("""
                () => {
                    // Procurar especificamente por accessToken do Cognito
                    const keys = Object.keys(localStorage);
                    const accessTokenKey = keys.find(k => k.includes('accessToken'));
                    if (accessTokenKey) {
                        return localStorage.getItem(accessTokenKey);
                    }
                    return null;
                }
            """)
            
            if token:
                self.logger.debug("✅ accessToken encontrado no localStorage")
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar accessToken: {e}")
        
        # Estratégia 2: idToken do Cognito (fallback, pode não funcionar)
        try:
            token = await page.evaluate("""
                () => {
                    const keys = Object.keys(localStorage);
                    const idTokenKey = keys.find(k => k.includes('idToken'));
                    if (idTokenKey) {
                        return localStorage.getItem(idTokenKey);
                    }
                    return null;
                }
            """)
            
            if token:
                self.logger.warning("⚠️ Usando idToken (pode resultar em erro 401)")
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar idToken: {e}")
        
        # Estratégia 3: Procurar qualquer token JWT em localStorage
        try:
            token = await page.evaluate("""
                () => {
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        const value = localStorage.getItem(key);
                        
                        // Procurar por JWT (começa com 'eyJ')
                        if (value && value.startsWith('eyJ')) {
                            return value;
                        }
                    }
                    return null;
                }
            """)
            
            if token:
                self.logger.debug("✅ Token JWT encontrado no localStorage")
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar token JWT: {e}")
        
        # Estratégia 4: sessionStorage
        try:
            token = await page.evaluate("""
                () => {
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        const value = sessionStorage.getItem(key);
                        
                        if (key && (
                            key.includes('token') || 
                            key.includes('auth') ||
                            key.includes('cognito')
                        )) {
                            try {
                                const parsed = JSON.parse(value);
                                if (parsed.accessToken || parsed.idToken) {
                                    return parsed.accessToken || parsed.idToken;
                                }
                            } catch {
                                if (value && value.length > 100) {
                                    return value;
                                }
                            }
                        }
                    }
                    return null;
                }
            """)
            
            if token:
                self.logger.debug("✅ Token encontrado no sessionStorage")
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar token no sessionStorage: {e}")
        
        # Estratégia 5: Cookies
        try:
            cookies = await page.context.cookies()
            for cookie in cookies:
                if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                    if len(cookie['value']) > 100:
                        self.logger.debug(f"✅ Token encontrado no cookie: {cookie['name']}")
                        return cookie['value']
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar token nos cookies: {e}")
        
        return None
    
    async def refresh_access_token(self) -> str:
        """
        Renova token de acesso usando refresh token.
        
        Returns:
            Novo token de acesso
            
        Raises:
            TokenExpiredError: Se refresh falhar
        """
        if not self.refresh_token:
            raise TokenExpiredError("Refresh token não disponível")
        
        # TODO: Implementar refresh via API Cognito
        # Por enquanto, lançar erro para forçar re-autenticação
        raise TokenExpiredError("Token expirado - necessário re-autenticar")
    
    def is_authenticated(self) -> bool:
        """Verifica se há token válido."""
        return self.token is not None
