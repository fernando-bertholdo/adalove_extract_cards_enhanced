import asyncio
import csv
import time
import logging
import os
from datetime import datetime
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv

def configurar_logging(nome_turma):
    """Configura logging com nome da turma"""
    os.makedirs("logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{nome_turma}_{timestamp}.log"
    
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

# Carregar variáveis do .env
load_dotenv()
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

async def fazer_login_inteligente(page, logger):
    """Login automático com fallback manual"""
    logger.info("🔑 Fazendo login...")
    
    try:
        # Tenta login automático
        botao_google = page.get_by_role("button", name="Entrar com o Google")
        if await botao_google.is_visible(timeout=10000):
            await botao_google.click()
            await page.wait_for_timeout(3000)
            
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
        for _ in range(20):
            await page.wait_for_timeout(1000)
            if "adalove.inteli.edu.br" in page.url and "/login" not in page.url:
                logger.info("✅ Login realizado!")
                return True
        
        # Fallback manual
        logger.warning("⚠️ Login automático falhou - intervenção manual")
        print("\n🤚 Complete o login manualmente se necessário")
        input("⏸️ Pressione Enter quando estiver logado: ")
        logger.info("✅ Login confirmado pelo usuário")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

async def navegar_academic_life(page, logger):
    """Navega para academic-life e fecha popups"""
    logger.info("🏠 Navegando para academic-life...")
    
    await page.goto("https://adalove.inteli.edu.br/academic-life")
    await page.wait_for_timeout(3000)
    
    # Fecha popup de faltas se aparecer
    try:
        fechar_btn = page.locator("button:has-text('Fechar')").first
        if await fechar_btn.is_visible(timeout=3000):
            await fechar_btn.click()
            await page.wait_for_timeout(2000)
            logger.info("✅ Popup fechado")
    except:
        pass
    
    logger.info("✅ Página academic-life carregada")

async def selecionar_turma_e_obter_nome(page, logger):
    """Seleção manual de turma + input do nome para organização"""
    print("\n" + "="*60)
    print("🎯 SELEÇÃO DE TURMA E ORGANIZAÇÃO")
    print("="*60)
    print("📋 PASSO 1: Selecionar turma na interface")
    print("   1. Clique no dropdown de turmas")
    print("   2. Digite/selecione a turma desejada")
    print("   3. Clique na turma para acessá-la")
    print("   4. Aguarde a página carregar")
    print("")
    print("📝 PASSO 2: Informar nome para organização")
    print("   O script criará uma pasta com este nome em 'dados_extraidos/'")
    print("="*60)
    
    # Input do nome da turma para organização
    nome_turma = input("📁 Digite o nome da turma para criar a pasta de organização: ").strip()
    
    if not nome_turma:
        nome_turma = f"turma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.warning(f"⚠️ Nome não informado, usando: {nome_turma}")
    
    logger.info(f"📁 Turma para organização: '{nome_turma}'")
    
    print(f"\n✅ Pasta será criada: dados_extraidos/{nome_turma}/")
    print("👆 Agora selecione a turma na interface da página")
    
    input("⏸️ Pressione Enter após selecionar a turma: ")
    logger.info("✅ Turma selecionada pelo usuário")
    await page.wait_for_timeout(3000)
    
    return nome_turma

async def descobrir_semanas(page, logger):
    """Descobre semanas disponíveis automaticamente"""
    logger.info("🔍 Descobrindo semanas disponíveis...")
    
    try:
        await page.wait_for_timeout(3000)
        
        # Procura por elementos que contenham "Semana"
        elementos_semana = page.locator("text=/Semana \\d+/i")
        count = await elementos_semana.count()
        
        semanas_encontradas = []
        
        if count > 0:
            logger.info(f"   🔍 Encontradas {count} semanas")
            
            for i in range(count):
                try:
                    elemento = elementos_semana.nth(i)
                    texto = await elemento.text_content()
                    if texto and texto.strip():
                        semanas_encontradas.append(texto.strip())
                except:
                    continue
        
        # Remove duplicatas e ordena
        semanas_unicas = sorted(list(set(semanas_encontradas)))
        
        if not semanas_unicas:
            # Fallback para semanas padrão
            logger.warning("⚠️ Usando semanas padrão")
            semanas_unicas = [f"Semana {i:02d}" for i in range(1, 11)]
        
        logger.info(f"📊 {len(semanas_unicas)} semanas descobertas:")
        for semana in semanas_unicas:
            logger.info(f"   📅 {semana}")
            
        return semanas_unicas
        
    except Exception as e:
        logger.error(f"❌ Erro ao descobrir semanas: {e}")
        return [f"Semana {i:02d}" for i in range(1, 11)]

async def extrair_dados_card_completo(card, indice, semana, logger):
    """Extrai dados completos do card incluindo links e materiais"""
    try:
        card_data = {
            "semana": semana,
            "indice": indice + 1,
            "id": "",
            "titulo": "",
            "descricao": "",
            "tipo": "",
            "texto_completo": "",
            "links": "",
            "materiais": "",
            "arquivos": ""
        }
        
        # ID do card
        try:
            card_id = await card.get_attribute("data-rbd-draggable-id")
            if card_id:
                card_data["id"] = card_id
        except:
            pass
        
        # Texto completo do card
        try:
            texto_completo = await card.text_content()
            if texto_completo:
                card_data["texto_completo"] = texto_completo.strip()
        except:
            pass
        
        # Título (primeira linha não vazia)
        if card_data["texto_completo"]:
            linhas = card_data["texto_completo"].split('\n')
            primeira_linha = next((linha.strip() for linha in linhas if linha.strip()), "")
            if primeira_linha:
                card_data["titulo"] = primeira_linha
        
        # Descrição (resto do texto, limitado)
        if card_data["texto_completo"] and card_data["titulo"]:
            resto_texto = card_data["texto_completo"].replace(card_data["titulo"], "", 1).strip()
            if resto_texto:
                card_data["descricao"] = resto_texto[:500]  # Limita descrição
        
        # *** EXTRAÇÃO DE LINKS E MATERIAIS ***
        links_encontrados = []
        materiais_encontrados = []
        arquivos_encontrados = []
        
        # Procura todos os links no card
        try:
            links_elementos = card.locator("a")
            count_links = await links_elementos.count()
            
            for i in range(count_links):
                try:
                    link_elem = links_elementos.nth(i)
                    href = await link_elem.get_attribute("href")
                    texto_link = await link_elem.text_content()
                    
                    if href:
                        # Categoriza o link
                        if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.zip']):
                            arquivos_encontrados.append(f"{texto_link.strip() if texto_link else 'Arquivo'}: {href}")
                        elif any(material in href.lower() for material in ['drive.google', 'docs.google', 'sheets.google']):
                            materiais_encontrados.append(f"{texto_link.strip() if texto_link else 'Material'}: {href}")
                        else:
                            links_encontrados.append(f"{texto_link.strip() if texto_link else 'Link'}: {href}")
                            
                except Exception as e:
                    logger.debug(f"   Erro ao processar link {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"   Erro ao procurar links: {e}")
        
        # Procura imagens e outros recursos
        try:
            imgs = card.locator("img")
            count_imgs = await imgs.count()
            
            for i in range(count_imgs):
                try:
                    img = imgs.nth(i)
                    src = await img.get_attribute("src")
                    alt = await img.get_attribute("alt")
                    
                    if src:
                        materiais_encontrados.append(f"Imagem {alt or 'sem título'}: {src}")
                        
                except:
                    continue
                    
        except:
            pass
        
        # Converte listas para strings
        card_data["links"] = " | ".join(links_encontrados) if links_encontrados else ""
        card_data["materiais"] = " | ".join(materiais_encontrados) if materiais_encontrados else ""
        card_data["arquivos"] = " | ".join(arquivos_encontrados) if arquivos_encontrados else ""
        
        # Tenta identificar tipo do card baseado no conteúdo
        texto_lower = card_data["texto_completo"].lower()
        if any(palavra in texto_lower for palavra in ['atividade', 'exercício', 'tarefa']):
            card_data["tipo"] = "Atividade"
        elif any(palavra in texto_lower for palavra in ['projeto', 'entrega']):
            card_data["tipo"] = "Projeto"
        elif any(palavra in texto_lower for palavra in ['quiz', 'prova', 'avaliação']):
            card_data["tipo"] = "Avaliação"
        elif any(palavra in texto_lower for palavra in ['material', 'leitura', 'conteúdo']):
            card_data["tipo"] = "Material"
        else:
            card_data["tipo"] = "Outros"
        
        return card_data
        
    except Exception as e:
        logger.warning(f"   ⚠️ Erro ao extrair card {indice}: {e}")
        return None

async def extrair_cards_semana(page, nome_semana, logger):
    """Extrai todos os cards de uma semana"""
    logger.info(f"📋 Extraindo: {nome_semana}")
    
    try:
        # Procura e clica na semana
        semana_element = page.get_by_text(nome_semana, exact=False).first
        
        if await semana_element.is_visible(timeout=10000):
            await semana_element.click()
            await page.wait_for_timeout(3000)
            
            # Procura cards
            cards = page.locator("[data-rbd-draggable-id]")
            count = await cards.count()
            
            if count > 0:
                logger.info(f"   ✅ {count} cards encontrados")
                
                cards_data = []
                for i in range(count):
                    try:
                        card = cards.nth(i)
                        card_info = await extrair_dados_card_completo(card, i, nome_semana, logger)
                        
                        if card_info:
                            cards_data.append(card_info)
                            
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro no card {i+1}: {e}")
                        continue
                
                logger.info(f"   📊 {len(cards_data)} cards processados com sucesso")
                return cards_data
            else:
                logger.warning(f"   ❌ Nenhum card encontrado em {nome_semana}")
                return []
        else:
            logger.warning(f"   ❌ Semana não encontrada: {nome_semana}")
            return []
            
    except Exception as e:
        logger.error(f"   ❌ Erro ao processar {nome_semana}: {e}")
        return []

async def salvar_dados_organizados(dados, nome_turma, logger):
    """Salva dados na pasta da turma"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Cria pasta da turma
    pasta_turma = f"dados_extraidos/{nome_turma}"
    os.makedirs(pasta_turma, exist_ok=True)
    
    filename = f"{pasta_turma}/cards_completos_{timestamp}.csv"
    
    logger.info(f"💾 Salvando {len(dados)} cards em: {filename}")
    
    try:
        headers = [
            "semana", "indice", "id", "titulo", "descricao", "tipo",
            "texto_completo", "links", "materiais", "arquivos"
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(dados)
        
        logger.info(f"✅ Dados salvos com sucesso!")
        
        # Estatísticas por semana
        semanas_stats = {}
        for card in dados:
            semana = card["semana"]
            if semana not in semanas_stats:
                semanas_stats[semana] = {"cards": 0, "links": 0, "materiais": 0}
            
            semanas_stats[semana]["cards"] += 1
            if card["links"]:
                semanas_stats[semana]["links"] += len(card["links"].split(" | "))
            if card["materiais"]:
                semanas_stats[semana]["materiais"] += len(card["materiais"].split(" | "))
        
        logger.info("📊 Estatísticas por semana:")
        for semana, stats in semanas_stats.items():
            logger.info(f"   {semana}: {stats['cards']} cards, {stats['links']} links, {stats['materiais']} materiais")
        
        return filename, pasta_turma
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar: {e}")
        return None, None

async def main():
    """Função principal - Extração completa organizada"""
    print("\n" + "="*60)
    print("🚀 ADALOVE CARDS EXTRACTOR - VERSÃO FINAL")
    print("="*60)
    print("📋 Este script faz extração completa incluindo:")
    print("   ✅ Títulos e descrições dos cards")
    print("   ✅ Links e materiais anexados")  
    print("   ✅ Arquivos e documentos")
    print("   ✅ Organização por pasta da turma")
    print("="*60)
    
    # Solicita nome da turma antes de começar
    nome_turma = input("📁 Digite o nome da turma para organizar os dados: ").strip()
    if not nome_turma:
        nome_turma = f"turma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"⚠️ Nome não informado, usando: {nome_turma}")
    
    logger = configurar_logging(nome_turma)
    logger.info(f"🚀 Iniciando extração para turma: {nome_turma}")
    
    start_time = time.time()
    todos_cards = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        page = await browser.new_page()
        
        try:
            # 1. Login
            await page.goto("https://adalove.inteli.edu.br/")
            if not await fazer_login_inteligente(page, logger):
                logger.error("❌ Falha no login")
                return
            
            # 2. Academic-life
            await navegar_academic_life(page, logger)
            
            # 3. Seleção manual da turma
            print(f"\n📁 Dados serão salvos em: dados_extraidos/{nome_turma}/")
            print("👆 Agora selecione a turma na interface:")
            input("⏸️ Pressione Enter após selecionar a turma na página: ")
            logger.info("✅ Turma selecionada")
            await page.wait_for_timeout(3000)
            
            # 4. Fecha popup novamente
            try:
                fechar_btn = page.locator("button:has-text('Fechar')").first
                if await fechar_btn.is_visible(timeout=2000):
                    await fechar_btn.click()
                    await page.wait_for_timeout(1000)
            except:
                pass
            
            # 5. Descobre semanas
            semanas = await descobrir_semanas(page, logger)
            
            # 6. Extrai cada semana
            logger.info(f"📚 Processando {len(semanas)} semanas...")
            
            for i, semana in enumerate(semanas, 1):
                logger.info(f"🔄 {semana} ({i}/{len(semanas)})")
                
                # Volta para academic-life
                await page.goto("https://adalove.inteli.edu.br/academic-life")
                await page.wait_for_timeout(2000)
                
                # Fecha popup
                try:
                    fechar_btn = page.locator("button:has-text('Fechar')").first
                    if await fechar_btn.is_visible(timeout=2000):
                        await fechar_btn.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass
                
                # Extrai cards da semana
                cards_semana = await extrair_cards_semana(page, semana, logger)
                todos_cards.extend(cards_semana)
            
            # 7. Salva resultados organizados
            if todos_cards:
                arquivo, pasta = await salvar_dados_organizados(todos_cards, nome_turma, logger)
                
                if arquivo:
                    # Resumo final
                    semanas_processadas = len(set(card["semana"] for card in todos_cards))
                    total_links = sum(1 for card in todos_cards if card["links"])
                    total_materiais = sum(1 for card in todos_cards if card["materiais"])
                    
                    print("\n" + "="*60)
                    print("🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
                    print("="*60)
                    print(f"📊 {len(todos_cards)} cards extraídos")
                    print(f"📚 {semanas_processadas} semanas processadas")
                    print(f"🔗 {total_links} cards com links")
                    print(f"📎 {total_materiais} cards com materiais")
                    print(f"📁 Pasta: {pasta}")
                    print(f"💾 Arquivo: {os.path.basename(arquivo)}")
                    print("="*60)
                    
                    logger.info("🎉 Extração finalizada com sucesso!")
                else:
                    logger.error("❌ Erro ao salvar dados")
            else:
                logger.warning("⚠️ Nenhum card foi extraído")
                
        except Exception as e:
            logger.error(f"❌ Erro geral: {e}")
        finally:
            await browser.close()
    
    duration = time.time() - start_time
    logger.info(f"⏱️ Tempo total: {duration:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
