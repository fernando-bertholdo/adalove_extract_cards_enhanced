"""
Testes unitários para IncrementalWriter.

Testa funcionalidades de escrita incremental, backup por semana e validação de integridade.
"""

import json
import pytest
import tempfile
from pathlib import Path

from adalove_extractor.io.incremental_writer import IncrementalWriter


class TestIncrementalWriter:
    """Testes para IncrementalWriter."""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
            
    @pytest.fixture
    def incremental_writer(self, temp_dir):
        """Cria instância de IncrementalWriter para testes."""
        return IncrementalWriter("teste_turma", temp_dir, "teste_20251017_120000")
        
    def test_write_single_card(self, incremental_writer):
        """Testa escrita de card individual."""
        card = {
            "semana": "Semana 01",
            "titulo": "Teste Card",
            "descricao": "Descrição do teste"
        }
        
        incremental_writer.write_card(card)
        
        # Verifica se card foi adicionado ao buffer
        assert len(incremental_writer._cards_buffer) == 1
        
        # Verifica metadata adicionada
        buffered_card = incremental_writer._cards_buffer[0]
        assert buffered_card["titulo"] == "Teste Card"
        assert "_written_at" in buffered_card
        assert "_execution_id" in buffered_card
        assert buffered_card["_execution_id"] == "teste_20251017_120000"
        
    def test_write_batch_cards(self, incremental_writer):
        """Testa escrita de lote de cards."""
        cards = [
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"},
            {"semana": "Semana 01", "titulo": "Card 3"}
        ]
        
        incremental_writer.write_batch(cards)
        
        # Verifica se todos os cards foram adicionados ao buffer
        assert len(incremental_writer._cards_buffer) == 3
        
        # Verifica títulos
        titulos = [card["titulo"] for card in incremental_writer._cards_buffer]
        assert "Card 1" in titulos
        assert "Card 2" in titulos
        assert "Card 3" in titulos
        
    def test_flush_persists_data(self, incremental_writer):
        """Testa que flush persiste dados no arquivo."""
        cards = [
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ]
        
        incremental_writer.write_batch(cards)
        incremental_writer.flush()
        
        # Verifica se arquivo foi criado
        assert incremental_writer.temp_jsonl_path.exists()
        
        # Verifica se buffer foi limpo
        assert len(incremental_writer._cards_buffer) == 0
        
        # Verifica contador
        assert incremental_writer._total_cards_written == 2
        
        # Verifica conteúdo do arquivo
        with open(incremental_writer.temp_jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        assert len(lines) == 2
        
        # Verifica se cada linha é JSON válido
        for line in lines:
            card = json.loads(line.strip())
            assert card["titulo"] in ["Card 1", "Card 2"]
            
    def test_finalize_consolidates(self, incremental_writer):
        """Testa que finalize consolida todos os dados."""
        # Escreve múltiplos batches
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        incremental_writer.flush()
        
        incremental_writer.write_batch([
            {"semana": "Semana 02", "titulo": "Card 3"},
            {"semana": "Semana 02", "titulo": "Card 4"}
        ])
        incremental_writer.flush()
        
        # Finaliza e consolida
        all_cards = incremental_writer.finalize()
        
        # Verifica se todos os cards foram consolidados
        assert len(all_cards) == 4
        
        # Verifica se metadata interna foi removida
        for card in all_cards:
            assert "_written_at" not in card
            assert "_execution_id" not in card
            
        # Verifica títulos
        titulos = [card["titulo"] for card in all_cards]
        assert "Card 1" in titulos
        assert "Card 2" in titulos
        assert "Card 3" in titulos
        assert "Card 4" in titulos
        
    def test_append_only_mode(self, incremental_writer):
        """Testa que modo append preserva dados anteriores."""
        # Primeiro batch
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"}
        ])
        incremental_writer.flush()
        
        # Segundo batch (deve ser appendado)
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        incremental_writer.flush()
        
        # Verifica se arquivo tem ambas as linhas
        with open(incremental_writer.temp_jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        assert len(lines) == 2
        
        # Verifica conteúdo
        card1 = json.loads(lines[0].strip())
        card2 = json.loads(lines[1].strip())
        
        assert card1["titulo"] == "Card 1"
        assert card2["titulo"] == "Card 2"
        
    def test_create_week_backup(self, incremental_writer):
        """Testa criação de backup por semana."""
        cards = [
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ]
        
        backup_path = incremental_writer.create_week_backup("Semana 01", cards)
        
        # Verifica se arquivo de backup foi criado
        assert Path(backup_path).exists()
        
        # Verifica conteúdo do backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            
        assert backup_data["semana"] == "Semana 01"
        assert backup_data["execution_id"] == "teste_20251017_120000"
        assert backup_data["cards_count"] == 2
        assert len(backup_data["cards"]) == 2
        assert "created_at" in backup_data
        
        # Verifica se backup foi registrado
        assert "Semana 01" in incremental_writer._week_backups
        
    def test_get_stats(self, incremental_writer):
        """Testa geração de estatísticas."""
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        incremental_writer.flush()
        
        incremental_writer.create_week_backup("Semana 01", [
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        
        stats = incremental_writer.get_stats()
        
        assert stats["turma"] == "teste_turma"
        assert stats["execution_id"] == "teste_20251017_120000"
        assert stats["total_cards_written"] == 2
        assert stats["cards_in_buffer"] == 0
        assert stats["week_backups"] == 1
        assert len(stats["backup_files"]) == 1
        
    def test_validate_integrity(self, incremental_writer):
        """Testa validação de integridade."""
        # Sem dados - deve ser válido
        assert incremental_writer.validate_integrity()
        
        # Com dados válidos
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        incremental_writer.flush()
        
        assert incremental_writer.validate_integrity()
        
        # Corrompe arquivo
        with open(incremental_writer.temp_jsonl_path, 'w') as f:
            f.write('{"invalid": json}\n')  # JSON inválido
            
        assert not incremental_writer.validate_integrity()
        
    def test_from_existing_classmethod(self, incremental_writer):
        """Testa criação de instância a partir de dados existentes."""
        # Cria dados existentes
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"},
            {"semana": "Semana 01", "titulo": "Card 2"}
        ])
        incremental_writer.flush()
        
        # Cria nova instância carregando dados existentes
        new_writer = IncrementalWriter.from_existing(
            "teste_turma",
            incremental_writer.output_dir,
            "teste_20251017_120000"
        )
        
        # Verifica se contador foi carregado corretamente
        assert new_writer._total_cards_written == 2
        
        # Verifica se pode continuar escrevendo
        new_writer.write_batch([{"semana": "Semana 02", "titulo": "Card 3"}])
        new_writer.flush()
        
        assert new_writer._total_cards_written == 3
        
    def test_cleanup_removes_temp_files(self, incremental_writer):
        """Testa limpeza de arquivos temporários."""
        incremental_writer.write_batch([
            {"semana": "Semana 01", "titulo": "Card 1"}
        ])
        incremental_writer.flush()
        
        # Verifica que arquivo existe
        assert incremental_writer.temp_jsonl_path.exists()
        
        # Limpa arquivos
        incremental_writer.cleanup()
        
        # Verifica que arquivo foi removido
        assert not incremental_writer.temp_jsonl_path.exists()
        
    def test_error_handling(self, incremental_writer):
        """Testa tratamento de erros."""
        # Testa flush com buffer vazio (deve funcionar)
        incremental_writer.flush()
        assert incremental_writer._total_cards_written == 0
        
        # Testa finalize com arquivo inexistente
        all_cards = incremental_writer.finalize()
        assert all_cards == []
        
    def test_directory_creation(self, temp_dir):
        """Testa criação automática de diretórios."""
        # Usa subdiretório que não existe
        writer = IncrementalWriter("nova_turma", temp_dir, "teste")
        
        # Escreve dados - deve criar diretório automaticamente
        writer.write_batch([{"semana": "Semana 01", "titulo": "Card 1"}])
        writer.flush()
        
        # Verifica se diretório foi criado
        assert writer.turma_dir.exists()
        assert writer.temp_jsonl_path.exists()






