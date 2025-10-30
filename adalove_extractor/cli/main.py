"""
Ponto de entrada principal para execução do extrator.

Este módulo implementa a lógica de extração completa usando a arquitetura modular
com sistema resiliente de checkpoints e recuperação automática.
"""

import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright

from ..config import get_settings, configure_logging
from ..browser import login_adalove, navigate_to_academic_life, discover_weeks
from ..extractors import extract_week_cards
from ..enrichment import EnrichmentEngine
from ..io import (
    write_cards_csv, write_enriched_outputs, compute_stats_by_week,
    CheckpointManager, IncrementalWriter, RecoveryManager
)


async def run_extraction(nome_turma: str) -> None:
    """
    Executa o fluxo completo de extração para uma turma com sistema resiliente.
    
    Fluxo:
    1. Detecção de execução interrompida
    2. Login na plataforma
    3. Navegação para academic-life
    4. Seleção manual da turma
    5. Descoberta de semanas
    6. Extração de cards por semana com checkpoints
    7. Enriquecimento de dados
    8. Exportação para CSV/JSONL
    
    Args:
        nome_turma: Nome da turma para organização dos arquivos
    """
    settings = get_settings()
    logger = configure_logging(nome_turma, settings.logs_dir, "DEBUG")
    
    print("\n" + "="*60)
    print("🚀 ADALOVE CARDS EXTRACTOR - VERSÃO 3.1.0 (RESILIENTE)")
    print("="*60)
    print("📋 Extração completa incluindo:")
    print("   ✅ Títulos e descrições dos cards")
    print("   ✅ Links e materiais anexados")
    print("   ✅ Arquivos e documentos")
    print("   ✅ Organização por pasta da turma")
    print("   ✅ Enriquecimento e ancoragem de autoestudos")
    print("   ✅ Sistema de checkpoints e recuperação automática")
    print("="*60)
    
    logger.info(f"🚀 Iniciando extração resiliente para turma: {nome_turma}")
    
    # 1. DETECÇÃO DE EXECUÇÃO INTERROMPIDA
    recovery_mgr = RecoveryManager(nome_turma, settings.output_dir)
    
    if recovery_mgr.detect_interrupted():
        logger.info("⚠️ Execução anterior detectada")
        
        # Mostra informações da execução anterior
        checkpoint = recovery_mgr.load_checkpoint()
        print(f"\n⚠️  EXECUÇÃO ANTERIOR DETECTADA!")
        print(f"📊 Progresso: {len(checkpoint['semanas_processadas'])}/{len(checkpoint['semanas_descobertas'])} semanas")
        print(f"📝 Cards extraídos: {checkpoint['cards_extraidos']}")
        print(f"⏰ Última atualização: {checkpoint['ultima_atualizacao']}")
        
        opcao = recovery_mgr.prompt_recovery()
        
        if opcao == 'continue':
            # RETOMAR EXECUÇÃO
            logger.info("🔄 Retomando execução anterior")
            return await resume_extraction(nome_turma, recovery_mgr, settings, logger)
        elif opcao == 'restart':
            # LIMPAR E RECOMEÇAR
            logger.info("🧹 Limpando execução anterior e recomeçando")
            recovery_mgr.cleanup_all()
            print("🧹 Limpeza concluída. Iniciando nova extração...")
        else:  # abort
            logger.info("❌ Usuário abortou execução")
            print("❌ Execução abortada pelo usuário")
            return
    
    # 2. NOVA EXECUÇÃO COM CHECKPOINTS
    execution_id = f"{nome_turma}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_mgr = CheckpointManager(nome_turma, settings.output_dir, execution_id)
    incremental_writer = IncrementalWriter(nome_turma, settings.output_dir, execution_id)
    
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel=settings.browser_channel, 
            headless=settings.headless
        )
        page = await browser.new_page()
        
        try:
            # Login
            await page.goto("https://adalove.inteli.edu.br/")
            if not await login_adalove(page, settings.login, settings.senha, logger):
                logger.error("❌ Falha no login")
                return
            
            # Academic-life
            await navigate_to_academic_life(page, logger)
            
            # Seleção manual da turma
            if settings.interactive:
                print(f"\n📁 Dados serão salvos em: {settings.output_dir}/{nome_turma}/")
                print("👆 Agora selecione a turma na interface:")
                try:
                    input("⏸️ Pressione Enter após selecionar a turma na página: ")
                    logger.info("✅ Turma selecionada")
                    await page.wait_for_timeout(3000)
                except (EOFError, KeyboardInterrupt):
                    print("\n❌ Entrada cancelada pelo usuário")
                    return
                
                # Fecha popup novamente
                try:
                    fechar_btn = page.locator("button:has-text('Fechar')").first
                    if await fechar_btn.is_visible(timeout=2000):
                        await fechar_btn.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass
            
            # Descobre semanas
            semanas = await discover_weeks(page, logger)
            
            # Inicializa checkpoint
            checkpoint_mgr.initialize(semanas)
            logger.info(f"📚 Processando {len(semanas)} semanas com checkpoints...")
            
            # LOOP POR SEMANAS COM SALVAMENTO INCREMENTAL
            for i, semana in enumerate(semanas, 1):
                logger.info(f"🔄 {semana} ({i}/{len(semanas)})")
                
                # Volta para academic-life antes de cada semana
                await page.goto("https://adalove.inteli.edu.br/academic-life")
                await page.wait_for_timeout(2000)
                
                # Fecha popup
                try:
                    fechar_btn = page.locator("button:has-text('Fechar')").first
                    if await fechar_btn.is_visible(timeout=2000):
                        await fechar_btn.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass
                
                # Extrai cards da semana
                cards_semana = await extract_week_cards(page, semana, logger)
                
                # SALVAMENTO INCREMENTAL (após cada semana)
                incremental_writer.write_batch(cards_semana)
                incremental_writer.flush()
                
                # Cria backup da semana
                incremental_writer.create_week_backup(semana, cards_semana)
                
                # ATUALIZA CHECKPOINT
                checkpoint_mgr.mark_week_completed(semana, len(cards_semana))
                checkpoint_mgr.save()
                
                logger.info(f"✅ Checkpoint: {semana} salva ({len(cards_semana)} cards)")
            
            # FINALIZAÇÃO
            checkpoint_mgr.mark_as_completed()
            all_cards = incremental_writer.finalize()  # Consolida JSONL temp
            
            # Salva arquivos finais + enriquecimento
            await save_and_enrich(all_cards, nome_turma, settings.output_dir, logger)
            
            # Limpeza de arquivos temporários
            checkpoint_mgr.cleanup()
            incremental_writer.cleanup()
            
            # Resumo final
            duration = time.time() - start_time
            print_final_summary(all_cards, nome_turma, settings.output_dir, duration, logger)
            
        except Exception as e:
            # MARCA CHECKPOINT COMO FAILED (se foi inicializado)
            try:
                checkpoint_mgr.mark_as_failed(str(e))
                checkpoint_mgr.save()
            except RuntimeError:
                # Checkpoint não foi inicializado ainda
                pass
            logger.error(f"❌ Erro geral: {e}")
            raise
        finally:
            await browser.close()


