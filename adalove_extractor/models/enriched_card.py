"""
Modelo de dados para Card enriquecido.

Estende o Card base com 20 campos adicionais de enriquecimento:
- 5 campos de normalização temporal
- 1 campo de detecção de professor
- 3 campos de classificação automática
- 4 campos de ancoragem
- 6 campos de URLs normalizadas
- 1 campo de integridade (hash)
"""

from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field
from .card import CardType


class EnrichedCard(BaseModel):
    """
    Representa um card enriquecido com dados derivados e relacionamentos.
    
    Contém todos os campos do Card base mais 20 campos enriquecidos.
    """
    
    # === Campos básicos (do Card original) ===
    semana: str = Field(description="Nome da semana")
    indice: int = Field(description="Índice do card na lista", ge=1)
    id: str = Field(default="", description="ID único do card")
    titulo: str = Field(default="", description="Título do card")
    descricao: str = Field(default="", description="Descrição completa do modal")
    tipo: str = Field(default="", description="Tipo do card")
    texto_completo: str = Field(default="", description="Texto completo")
    data_hora: Optional[str] = Field(default=None, description="Data/hora para cards de encontro")
    links: str = Field(default="", description="Links encontrados")
    materiais: str = Field(default="", description="Materiais encontrados")
    arquivos: str = Field(default="", description="Arquivos encontrados")
    
    # NOVA TAXONOMIA UNIFICADA
    card_type: CardType = Field(default="outros", description="Tipo do card conforme plataforma AdaLove")
    is_encontro: bool = Field(default=False, description="True se é qualquer tipo de encontro")
    is_sincrono: bool = Field(default=False, description="True se tem data/hora marcada")
    is_avaliativo: bool = Field(default=False, description="True se é avaliação/projeto ponderado")
    
    # SEÇÕES RELACIONADAS
    assuntos_relacionados: List[str] = Field(default_factory=list, description="Lista de assuntos relacionados")
    conteudos_relacionados: List[Dict[str, str]] = Field(default_factory=list, description="Lista de conteúdos relacionados")
    
    # === Normalização temporal (5 campos) ===
    semana_num: Optional[int] = Field(
        default=None, 
        description="Número da semana extraído (1-10)"
    )
    sprint: Optional[int] = Field(
        default=None,
        description="Número do sprint (semana_num dividido por 2 arredondado para cima)"
    )
    data_ddmmaaaa: Optional[str] = Field(
        default=None,
        description="Data em formato brasileiro (dd/mm/aaaa)"
    )
    hora_hhmm: Optional[str] = Field(
        default=None,
        description="Hora em formato 24h (HH:MM)"
    )
    data_hora_iso: Optional[str] = Field(
        default=None,
        description="Data/hora em ISO 8601 com timezone (YYYY-MM-DDTHH:MM:SS-03:00)"
    )
    
    # === Detecção de professor (1 campo) ===
    professor: Optional[str] = Field(
        default=None,
        description="Nome do professor detectado via heurística"
    )
    
    # === Classificação automática (3 campos) - LEGADOS ===
    is_instrucao: bool = Field(
        default=False,
        description="True se o card é uma instrução/encontro (DEPRECADO: usar is_encontro)"
    )
    is_autoestudo: bool = Field(
        default=False,
        description="True se o card é um autoestudo (DEPRECADO: usar card_type)"
    )
    is_atividade_ponderada: bool = Field(
        default=False,
        description="True se o card é uma atividade avaliada (DEPRECADO: usar is_avaliativo)"
    )
    
    # === Sistema de ancoragem (4 campos) ===
    parent_instruction_id: Optional[str] = Field(
        default=None,
        description="ID da instrução à qual este autoestudo está ancorado"
    )
    parent_instruction_title: Optional[str] = Field(
        default=None,
        description="Título da instrução ancorada"
    )
    anchor_method: Optional[str] = Field(
        default=None,
        description="Método usado para ancoragem (ex: 'professor,same_date,sim=0.85')"
    )
    anchor_confidence: Optional[str] = Field(
        default=None,
        description="Confiança da ancoragem: high/medium/low/locked"
    )
    
    # === URLs normalizadas (6 campos) ===
    links_urls: str = Field(
        default="",
        description="URLs de links normalizadas (pipe-separated)"
    )
    materiais_urls: str = Field(
        default="",
        description="URLs de materiais normalizadas (pipe-separated)"
    )
    arquivos_urls: str = Field(
        default="",
        description="URLs de arquivos normalizadas (pipe-separated)"
    )
    num_links: int = Field(
        default=0,
        description="Número de links"
    )
    num_materiais: int = Field(
        default=0,
        description="Número de materiais"
    )
    num_arquivos: int = Field(
        default=0,
        description="Número de arquivos"
    )
    
    # === Integridade (1 campo) ===
    record_hash: str = Field(
        default="",
        description="Hash SHA1 do registro (titulo|data|professor)"
    )
    
    class Config:
        """Configuração do modelo Pydantic."""
        str_strip_whitespace = True
        
    def to_dict(self) -> dict:
        """
        Converte o card enriquecido para dicionário.
        
        Returns:
            Dicionário com todos os campos
        """
        return self.model_dump()







