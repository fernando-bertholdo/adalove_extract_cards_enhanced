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
        botoes_proxima = ["Next", "Próxima", "Continue"]
        
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

async def debug_pagina_completa(page):
    """
    Debug completo da página para entender a estrutura
    """
    print("🔍 === DEBUG COMPLETO DA PÁGINA ===")
    
    # 1. Informações básicas
    print(f"📍 URL: {page.url}")
    print(f"📄 Título: {await page.title()}")
    
    # 2. Procura por seletores relacionados ao dropdown
    print("\n🔍 Procurando seletores de dropdown:")
    
    seletores_debug = [
        "div[role='combobox']",
        ".MuiSelect-select", 
        ".MuiFormControl-root",
        ".css-165oggv",
        ".css-3joqfb",
        "[aria-haspopup='listbox']",
        "div:has-text('2025-1B-T13')"
    ]
    
    for seletor in seletores_debug:
        try:
            elementos = page.locator(seletor)
            count = await elementos.count()
            if count > 0:
                print(f"   ✅ {seletor}: {count} elemento(s)")
                
                # Se encontrou elementos, tenta pegar texto
                for i in range(min(count, 3)):  # Máximo 3 elementos
                    try:
                        texto = await elementos.nth(i).text_content()
                        if texto and len(texto.strip()) > 0:
                            print(f"      📝 Texto {i+1}: '{texto.strip()}'")
                    except:
                        print(f"      ❌ Não conseguiu ler texto do elemento {i+1}")
            else:
                print(f"   ❌ {seletor}: não encontrado")
        except Exception as e:
            print(f"   ❌ {seletor}: erro - {str(e)[:50]}")
    
    # 3. Procura especificamente por texto "2025-1B-T13"
    print("\n🎯 Procurando especificamente por '2025-1B-T13':")
    try:
        elementos_texto = page.get_by_text("2025-1B-T13", exact=False)
        count = await elementos_texto.count()
        print(f"   📋 Encontrados {count} elementos com '2025-1B-T13'")
        
        for i in range(count):
            try:
                elemento = elementos_texto.nth(i)
                texto = await elemento.text_content()
                visivel = await elemento.is_visible()
                print(f"      {i+1}. Texto: '{texto}' | Visível: {visivel}")
            except:
                print(f"      {i+1}. Erro ao ler elemento")
                
    except Exception as e:
        print(f"   ❌ Erro na busca por texto: {e}")
    
    print("\n🔍 === FIM DO DEBUG ===\n")

async def clicar_dropdown_com_debug(page):
    """
    Tenta clicar no dropdown com debug detalhado
    """
    print("🎯 Tentando clicar no dropdown com debug...")
    
    # Primeiro faz debug
    await debug_pagina_completa(page)
    
    # Agora tenta clicar especificamente no elemento com "2025-1B-T13"
    print("🎯 Tentativa 1: Clicando diretamente no texto '2025-1B-T13'")
    try:
        elemento_texto = page.get_by_text("2025-1B-T13", exact=False)
        if await elemento_texto.count() > 0:
            await elemento_texto.first.click()
            print("✅ Clicou no elemento com texto '2025-1B-T13'")
            await page.wait_for_timeout(3000)  # Aguarda dropdown abrir
            return True
    except Exception as e:
        print(f"❌ Erro na tentativa 1: {e}")
    
    # Tentativa 2: Combobox
    print("🎯 Tentativa 2: Clicando em div[role='combobox']")
    try:
        combobox = page.locator("div[role='combobox']")
        if await combobox.count() > 0:
            await combobox.first.click()
            print("✅ Clicou no combobox")
            await page.wait_for_timeout(3000)
            return True
    except Exception as e:
        print(f"❌ Erro na tentativa 2: {e}")
    
    # Tentativa 3: Seletores MUI
    print("🎯 Tentativa 3: Seletores Material-UI")
    seletores_mui = [
        ".MuiFormControl-root .MuiInputBase-root",
        ".css-165oggv",
        ".css-3joqfb"
    ]
    
    for seletor in seletores_mui:
        try:
            elemento = page.locator(seletor)
            if await elemento.count() > 0:
                await elemento.first.click()
                print(f"✅ Clicou usando {seletor}")
                await page.wait_for_timeout(3000)
                return True
        except Exception as e:
            print(f"❌ Erro com {seletor}: {e}")
    
    print("❌ Todas as tentativas falharam")
    return False

