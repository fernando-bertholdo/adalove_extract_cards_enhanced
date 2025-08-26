import asyncio
import csv
import time
import logging
from datetime import datetime
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os
import json

# Configuração do sistema de logging
def configurar_logging():
    """
    Configura o sistema de logging para arquivo e console
    """
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dados_extraidos", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/extracao_completa_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Iniciando extração completa - Log: {log_filename}")
    return logger

# Carregar variáveis do arquivo .env
load_dotenv()

LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

logger = configurar_logging()

async def fazer_login_inteligente(page):
    """
    Função de login inteligente (mesma do script anterior)
    """
    logger.info("🔑 Iniciando processo de login inteligente...")
    
    try:
        logger.info("🔑 Procurando botão 'Entrar com o Google'...")
        botao_google = page.get_by_role("button", name="Entrar com o Google")
        
        if await botao_google.is_visible(timeout=10000):
            logger.info("✅ Botão Google encontrado, clicando...")
            await botao_google.click()
        else:
            logger.error("❌ Botão 'Entrar com o Google' não encontrado")
            return False
        
        await page.wait_for_timeout(4000)
        current_url = page.url
        logger.info(f"📍 URL após click no botão Google: {current_url}")
        
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
        logger.error(f"❌ Erro no processo de login: {str(e)}")
        return False

async def fazer_login_google_completo(page):
    """
    Faz o login completo no Google (email + senha)
    """
    logger.info("📧 Iniciando login completo no Google...")
    
    try:
        # Email
        logger.info("📧 Procurando campo de email...")
        seletores_email = ["input[type='email']", "#identifierId", "input[name='identifier']"]
        
        email_preenchido = False
        for seletor in seletores_email:
            try:
                campo_email = page.locator(seletor)
                await expect(campo_email).to_be_visible(timeout=10000)
                await campo_email.fill(LOGIN)
                email_preenchido = True
                logger.info(f"✅ Email preenchido com: {seletor}")
                break
            except:
                continue
                
        if not email_preenchido:
            logger.error("❌ Não foi possível preencher o email")
            return False
        
        # Próxima
        logger.info("➡️ Procurando botão 'Próxima'...")
        botoes_proxima = ["Próxima", "Next", "Continue"]
        
        for texto_botao in botoes_proxima:
            try:
                botao = page.get_by_role("button", name=texto_botao)
                await botao.click(timeout=5000)
                logger.info(f"✅ Clicou em: {texto_botao}")
                break
            except:
                continue
        
        await page.wait_for_timeout(5000)
        
        # Senha
        logger.info("🔐 Procurando campo de senha...")
        seletores_senha = ["input[type='password']", "input[name='password']"]
        
        senha_preenchida = False
        for seletor in seletores_senha:
            try:
                campo_senha = page.locator(seletor)
                await expect(campo_senha).to_be_visible(timeout=15000)
                await campo_senha.fill(SENHA)
                senha_preenchida = True
                logger.info(f"✅ Senha preenchida com: {seletor}")
                break
            except:
                continue
                
        if not senha_preenchida:
            logger.error("❌ Não foi possível preencher a senha")
            return False
        
        # Botão final
        logger.info("🎯 Finalizando login...")
        for texto_botao in botoes_proxima:
            try:
                botao = page.get_by_role("button", name=texto_botao)
                await botao.click(timeout=5000)
                logger.info(f"✅ Clicou no botão final: {texto_botao}")
                break
            except:
                continue
        
        # Aguarda redirecionamento
        logger.info("⏳ Aguardando redirecionamento para AdaLove...")
        for i in range(30):
            await page.wait_for_timeout(1000)
            current_url = page.url
            
            if "adalove.inteli.edu.br" in current_url and ("feed" in current_url or "/login" not in current_url):
                logger.info("✅ Login Google completo!")
                return True
                
        logger.error("❌ Timeout no redirecionamento")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro no login Google: {str(e)}")
        return False

