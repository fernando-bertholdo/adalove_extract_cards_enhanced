"""
Valida os seletores da tela de login do Google contra a página real.

Motivo: o auto-preenchimento usava `input[type='email']`, seletor que casa com
ZERO elementos na tela atual do Google (o campo é `input[type=text]#identifierId`).
Nenhum teste cobria seletores, então a falha só aparecia em execução real — e
como `fill()` apenas estoura timeout, o sintoma era "o campo fica vazio", sem
qualquer pista da causa.

Estes testes usam rede e browser real, e por isso ficam fora da suíte padrão.

    pytest -m rede tests/test_google_selectors.py
"""

import pytest

from adalove_extractor.api.auth import (
    EMAIL_SELECTORS,
    NEXT_BUTTON_RE,
    PASSWORD_SELECTORS,
)

GOOGLE_IDENTIFIER_URL = (
    "https://accounts.google.com/v3/signin/identifier?flowName=GlifWebSignIn"
)

pytestmark = pytest.mark.rede


@pytest.fixture
async def google_page(tmp_path):
    """Abre a tela de identificação do Google. Nenhuma credencial é usada."""
    playwright = pytest.importorskip("playwright.async_api")

    async with playwright.async_playwright() as p:
        try:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(tmp_path / "profile"),
                channel="chrome",
                headless=True,
                locale="pt-BR",
            )
        except Exception:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=str(tmp_path / "profile"),
                headless=True,
                locale="pt-BR",
            )

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.goto(GOOGLE_IDENTIFIER_URL, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)
            yield page
        finally:
            await ctx.close()


async def test_algum_seletor_de_email_e_editavel(google_page):
    """Ao menos um candidato precisa resolver para um campo preenchível.

    É exatamente esta asserção que falharia hoje se a lista contivesse só
    `input[type='email']`.
    """
    editaveis = []
    for selector in EMAIL_SELECTORS:
        try:
            if await google_page.locator(selector).count():
                if await google_page.locator(selector).first.is_editable(timeout=1500):
                    editaveis.append(selector)
        except Exception:
            continue

    assert editaveis, (
        f"Nenhum seletor de e-mail funciona na tela atual do Google. "
        f"Testados: {EMAIL_SELECTORS}. O Google provavelmente mudou o layout."
    )


async def test_botao_de_avanco_e_reconhecido(google_page):
    """O rótulo do botão varia com o idioma detectado por IP (aqui: 'Avançar')."""
    rotulos = await google_page.evaluate(
        """
        () => [...document.querySelectorAll('button')]
            .filter(b => b.getBoundingClientRect().width > 0)
            .map(b => (b.innerText || '').trim())
            .filter(Boolean)
        """
    )

    assert any(NEXT_BUTTON_RE.match(r) for r in rotulos), (
        f"NEXT_BUTTON_RE não reconhece nenhum botão visível. Rótulos: {rotulos}. "
        f"Há fallback para a tecla Enter, mas o regex deveria cobrir este idioma."
    )


def test_listas_de_seletores_nao_estao_vazias():
    """Guarda barata: uma lista vazia desabilitaria o preenchimento em silêncio."""
    assert EMAIL_SELECTORS, "EMAIL_SELECTORS vazio"
    assert PASSWORD_SELECTORS, "PASSWORD_SELECTORS vazio"