async def resume_extraction(
    nome_turma: str, 
    recovery_mgr: RecoveryManager, 
    settings, 
    logger
) -> None:
    """
    Retoma extração interrompida do último checkpoint.
    
    Args:
        nome_turma: Nome da turma
        recovery_mgr: Instância do RecoveryManager
        settings: Configurações do sistema
        logger: Logger
    """
    checkpoint = recovery_mgr.load_checkpoint()
    execution_id = checkpoint['execution_id']
    
    # Carrega dados já extraídos
    cards_existentes = recovery_mgr.load_temp_data()
    logger.info(f"📦 Carregados {len(cards_existentes)} cards do checkpoint")
    
    # Retoma writer e checkpoint manager
    checkpoint_mgr, incremental_writer = recovery_mgr.resume_from(execution_id)
    
    semanas_pendentes = [
        s for s in checkpoint['semanas_descobertas'] 
        if s not in checkpoint['semanas_processadas']
    ]
    
    logger.info(f"🔄 Retomando extração. Faltam {len(semanas_pendentes)} semanas")
    
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel=settings.browser_channel, 
            headless=settings.headless
        )
        page = await browser.new_page()
        
        try:
            # Login
            await page.goto("https://adalove.inteli.edu.br/")
            if not await login_adalove(page, settings.login, settings.senha, logger):
                logger.error("❌ Falha no login")
                return
            
            # Academic-life
            await navigate_to_academic_life(page, logger)
            
            # Continua extração das semanas restantes
            for i, semana in enumerate(semanas_pendentes, 1):
                logger.info(f"🔄 {semana} ({i}/{len(semanas_pendentes)}) - RETOMADA")
                
                # Volta para academic-life antes de cada semana
                await page.goto("https://adalove.inteli.edu.br/academic-life")
                await page.wait_for_timeout(2000)
                
                # Fecha popup
                try:
                    fechar_btn = page.locator("button:has-text('Fechar')").first
                    if await fechar_btn.is_visible(timeout=2000):
                        await fechar_btn.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass
                
                # Extrai cards da semana
                cards_semana = await extract_week_cards(page, semana, logger)
                
                # SALVAMENTO INCREMENTAL
                incremental_writer.write_batch(cards_semana)
                incremental_writer.flush()
                
                # Cria backup da semana
                incremental_writer.create_week_backup(semana, cards_semana)
                
                # ATUALIZA CHECKPOINT
                checkpoint_mgr.mark_week_completed(semana, len(cards_semana))
                checkpoint_mgr.save()
                
                logger.info(f"✅ Checkpoint: {semana} salva ({len(cards_semana)} cards)")
            
            # FINALIZAÇÃO
            checkpoint_mgr.mark_as_completed()
            all_cards = incremental_writer.finalize()  # Consolida JSONL temp
            
            # Salva arquivos finais + enriquecimento
            await save_and_enrich(all_cards, nome_turma, settings.output_dir, logger)
            
            # Limpeza de arquivos temporários
            checkpoint_mgr.cleanup()
            incremental_writer.cleanup()
            recovery_mgr.cleanup_after_recovery()
            
            # Resumo final
            duration = time.time() - start_time
            print_final_summary(all_cards, nome_turma, settings.output_dir, duration, logger)
                
        except Exception as e:
            # MARCA CHECKPOINT COMO FAILED (se foi inicializado)
            try:
                checkpoint_mgr.mark_as_failed(str(e))
                checkpoint_mgr.save()
            except RuntimeError:
                # Checkpoint não foi inicializado ainda
                pass
            logger.error(f"❌ Erro geral: {e}")
            raise
        finally:
            await browser.close()
    

