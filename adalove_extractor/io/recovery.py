"""
Recovery Manager para detecção e retomada de execuções interrompidas.

Este módulo implementa sistema de recuperação que:
- Detecta automaticamente execuções interrompidas
- Oferece interface interativa para retomada
- Consolida dados de múltiplas execuções
- Limpa arquivos temporários após recuperação
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .checkpoint import CheckpointManager
from .incremental_writer import IncrementalWriter


class RecoveryManager:
    """
    Gerenciador de recuperação para execuções interrompidas.
    
    Funcionalidades:
    - Detecção automática de checkpoints órfãos
    - Interface interativa para escolha de ação
    - Consolidação de dados de múltiplas execuções
    - Limpeza de arquivos temporários
    """
    
    def __init__(self, turma: str, output_dir: str):
        """
        Inicializa o gerenciador de recuperação.
        
        Args:
            turma: Nome da turma
            output_dir: Diretório base de saída
        """
        self.turma = turma
        self.output_dir = output_dir
        self.turma_dir = Path(output_dir) / turma
        
    def detect_interrupted(self) -> bool:
        """
        Detecta se existe execução interrompida para esta turma.
        
        Returns:
            True se existe checkpoint recuperável
        """
        checkpoint_path = self.turma_dir / "progress.json"
        
        if not checkpoint_path.exists():
            return False
            
        try:
            checkpoint_mgr = CheckpointManager(self.turma, self.output_dir, "dummy")
            return checkpoint_mgr.is_recoverable()
        except Exception:
            return False
            
    def load_checkpoint(self) -> Dict[str, Any]:
        """
        Carrega dados do checkpoint interrompido.
        
        Returns:
            Dados do checkpoint
            
        Raises:
            RuntimeError: Se não conseguir carregar checkpoint
        """
        checkpoint_path = self.turma_dir / "progress.json"
        
        if not checkpoint_path.exists():
            raise RuntimeError("Nenhum checkpoint encontrado")
            
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar checkpoint: {e}")
            
    def load_temp_data(self) -> List[Dict[str, Any]]:
        """
        Carrega dados do arquivo JSONL temporário.
        
        Returns:
            Lista de cards já extraídos
        """
        all_cards = []
        
        # Procura por arquivos temp_*.jsonl
        temp_files = list(self.turma_dir.glob("cards_temp_*.jsonl"))
        
        for temp_file in temp_files:
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            card = json.loads(line)
                            # Remove metadata interna
                            card.pop("_written_at", None)
                            card.pop("_execution_id", None)
                            all_cards.append(card)
            except Exception as e:
                print(f"⚠️ Aviso: Erro ao ler arquivo {temp_file}: {e}")
                
        return all_cards
        
    def merge_temp_data(self) -> List[Dict[str, Any]]:
        """
        Consolida dados de múltiplos arquivos temporários.
        
        Returns:
            Lista consolidada de cards únicos
        """
        all_cards = self.load_temp_data()
        
        # Remove duplicatas baseado em campos únicos
        seen_cards = set()
        unique_cards = []
        
        for card in all_cards:
            # Cria chave única baseada em semana + título + descrição
            key = (
                card.get("semana", ""),
                card.get("titulo", ""),
                card.get("descricao", "")
            )
            
            if key not in seen_cards:
                seen_cards.add(key)
                unique_cards.append(card)
                
        return unique_cards
        
    def prompt_recovery(self) -> str:
        """
        Exibe prompt interativo para recuperação.
        
        Returns:
            Opção escolhida: 'continue', 'restart', 'abort'
        """
        checkpoint = self.load_checkpoint()
        
        print(f"\n⚠️  EXECUÇÃO ANTERIOR DETECTADA!")
        print(f"📊 Progresso: {len(checkpoint.get('semanas_processadas', []))}/{len(checkpoint.get('semanas_descobertas', []))} semanas")
        print(f"📝 Cards extraídos: {checkpoint.get('cards_extraidos', 0)}")
        print(f"⏰ Última atualização: {checkpoint.get('ultima_atualizacao', 'N/A')}")
        print(f"🔄 Status: {checkpoint.get('status', 'unknown')}")
        
        print(f"\n❓ Escolha uma opção:")
        print(f"   (C)ontinuar de onde parou")
        print(f"   (R)ecomeçar do zero")
        print(f"   (A)bortar")
        
        while True:
            try:
                opcao = input("\nOpção [C/r/a]: ").strip().lower()
                
                if opcao in ['c', '']:
                    return 'continue'
                elif opcao == 'r':
                    return 'restart'
                elif opcao == 'a':
                    return 'abort'
                else:
                    print("Opção inválida. Digite C, R ou A.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Entrada cancelada pelo usuário")
                return 'abort'
                
    def cleanup_all(self) -> None:
        """
        Remove todos os arquivos de checkpoint e temporários.
        """
        try:
            # Remove checkpoint principal
            checkpoint_path = self.turma_dir / "progress.json"
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                
            # Remove arquivos temporários JSONL
            temp_files = list(self.turma_dir.glob("cards_temp_*.jsonl"))
            for temp_file in temp_files:
                temp_file.unlink()
                
            # Remove backups de semanas
            backup_files = list(self.turma_dir.glob("checkpoint_semana_*.json"))
            for backup_file in backup_files:
                backup_file.unlink()
                
            print("🧹 Limpeza concluída.")
            
        except Exception as e:
            print(f"⚠️ Aviso: Erro durante limpeza: {e}")
            
    def cleanup_after_recovery(self) -> None:
        """
        Limpa arquivos temporários após recuperação bem-sucedida.
        """
        try:
            # Remove apenas arquivos temporários, mantém backups para debug
            temp_files = list(self.turma_dir.glob("cards_temp_*.jsonl"))
            for temp_file in temp_files:
                temp_file.unlink()
                
        except Exception as e:
            print(f"⚠️ Aviso: Erro durante limpeza pós-recuperação: {e}")
            
    def get_recovery_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo da situação de recuperação.
        
        Returns:
            Dicionário com informações de recuperação
        """
        if not self.detect_interrupted():
            return {"status": "no_interruption"}
            
        try:
            checkpoint = self.load_checkpoint()
            temp_cards = self.load_temp_data()
            
            return {
                "status": "interrupted",
                "checkpoint": checkpoint,
                "temp_cards_count": len(temp_cards),
                "semanas_processadas": len(checkpoint.get("semanas_processadas", [])),
                "semanas_total": len(checkpoint.get("semanas_descobertas", [])),
                "execution_id": checkpoint.get("execution_id"),
                "last_update": checkpoint.get("ultima_atualizacao")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def validate_recovery_data(self) -> Tuple[bool, List[str]]:
        """
        Valida integridade dos dados de recuperação.
        
        Returns:
            Tupla (is_valid, error_messages)
        """
        errors = []
        
        try:
            checkpoint = self.load_checkpoint()
            
            # Valida estrutura básica do checkpoint
            required_fields = ["turma", "execution_id", "status", "semanas_descobertas"]
            for field in required_fields:
                if field not in checkpoint:
                    errors.append(f"Campo obrigatório ausente: {field}")
                    
            # Valida dados temporários
            temp_cards = self.load_temp_data()
            
            # Verifica se número de cards bate com checkpoint
            checkpoint_cards = checkpoint.get("cards_extraidos", 0)
            if len(temp_cards) != checkpoint_cards:
                errors.append(f"Inconsistência: checkpoint diz {checkpoint_cards} cards, mas encontrados {len(temp_cards)}")
                
            # Valida estrutura dos cards
            for i, card in enumerate(temp_cards[:5]):  # Valida apenas primeiros 5
                if not isinstance(card, dict):
                    errors.append(f"Card {i} não é dicionário")
                    continue
                    
                if "semana" not in card:
                    errors.append(f"Card {i} sem campo 'semana'")
                    
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Erro na validação: {e}"]
            
    def resume_from(self, execution_id: str) -> Tuple[CheckpointManager, IncrementalWriter]:
        """
        Prepara instâncias para retomada de execução.
        
        Args:
            execution_id: ID da execução a ser retomada
            
        Returns:
            Tupla (CheckpointManager, IncrementalWriter) configurados
        """
        checkpoint_mgr = CheckpointManager.from_existing(
            self.turma, self.output_dir, execution_id
        )
        
        incremental_writer = IncrementalWriter.from_existing(
            self.turma, self.output_dir, execution_id
        )
        
        return checkpoint_mgr, incremental_writer