async def navegar_para_academic_life(page):
    """
    Navega para academic-life
    """
    logger.info("🏠 Navegando para academic-life...")
    
    try:
        current_url = page.url
        logger.info(f"📍 URL atual: {current_url}")
        
        target_url = "https://adalove.inteli.edu.br/academic-life"
        logger.info(f"🎯 Navegando para: {target_url}")
        
        await page.goto(target_url)
        await page.wait_for_timeout(3000)
        
        current_url = page.url
        logger.info(f"📍 Nova URL: {current_url}")
        
        if "academic-life" in current_url:
            logger.info("✅ Navegação para academic-life bem-sucedida!")
            return True
        else:
            logger.warning(f"⚠️ URL não contém 'academic-life': {current_url}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao navegar: {str(e)}")
        return False

async def fechar_popup_faltas(page):
    """
    Fecha popup de faltas se aparecer
    """
    logger.info("🚫 Verificando popup de faltas...")
    
    try:
        await page.wait_for_timeout(3000)
        
        seletores_fechar = [
            "button:has-text('Fechar')",
            "[aria-label='Fechar']", 
            ".MuiButton-root:has-text('Fechar')",
            "[role='button']:has-text('Fechar')",
            ".close-button",
            ".popup-close"
        ]
        
        for seletor in seletores_fechar:
            try:
                botao_fechar = page.locator(seletor)
                if await botao_fechar.is_visible(timeout=3000):
                    await botao_fechar.click()
                    logger.info(f"✅ Popup fechado com: {seletor}")
                    await page.wait_for_timeout(2000)
                    return True
            except:
                continue
        
        logger.info("ℹ️ Nenhum popup detectado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao fechar popup: {str(e)}")
        return False

async def selecionar_turma_manual(page):
    """
    Permite seleção manual da turma (mais confiável)
    """
    logger.info("🎯 Iniciando seleção de turma...")
    
    print("\n" + "="*60)
    print("📋 SELEÇÃO DE TURMA - PROCESSO MANUAL")
    print("="*60)
    print("🤚 Para garantir precisão, vamos fazer a seleção manualmente:")
    print("1. Clique no seletor de turmas na página")
    print("2. Digite ou selecione a turma desejada")
    print("3. Clique na opção da turma")
    print("4. Aguarde a página carregar")
    print("5. Pressione Enter aqui no terminal quando concluído")
    print("="*60)
    
    input("⏸️ Pressione Enter após selecionar a turma na interface: ")
    
    logger.info("✅ Usuário confirmou seleção da turma")
    await page.wait_for_timeout(3000)
    
    return True

async def descobrir_semanas_disponiveis(page):
    """
    Descobre automaticamente todas as semanas disponíveis
    """
    logger.info("🔍 Descobrindo semanas disponíveis...")
    
    try:
        # Aguarda página carregar
        await page.wait_for_timeout(3000)
        
        # Procura por elementos que contenham "Semana"
        seletores_semanas = [
            "text=/Semana \\d+/",
            "text=/Week \\d+/", 
            "[class*='week']",
            "[data-week]",
            ".semana",
            ".week"
        ]
        
        semanas_encontradas = []
        
        # Tenta diferentes seletores
        for seletor in seletores_semanas:
            try:
                elementos = page.locator(seletor)
                count = await elementos.count()
                
                if count > 0:
                    logger.info(f"   🔍 Encontradas {count} semanas com seletor: {seletor}")
                    
                    for i in range(count):
                        try:
                            elemento = elementos.nth(i)
                            texto = await elemento.text_content()
                            
                            if texto and "semana" in texto.lower():
                                semanas_encontradas.append(texto.strip())
                                
                        except:
                            continue
                    
                    break
                    
            except Exception as e:
                logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                continue
        
        # Remove duplicatas e ordena
        semanas_unicas = list(set(semanas_encontradas))
        semanas_unicas.sort()
        
        logger.info(f"📊 Semanas descobertas: {len(semanas_unicas)}")
        for semana in semanas_unicas:
            logger.info(f"   📅 {semana}")
        
        if not semanas_unicas:
            # Fallback: tenta semanas padrão
            logger.warning("⚠️ Nenhuma semana encontrada automaticamente, usando padrão")
            semanas_unicas = [f"Semana {i:02d}" for i in range(1, 11)]
            logger.info("📅 Usando semanas padrão: Semana 01 a 10")
        
        return semanas_unicas
        
    except Exception as e:
        logger.error(f"❌ Erro ao descobrir semanas: {str(e)}")
        # Retorna semanas padrão
        return [f"Semana {i:02d}" for i in range(1, 11)]

