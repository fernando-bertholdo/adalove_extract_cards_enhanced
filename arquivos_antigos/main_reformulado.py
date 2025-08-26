import asyncio
import csv
import time
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('adalove_extraction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Carregar variáveis do arquivo .env
load_dotenv()

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

async def fazer_login_inteligente(page):
    """
    Login inteligente no AdaLove
    """
    logger.info("=== INICIANDO PROCESSO DE LOGIN ===")
    
    try:
        # Clica no botão "Entrar com o Google"
        logger.info("Procurando botão 'Entrar com o Google'")
        await page.get_by_role("button", name="Entrar com o Google").click()
        logger.info("✓ Clicou em 'Entrar com o Google'")
        
        # Aguarda redirecionamento
        await page.wait_for_timeout(5000)
        current_url = page.url
        logger.info(f"URL após click: {current_url}")
        
        if "accounts.google.com" in current_url:
            logger.info("Redirecionado para Google - iniciando login completo")
            return await fazer_login_google_completo(page)
        elif "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
            logger.info("✓ Login automático bem-sucedido (já logado no Google)")
            return True
        else:
            logger.warning("Situação inesperada no login")
            await page.wait_for_timeout(10000)
            current_url = page.url
            logger.info(f"URL após espera adicional: {current_url}")
            
            if "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
                logger.info("✓ Login concluído após espera")
                return True
            else:
                logger.error("Login não foi concluído automaticamente")
                return False
                
    except Exception as e:
        logger.error(f"Erro no processo de login: {e}")
        return False

async def fazer_login_google_completo(page):
    """
    Login completo no Google com email e senha
    """
    logger.info("=== LOGIN COMPLETO NO GOOGLE ===")
    
    try:
        # Preenche email
        logger.info("Preenchendo email")
        seletores_email = ["input[type='email']", "#identifierId", "input[name='identifier']"]
        
        email_preenchido = False
        for seletor in seletores_email:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=10000)
                await page.locator(seletor).fill(LOGIN)
                email_preenchido = True
                logger.info(f"✓ Email preenchido usando seletor: {seletor}")
                break
            except:
                logger.debug(f"Seletor {seletor} não funcionou para email")
                continue
                
        if not email_preenchido:
            logger.error("Não conseguiu preencher email")
            return False
        
        # Clica Próxima
        logger.info("Clicando em 'Próxima'")
        botoes_proxima = ["Next", "Próxima", "Continue"]
        
        for texto_botao in botoes_proxima:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                logger.info(f"✓ Clicou em botão: {texto_botao}")
                break
            except:
                logger.debug(f"Botão '{texto_botao}' não encontrado")
                continue
        
        await page.wait_for_timeout(5000)
        
        # Preenche senha
        logger.info("Preenchendo senha")
        seletores_senha = ["input[type='password']", "input[name='password']"]
        
        senha_preenchida = False
        for seletor in seletores_senha:
            try:
                await expect(page.locator(seletor)).to_be_visible(timeout=15000)
                await page.locator(seletor).fill(SENHA)
                senha_preenchida = True
                logger.info(f"✓ Senha preenchida usando seletor: {seletor}")
                break
            except:
                logger.debug(f"Seletor {seletor} não funcionou para senha")
                continue
                
        if not senha_preenchida:
            logger.error("Não conseguiu preencher senha")
            return False
        
        # Clica botão final
        logger.info("Finalizando login")
        for texto_botao in botoes_proxima:
            try:
                await page.get_by_role("button", name=texto_botao).click(timeout=5000)
                logger.info(f"✓ Clicou em botão final: {texto_botao}")
                break
            except:
                logger.debug(f"Botão final '{texto_botao}' não encontrado")
                continue
        
        # Aguarda redirecionamento
        logger.info("Aguardando redirecionamento para AdaLove")
        for i in range(30):
            await page.wait_for_timeout(1000)
            current_url = page.url
            
            if "adalove.inteli.edu.br" in current_url and "/login" not in current_url:
                logger.info("✓ Login Google completo - redirecionado para AdaLove")
                return True
                
        logger.error("Timeout aguardando redirecionamento do Google")
        return False
        
    except Exception as e:
        logger.error(f"Erro no login do Google: {e}")
        return False

