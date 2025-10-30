"""
Testes de integração para sistema resiliente completo.

Testa fluxo completo de extração com checkpoints, interrupção e recuperação.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from adalove_extractor.io.checkpoint import CheckpointManager
from adalove_extractor.io.incremental_writer import IncrementalWriter
from adalove_extractor.io.recovery import RecoveryManager


class TestIntegrationCheckpointFlow:
    """Testes de integração para fluxo completo com checkpoints."""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
            
    @pytest.fixture
    def mock_settings(self, temp_dir):
        """Cria configurações mock para testes."""
        settings = MagicMock()
        settings.output_dir = temp_dir
        settings.logs_dir = temp_dir
        settings.log_level = "INFO"
        settings.browser_channel = "chrome"
        settings.headless = True
        settings.interactive = False
        settings.login = "test@example.com"
        settings.senha = "password123"
        return settings
        
    @pytest.fixture
    def mock_logger(self):
        """Cria logger mock para testes."""
        logger = MagicMock()
        return logger
        
    def test_full_extraction_with_checkpoints(self, temp_dir, mock_settings, mock_logger):
        """Testa fluxo completo de extração com checkpoints."""
        nome_turma = "teste_turma"
        execution_id = f"{nome_turma}_20251017_120000"
        
        # Cria instâncias
        checkpoint_mgr = CheckpointManager(nome_turma, temp_dir, execution_id)
        incremental_writer = IncrementalWriter(nome_turma, temp_dir, execution_id)
        
        # Simula descoberta de semanas
        semanas = ["Semana 01", "Semana 02", "Semana 03"]
        checkpoint_mgr.initialize(semanas)
        
        # Simula processamento de semanas
        for i, semana in enumerate(semanas):
            cards_semana = [
                {"semana": semana, "titulo": f"Card {i+1}", "descricao": f"Descrição {i+1}"},
                {"semana": semana, "titulo": f"Card {i+2}", "descricao": f"Descrição {i+2}"}
            ]
            
            # Salvamento incremental
            incremental_writer.write_batch(cards_semana)
            incremental_writer.flush()
            
            # Backup da semana
            incremental_writer.create_week_backup(semana, cards_semana)
            
            # Atualiza checkpoint
            checkpoint_mgr.mark_week_completed(semana, len(cards_semana))
            checkpoint_mgr.save()
            
        # Finaliza
        checkpoint_mgr.mark_as_completed()
        all_cards = incremental_writer.finalize()
        
        # Verificações
        assert len(all_cards) == 6  # 2 cards por semana × 3 semanas
        
        # Verifica checkpoint final
        checkpoint_data = checkpoint_mgr.load()
        assert checkpoint_data["status"] == "completed"
        assert len(checkpoint_data["semanas_processadas"]) == 3
        assert checkpoint_data["cards_extraidos"] == 6
        
        # Verifica arquivos de backup
        backup_files = list(Path(temp_dir).glob("teste_turma/checkpoint_semana_*.json"))
        assert len(backup_files) == 3
        
        # Limpeza
        checkpoint_mgr.cleanup()
        incremental_writer.cleanup()
        
    def test_resume_after_interruption(self, temp_dir, mock_settings, mock_logger):
        """Testa retomada após interrupção simulada."""
        nome_turma = "teste_turma"
        execution_id = f"{nome_turma}_20251017_120000"
        
        # Simula execução interrompida após 2 semanas
        checkpoint_mgr = CheckpointManager(nome_turma, temp_dir, execution_id)
        incremental_writer = IncrementalWriter(nome_turma, temp_dir, execution_id)
        
        semanas = ["Semana 01", "Semana 02", "Semana 03"]
        checkpoint_mgr.initialize(semanas)
        
        # Processa apenas 2 semanas (simula interrupção)
        for i in range(2):
            semana = semanas[i]
            cards_semana = [
                {"semana": semana, "titulo": f"Card {i+1}", "descricao": f"Descrição {i+1}"}
            ]
            
            incremental_writer.write_batch(cards_semana)
            incremental_writer.flush()
            incremental_writer.create_week_backup(semana, cards_semana)
            checkpoint_mgr.mark_week_completed(semana, len(cards_semana))
            checkpoint_mgr.save()
        
        # Simula retomada
        recovery_mgr = RecoveryManager(nome_turma, temp_dir)
        
        # Verifica detecção de interrupção
        assert recovery_mgr.detect_interrupted()
        
        # Carrega dados existentes
        cards_existentes = recovery_mgr.load_temp_data()
        assert len(cards_existentes) == 2
        
        # Retoma execução
        checkpoint_mgr_resume, incremental_writer_resume = recovery_mgr.resume_from(execution_id)
        
        # Verifica estado carregado
        assert checkpoint_mgr_resume._checkpoint_data is not None
        assert incremental_writer_resume._total_cards_written == 2
        
        # Processa semana restante
        semana_restante = "Semana 03"
        cards_semana = [
            {"semana": semana_restante, "titulo": "Card 3", "descricao": "Descrição 3"}
        ]
        
        incremental_writer_resume.write_batch(cards_semana)
        incremental_writer_resume.flush()
        incremental_writer_resume.create_week_backup(semana_restante, cards_semana)
        checkpoint_mgr_resume.mark_week_completed(semana_restante, len(cards_semana))
        checkpoint_mgr_resume.save()
        
        # Finaliza
        checkpoint_mgr_resume.mark_as_completed()
        all_cards = incremental_writer_resume.finalize()
        
        # Verificações finais
        assert len(all_cards) == 3
        
        checkpoint_data = checkpoint_mgr_resume.load()
        assert checkpoint_data["status"] == "completed"
        assert len(checkpoint_data["semanas_processadas"]) == 3
        
        # Limpeza
        checkpoint_mgr_resume.cleanup()
        incremental_writer_resume.cleanup()
        recovery_mgr.cleanup_after_recovery()
        
    def test_recovery_with_partial_data(self, temp_dir, mock_settings, mock_logger):
        """Testa recuperação com dados parciais."""
        nome_turma = "teste_turma"
        execution_id = f"{nome_turma}_20251017_120000"
        
        # Cria dados parciais
        checkpoint_mgr = CheckpointManager(nome_turma, temp_dir, execution_id)
        incremental_writer = IncrementalWriter(nome_turma, temp_dir, execution_id)
        
        semanas = ["Semana 01", "Semana 02"]
        checkpoint_mgr.initialize(semanas)
        
        # Processa apenas primeira semana
        cards_semana = [
            {"semana": "Semana 01", "titulo": "Card 1", "descricao": "Descrição 1"}
        ]
        
        incremental_writer.write_batch(cards_semana)
        incremental_writer.flush()
        incremental_writer.create_week_backup("Semana 01", cards_semana)
        checkpoint_mgr.mark_week_completed("Semana 01", len(cards_semana))
        checkpoint_mgr.save()
        
        # Simula falha (não marca como completed)
        
        # Testa recuperação
        recovery_mgr = RecoveryManager(nome_turma, temp_dir)
        
        # Verifica detecção
        assert recovery_mgr.detect_interrupted()
        
        # Valida dados
        is_valid, errors = recovery_mgr.validate_recovery_data()
        assert is_valid
        assert len(errors) == 0
        
        # Carrega dados
        cards_existentes = recovery_mgr.load_temp_data()
        assert len(cards_existentes) == 1
        
        # Consolida dados
        merged_cards = recovery_mgr.merge_temp_data()
        assert len(merged_cards) == 1
        
        # Limpeza
        recovery_mgr.cleanup_all()
        
    def test_error_handling_during_extraction(self, temp_dir, mock_settings, mock_logger):
        """Testa tratamento de erros durante extração."""
        nome_turma = "teste_turma"
        execution_id = f"{nome_turma}_20251017_120000"
        
        checkpoint_mgr = CheckpointManager(nome_turma, temp_dir, execution_id)
        incremental_writer = IncrementalWriter(nome_turma, temp_dir, execution_id)
        
        semanas = ["Semana 01", "Semana 02"]
        checkpoint_mgr.initialize(semanas)
        
        # Processa primeira semana com sucesso
        cards_semana = [
            {"semana": "Semana 01", "titulo": "Card 1", "descricao": "Descrição 1"}
        ]
        
        incremental_writer.write_batch(cards_semana)
        incremental_writer.flush()
        checkpoint_mgr.mark_week_completed("Semana 01", len(cards_semana))
        checkpoint_mgr.save()
        
        # Simula erro
        try:
            raise RuntimeError("Erro simulado durante extração")
        except Exception as e:
            # Marca checkpoint como failed
            checkpoint_mgr.mark_as_failed(str(e))
            checkpoint_mgr.save()
        
        # Verifica estado de erro
        checkpoint_data = checkpoint_mgr.load()
        assert checkpoint_data["status"] == "failed"
        assert "Erro simulado" in checkpoint_data["error_message"]
        
        # Verifica que não é recuperável
        assert not checkpoint_mgr.is_recoverable()
        
    def test_multiple_execution_ids(self, temp_dir, mock_settings, mock_logger):
        """Testa múltiplas execuções com IDs diferentes."""
        nome_turma = "teste_turma"
        
        # Primeira execução
        execution_id_1 = f"{nome_turma}_20251017_120000"
        checkpoint_mgr_1 = CheckpointManager(nome_turma, temp_dir, execution_id_1)
        incremental_writer_1 = IncrementalWriter(nome_turma, temp_dir, execution_id_1)
        
        checkpoint_mgr_1.initialize(["Semana 01"])
        incremental_writer_1.write_batch([{"semana": "Semana 01", "titulo": "Card 1"}])
        incremental_writer_1.flush()
        checkpoint_mgr_1.mark_week_completed("Semana 01", 1)
        checkpoint_mgr_1.save()
        
        # Segunda execução (diferente ID)
        execution_id_2 = f"{nome_turma}_20251017_130000"
        checkpoint_mgr_2 = CheckpointManager(nome_turma, temp_dir, execution_id_2)
        incremental_writer_2 = IncrementalWriter(nome_turma, temp_dir, execution_id_2)
        
        checkpoint_mgr_2.initialize(["Semana 01", "Semana 02"])
        incremental_writer_2.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 02", "titulo": "Card 2"}
        ])
        incremental_writer_2.flush()
        checkpoint_mgr_2.mark_week_completed("Semana 01", 1)
        checkpoint_mgr_2.mark_week_completed("Semana 02", 1)
        checkpoint_mgr_2.save()
        
        # Verifica que RecoveryManager detecta a execução mais recente
        recovery_mgr = RecoveryManager(nome_turma, temp_dir)
        assert recovery_mgr.detect_interrupted()
        
        checkpoint = recovery_mgr.load_checkpoint()
        assert checkpoint["execution_id"] == execution_id_2
        
        # Limpeza
        recovery_mgr.cleanup_all()






