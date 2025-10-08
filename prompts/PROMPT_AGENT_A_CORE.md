# 🤖 Agent A: Core & Models (FUNDAÇÃO)

## 🎯 Missão
Criar fundação do pacote: modelos de dados e configuração central.

**Prioridade**: 🔴 CRÍTICA (outros agents dependem de você!)

---

## 📦 Estrutura a Criar

```
adalove_extractor/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── card.py          # Card (Pydantic model)
│   └── enriched_card.py # EnrichedCard (Pydantic model)
└── config/
    ├── __init__.py
    ├── settings.py      # Settings (Pydantic Settings)
    └── logging.py       # Logging config
```

Adicione também:
- `pyproject.toml` ou `setup.py` (instalação do pacote)
- `tests/test_models.py` (testes dos models)

---

## ✅ Tarefas Específicas

### 1. Setup de Pacote (Dia 1)
- [ ] Criar `adalove_extractor/__init__.py`
- [ ] Criar `pyproject.toml` com:
  ```toml
  [project]
  name = "adalove-extractor"
  version = "3.0.0"
  requires-python = ">=3.8"
  dependencies = [
      "playwright>=1.49.1",
      "python-dotenv>=1.0.1",
      "pydantic>=2.0.0",
      "pydantic-settings>=2.0.0",
  ]
  
  [project.scripts]
  adalove = "adalove_extractor.cli.main:app"
  ```

### 2. Modelos de Dados (Dia 1-2)

**`models/card.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional

class Card(BaseModel):
    """Card básico extraído do AdaLove."""
    
    semana: str = Field(..., description="Semana (ex: '01', '02')")
    indice: int = Field(..., description="Índice do card no Kanban")
    id: str = Field(..., description="ID único do card")
    titulo: str = Field(..., description="Título do card")
    descricao: Optional[str] = Field(None, description="Descrição")
    tipo: str = Field(..., description="Tipo do card")
    texto_completo: str = Field(..., description="Texto completo")
    links: str = Field(default="", description="Links como string")
    materiais: str = Field(default="", description="Materiais como string")
    arquivos: str = Field(default="", description="Arquivos como string")
    
    class Config:
        frozen = False  # Permitir modificação (para enrichment)
```

**`models/enriched_card.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from .card import Card

class EnrichedCard(Card):
    """Card enriquecido com metadados adicionais."""
    
    # Temporais
    semana_num: int = Field(..., description="Número da semana")
    sprint: int = Field(..., description="Sprint calculada")
    data_hora_iso: Optional[str] = Field(None, description="Data/hora ISO 8601")
    data_ddmmaaaa: Optional[str] = Field(None, description="Data DD/MM/AAAA")
    hora_hhmm: Optional[str] = Field(None, description="Hora HH:MM")
    
    # Identificação
    professor: Optional[str] = Field(None, description="Professor detectado")
    
    # Classificação
    is_instrucao: bool = Field(default=False, description="É instrução?")
    is_autoestudo: bool = Field(default=False, description="É autoestudo?")
    is_atividade_ponderada: bool = Field(default=False, description="É ponderada?")
    
    # Ancoragem
    parent_instruction_id: Optional[str] = Field(None, description="ID da instrução pai")
    parent_instruction_title: Optional[str] = Field(None, description="Título da instrução pai")
    anchor_method: Optional[str] = Field(None, description="Método de ancoragem usado")
    anchor_confidence: Optional[str] = Field(None, description="Confiança da ancoragem")
    
    # URLs
    links_urls: str = Field(default="", description="URLs normalizadas de links")
    materiais_urls: str = Field(default="", description="URLs normalizadas de materiais")
    arquivos_urls: str = Field(default="", description="URLs normalizadas de arquivos")
    num_links: int = Field(default=0, description="Número de links")
    num_materiais: int = Field(default=0, description="Número de materiais")
    num_arquivos: int = Field(default=0, description="Número de arquivos")
    
    # Integridade
    record_hash: str = Field(..., description="Hash único do registro")
```

### 3. Configuração (Dia 2-3)

**`config/settings.py`**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """Configurações globais do extrator."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Credenciais
    login: str
    senha: str
    
    # Extração
    default_output_dir: str = "dados_extraidos"
    headless: bool = True
    interactive: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Enriquecimento
    enable_anchoring: bool = True
    anchor_confidence_threshold: float = 0.6
    
    # Logs
    log_level: str = "INFO"
    log_dir: str = "logs"

# Singleton global
settings = Settings()
```

**`config/logging.py`**:
```python
import logging
import sys
from pathlib import Path
from .settings import settings

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Configura logging centralizado."""
    
    logger = logging.getLogger("adalove_extractor")
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (se especificado)
    if log_file:
        Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            Path(settings.log_dir) / log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger
```

### 4. Exports (Dia 3)

**`adalove_extractor/__init__.py`**:
```python
"""Adalove Extract Cards - Enhanced."""

__version__ = "3.0.0"

from .models.card import Card
from .models.enriched_card import EnrichedCard
from .config.settings import settings

__all__ = ["Card", "EnrichedCard", "settings", "__version__"]
```

### 5. Testes (Dia 3)

**`tests/test_models.py`**:
```python
import pytest
from adalove_extractor.models import Card, EnrichedCard

def test_card_creation():
    """Testa criação de Card básico."""
    card = Card(
        semana="01",
        indice=1,
        id="card_123",
        titulo="Test Card",
        tipo="instrucao",
        texto_completo="Test content"
    )
    assert card.semana == "01"
    assert card.indice == 1

def test_enriched_card_creation():
    """Testa criação de EnrichedCard."""
    card = EnrichedCard(
        semana="01",
        indice=1,
        id="card_123",
        titulo="Test Card",
        tipo="instrucao",
        texto_completo="Test content",
        semana_num=1,
        sprint=1,
        record_hash="abc123"
    )
    assert card.semana_num == 1
    assert card.record_hash == "abc123"

def test_card_validation():
    """Testa validação de campos obrigatórios."""
    with pytest.raises(ValueError):
        Card(titulo="Sem campos obrigatórios")
```

---

## 📋 Checklist de Entrega

- [ ] Estrutura de pacote criada
- [ ] `pyproject.toml` configurado
- [ ] `Card` model implementado com Pydantic
- [ ] `EnrichedCard` model implementado
- [ ] `Settings` implementado com Pydantic Settings
- [ ] `logging.py` configurado
- [ ] Todos exports em `__init__.py`
- [ ] Testes criados e passando
- [ ] Type hints 100%
- [ ] Docstrings em todas classes/funções
- [ ] Instalável via `pip install -e .`

---

## 🧪 Validação

```bash
# Instalar em modo dev
pip install -e .

# Testar imports
python -c "from adalove_extractor import Card, EnrichedCard, settings; print('✅ Imports OK')"

# Rodar testes
pytest tests/test_models.py -v

# Verificar instalação
python -c "import adalove_extractor; print(adalove_extractor.__version__)"
```

---

## 🚨 Importante

- **Type hints obrigatórios**: Todos os campos devem ter tipos
- **Docstrings obrigatórias**: Google format
- **Pydantic v2**: Use versão mais recente
- **Compatibilidade**: Python 3.8+

---

## 📊 Estimativa

**Tempo**: 3-5 dias  
**Complexidade**: 🟢 Baixa  
**Bloqueadores**: Nenhum  

---

**Branch**: `feature/v3.0.0-agent-a-core`  
**Status ao completar**: ✅ Desbloqueia Agents B, C, D

