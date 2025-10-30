"""
Testes unitários para CheckpointManager.

Testa funcionalidades de persistência, validação e recuperação de checkpoints.
"""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from adalove_extractor.io.checkpoint import CheckpointManager


class TestCheckpointManager:
    """Testes para CheckpointManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
            
    @pytest.fixture
    def checkpoint_manager(self, temp_dir):
        """Cria instância de CheckpointManager para testes."""
        return CheckpointManager("teste_turma", temp_dir, "teste_20251017_120000")
        
    def test_create_new_checkpoint(self, checkpoint_manager):
        """Testa criação de checkpoint inicial."""
        semanas = ["Semana 01", "Semana 02", "Semana 03"]
        
        checkpoint_manager.initialize(semanas)
        
        # Verifica se arquivo foi criado
        assert checkpoint_manager.checkpoint_path.exists()
        
        # Verifica dados salvos
        data = checkpoint_manager.load()
        assert data["turma"] == "teste_turma"
        assert data["execution_id"] == "teste_20251017_120000"
        assert data["status"] == "extracting"
        assert data["semanas_descobertas"] == semanas
        assert data["semanas_processadas"] == []
        assert data["cards_extraidos"] == 0
        # Verifica estrutura básica dos dados
        assert "created_at" in data
        
    def test_save_and_load_checkpoint(self, checkpoint_manager):
        """Testa persistência e carga de checkpoint."""
        semanas = ["Semana 01", "Semana 02"]
        checkpoint_manager.initialize(semanas)
        
        # Modifica dados
        checkpoint_manager.mark_week_completed("Semana 01", 5)
        checkpoint_manager.save()
        
        # Carrega e verifica
        data = checkpoint_manager.load()
        assert data["semanas_processadas"] == ["Semana 01"]
        assert data["cards_extraidos"] == 5
        assert data["last_checkpoint_semana"] == "Semana 01"
        
    def test_mark_week_completed(self, checkpoint_manager):
        """Testa marcação de semana como processada."""
        checkpoint_manager.initialize(["Semana 01", "Semana 02"])
        
        # Marca primeira semana
        checkpoint_manager.mark_week_completed("Semana 01", 3)
        checkpoint_manager.save()
        
        data = checkpoint_manager.load()
        assert "Semana 01" in data["semanas_processadas"]
        assert data["cards_extraidos"] == 3
        assert data["last_checkpoint_semana"] == "Semana 01"
        
        # Verifica detalhes do checkpoint
        assert "Semana 01" in data["checkpoints"]
        assert data["checkpoints"]["Semana 01"]["cards"] == 3
        assert data["checkpoints"]["Semana 01"]["status"] == "completed"
        
        # Marca segunda semana
        checkpoint_manager.mark_week_completed("Semana 02", 7)
        checkpoint_manager.save()
        
        data = checkpoint_manager.load()
        assert len(data["semanas_processadas"]) == 2
        assert data["cards_extraidos"] == 10  # 3 + 7
        assert data["last_checkpoint_semana"] == "Semana 02"
        
    def test_checkpoint_status_transitions(self, checkpoint_manager):
        """Testa transições de status do checkpoint."""
        checkpoint_manager.initialize(["Semana 01"])
        
        # Status inicial
        assert checkpoint_manager._checkpoint_data["status"] == "extracting"
        
        # Marca como concluído
        checkpoint_manager.mark_as_completed()
        assert checkpoint_manager._checkpoint_data["status"] == "completed"
        assert "completed_at" in checkpoint_manager._checkpoint_data
        
        # Testa marcação de falha
        checkpoint_manager2 = CheckpointManager("teste_turma2", checkpoint_manager.output_dir, "teste2")
        checkpoint_manager2.initialize(["Semana 01"])
        checkpoint_manager2.mark_as_failed("Erro de teste")
        
        assert checkpoint_manager2._checkpoint_data["status"] == "failed"
        assert checkpoint_manager2._checkpoint_data["error_message"] == "Erro de teste"
        assert "failed_at" in checkpoint_manager2._checkpoint_data
        
    def test_cleanup_removes_checkpoint(self, checkpoint_manager):
        """Testa limpeza de checkpoint após conclusão."""
        checkpoint_manager.initialize(["Semana 01"])
        checkpoint_manager.mark_as_completed()
        checkpoint_manager.save()
        
        # Verifica que arquivo existe
        assert checkpoint_manager.checkpoint_path.exists()
        
        # Limpa checkpoint
        checkpoint_manager.cleanup()
        
        # Verifica que arquivo foi removido
        assert not checkpoint_manager.checkpoint_path.exists()
        
    def test_exists_and_is_recoverable(self, checkpoint_manager):
        """Testa detecção de checkpoint existente e recuperável."""
        # Sem checkpoint
        assert not checkpoint_manager.exists()
        assert not checkpoint_manager.is_recoverable()
        
        # Checkpoint em execução (recuperável)
        checkpoint_manager.initialize(["Semana 01"])
        assert checkpoint_manager.exists()
        assert checkpoint_manager.is_recoverable()
        
        # Checkpoint concluído (não recuperável)
        checkpoint_manager.mark_as_completed()
        checkpoint_manager.save()
        assert checkpoint_manager.exists()
        assert not checkpoint_manager.is_recoverable()
        
    def test_from_existing_classmethod(self, checkpoint_manager):
        """Testa criação de instância a partir de checkpoint existente."""
        checkpoint_manager.initialize(["Semana 01", "Semana 02"])
        checkpoint_manager.mark_week_completed("Semana 01", 5)
        checkpoint_manager.save()
        
        # Cria nova instância carregando dados existentes
        new_manager = CheckpointManager.from_existing(
            "teste_turma", 
            checkpoint_manager.output_dir, 
            "teste_20251017_120000"
        )
        
        # Verifica se dados foram carregados
        assert new_manager._checkpoint_data is not None
        assert new_manager._checkpoint_data["semanas_processadas"] == ["Semana 01"]
        assert new_manager._checkpoint_data["cards_extraidos"] == 5
        
    def test_get_progress_summary(self, checkpoint_manager):
        """Testa geração de resumo de progresso."""
        checkpoint_manager.initialize(["Semana 01", "Semana 02", "Semana 03"])
        checkpoint_manager.mark_week_completed("Semana 01", 3)
        checkpoint_manager.mark_week_completed("Semana 02", 7)
        
        summary = checkpoint_manager.get_progress_summary()
        
        assert summary["turma"] == "teste_turma"
        assert summary["execution_id"] == "teste_20251017_120000"
        assert summary["status"] == "extracting"
        assert summary["semanas_total"] == 3
        assert summary["semanas_processadas"] == 2
        assert summary["semanas_pendentes"] == 1
        assert summary["cards_extraidos"] == 10
        assert summary["last_checkpoint_semana"] == "Semana 02"
        
    def test_checksum_validation(self, checkpoint_manager):
        """Testa validação de integridade via checksum."""
        checkpoint_manager.initialize(["Semana 01"])
        checkpoint_manager.save()
        
        # Corrompe arquivo com JSON inválido
        with open(checkpoint_manager.checkpoint_path, 'w') as f:
            f.write('{"corrupted": true, "invalid": }')  # JSON inválido
            
        # Deve falhar ao carregar
        with pytest.raises(RuntimeError, match="JSON inválido"):
            checkpoint_manager.load()
            
    def test_error_handling(self, checkpoint_manager):
        """Testa tratamento de erros."""
        # Tentativa de operação sem inicialização
        with pytest.raises(RuntimeError, match="Checkpoint não inicializado"):
            checkpoint_manager.mark_week_completed("Semana 01", 1)
            
        with pytest.raises(RuntimeError, match="Checkpoint não inicializado"):
            checkpoint_manager.mark_as_completed()
            
        with pytest.raises(RuntimeError, match="Checkpoint não inicializado"):
            checkpoint_manager.save()
            
        # Tentativa de carregar checkpoint inexistente
        with pytest.raises(FileNotFoundError):
            checkpoint_manager.load()
            
    def test_directory_creation(self, temp_dir):
        """Testa criação automática de diretórios."""
        # Usa subdiretório que não existe
        checkpoint_manager = CheckpointManager("nova_turma", temp_dir, "teste")
        
        # Inicializa - deve criar diretório automaticamente
        checkpoint_manager.initialize(["Semana 01"])
        
        # Verifica se diretório foi criado
        assert checkpoint_manager.turma_dir.exists()
        assert checkpoint_manager.checkpoint_path.exists()
