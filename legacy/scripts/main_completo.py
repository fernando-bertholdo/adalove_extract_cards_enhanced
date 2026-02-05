import asyncio
import csv
import time
import logging
from datetime import datetime
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os

# Configuração do sistema de logging
def configurar_logging():
    """
    Configura o sistema de logging para arquivo e console
    """
    # Cria pasta de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/adalove_extraction_{timestamp}.log"
    
    # Configuração do logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Para exibir no console também
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Iniciando nova sessão de extração - Log: {log_filename}")
    return logger

# Carregar variáveis do arquivo .env
load_dotenv()

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

logger = configurar_logging()

async def fazer_login_inteligente(page):
    """
    Função inteligente que detecta o tipo de login necessário
    """
    logger.info("🔑 Iniciando processo de login inteligente...")
    
    try:
        # Clica no botão "Entrar com o Google"
        logger.info("🔑 Procurando botão 'Entrar com o Google'...")
        botao_google = page.get_by_role("button", name="Entrar com o Google")
        
        if await botao_google.is_visible(timeout=10000):
            logger.info("✅ Botão Google encontrado, clicando...")
            await botao_google.click()
        else:
            logger.error("❌ Botão 'Entrar com o Google' não encontrado")
            return False
        
        # Aguarda 4 segundos para ver onde foi parar
        await page.wait_for_timeout(4000)
        
        current_url = page.url
        logger.info(f"📍 URL após click no botão Google: {current_url}")
        
        # Analisa onde estamos após o click
        if "accounts.google.com" in current_url:
            logger.info("🌐 Redirecionado para Google - fazendo login completo...")
            return await fazer_login_google_completo(page)
            
        elif "adalove.inteli.edu.br" in current_url and "/feed" in current_url:
            logger.info("✅ Login automático bem-sucedido - chegou no feed!")
            return True
            
        elif "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
            logger.info("✅ Login automático bem-sucedido - já estava na plataforma!")
            return True
            
        else:
            logger.info("❓ Aguardando conclusão do login...")
            # Aguarda mais tempo para ver se vai para o feed
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            logger.info(f"📍 URL após espera adicional: {current_url}")
            
            if "adalove.inteli.edu.br" in current_url and ("feed" in current_url or "/login" not in current_url):
                logger.info("✅ Login concluído com sucesso!")
                return True
            else:
                logger.error("❌ Login não foi concluído - timeout atingido")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro no processo de login inteligente: {str(e)}")
        return False