async def extrair_cards_semana(page, nome_semana):
    """
    Extrai todos os cards de uma semana específica
    """
    logger.info(f"📋 Extraindo cards de: {nome_semana}")
    
    try:
        # Procura e clica na semana
        logger.info(f"   🔍 Procurando elemento da semana: {nome_semana}")
        
        elemento_semana = page.get_by_text(nome_semana, exact=False).first
        
        if await elemento_semana.is_visible(timeout=10000):
            await elemento_semana.click()
            logger.info(f"   ✅ Clicou na semana: {nome_semana}")
            await page.wait_for_timeout(3000)
        else:
            logger.warning(f"   ❌ Semana não encontrada: {nome_semana}")
            return []
        
        # Procura todos os cards
        logger.info("   🔍 Procurando cards...")
        
        seletores_cards = [
            "[data-rbd-draggable-id]",
            ".card",
            ".activity-card", 
            "[class*='card']",
            ".draggable-card"
        ]
        
        cards_encontrados = []
        
        for seletor in seletores_cards:
            try:
                cards = page.locator(seletor)
                count = await cards.count()
                
                if count > 0:
                    logger.info(f"   ✅ {count} cards encontrados com: {seletor}")
                    
                    # Extrai informações de cada card
                    for i in range(count):
                        try:
                            card = cards.nth(i)
                            card_info = await extrair_dados_card(card, i, nome_semana)
                            
                            if card_info:
                                cards_encontrados.append(card_info)
                                
                        except Exception as e:
                            logger.warning(f"   ⚠️ Erro ao extrair card {i}: {str(e)}")
                            continue
                    
                    break
                    
            except Exception as e:
                logger.debug(f"   ❌ Seletor falhou: {seletor} - {str(e)}")
                continue
        
        logger.info(f"   📊 Total extraído: {len(cards_encontrados)} cards")
        return cards_encontrados
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair cards da {nome_semana}: {str(e)}")
        return []

async def extrair_dados_card(card, indice, semana):
    """
    Extrai dados detalhados de um card individual
    """
    try:
        card_data = {
            "semana": semana,
            "indice": indice + 1,
            "id": "",
            "titulo": "",
            "descricao": "",
            "tipo": "",
            "status": "",
            "data_entrega": "",
            "tags": "",
            "link": "",
            "texto_completo": ""
        }
        
        # ID do card (se disponível)
        try:
            id_element = await card.get_attribute("data-rbd-draggable-id")
            if id_element:
                card_data["id"] = id_element
        except:
            pass
        
        # Título (procura em diferentes elementos)
        seletores_titulo = [
            "h1", "h2", "h3", "h4", "h5", "h6",
            ".title", ".card-title", ".activity-title",
            "[class*='title']", ".name", ".card-name"
        ]
        
        for seletor in seletores_titulo:
            try:
                titulo_elem = card.locator(seletor).first
                if await titulo_elem.count() > 0:
                    titulo = await titulo_elem.text_content()
                    if titulo and titulo.strip():
                        card_data["titulo"] = titulo.strip()
                        break
            except:
                continue
        
        # Descrição
        seletores_descricao = [
            ".description", ".card-description", ".activity-description",
            "[class*='description']", ".content", ".card-content", 
            ".text", ".card-text", "p"
        ]
        
        for seletor in seletores_descricao:
            try:
                desc_elem = card.locator(seletor).first
                if await desc_elem.count() > 0:
                    descricao = await desc_elem.text_content()
                    if descricao and descricao.strip():
                        card_data["descricao"] = descricao.strip()
                        break
            except:
                continue
        
        # Tipo/Categoria
        seletores_tipo = [
            ".type", ".card-type", ".category", ".tag",
            "[class*='type']", "[class*='category']",
            ".badge", ".label"
        ]
        
        for seletor in seletores_tipo:
            try:
                tipo_elem = card.locator(seletor).first
                if await tipo_elem.count() > 0:
                    tipo = await tipo_elem.text_content()
                    if tipo and tipo.strip():
                        card_data["tipo"] = tipo.strip()
                        break
            except:
                continue
        
        # Data de entrega
        seletores_data = [
            ".date", ".due-date", ".deadline", ".card-date",
            "[class*='date']", "[class*='due']", 
            "time", ".timestamp"
        ]
        
        for seletor in seletores_data:
            try:
                data_elem = card.locator(seletor).first
                if await data_elem.count() > 0:
                    data = await data_elem.text_content()
                    if data and data.strip():
                        card_data["data_entrega"] = data.strip()
                        break
            except:
                continue
        
        # Link (se houver)
        try:
            link_elem = card.locator("a").first
            if await link_elem.count() > 0:
                link = await link_elem.get_attribute("href")
                if link:
                    card_data["link"] = link
        except:
            pass
        
        # Texto completo do card como fallback
        try:
            texto_completo = await card.text_content()
            if texto_completo:
                card_data["texto_completo"] = texto_completo.strip()
        except:
            pass
        
        # Se não conseguiu título, usa parte do texto completo
        if not card_data["titulo"] and card_data["texto_completo"]:
            linhas = card_data["texto_completo"].split('\n')
            primeira_linha = next((linha.strip() for linha in linhas if linha.strip()), "")
            if primeira_linha:
                card_data["titulo"] = primeira_linha[:100]  # Limita a 100 caracteres
        
        return card_data
        
    except Exception as e:
        logger.warning(f"   ⚠️ Erro ao extrair dados do card {indice}: {str(e)}")
        return None

