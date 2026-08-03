"""
Testes da lógica pura de autenticação.

Cobre as duas decisões que derrubavam o fluxo de login no Windows:
1. Validade do token em cache (era aceito mesmo expirado)
2. Classificação do estado da tela de login do Google
   (a tela normal de senha era confundida com "senha incorreta")
"""

import base64
import json
import time

import pytest

from adalove_extractor.api.auth import (
    LoginState,
    classify_login_state,
    decode_jwt_claims,
    is_token_valid,
)


def make_jwt(exp_offset_seconds: int) -> str:
    """Cria um JWT sintético que expira em `exp_offset_seconds` a partir de agora.

    Args:
        exp_offset_seconds: Segundos até a expiração (negativo = já expirado)

    Returns:
        String JWT com assinatura fake (não é validada localmente)
    """

    def b64(data: dict) -> str:
        raw = json.dumps(data).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    header = b64({"alg": "RS256", "typ": "JWT"})
    payload = b64({"exp": int(time.time()) + exp_offset_seconds, "token_use": "access"})
    return f"{header}.{payload}.fake-signature"


class TestIsTokenValid:
    """Token em cache só pode ser reaproveitado se ainda estiver vivo."""

    def test_rejects_none(self):
        assert is_token_valid(None) is False

    def test_rejects_empty_string(self):
        assert is_token_valid("") is False

    def test_rejects_non_jwt_string(self):
        # O bug original: qualquer string com len > 20 era aceita
        assert is_token_valid("x" * 50) is False

    def test_rejects_malformed_payload(self):
        assert is_token_valid("eyJhbGciOiJSUzI1NiJ9.###nao-e-base64###.sig") is False

    def test_rejects_expired_token(self):
        # Cenário real: .token_cache do repositório venceu e foi aceito mesmo assim
        assert is_token_valid(make_jwt(-3600)) is False

    def test_accepts_valid_token(self):
        assert is_token_valid(make_jwt(3600)) is True

    def test_rejects_token_inside_safety_margin(self):
        # Expira em 30s: não vale a pena começar uma extração com ele
        assert is_token_valid(make_jwt(30), skew_seconds=120) is False

    def test_accepts_token_beyond_safety_margin(self):
        assert is_token_valid(make_jwt(300), skew_seconds=120) is True

    def test_rejects_token_without_exp_claim(self):
        def b64(data: dict) -> str:
            return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

        sem_exp = f"{b64({'alg': 'RS256'})}.{b64({'sub': 'abc'})}.sig"
        assert is_token_valid(sem_exp) is False


class TestDecodeJwtClaims:
    """Decodificação de claims não pode explodir com entrada inválida."""

    def test_returns_claims_for_valid_jwt(self):
        claims = decode_jwt_claims(make_jwt(60))
        assert claims is not None
        assert "exp" in claims

    def test_returns_none_for_garbage(self):
        assert decode_jwt_claims("nao-e-um-jwt") is None

    def test_returns_none_for_none(self):
        assert decode_jwt_claims(None) is None


class TestClassifyLoginState:
    """Classificação da tela atual do fluxo OAuth."""

    def test_password_screen_is_not_wrong_password(self):
        """REGRESSÃO: a URL da tela normal de senha É challenge/pwd.

        O código antigo tratava essa URL como prova de senha incorreta e
        matava o browser assim que o usuário chegava na tela para digitar.
        """
        url = "https://accounts.google.com/v3/signin/challenge/pwd?flowName=GlifWebSignIn"
        assert classify_login_state(url, "<html>Digite sua senha</html>") == LoginState.GOOGLE_PASSWORD

    def test_wrong_password_needs_explicit_error_in_content(self):
        url = "https://accounts.google.com/v3/signin/challenge/pwd?flowName=GlifWebSignIn"
        content = "<html>Wrong password. Try again or click Forgot password.</html>"
        assert classify_login_state(url, content) == LoginState.WRONG_PASSWORD

    def test_wrong_password_detects_portuguese_error(self):
        url = "https://accounts.google.com/v3/signin/challenge/pwd"
        assert classify_login_state(url, "<html>Senha incorreta</html>") == LoginState.WRONG_PASSWORD

    def test_rejected_signin_is_wrong_password(self):
        assert classify_login_state("https://accounts.google.com/signin/rejected", "") == LoginState.WRONG_PASSWORD

    def test_email_screen(self):
        url = "https://accounts.google.com/v3/signin/identifier?flowName=GlifWebSignIn"
        assert classify_login_state(url, "") == LoginState.GOOGLE_EMAIL

    @pytest.mark.parametrize(
        "path",
        [
            "/v3/signin/challenge/totp/1",   # app autenticador
            "/v3/signin/challenge/selection",  # escolher método
            "/v3/signin/challenge/ipp/1",    # SMS
            "/v3/signin/challenge/az",       # Google prompt no celular
            "/v3/signin/challenge/dp",       # device prompt
        ],
    )
    def test_2fa_challenges(self, path):
        assert classify_login_state(f"https://accounts.google.com{path}", "") == LoginState.GOOGLE_2FA

    def test_adalove_authenticated_page(self):
        url = "https://adalove.inteli.edu.br/desenvolvimento"
        assert classify_login_state(url, "") == LoginState.ADALOVE_READY

    def test_adalove_login_page_is_not_ready(self):
        assert classify_login_state("https://adalove.inteli.edu.br/login", "") != LoginState.ADALOVE_READY

    @pytest.mark.parametrize(
        "url",
        [
            "https://adalove.inteli.edu.br",
            "https://adalove.inteli.edu.br/",
            "https://adalove.inteli.edu.br/?redirect=1",
            "https://adalove.inteli.edu.br/#/",
        ],
    )
    def test_adalove_root_is_not_ready(self, url):
        """REGRESSÃO: a raiz renderiza a tela de login e não traz '/login' na URL.

        Tratá-la como autenticada fazia o auto-preenchimento concluir que
        não havia nada a fazer e retornar sem sequer clicar em "Entrar com
        o Google" — a janela ficava parada na tela de login até o timeout.
        """
        assert classify_login_state(url, "") != LoginState.ADALOVE_READY

    def test_cognito_redirect_is_unknown(self):
        url = "https://adalove.auth.us-east-2.amazoncognito.com/oauth2/authorize?client_id=x"
        assert classify_login_state(url, "") == LoginState.UNKNOWN

    def test_content_is_optional(self):
        # Chamadas sem conteúdo não podem quebrar (page.content() pode falhar durante navegação)
        assert classify_login_state("https://accounts.google.com/v3/signin/identifier") == LoginState.GOOGLE_EMAIL

    def test_browser_blocked_by_google(self):
        """Google recusa Chromium automatizado — precisa ser distinguível de senha errada."""
        url = "https://accounts.google.com/v3/signin/identifier"
        content = "<html>Couldn't sign you in. This browser or app may not be secure.</html>"
        assert classify_login_state(url, content) == LoginState.BROWSER_BLOCKED

    def test_browser_blocked_takes_precedence_over_password_screen(self):
        url = "https://accounts.google.com/v3/signin/challenge/pwd"
        content = "<html>Este navegador ou app pode não ser seguro</html>"
        assert classify_login_state(url, content) == LoginState.BROWSER_BLOCKED
