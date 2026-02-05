# Design: Extração via API - Fase 2

## 📋 Objetivo

Implementar extração de dados via **API REST do AdaLove** (`apiv2.inteli.edu.br`) mantendo **100% de paridade** com a extração atual via Playwright em termos de:
- ✅ Tipos de cards identificados
- ✅ Campos extraídos por tipo
- ✅ Categorização e enriquecimento
- ✅ Completude dos dados

---

## 🎯 Requisitos de Paridade

### Tipos de Cards Suportados

| Tipo | Ícone | Campos Especiais |
|------|-------|------------------|
| **autoestudo** | `book-open-reader-solido` | professor, assuntos_relacionados, conteudos_relacionados |
| **encontro_instrucao** | `chalkboard-user-solido` | data_hora, professor, assuntos_relacionados |
| **encontro_orientacao** | `user-group-solido` | data_hora, professor, assuntos_relacionados |
| **projeto** | `square-code-solido` | atividade_ponderada (obrigatório) |
| **avaliacao** | `user-pen-solido` | data_hora, professor, atividade_ponderada |

### Campos Extraídos (20+ campos)

**Campos Básicos** (todos os cards):
- `semana` - Nome da semana
- `indice` - Posição na lista
- `id` - UUID do card
- `titulo` - Primeira linha
- `descricao` - Texto completo do modal
- `tipo` - Classificação heurística (legado)
- `texto_completo` - Título + descrição
- `links` - URLs gerais
- `materiais` - Google Drive/Docs
- `arquivos` - PDFs, DOCs, etc.

**Campos de Taxonomia**:
- `card_type` - Tipo oficial (autoestudo, encontro, etc.)
- `is_encontro` - Boolean
- `is_sincrono` - Boolean (tem data/hora)
- `is_avaliativo` - Boolean (é ponderado)

**Campos Condicionais** (dependem do tipo):
- `data_hora` - Para encontros e avaliações
- `professor` - Para autoestudo, encontros, avaliações
- `assuntos_relacionados` - Lista de strings
- `conteudos_relacionados` - Lista de {titulo, url}
- `atividade_ponderada` - {is_ponderada, pontos}

---

## 🏗️ Arquitetura Proposta

### Estrutura de Módulos

```
adalove_extractor/
├── api/                           # 🆕 NOVO
│   ├── __init__.py
│   ├── client.py                  # Cliente HTTP base
│   ├── auth.py                    # Autenticação AWS Cognito
│   ├── endpoints.py               # Definição de endpoints
│   ├── models.py                  # Modelos de request/response
│   └── exceptions.py              # Exceções customizadas
│
├── extractors/
│   ├── playwright/                # 🔄 MOVER código atual
│   │   ├── __init__.py
│   │   ├── week.py
│   │   └── card.py
│   │
│   └── api/                       # 🆕 NOVO
│       ├── __init__.py
│       ├── section.py             # Extração de seções/semanas
│       ├── activity.py            # Extração de atividades/cards
│       └── enrichment.py          # Enriquecimento de dados
│
├── config/
│   └── settings.py                # 🔄 MODIFICAR (adicionar extraction_mode)
│
└── cli/
    └── main.py                    # 🔄 MODIFICAR (seleção de modo)
```

---

## 🔐 Módulo: Autenticação (api/auth.py)

### Fluxo de Autenticação

```
1. Google OAuth (accounts.google.com)
   ↓
2. Callback para AdaLove
   ↓
3. Troca código por token AWS Cognito
   ↓
4. Token usado em todas as requisições
```

### Implementação

```python
import httpx
from typing import Optional

class CognitoAuthenticator:
    """Gerencia autenticação via AWS Cognito OAuth2."""
    
    def __init__(self):
        self.cognito_url = "https://adalove.auth.us-east-2.amazoncognito.com"
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    async def authenticate_google_oauth(
        self, 
        login: str, 
        senha: str
    ) -> str:
        """
        Autentica via Google OAuth e obtém token Cognito.
        
        Passos:
        1. Simula login Google (ou usa Playwright para obter token)
        2. Captura código de autorização
        3. Troca código por token Cognito
        
        Returns:
            Token de acesso Cognito
        """
        # OPÇÃO 1: Usar Playwright apenas para autenticação
        # (mais simples, reutiliza código existente)
        
        # OPÇÃO 2: Simular OAuth flow completo via requests
        # (mais complexo, mas totalmente independente)
        
        pass
    
    async def refresh_access_token(self) -> str:
        """Renova token de acesso usando refresh token."""
        pass
```

