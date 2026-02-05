import asyncio
import csv
import time
import logging
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

# Configuração simples de logging
def configurar_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/extracao_simples_{timestamp}.log"
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dados_extraidos", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

load_dotenv()
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")
logger = configurar_logging()

async def fazer_login_completo(page):
    """Login simplificado - com intervenção manual se necessário"""
    logger.info("🔑 Fazendo login...")
    
    try:
        # Tenta clique automático no botão Google
        botao_google = page.get_by_role("button", name="Entrar com o Google")
        if await botao_google.is_visible(timeout=10000):
            await botao_google.click()
            await page.wait_for_timeout(3000)
            
            # Se foi para Google, tenta login automático
            if "accounts.google.com" in page.url:
                logger.info("   📧 Preenchendo credenciais...")
                
                # Email
                try:
                    email_field = page.locator("input[type='email']").first
                    await email_field.fill(LOGIN)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(3000)
                except:
                    pass
                
                # Senha
                try:
                    senha_field = page.locator("input[type='password']").first
                    await senha_field.fill(SENHA)
                    await page.get_by_role("button", name="Next").click()
                    await page.wait_for_timeout(5000)
                except:
                    pass
        
        # Verifica se chegou no AdaLove
        for _ in range(20):  # 20 segundos
            await page.wait_for_timeout(1000)
            if "adalove.inteli.edu.br" in page.url and "/login" not in page.url:
                logger.info("✅ Login realizado!")
                return True
        
        # Se não conseguiu automaticamente
        logger.warning("⚠️ Login automático falhou")
        print("\n🤚 Complete o login manualmente se necessário")
        print("⏸️ Pressione Enter quando estiver logado:")
        input()
        logger.info("✅ Login confirmado pelo usuário")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

async def ir_para_academic_life(page):
    """Navega para academic-life"""
    logger.info("🏠 Indo para academic-life...")
    await page.goto("https://adalove.inteli.edu.br/academic-life")
    await page.wait_for_timeout(3000)
    
    # Fecha popup se aparecer
    try:
        fechar_btn = page.locator("button:has-text('Fechar')").first
        if await fechar_btn.is_visible(timeout=3000):
            await fechar_btn.click()
            await page.wait_for_timeout(2000)
    except:
        pass
    
    logger.info("✅ Página academic-life carregada")

async def selecionar_turma(page):
    """Seleção manual de turma - mais confiável"""
    print("\n" + "="*50)
    print("🎯 SELEÇÃO DE TURMA")
    print("="*50)
    print("👆 Na página, selecione a turma desejada:")
    print("1. Clique no dropdown de turmas")
    print("2. Escolha/digite a turma")  
    print("3. Clique na turma desejada")
    print("4. Aguarde carregar")
    print("5. Pressione Enter aqui")
    print("="*50)
    
    input("⏸️ Pressione Enter após selecionar a turma: ")
    logger.info("✅ Turma selecionada pelo usuário")
    await page.wait_for_timeout(3000)

