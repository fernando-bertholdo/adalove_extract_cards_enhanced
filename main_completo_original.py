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
    
    # Aguarda 4 segundos para ver onde foi parar
    await page.wait_for_timeout(4000)
    
    current_url = page.url
    print(f"📍 URL após click: {current_url}")
    
    # Analisa onde estamos após o click
    if "accounts.google.com" in current_url:
        print("🌐 Redirecionado para Google - fazendo login completo...")
        return await fazer_login_google_completo(page)
        
    elif "adalove.inteli.edu.br" in current_url and "/feed" in current_url:
        print("✅ Login automático bem-sucedido - chegou no feed!")
        return True
        
    elif "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
        print("✅ Login automático bem-sucedido - já estava na plataforma!")
        return True
        
    else:
        print("❓ Aguardando conclusão do login...")
        # Aguarda mais tempo para ver se vai para o feed
        await page.wait_for_timeout(10000)
        
        current_url = page.url
        print(f"📍 URL após espera: {current_url}")
        
        if "adalove.inteli.edu.br" in current_url and ("feed" in current_url or "/login" not in current_url):
            print("✅ Login concluído!")
            return True
        else:
            print("❌ Login não foi concluído")
            return False

async def fazer_login_google_completo(page):
    """
    Faz o login completo no Google (email + senha)
    """
    print("📧 Preenchendo email...")
    
    try:
        # Aguarda e preenche email
        seletores_email = ["input[type='email']", "#identifierId", "input[name='identifier']"]
        
        email_preenchido = False
        for seletor in seletores_email:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=10000)
                await page.locator(seletor).fill(LOGIN)
                email_preenchido = True
                print(f"✅ Email preenchido")
                break
            except:
                continue
                
        if not email_preenchido:
            print("❌ Não conseguiu preencher email")
            return False
            
        # Clica Próxima
        print("➡️ Clicando em Próxima...")
        botoes_proxima = ["Próxima", "Next", "Continue"]
        
        for texto_botao in botoes_proxima:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                print(f"✅ Clicou em: {texto_botao}")
                break
            except:
                continue
        
        # Aguarda página de senha
        await page.wait_for_timeout(5000)
        
        # Preenche senha
        print("🔐 Preenchendo senha...")
        seletores_senha = ["input[type='password']", "input[name='password']"]
        
        senha_preenchida = False
        for seletor in seletores_senha:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=15000)
                await page.locator(seletor).fill(SENHA)
                senha_preenchida = True
                print(f"✅ Senha preenchida")
                break
            except:
                continue
                
        if not senha_preenchida:
            print("❌ Não conseguiu preencher senha")
            return False
        
        # Clica botão final
        print("🎯 Finalizando login...")
        for texto_botao in botoes_proxima:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                break
            except:
                continue
        
        # Aguarda redirecionamento para AdaLove
        print("⏳ Aguardando redirecionamento...")
        for i in range(30):
            await page.wait_for_timeout(1000)
            current_url = page.url
            
            if "adalove.inteli.edu.br" in current_url and ("feed" in current_url or "/login" not in current_url):
                print("✅ Login Google completo!")
                return True
                
        print("❌ Timeout no redirecionamento")
        return False
        
    except Exception as e:
        print(f"❌ Erro no login Google: {e}")
        return False

async def navegar_para_feed(page):
    """
    Garante que está na página de feed
    """
    current_url = page.url
    print(f"📍 URL atual: {current_url}")
    
    if "/feed" not in current_url:
        print("🏠 Navegando para feed...")
        await page.goto("https://adalove.inteli.edu.br/feed")
        await page.wait_for_timeout(3000)