async def fazer_login_google_completo(page):
    """
    Faz o login completo no Google (email + senha)
    """
    logger.info("📧 Iniciando login completo no Google...")
    
    try:
        # Aguarda e preenche email
        logger.info("📧 Procurando campo de email...")
        seletores_email = ["input[type='email']", "#identifierId", "input[name='identifier']"]
        
        email_preenchido = False
        for seletor in seletores_email:
            try:
                logger.info(f"   🔍 Tentando seletor de email: {seletor}")
                campo_email = page.locator(seletor)
                await expect(campo_email).to_be_visible(timeout=10000)
                await campo_email.fill(LOGIN)
                email_preenchido = True
                logger.info(f"✅ Email preenchido com sucesso usando: {seletor}")
                break
            except:
                logger.warning(f"   ❌ Seletor falhou: {seletor}")
                continue
                
        if not email_preenchido:
            logger.error("❌ Não foi possível preencher o email com nenhum seletor")
            return False
            
        # Clica Próxima
        logger.info("➡️ Procurando botão 'Próxima'...")
        botoes_proxima = ["Próxima", "Next", "Continue"]
        
        botao_clicado = False
        for texto_botao in botoes_proxima:
            try:
                logger.info(f"   🔍 Tentando botão: {texto_botao}")
                botao = page.get_by_role("button", name=texto_botao)
                await botao.click(timeout=5000)
                logger.info(f"✅ Clicou em: {texto_botao}")
                botao_clicado = True
                break
            except:
                logger.warning(f"   ❌ Botão não encontrado: {texto_botao}")
                continue
        
        if not botao_clicado:
            logger.error("❌ Não foi possível clicar em nenhum botão 'Próxima'")
        
        # Aguarda página de senha
        logger.info("⏳ Aguardando página de senha...")
        await page.wait_for_timeout(5000)
        
        # Preenche senha
        logger.info("🔐 Procurando campo de senha...")
        seletores_senha = ["input[type='password']", "input[name='password']"]
        
        senha_preenchida = False
        for seletor in seletores_senha:
            try:
                logger.info(f"   🔍 Tentando seletor de senha: {seletor}")
                campo_senha = page.locator(seletor)
                await expect(campo_senha).to_be_visible(timeout=15000)
                await campo_senha.fill(SENHA)
                senha_preenchida = True
                logger.info(f"✅ Senha preenchida com sucesso usando: {seletor}")
                break
            except:
                logger.warning(f"   ❌ Seletor falhou: {seletor}")
                continue
                
        if not senha_preenchida:
            logger.error("❌ Não foi possível preencher a senha")
            return False
        
        # Clica botão final
        logger.info("🎯 Finalizando login...")
        botao_clicado = False
        for texto_botao in botoes_proxima:
            try:
                botao = page.get_by_role("button", name=texto_botao)
                await botao.click(timeout=5000)
                logger.info(f"✅ Clicou no botão final: {texto_botao}")
                botao_clicado = True
                break
            except:
                continue
        
        if not botao_clicado:
            logger.warning("⚠️  Não foi possível clicar no botão final - tentando continuar")
        
        # Aguarda redirecionamento para AdaLove
        logger.info("⏳ Aguardando redirecionamento para AdaLove...")
        for i in range(30):
            await page.wait_for_timeout(1000)
            current_url = page.url
            logger.debug(f"   Verificação {i+1}/30 - URL: {current_url}")
            
            if "adalove.inteli.edu.br" in current_url and ("feed" in current_url or "/login" not in current_url):
                logger.info("✅ Login Google completo e redirecionamento bem-sucedido!")
                return True
                
        logger.error("❌ Timeout no redirecionamento para AdaLove")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro no login Google: {str(e)}")
        return False

async def navegar_para_academic_life(page):
    """
    Navega diretamente para a página academic-life
    """
    logger.info("🏠 Navegando para academic-life...")
    
    try:
        current_url = page.url
        logger.info(f"📍 URL atual: {current_url}")
        
        # Navega para academic-life
        target_url = "https://adalove.inteli.edu.br/academic-life"
        logger.info(f"🎯 Navegando para: {target_url}")
        
        await page.goto(target_url)
        await page.wait_for_timeout(3000)
        
        # Verifica se chegou no lugar certo
        current_url = page.url
        logger.info(f"📍 Nova URL: {current_url}")
        
        if "academic-life" in current_url:
            logger.info("✅ Navegação para academic-life bem-sucedida!")
            return True
        else:
            logger.warning(f"⚠️  URL não contém 'academic-life': {current_url}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao navegar para academic-life: {str(e)}")
        return False