async def salvar_dados_csv(dados, timestamp):
    """
    Salva os dados extraídos em CSV
    """
    logger.info("💾 Salvando dados em CSV...")
    
    try:
        filename = f"dados_extraidos/cards_adalove_{timestamp}.csv"
        
        if not dados:
            logger.warning("⚠️ Nenhum dado para salvar")
            return
        
        # Headers do CSV
        headers = [
            "semana", "indice", "id", "titulo", "descricao", 
            "tipo", "status", "data_entrega", "tags", "link", "texto_completo"
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for linha in dados:
                writer.writerow(linha)
        
        logger.info(f"✅ Dados salvos em: {filename}")
        logger.info(f"📊 Total de cards salvos: {len(dados)}")
        
        return filename
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar CSV: {str(e)}")
        return None

async def salvar_dados_json(dados, timestamp):
    """
    Salva os dados extraídos em JSON (backup)
    """
    logger.info("💾 Salvando dados em JSON...")
    
    try:
        filename = f"dados_extraidos/cards_adalove_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(dados, jsonfile, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Backup JSON salvo em: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar JSON: {str(e)}")
        return None

async def gerar_relatorio_extracao(dados, timestamp):
    """
    Gera relatório resumido da extração
    """
    logger.info("📊 Gerando relatório da extração...")
    
    try:
        filename = f"dados_extraidos/relatorio_extracao_{timestamp}.txt"
        
        # Análise dos dados
        total_cards = len(dados)
        semanas_processadas = set(card["semana"] for card in dados)
        cards_por_semana = {}
        
        for semana in semanas_processadas:
            cards_por_semana[semana] = sum(1 for card in dados if card["semana"] == semana)
        
        # Gera relatório
        relatorio = []
        relatorio.append("📋 RELATÓRIO DE EXTRAÇÃO - ADALOVE CARDS")
        relatorio.append("=" * 60)
        relatorio.append(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append(f"👤 Usuário: {LOGIN}")
        relatorio.append("")
        relatorio.append("📊 RESUMO GERAL")
        relatorio.append("-" * 30)
        relatorio.append(f"🎯 Total de cards extraídos: {total_cards}")
        relatorio.append(f"📚 Semanas processadas: {len(semanas_processadas)}")
        relatorio.append("")
        relatorio.append("📈 CARDS POR SEMANA")
        relatorio.append("-" * 30)
        
        for semana in sorted(semanas_processadas):
            count = cards_por_semana[semana]
            relatorio.append(f"   {semana}: {count} cards")
        
        relatorio.append("")
        relatorio.append("🔍 TIPOS DE DADOS EXTRAÍDOS")
        relatorio.append("-" * 30)
        relatorio.append("✅ Semana")
        relatorio.append("✅ Índice do card")
        relatorio.append("✅ ID (quando disponível)")
        relatorio.append("✅ Título")
        relatorio.append("✅ Descrição")
        relatorio.append("✅ Tipo/Categoria")
        relatorio.append("✅ Data de entrega")
        relatorio.append("✅ Links")
        relatorio.append("✅ Texto completo")
        
        # Salva relatório
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(relatorio))
        
        logger.info(f"✅ Relatório salvo em: {filename}")
        
        # Mostra resumo no console
        print("\n" + "="*60)
        print("📊 EXTRAÇÃO CONCLUÍDA!")
        print("="*60)
        print(f"🎯 Total de cards extraídos: {total_cards}")
        print(f"📚 Semanas processadas: {len(semanas_processadas)}")
        print(f"📁 Dados salvos em: dados_extraidos/")
        print("="*60)
        
        return filename
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {str(e)}")
        return None