async def navegar_para_academic_life(page):
    """
    Navega diretamente para a página academic-life
    """
    logger.info("=== NAVEGANDO PARA ACADEMIC-LIFE ===")
    
    try:
        current_url = page.url
        logger.info(f"URL atual: {current_url}")
        
        logger.info("Navegando para https://adalove.inteli.edu.br/academic-life")
        await page.goto("https://adalove.inteli.edu.br/academic-life")
        await page.wait_for_timeout(3000)
        
        logger.info(f"✓ Navegação concluída. URL atual: {page.url}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao navegar para academic-life: {e}")
        return False

async def fechar_popup_faltas(page):
    """
    Fecha popup de faltas se aparecer
    """
    logger.info("Verificando popup de faltas")
    
    await page.wait_for_timeout(3000)
    
    seletores_fechar = [
        "button:has-text('Fechar')",
        "[aria-label='Fechar']",
        ".MuiButton-root:has-text('Fechar')"
    ]
    
    for seletor in seletores_fechar:
        try:
            botao_fechar = page.locator(seletor)
            if await botao_fechar.is_visible(timeout=3000):
                await botao_fechar.click()
                logger.info("✓ Popup de faltas fechado")
                return True
        except:
            continue
    
    logger.info("Nenhum popup de faltas detectado")
    return False

async def abrir_modal_selecao_turma(page):
    """
    Abre o modal de seleção de turma clicando no seletor
    """
    logger.info("=== ABRINDO MODAL DE SELEÇÃO DE TURMA ===")
    
    # Primeiro fecha popup de faltas se existir
    await fechar_popup_faltas(page)
    
    # Seletores possíveis para o campo de turma baseado nas imagens
    seletores_campo_turma = [
        "input[aria-invalid='false'].MuiInputBase-input.MuiOutlinedInput-input",
        ".MuiInputBase-input.MuiOutlinedInput-input",
        "input.css-h4os0j",
        "input[autocomplete='off']",
        "div[role='combobox']",
        ".MuiFormControl-root input"
    ]
    
    for seletor in seletores_campo_turma:
        try:
            logger.info(f"Tentando clicar no seletor: {seletor}")
            campo = page.locator(seletor)
            
            if await campo.count() > 0:
                logger.info(f"Seletor encontrado: {seletor} ({await campo.count()} elementos)")
                await campo.first.click()
                logger.info("✓ Clicou no seletor de turma")
                
                # Aguarda modal abrir
                await page.wait_for_timeout(3000)
                
                # Verifica se modal abriu procurando por elementos típicos
                modal_aberto = False
                elementos_modal = ["dialog", ".MuiDialog-root", ".MuiModal-root", "div[role='dialog']"]
                
                for elem_modal in elementos_modal:
                    if await page.locator(elem_modal).count() > 0:
                        logger.info(f"✓ Modal detectado usando: {elem_modal}")
                        modal_aberto = True
                        break
                
                if modal_aberto:
                    return True
                else:
                    logger.info("Modal pode ter aberto - continuando")
                    return True
                    
        except Exception as e:
            logger.debug(f"Seletor {seletor} falhou: {e}")
            continue
    
    logger.error("Não foi possível abrir modal de seleção de turma")
    return False

def obter_nome_turma_do_usuario():
    """
    Obtém nome da turma do usuário via input no terminal
    """
    logger.info("=== OBTENDO NOME DA TURMA ===")
    
    print("\n" + "="*50)
    print("SELEÇÃO DE TURMA/MÓDULO")
    print("="*50)
    print("Exemplos de nomes válidos:")
    print("- 2025-1B-T13")
    print("- 2025-2A-T13") 
    print("- GRAD ES06")
    print("- ES07")
    print("="*50)
    
    while True:
        nome_turma = input("Digite o nome EXATO da turma que deseja acessar: ").strip()
        
        if nome_turma:
            logger.info(f"Turma selecionada pelo usuário: {nome_turma}")
            return nome_turma
        else:
            print("Por favor, digite um nome válido.")

