import asyncio
import csv
import time
import logging
import os
import re
import json
import hashlib
from datetime import datetime
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv

# === Normalization/Enrichment helpers ===
DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})h?", re.IGNORECASE)
WEEK_RE = re.compile(r"Semana\s*(\d+)", re.IGNORECASE)
HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)
NAME_CAND_RE = re.compile(r"^[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+(\s+[A-ZÁÂÃÀÉÊÍÓÔÕÚÇ][A-Za-zÁÂÃÀÉÊÍÓÔÕÚÇäâãàéêíóôõúç'`´^~.-]+){1,}$")


def _extract_date_time(text: str, tz_offset: str = "-03:00"):
    if not text:
        return None, None, None
    m = DATE_RE.search(text)
    if not m:
        return None, None, None
    date_str = m.group(1)
    time_str = m.group(2)
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        iso = dt.strftime("%Y-%m-%dT%H:%M:00") + tz_offset
        return iso, date_str, time_str
    except Exception:
        return None, None, None


def _parse_week(semana: str):
    m = WEEK_RE.search(semana or "")
    return int(m.group(1)) if m else None


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def _guess_professor(text: str, known_names):
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln and ln.strip()]
    if known_names:
        for ln in reversed(lines):
            for name in known_names:
                if ln.lower() == name.lower():
                    return name
    for ln in reversed(lines):
        if NAME_CAND_RE.match(ln) and not any(ch.isdigit() for ch in ln):
            return ln
    return None


def _detect_known_names(records):
    counter = {}
    for r in records:
        text = (r.get("texto_completo") or "")
        for ln in text.splitlines():
            ln = ln.strip()
            if NAME_CAND_RE.match(ln) and not any(ch.isdigit() for ch in ln):
                counter[ln] = counter.get(ln, 0) + 1
    return [name for name, _ in sorted(counter.items(), key=lambda kv: kv[1], reverse=True) if counter[name] >= 2]


def _is_autoestudo(title: str, text: str):
    t = (title or "").lower()
    if any(k in t for k in ["autoestudo", "auto estudo"]):
        return True
    return "autoestudo" in (text or "").lower()


def _is_atividade_ponderada(text: str):
    t = (text or "").lower()
    return "atividade ponderada" in t or "nota:" in t or "prova" in t


def _is_instrucao(title: str, text: str, is_auto: bool):
    if is_auto:
        return False
    t = (title or "").lower()
    if any(k in t for k in ["encontro", "introdução", "instr", "workshop", "sprint", "aula", "orientação", "review", "retrospective"]):
        return True
    if DATE_RE.search(((text or "") + "\n" + (title or ""))):
        return True
    return False