---

## 📡 Módulo: Cliente HTTP (api/client.py)

### Cliente Base

```python
import httpx
import logging
from typing import Optional, Dict, Any, List
from .auth import CognitoAuthenticator
from .exceptions import APIError, AuthenticationError

class AdaLoveAPIClient:
    """Cliente HTTP para API do AdaLove."""
    
    def __init__(
        self,
        base_url: str = "https://apiv2.inteli.edu.br",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = httpx.AsyncClient(timeout=timeout)
        self.auth = CognitoAuthenticator()
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self, login: str, senha: str):
        """Autentica e armazena token."""
        token = await self.auth.authenticate_google_oauth(login, senha)
        self.logger.info("✅ Autenticação bem-sucedida")
    
    def _build_headers(self) -> Dict[str, str]:
        """Constrói headers com autenticação."""
        if not self.auth.token:
            raise AuthenticationError("Token não disponível")
        
        return {
            "Authorization": f"Bearer {self.auth.token}",
            "Content-Type": "application/json",
            "User-Agent": "AdaLove-Extractor/3.0"
        }
    
    async def get(
        self, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """GET request com retry automático."""
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        
        for attempt in range(self.max_retries):
            try:
                response = await self.session.get(
                    url, 
                    headers=headers, 
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    # Token expirado, tentar refresh
                    await self.auth.refresh_access_token()
                    continue
                raise APIError(f"HTTP {e.response.status_code}: {e}")
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Falha após {self.max_retries} tentativas: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise APIError("Máximo de tentativas excedido")
```

---

## 📍 Módulo: Endpoints (api/endpoints.py)

### Mapeamento de Endpoints

```python
class Endpoints:
    """Definição centralizada de endpoints da API."""
    
    # Autenticação
    OAUTH_TOKEN = "/oauth2/token"  # Cognito
    
    # Usuário
    USER_DETAILS = "/users/details"
    USER_MENUS = "/users/menus"
    
    # Seções (Semanas)
    SECTIONS = "/sections"
    SECTION_USERDATA = "/sections/{section_uuid}/userdata"
    
    # Atividades (Cards)
    SECTION_ACTIVITIES = "/student-course-descriptions/section/{section_uuid}"
    
    # Notificações
    NOTIFICATIONS = "/notifications"
    
    # Versão
    VERSIONS = "/versions"
    
    @staticmethod
    def section_userdata(section_uuid: str) -> str:
        """Retorna endpoint de userdata para uma seção."""
        return Endpoints.SECTION_USERDATA.format(section_uuid=section_uuid)
    
    @staticmethod
    def section_activities(section_uuid: str) -> str:
        """Retorna endpoint de atividades para uma seção."""
        return Endpoints.SECTION_ACTIVITIES.format(section_uuid=section_uuid)
```

---

## 🎨 Módulo: Modelos de Resposta (api/models.py)

### Modelos Pydantic para API

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class APISection(BaseModel):
    """Seção/Semana retornada pela API."""
    id: str
    uuid: str
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    order: int

class APIActivity(BaseModel):
    """Atividade/Card retornada pela API."""
    id: str
    uuid: str
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    icon_id: Optional[str] = None
    
    # Campos condicionais
    scheduled_at: Optional[datetime] = None
    professor_name: Optional[str] = None
    related_subjects: List[str] = Field(default_factory=list)
    related_contents: List[Dict[str, str]] = Field(default_factory=list)
    
    # Atividade ponderada
    is_graded: bool = False
    points: Optional[int] = None
    
    # Materiais
    materials: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[Dict[str, str]] = Field(default_factory=list)
    files: List[Dict[str, str]] = Field(default_factory=list)