async def abrir_seletor_turmas(page):
    """
    Abre o seletor/modal de turmas na página academic-life
    """
    logger.info("📋 Procurando seletor de turmas/módulo...")
    
    try:
        # Aguarda a página carregar completamente
        await page.wait_for_timeout(3000)
        
        # Múltiplos seletores possíveis para o dropdown/seletor de turmas
        seletores_dropdown = [
            ".MuiFormControl-root.MuiFormControl-fullWidth",
            ".css-165oggv",
            ".MuiInputBase-root.MuiOutlinedInput-root", 
            ".css-3joqfb",
            "[role='combobox']",
            "select",
            ".MuiSelect-root",
            ".MuiSelect-select",
            "[data-testid='select-class']",
            "[data-testid='class-selector']"
        ]
        
        dropdown_encontrado = False
        seletor_usado = None
        
        for seletor in seletores_dropdown:
            try:
                logger.info(f"   🔍 Tentando seletor: {seletor}")
                dropdown = page.locator(seletor).first
                
                if await dropdown.is_visible(timeout=3000):
                    logger.info(f"   ✅ Dropdown encontrado com: {seletor}")
                    await dropdown.click()
                    dropdown_encontrado = True
                    seletor_usado = seletor
                    break
                    
            except Exception as e:
                logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                continue
        
        if not dropdown_encontrado:
            logger.warning("❌ Dropdown não encontrado com seletores automáticos")
            logger.info("🤚 Solicitando intervenção manual...")
            print("\n" + "="*50)
            print("🤚 INTERVENÇÃO MANUAL NECESSÁRIA")
            print("="*50)
            print("👆 Clique manualmente no seletor de turmas/módulo na página")
            print("⏸️  Pressione Enter no terminal após clicar")
            print("="*50)
            
            input("Aguardando... Pressione Enter após clicar no seletor: ")
            logger.info("✅ Usuário confirmou intervenção manual no seletor")
        else:
            logger.info(f"✅ Seletor clicado automaticamente com: {seletor_usado}")
        
        # Aguarda modal/dropdown abrir
        await page.wait_for_timeout(2000)
        logger.info("⏳ Aguardando modal de turmas abrir...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao abrir seletor de turmas: {str(e)}")
        return False

