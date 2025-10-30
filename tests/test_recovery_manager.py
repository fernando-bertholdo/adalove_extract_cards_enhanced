"""
Testes unitários para RecoveryManager.

Testa funcionalidades de detecção, recuperação e consolidação de dados.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from adalove_extractor.io.recovery import RecoveryManager
from adalove_extractor.io.checkpoint import CheckpointManager
from adalove_extractor.io.incremental_writer import IncrementalWriter


class TestRecoveryManager:
    """Testes para RecoveryManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
            
    @pytest.fixture
    def recovery_manager(self, temp_dir):
        """Cria instância de RecoveryManager para testes."""
        return RecoveryManager("teste_turma", temp_dir)
        
    def test_detect_no_checkpoint(self, recovery_manager):
        """Testa detecção quando não há checkpoint."""
        assert not recovery_manager.detect_interrupted()
        
    def test_detect_existing_checkpoint(self, recovery_manager):
        """Testa detecção de checkpoint existente."""
        # Cria checkpoint válido
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01", "Semana 02"])
        checkpoint_mgr.save()
        
        assert recovery_manager.detect_interrupted()
        
    def test_load_checkpoint(self, recovery_manager):
        """Testa carregamento de checkpoint."""
        # Cria checkpoint
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01", "Semana 02"])
        checkpoint_mgr.mark_week_completed("Semana 01", 5)
        checkpoint_mgr.save()
        
        # Carrega via RecoveryManager
        checkpoint = recovery_manager.load_checkpoint()
        
        assert checkpoint["turma"] == "teste_turma"
        assert checkpoint["execution_id"] == "teste_id"
        assert checkpoint["status"] == "extracting"
        assert "Semana 01" in checkpoint["semanas_processadas"]
        assert checkpoint["cards_extraidos"] == 5
        
    def test_load_checkpoint_not_found(self, recovery_manager):
        """Testa erro quando checkpoint não existe."""
        with pytest.raises(RuntimeError, match="Nenhum checkpoint encontrado"):
            recovery_manager.load_checkpoint()
            
    def test_load_temp_data(self, recovery_manager):
        """Testa carregamento de dados temporários."""
        # Cria arquivo JSONL temporário
        temp_file = recovery_manager.turma_dir / "cards_temp_test_id.jsonl"
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        
        cards_data = [
            {"semana": "Semana 01", "titulo": "Card 1", "_written_at": "2025-01-01", "_execution_id": "test"},
            {"semana": "Semana 01", "titulo": "Card 2", "_written_at": "2025-01-01", "_execution_id": "test"}
        ]
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            for card in cards_data:
                f.write(json.dumps(card) + "\n")
                
        # Carrega dados
        loaded_cards = recovery_manager.load_temp_data()
        
        assert len(loaded_cards) == 2
        assert loaded_cards[0]["titulo"] == "Card 1"
        assert loaded_cards[1]["titulo"] == "Card 2"
        
        # Verifica se metadata interna foi removida
        for card in loaded_cards:
            assert "_written_at" not in card
            assert "_execution_id" not in card
            
    def test_load_temp_data_multiple_files(self, recovery_manager):
        """Testa carregamento de múltiplos arquivos temporários."""
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria múltiplos arquivos temp
        temp_files = [
            recovery_manager.turma_dir / "cards_temp_exec1.jsonl",
            recovery_manager.turma_dir / "cards_temp_exec2.jsonl"
        ]
        
        for i, temp_file in enumerate(temp_files):
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps({"semana": f"Semana {i+1:02d}", "titulo": f"Card {i+1}"}) + "\n")
                
        # Carrega dados
        loaded_cards = recovery_manager.load_temp_data()
        
        assert len(loaded_cards) == 2
        
        # Verifica títulos (ordem pode variar)
        titulos = [card["titulo"] for card in loaded_cards]
        assert "Card 1" in titulos
        assert "Card 2" in titulos
        
    def test_merge_temp_data(self, recovery_manager):
        """Testa consolidação de dados temporários."""
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria arquivo com dados duplicados
        temp_file = recovery_manager.turma_dir / "cards_temp_test.jsonl"
        cards_data = [
            {"semana": "Semana 01", "titulo": "Card 1", "descricao": "Desc 1"},
            {"semana": "Semana 01", "titulo": "Card 1", "descricao": "Desc 1"},  # Duplicata
            {"semana": "Semana 01", "titulo": "Card 2", "descricao": "Desc 2"}
        ]
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            for card in cards_data:
                f.write(json.dumps(card) + "\n")
                
        # Consolida dados
        merged_cards = recovery_manager.merge_temp_data()
        
        # Deve ter removido duplicata
        assert len(merged_cards) == 2
        assert merged_cards[0]["titulo"] == "Card 1"
        assert merged_cards[1]["titulo"] == "Card 2"
        
    def test_prompt_recovery(self, recovery_manager):
        """Testa prompt interativo de recuperação."""
        # Cria checkpoint
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01", "Semana 02"])
        checkpoint_mgr.mark_week_completed("Semana 01", 5)
        checkpoint_mgr.save()
        
        # Simula input do usuário
        with patch('builtins.input', side_effect=['c']):
            opcao = recovery_manager.prompt_recovery()
            assert opcao == 'continue'
            
        with patch('builtins.input', side_effect=['r']):
            opcao = recovery_manager.prompt_recovery()
            assert opcao == 'restart'
            
        with patch('builtins.input', side_effect=['a']):
            opcao = recovery_manager.prompt_recovery()
            assert opcao == 'abort'
            
        # Testa opção padrão (Enter)
        with patch('builtins.input', side_effect=['']):
            opcao = recovery_manager.prompt_recovery()
            assert opcao == 'continue'
            
    def test_cleanup_all(self, recovery_manager):
        """Testa limpeza completa de arquivos."""
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria arquivos para limpar
        checkpoint_path = recovery_manager.turma_dir / "progress.json"
        temp_file = recovery_manager.turma_dir / "cards_temp_test.jsonl"
        backup_file = recovery_manager.turma_dir / "checkpoint_semana_01.json"
        
        checkpoint_path.write_text('{"test": true}')
        temp_file.write_text('{"test": true}')
        backup_file.write_text('{"test": true}')
        
        # Verifica que arquivos existem
        assert checkpoint_path.exists()
        assert temp_file.exists()
        assert backup_file.exists()
        
        # Limpa tudo
        recovery_manager.cleanup_all()
        
        # Verifica que arquivos foram removidos
        assert not checkpoint_path.exists()
        assert not temp_file.exists()
        assert not backup_file.exists()
        
    def test_cleanup_after_recovery(self, recovery_manager):
        """Testa limpeza após recuperação."""
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria arquivos
        temp_file = recovery_manager.turma_dir / "cards_temp_test.jsonl"
        backup_file = recovery_manager.turma_dir / "checkpoint_semana_01.json"
        
        temp_file.write_text('{"test": true}')
        backup_file.write_text('{"test": true}')
        
        # Limpa apenas arquivos temporários
        recovery_manager.cleanup_after_recovery()
        
        # Verifica que apenas temp foi removido
        assert not temp_file.exists()
        assert backup_file.exists()  # Backup deve ser mantido
        
    def test_get_recovery_summary(self, recovery_manager):
        """Testa geração de resumo de recuperação."""
        # Sem checkpoint
        summary = recovery_manager.get_recovery_summary()
        assert summary["status"] == "no_interruption"
        
        # Com checkpoint válido
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01", "Semana 02"])
        checkpoint_mgr.mark_week_completed("Semana 01", 5)
        checkpoint_mgr.save()
        
        # Cria dados temporários
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        temp_file = recovery_manager.turma_dir / "cards_temp_test_id.jsonl"
        with open(temp_file, 'w') as f:
            f.write('{"semana": "Semana 01", "titulo": "Card 1"}\n')
            
        summary = recovery_manager.get_recovery_summary()
        
        assert summary["status"] == "interrupted"
        assert summary["temp_cards_count"] == 1
        assert summary["semanas_processadas"] == 1
        assert summary["semanas_total"] == 2
        assert summary["execution_id"] == "teste_id"
        
    def test_validate_recovery_data(self, recovery_manager):
        """Testa validação de dados de recuperação."""
        # Sem checkpoint
        is_valid, errors = recovery_manager.validate_recovery_data()
        assert not is_valid
        assert "Nenhum checkpoint encontrado" in errors[0]
        
        # Com checkpoint válido
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01"])
        checkpoint_mgr.mark_week_completed("Semana 01", 2)
        checkpoint_mgr.save()
        
        # Cria dados temporários correspondentes
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        temp_file = recovery_manager.turma_dir / "cards_temp_test_id.jsonl"
        with open(temp_file, 'w') as f:
            f.write('{"semana": "Semana 01", "titulo": "Card 1"}\n')
            f.write('{"semana": "Semana 01", "titulo": "Card 2"}\n')
            
        is_valid, errors = recovery_manager.validate_recovery_data()
        assert is_valid
        assert len(errors) == 0
        
        # Com inconsistência
        with open(temp_file, 'w') as f:
            f.write('{"semana": "Semana 01", "titulo": "Card 1"}\n')  # Apenas 1 card
        
        is_valid, errors = recovery_manager.validate_recovery_data()
        assert not is_valid
        assert "Inconsistência" in errors[0]
        
    def test_resume_from(self, recovery_manager):
        """Testa preparação para retomada."""
        # Cria checkpoint e dados temporários
        checkpoint_mgr = CheckpointManager("teste_turma", recovery_manager.output_dir, "teste_id")
        checkpoint_mgr.initialize(["Semana 01", "Semana 02"])
        checkpoint_mgr.mark_week_completed("Semana 01", 2)
        checkpoint_mgr.save()
        
        recovery_manager.turma_dir.mkdir(parents=True, exist_ok=True)
        temp_file = recovery_manager.turma_dir / "cards_temp_teste_id.jsonl"
        with open(temp_file, 'w') as f:
            f.write('{"semana": "Semana 01", "titulo": "Card 1"}\n')
            f.write('{"semana": "Semana 01", "titulo": "Card 2"}\n')
            
        # Prepara retomada
        checkpoint_mgr_resume, incremental_writer_resume = recovery_manager.resume_from("teste_id")
        
        # Verifica se instâncias foram criadas corretamente
        assert isinstance(checkpoint_mgr_resume, CheckpointManager)
        assert isinstance(incremental_writer_resume, IncrementalWriter)
        
        # Verifica se dados foram carregados
        assert checkpoint_mgr_resume._checkpoint_data is not None
        assert incremental_writer_resume._total_cards_written == 2
