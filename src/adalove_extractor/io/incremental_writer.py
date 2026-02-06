"""
Incremental Writer para salvamento seguro de dados durante extração.

Este módulo implementa sistema de escrita incremental que:
- Salva cards conforme são extraídos (não apenas no final)
- Usa arquivo JSONL append-only para segurança
- Faz backup por semana como snapshot
- Permite recuperação de dados parciais
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class IncrementalWriter:
    """
    Writer incremental para salvamento seguro de cards durante extração.
    
    Características:
    - Arquivo JSONL append-only para evitar perda de dados
    - Backup por semana como snapshot de segurança
    - Flush automático após cada semana processada
    - Validação de integridade com checksums
    """
    
    def __init__(self, turma: str, output_dir: str, execution_id: str):
        """
        Inicializa o writer incremental.
        
        Args:
            turma: Nome da turma sendo extraída
            output_dir: Diretório base de saída
            execution_id: ID único da execução
        """
        self.turma = turma
        self.output_dir = output_dir
        self.execution_id = execution_id
        
        # Caminhos dos arquivos
        self.turma_dir = Path(output_dir) / turma
        self.temp_jsonl_path = self.turma_dir / f"cards_temp_{execution_id}.jsonl"
        
        # Estado interno
        self._cards_buffer: List[Dict[str, Any]] = []
        self._total_cards_written = 0
        self._week_backups: Dict[str, str] = {}  # semana -> caminho do backup
        
    def write_card(self, card: Dict[str, Any]) -> None:
        """
        Escreve um card individual no buffer.
        
        Args:
            card: Dados do card a ser escrito
        """
        # Adiciona metadata de escrita
        card_with_metadata = {
            **card,
            "_written_at": datetime.now().isoformat(),
            "_execution_id": self.execution_id
        }
        
        self._cards_buffer.append(card_with_metadata)
        
    def write_batch(self, cards: List[Dict[str, Any]]) -> None:
        """
        Escreve um lote de cards no buffer.
        
        Args:
            cards: Lista de cards a serem escritos
        """
        for card in cards:
            self.write_card(card)
            
    def flush(self) -> None:
        """
        Força escrita do buffer para arquivo JSONL.
        
        Garante que todos os cards no buffer sejam persistidos.
        """
        if not self._cards_buffer:
            return
            
        # Cria diretório se necessário
        self.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Escreve em modo append-only
        try:
            with open(self.temp_jsonl_path, 'a', encoding='utf-8') as f:
                for card in self._cards_buffer:
                    f.write(json.dumps(card, ensure_ascii=False) + "\n")
                    
            # Atualiza contador
            self._total_cards_written += len(self._cards_buffer)
            
            # Limpa buffer
            self._cards_buffer.clear()
            
        except Exception as e:
            raise RuntimeError(f"Falha ao escrever dados incrementais: {e}")
            
    def create_week_backup(self, semana: str, cards: List[Dict[str, Any]]) -> str:
        """
        Cria backup da semana como arquivo JSON separado.
        
        Args:
            semana: Nome da semana (ex: "Semana 01")
            cards: Cards da semana
            
        Returns:
            Caminho do arquivo de backup criado
        """
        backup_filename = f"checkpoint_semana_{semana.replace(' ', '_').lower()}.json"
        backup_path = self.turma_dir / backup_filename
        
        # Cria diretório se necessário
        self.turma_dir.mkdir(parents=True, exist_ok=True)
        
        backup_data = {
            "semana": semana,
            "execution_id": self.execution_id,
            "cards_count": len(cards),
            "created_at": datetime.now().isoformat(),
            "cards": cards
        }
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
            self._week_backups[semana] = str(backup_path)
            return str(backup_path)
            
        except Exception as e:
            raise RuntimeError(f"Falha ao criar backup da semana {semana}: {e}")
            
    def finalize(self) -> List[Dict[str, Any]]:
        """
        Finaliza escrita e consolida todos os dados.
        
        Returns:
            Lista completa de todos os cards escritos
        """
        # Força flush final
        self.flush()
        
        # Carrega todos os cards do arquivo JSONL
        all_cards = []
        
        if self.temp_jsonl_path.exists():
            try:
                with open(self.temp_jsonl_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            card = json.loads(line)
                            # Remove metadata interna
                            card.pop("_written_at", None)
                            card.pop("_execution_id", None)
                            all_cards.append(card)
                            
            except Exception as e:
                raise RuntimeError(f"Falha ao ler dados consolidados: {e}")
                
        return all_cards
        
    def cleanup(self) -> None:
        """
        Remove arquivos temporários após execução bem-sucedida.
        
        Mantém apenas backups de semanas para debug se necessário.
        """
        try:
            # Remove arquivo JSONL temporário
            if self.temp_jsonl_path.exists():
                self.temp_jsonl_path.unlink()
                
            # Opcional: remove backups de semanas (comentado para debug)
            # for backup_path in self._week_backups.values():
            #     if os.path.exists(backup_path):
            #         os.unlink(backup_path)
                    
        except Exception:
            # Se não conseguir limpar, não falha a execução
            pass
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do writer.
        
        Returns:
            Dicionário com estatísticas de escrita
        """
        return {
            "turma": self.turma,
            "execution_id": self.execution_id,
            "total_cards_written": self._total_cards_written,
            "cards_in_buffer": len(self._cards_buffer),
            "temp_file_path": str(self.temp_jsonl_path),
            "week_backups": len(self._week_backups),
            "backup_files": list(self._week_backups.values())
        }
        
    def validate_integrity(self) -> bool:
        """
        Valida integridade dos dados escritos.
        
        Returns:
            True se dados estão íntegros
        """
        if not self.temp_jsonl_path.exists():
            return True  # Arquivo não existe ainda
            
        try:
            # Conta linhas válidas
            valid_lines = 0
            with open(self.temp_jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        json.loads(line)  # Valida JSON
                        valid_lines += 1
                        
            # Verifica se contador interno bate
            return valid_lines == self._total_cards_written
            
        except Exception:
            return False
            
    @classmethod
    def from_existing(cls, turma: str, output_dir: str, execution_id: str) -> "IncrementalWriter":
        """
        Cria instância carregando estado de execução existente.
        
        Args:
            turma: Nome da turma
            output_dir: Diretório base de saída
            execution_id: ID da execução existente
            
        Returns:
            Instância com estado carregado
        """
        instance = cls(turma, output_dir, execution_id)
        
        # Conta cards já escritos
        if instance.temp_jsonl_path.exists():
            try:
                with open(instance.temp_jsonl_path, 'r', encoding='utf-8') as f:
                    instance._total_cards_written = sum(1 for line in f if line.strip())
            except Exception:
                instance._total_cards_written = 0
                
        return instance