def _normalize_urls_pipe(raw: str):
    if not raw:
        return []
    urls = []
    for p in [x.strip() for x in raw.split("|") if x.strip()]:
        if ":" in p:
            p = p.split(":", 1)[1].strip()
        if HTTP_RE.match(p):
            urls.append(p)
    # dedupe preserve order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _title_norm(s: str):
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"autoestudo\s*\d*", "", s)
    s = re.sub(r"instru[cç][aã]o|encontro|workshop|sprint|review|retrospective", "", s)
    s = re.sub(r"[^a-z0-9áâãàéêíóôõúç\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _title_sim(a: str, b: str) -> float:
    na, nb = _title_norm(a), _title_norm(b)
    if not na or not nb:
        return 0.0
    # simple Jaccard over tokens for robustness
    sa, sb = set(na.split()), set(nb.split())
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union


def _compute_hash(*fields):
    return hashlib.sha1("|".join([f or "" for f in fields]).encode("utf-8")).hexdigest()


def enrich_records(dados, logger, previous_map=None):
    previous_map = previous_map or {}
    # Pre-pass known names
    known_names = _detect_known_names(dados)

    # derive
    for rec in dados:
        semana = rec.get("semana") or ""
        rec["semana_num"] = _parse_week(semana)
        rec["sprint"] = _ceil_div(rec["semana_num"], 2) if rec["semana_num"] else None
        iso, dstr, hstr = _extract_date_time("\n".join([rec.get("titulo") or "", rec.get("descricao") or "", rec.get("texto_completo") or ""]))
        rec["data_hora_iso"] = iso
        rec["data_ddmmaaaa"] = dstr
        rec["hora_hhmm"] = hstr
        rec["professor"] = _guess_professor(rec.get("texto_completo") or "", known_names)
        rec["is_autoestudo"] = _is_autoestudo(rec.get("titulo") or "", rec.get("texto_completo") or "")
        rec["is_atividade_ponderada"] = _is_atividade_ponderada("\n".join([rec.get("titulo") or "", rec.get("descricao") or "", rec.get("texto_completo") or ""]))
        rec["is_instrucao"] = _is_instrucao(rec.get("titulo") or "", rec.get("texto_completo") or "", rec["is_autoestudo"])    
        # urls normalized
        rec["links_urls"] = " | ".join(_normalize_urls_pipe(rec.get("links") or ""))
        rec["materiais_urls"] = " | ".join(_normalize_urls_pipe(rec.get("materiais") or ""))
        rec["arquivos_urls"] = " | ".join(_normalize_urls_pipe(rec.get("arquivos") or ""))
        rec["num_links"] = len(rec["links_urls"].split("|") if rec["links_urls"] else [])
        rec["num_materiais"] = len(rec["materiais_urls"].split("|") if rec["materiais_urls"] else [])
        rec["num_arquivos"] = len(rec["arquivos_urls"].split("|") if rec["arquivos_urls"] else [])
        rec["record_hash"] = _compute_hash(rec.get("titulo"), rec.get("data_ddmmaaaa"), rec.get("professor"))

    # robust anchoring per week
    weeks = {}
    for r in dados:
        weeks.setdefault(r.get("semana_num") or -1, []).append(r)
    for week, recs in weeks.items():
        recs.sort(key=lambda r: (int(r.get("indice") or 0), r.get("titulo") or ""))
        instructions = [r for r in recs if r.get("is_instrucao")]
        for r in recs:
            if not (r.get("is_autoestudo") or r.get("is_atividade_ponderada")):
                continue
            if r.get("id") in previous_map:
                pid, ptitle = previous_map[r["id"]]
                r["parent_instruction_id"] = pid
                r["parent_instruction_title"] = ptitle
                r["anchor_method"] = "preserved_previous"
                r["anchor_confidence"] = "locked"
                continue
            best_score = -1e9
            best = None
            best_method = ""
            best_conf = "low"
            for instr in instructions:
                score = 0.0
                bits = []
                conf = "low"
                if r.get("professor") and instr.get("professor") and r["professor"].lower() == instr["professor"].lower():
                    score += 3.0
                    bits.append("professor")
                    conf = "high"
                if r.get("data_ddmmaaaa") and instr.get("data_ddmmaaaa") and r["data_ddmmaaaa"] == instr["data_ddmmaaaa"]:
                    score += 3.0
                    bits.append("same_date")
                    conf = "high"
                sim = _title_sim(r.get("titulo") or "", instr.get("titulo") or "")
                score += 2.0 * sim
                bits.append(f"sim={sim:.2f}")
                if sim >= 0.5 and conf != "high":
                    conf = "medium"
                delta = int(r.get("indice") or 0) - int(instr.get("indice") or 0)
                if delta >= 0:
                    prox = max(0.0, 1.5 - 0.1 * delta)
                    score += prox
                    bits.append(f"prev_prox={prox:.2f}")
                    if conf == "low":
                        conf = "medium"
                else:
                    score -= 0.2
                    bits.append("after=-0.2")
                if score > best_score:
                    best_score = score
                    best = instr
                    best_method = ",".join(bits)
                    best_conf = conf
            if best:
                r["parent_instruction_id"] = best.get("id")
                r["parent_instruction_title"] = best.get("titulo")
                r["anchor_method"] = best_method
                r["anchor_confidence"] = best_conf

    return dados


def write_enriched_outputs(dados, pasta_turma, timestamp, logger):
    suffix = f"{timestamp}.csv"
    enriched_csv = os.path.join(pasta_turma, f"cards_enriquecidos_{suffix}")
    enriched_jsonl = os.path.join(pasta_turma, f"cards_enriquecidos_{timestamp}.jsonl")

    fields = [
        "semana","semana_num","sprint","indice","id","titulo","descricao","tipo",
        "data_ddmmaaaa","hora_hhmm","data_hora_iso","professor",
        "is_instrucao","is_autoestudo","is_atividade_ponderada",
        "parent_instruction_id","parent_instruction_title","anchor_method","anchor_confidence",
        "links_urls","materiais_urls","arquivos_urls","num_links","num_materiais","num_arquivos",
        "record_hash","texto_completo","links","materiais","arquivos"
    ]
    with open(enriched_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in dados:
            row = {k: r.get(k) for k in fields}
            writer.writerow(row)
    with open(enriched_jsonl, 'w', encoding='utf-8') as f:
        for r in dados:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info(f"💾 Enriched CSV: {enriched_csv}")
    logger.info(f"💾 Enriched JSONL: {enriched_jsonl}")
    return enriched_csv, enriched_jsonl


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

async def close_modal_if_open(page, logger):
    """Try multiple strategies to close an open modal and wait until it's gone."""
    try:
        modal = page.locator("[role='dialog']").first
        modal_exists = False
        try:
            modal_exists = await modal.count() > 0
        except Exception:
            modal_exists = False
        if modal_exists or await page.locator(".MuiBackdrop-root").count() > 0:
            # Prefer explicit close buttons (MUI often uses aria-label="close")
            selectors = [
                "[role='dialog'] button[aria-label='close' i]",
                "[role='dialog'] button[aria-label*='close' i]",
                "[role='dialog'] button[aria-label='fechar' i]",
                "[role='dialog'] button[aria-label*='fechar' i]",
                "[role='dialog'] button.MuiIconButton-root",
                "button:has-text('Fechar')",
                "button:has-text('Close')",
            ]
            closed = False
            for sel in selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible(timeout=300):
                        await btn.click()
                        closed = True
                        break
                except Exception:
                    continue
            # Fallback: try clicking backdrop
            if not closed:
                try:
                    backdrop = page.locator(".MuiBackdrop-root").first
                    if await backdrop.count() > 0:
                        await backdrop.click(position={"x": 5, "y": 5})
                        await page.wait_for_timeout(200)
                        closed = True
                except Exception:
                    pass
            # Fallback: click outside dialog using its bounding box
            if not closed:
                try:
                    box = await modal.bounding_box()
                    if box:
                        x = max(2, int(box["x"]) - 10)
                        y = max(2, int(box["y"]) - 10)
                        await page.mouse.click(x, y)
                        await page.wait_for_timeout(250)
                        closed = True
                except Exception:
                    pass
            # Fallback: unconditional body click near (2,2)
            try:
                await page.click("body", position={"x": 2, "y": 2})
                await page.wait_for_timeout(250)
            except Exception:
                pass
            # Fallback: press Escape a few times
            for _ in range(3):
                try:
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(200)
                except Exception:
                    pass
            # Final fallback
            try:
                await page.mouse.click(5, 5)
            except Exception:
                pass
            # Wait until the modal is hidden or detached (best-effort)
            try:
                await modal.wait_for(state="hidden", timeout=2000)
            except Exception:
                try:
                    await modal.wait_for(state="detached", timeout=1000)
                except Exception:
                    logger.debug("Modal may still be open; proceeding")
    except Exception:
        pass

async def extrair_dados_card_completo(card, indice, semana, page, logger):
    """Extrai dados completos do card incluindo links e materiais (abre modal)"""
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
        
        # Texto completo do card (lista)
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
        
        links_encontrados = []
        materiais_encontrados = []
        arquivos_encontrados = []
        
        # Links visíveis no card
        try:
            links_elementos = card.locator("a")
            count_links = await links_elementos.count()
            for i in range(count_links):
                try:
                    link_elem = links_elementos.nth(i)
                    href = await link_elem.get_attribute("href")
                    texto_link = await link_elem.text_content()
                    if href:
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
        
        # Abre modal do card para capturar materiais reais
        try:
            await card.click()
            await page.wait_for_timeout(600)
            # Tenta localizar um dialog
            modal = page.locator("[role='dialog']").first
            if await modal.is_visible(timeout=4000):
                try:
                    modal_text = await modal.text_content()
                    if modal_text:
                        # anexa ao texto completo para melhor detecção downstream
                        card_data["texto_completo"] = (card_data["texto_completo"] + "\n\n" + modal_text.strip()).strip()
                except:
                    pass
                # coleta âncoras do modal
                try:
                    modal_links = modal.locator("a")
                    mcount = await modal_links.count()
                    for j in range(mcount):
                        try:
                            a = modal_links.nth(j)
                            href = await a.get_attribute("href")
                            texta = (await a.text_content()) or ""
                            if not href:
                                continue
                            if not HTTP_RE.match(href):
                                continue
                            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.zip']):
                                arquivos_encontrados.append(f"{texta.strip() or 'Arquivo'}: {href}")
                            elif any(material in href.lower() for material in ['drive.google', 'docs.google', 'sheets.google']):
                                materiais_encontrados.append(f"{texta.strip() or 'Material'}: {href}")
                            else:
                                links_encontrados.append(f"{texta.strip() or 'Link'}: {href}")
                        except:
                            continue
                except:
                    pass
                # Fecha modal
                try:
                    fechar = page.locator("button:has-text('Fechar')").first
                    if await fechar.is_visible(timeout=1000):
                        await fechar.click()
                        await page.wait_for_timeout(300)
                except:
                    # tenta ESC
                    try:
                        await page.keyboard.press('Escape')
                    except:
                        pass
        except Exception as e:
            logger.debug(f"   Modal não pôde ser aberto para o card {indice+1}: {e}")
        
        # Procura imagens e outros recursos no card (fallback)
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
                except:
                    continue
        except:
            pass
        
        # Converte listas para strings sem duplicatas
        def _dedupe(lst):
            seen = set()
            out = []
            for x in lst:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out
        links_encontrados = _dedupe(links_encontrados)
        materiais_encontrados = _dedupe(materiais_encontrados)
        arquivos_encontrados = _dedupe(arquivos_encontrados)

        card_data["links"] = " | ".join(links_encontrados) if links_encontrados else ""
        card_data["materiais"] = " | ".join(materiais_encontrados) if materiais_encontrados else ""
        card_data["arquivos"] = " | ".join(arquivos_encontrados) if arquivos_encontrados else ""
        
        # Tipo heurístico
        texto_lower = (card_data["texto_completo"] or "").lower()
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
        
        # Ensure modal is closed before returning
        await close_modal_if_open(page, logger)
        
        return card_data
        
    except Exception as e:
        logger.warning(f"   ⚠️ Erro ao extrair card {indice}: {e}")
        # Try to close modal if something went wrong
        try:
            await close_modal_if_open(page, logger)
        except Exception:
            pass
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
                        card_info = await extrair_dados_card_completo(card, i, nome_semana, page, logger)
                        
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
    """Salva dados na pasta da turma e gera arquivos enriquecidos"""
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
        
        # Enrichment pass and outputs
        logger.info("🔧 Enriquecendo registros (ancoragem robusta, normalizações)...")
        dados_enriquecidos = enrich_records([dict(r) for r in dados], logger)
        enriched_csv, enriched_jsonl = write_enriched_outputs(dados_enriquecidos, pasta_turma, timestamp, logger)
        
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
    print("   ✅ Enriquecimento e ancoragem de autoestudos")
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
            
            # 7. Salva resultados organizados e enriquecidos
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
