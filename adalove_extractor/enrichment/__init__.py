"""
Sistema de enriquecimento de dados.

Transforma cards brutos em cards enriquecidos com:
- Normalização temporal (datas, horas, sprints)
- Detecção de professor
- Classificação automática
- Ancoragem de autoestudos às instruções
- Normalização de URLs
- Hash de integridade
"""

from .engine import EnrichmentEngine

__all__ = ["EnrichmentEngine"]