async def filtrar_e_selecionar_turma(page):
    """
    Pede input do usuário e filtra/seleciona a turma desejada
    """
    logger.info("🎯 Iniciando processo de seleção de turma...")
    
    try:
        # Solicita input do usuário
        print("\n" + "="*60)
        print("📋 SELEÇÃO DE TURMA")
        print("="*60)
        print("Agora você precisa informar o nome EXATO da turma que deseja acessar.")
        print("Este nome será usado para filtrar a lista de turmas disponíveis.")
        print("Exemplos: '2025-1B-T13', 'GRAD ES06', 'Turma 13', etc.")
        print("="*60)
        
        nome_turma = input("Digite o nome exato da turma: ").strip()
        
        if not nome_turma:
            logger.error("❌ Nome da turma não informado")
            return False
            
        logger.info(f"🎯 Turma informada pelo usuário: '{nome_turma}'")
        
        # Procura pelo campo de input/filtro no modal
        logger.info("🔍 Procurando campo de filtro no modal...")
        
        seletores_input = [
            "input[type='text']",
            "input[placeholder*='turma']",
            "input[placeholder*='filtro']", 
            "input[placeholder*='pesquisar']",
            "input[placeholder*='buscar']",
            ".MuiInputBase-input",
            "[data-testid='search-input']",
            "[data-testid='filter-input']"
        ]
        
        campo_encontrado = False
        
        for seletor in seletores_input:
            try:
                logger.info(f"   🔍 Tentando seletor de input: {seletor}")
                campo_input = page.locator(seletor).first
                
                if await campo_input.is_visible(timeout=3000):
                    logger.info(f"   ✅ Campo de filtro encontrado: {seletor}")
                    
                    # Limpa o campo e digita o nome da turma
                    await campo_input.clear()
                    await campo_input.fill(nome_turma)
                    
                    logger.info(f"✅ Nome da turma digitado no filtro: '{nome_turma}'")
                    campo_encontrado = True
                    break
                    
            except Exception as e:
                logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                continue
        
        if not campo_encontrado:
            logger.warning("❌ Campo de filtro não encontrado automaticamente")
            logger.info("🤚 Solicitando intervenção manual...")
            print("\n" + "="*50)
            print("🤚 INTERVENÇÃO MANUAL NECESSÁRIA")
            print("="*50)
            print(f"👆 Digite manualmente '{nome_turma}' no campo de filtro do modal")
            print("⏸️  Pressione Enter no terminal após digitar")
            print("="*50)
            
            input("Aguardando... Pressione Enter após digitar o nome: ")
            logger.info("✅ Usuário confirmou digitação manual do nome")
        
        # Aguarda filtro ser aplicado
        await page.wait_for_timeout(2000)
        logger.info("⏳ Aguardando filtro ser aplicado...")
        
        # Procura e clica na opção filtrada
        logger.info("🎯 Procurando opção da turma na lista filtrada...")
        
        seletores_opcoes = [
            f"text={nome_turma}",
            f"*[text*='{nome_turma}']",
            ".MuiMenuItem-root",
            "[role='option']",
            ".MuiList-root li",
            ".dropdown-item",
            "[data-testid='class-option']"
        ]
        
        opcao_clicada = False
        
        # Primeiro tenta encontrar por texto exato
        try:
            logger.info(f"   🔍 Procurando por texto exato: '{nome_turma}'")
            opcao_exata = page.get_by_text(nome_turma, exact=True).first
            
            if await opcao_exata.is_visible(timeout=5000):
                await opcao_exata.click()
                logger.info(f"✅ Clicou na turma por texto exato: '{nome_turma}'")
                opcao_clicada = True
            
        except Exception as e:
            logger.debug(f"   ❌ Busca por texto exato falhou: {str(e)}")
        
        # Se não encontrou por texto exato, tenta busca parcial
        if not opcao_clicada:
            try:
                logger.info(f"   🔍 Procurando por texto parcial: '{nome_turma}'")
                opcao_parcial = page.get_by_text(nome_turma, exact=False).first
                
                if await opcao_parcial.is_visible(timeout=5000):
                    await opcao_parcial.click()
                    logger.info(f"✅ Clicou na turma por texto parcial: '{nome_turma}'")
                    opcao_clicada = True
                
            except Exception as e:
                logger.debug(f"   ❌ Busca por texto parcial falhou: {str(e)}")
        
        # Se ainda não encontrou, tenta pelos seletores genéricos
        if not opcao_clicada:
            logger.info("   🔍 Tentando seletores genéricos de opções...")
            
            for seletor in seletores_opcoes[2:]:  # Pula os seletores de texto
                try:
                    logger.info(f"   🔍 Tentando seletor: {seletor}")
                    opcoes = page.locator(seletor)
                    count = await opcoes.count()
                    
                    if count > 0:
                        # Procura pela opção que contém o nome da turma
                        for i in range(count):
                            try:
                                opcao = opcoes.nth(i)
                                texto = await opcao.text_content()
                                
                                if texto and nome_turma.lower() in texto.lower():
                                    await opcao.click()
                                    logger.info(f"✅ Clicou na opção: '{texto.strip()}'")
                                    opcao_clicada = True
                                    break
                                    
                            except:
                                continue
                        
                        if opcao_clicada:
                            break
                            
                except Exception as e:
                    logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                    continue
        
        if not opcao_clicada:
            logger.warning("❌ Opção da turma não encontrada automaticamente")
            logger.info("🤚 Solicitando intervenção manual...")
            print("\n" + "="*50)
            print("🤚 INTERVENÇÃO MANUAL NECESSÁRIA") 
            print("="*50)
            print(f"👆 Clique manualmente na opção da turma '{nome_turma}' na lista")
            print("⏸️  Pressione Enter no terminal após clicar")
            print("="*50)
            
            input("Aguardando... Pressione Enter após clicar na turma: ")
            logger.info("✅ Usuário confirmou seleção manual da turma")
        
        # Aguarda modal fechar e página carregar
        await page.wait_for_timeout(3000)
        logger.info("⏳ Aguardando modal fechar e página carregar...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no processo de seleção de turma: {str(e)}")
        return False

async def verificar_pagina_turma(page):
    """
    Verifica se chegou na página da turma corretamente
    """
    logger.info("🔍 Verificando se chegou na página da turma...")
    
    try:
        current_url = page.url
        logger.info(f"📍 URL atual: {current_url}")
        
        # Aguarda página carregar
        await page.wait_for_timeout(3000)
        
        # Procura por elementos característicos da página da turma
        elementos_caracteristicos = [
            "text=Semana",
            "[data-rbd-draggable-id]",  # Cards arrastáveis
            ".week-container",
            ".academic-week",
            "text=Cards"
        ]
        
        elementos_encontrados = 0
        
        for elemento in elementos_caracteristicos:
            try:
                if await page.locator(elemento).count() > 0:
                    elementos_encontrados += 1
                    logger.info(f"   ✅ Elemento encontrado: {elemento}")
                else:
                    logger.info(f"   ❌ Elemento não encontrado: {elemento}")
            except:
                logger.info(f"   ❌ Erro ao procurar elemento: {elemento}")
        
        logger.info(f"📊 Elementos característicos encontrados: {elementos_encontrados}/{len(elementos_caracteristicos)}")
        
        if elementos_encontrados >= 2:
            logger.info("✅ Página da turma carregada com sucesso!")
            return True
        else:
            logger.warning("⚠️  Página da turma pode não ter carregado completamente")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar página da turma: {str(e)}")
        return False