async def filtrar_e_selecionar_turma(page, nome_turma):
    """
    Filtra a turma usando o campo de busca e seleciona a opção
    """
    logger.info(f"=== FILTRANDO E SELECIONANDO TURMA: {nome_turma} ===")
    
    try:
        # Procura pelo campo de input no modal
        seletores_input_filtro = [
            "input[type='text']",
            ".MuiInputBase-input",
            "input[placeholder]",
            "dialog input",
            ".MuiModal-root input"
        ]
        
        campo_filtro_encontrado = False
        
        for seletor in seletores_input_filtro:
            try:
                campo = page.locator(seletor)
                count = await campo.count()
                logger.info(f"Seletor {seletor}: {count} elementos")
                
                if count > 0:
                    # Tenta usar o primeiro campo visível
                    for i in range(count):
                        try:
                            campo_atual = campo.nth(i)
                            if await campo_atual.is_visible():
                                logger.info(f"Preenchendo campo {i+1} com: {nome_turma}")
                                
                                await campo_atual.click()
                                await campo_atual.clear()
                                await campo_atual.fill(nome_turma)
                                
                                campo_filtro_encontrado = True
                                logger.info("✓ Filtro aplicado")
                                break
                        except Exception as e:
                            logger.debug(f"Campo {i+1} falhou: {e}")
                            continue
                
                if campo_filtro_encontrado:
                    break
                    
            except Exception as e:
                logger.debug(f"Seletor {seletor} falhou: {e}")
                continue
        
        if not campo_filtro_encontrado:
            logger.error("Não foi possível encontrar campo de filtro")
            return False
        
        # Aguarda filtro ser aplicado
        await page.wait_for_timeout(2000)
        
        # Procura pela opção filtrada e clica
        logger.info("Procurando opção da turma filtrada")
        
        seletores_opcoes = [
            f"li:has-text('{nome_turma}')",
            f".MuiMenuItem-root:has-text('{nome_turma}')",
            f"[role='option']:has-text('{nome_turma}')",
            f"button:has-text('{nome_turma}')"
        ]
        
        opcao_selecionada = False
        
        for seletor in seletores_opcoes:
            try:
                opcoes = page.locator(seletor)
                count = await opcoes.count()
                logger.info(f"Opções encontradas com {seletor}: {count}")
                
                if count > 0:
                    await opcoes.first.click()
                    logger.info(f"✓ Turma selecionada usando: {seletor}")
                    opcao_selecionada = True
                    break
                    
            except Exception as e:
                logger.debug(f"Seletor {seletor} falhou: {e}")
                continue
        
        if not opcao_selecionada:
            logger.error("Não foi possível selecionar a turma filtrada")
            return False
        
        # Aguarda modal fechar e página carregar
        await page.wait_for_timeout(3000)
        logger.info("✓ Turma selecionada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao filtrar e selecionar turma: {e}")
        return False

async def testar_acesso_semanas(context, nome_turma):
    """
    Testa acesso às primeiras semanas da turma selecionada
    """
    logger.info(f"=== TESTANDO ACESSO ÀS SEMANAS DA TURMA: {nome_turma} ===")
    
    semanas_teste = ["Semana 01", "Semana 02", "Semana 03"]
    resultados = []
    
    for semana in semanas_teste:
        page = await context.new_page()
        try:
            logger.info(f"Testando acesso: {semana}")
            
            await page.goto("https://adalove.inteli.edu.br/academic-life")
            await page.wait_for_timeout(3000)
            
            # Fecha popup de faltas se aparecer
            await fechar_popup_faltas(page)
            
            # Procura pela semana
            elemento_semana = page.get_by_text(semana, exact=False)
            count = await elemento_semana.count()
            logger.info(f"Elementos com texto '{semana}': {count}")
            
            if count > 0:
                await elemento_semana.first.click(timeout=8000)
                await page.wait_for_timeout(3000)
                
                # Conta cards
                cards = await page.query_selector_all('[data-rbd-draggable-id]')
                cards_count = len(cards)
                logger.info(f"✓ {semana}: {cards_count} cards encontrados")
                resultados.append({"semana": semana, "cards": cards_count, "sucesso": True})
            else:
                logger.warning(f"✗ {semana}: não encontrada")
                resultados.append({"semana": semana, "cards": 0, "sucesso": False})
                
        except Exception as e:
            logger.error(f"✗ {semana}: erro - {str(e)}")
            resultados.append({"semana": semana, "cards": 0, "sucesso": False})
        finally:
            await page.close()
    
    # Resumo dos resultados
    sucessos = sum(1 for r in resultados if r["sucesso"])
    total_cards = sum(r["cards"] for r in resultados)
    
    logger.info(f"RESULTADO DO TESTE: {sucessos}/3 semanas acessadas, {total_cards} cards total")
    
    return sucessos > 0

