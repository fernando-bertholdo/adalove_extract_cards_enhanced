"""
Gerenciamento de autenticação via AWS Cognito OAuth2.

Este módulo lida com a autenticação do usuário via Google OAuth
e obtenção de tokens do AWS Cognito para acesso à API do AdaLove.

Estratégia de sessão (3 níveis, do mais barato ao mais caro):

1. Token Cognito em cache (.token_cache) ainda válido  → nenhum browser abre
2. Perfil persistente (.auth_profile) com sessão Google → browser headless, ~5s
3. Login interativo                                     → janela visível, o
   usuário assume o controle e a janela permanece aberta até concluir

O princípio central deste módulo é **esperar por condição, nunca por tempo
fixo**: o sucesso é definido por "o accessToken apareceu no localStorage",
não por "já se passaram N segundos".
"""

import asyncio
import base64
import json
import logging
import os
import re
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from playwright.async_api import Page, async_playwright
from rich.console import Console

from .exceptions import AuthenticationError, TokenExpiredError

# ── Tempos ────────────────────────────────────────────────────────────────
# Login interativo cobre: digitar e-mail, senha, pegar o celular e aprovar 2FA.
AUTH_TIMEOUT_SECONDS = int(os.getenv("ADALOVE_AUTH_TIMEOUT", "300"))
# Sessão já salva no perfil: se demorar mais que isso, algo mudou.
HEADLESS_TIMEOUT_SECONDS = 45
# Orçamento do auto-preenchimento. Sem um teto próprio, os timeouts internos
# dele (goto 45s + cliques 20s + waits 30s) consumiam a fase inteira antes de
# o polling sequer começar.
AUTOFILL_BUDGET_SECONDS = 60
# Tempo máximo esperando a SPA do AdaLove decidir entre "logado" e "tela de login".
SPA_SETTLE_SECONDS = 15
# Margem para não iniciar uma extração com token prestes a vencer.
TOKEN_EXPIRY_SKEW_SECONDS = 120
# Intervalo de polling da condição de sucesso.
POLL_INTERVAL_MS = 500

# Diretório do perfil persistente do Chrome (sessão Google fica aqui).
AUTH_PROFILE_DIR = Path(".auth_profile")
# Marcador escrito só após um login bem-sucedido. O diretório sozinho não serve
# como sinal: ele é criado em toda tentativa, inclusive nas que falham, e uma
# tentativa headless sobre perfil vazio é garantidamente inútil — só queima tempo.
SESSION_MARKER = AUTH_PROFILE_DIR / ".session_ok"

# O Google localiza a interface por IP, então o rótulo do botão varia.
# Sempre há fallback para a tecla Enter, que independe de idioma.
NEXT_BUTTON_RE = re.compile(
    r"^\s*(next|avan[çc]ar|pr[óo]xim[ao]|siguiente|weiter|suivant)\s*$", re.IGNORECASE
)
GOOGLE_LOGIN_BUTTON_RE = re.compile(r"entrar com o google|sign in with google", re.IGNORECASE)

# O Google altera a estrutura da tela de login sem aviso. Hoje o campo de e-mail
# é <input type="text" id="identifierId" name="identifier"> — NÃO existe nenhum
# input[type=email] na página. O seletor antigo casava com zero elementos e só
# estourava timeout de 15s, deixando o campo vazio. Uma lista de candidatos
# degrada graciosamente em vez de travar quando a estrutura muda de novo.
EMAIL_SELECTORS = (
    "#identifierId",
    "input[name='identifier']",
    "input[type='email']:visible",
    "input[autocomplete='username']:visible",
    "input[type='text']:visible",
)
PASSWORD_SELECTORS = (
    "input[type='password']:visible",
    "input[name='Passwd']",
    "#password input",
)

WRONG_PASSWORD_MARKERS = (
    "wrong password",
    "senha incorreta",
    "senha errada",
    "incorrect password",
)