def print_final_summary(
    cards_data: list[dict], 
    nome_turma: str, 
    output_dir: str, 
    duration: float, 
    logger
) -> None:
    """
    Exibe resumo final da extração.
    
    Args:
        cards_data: Lista de cards extraídos
        nome_turma: Nome da turma
        output_dir: Diretório de saída
        duration: Tempo total de execução
        logger: Logger
    """
    # Estatísticas por semana
    stats = compute_stats_by_week(cards_data)
    logger.info("📊 Estatísticas por semana:")
    for semana, dados in stats.items():
        logger.info(
            f"   {semana}: {dados['cards']} cards, "
            f"{dados['links']} links, {dados['materiais']} materiais"
        )
    
    # Resumo final
    semanas_processadas = len(set(card["semana"] for card in cards_data))
    total_links = sum(1 for card in cards_data if card.get("links"))
    total_materiais = sum(1 for card in cards_data if card.get("materiais"))
    
    print("\n" + "="*60)
    print("🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"📊 {len(cards_data)} cards extraídos")
    print(f"📚 {semanas_processadas} semanas processadas")
    print(f"🔗 {total_links} cards com links")
    print(f"📎 {total_materiais} cards com materiais")
    print(f"⏱️ Tempo total: {duration:.1f}s")
    print(f"📁 Pasta: {output_dir}/{nome_turma}")
    print("="*60)
    
    logger.info("🎉 Extração finalizada com sucesso!")


async def save_and_enrich(
    cards_data: list[dict],
    nome_turma: str,
    output_base_dir: str,
    logger
) -> None:
    """
    Salva dados brutos e enriquecidos.
    
    Args:
        cards_data: Lista de cards extraídos
        nome_turma: Nome da turma
        output_base_dir: Diretório base de saída
        logger: Logger
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_turma = f"{output_base_dir}/{nome_turma}"
    
    # Salva CSV bruto
    csv_bruto = f"{pasta_turma}/cards_completos_{timestamp}.csv"
    write_cards_csv(cards_data, csv_bruto, logger)
    
    # Estatísticas por semana
    stats = compute_stats_by_week(cards_data)
    logger.info("📊 Estatísticas por semana:")
    for semana, dados in stats.items():
        logger.info(
            f"   {semana}: {dados['cards']} cards, "
            f"{dados['links']} links, {dados['materiais']} materiais"
        )
    
    # Enriquecimento
    logger.info("🔧 Enriquecendo registros (ancoragem robusta, normalizações)...")
    enrichment_engine = EnrichmentEngine(logger)
    enriched_data = enrichment_engine.enrich_cards(cards_data)
    
    # Salva CSV e JSONL enriquecidos
    csv_enriquecido, jsonl_enriquecido = write_enriched_outputs(
        enriched_data, pasta_turma, timestamp, logger
    )
    
    # Resumo final
    semanas_processadas = len(set(card["semana"] for card in cards_data))
    total_links = sum(1 for card in cards_data if card.get("links"))
    total_materiais = sum(1 for card in cards_data if card.get("materiais"))
    
    print("\n" + "="*60)
    print("🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"📊 {len(cards_data)} cards extraídos")
    print(f"📚 {semanas_processadas} semanas processadas")
    print(f"🔗 {total_links} cards com links")
    print(f"📎 {total_materiais} cards com materiais")
    print(f"📁 Pasta: {pasta_turma}")
    print(f"💾 Arquivos gerados:")
    print(f"   - cards_completos_{timestamp}.csv")
    print(f"   - cards_enriquecidos_{timestamp}.csv")
    print(f"   - cards_enriquecidos_{timestamp}.jsonl")
    print("="*60)
    
    logger.info("🎉 Extração finalizada com sucesso!")