class APISectionActivitiesResponse(BaseModel):
    """Resposta do endpoint de atividades de uma seção."""
    section_uuid: str
    activities: List[APIActivity]
```

---

## 🔄 Módulo: Extração via API (extractors/api/activity.py)

### Extração de Atividades

```python
from typing import List, Optional
import logging
from ...api.client import AdaLoveAPIClient
from ...api.endpoints import Endpoints
from ...api.models import APIActivity
from ...models.card import Card, CardType
from ...models.card_types import get_card_type_from_icon

async def extract_activities_from_section(
    client: AdaLoveAPIClient,
    section_uuid: str,
    section_name: str,
    logger: logging.Logger
) -> List[Card]:
    """
    Extrai todas as atividades de uma seção via API.
    
    Args:
        client: Cliente HTTP autenticado
        section_uuid: UUID da seção
        section_name: Nome da seção (ex: "Semana 01")
        logger: Logger
    
    Returns:
        Lista de Cards extraídos e enriquecidos
    """
    logger.info(f"📥 Extraindo atividades da {section_name}...")
    
    # Buscar atividades da API
    endpoint = Endpoints.section_activities(section_uuid)
    data = await client.get(endpoint)
    
    # Parse response
    activities_data = data.get("activities", [])
    logger.info(f"   📊 {len(activities_data)} atividades encontradas")
    
    cards = []
    for idx, activity_data in enumerate(activities_data):
        try:
            card = await _convert_api_activity_to_card(
                activity_data,
                section_name,
                idx,
                logger
            )
            if card:
                cards.append(card)
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar atividade {idx}: {e}")
            continue
    
    logger.info(f"   ✅ {len(cards)} cards extraídos com sucesso")
    return cards


async def _convert_api_activity_to_card(
    activity_data: dict,
    semana: str,
    indice: int,
    logger: logging.Logger
) -> Optional[Card]:
    """
    Converte dados da API para modelo Card.
    
    IMPORTANTE: Mantém paridade com extração Playwright:
    - Mesmos campos
    - Mesma categorização
    - Mesmo enriquecimento
    """
    
    # Identificar tipo do card pelo ícone
    icon_id = activity_data.get("icon_id", "")
    card_type = get_card_type_from_icon(icon_id)
    
    # Extrair campos básicos
    card_data = {
        "semana": semana,
        "indice": indice + 1,
        "id": activity_data.get("uuid", ""),
        "titulo": activity_data.get("title", ""),
        "descricao": activity_data.get("description", ""),
        "card_type": card_type,
    }
    
    # Texto completo
    if card_data["titulo"] and card_data["descricao"]:
        card_data["texto_completo"] = f"{card_data['titulo']}\\n\\n{card_data['descricao']}"
    else:
        card_data["texto_completo"] = card_data["titulo"] or card_data["descricao"]
    
    # Campos condicionais baseados no tipo
    if card_type in ["encontro_instrucao", "encontro_orientacao", "avaliacao"]:
        card_data["data_hora"] = activity_data.get("scheduled_at")
        card_data["is_sincrono"] = True
    
    if card_type in ["autoestudo", "encontro_instrucao", "encontro_orientacao", "avaliacao"]:
        card_data["professor"] = activity_data.get("professor_name")
    
    if card_type in ["autoestudo", "encontro_instrucao", "encontro_orientacao"]:
        card_data["assuntos_relacionados"] = activity_data.get("related_subjects", [])
    
    if card_type == "autoestudo":
        card_data["conteudos_relacionados"] = activity_data.get("related_contents", [])
    
    if card_type in ["projeto", "avaliacao"]:
        card_data["is_avaliativo"] = activity_data.get("is_graded", False)
        # Extrair pontos se disponível
    
    # Taxonomia
    card_data["is_encontro"] = card_type in ["encontro_instrucao", "encontro_orientacao"]
    
    # Materiais e links
    card_data["links"], card_data["materiais"], card_data["arquivos"] = _extract_materials(
        activity_data.get("materials", []),
        activity_data.get("links", []),
        activity_data.get("files", [])
    )
    
    # Tipo heurístico (legado)
    card_data["tipo"] = _map_card_type_to_legacy_tipo(card_type)
    
    return Card(**card_data)