async def extrair_cards_de_semana(page, nome_semana):
    """Extrai cards de uma semana"""
    logger.info(f"   📋 Extraindo: {nome_semana}")
    
    try:
        # Clica na semana
        semana_element = page.get_by_text(nome_semana, exact=False).first
        
        if await semana_element.is_visible(timeout=8000):
            await semana_element.click()
            await page.wait_for_timeout(3000)
            
            # Procura cards
            cards = page.locator("[data-rbd-draggable-id]")
            count = await cards.count()
            
            if count > 0:
                logger.info(f"      ✅ {count} cards encontrados")
                
                # Extrai dados de cada card
                cards_data = []
                for i in range(count):
                    try:
                        card = cards.nth(i)
                        
                        # Dados básicos do card
                        card_info = {
                            "semana": nome_semana,
                            "indice": i + 1,
                            "id": await card.get_attribute("data-rbd-draggable-id") or "",
                            "texto_completo": await card.text_content() or "",
                            "titulo": "",
                            "descricao": ""
                        }
                        
                        # Tenta extrair título (primeira linha não vazia)
                        linhas = card_info["texto_completo"].split('\n')
                        primeira_linha = next((linha.strip() for linha in linhas if linha.strip()), "")
                        if primeira_linha:
                            card_info["titulo"] = primeira_linha
                        
                        # Descrição (resto do texto)
                        if len(linhas) > 1:
                            resto = '\n'.join(linha.strip() for linha in linhas[1:] if linha.strip())
                            card_info["descricao"] = resto[:500]  # Limita descrição
                        
                        cards_data.append(card_info)
                        
                    except Exception as e:
                        logger.warning(f"      ⚠️ Erro no card {i+1}: {e}")
                
                return cards_data
            else:
                logger.warning(f"      ❌ Nenhum card encontrado em {nome_semana}")
                return []
        else:
            logger.warning(f"   ❌ Semana não encontrada: {nome_semana}")
            return []
            
    except Exception as e:
        logger.error(f"   ❌ Erro ao extrair {nome_semana}: {e}")
        return []

async def salvar_resultados(todos_cards):
    """Salva resultados em CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dados_extraidos/cards_extracao_{timestamp}.csv"
    
    logger.info(f"💾 Salvando {len(todos_cards)} cards...")
    
    headers = ["semana", "indice", "id", "titulo", "descricao", "texto_completo"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(todos_cards)
    
    logger.info(f"✅ Salvo em: {filename}")
    return filename

async def main():
    """Extração simplificada e eficiente"""
    logger.info("🚀 Iniciando extração SIMPLIFICADA...")
    
    # Lista de semanas para processar (ajuste conforme necessário)
    semanas = [
        "Semana 01", "Semana 02", "Semana 03", "Semana 04", "Semana 05",
        "Semana 06", "Semana 07", "Semana 08", "Semana 09", "Semana 10"
    ]
    
    start_time = time.time()
    todos_cards = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        page = await browser.new_page()
        
        try:
            # 1. Login
            await page.goto("https://adalove.inteli.edu.br/")
            await fazer_login_completo(page)
            
            # 2. Vai para academic-life
            await ir_para_academic_life(page)
            
            # 3. Seleciona turma
            await selecionar_turma(page)
            
            # 4. Processa cada semana
            logger.info(f"📚 Processando {len(semanas)} semanas...")
            
            for i, semana in enumerate(semanas, 1):
                logger.info(f"🔄 {semana} ({i}/{len(semanas)})")
                
                # Volta para academic-life
                await page.goto("https://adalove.inteli.edu.br/academic-life")
                await page.wait_for_timeout(2000)
                
                # Fecha popup se aparecer
                try:
                    fechar_btn = page.locator("button:has-text('Fechar')").first
                    if await fechar_btn.is_visible(timeout=2000):
                        await fechar_btn.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass
                
                # Extrai cards da semana
                cards_semana = await extrair_cards_de_semana(page, semana)
                todos_cards.extend(cards_semana)
            
            # 5. Salva resultados
            if todos_cards:
                arquivo = await salvar_resultados(todos_cards)
                
                # Resumo final
                semanas_com_cards = len(set(card["semana"] for card in todos_cards))
                
                print("\n" + "="*50)
                print("🎉 EXTRAÇÃO CONCLUÍDA!")
                print("="*50)
                print(f"📊 {len(todos_cards)} cards extraídos")
                print(f"📚 {semanas_com_cards} semanas processadas")
                print(f"📁 Arquivo: {arquivo}")
                print("="*50)
                
                logger.info("🎉 Extração completa finalizada!")
            else:
                logger.warning("⚠️ Nenhum card foi extraído")
            
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
        finally:
            await browser.close()
    
    duration = time.time() - start_time
    logger.info(f"⏱️ Tempo total: {duration:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
