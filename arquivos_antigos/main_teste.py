import asyncio
import csv
import time
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Substitua aqui as credenciais
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

async def fazer_login_google(page):
    """
    Função para fazer login no Google de forma mais robusta
    """
    print("Preenchendo email...")
    await page.wait_for_timeout(3000)
    
    # Tenta diferentes seletores para o campo de email
    email_preenchido = False
    seletores_email = [
        "input[type='email']",
        "#identifierId",
        "input[name='identifier']",
        "[data-initial-value]:has([data-initial-dir])"
    ]
    
    for seletor in seletores_email:
        try:
            await expect(page.locator(seletor)).to_be_visible(timeout=10000)
            await page.locator(seletor).click()
            await page.locator(seletor).fill(LOGIN)
            email_preenchido = True
            print(f"Email preenchido usando seletor: {seletor}")
            break
        except:
            continue
    
    if not email_preenchido:
        print("Não foi possível preencher o email automaticamente")
        print("PAUSANDO para preenchimento manual...")
        await page.pause()
        
    # Tenta diferentes textos para o botão Próxima/Next
    botao_clicado = False
    textos_botao = ["Próxima", "Next", "Continue", "Próximo", "Avançar"]
    
    for texto in textos_botao:
        try:
            await page.get_by_role("button", name=texto).click(timeout=5000)
            print(f"Clicou no botão: {texto}")
            botao_clicado = True
            break
        except:
            continue
    
    if not botao_clicado:
        try:
            # Tenta clicar em qualquer botão que pareça ser o próximo passo
            await page.locator("button[type='button']").first.click(timeout=5000)
            print("Clicou no primeiro botão encontrado")
            botao_clicado = True
        except:
            print("Não foi possível clicar no botão automaticamente")
            print("PAUSANDO para click manual...")
            await page.pause()

    # Preenche a senha
    print("Aguardando página de senha...")
    await page.wait_for_timeout(5000)
    
    senha_preenchida = False
    seletores_senha = [
        "input[type='password']",
        "input[name='password']",
        "[aria-label='Digite sua senha']"
    ]
    
    for seletor in seletores_senha:
        try:
            await expect(page.locator(seletor)).to_be_visible(timeout=15000)
            await page.locator(seletor).click()
            await page.locator(seletor).fill(SENHA)
            senha_preenchida = True
            print(f"Senha preenchida usando seletor: {seletor}")
            break
        except:
            continue
    
    if not senha_preenchida:
        print("Não foi possível preencher a senha automaticamente")
        print("PAUSANDO para preenchimento manual...")
        await page.pause()
    
    # Clica no botão final
    botao_final_clicado = False
    for texto in textos_botao:
        try:
            await page.get_by_role("button", name=texto).click(timeout=5000)
            print(f"Clicou no botão final: {texto}")
            botao_final_clicado = True
            break
        except:
            continue
    
    if not botao_final_clicado:
        try:
            await page.locator("button[type='button']").first.click(timeout=5000)
            print("Clicou no primeiro botão para finalizar")
        except:
            print("PAUSANDO para click manual do botão final...")
            await page.pause()

async def selecionar_modulo(page):
    """
    Função para selecionar o Módulo 6
    """
    print("Navegando para seleção de módulos...")
    await page.goto("https://adalove.inteli.edu.br/")
    await page.wait_for_timeout(5000)
    
    # Procura pelo módulo 6 - tenta várias variações do nome
    modulo_encontrado = False
    modulos_para_tentar = [
        "2025-1B-T13",
        "2025-1B-T13 - GRAD ES06 - 2025-1B",
        "Módulo 6",
        "GRAD ES06",
        "ES06",
        "T13"
    ]
    
    for nome_modulo in modulos_para_tentar:
        try:
            print(f"Procurando por módulo: {nome_modulo}")
            await page.get_by_text(nome_modulo).click(timeout=5000)
            print(f"Módulo encontrado e selecionado: {nome_modulo}")
            modulo_encontrado = True
            await page.wait_for_timeout(3000)
            break
        except:
            continue
    
    if not modulo_encontrado:
        print("Não foi possível encontrar o módulo automaticamente.")
        print("PAUSANDO para seleção manual do módulo...")
        print("Por favor:")
        print("1. Selecione manualmente o Módulo 6 (2025-1B-T13) na interface")
        print("2. Aguarde a página carregar completamente")
        print("3. Pressione Enter aqui quando estiver pronto para continuar")
        await page.pause()

async def processar_unidade_simples(context, unidade_nome):
    """
    Versão simplificada para testar se conseguimos acessar as semanas
    """
    page = await context.new_page()
    print(f"Testando acesso a {unidade_nome}...")
    
    try:
        await page.goto("https://adalove.inteli.edu.br/academic-life")
        await page.wait_for_timeout(3000)
        
        # Procura pela semana
        await page.get_by_text(unidade_nome).click(timeout=10000)
        print(f"✅ {unidade_nome} encontrada e acessada")
        
        # Conta quantos cards existem
        await page.wait_for_timeout(2000)
        cards = await page.query_selector_all('[data-rbd-draggable-id]')
        print(f"📋 {len(cards)} cards encontrados na {unidade_nome}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar {unidade_nome}: {str(e)}")
    
    finally:
        await page.close()

async def main():
    """
    Função principal simplificada para testar o acesso
    """
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        print("Acessando AdaLove...")
        await page.goto("https://adalove.inteli.edu.br/")
        
        print("Clicando em 'Entrar com o Google'...")
        await page.get_by_role("button", name="Entrar com o Google").click()

        # Faz login
        await fazer_login_google(page)

        # Aguarda o login concluir
        print("Aguardando login finalizar...")
        await page.wait_for_timeout(8000)
        
        # Seleciona o módulo
        await selecionar_modulo(page)
        
        # Testa acesso a algumas semanas primeiro
        print("Testando acesso às semanas...")
        semanas_teste = ["Semana 01", "Semana 02", "Semana 03"]
        
        for semana in semanas_teste:
            await processar_unidade_simples(context, semana)
        
        print("Teste concluído!")
        print("Se as semanas foram acessadas com sucesso, podemos prosseguir com a extração completa.")
        
        # Pausa para verificação
        print("PAUSANDO para verificação...")
        print("Pressione Enter se quiser continuar com a extração completa dos dados")
        await page.pause()

        await context.close()
        await browser.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Teste concluído em {elapsed_time:.2f} segundos.")

# Executa o script de teste
asyncio.run(main())