async def fechar_popup_faltas(page):
    """
    Fecha o popup de faltas se aparecer
    """
    logger.info("🚫 Verificando se há popup de faltas...")
    
    try:
        await page.wait_for_timeout(3000)  # Aguarda popup aparecer se houver
        
        # Procura pelo botão "Fechar"
        seletores_fechar = [
            "button:has-text('Fechar')",
            "[aria-label='Fechar']",
            ".MuiButton-root:has-text('Fechar')",
            "[role='button']:has-text('Fechar')",
            ".close-button",
            ".popup-close",
            "[data-testid='close-modal']"
        ]
        
        popup_fechado = False
        
        for seletor in seletores_fechar:
            try:
                logger.info(f"   🔍 Procurando botão fechar: {seletor}")
                botao_fechar = page.locator(seletor)
                
                if await botao_fechar.is_visible(timeout=3000):
                    await botao_fechar.click()
                    logger.info(f"✅ Popup fechado com botão: {seletor}")
                    popup_fechado = True
                    break
                    
            except Exception as e:
                logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                continue
        
        if not popup_fechado:
            logger.info("ℹ️  Nenhum popup de faltas detectado")
        
        await page.wait_for_timeout(2000)  # Aguarda popup fechar completamente
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao fechar popup de faltas: {str(e)}")
        return False

async def testar_acesso_semanas(context):
    """
    Testa acesso às primeiras 3 semanas para verificar se tudo está funcionando
    """
    logger.info("🧪 Testando acesso às semanas para validação...")
    
    semanas = ["Semana 01", "Semana 02", "Semana 03"]
    resultados = []
    
    for semana in semanas:
        page = await context.new_page()
        
        try:
            logger.info(f"   🔍 Testando: {semana}")
            
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
                logger.info(f"   ✅ {semana}: {len(cards)} cards encontrados")
                resultados.append({"semana": semana, "cards": len(cards), "sucesso": True})
            else:
                logger.warning(f"   ❌ {semana}: não encontrada")
                resultados.append({"semana": semana, "cards": 0, "sucesso": False})
                
        except Exception as e:
            logger.error(f"   ❌ {semana}: erro - {str(e)}")
            resultados.append({"semana": semana, "cards": 0, "sucesso": False})
            
        finally:
            await page.close()
    
    # Resumo dos resultados
    sucessos = sum(1 for r in resultados if r["sucesso"])
    total_cards = sum(r["cards"] for r in resultados)
    
    logger.info(f"📊 Resultado do teste: {sucessos}/3 semanas acessadas, {total_cards} cards total")
    
    if sucessos > 0:
        logger.info("✅ Teste de validação passou - automação funcionando!")
    else:
        logger.error("❌ Teste de validação falhou - verificar configuração")
    
    return sucessos > 0