async def main():
    """
    Função principal reformulada
    """
    logger.info("="*60)
    logger.info("INICIANDO EXTRAÇÃO ADALOVE - VERSÃO REFORMULADA")
    logger.info("="*60)
    
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Acessa AdaLove
            logger.info("Acessando AdaLove")
            await page.goto("https://adalove.inteli.edu.br/")
            await page.wait_for_timeout(3000)
            
            # 2. Faz login
            login_sucesso = await fazer_login_inteligente(page)
            
            if not login_sucesso:
                logger.error("Falha no login automático")
                print("\n❌ Login automático falhou.")
                print("👆 Faça login manualmente no navegador e pressione Enter aqui:")
                input()
                logger.info("Login manual concluído pelo usuário")
            
            # 3. Navega diretamente para academic-life
            nav_sucesso = await navegar_para_academic_life(page)
            
            if not nav_sucesso:
                logger.error("Falha na navegação para academic-life")
                return
            
            # 4. Abre modal de seleção de turma
            modal_aberto = await abrir_modal_selecao_turma(page)
            
            if not modal_aberto:
                logger.error("Não foi possível abrir modal de turma")
                print("\n❌ Modal de seleção não abriu automaticamente.")
                print("👆 Abra manualmente o seletor de turmas e pressione Enter:")
                input()
                logger.info("Modal aberto manualmente pelo usuário")
            
            # 5. Obtém nome da turma do usuário
            nome_turma = obter_nome_turma_do_usuario()
            
            # 6. Filtra e seleciona a turma
            selecao_sucesso = await filtrar_e_selecionar_turma(page, nome_turma)
            
            if not selecao_sucesso:
                logger.error("Falha na seleção da turma")
                print(f"\n❌ Não foi possível selecionar '{nome_turma}' automaticamente.")
                print("👆 Selecione a turma manualmente e pressione Enter:")
                input()
                logger.info("Turma selecionada manualmente pelo usuário")
            
            # 7. Testa acesso às semanas
            teste_sucesso = await testar_acesso_semanas(context, nome_turma)
            
            if teste_sucesso:
                logger.info("✓ TESTE BEM-SUCEDIDO! Sistema configurado corretamente")
                print(f"\n🎉 SUCESSO! Turma '{nome_turma}' configurada corretamente!")
                print("✅ Sistema pronto para extração completa")
                print("👆 Pressione Enter para continuar:")
                input()
                
                # Aqui seria implementada a extração completa
                logger.info("Sistema pronto para implementar extração completa")
                
            else:
                logger.error("Teste de acesso às semanas falhou")
                print(f"\n❌ Falha no teste de acesso às semanas da turma '{nome_turma}'")
                print("👆 Verifique se a turma foi selecionada corretamente")
                print("Pressione Enter para sair:")
                input()
        
        except Exception as e:
            logger.error(f"Erro geral no script: {e}")
            print(f"\n❌ Erro geral: {e}")
            print("👆 Pressione Enter para sair:")
            input()
            
        finally:
            await context.close()
            await browser.close()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"SCRIPT CONCLUÍDO EM {elapsed_time:.1f} SEGUNDOS")
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(main())