async def listar_e_selecionar_modulo(page):
    """
    Lista módulos disponíveis e seleciona o Módulo 6
    """
    print("📋 Listando módulos disponíveis...")
    
    # Aguarda a página carregar
    await page.wait_for_timeout(3000)
    
    # Múltiplos seletores para o dropdown
    seletores_dropdown = [
        ".MuiFormControl-root.MuiFormControl-fullWidth",
        ".css-165oggv",
        ".MuiInputBase-root.MuiOutlinedInput-root",
        ".css-3joqfb",
        "[role='combobox']",
        "select",
        ".MuiSelect-root"
    ]
    
    dropdown_encontrado = False
    
    for seletor in seletores_dropdown:
        try:
            print(f"   🔍 Tentando seletor: {seletor}")
            dropdown = page.locator(seletor).first
            
            if await dropdown.is_visible(timeout=5000):
                print(f"   ✅ Dropdown encontrado: {seletor}")
                await dropdown.click()
                dropdown_encontrado = True
                break
                
        except:
            continue
    
    if not dropdown_encontrado:
        print("❌ Dropdown não encontrado com seletores automáticos")
        print("🤚 PAUSANDO para seleção manual...")
        print("   👆 Abra o dropdown de módulos manualmente")
        print("   ⏸️  Pressione Enter após abrir o dropdown")
        await page.pause()
    
    # Aguarda opções do dropdown aparecerem
    await page.wait_for_timeout(2000)
    
    # Tenta listar as opções disponíveis
    print("📋 Opções de módulos encontradas:")
    
    seletores_opcoes = [
        ".MuiMenuItem-root",
        "[role='option']", 
        ".MuiList-root li",
        "option",
        ".dropdown-item"
    ]
    
    opcoes_encontradas = []
    
    for seletor in seletores_opcoes:
        try:
            opcoes = page.locator(seletor)
            count = await opcoes.count()
            
            if count > 0:
                print(f"   ✅ {count} opções encontradas com {seletor}")
                
                # Lista cada opção
                for i in range(count):
                    try:
                        texto = await opcoes.nth(i).text_content()
                        if texto and len(texto.strip()) > 0:
                            opcoes_encontradas.append(texto.strip())
                            print(f"      {i+1}. {texto.strip()}")
                    except:
                        pass
                break
                
        except:
            continue
    
    if not opcoes_encontradas:
        print("❌ Não foi possível listar opções automaticamente")
        print("🤚 PAUSANDO para seleção manual do módulo...")
        print("   👆 Selecione o Módulo 6 manualmente no dropdown")
        print("   📋 Procure por: '2025-1B-T13' ou 'GRAD ES06' ou similar")
        print("   ⏸️  Pressione Enter após selecionar")
        await page.pause()
        return True
    
    # Procura pelo módulo 6
    nomes_modulo6 = [
        "2025-1B-T13",
        "2025-1B-T13 - GRAD ES06 - 2025-1B",
        "GRAD ES06 - 2025-1B",
        "GRAD ES06", 
        "ES06",
        "T13"
    ]
    
    modulo_selecionado = False
    
    print("🎯 Procurando Módulo 6...")
    for nome_procurado in nomes_modulo6:
        for opcao in opcoes_encontradas:
            if nome_procurado.lower() in opcao.lower():
                print(f"   ✅ Módulo 6 encontrado: {opcao}")
                
                # Tenta clicar na opção
                try:
                    await page.get_by_text(opcao, exact=True).click(timeout=5000)
                    modulo_selecionado = True
                    print("   ✅ Módulo 6 selecionado!")
                    break
                except:
                    try:
                        await page.get_by_text(opcao, exact=False).click(timeout=5000)
                        modulo_selecionado = True
                        print("   ✅ Módulo 6 selecionado (busca parcial)!")
                        break
                    except:
                        continue
        
        if modulo_selecionado:
            break
    
    if not modulo_selecionado:
        print("❌ Módulo 6 não encontrado automaticamente")
        print("🤚 PAUSANDO para seleção manual...")
        print("   👆 Selecione o Módulo 6 manualmente")
        print("   ⏸️  Pressione Enter após selecionar")
        await page.pause()
    
    return True

