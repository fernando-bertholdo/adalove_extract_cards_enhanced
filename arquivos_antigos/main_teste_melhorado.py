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

async def aguardar_login_concluido(page):
    """
    Aguarda o login ser concluído, seja automaticamente ou manualmente
    """
    print("Aguardando conclusão do login...")
    
    # Aguarda até 60 segundos para o login ser concluído
    for i in range(60):
        current_url = page.url
        print(f"URL atual: {current_url}")
        
        # Se estiver na página principal do AdaLove (não na página de login)
        if "adalove.inteli.edu.br" in current_url and "/login" not in current_url and "accounts.google.com" not in current_url:
            print("✅ Login concluído com sucesso!")
            return True
            
        # Verifica se existem elementos que indicam que estamos logados
        try:
            # Procura por elementos típicos da interface logada
            elementos_logado = [
                "[data-testid]",  # Elementos da interface interna
                ".MuiAvatar-root",  # Avatar do usuário
                "[aria-label*='user']",  # Elementos relacionados ao usuário
                "button:has-text('Perfil')",
                "nav",  # Navegação interna
            ]
            
            for elemento in elementos_logado:
                if await page.locator(elemento).first.is_visible():
                    print("✅ Login detectado pela interface!")
                    return True
                    
        except:
            pass
            
        await page.wait_for_timeout(1000)  # Espera 1 segundo
    
    print("⏰ Timeout aguardando login - continuando mesmo assim")
    return False

async def selecionar_modulo(page):
    """
    Função para selecionar o Módulo 6
    """
    print("🔍 Procurando pelo Módulo 6...")
    
    # Se não estiver na página inicial, navega para lá
    if "adalove.inteli.edu.br" not in page.url or page.url.endswith("/"):
        await page.goto("https://adalove.inteli.edu.br/")
        await page.wait_for_timeout(3000)
    
    # Procura pelo módulo 6 - tenta várias variações do nome
    modulos_para_tentar = [
        "2025-1B-T13",
        "2025-1B-T13 - GRAD ES06 - 2025-1B", 
        "GRAD ES06 - 2025-1B",
        "ES06",
        "T13",
        "Módulo 6",
        "GRAD ES06"
    ]
    
    for nome_modulo in modulos_para_tentar:
        try:
            print(f"🔍 Procurando: {nome_modulo}")
            
            # Tenta encontrar o módulo por texto
            elemento = page.get_by_text(nome_modulo, exact=False)
            if await elemento.count() > 0:
                await elemento.first.click(timeout=5000)
                print(f"✅ Módulo selecionado: {nome_modulo}")
                await page.wait_for_timeout(3000)
                return True
                
        except Exception as e:
            print(f"❌ Não encontrado: {nome_modulo}")
            continue
    
    # Se não encontrou automaticamente, tenta buscar por seletores mais genéricos
    print("🔍 Procurando seletores genéricos para módulos...")
    try:
        # Procura por cards ou elementos clicáveis que podem ser módulos
        seletores_modulo = [
            "[data-testid*='module']",
            "[data-testid*='course']", 
            ".card:has-text('2025')",
            ".module:has-text('ES06')",
            "button:has-text('2025')",
            "[role='button']:has-text('T13')"
        ]
        
        for seletor in seletores_modulo:
            elementos = page.locator(seletor)
            if await elementos.count() > 0:
                await elementos.first.click()
                print(f"✅ Clicou em elemento: {seletor}")
                await page.wait_for_timeout(3000)
                return True
                
    except:
        pass
    
    print("❓ Módulo não encontrado automaticamente")
    return False

