"""
Checkpoint Manager para persistir estado da extração.

Este módulo implementa o sistema de checkpoints que permite:
- Salvar progresso incrementalmente durante extração
- Detectar execuções interrompidas
- Retomar extração do último ponto válido
- Evitar perda total de dados
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class CheckpointManager:
    """
    Gerenciador de checkpoints para extração resiliente.
    
    Persiste o estado da extração em arquivo JSON, permitindo:
    - Salvamento incremental do progresso
    - Detecção de execuções interrompidas
    - Retomada automática de extrações
    """
    
    def __init__(self, turma: str, output_dir: str, execution_id: str):
        """
        Inicializa o gerenciador de checkpoints.
        
        Args:
            turma: Nome da turma sendo extraída
            output_dir: Diretório base de saída
            execution_id: ID único da execução (formato: turma_YYYYMMDD_HHMMSS)
        """
        self.turma = turma
        self.output_dir = output_dir
        self.execution_id = execution_id
        
        # Caminhos dos arquivos
        self.turma_dir = Path(output_dir) / turma
        self.checkpoint_path = self.turma_dir / "progress.json"
        
        # Estado interno
        self._checkpoint_data: Optional[Dict[str, Any]] = None
        
    def initialize(self, semanas_descobertas: List[str]) -> None:
        """
        Inicializa um novo checkpoint com semanas descobertas.
        
        Args:
            semanas_descobertas: Lista de semanas encontradas no Kanban
        """
        self._checkpoint_data = {
            "turma": self.turma,
            "execution_id": self.execution_id,
            "status": "extracting",
            "semanas_descobertas": semanas_descobertas,
            "semanas_processadas": [],
            "cards_extraidos": 0,
            "ultima_atualizacao": datetime.now().isoformat(),
            "last_checkpoint_semana": None,
            "created_at": datetime.now().isoformat(),
            "checkpoints": {}  # Detalhes por semana
        }
        
        # Cria diretório se necessário
        self.turma_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva checkpoint inicial
        self.save()
        
    def mark_week_completed(self, semana: str, cards_count: int) -> None:
        """
        Marca uma semana como processada e atualiza contadores.
        
        Args:
            semana: Nome da semana (ex: "Semana 01")
            cards_count: Número de cards extraídos nesta semana
        """
        if not self._checkpoint_data:
            raise RuntimeError("Checkpoint não inicializado. Chame initialize() primeiro.")
            
        # Adiciona semana às processadas se não estiver
        if semana not in self._checkpoint_data["semanas_processadas"]:
            self._checkpoint_data["semanas_processadas"].append(semana)
            
        # Atualiza contadores
        self._checkpoint_data["cards_extraidos"] += cards_count
        self._checkpoint_data["last_checkpoint_semana"] = semana
        self._checkpoint_data["ultima_atualizacao"] = datetime.now().isoformat()
        
        # Detalhes do checkpoint desta semana
        self._checkpoint_data["checkpoints"][semana] = {
            "cards": cards_count,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
    def mark_as_completed(self) -> None:
        """Marca a extração como concluída com sucesso."""
        if not self._checkpoint_data:
            raise RuntimeError("Checkpoint não inicializado.")
            
        self._checkpoint_data["status"] = "completed"
        self._checkpoint_data["ultima_atualizacao"] = datetime.now().isoformat()
        self._checkpoint_data["completed_at"] = datetime.now().isoformat()
        
        # Salva automaticamente
        self.save()
        
    def mark_as_failed(self, error_message: str) -> None:
        """
        Marca a extração como falhou.
        
        Args:
            error_message: Mensagem de erro que causou a falha
        """
        if not self._checkpoint_data:
            raise RuntimeError("Checkpoint não inicializado.")
            
        self._checkpoint_data["status"] = "failed"
        self._checkpoint_data["ultima_atualizacao"] = datetime.now().isoformat()
        self._checkpoint_data["failed_at"] = datetime.now().isoformat()
        self._checkpoint_data["error_message"] = error_message
        
        # Salva automaticamente
        self.save()
        
    def save(self) -> None:
        """Salva o checkpoint atual em arquivo JSON."""
        if not self._checkpoint_data:
            raise RuntimeError("Checkpoint não inicializado.")
            
        # Atualiza timestamp
        self._checkpoint_data["ultima_atualizacao"] = datetime.now().isoformat()
        
        # Salva arquivo (sem checksum por enquanto - focar na funcionalidade principal)
        try:
            with open(self.checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(self._checkpoint_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Falha ao salvar checkpoint: {e}")
            
    def load(self) -> Dict[str, Any]:
        """
        Carrega checkpoint do arquivo.
        
        Returns:
            Dados do checkpoint carregados
            
        Raises:
            FileNotFoundError: Se arquivo de checkpoint não existir
            RuntimeError: Se checkpoint estiver corrompido
        """
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint não encontrado: {self.checkpoint_path}")
            
        try:
            with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                    
            self._checkpoint_data = data
            return data
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Checkpoint corrompido: JSON inválido - {e}")
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar checkpoint: {e}")
            
    def exists(self) -> bool:
        """
        Verifica se checkpoint existe e é válido.
        
        Returns:
            True se checkpoint existe e é válido
        """
        if not self.checkpoint_path.exists():
            return False
            
        try:
            self.load()
            return True
        except (RuntimeError, FileNotFoundError):
            return False
            
    def is_recoverable(self) -> bool:
        """
        Verifica se checkpoint pode ser recuperado (não está completed/failed).
        
        Returns:
            True se execução pode ser retomada
        """
        if not self.exists():
            return False
            
        try:
            data = self.load()
            return data.get("status") in ["extracting", "enriching"]
        except Exception:
            return False
            
    def cleanup(self) -> None:
        """
        Remove arquivo de checkpoint após execução bem-sucedida.
        
        Mantém apenas checkpoints com falhas para debug.
        """
        if not self.checkpoint_path.exists():
            return
            
        try:
            # Só remove se status for "completed"
            data = self.load()
            if data.get("status") == "completed":
                self.checkpoint_path.unlink()
        except Exception:
            # Se não conseguir ler, mantém arquivo para debug
            pass
            
    @classmethod
    def from_existing(cls, turma: str, output_dir: str, execution_id: str) -> "CheckpointManager":
        """
        Cria instância carregando checkpoint existente.
        
        Args:
            turma: Nome da turma
            output_dir: Diretório base de saída
            execution_id: ID da execução existente
            
        Returns:
            Instância com checkpoint carregado
        """
        instance = cls(turma, output_dir, execution_id)
        instance.load()  # Carrega dados existentes
        return instance
        
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do progresso atual.
        
        Returns:
            Dicionário com estatísticas de progresso
        """
        if not self._checkpoint_data:
            return {}
            
        semanas_total = len(self._checkpoint_data.get("semanas_descobertas", []))
        semanas_processadas = len(self._checkpoint_data.get("semanas_processadas", []))
        
        return {
            "turma": self.turma,
            "execution_id": self.execution_id,
            "status": self._checkpoint_data.get("status"),
            "semanas_total": semanas_total,
            "semanas_processadas": semanas_processadas,
            "semanas_pendentes": semanas_total - semanas_processadas,
            "cards_extraidos": self._checkpoint_data.get("cards_extraidos", 0),
            "ultima_atualizacao": self._checkpoint_data.get("ultima_atualizacao"),
            "last_checkpoint_semana": self._checkpoint_data.get("last_checkpoint_semana")
        }