async def main():
    """
    Função principal - Extração completa
    """
    logger.info("🚀 Iniciando EXTRAÇÃO COMPLETA do AdaLove...")
    logger.info(f"👤 Usuário: {LOGIN}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()
    todos_os_cards = []

    async with async_playwright() as p:
        try:
            logger.info("🌐 Iniciando navegador...")
            browser = await p.chromium.launch(channel="chrome", headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 1. Login
            logger.info("🔐 Fazendo login...")
            await page.goto("https://adalove.inteli.edu.br/")
            await page.wait_for_timeout(3000)
            
            login_sucesso = await fazer_login_inteligente(page)
            
            if not login_sucesso:
                logger.error("❌ Falha no login automático")
                print("\n🤚 Por favor, faça login manualmente na página")
                input("⏸️ Pressione Enter após fazer login: ")
                logger.info("✅ Login manual confirmado")
            
            # 2. Navegação
            logger.info("🏠 Navegando para academic-life...")
            await navegar_para_academic_life(page)
            
            # 3. Fecha popup
            await fechar_popup_faltas(page)
            
            # 4. Seleção de turma (manual)
            logger.info("🎯 Selecionando turma...")
            await selecionar_turma_manual(page)
            
            # 5. Fecha popup novamente
            await fechar_popup_faltas(page)
            
            # 6. Descobre semanas disponíveis
            logger.info("🔍 Descobrindo semanas disponíveis...")
            semanas = await descobrir_semanas_disponiveis(page)
            
            if not semanas:
                logger.error("❌ Nenhuma semana encontrada")
                return
            
            logger.info(f"📚 {len(semanas)} semanas para processar")
            
            # 7. Extração de cada semana
            logger.info("📋 Iniciando extração por semana...")
            
            for i, semana in enumerate(semanas, 1):
                logger.info(f"🔄 Processando {semana} ({i}/{len(semanas)})")
                
                # Volta para academic-life antes de cada semana
                await page.goto("https://adalove.inteli.edu.br/academic-life")
                await page.wait_for_timeout(3000)
                await fechar_popup_faltas(page)
                
                # Extrai cards da semana
                cards_semana = await extrair_cards_semana(page, semana)
                
                if cards_semana:
                    todos_os_cards.extend(cards_semana)
                    logger.info(f"   ✅ {len(cards_semana)} cards extraídos de {semana}")
                else:
                    logger.warning(f"   ⚠️ Nenhum card extraído de {semana}")
                
                # Pequena pausa entre semanas
                await page.wait_for_timeout(2000)
            
            # 8. Salva resultados
            logger.info("💾 Salvando resultados...")
            
            if todos_os_cards:
                # Salva CSV
                arquivo_csv = await salvar_dados_csv(todos_os_cards, timestamp)
                
                # Salva JSON backup
                arquivo_json = await salvar_dados_json(todos_os_cards, timestamp)
                
                # Gera relatório
                arquivo_relatorio = await gerar_relatorio_extracao(todos_os_cards, timestamp)
                
                logger.info("🎉 EXTRAÇÃO COMPLETA FINALIZADA!")
                
            else:
                logger.error("❌ Nenhum card foi extraído")
                
        except Exception as e:
            logger.error(f"❌ Erro geral: {str(e)}")
            
        finally:
            logger.info("🔚 Finalizando navegador...")
            await context.close()
            await browser.close()

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"⏱️ Extração concluída em {duration:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