async def listar_opcoes_com_debug(page):
    """
    Lista opções com debug detalhado
    """
    print("📋 === LISTANDO OPÇÕES COM DEBUG ===")
    
    # Aguarda mais tempo para as opções aparecerem
    print("⏳ Aguardando opções carregarem...")
    await page.wait_for_timeout(5000)
    
    # Debug dos elementos li (opções)
    print("🔍 Procurando elementos <li> (opções):")
    
    seletores_li = [
        "li[role='option']",
        ".MuiMenuItem-root",
        ".css-duonqd",
        "li.MuiButtonBase-root.MuiMenuItem-root", 
        ".MuiList-root li"
    ]
    
    opcoes_encontradas = []
    
    for seletor in seletores_li:
        try:
            elementos = page.locator(seletor)
            count = await elementos.count()
            print(f"   🔍 {seletor}: {count} elemento(s)")
            
            if count > 0:
                for i in range(count):
                    try:
                        elemento = elementos.nth(i)
                        texto = await elemento.text_content()
                        visivel = await elemento.is_visible()
                        
                        if texto and len(texto.strip()) > 0:
                            opcoes_encontradas.append(texto.strip())
                            print(f"      {i+1}. '{texto.strip()}' (Visível: {visivel})")
                    except:
                        print(f"      {i+1}. Erro ao ler")
                
                if opcoes_encontradas:
                    break  # Se encontrou opções, para aqui
                    
        except Exception as e:
            print(f"   ❌ {seletor}: erro - {str(e)[:50]}")
    
    print(f"\n📊 Total de opções encontradas: {len(opcoes_encontradas)}")
    
    if not opcoes_encontradas:
        print("🔍 Tentando buscar qualquer elemento com texto...")
        try:
            # Busca por qualquer elemento visível com texto
            todos_elementos = page.locator("*:visible")
            count = await todos_elementos.count()
            print(f"   📋 {count} elementos visíveis na página")
            
            # Procura por elementos que contenham anos (2022, 2024, 2025)
            anos = ["2022", "2024", "2025"]
            for ano in anos:
                elementos_ano = page.get_by_text(ano, exact=False)
                count_ano = await elementos_ano.count()
                if count_ano > 0:
                    print(f"   📅 {count_ano} elementos contendo '{ano}'")
                    
                    # Lista alguns desses elementos
                    for i in range(min(count_ano, 5)):
                        try:
                            texto = await elementos_ano.nth(i).text_content()
                            if texto and len(texto.strip()) > 0:
                                opcoes_encontradas.append(texto.strip())
                                print(f"      - {texto.strip()}")
                        except:
                            pass
                            
        except Exception as e:
            print(f"   ❌ Erro na busca geral: {e}")
    
    print("📋 === FIM DA LISTAGEM COM DEBUG ===\n")
    return opcoes_encontradas

def aguardar_usuario():
    """
    Aguarda o usuário pressionar Enter
    """
    try:
        input()
        return True
    except:
        return True

async def main():
    """
    Função principal com debug completo
    """
    print("🚀 Iniciando com DEBUG COMPLETO...")
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
                print("🤚 Faça login manualmente e pressione Enter:")
                aguardar_usuario()
            
            # 3. Navega para feed
            await navegar_para_feed(page)
            
            # 4. DEBUG COMPLETO + Tentativa de click no dropdown
            dropdown_aberto = await clicar_dropdown_com_debug(page)
            
            if not dropdown_aberto:
                print("❌ Não conseguiu abrir dropdown automaticamente")
                print("🤚 ABRA O DROPDOWN MANUALMENTE (clique no '2025-1B-T13 -') e pressione Enter:")
                aguardar_usuario()
            
            # 5. Lista opções com debug
            opcoes = await listar_opcoes_com_debug(page)
            
            if opcoes:
                print(f"🎉 SUCESSO! Encontradas {len(opcoes)} opções:")
                for i, opcao in enumerate(opcoes):
                    print(f"   {i+1}. {opcao}")
                
                # Procura pelo módulo 6
                modulo6_encontrado = None
                for opcao in opcoes:
                    if "2025-1B-T13" in opcao:
                        modulo6_encontrado = opcao
                        break
                
                if modulo6_encontrado:
                    print(f"🎯 Módulo 6 encontrado: {modulo6_encontrado}")
                    
                    # Tenta selecionar
                    try:
                        await page.get_by_text(modulo6_encontrado, exact=True).click()
                        print("✅ Módulo 6 selecionado automaticamente!")
                    except:
                        print("🤚 Selecione o módulo '2025-1B-T13' manualmente e pressione Enter:")
                        aguardar_usuario()
                else:
                    print("❌ Módulo 6 não encontrado na lista")
                    print("🤚 Selecione o módulo '2025-1B-T13' manualmente e pressione Enter:")
                    aguardar_usuario()
                    
            else:
                print("❌ Nenhuma opção foi listada")
                print("🤚 Selecione o módulo '2025-1B-T13' manualmente e pressione Enter:")
                aguardar_usuario()
            
            print("🎉 DEBUG COMPLETO! Agora você pode continuar com o desenvolvimento...")
            print("🤚 Pressione Enter para sair:")
            aguardar_usuario()
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            print("🤚 Pressione Enter para sair:")
            aguardar_usuario()
            
        finally:
            await context.close()
            await browser.close()

    end_time = time.time()
    print(f"⏱️  Debug concluído em {end_time - start_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