def _extract_materials(
    materials: List[dict],
    links: List[dict],
    files: List[dict]
) -> tuple[str, str, str]:
    """
    Extrai e categoriza materiais, links e arquivos.
    
    Mantém formato compatível com Playwright:
    - links: "Texto: URL | Texto: URL"
    - materiais: "Texto: URL | Texto: URL"
    - arquivos: "Texto: URL | Texto: URL"
    """
    links_str = []
    materiais_str = []
    arquivos_str = []
    
    # Processar materials
    for material in materials:
        url = material.get("url", "")
        text = material.get("title", "Link")
        
        if "drive.google.com" in url or "docs.google.com" in url:
            materiais_str.append(f"{text}: {url}")
        elif any(url.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".ppt", ".pptx"]):
            arquivos_str.append(f"{text}: {url}")
        else:
            links_str.append(f"{text}: {url}")
    
    # Processar links
    for link in links:
        url = link.get("url", "")
        text = link.get("text", "Link")
        links_str.append(f"{text}: {url}")
    
    # Processar files
    for file in files:
        url = file.get("url", "")
        text = file.get("name", "Arquivo")
        arquivos_str.append(f"{text}: {url}")
    
    return (
        " | ".join(links_str),
        " | ".join(materiais_str),
        " | ".join(arquivos_str)
    )


def _map_card_type_to_legacy_tipo(card_type: str) -> str:
    """Mapeia card_type para campo 'tipo' legado."""
    mapping = {
        "autoestudo": "Material",
        "encontro_instrucao": "Atividade",
        "encontro_orientacao": "Atividade",
        "projeto": "Projeto",
        "avaliacao": "Avaliação",
        "outros": "Outros"
    }
    return mapping.get(card_type, "Outros")
```

---

## ✅ Checklist de Paridade

### Campos Obrigatórios
- [ ] semana
- [ ] indice
- [ ] id
- [ ] titulo
- [ ] descricao
- [ ] tipo (legado)
- [ ] texto_completo
- [ ] links
- [ ] materiais
- [ ] arquivos
- [ ] card_type
- [ ] is_encontro
- [ ] is_sincrono
- [ ] is_avaliativo

### Campos Condicionais
- [ ] data_hora (encontros, avaliações)
- [ ] professor (autoestudo, encontros, avaliações)
- [ ] assuntos_relacionados (autoestudo, encontros)
- [ ] conteudos_relacionados (autoestudo)
- [ ] atividade_ponderada (projeto, avaliação)

### Categorização
- [ ] Identificação correta de 5 tipos de cards
- [ ] Flags booleanas (is_encontro, is_sincrono, is_avaliativo)
- [ ] Tipo legado compatível

---

## 🧪 Testes de Paridade

```python
# tests/test_api_parity.py

async def test_card_extraction_parity():
    """
    Testa paridade entre Playwright e API.
    
    Extrai mesma semana com ambos métodos e compara:
    - Número de cards
    - Campos obrigatórios
    - Categorização
    """
    
    # Extrair via Playwright
    cards_playwright = await extract_via_playwright("Semana 01")
    
    # Extrair via API
    cards_api = await extract_via_api("Semana 01")
    
    # Comparar
    assert len(cards_playwright) == len(cards_api)
    
    for card_pw, card_api in zip(cards_playwright, cards_api):
        assert card_pw.titulo == card_api.titulo
        assert card_pw.card_type == card_api.card_type
        assert card_pw.is_encontro == card_api.is_encontro
        # ... outros campos
```

---

## 📊 Próximos Passos

1. **Implementar autenticação** (api/auth.py)
2. **Implementar cliente HTTP** (api/client.py)
3. **Implementar extração de atividades** (extractors/api/activity.py)
4. **Testes de paridade** (comparar com Playwright)
5. **Modo híbrido** (API + fallback Playwright)

**Estimativa**: 3-5 dias de desenvolvimento