async def processar_unidade_simples(context, unidade_nome):
    """
    Testa se conseguimos acessar uma semana específica
    """
    page = await context.new_page()
    
    try:
        print(f"🔍 Testando acesso: {unidade_nome}")
        
        # Vai para academic-life
        await page.goto("https://adalove.inteli.edu.br/academic-life")
        await page.wait_for_timeout(3000)
        
        # Procura pela semana
        semana_encontrada = False
        
        # Tenta diferentes formas de encontrar a semana
        variações_semana = [
            unidade_nome,  # "Semana 01"
            unidade_nome.replace("Semana ", "Semana"),  # Remove espaços extras
            unidade_nome.replace("Semana 0", "Semana "),  # "Semana 1" 
            f"Week {unidade_nome.split()[-1]}"  # "Week 01"
        ]
        
        for variacao in variações_semana:
            try:
                elemento = page.get_by_text(variacao, exact=False)
                if await elemento.count() > 0:
                    await elemento.first.click(timeout=5000)
                    semana_encontrada = True
                    print(f"✅ {unidade_nome} encontrada como: {variacao}")
                    break
            except:
                continue
        
        if not semana_encontrada:
            print(f"❌ {unidade_nome} não encontrada")
            return False
        
        # Aguarda carregar e conta os cards
        await page.wait_for_timeout(3000)
        cards = await page.query_selector_all('[data-rbd-draggable-id]')
        print(f"📋 {len(cards)} cards encontrados na {unidade_nome}")
        
        # Se encontrou cards, é um bom sinal
        if len(cards) > 0:
            print(f"✅ {unidade_nome} - Acesso bem-sucedido!")
            return True
        else:
            print(f"⚠️  {unidade_nome} - Acessada mas sem cards")
            return False
            
    except Exception as e:
        print(f"❌ Erro em {unidade_nome}: {str(e)[:100]}")
        return False
    
    finally:
        await page.close()

async def main():
    """
    Função principal de teste melhorada
    """
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        
        print("🌐 Acessando AdaLove...")
        await page.goto("https://adalove.inteli.edu.br/")
        await page.wait_for_timeout(2000)
        
        print("🔑 Procurando botão de login...")
        
        # Clica no botão "Entrar com o Google" se estiver visível
        try:
            botao_login = page.get_by_role("button", name="Entrar com o Google")
            if await botao_login.is_visible():
                print("🔑 Clicando em 'Entrar com o Google'...")
                await botao_login.click()
            else:
                print("🔑 Botão de login não visível - pode já estar logado")
        except:
            print("🔑 Não foi possível clicar no botão - continuando...")

        # Aguarda o login ser concluído (automaticamente ou manualmente)
        login_ok = await aguardar_login_concluido(page)
        
        if not login_ok:
            print("❌ Login não foi detectado. Continuando mesmo assim...")
        
        # Seleciona o módulo
        modulo_ok = await selecionar_modulo(page)
        
        if not modulo_ok:
            print("❓ PAUSANDO para seleção manual do módulo...")
            print("👆 Por favor, selecione manualmente o Módulo 6 na interface do navegador")
            print("📋 Procure por: '2025-1B-T13' ou 'GRAD ES06' ou similar") 
            print("⏸️  Pressione Enter aqui DEPOIS de selecionar o módulo")
            await page.pause()
        
        # Testa acesso às semanas
        print("🧪 Testando acesso às semanas do Módulo 6...")
        semanas_teste = ["Semana 01", "Semana 02", "Semana 03"]
        
        semanas_ok = 0
        for semana in semanas_teste:
            resultado = await processar_unidade_simples(context, semana)
            if resultado:
                semanas_ok += 1
        
        print(f"\n📊 Resultado do teste: {semanas_ok}/{len(semanas_teste)} semanas acessadas com sucesso")
        
        if semanas_ok > 0:
            print("✅ Teste bem-sucedido! Podemos prosseguir com a extração completa.")
            print("⏸️  PAUSANDO - Pressione Enter se quiser continuar com a extração de TODAS as 10 semanas")
            await page.pause()
        else:
            print("❌ Nenhuma semana foi acessada. Verifique se o módulo correto foi selecionado.")
            print("⏸️  PAUSANDO para verificação manual...")
            await page.pause()

        await context.close()
        await browser.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"⏱️  Teste concluído em {elapsed_time:.2f} segundos.")

# Executa o script
if __name__ == "__main__":
    asyncio.run(main())
