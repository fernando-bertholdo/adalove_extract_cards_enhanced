"""
Extração de dados de cards individuais.
"""

import re
import logging
from typing import Optional
from playwright.async_api import Page, Locator

from ..browser.navigator import close_modal_if_open
from ..models.card_types import (
    ICON_TO_CARD_TYPE, 
    CARD_TYPE_FIELDS, 
    get_card_type_from_icon,
    get_expected_fields,
    should_extract_field
)


# Regex para URLs válidas
HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)


async def extract_card_data(
    card: Locator,
    indice: int,
    semana: str,
    page: Page,
    logger: logging.Logger,
    extract_references: bool = False
) -> Optional[dict]:
    """
    Extrai dados completos de um card (lista + modal).
    
    Passos:
    1. Lê informação visível no card da lista
    2. Abre modal do card para capturar texto completo
    3. Extrai todos os links/materiais/arquivos
    4. Classifica tipo heurístico
    5. Fecha modal robustamente
    
    Args:
        card: Locator do card no Playwright
        indice: Índice do card na lista (0-based)
        semana: Nome da semana (ex: "Semana 01")
        page: Página do Playwright
        logger: Logger para mensagens
        
    Returns:
        Dicionário com dados do card ou None se erro
    """
    try:
        card_data = {
            "semana": semana,
            "indice": indice + 1,  # 1-indexed para usuário
            "id": "",
            "titulo": "",
            "descricao": "",
            "tipo": "",
            "texto_completo": "",
            "links": "",
            "materiais": "",
            "arquivos": ""
        }
        
        # === Extração da lista ===
        
        # ID do card
        try:
            card_id = await card.get_attribute("data-rbd-draggable-id")
            if card_id:
                card_data["id"] = card_id
        except Exception:
            pass
        
        # Texto completo do card (visível na lista)
        try:
            texto_completo = await card.text_content()
            if texto_completo:
                card_data["texto_completo"] = texto_completo.strip()
        except Exception:
            pass
        
        # Título (primeira linha não vazia)
        if card_data["texto_completo"]:
            linhas = card_data["texto_completo"].split('\n')
            primeira_linha = next((ln.strip() for ln in linhas if ln.strip()), "")
            if primeira_linha:
                card_data["titulo"] = primeira_linha
        
        # Descrição (resto do texto, integral)
        if card_data["texto_completo"] and card_data["titulo"]:
            resto_texto = card_data["texto_completo"].replace(
                card_data["titulo"], "", 1
            ).strip()
            if resto_texto:
                card_data["descricao"] = resto_texto  # Descrição integral, sem limite
        
        # === Extração de links da lista ===
        links_encontrados = []
        materiais_encontrados = []
        arquivos_encontrados = []
        
        try:
            links_elementos = card.locator("a")
            count_links = await links_elementos.count()
            
            for i in range(count_links):
                try:
                    link_elem = links_elementos.nth(i)
                    href = await link_elem.get_attribute("href")
                    texto_link = await link_elem.text_content()
                    
                    if href:
                        _categorize_url(
                            href, 
                            texto_link or "Link",
                            links_encontrados,
                            materiais_encontrados,
                            arquivos_encontrados
                        )
                except Exception as e:
                    logger.debug(f"   Erro ao processar link {i}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"   Erro ao procurar links: {e}")
        
        # === Abertura do modal ===
        try:
            logger.debug(f"   🔍 Iniciando extração do card {indice+1}")
            logger.debug(f"   🖱️ Clicando no card...")
            await card.click()
            await page.wait_for_timeout(600)
            logger.debug(f"   ✅ Card clicado")
            
            logger.debug(f"   ⏳ Aguardando modal aparecer...")
            
            # ESTRATÉGIA ROBUSTA: Aguarda modal aparecer com múltiplos seletores
            modal = None
            modal_selectors = [
                "[role='dialog']",
                ".MuiModal-root",
                "[class*='Modal']",
                "[class*='modal']",
                ".modal",
                "[data-testid*='modal']"
            ]
            
            for selector in modal_selectors:
                try:
                    logger.debug(f"   🔍 Tentando seletor: {selector}")
                    temp_modal = page.locator(selector).first
                    await temp_modal.wait_for(state="visible", timeout=2000)
                    modal = temp_modal
                    logger.debug(f"   ✅ Modal encontrado com seletor: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"   ⚠️ Seletor {selector} falhou: {e}")
                    continue
            
            if modal:
                logger.debug(f"   ✅ Modal visível e pronto!")
                
                # Aguarda elementos específicos do modal carregarem
                try:
                    await modal.locator("div").first.wait_for(state="visible", timeout=2000)
                    logger.debug(f"   ✅ Conteúdo do modal carregado")
                except Exception as e:
                    logger.debug(f"   ⚠️ Aguardando conteúdo do modal: {e}")
                
                if True:  # Modal encontrado e visível
                    logger.debug(f"   ✅ Modal visível")
                    
                    # Log do HTML do modal para debug
                    modal_html = await modal.inner_html()
                    logger.debug(f"   📄 Modal HTML ({len(modal_html)} chars)")
                    
                    # Aguarda loading overlay desaparecer
                    try:
                        await page.wait_for_selector("[class*='MuiCircularProgress'], [class*='loading']", state="hidden", timeout=3000)
                        logger.debug(f"   ⏳ Loading overlay desapareceu")
                    except:
                        logger.debug(f"   ⏳ Sem loading overlay detectado")
                    
                    # === PASSO 1: IDENTIFICAR TIPO PELO ÍCONE (DETERMINÍSTICO) ===
                    card_type = "outros"  # fallback
                    icon_id = None
                    
                    try:
                        # Buscar elemento com id que termina em '-solido'
                        icon_elements = modal.locator("[id*='-solido']")
                        count = await icon_elements.count()
                        
                        logger.debug(f"   🔍 Encontrados {count} elementos com ícones")
                        
                        for i in range(count):
                            elem = icon_elements.nth(i)
                            icon_id = await elem.get_attribute("id")
                            
                            # Extrair nome do ícone (ex: "book-open-reader-solido")
                            if icon_id:
                                logger.debug(f"   🎯 Ícone encontrado: {icon_id}")
                                card_type = get_card_type_from_icon(icon_id)
                                if card_type != "outros":
                                    logger.info(f"   ✅ Tipo identificado por ícone: {card_type} ({icon_id})")
                                    break
                        
                        if card_type == "outros":
                            logger.warning(f"   ⚠️ Ícone não reconhecido, usando fallback heurístico")
                            card_type = _classify_card_type_fallback(card_data["texto_completo"])
                            
                    except Exception as e:
                        logger.debug(f"   ⚠️ Erro ao extrair ícone: {e}")
                        card_type = _classify_card_type_fallback(card_data["texto_completo"])
                    
                    card_data["card_type"] = card_type
                    
                    # === MODO DE EXTRAÇÃO DE REFERÊNCIAS ===
                    if extract_references:
                        await _extract_reference_html(modal, card_type, icon_id, logger)
                        # Continuar com extração normal mesmo no modo referência
                
                    # === Extração simplificada da descrição ===
                    try:
                        # Logs detalhados de cada elemento encontrado
                        logger.debug(f"   🔍 Buscando div.content-description-text...")
                        desc_divs = await modal.locator("div.content-description-text").count()
                        logger.debug(f"   📊 Encontrados {desc_divs} elementos content-description-text")
                        
                        logger.debug(f"   🔍 Buscando p dentro de content-description-text...")
                        desc_ps = await modal.locator("div.content-description-text p").count()
                        logger.debug(f"   📊 Encontrados {desc_ps} elementos p")
                        
                        # Extrai descrição COMPLETA diretamente (já está no HTML)
                        try:
                            # O texto completo está em div.content-description-text > p
                            desc_element = modal.locator("div.content-description-text p").first
                            if await desc_element.count() > 0:
                                full_text = await desc_element.text_content()
                                card_data["descricao"] = full_text.strip()
                                logger.info(f"   📝 Descrição extraída: {len(full_text)} caracteres")
                                logger.debug(f"   📄 Primeiros 100 chars: {full_text[:100]}...")
                            else:
                                logger.debug(f"   ⚠️ Nenhum elemento p encontrado em content-description-text")
                        except Exception as e:
                            logger.debug(f"   ⚠️ Erro ao extrair descrição: {e}")
                        
                        # === PASSO 2: EXTRAIR CAMPOS BASEADO NO TIPO ===
                        expected_fields = get_expected_fields(card_type)
                        
                        # Data/Hora (apenas se esperado para este tipo)
                        if should_extract_field(card_type, "has_data_hora"):
                            card_data["data_hora"] = await _extract_data_hora(modal, logger)
                        
                        # Professor (apenas se esperado para este tipo)
                        if should_extract_field(card_type, "has_professor"):
                            card_data["professor"] = await _extract_professor(modal, logger)
                        
                        # Atualiza texto_completo com descrição do modal
                        if card_data["descricao"]:
                        card_data["texto_completo"] = (
                                card_data["titulo"] + "\n\n" + card_data["descricao"]
                        ).strip()
                            logger.debug(f"   📝 Texto completo atualizado: {len(card_data['texto_completo'])} caracteres")
                        
                        # === Assuntos Relacionados (apenas se esperado para este tipo) ===
                        if should_extract_field(card_type, "has_assuntos_relacionados"):
                            assuntos_encontrados = await _extract_assuntos_relacionados(
                                modal, card_data["titulo"], logger
                            )
                            if assuntos_encontrados:
                                card_data["assuntos_relacionados"] = assuntos_encontrados
                                logger.info(f"   🔗 {len(assuntos_encontrados)} assuntos relacionados encontrados!")
                        
                        # === Conteúdos Relacionados (apenas se esperado para este tipo) ===
                        if should_extract_field(card_type, "has_conteudos_relacionados"):
                            conteudos_encontrados = await _extract_conteudos_relacionados(modal, logger)
                            if conteudos_encontrados:
                                card_data["conteudos_relacionados"] = conteudos_encontrados
                                logger.info(f"   📚 {len(conteudos_encontrados)} conteúdos relacionados encontrados!")
                                
                                # Atualizar campo materiais com conteúdos relacionados
                                materiais_list = [f"{c['titulo']}: {c['url']}" for c in conteudos_encontrados]
                                card_data["materiais"] = " | ".join(materiais_list)
                                logger.debug(f"   📦 Campo materiais atualizado com {len(materiais_list)} itens")
                    except Exception as e:
                        logger.debug(f"   ⚠️ Erro ao extrair descrição do modal: {e}")
                    pass
                
                # Links do modal
                try:
                    modal_links = modal.locator("a")
                    mcount = await modal_links.count()
                    
                    for j in range(mcount):
                        try:
                            a = modal_links.nth(j)
                            href = await a.get_attribute("href")
                            texta = (await a.text_content()) or ""
                            
                            if not href or not HTTP_RE.match(href):
                                continue
                            
                            _categorize_url(
                                href,
                                texta.strip() or "Link",
                                links_encontrados,
                                materiais_encontrados,
                                arquivos_encontrados
                            )
                        except Exception:
                            continue
                except Exception:
                    pass
                
                # Fechar modal
                try:
                    fechar = page.locator("button:has-text('Fechar')").first
                    if await fechar.is_visible(timeout=1000):
                        await fechar.click()
                        await page.wait_for_timeout(300)
                except Exception:
                    try:
                        await page.keyboard.press('Escape')
                    except Exception:
                        pass
            else:
                logger.debug(f"   ❌ Modal não encontrado com nenhum seletor")
        except Exception as e:
            logger.debug(f"   Modal não pôde ser aberto para card {indice+1}: {e}")
        
        # === Imagens e outros recursos ===
        try:
            imgs = card.locator("img")
            count_imgs = await imgs.count()
            
            for i in range(count_imgs):
                try:
                    img = imgs.nth(i)
                    src = await img.get_attribute("src")
                    alt = await img.get_attribute("alt")
                    
                    if src and HTTP_RE.match(src):
                        materiais_encontrados.append(f"Imagem {alt or 'sem título'}: {src}")
                except Exception:
                    continue
        except Exception:
            pass
        
        # === Deduplica e concatena ===
        links_encontrados = _dedupe(links_encontrados)
        materiais_encontrados = _dedupe(materiais_encontrados)
        arquivos_encontrados = _dedupe(arquivos_encontrados)
        
        card_data["links"] = " | ".join(links_encontrados) if links_encontrados else ""
        card_data["materiais"] = " | ".join(materiais_encontrados) if materiais_encontrados else ""
        card_data["arquivos"] = " | ".join(arquivos_encontrados) if arquivos_encontrados else ""
        
        # === Descrição já foi extraída do modal ===
        # Não precisa recalcular, pois a descrição já vem completa do modal
        
        # === Extração de Atividade Ponderada (AGNÓSTICA) ===
        weighted_info = await _extract_atividade_ponderada(modal, logger)
        card_data["is_atividade_ponderada"] = weighted_info["is_ponderada"]
        card_data["pontos_atividade"] = weighted_info["pontos"]
        
        # Para projetos, SEMPRE é ponderada
        if card_type == "projeto" and not card_data["is_atividade_ponderada"]:
            logger.warning(f"   ⚠️ Card de projeto sem atividade ponderada detectada - forçando True")
            card_data["is_atividade_ponderada"] = True
            if card_data["pontos_atividade"] == 0:
                card_data["pontos_atividade"] = 1  # Valor padrão para projetos
        
        # === Flags booleanos derivados ===
        # is_avaliativo é DERIVADO de is_atividade_ponderada
        card_data["is_avaliativo"] = card_data["is_atividade_ponderada"]
        
        # is_encontro é derivado do card_type
        card_data["is_encontro"] = card_type in ["encontro_orientacao", "encontro_instrucao"]
        
        # is_sincrono é derivado da presença de data/hora
        card_data["is_sincrono"] = bool(card_data.get("data_hora"))
        
        # Manter compatibilidade com campo antigo
        card_data["tipo"] = card_type
        
        # === Garante que modal foi fechado ===
        await close_modal_if_open(page, logger)
        
        return card_data
        
    except Exception as e:
        logger.warning(f"   ⚠️ Erro ao extrair card {indice}: {e}")
        
        try:
            await close_modal_if_open(page, logger)
        except Exception:
            pass
        
        return None


def _categorize_url(
    url: str,
    text: str,
    links: list,
    materiais: list,
    arquivos: list
) -> None:
    """Categoriza URL em links/materiais/arquivos."""
    # Extensões de arquivo
    arquivo_exts = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.zip']
    # Domínios de materiais
    material_domains = ['drive.google', 'docs.google', 'sheets.google']
    
    if any(ext in url.lower() for ext in arquivo_exts):
        arquivos.append(f"{text}: {url}")
    elif any(domain in url.lower() for domain in material_domains):
        materiais.append(f"{text}: {url}")
    else:
        links.append(f"{text}: {url}")


def _dedupe(items: list) -> list:
    """Remove duplicatas preservando ordem."""
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


async def _extract_reference_html(modal, card_type: str, icon_id: str, logger: logging.Logger) -> None:
    """Extrai HTML de referência para documentação."""
    try:
        from pathlib import Path
        
        # Criar pasta referencias se não existir
        Path("referencias").mkdir(exist_ok=True)
        
        # Extrair HTML completo do modal
        html_completo = await modal.inner_html()
        
        # Salvar em arquivo
        filename = f"referencias/modal_{card_type}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_completo)
        
        logger.info(f"   📁 HTML de referência salvo: {filename}")
        logger.info(f"   🎯 Tipo: {card_type}, Ícone: {icon_id}")
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao salvar referência: {e}")


async def _extract_data_hora(modal, logger: logging.Logger) -> Optional[str]:
    """Extrai data/hora do modal."""
    try:
        # Seletores específicos para data/hora
        date_elements = modal.locator("*:has-text(/\\d{2}\\/\\d{2}\\/\\d{4}/)")
        count = await date_elements.count()
        
        for i in range(count):
            elem = date_elements.nth(i)
            text = await elem.text_content()
            date_match = re.search(r'\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2}h?', text)
            if date_match:
                logger.debug(f"   📅 Data/hora: {date_match.group()}")
                return date_match.group()
        
        return None
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao extrair data/hora: {e}")
        return None


async def _extract_professor(modal, logger: logging.Logger) -> Optional[str]:
    """Extrai nome do professor do modal."""
    try:
        # Buscar todos os elementos dentro de general-information-activity
        activity_rows = modal.locator("div.general-information-activity-row")
        count = await activity_rows.count()
        
        for i in range(count):
            row = activity_rows.nth(i)
            # Buscar span com nome (geralmente professores têm formato de nome completo)
            spans = await row.locator("span.MuiTypography-root").all()
            for span in spans:
                text = await span.text_content()
                text = text.strip()
                # Verificar se parece um nome (regex de nome completo)
                if text and len(text.split()) >= 2 and not any(char.isdigit() for char in text):
                    # Verificar se não é data/hora ou outros campos
                    if not re.search(r'\d{2}/\d{2}/\d{4}', text) and not re.search(r'\d{2}:\d{2}', text):
                        logger.debug(f"   👨‍🏫 Professor: {text}")
                        return text
        
        return None
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao extrair professor: {e}")
        return None


async def _extract_assuntos_relacionados(modal, titulo: str, logger: logging.Logger) -> list:
    """Extrai assuntos relacionados do modal."""
    try:
        assuntos_selectors = [
            "div.content-related-issues div.content-related-issues-list ul",
            "div.content-related-issues ul li",
            "div.content-related-issues-list ul",
            "div.content-related-issues ul",
            ".content-related-issues-list ul",
            "div:has-text('Assuntos Relacionados') ul",
            "div:has-text('Assuntos relacionados') ul",
            "div:has-text('assuntos relacionados') ul",
            "[class*='related-issues'] ul",
            "[class*='assunto'] ul",
            "[class*='Assunto'] ul",
            "div:has-text('Assuntos') ul",
            "div:has-text('Relacionados') ul",
        ]
        
        assuntos_encontrados = []
        
        for selector in assuntos_selectors:
            try:
                assuntos_list = modal.locator(selector).first
                count = await assuntos_list.count()
                
                if count > 0:
                    items = await assuntos_list.locator("li").all()
                    
                    for item in items:
                        # Tentar pegar <p> primeiro, depois texto direto
                        p_elem = item.locator("p").first
                        if await p_elem.count() > 0:
                            text = await p_elem.text_content()
                        else:
                            text = await item.text_content()
                        
                        if text and text.strip():
                            # Filtrar se for idêntico ao título do card
                            if text.strip() != titulo:
                                assuntos_encontrados.append(text.strip())
                    
                    if assuntos_encontrados:
                        break
            except Exception:
                continue
        
        return assuntos_encontrados
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao extrair assuntos: {e}")
        return []


async def _extract_conteudos_relacionados(modal, logger: logging.Logger) -> list:
    """Extrai conteúdos relacionados do modal."""
    try:
        conteudos_selectors = [
            "div.content-related-content div.content-related-content-list ul",
            "div.content-related-content ul li a",
            "div.content-related-content-list ul",
            "div.content-related-content ul",
            ".content-related-content-list ul",
            "div:has-text('Conteúdos Relacionados') ul",
            "div:has-text('Conteúdos relacionados') ul",
            "div:has-text('conteúdos relacionados') ul",
            "[class*='related-content'] ul",
            "[class*='conteudo'] ul",
            "[class*='Conteudo'] ul",
            "div:has-text('Conteúdos') ul",
            "div:has-text('Relacionados') ul",
        ]
        
        conteudos_encontrados = []
        
        for selector in conteudos_selectors:
            try:
                conteudos_list = modal.locator(selector).first
                count = await conteudos_list.count()
                
                if count > 0:
                    items = await conteudos_list.locator("li").all()
                    
                    for item in items:
                        link = item.locator("a").first
                        if await link.count() > 0:
                            # Tentar pegar <p> primeiro, depois texto direto
                            p_elem = link.locator("p").first
                            if await p_elem.count() > 0:
                                titulo = await p_elem.text_content()
                            else:
                                titulo = await link.text_content()
                            
                            url = await link.get_attribute("href")
                            
                            if titulo and url and HTTP_RE.match(url):
                                conteudos_encontrados.append({
                                    "titulo": titulo.strip(),
                                    "url": url
                                })
                    
                    if conteudos_encontrados:
                        break
            except Exception:
                continue
        
        return conteudos_encontrados
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao extrair conteúdos: {e}")
        return []


async def _extract_atividade_ponderada(modal, logger: logging.Logger) -> dict:
    """
    Extrai informações de atividade ponderada de forma agnóstica.
    
    IMPORTANTE:
    - Busca em div.general-information-activity
    - "Atividade ponderada: X pontos" → is_ponderada=True, pontos=X
    - "Atividade não ponderada" → is_ponderada=False, pontos=0
    - Ausência de indicador → is_ponderada=False, pontos=0
    
    Funciona para QUALQUER tipo de card (encontro, autoestudo, projeto, etc.)
    
    Retorna: {"is_ponderada": bool, "pontos": int}
    """
    try:
        # Buscar APENAS em div.general-information-activity
        activity_section = modal.locator("div.general-information-activity").first
        
        if not await activity_section.count():
            logger.debug("   ℹ️ Seção general-information-activity não encontrada")
            return {"is_ponderada": False, "pontos": 0}
        
        # Buscar todos os elementos com "Atividade"
        activity_texts = await activity_section.locator("p").all_text_contents()
        
        for text in activity_texts:
            text_lower = text.lower()
            
            # CRÍTICO: Verificar "não ponderada" ANTES de "ponderada"
            if "não ponderada" in text_lower or "nao ponderada" in text_lower:
                logger.debug(f"   ℹ️ Atividade NÃO ponderada: {text.strip()}")
                return {"is_ponderada": False, "pontos": 0}
            
            # Verificar "ponderada" com pontos
            if "ponderada" in text_lower:
                pontos_match = re.search(r'(\d+)\s*pontos?', text, re.IGNORECASE)
                if pontos_match:
                    pontos = int(pontos_match.group(1))
                    logger.info(f"   ✅ Atividade ponderada: {pontos} pontos")
                    return {"is_ponderada": True, "pontos": pontos}
                else:
                    # "ponderada" sem número (caso raro, tratar como True com pontos=0)
                    logger.warning(f"   ⚠️ 'Ponderada' sem pontos: {text.strip()}")
                    return {"is_ponderada": True, "pontos": 0}
        
        logger.debug("   ℹ️ Nenhum indicador de atividade ponderada encontrado")
        return {"is_ponderada": False, "pontos": 0}
        
    except Exception as e:
        logger.debug(f"   ⚠️ Erro ao extrair atividade ponderada: {e}")
        return {"is_ponderada": False, "pontos": 0}


def _classify_card_type_fallback(texto: str) -> str:
    """Classifica tipo de card heuristicamente."""
    texto_lower = (texto or "").lower()
    
    # 0. AUTOESTUDO tem prioridade (verificar palavras-chave específicas)
    # Verificar se é autoestudo ANTES de outras classificações
    autoestudo_keywords = [
        "autoestudo", "auto-estudo", "auto estudo",
        "leitura", "material de apoio", "estudo dirigido"
    ]
    if any(kw in texto_lower for kw in autoestudo_keywords):
        return "autoestudo"
    
    # 1. ATIVIDADE PONDERADA (apenas se explicitamente mencionadas)
    if "atividade ponderada" in texto_lower:
        return "atividade_ponderada"
    elif any(palavra in texto_lower for palavra in ['encontro', 'sprint planning', 'retrospectiva', 'workshop', 'reunião']):
        return "encontro"
    elif any(palavra in texto_lower for palavra in ['projeto', 'desenvolvimento', 'implementação', 'entrega']):
        return "projeto"
    elif any(palavra in texto_lower for palavra in ['avaliação', 'avaliacao', 'prova', 'teste']):
        return "avaliacao"
    elif any(palavra in texto_lower for palavra in ['atividade', 'exercício', 'tarefa']):
        return "atividade"
    else:
        return "outro"





