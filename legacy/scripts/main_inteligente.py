import asyncio
import csv
import time
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

async def fazer_login_inteligente(page):
    """
    Função inteligente que detecta o tipo de login necessário
    """
    print("🔑 Iniciando processo de login inteligente...")
    
    # Clica no botão "Entrar com o Google"
    print("🔑 Clicando em 'Entrar com o Google'...")
    await page.get_by_role("button", name="Entrar com o Google").click()
    
    # Aguarda 5 segundos para ver onde foi parar
    await page.wait_for_timeout(5000)
    
    current_url = page.url
    print(f"📍 URL após click: {current_url}")
    
    # Analisa onde estamos após o click
    if "accounts.google.com" in current_url:
        print("🌐 Redirecionado para Google - fazendo login completo...")
        return await fazer_login_google_completo(page)
        
    elif "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
        print("✅ Login automático bem-sucedido - já estava logado no Google!")
        return True
        
    else:
        print("❓ Situação inesperada - aguardando...")
        # Aguarda mais um pouco para ver se algo acontece
        await page.wait_for_timeout(10000)
        
        current_url = page.url
        print(f"📍 URL após espera adicional: {current_url}")
        
        if "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
            print("✅ Login concluído após espera!")
            return True
        else:
            print("❌ Login não foi concluído automaticamente")
            return False

async def fazer_login_google_completo(page):
    """
    Faz o login completo no Google (email + senha)
    """
    print("📧 Preenchendo email...")
    
    # Aguarda e preenche email
    try:
        # Tenta diferentes seletores para o campo de email
        seletores_email = ["input[type='email']", "#identifierId", "input[name='identifier']"]
        
        email_preenchido = False
        for seletor in seletores_email:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=10000)
                await page.locator(seletor).fill(LOGIN)
                email_preenchido = True
                print(f"✅ Email preenchido com: {seletor}")
                break
            except:
                continue
                
        if not email_preenchido:
            print("❌ Não conseguiu preencher email automaticamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher email: {e}")
        return False
    
    # Clica no botão Próxima/Next
    print("➡️ Clicando em Próxima...")
    try:
        botoes_proxima = ["Próxima", "Next", "Continue", "Continuar"]
        
        botao_clicado = False
        for texto_botao in botoes_proxima:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                print(f"✅ Clicou em: {texto_botao}")
                botao_clicado = True
                break
            except:
                continue
                
        if not botao_clicado:
            print("❌ Não conseguiu clicar em Próxima")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao clicar em Próxima: {e}")
        return False
    
    # Aguarda página de senha
    print("🔐 Aguardando página de senha...")
    await page.wait_for_timeout(5000)
    
    # Preenche senha
    print("🔐 Preenchendo senha...")
    try:
        seletores_senha = ["input[type='password']", "input[name='password']"]
        
        senha_preenchida = False
        for seletor in seletores_senha:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=15000)
                await page.locator(seletor).fill(SENHA)
                senha_preenchida = True
                print(f"✅ Senha preenchida com: {seletor}")
                break
            except:
                continue
                
        if not senha_preenchida:
            print("❌ Não conseguiu preencher senha automaticamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher senha: {e}")
        return False
    
    # Clica no botão final
    print("🎯 Finalizando login...")
    try:
        botoes_final = ["Próxima", "Next", "Sign in", "Entrar", "Login"]
        
        for texto_botao in botoes_final:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                print(f"✅ Clicou em botão final: {texto_botao}")
                break
            except:
                continue
                
    except Exception as e:
        print(f"❌ Erro no botão final: {e}")
        return False
    
    # Aguarda redirecionamento para AdaLove
    print("⏳ Aguardando redirecionamento para AdaLove...")
    for i in range(30):  # 30 segundos no máximo
        await page.wait_for_timeout(1000)
        current_url = page.url
        
        if "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
            print("✅ Login Google completo - redirecionado para AdaLove!")
            return True
            
    print("❌ Timeout aguardando redirecionamento")
    return False

