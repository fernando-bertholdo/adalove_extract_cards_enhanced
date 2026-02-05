"""
Modelos Pydantic para requests e responses da API do AdaLove.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class APISection(BaseModel):
    """Seção/Semana retornada pela API."""
    
    id: str = Field(description="ID da seção")
    uuid: str = Field(description="UUID da seção")
    name: str = Field(description="Nome da seção (ex: 'Semana 01')")
    start_date: Optional[datetime] = Field(default=None, description="Data de início")
    end_date: Optional[datetime] = Field(default=None, description="Data de término")
    order: int = Field(description="Ordem da seção")
    
    class Config:
        """Configuração do modelo."""
        str_strip_whitespace = True


class APIActivity(BaseModel):
    """Atividade/Card retornada pela API."""
    
    # Campos básicos
    id: str = Field(description="ID da atividade")
    uuid: str = Field(description="UUID da atividade")
    title: str = Field(description="Título da atividade")
    description: Optional[str] = Field(default=None, description="Descrição completa")
    type: Optional[str] = Field(default=None, description="Tipo da atividade")
    icon_id: Optional[str] = Field(default=None, description="ID do ícone SVG")
    
    # Campos condicionais
    scheduled_at: Optional[datetime] = Field(default=None, description="Data/hora agendada")
    professor_name: Optional[str] = Field(default=None, description="Nome do professor")
    related_subjects: List[str] = Field(default_factory=list, description="Assuntos relacionados")
    related_contents: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Conteúdos relacionados com título e URL"
    )
    
    # Atividade ponderada
    is_graded: bool = Field(default=False, description="Se é atividade avaliativa")
    points: Optional[int] = Field(default=None, description="Pontos da atividade")
    
    # Materiais
    materials: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Materiais de estudo"
    )
    links: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Links externos"
    )
    files: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Arquivos anexados"
    )
    
    class Config:
        """Configuração do modelo."""
        str_strip_whitespace = True


class APISectionActivitiesResponse(BaseModel):
    """Resposta do endpoint de atividades de uma seção."""
    
    section_uuid: str = Field(description="UUID da seção")
    activities: List[APIActivity] = Field(
        default_factory=list, 
        description="Lista de atividades"
    )


class APIUserDetails(BaseModel):
    """Detalhes do usuário retornados pela API."""
    
    id: str = Field(description="ID do usuário")
    name: str = Field(description="Nome completo")
    email: str = Field(description="Email")
    role: Optional[str] = Field(default=None, description="Papel/função")
    
    class Config:
        """Configuração do modelo."""
        str_strip_whitespace = True