async def main():
    """
    Função principal com fluxo reformulado
    """
    logger.info("🚀 Iniciando extração reformulada do AdaLove...")
    logger.info(f"👤 Usuário: {LOGIN}")
    start_time = time.time()

    async with async_playwright() as p:
        try:
            logger.info("🌐 Iniciando navegador...")
            browser = await p.chromium.launch(channel="chrome", headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 1. Acessa AdaLove
            logger.info("🌐 Acessando página inicial do AdaLove...")
            await page.goto("https://adalove.inteli.edu.br/")
            await page.wait_for_timeout(3000)
            
            # 2. Faz login inteligente  
            logger.info("🔐 Iniciando processo de login...")
            login_sucesso = await fazer_login_inteligente(page)
            
            if not login_sucesso:
                logger.error("❌ Falha no login automático")
                logger.info("🤚 PAUSANDO para intervenção manual no login...")
                
                print("\n" + "="*50)
                print("🤚 INTERVENÇÃO MANUAL NECESSÁRIA - LOGIN")
                print("="*50)
                print("❌ O login automático falhou.")
                print("👆 Complete o login manualmente na página")
                print("⏸️  Pressione Enter após fazer login com sucesso")
                print("="*50)
                
                input("Aguardando... Pressione Enter após login manual: ")
                logger.info("✅ Usuário confirmou login manual")
            
            # 3. Navega diretamente para academic-life
            logger.info("🏠 Navegando para academic-life...")
            navegacao_sucesso = await navegar_para_academic_life(page)
            
            if not navegacao_sucesso:
                logger.error("❌ Falha na navegação para academic-life")
                return
            
            # 4. Fecha popup de faltas se aparecer
            await fechar_popup_faltas(page)
            
            # 5. Abre seletor de turmas
            logger.info("📋 Abrindo seletor de turmas...")
            seletor_sucesso = await abrir_seletor_turmas(page)
            
            if not seletor_sucesso:
                logger.error("❌ Falha ao abrir seletor de turmas")
                return
            
            # 6. Filtra e seleciona turma
            logger.info("🎯 Filtrando e selecionando turma...")
            selecao_sucesso = await filtrar_e_selecionar_turma(page)
            
            if not selecao_sucesso:
                logger.error("❌ Falha na seleção da turma")
                return
            
            # 7. Verifica se chegou na página da turma
            logger.info("🔍 Verificando página da turma...")
            pagina_sucesso = await verificar_pagina_turma(page)
            
            if not pagina_sucesso:
                logger.warning("⚠️  Página da turma pode não ter carregado corretamente")
            
            # 8. Fecha popup de faltas novamente (pode aparecer na nova página)
            await fechar_popup_faltas(page)
            
            # 9. Testa acesso às semanas
            logger.info("🧪 Executando teste de validação...")
            teste_sucesso = await testar_acesso_semanas(context)
            
            if teste_sucesso:
                logger.info("🎉 SUCESSO! Configuração da turma concluída!")
                logger.info("✅ Pronto para extração completa de todas as semanas")
                
                print("\n" + "="*60)
                print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
                print("="*60)
                print("✅ Login realizado")
                print("✅ Navegação para academic-life")
                print("✅ Seleção de turma")
                print("✅ Teste de acesso às semanas")
                print("="*60)
                print("⏸️  Pressione Enter para continuar com a extração completa...")
                print("❌ Ou feche o navegador para sair")
                print("="*60)
                
                input("Aguardando... Pressione Enter para prosseguir: ")
                logger.info("✅ Usuário confirmou prosseguimento")
                
            else:
                logger.error("❌ Teste de validação falhou - verificar configuração")
                
                print("\n" + "="*60)
                print("❌ TESTE DE VALIDAÇÃO FALHOU")
                print("="*60)
                print("⚠️  A configuração não passou no teste de validação")
                print("🔧 Verifique se a turma foi selecionada corretamente")
                print("⏸️  Pressione Enter para sair")
                print("="*60)
                
                input("Pressione Enter para sair: ")
                logger.info("❌ Usuário confirmou saída após falha no teste")
        
        except Exception as e:
            logger.error(f"❌ Erro geral na execução: {str(e)}")
            
            print("\n" + "="*60)
            print("❌ ERRO GERAL")
            print("="*60)
            print(f"Erro: {str(e)}")
            print("⏸️  Pressione Enter para sair")
            print("="*60)
            
            input("Pressione Enter para sair: ")
            
        finally:
            logger.info("🔚 Finalizando navegador...")
            if 'context' in locals():
                await context.close()
            if 'browser' in locals():
                await browser.close()

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"⏱️  Execução concluída em {duration:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