async def selecionar_modulo_6(page):
    """
    Seleciona o Módulo 6 com várias tentativas
    """
    print("🎯 Procurando Módulo 6...")
    
    # Garante que está na página inicial
    current_url = page.url
    if not current_url.endswith("adalove.inteli.edu.br/") and "academic-life" not in current_url:
        print("🏠 Navegando para página inicial...")
        await page.goto("https://adalove.inteli.edu.br/")
        await page.wait_for_timeout(3000)
    
    # Lista de nomes possíveis para o módulo 6
    nomes_modulo = [
        "2025-1B-T13",
        "2025-1B-T13 - GRAD ES06 - 2025-1B",
        "GRAD ES06 - 2025-1B", 
        "GRAD ES06",
        "ES06",
        "T13",
        "Módulo 6"
    ]
    
    print("🔍 Tentando encontrar módulo automaticamente...")
    
    for nome in nomes_modulo:
        try:
            print(f"   🔍 Buscando: {nome}")
            
            # Procura elemento com texto exato
            elemento = page.get_by_text(nome, exact=True)
            if await elemento.count() > 0:
                await elemento.first.click(timeout=5000)
                print(f"✅ Módulo selecionado: {nome}")
                await page.wait_for_timeout(3000)
                return True
            
            # Procura elemento com texto parcial
            elemento_parcial = page.get_by_text(nome, exact=False)
            if await elemento_parcial.count() > 0:
                await elemento_parcial.first.click(timeout=5000)
                print(f"✅ Módulo selecionado (parcial): {nome}")
                await page.wait_for_timeout(3000)
                return True
                
        except:
            continue
    
    print("❌ Módulo não encontrado automaticamente")
    return False

async def testar_acesso_semanas(context):
    """
    Testa acesso às primeiras 3 semanas
    """
    print("🧪 Testando acesso às semanas...")
    
    semanas = ["Semana 01", "Semana 02", "Semana 03"]
    resultados = []
    
    for semana in semanas:
        page = await context.new_page()
        try:
            print(f"   🔍 Testando: {semana}")
            
            await page.goto("https://adalove.inteli.edu.br/academic-life")
            await page.wait_for_timeout(3000)
            
            # Procura pela semana
            elemento = page.get_by_text(semana, exact=False)
            if await elemento.count() > 0:
                await elemento.first.click(timeout=8000)
                await page.wait_for_timeout(3000)
                
                # Conta cards
                cards = await page.query_selector_all('[data-rbd-draggable-id]')
                print(f"   ✅ {semana}: {len(cards)} cards encontrados")
                resultados.append({"semana": semana, "cards": len(cards), "sucesso": True})
            else:
                print(f"   ❌ {semana}: não encontrada")
                resultados.append({"semana": semana, "cards": 0, "sucesso": False})
                
        except Exception as e:
            print(f"   ❌ {semana}: erro - {str(e)[:50]}")
            resultados.append({"semana": semana, "cards": 0, "sucesso": False})
        finally:
            await page.close()
    
    # Resumo dos resultados
    sucessos = sum(1 for r in resultados if r["sucesso"])
    total_cards = sum(r["cards"] for r in resultados)
    
    print(f"\n📊 Resultado: {sucessos}/3 semanas acessadas, {total_cards} cards total")
    
    return sucessos > 0

async def main():
    """
    Função principal inteligente
    """
    print("🚀 Iniciando extração inteligente do AdaLove...")
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Acessa AdaLove
        print("🌐 Acessando AdaLove...")
        await page.goto("https://adalove.inteli.edu.br/")
        await page.wait_for_timeout(3000)
        
        # 2. Faz login inteligente
        login_sucesso = await fazer_login_inteligente(page)
        
        if not login_sucesso:
            print("❌ Falha no login automático")
            print("🤚 PAUSANDO para login manual...")
            print("   👆 Faça login manualmente no navegador")
            print("   ⏸️  Pressione Enter quando terminar")
            await page.pause()
        
        # 3. Seleciona módulo 6
        modulo_sucesso = await selecionar_modulo_6(page)
        
        if not modulo_sucesso:
            print("🤚 PAUSANDO para seleção manual do módulo...")
            print("   👆 Selecione o Módulo 6 (2025-1B-T13) manualmente")
            print("   ⏸️  Pressione Enter quando terminar")
            await page.pause()
        
        # 4. Testa acesso às semanas
        teste_sucesso = await testar_acesso_semanas(context)
        
        if teste_sucesso:
            print("✅ Teste bem-sucedido!")
            print("🚀 Pronto para extração completa de todas as 10 semanas")
            print("⏸️  Pressione Enter para continuar com extração completa...")
            await page.pause()
        else:
            print("❌ Teste falhou - verifique se módulo correto foi selecionado")
            print("⏸️  Pressione Enter para sair...")
            await page.pause()

        await context.close()
        await browser.close()

    end_time = time.time()
    print(f"⏱️  Concluído em {end_time - start_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
