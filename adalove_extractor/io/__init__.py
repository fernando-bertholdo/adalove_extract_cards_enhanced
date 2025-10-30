"""
Módulo de Input/Output para extração resiliente.

Inclui:
- Writers para exportação de dados
- CheckpointManager para persistência de estado
- IncrementalWriter para salvamento seguro
- RecoveryManager para recuperação de execuções interrompidas
"""

from .writers import write_cards_csv, write_enriched_outputs, compute_stats_by_week
from .checkpoint import CheckpointManager
from .incremental_writer import IncrementalWriter
from .recovery import RecoveryManager

__all__ = [
    "write_cards_csv",
    "write_enriched_outputs", 
    "compute_stats_by_week",
    "CheckpointManager",
    "IncrementalWriter",
    "RecoveryManager"
]