async def clicar_ir_para_turma(page):
    """
    Clica no botão 'Ir para a turma'
    """
    print("🎯 Procurando botão 'Ir para a turma'...")
    
    # Múltiplas formas de encontrar o botão
    seletores_botao = [
        "button:has-text('Ir para a turma')",
        ".button-go-to-the-class",
        ".MuiButton-root:has-text('Ir para a turma')",
        "[class*='button-go-to-the-class']"
    ]
    
    for seletor in seletores_botao:
        try:
            botao = page.locator(seletor)
            if await botao.is_visible(timeout=5000):
                await botao.click()
                print("✅ Clicou em 'Ir para a turma'")
                return True
        except:
            continue
    
    print("❌ Botão não encontrado automaticamente")
    print("🤚 PAUSANDO para click manual...")
    print("   👆 Clique no botão 'Ir para a turma'") 
    print("   ⏸️  Pressione Enter após clicar")
    await page.pause()
    return True

async def fechar_popup_faltas(page):
    """
    Fecha o popup de faltas se aparecer
    """
    print("🚫 Verificando popup de faltas...")
    
    await page.wait_for_timeout(3000)  # Aguarda popup aparecer
    
    # Procura pelo botão "Fechar"
    seletores_fechar = [
        "button:has-text('Fechar')",
        "[aria-label='Fechar']",
        ".MuiButton-root:has-text('Fechar')",
        "[role='button']:has-text('Fechar')",
        ".close-button",
        ".popup-close"
    ]
    
    popup_fechado = False
    
    for seletor in seletores_fechar:
        try:
            botao_fechar = page.locator(seletor)
            if await botao_fechar.is_visible(timeout=3000):
                await botao_fechar.click()
                print("✅ Popup de faltas fechado")
                popup_fechado = True
                break
        except:
            continue
    
    if not popup_fechado:
        print("ℹ️  Nenhum popup de faltas detectado")
    
    await page.wait_for_timeout(2000)  # Aguarda popup fechar

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
            
            # Fecha popup de faltas se aparecer nesta página também
            await fechar_popup_faltas(page)
            
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
    Função principal com fluxo completo
    """
    print("🚀 Iniciando extração completa do Módulo 6...")
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Acessa AdaLove
            print("🌐 Acessando AdaLove...")
            await page.goto("https://adalove.inteli.edu.br/")
            await page.wait_for_timeout(3000)
            
            # 2. Faz login inteligente
            login_sucesso = await fazer_login_inteligente(page)
            
            if not login_sucesso:
                print("❌ Falha no login automático")
                print("🤚 PAUSANDO para login manual...")
                await page.pause()
            
            # 3. Navega para feed se necessário
            await navegar_para_feed(page)
            
            # 4. Lista e seleciona módulo 6
            await listar_e_selecionar_modulo(page)
            
            # 5. Clica "Ir para a turma"
            await clicar_ir_para_turma(page)
            
            # 6. Aguarda chegar no academic-life
            await page.wait_for_timeout(3000)
            
            # 7. Fecha popup de faltas
            await fechar_popup_faltas(page)
            
            # 8. Testa acesso às semanas
            teste_sucesso = await testar_acesso_semanas(context)
            
            if teste_sucesso:
                print("🎉 SUCESSO! Módulo 6 configurado corretamente!")
                print("✅ Pronto para extração completa de todas as 10 semanas")
                print("⏸️  Pressione Enter para continuar com extração completa...")
                await page.pause()
            else:
                print("❌ Teste falhou - verificar configuração")
                print("⏸️  Pressione Enter para sair...")
                await page.pause()
        
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            print("⏸️  Pressione Enter para sair...")
            await page.pause()
            
        finally:
            await context.close()
            await browser.close()

    end_time = time.time()
    print(f"⏱️  Concluído em {end_time - start_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