BROWSER_BLOCKED_MARKERS = (
    "this browser or app may not be secure",
    "browser or app may not be secure",
    "navegador ou app pode não ser seguro",
    "este navegador ou app",
)


class LoginState(str, Enum):
    """Estado observável da máquina de login OAuth."""

    ADALOVE_READY = "adalove_ready"
    GOOGLE_EMAIL = "google_email"
    GOOGLE_PASSWORD = "google_password"
    GOOGLE_2FA = "google_2fa"
    WRONG_PASSWORD = "wrong_password"
    BROWSER_BLOCKED = "browser_blocked"
    UNKNOWN = "unknown"


# ── Lógica pura (testável sem browser) ────────────────────────────────────


def decode_jwt_claims(token: Optional[str]) -> Optional[dict]:
    """Decodifica o payload de um JWT sem validar a assinatura.

    A validação criptográfica é responsabilidade do servidor. Aqui só
    precisamos ler o claim `exp` para saber se vale a pena reaproveitar
    o token — o que evita abrir um browser à toa.

    Args:
        token: String JWT (header.payload.signature)

    Returns:
        Dict com as claims, ou None se o token for malformado.
    """
    if not token or not isinstance(token, str):
        return None

    parts = token.split(".")
    if len(parts) != 3:
        return None

    try:
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)  # restaura padding base64url
        claims = json.loads(base64.urlsafe_b64decode(payload))
        return claims if isinstance(claims, dict) else None
    except Exception:
        return None


def is_token_valid(
    token: Optional[str], skew_seconds: int = TOKEN_EXPIRY_SKEW_SECONDS
) -> bool:
    """Verifica se o token é um JWT bem formado e ainda vigente.

    Args:
        token: Token a validar
        skew_seconds: Margem de segurança; um token que expira dentro
            dessa janela é considerado inválido.

    Returns:
        True se o token pode ser reaproveitado com segurança.

    Example:
        >>> is_token_valid(None)
        False
    """
    claims = decode_jwt_claims(token)
    if not claims:
        return False

    exp = claims.get("exp")
    if not isinstance(exp, (int, float)):
        return False

    return (exp - skew_seconds) > time.time()


def classify_login_state(url: str, content: str = "") -> LoginState:
    """Classifica em que ponto do fluxo OAuth a página está.

    IMPORTANTE: `accounts.google.com/v3/signin/challenge/pwd` é a URL da
    *tela de digitação* de senha, não um veredito sobre ela. Só existe
    senha incorreta quando a página traz o erro explícito no conteúdo.
    Confundir os dois derrubava o login assim que o usuário chegava na
    tela para digitar.

    Args:
        url: URL corrente da página
        content: HTML da página (opcional; pode falhar durante navegação)

    Returns:
        Estado correspondente do fluxo.
    """
    u = (url or "").lower()
    c = (content or "").lower()

    if any(marker in c for marker in BROWSER_BLOCKED_MARKERS):
        return LoginState.BROWSER_BLOCKED

    if "signin/rejected" in u:
        return LoginState.WRONG_PASSWORD

    if "accounts.google.com" in u:
        if "/challenge/pwd" in u:
            if any(marker in c for marker in WRONG_PASSWORD_MARKERS):
                return LoginState.WRONG_PASSWORD
            return LoginState.GOOGLE_PASSWORD

        if "/challenge/" in u or "verifyidentitychallenge" in u:
            return LoginState.GOOGLE_2FA

        if "/identifier" in u:
            return LoginState.GOOGLE_EMAIL

        return LoginState.UNKNOWN

    if "adalove.inteli.edu.br" in u:
        # A raiz do AdaLove renderiza a própria tela de login, e a URL não
        # contém "/login". Inferir sessão só pela ausência desse trecho fazia
        # o auto-preenchimento concluir "já autenticado" e retornar sem nunca
        # clicar em "Entrar com o Google".
        path = u.split("adalove.inteli.edu.br", 1)[1].split("?")[0].split("#")[0]
        if path in ("", "/") or "/login" in path:
            return LoginState.UNKNOWN
        return LoginState.ADALOVE_READY

    return LoginState.UNKNOWN


