"""
Modelo de dados para Card bruto extraído do AdaLove.

Este modelo representa a estrutura básica de um card como extraído da plataforma,
sem enriquecimento de dados.
"""

from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field

CardType = Literal[
    "encontro_instrucao",
    "encontro_orientacao", 
    "autoestudo",
    "avaliacao",
    "projeto",
    "atividade_customizada",
    "outros"
]


class Card(BaseModel):
    """
    Representa um card bruto extraído do Kanban do AdaLove.
    
    Attributes:
        semana: Nome da semana (ex: "Semana 01")
        indice: Posição do card na lista (1-indexed)
        id: ID único do card (data-rbd-draggable-id)
        titulo: Título/primeira linha do card
        descricao: Descrição completa do modal
        tipo: Tipo heurístico (Atividade/Projeto/Avaliação/Material/Outros)
        texto_completo: Texto completo do card incluindo modal
        links: Links encontrados (formato: "Texto: URL | Texto: URL")
        materiais: Materiais encontrados (Google Drive/Docs)
        arquivos: Arquivos encontrados (.pdf, .doc, etc.)
        card_type: Tipo do card conforme plataforma AdaLove
        is_encontro: True se é qualquer tipo de encontro
        is_sincrono: True se tem data/hora marcada
        is_avaliativo: True se é avaliação/projeto ponderado
        assuntos_relacionados: Lista de assuntos relacionados
        conteudos_relacionados: Lista de conteúdos relacionados com título e URL
    """
    
    semana: str = Field(description="Nome da semana")
    indice: int = Field(description="Índice do card na lista", ge=1)
    id: str = Field(default="", description="ID único do card")
    titulo: str = Field(default="", description="Título do card")
    descricao: str = Field(default="", description="Descrição completa do modal")
    tipo: str = Field(default="", description="Tipo do card")
    texto_completo: str = Field(default="", description="Texto completo")
    data_hora: Optional[str] = Field(default=None, description="Data/hora para cards de encontro")
    professor: Optional[str] = Field(default=None, description="Nome do professor para cards de autoestudo")
    links: str = Field(default="", description="Links encontrados")
    materiais: str = Field(default="", description="Materiais encontrados")
    arquivos: str = Field(default="", description="Arquivos encontrados")
    
    # NOVA TAXONOMIA UNIFICADA
    card_type: CardType = Field(
        default="outros",
        description="Tipo do card conforme plataforma AdaLove"
    )
    is_encontro: bool = Field(
        default=False,
        description="True se é qualquer tipo de encontro (instrução ou orientação)"
    )
    is_sincrono: bool = Field(
        default=False,
        description="True se tem data/hora marcada (encontros síncronos)"
    )
    is_avaliativo: bool = Field(
        default=False,
        description="True se é avaliação/projeto ponderado"
    )
    
    # SEÇÕES RELACIONADAS
    assuntos_relacionados: List[str] = Field(
        default_factory=list,
        description="Lista de assuntos relacionados (bullet points)"
    )
    conteudos_relacionados: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Lista de conteúdos relacionados com título e URL"
    )
    
    class Config:
        """Configuração do modelo Pydantic."""
        str_strip_whitespace = True
        
    def to_dict(self) -> dict:
        """
        Converte o card para dicionário para compatibilidade com código legado.
        
        Returns:
            Dicionário com os campos do card
        """
        return self.model_dump()