# ── Autenticador ──────────────────────────────────────────────────────────


class CognitoAuthenticator:
    """
    Gerencia autenticação via AWS Cognito OAuth2.

    Estratégia:
    - Usa Playwright APENAS para autenticação (obter token)
    - Token é reutilizado para todas as requisições HTTP
    - Perfil persistente evita repetir 2FA a cada execução
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

    # ── API pública ───────────────────────────────────────────────────────

    async def authenticate_google_oauth(
        self,
        login: str,
        senha: str,
        timeout_seconds: int = AUTH_TIMEOUT_SECONDS,
    ) -> str:
        """
        Autentica via Google OAuth e obtém token Cognito.

        Tenta, em ordem: token em cache → perfil salvo (headless) →
        login interativo em janela visível.

        Args:
            login: Email do usuário
            senha: Senha do usuário
            timeout_seconds: Orçamento para o login interativo

        Returns:
            Token de acesso Cognito

        Raises:
            AuthenticationError: Se a autenticação não for concluída
        """
        console = Console()

        # Nível 1: token em cache ainda vigente — nenhum browser abre.
        if is_token_valid(self.token):
            self.logger.info("🔑 Token em cache ainda válido; browser não será aberto")
            return self.token

        self.logger.info("🔐 Iniciando autenticação via Google OAuth...")

        # Guarda externa: só deve disparar se o Playwright travar de forma anômala.
        # Precisa cobrir AMBAS as fases (headless + interativa) mais a abertura do
        # Chrome com perfil persistente, que é lenta. Um limite menor que a soma
        # das fases cancelava o login com tempo ainda sobrando no relógio interno.
        hard_limit = HEADLESS_TIMEOUT_SECONDS + timeout_seconds + 120
        try:
            return await asyncio.wait_for(
                self._perform_oauth_login(login, senha, timeout_seconds),
                timeout=hard_limit,
            )
        except asyncio.TimeoutError:
            msg = f"Autenticação excedeu o limite de {hard_limit}s."
            self.logger.error(f"⏰ {msg}")
            console.print(f"[bold red]⏰ TIMEOUT:[/bold red] {msg}")
            raise AuthenticationError(msg)

    def is_authenticated(self) -> bool:
        """Verifica se há token válido e não expirado."""
        return is_token_valid(self.token)

    # ── Orquestração do login ─────────────────────────────────────────────

    async def _perform_oauth_login(
        self, login: str, senha: str, timeout_seconds: int
    ) -> str:
        """Executa o fluxo OAuth escalando do modo barato para o interativo."""
        console = Console()
        forced_headless = os.getenv("ADALOVE_HEADLESS", "").lower() in ("true", "1", "yes")
        non_interactive = os.getenv("ADALOVE_INTERACTIVE", "").lower() in ("false", "0", "no")

        # Nível 2: sessão comprovadamente salva → tenta headless, sem incomodar.
        if SESSION_MARKER.exists():
            console.print("[dim]   🔎 Reaproveitando sessão salva...[/dim]")
            token = await self._run_oauth_session(
                login,
                senha,
                headless=True,
                timeout_seconds=HEADLESS_TIMEOUT_SECONDS,
                interactive=False,
            )
            if token:
                console.print("[bold green]   ✅ Sessão salva reaproveitada![/bold green]")
                return token
            console.print("[dim]   ↪ Sessão salva insuficiente; abrindo janela...[/dim]")

        if forced_headless or non_interactive:
            raise AuthenticationError(
                "Login interativo necessário, mas o modo headless/não-interativo está ativo. "
                "Execute uma vez em modo interativo para salvar a sessão em .auth_profile/."
            )

        # Nível 3: janela visível, usuário no controle.
        token = await self._run_oauth_session(
            login,
            senha,
            headless=False,
            timeout_seconds=timeout_seconds,
            interactive=True,
        )
        if not token:
            raise AuthenticationError(
                "Login não concluído dentro do tempo previsto. "
                f"Aumente com ADALOVE_AUTH_TIMEOUT (atual: {timeout_seconds}s)."
            )
        return token

    async def _run_oauth_session(
        self,
        login: str,
        senha: str,
        *,
        headless: bool,
        timeout_seconds: int,
        interactive: bool,
    ) -> Optional[str]:
        """Abre um contexto de browser e tenta obter o token.

        Devolve None (em vez de levantar) quando o login simplesmente não
        se completou — assim o chamador pode escalar para o modo interativo.

        Args:
            headless: Se a janela deve ficar oculta
            timeout_seconds: Orçamento de espera pela condição de sucesso
            interactive: Se um humano pode intervir na janela

        Returns:
            Token Cognito, ou None se não concluído.
        """
        console = Console()
        AUTH_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds

        async with async_playwright() as p:
            context = await self._launch_context(p, headless=headless)
            try:
                page = context.pages[0] if context.pages else await context.new_page()

                # O auto-preenchimento recebe teto próprio para não devorar o
                # orçamento da fase antes de o polling começar.
                autofill_budget = min(
                    AUTOFILL_BUDGET_SECONDS, max(5.0, deadline - time.monotonic())
                )
                try:
                    await asyncio.wait_for(
                        self._try_autofill(page, login, senha, console=console),
                        timeout=autofill_budget,
                    )
                except asyncio.TimeoutError:
                    self.logger.info(
                        f"Auto-preenchimento excedeu {autofill_budget:.0f}s; usuário assume"
                    )

                token = await self._wait_for_authentication(
                    page,
                    deadline=deadline,
                    interactive=interactive,
                    console=console,
                )
                if token:
                    self._mark_session_ok()
                return token
            except Exception as e:
                # Nenhuma exceção do fluxo derruba o login: em modo interativo
                # a janela continua disponível e o polling segue tentando.
                self.logger.warning(f"⚠️ Falha durante a sessão de login: {e}")
                return None
            finally:
                await context.close()

    async def _launch_context(self, playwright, *, headless: bool):
        """Abre contexto persistente, preferindo o Chrome real.

        O Google bloqueia logins em Chromium automatizado com "este navegador
        ou app pode não ser seguro". O Chrome instalado no sistema (channel
        "chrome") não sofre esse bloqueio na maioria dos casos.
        """
        launch_args = {
            "user_data_dir": str(AUTH_PROFILE_DIR),
            "headless": headless,
            "locale": "pt-BR",
            "viewport": {"width": 1280, "height": 900},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        }

        try:
            return await playwright.chromium.launch_persistent_context(
                channel="chrome", **launch_args
            )
        except Exception as e:
            self.logger.info(f"Chrome do sistema indisponível ({e}); usando Chromium empacotado")
            return await playwright.chromium.launch_persistent_context(**launch_args)

    async def _try_autofill(self, page: Page, login: str, senha: str, *, console) -> None:
        """Preenche credenciais em regime de melhor-esforço.

        Toda falha aqui é recuperável por design: se qualquer etapa não
        funcionar, o usuário simplesmente assume o controle na janela. Por
        isso nada aqui levanta exceção para fora.
        """
        try:
            console.print("[dim]   🌐 Acessando AdaLove...[/dim]")
            await page.goto(self.adalove_url, wait_until="domcontentloaded", timeout=45000)

            # A SPA leva um tempo para decidir entre "já logado" e "tela de
            # login", e a URL é a MESMA nos dois casos enquanto isso. Só o token
            # distingue de verdade — inferir pela URL fazia esta função concluir
            # "já autenticado" e retornar sem clicar em nada, deixando a janela
            # parada na tela de login até o timeout.
            google_btn = page.get_by_role("button", name=GOOGLE_LOGIN_BUTTON_RE).first
            settle_deadline = time.monotonic() + SPA_SETTLE_SECONDS
            while time.monotonic() < settle_deadline:
                if await self._extract_token_from_page(page, strict=True):
                    return  # sessão do perfil já valeu; nada a preencher
                if "accounts.google.com" in page.url:
                    break
                try:
                    if await google_btn.is_visible(timeout=500):
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)

            if "accounts.google.com" not in page.url:
                console.print("[dim]   🔘 Iniciando OAuth Google...[/dim]")
                await google_btn.click(timeout=20000)
                # Espera pela CONDIÇÃO de chegada ao Google, não por tempo fixo.
                await page.wait_for_url(re.compile(r"accounts\.google\.com"), timeout=30000)

            state, _ = await self._read_state(page)

            if state == LoginState.GOOGLE_EMAIL:
                console.print("[dim]   📧 Preenchendo e-mail...[/dim]")
                if not await self._fill_first_available(
                    page, EMAIL_SELECTORS, login, campo="e-mail"
                ):
                    return  # usuário assume na janela
                await self._submit_step(page)

                # Espera a CONDIÇÃO real (campo de senha visível) em vez da URL
                # challenge/pwd: se o Google mudar a rota, a espera por URL trava
                # os 30s inteiros mesmo com a tela de senha já na frente.
                try:
                    await page.locator(PASSWORD_SELECTORS[0]).wait_for(
                        state="visible", timeout=25000
                    )
                except Exception:
                    pass
                state, _ = await self._read_state(page)

            if state == LoginState.GOOGLE_PASSWORD:
                console.print("[dim]   🔑 Preenchendo senha...[/dim]")
                if not await self._fill_first_available(
                    page, PASSWORD_SELECTORS, senha, campo="senha"
                ):
                    return  # usuário assume na janela
                await self._submit_step(page)

        except Exception as e:
            self.logger.info(f"Auto-preenchimento incompleto ({type(e).__name__}); usuário assume")

    async def _fill_first_available(
        self, page: Page, selectors: tuple[str, ...], value: str, *, campo: str
    ) -> bool:
        """Preenche o primeiro seletor que existir e estiver editável.

        Cada candidato recebe um timeout curto: com um seletor único e errado,
        o Playwright espera o timeout inteiro por um elemento inexistente e o
        campo fica vazio sem explicação. Falhar rápido e tentar o próximo é o
        que permite sobreviver a mudanças de layout do Google.

        Args:
            selectors: Candidatos em ordem de preferência
            campo: Nome do campo, apenas para log

        Returns:
            True se algum seletor foi preenchido.
        """
        for selector in selectors:
            try:
                loc = page.locator(selector).first
                await loc.wait_for(state="visible", timeout=3000)
                await loc.fill(value, timeout=5000)
                self.logger.info(f"Campo '{campo}' preenchido via seletor {selector!r}")
                return True
            except Exception:
                continue

        self.logger.warning(
            f"Nenhum seletor funcionou para o campo '{campo}' — usuário assume o preenchimento"
        )
        return False

    async def _submit_step(self, page: Page) -> None:
        """Avança uma etapa do formulário Google.

        Tenta o botão pelo rótulo (que muda conforme o idioma detectado por
        IP) e recorre ao Enter, que funciona em qualquer localização.
        """
        try:
            await page.get_by_role("button", name=NEXT_BUTTON_RE).first.click(timeout=8000)
        except Exception:
            self.logger.debug("Botão de avanço não localizado; usando Enter")
            await page.keyboard.press("Enter")

    # ── Espera por condição ───────────────────────────────────────────────

    async def _wait_for_authentication(
        self,
        page: Page,
        *,
        deadline: float,
        interactive: bool,
        console,
    ) -> Optional[str]:
        """Aguarda a CONDIÇÃO de sucesso: o accessToken aparecer no navegador.

        Substitui a contagem de tentativas do fluxo antigo, que desistia em
        ~21s quando o 2FA ainda não tinha sido *detectado* — inclusive
        enquanto o usuário ainda digitava o e-mail.

        Args:
            deadline: Instante (time.monotonic) em que a espera acaba. É
                absoluto, e não uma duração, para que o tempo já gasto na
                abertura do browser e no auto-preenchimento seja descontado
                deste mesmo orçamento.
            interactive: Se há um humano capaz de agir na janela

        Returns:
            Token, ou None se o tempo acabar.
        """
        announced: set[LoginState] = set()
        last_progress = time.monotonic()

        while time.monotonic() < deadline:
            # A condição de sucesso tem precedência sobre qualquer heurística.
            token = await self._extract_token_from_page(page, strict=True)
            if token and is_token_valid(token):
                self.token = token
                self.save_token(token)
                self.logger.info("✅ Autenticação bem-sucedida!")
                return token

            state, url = await self._read_state(page)

            if state == LoginState.BROWSER_BLOCKED and state not in announced:
                announced.add(state)
                self._banner(
                    "🚫 GOOGLE BLOQUEOU ESTE NAVEGADOR",
                    [
                        "O Google recusou o login por considerar o navegador inseguro.",
                        "• Instale o Google Chrome (o extrator prefere o Chrome real)",
                        "• Ou faça login manualmente na janela aberta",
                    ],
                )

            if state == LoginState.WRONG_PASSWORD and state not in announced:
                announced.add(state)
                # Não é fatal: o usuário pode corrigir na própria janela.
                self._banner(
                    "❌ SENHA RECUSADA PELO GOOGLE",
                    [
                        "A senha do .env não foi aceita.",
                        "• Corrija SENHA= no .env para as próximas execuções",
                        "• Ou digite a senha correta na janela aberta agora",
                    ],
                )

            if state == LoginState.GOOGLE_2FA:
                if not interactive:
                    # Headless não resolve 2FA: escala para janela visível.
                    self.logger.info("2FA exigido; escalando para modo interativo")
                    return None
                if state not in announced:
                    announced.add(state)
                    try:
                        await page.bring_to_front()
                    except Exception:
                        pass
                    self._banner(
                        "🔐 VERIFICAÇÃO EM DUAS ETAPAS",
                        [
                            "👆 Complete a verificação NA JANELA DO NAVEGADOR.",
                            "• A extração continua sozinha assim que você aprovar",
                            "• A janela NÃO será fechada enquanto você resolve",
                        ],
                    )

            # Feedback de progresso a cada 15s, sem poluir o terminal.
            if interactive and time.monotonic() - last_progress >= 15:
                last_progress = time.monotonic()
                restante = int(deadline - time.monotonic())
                print(
                    f"⏳ Aguardando conclusão do login... ({restante}s restantes)",
                    file=sys.stderr,
                    flush=True,
                )

            await asyncio.sleep(POLL_INTERVAL_MS / 1000)

        # Última tentativa com estratégias mais permissivas antes de desistir.
        token = await self._extract_token_from_page(page, strict=False)
        if token and is_token_valid(token):
            self.token = token
            self.save_token(token)
            return token

        return None

    async def _read_state(self, page: Page) -> Tuple[LoginState, str]:
        """Lê o estado atual da página de forma resiliente a navegações.

        `page.content()` levanta "Execution context was destroyed" quando a
        página navega no meio da leitura — por isso ele só é chamado onde é
        realmente necessário (distinguir tela de senha de senha recusada) e
        sempre protegido.
        """
        try:
            url = page.url
        except Exception:
            return LoginState.UNKNOWN, ""

        content = ""
        if "/challenge/pwd" in url.lower() or "accounts.google.com" in url.lower():
            try:
                content = await page.content()
            except Exception:
                content = ""

        return classify_login_state(url, content), url

    @staticmethod
    def _banner(title: str, lines: list[str]) -> None:
        """Imprime aviso em stderr, fora do controle do spinner do Rich."""
        print("\n" + "=" * 62, file=sys.stderr)
        print(title, file=sys.stderr)
        print("=" * 62, file=sys.stderr)
        for line in lines:
            print(line, file=sys.stderr)
        print("=" * 62 + "\n", file=sys.stderr, flush=True)

    # ── Persistência de token ─────────────────────────────────────────────

    def _mark_session_ok(self) -> None:
        """Registra que este perfil já concluiu um login com sucesso.

        Só a partir daí vale tentar o atalho headless. A existência do
        diretório não serve como sinal: ele é criado em toda tentativa,
        inclusive nas que falham.
        """
        try:
            SESSION_MARKER.write_text("ok", encoding="utf-8")
        except Exception as e:
            self.logger.debug(f"Não foi possível marcar a sessão: {e}")

    def save_token(self, token: str):
        """Salva token em arquivo de cache com permissão restrita."""
        try:
            self.token_file.write_text(token, encoding="utf-8")
            try:
                os.chmod(self.token_file, 0o600)  # no-op efetivo no Windows
            except OSError:
                pass
            self.logger.debug("💾 Token salvo no cache")
        except Exception as e:
            self.logger.warning(f"⚠️ Falha ao salvar token no cache: {e}")

    def load_token(self):
        """Carrega token do cache, descartando-o se estiver expirado."""
        if not self.token_file.exists():
            return

        try:
            token = self.token_file.read_text(encoding="utf-8").strip()
        except Exception as e:
            self.logger.warning(f"⚠️ Falha ao ler token do cache: {e}")
            return

        if is_token_valid(token):
            self.token = token
            self.logger.info("📂 Token carregado do cache")
            return

        # Não apagamos o arquivo: ele é sobrescrito no próximo login bem-sucedido.
        claims = decode_jwt_claims(token)
        if claims and "exp" in claims:
            self.logger.info("🕒 Token em cache expirado; será renovado")
        else:
            self.logger.info("🗑️ Token em cache inválido; será renovado")

    async def _extract_token_from_page(
        self, page: Page, strict: bool = True
    ) -> Optional[str]:
        """
        Extrai o token de autenticação da página.

        IMPORTANTE: A API do AdaLove usa **accessToken** do AWS Cognito,
        não o idToken. O idToken resulta em erro 401 — por isso, durante o
        polling (strict=True), apenas o accessToken conta como sucesso.

        Args:
            page: Página do Playwright
            strict: Se True, aceita somente accessToken do Cognito

        Returns:
            Token de acesso ou None
        """
        # Estratégia 1: accessToken do Cognito (único aceito em modo estrito)
        try:
            token = await page.evaluate(
                """
                () => {
                    const key = Object.keys(localStorage).find(k => k.includes('accessToken'));
                    return key ? localStorage.getItem(key) : null;
                }
            """
            )
            if token:
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar accessToken: {e}")

        if strict:
            return None

        # Estratégia 2: qualquer JWT em localStorage (fallback de último recurso)
        try:
            token = await page.evaluate(
                """
                () => {
                    for (let i = 0; i < localStorage.length; i++) {
                        const value = localStorage.getItem(localStorage.key(i));
                        if (value && value.startsWith('eyJ')) return value;
                    }
                    return null;
                }
            """
            )
            if token:
                self.logger.warning("⚠️ Usando token alternativo do localStorage")
                return token
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao buscar token JWT: {e}")

        # Estratégia 3: cookies
        try:
            for cookie in await page.context.cookies():
                name = cookie.get("name", "").lower()
                if ("token" in name or "auth" in name) and len(cookie.get("value", "")) > 100:
                    self.logger.debug(f"✅ Token encontrado no cookie: {name}")
                    return cookie["value"]
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
