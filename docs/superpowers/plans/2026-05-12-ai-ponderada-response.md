# AI Ponderada Response — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir bugs existentes, modernizar o README e implementar a feature "Gerar resposta com IA" no `menu_ponderada` do adalove_cli.py, usando o `claude` CLI como subprocess.

**Architecture:** Novo módulo `src/adalove_extractor/ai/` com separação clara (context_builder → system_prompt → answer_generator). O `adalove_cli.py` orquestra o fluxo de UX. Submissão via API com fallback para arquivo.

**Tech Stack:** Python 3.11+, httpx (já existente), subprocess (stdlib), `claude` CLI (externo, já instalado), pytest, rich, questionary.

---

## File Map

| Ação | Arquivo | Responsabilidade |
|------|---------|-----------------|
| CREATE | `tests/conftest.py` | Adiciona `src/` ao sys.path para pytest |
| MODIFY | `requirements.txt` | Remove playwright, adiciona httpx |
| MODIFY | `pyproject.toml` | Sincroniza versão e dependências |
| CREATE | `.env.example` | Template documentado de variáveis |
| MODIFY | `README.md` | Versão moderna e profissional |
| CREATE | `src/adalove_extractor/ai/__init__.py` | Exports do módulo ai |
| CREATE | `src/adalove_extractor/ai/context_builder.py` | Monta contexto completo para o prompt |
| CREATE | `src/adalove_extractor/ai/system_prompt.py` | Carrega e combina system prompt |
| CREATE | `src/adalove_extractor/ai/answer_generator.py` | Chama claude CLI, retorna texto |
| CREATE | `src/adalove_extractor/config/default_system_prompt.md` | Template padrão editável |
| MODIFY | `src/adalove_extractor/api/endpoints.py` | Adiciona endpoint de submissão |
| MODIFY | `src/adalove_extractor/api/client.py` | Adiciona put() e submit_answer() |
| MODIFY | `adalove_cli.py` | Nova opção no menu_ponderada |
| CREATE | `tests/unit/__init__.py` | Pacote |
| CREATE | `tests/unit/ai/__init__.py` | Pacote |
| CREATE | `tests/unit/ai/test_context_builder.py` | Testes do context_builder |
| CREATE | `tests/unit/ai/test_system_prompt.py` | Testes do system_prompt |
| CREATE | `tests/unit/ai/test_answer_generator.py` | Testes do answer_generator (subprocess mockado) |

---

## Task 1: Corrigir bugs de infraestrutura

**Files:**
- Create: `tests/conftest.py`
- Modify: `requirements.txt`
- Modify: `pyproject.toml`
- Create: `.env.example`

- [ ] **Step 1.1: Criar tests/conftest.py**

```python
# tests/conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

- [ ] **Step 1.2: Verificar que os testes existentes passam**

```bash
cd /Users/fernandobertholdo/Documents/Inteli/adalove_extract_cards_enhanced
source venv/bin/activate
pip install -e ".[dev]" -q
pytest tests/ -v --no-cov 2>&1 | head -40
```

Esperado: testes coletados sem `ModuleNotFoundError`. (Podem falhar por outras razões — OK por enquanto.)

- [ ] **Step 1.3: Corrigir requirements.txt**

Substituir o conteúdo completo:

```
# Dependências para executar o AdaLove Extractor
httpx>=0.27.0
python-dotenv==1.0.1
pydantic>=2.7.0
pydantic-settings>=2.0.0
rich>=13.0.0
questionary>=2.0.0
icalendar>=5.0.0
pytz>=2024.1
```

- [ ] **Step 1.4: Corrigir pyproject.toml — versão e dependências**

Na seção `[project]`, mudar `version = "3.0.0"` para `version = "2.0.0"`.

Na seção `dependencies`, substituir:
```toml
dependencies = [
    "httpx>=0.27.0",
    "python-dotenv>=1.0.1",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.0.0",
    "rich>=13.0.0",
    "questionary>=2.0.0",
    "icalendar>=5.0.0",
    "pytz>=2024.1",
]
```

- [ ] **Step 1.5: Criar .env.example**

```bash
# .env.example — copie para .env e preencha com suas credenciais
# cp .env.example .env

# === Autenticação AdaLove ===
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha_aqui

# === Configurações de extração ===
MAX_RETRIES=3
LOG_LEVEL=INFO
OUTPUT_DIR=dados_extraidos
```

- [ ] **Step 1.6: Verificar instalação limpa**

```bash
pip install -r requirements.txt -q && echo "OK"
```

Esperado: `OK` sem erros de playwright ou dependências ausentes.

- [ ] **Step 1.7: Commit**

```bash
git add tests/conftest.py requirements.txt pyproject.toml .env.example
git commit -m "fix: corrigir dependências, versão e path de testes"
```

---

## Task 2: Modernizar README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 2.1: Reescrever README.md com estrutura moderna**

Substituir o conteúdo completo pelo seguinte:

```markdown
# Adalove Extract Cards — Enhanced

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/architecture-API--first-brightgreen)](#arquitetura)

> **Aviso:** Este projeto tem fins acadêmicos e educacionais. Use com responsabilidade e respeite os termos de uso da plataforma AdaLove.

CLI interativa para extrair cards da plataforma AdaLove via API, organizar encontros e autoestudos por semana, e gerar respostas para atividades ponderadas com IA.

---

## Quick Start

```bash
# 1. Clone e configure ambiente
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure credenciais
cp .env.example .env
# edite .env com seu login e senha do AdaLove

# 3. Execute
python adalove_cli.py
```

---

## O que faz

| Recurso | Descrição |
|---------|-----------|
| **Extração via API** | Extrai cards sem automação de browser (~10s/turma) |
| **Organização por semana** | JSON hierárquico com encontros e autoestudos por data |
| **Ancoragem multi-fator** | Vincula autoestudos aos encontros corretos (professor + proximidade + título) |
| **Viewer de ponderadas** | Lista atividades avaliativas com status, prazo e nota |
| **Exportação de calendário** | Gera `.ics` com todos os encontros para importar no Google Calendar |
| **Resposta com IA** | Gera rascunho de resposta para ponderadas usando Claude, com contexto dos materiais |

---

## Estrutura de Saída

```
output/api_extraction/
└── 2026-1A-T13/
    ├── extracao_completa.json    # Todas as semanas
    ├── 2026-1A-T13_calendario.ics
    ├── rascunhos/                # Rascunhos gerados por IA
    └── semanas/
        ├── semana_01.json
        └── ...
```

**Formato do JSON:**

```json
{
  "encontros": {
    "2026-03-23": {
      "dia_semana": "Segunda-feira",
      "titulo": "Suporte ao Projeto",
      "tipo": "encontro_instrucao",
      "professor": "Nome do Professor",
      "autoestudos": {
        "Título do autoestudo": {
          "descricao": "...",
          "professor": "...",
          "ancora_confianca": "high"
        }
      }
    }
  }
}
```

---

## Arquitetura

```
src/adalove_extractor/
├── api/           # Cliente HTTP + autenticação AWS Cognito
├── extractors/    # Extração completa de turma
├── enrichment/    # Ancoragem multi-fator de autoestudos
├── ai/            # Geração de respostas com IA (claude CLI)
├── io/            # Writers, calendário, checkpoints
├── models/        # Tipos de cards e dados enriquecidos
├── config/        # Settings (pydantic) + system prompt padrão
└── utils/         # Hash, texto, helpers
```

| Módulo | Responsabilidade |
|--------|-----------------|
| `api/client.py` | HTTP assíncrono com auth, retry e submissão |
| `extractors/turma_completa.py` | Orquestra extração completa de uma turma |
| `enrichment/anchor.py` | Sistema de ancoragem multi-fator |
| `ai/context_builder.py` | Monta contexto para geração de resposta |
| `ai/answer_generator.py` | Chama `claude` CLI como subprocess |
| `io/calendar.py` | Exportação para formato iCalendar |

---

## Configuração

Edite `.env` (criado a partir de `.env.example`):

```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

Para personalizar o estilo das respostas geradas por IA, edite:
```
src/adalove_extractor/config/default_system_prompt.md
```

---

## Desenvolvimento

```bash
# Instalar com dependências de dev
pip install -e ".[dev]"

# Rodar testes
pytest tests/ -v

# Verificar tipos
mypy src/adalove_extractor/
```

---

## Créditos e Licença

- **Projeto original:** [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards)
- **Esta versão:** Fernando Bertholdo
- **Licença:** MIT — veja [LICENSE](LICENSE)
```

- [ ] **Step 2.2: Commit**

```bash
git add README.md
git commit -m "docs: modernizar README com estrutura profissional"
```

---

## Task 3: Criar default_system_prompt.md e esqueleto do módulo ai/

**Files:**
- Create: `src/adalove_extractor/config/default_system_prompt.md`
- Create: `src/adalove_extractor/ai/__init__.py`

- [ ] **Step 3.1: Criar default_system_prompt.md**

```markdown
# System Prompt Padrão — Geração de Respostas para Ponderadas

Você é um assistente que ajuda um estudante universitário a elaborar respostas para atividades avaliativas (ponderadas) de um curso de tecnologia.

## Estilo de Escrita

- Escreva **como um estudante que ainda está aprendendo** — não como um especialista ou uma IA
- Use linguagem coloquial, mas seguindo a norma culta do português brasileiro
- **Não use hífen (-) para listar itens**; prefira parágrafos ou frases conectadas
- **Não use travessão (—)** como recurso estilístico
- Evite jargões técnicos excessivos; quando necessário, explique brevemente
- Não use expressões clichê de IA (ex: "é crucial", "no âmbito de", "destaca-se que", "vale ressaltar")
- Responda de forma completa, objetivando a nota máxima, mas sem ser prolixo

## Sobre o Conteúdo

- Use **apenas as informações presentes no contexto fornecido** (materiais do curso, transcrição, notas)
- Se o contexto não cobrir algum ponto da pergunta, mencione brevemente que o tema foi abordado em aula mas não dê detalhes inventados
- Priorize ideias e conceitos do professor sobre fontes externas
- Conecte os autoestudos relacionados de forma coesa na resposta

## Formato da Resposta

- Responda diretamente à pergunta, sem introdução genérica ("Nesta atividade ponderada...")
- Use parágrafos curtos (3-5 linhas)
- Se houver múltiplos pontos a responder, organize em parágrafos temáticos, não em listas com hífens
```

- [ ] **Step 3.2: Criar src/adalove_extractor/ai/__init__.py**

```python
"""Módulo de geração de respostas com IA para atividades ponderadas."""

from .context_builder import ContextBuilder
from .system_prompt import SystemPromptLoader
from .answer_generator import AnswerGenerator

__all__ = ["ContextBuilder", "SystemPromptLoader", "AnswerGenerator"]
```

- [ ] **Step 3.3: Commit**

```bash
git add src/adalove_extractor/config/default_system_prompt.md src/adalove_extractor/ai/__init__.py
git commit -m "feat(ai): adicionar system prompt padrão e esqueleto do módulo"
```

---

## Task 4: Implementar context_builder.py com TDD

**Files:**
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/ai/__init__.py`
- Create: `tests/unit/ai/test_context_builder.py`
- Create: `src/adalove_extractor/ai/context_builder.py`

- [ ] **Step 4.1: Criar pacotes de teste**

```bash
touch tests/unit/__init__.py tests/unit/ai/__init__.py
```

- [ ] **Step 4.2: Escrever testes para ContextBuilder**

```python
# tests/unit/ai/test_context_builder.py
import tempfile
import pytest
from pathlib import Path
from adalove_extractor.ai.context_builder import ContextBuilder


POND_FIXTURE = {
    "titulo": "Implementar CRUD",
    "data_encontro": "2026-03-23",
    "encontro_titulo": "Aula de APIs REST",
    "professor": "Prof. Silva",
    "semana": "Semana 08",
    "avaliacao": {
        "pergunta": "Como você implementaria um CRUD com FastAPI?",
        "peso": 3,
    },
    "descricao": "Atividade sobre criação de APIs REST.",
    "student_activity_uuid": "abc-123",
}

EXTRACAO_FIXTURE = {
    "semanas": {
        "Semana 08": {
            "encontros": {
                "2026-03-23": {
                    "titulo": "Aula de APIs REST",
                    "tipo": "encontro_instrucao",
                    "professor": "Prof. Silva",
                    "descricao": "Aula sobre FastAPI e CRUD.",
                    "autoestudos": {
                        "Leitura: FastAPI Docs": {
                            "descricao": "Leia a documentação oficial do FastAPI.",
                            "professor": "Prof. Silva",
                            "conteudos_relacionados": ["https://fastapi.tiangolo.com"],
                        }
                    },
                }
            },
            "sem_ancora": [],
        }
    }
}


def test_build_returns_non_empty_string():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert isinstance(result, str)
    assert len(result) > 100


def test_build_includes_question():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "Como você implementaria um CRUD com FastAPI?" in result


def test_build_includes_autoestudo_content():
    builder = ContextBuilder()
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "Leitura: FastAPI Docs" in result
    assert "documentação oficial do FastAPI" in result


def test_build_includes_transcript_when_provided():
    builder = ContextBuilder()
    transcript = "O professor explicou que FastAPI usa Pydantic para validação."
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, transcript=transcript)
    assert "Pydantic para validação" in result


def test_build_includes_user_notes_when_provided():
    builder = ContextBuilder()
    notes = "Entregar link do GitHub com código funcional."
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, user_notes=notes)
    assert "Entregar link do GitHub" in result


def test_build_without_optional_context():
    builder = ContextBuilder()
    # Sem transcrição e sem notas — não deve lançar erro
    result = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    assert "PERGUNTA DA ATIVIDADE" in result


def test_build_skeleton_prompt_is_shorter():
    builder = ContextBuilder()
    full = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE)
    skeleton = builder.build(POND_FIXTURE, EXTRACAO_FIXTURE, skeleton_mode=True)
    # Skeleton mode adiciona instrução de gerar apenas estrutura
    assert "esqueleto" in skeleton.lower() or "estrutura" in skeleton.lower()
```

- [ ] **Step 4.3: Rodar testes para confirmar que falham**

```bash
pytest tests/unit/ai/test_context_builder.py -v --no-cov 2>&1 | tail -15
```

Esperado: `ImportError` ou `ModuleNotFoundError` (ainda não implementado).

- [ ] **Step 4.4: Implementar context_builder.py**

```python
# src/adalove_extractor/ai/context_builder.py
"""Monta o contexto completo para geração de resposta de ponderada."""

from __future__ import annotations


class ContextBuilder:
    """Constrói o prompt de usuário com todo o contexto disponível."""

    def build(
        self,
        ponderada: dict,
        extracao_data: dict,
        transcript: str | None = None,
        user_notes: str | None = None,
        skeleton_mode: bool = False,
    ) -> str:
        """
        Monta o prompt completo para envio ao claude CLI.

        Args:
            ponderada: Dict com dados da ponderada (de extrair_ponderadas).
            extracao_data: Dict completo da extração (extracao_completa.json).
            transcript: Texto da transcrição de aula (opcional).
            user_notes: Notas adicionais do usuário (opcional).
            skeleton_mode: Se True, solicita apenas esqueleto/estrutura.

        Returns:
            String com o prompt completo.
        """
        sections: list[str] = []

        # --- 1. Metadados da ponderada ---
        aval = ponderada.get("avaliacao", {})
        sections.append("## ATIVIDADE PONDERADA")
        sections.append(f"**Título:** {ponderada.get('titulo', '')}")
        sections.append(f"**Semana:** {ponderada.get('semana', '')} — {ponderada.get('data_encontro', '')}")
        sections.append(f"**Encontro relacionado:** {ponderada.get('encontro_titulo', '')}")
        sections.append(f"**Professor:** {ponderada.get('professor', '')}")
        sections.append(f"**Peso:** {aval.get('peso', '?')}")
        if ponderada.get("descricao"):
            sections.append(f"\n**Descrição da atividade:**\n{ponderada['descricao']}")

        # --- 2. Pergunta ---
        pergunta = aval.get("pergunta", "")
        if pergunta:
            sections.append(f"\n## PERGUNTA DA ATIVIDADE\n{pergunta}")

        # --- 3. Contexto do encontro + autoestudos ---
        autoestudos = self._extract_autoestudos(ponderada, extracao_data)
        if autoestudos:
            sections.append("\n## MATERIAIS E AUTOESTUDOS RELACIONADOS")
            for titulo, auto in autoestudos.items():
                sections.append(f"\n### {titulo}")
                if auto.get("descricao"):
                    sections.append(auto["descricao"])
                if auto.get("conteudos_relacionados"):
                    links = "\n".join(f"- {c}" for c in auto["conteudos_relacionados"])
                    sections.append(f"**Links:**\n{links}")

        # --- 4. Transcrição (opcional) ---
        if transcript and transcript.strip():
            sections.append(f"\n## TRANSCRIÇÃO DA AULA\n{transcript.strip()}")

        # --- 5. Notas do usuário (opcional) ---
        if user_notes and user_notes.strip():
            sections.append(f"\n## INSTRUÇÕES E NOTAS ADICIONAIS\n{user_notes.strip()}")

        # --- 6. Instrução final ---
        if skeleton_mode:
            sections.append(
                "\n## TAREFA\n"
                "Com base no contexto acima, gere APENAS o **esqueleto/estrutura** da resposta. "
                "Inclua:\n"
                "1. Formato de entrega detectado (ex: texto corrido, link GitHub, etc.)\n"
                "2. Tópicos principais que serão abordados (3-5 pontos)\n"
                "3. Instruções do professor identificadas no contexto\n"
                "4. Fontes de contexto que serão usadas\n\n"
                "NÃO escreva a resposta completa ainda. Apenas a estrutura para validação."
            )
        else:
            sections.append(
                "\n## TAREFA\n"
                "Com base em todo o contexto acima, escreva a resposta completa para a "
                "atividade ponderada. Siga as instruções de estilo do system prompt e "
                "priorize o conteúdo do contexto fornecido."
            )

        return "\n".join(sections)

    def _extract_autoestudos(self, ponderada: dict, extracao_data: dict) -> dict:
        """Extrai autoestudos do encontro ancorado à ponderada."""
        data_encontro = ponderada.get("data_encontro")
        semana = ponderada.get("semana")

        if not data_encontro or not semana:
            return {}

        semana_data = extracao_data.get("semanas", {}).get(semana, {})
        encontro = semana_data.get("encontros", {}).get(data_encontro, {})
        return encontro.get("autoestudos", {})
```

- [ ] **Step 4.5: Rodar testes e confirmar que passam**

```bash
pytest tests/unit/ai/test_context_builder.py -v --no-cov
```

Esperado: todos os 7 testes passam.

- [ ] **Step 4.6: Commit**

```bash
git add src/adalove_extractor/ai/context_builder.py tests/unit/__init__.py tests/unit/ai/__init__.py tests/unit/ai/test_context_builder.py
git commit -m "feat(ai): implementar ContextBuilder com testes"
```

---

## Task 5: Implementar system_prompt.py com TDD

**Files:**
- Create: `tests/unit/ai/test_system_prompt.py`
- Create: `src/adalove_extractor/ai/system_prompt.py`

- [ ] **Step 5.1: Escrever testes**

```python
# tests/unit/ai/test_system_prompt.py
import pytest
from pathlib import Path
import tempfile
from adalove_extractor.ai.system_prompt import SystemPromptLoader


def test_load_returns_string():
    loader = SystemPromptLoader()
    result = loader.load()
    assert isinstance(result, str)
    assert len(result) > 50


def test_load_contains_default_content():
    loader = SystemPromptLoader()
    result = loader.load()
    # O default_system_prompt.md deve conter instruções de estilo
    assert "hífen" in result or "estudante" in result


def test_load_with_session_additions():
    loader = SystemPromptLoader()
    additions = "Entregar apenas o link do repositório GitHub no campo de resposta."
    result = loader.load(session_additions=additions)
    assert "link do repositório GitHub" in result


def test_load_with_empty_session_additions():
    loader = SystemPromptLoader()
    result_without = loader.load()
    result_with_empty = loader.load(session_additions="")
    assert result_without == result_with_empty


def test_load_custom_path(tmp_path):
    custom_prompt = tmp_path / "custom_system_prompt.md"
    custom_prompt.write_text("# Prompt customizado\nFaça respostas curtas.")
    loader = SystemPromptLoader(prompt_path=custom_prompt)
    result = loader.load()
    assert "Faça respostas curtas" in result


def test_load_fallback_when_file_missing(tmp_path):
    nonexistent = tmp_path / "nao_existe.md"
    loader = SystemPromptLoader(prompt_path=nonexistent)
    # Deve retornar string não-vazia mesmo sem o arquivo
    result = loader.load()
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 5.2: Rodar testes para confirmar que falham**

```bash
pytest tests/unit/ai/test_system_prompt.py -v --no-cov 2>&1 | tail -10
```

Esperado: `ImportError`.

- [ ] **Step 5.3: Implementar system_prompt.py**

```python
# src/adalove_extractor/ai/system_prompt.py
"""Carrega e combina o system prompt padrão com adições por sessão."""

from __future__ import annotations
from pathlib import Path

_DEFAULT_PROMPT_PATH = (
    Path(__file__).parent.parent / "config" / "default_system_prompt.md"
)

_FALLBACK_PROMPT = (
    "Você é um assistente que ajuda um estudante universitário a elaborar "
    "respostas para atividades avaliativas. Escreva como um estudante em "
    "aprendizado, usando português coloquial mas correto. Sem hífens em listas, "
    "sem clichês de IA, sem jargão excessivo. Responda de forma completa."
)


class SystemPromptLoader:
    """Carrega system prompt do arquivo padrão e combina com adições por sessão."""

    def __init__(self, prompt_path: Path | None = None):
        self._path = prompt_path or _DEFAULT_PROMPT_PATH

    def load(self, session_additions: str | None = None) -> str:
        """
        Retorna o system prompt completo.

        Args:
            session_additions: Instruções extras adicionadas pelo usuário nesta sessão.

        Returns:
            String com system prompt pronto para uso.
        """
        base = self._load_base()

        if session_additions and session_additions.strip():
            base = (
                base
                + "\n\n## INSTRUÇÕES ADICIONAIS PARA ESTA RESPOSTA\n"
                + session_additions.strip()
            )

        return base

    def _load_base(self) -> str:
        try:
            return self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return _FALLBACK_PROMPT
```

- [ ] **Step 5.4: Rodar testes**

```bash
pytest tests/unit/ai/test_system_prompt.py -v --no-cov
```

Esperado: todos os 6 testes passam.

- [ ] **Step 5.5: Commit**

```bash
git add src/adalove_extractor/ai/system_prompt.py tests/unit/ai/test_system_prompt.py
git commit -m "feat(ai): implementar SystemPromptLoader com testes"
```

---

## Task 6: Implementar answer_generator.py com TDD

**Files:**
- Create: `tests/unit/ai/test_answer_generator.py`
- Create: `src/adalove_extractor/ai/answer_generator.py`

- [ ] **Step 6.1: Escrever testes (subprocess mockado)**

```python
# tests/unit/ai/test_answer_generator.py
import pytest
from unittest.mock import patch, MagicMock
from adalove_extractor.ai.answer_generator import AnswerGenerator, ClaudeNotFoundError


MOCK_RESPONSE = "Esta é uma resposta gerada pelo Claude sobre FastAPI e CRUD."


def _mock_run_success(*args, **kwargs):
    m = MagicMock()
    m.returncode = 0
    m.stdout = MOCK_RESPONSE
    m.stderr = ""
    return m


def _mock_run_failure(*args, **kwargs):
    m = MagicMock()
    m.returncode = 1
    m.stdout = ""
    m.stderr = "Error: authentication required"
    return m


def test_generate_returns_string_on_success():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=_mock_run_success):
        result = gen.generate(user_prompt="pergunta", system_prompt="instrucoes")
    assert result == MOCK_RESPONSE


def test_generate_raises_on_nonzero_returncode():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=_mock_run_failure):
        with pytest.raises(RuntimeError, match="claude"):
            gen.generate(user_prompt="pergunta", system_prompt="instrucoes")


def test_generate_raises_claude_not_found_when_missing():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
        with pytest.raises(ClaudeNotFoundError):
            gen.generate(user_prompt="pergunta", system_prompt="instrucoes")


def test_generate_strips_whitespace():
    gen = AnswerGenerator()
    with patch("subprocess.run", side_effect=lambda *a, **k: MagicMock(
        returncode=0, stdout="  resposta com espaços  \n", stderr=""
    )):
        result = gen.generate(user_prompt="p", system_prompt="s")
    assert result == "resposta com espaços"


def test_generate_passes_system_prompt_in_call():
    gen = AnswerGenerator()
    captured = {}

    def capture_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return MagicMock(returncode=0, stdout="ok", stderr="")

    with patch("subprocess.run", side_effect=capture_run):
        gen.generate(user_prompt="usuario", system_prompt="SISTEMA")

    # O system prompt deve aparecer no comando
    full_cmd = " ".join(str(x) for x in captured["args"][0])
    assert "SISTEMA" in full_cmd or "system" in full_cmd.lower()
```

- [ ] **Step 6.2: Rodar testes para confirmar que falham**

```bash
pytest tests/unit/ai/test_answer_generator.py -v --no-cov 2>&1 | tail -10
```

Esperado: `ImportError`.

- [ ] **Step 6.3: Implementar answer_generator.py**

```python
# src/adalove_extractor/ai/answer_generator.py
"""Gera respostas usando o claude CLI como subprocess."""

from __future__ import annotations
import subprocess
import logging

logger = logging.getLogger(__name__)


class ClaudeNotFoundError(Exception):
    """Levantada quando o claude CLI não está instalado/disponível."""


class AnswerGenerator:
    """Chama o claude CLI em modo não-interativo e retorna o texto gerado."""

    def __init__(self, timeout: int = 180):
        self.timeout = timeout

    def generate(self, user_prompt: str, system_prompt: str) -> str:
        """
        Gera texto via claude CLI.

        Args:
            user_prompt: Contexto + tarefa montados pelo ContextBuilder.
            system_prompt: Instruções de estilo carregadas pelo SystemPromptLoader.

        Returns:
            Texto gerado pelo Claude.

        Raises:
            ClaudeNotFoundError: Se claude CLI não estiver no PATH.
            RuntimeError: Se claude retornar código de erro.
        """
        # Embute o system prompt no início do prompt do usuário
        # pois o claude CLI via -p não tem flag dedicada de system prompt
        full_prompt = (
            f"<system>\n{system_prompt}\n</system>\n\n"
            f"<user>\n{user_prompt}\n</user>"
        )

        cmd = ["claude", "-p", full_prompt]

        logger.debug("Chamando claude CLI...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError as e:
            raise ClaudeNotFoundError(
                "claude CLI não encontrado no PATH. "
                "Instale via: npm install -g @anthropic-ai/claude-code"
            ) from e

        if result.returncode != 0:
            error_msg = result.stderr or "erro desconhecido"
            raise RuntimeError(
                f"claude CLI retornou código {result.returncode}: {error_msg}"
            )

        return result.stdout.strip()
```

- [ ] **Step 6.4: Rodar testes**

```bash
pytest tests/unit/ai/test_answer_generator.py -v --no-cov
```

Esperado: todos os 5 testes passam.

- [ ] **Step 6.5: Commit**

```bash
git add src/adalove_extractor/ai/answer_generator.py tests/unit/ai/test_answer_generator.py
git commit -m "feat(ai): implementar AnswerGenerator com subprocess do claude CLI"
```

---

## Task 7: Adicionar put() e submit_answer() ao cliente HTTP

**Files:**
- Modify: `src/adalove_extractor/api/endpoints.py`
- Modify: `src/adalove_extractor/api/client.py`

- [ ] **Step 7.1: Adicionar endpoint de submissão em endpoints.py**

Adicionar ao final da classe `Endpoints`, antes do último `@staticmethod`:

```python
    # Submissão de resposta de atividade
    STUDENT_ACTIVITY_ANSWER = "/student-activities/{student_activity_uuid}"

    @staticmethod
    def student_activity_answer(student_activity_uuid: str) -> str:
        """Endpoint para submeter resposta de atividade ponderada."""
        return Endpoints.STUDENT_ACTIVITY_ANSWER.format(
            student_activity_uuid=student_activity_uuid
        )
```

- [ ] **Step 7.2: Adicionar método put() em client.py**

Adicionar após o método `post()`, antes de `close()`:

```python
    async def put(
        self,
        endpoint: str,
        json: dict | None = None,
        **kwargs,
    ) -> dict:
        """
        PUT request com retry automático.

        Args:
            endpoint: Endpoint da API.
            json: JSON body.

        Returns:
            Resposta JSON da API (ou dict vazio em respostas 204).

        Raises:
            APIError: Em caso de erro na requisição.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()

        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"📡 PUT {endpoint} (tentativa {attempt + 1}/{self.max_retries})")
                response = await self.session.put(
                    url,
                    headers=headers,
                    json=json,
                    **kwargs,
                )
                response.raise_for_status()
                self.logger.debug(f"✅ PUT {endpoint} - {response.status_code}")
                if response.status_code == 204 or not response.content:
                    return {}
                return response.json()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Erro no PUT: {e}")
                await asyncio.sleep(2 ** attempt)

        raise APIError(f"Máximo de tentativas excedido para PUT {endpoint}")
```

- [ ] **Step 7.3: Adicionar submit_answer() em client.py**

Adicionar após `put()`, antes de `close()`:

```python
    async def submit_answer(
        self,
        student_activity_uuid: str,
        answer_text: str,
    ) -> bool:
        """
        Submete resposta para uma atividade ponderada.

        NOTA: O endpoint exato de submissão pode precisar de ajuste se a API
        mudar. O campo 'studyAnswer' foi confirmado na leitura dos dados via
        section_userdata. O endpoint PUT /student-activities/{uuid} é a
        abordagem REST mais provável para atualização.

        Args:
            student_activity_uuid: UUID da atividade do estudante.
            answer_text: Texto da resposta a submeter.

        Returns:
            True se submissão bem-sucedida, False caso contrário.
        """
        endpoint = Endpoints.student_activity_answer(student_activity_uuid)
        try:
            await self.put(endpoint, json={"studyAnswer": answer_text})
            self.logger.info(f"✅ Resposta submetida para {student_activity_uuid}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Falha ao submeter resposta: {e}")
            return False
```

- [ ] **Step 7.4: Verificar que o cliente ainda importa sem erros**

```bash
python -c "from adalove_extractor.api.client import AdaLoveAPIClient; print('OK')"
```

Esperado: `OK`.

- [ ] **Step 7.5: Commit**

```bash
git add src/adalove_extractor/api/endpoints.py src/adalove_extractor/api/client.py
git commit -m "feat(api): adicionar método put() e submit_answer() ao cliente HTTP"
```

---

## Task 8: Integrar feature no adalove_cli.py

**Files:**
- Modify: `adalove_cli.py`

A integração tem duas partes: (A) nova opção no `menu_ponderada` e (B) função `gerar_resposta_ia()`.

- [ ] **Step 8.1: Adicionar imports do módulo ai no topo de adalove_cli.py**

Após a linha `from adalove_extractor.io.calendar import ICalendarExport`, adicionar:

```python
from adalove_extractor.ai.context_builder import ContextBuilder
from adalove_extractor.ai.system_prompt import SystemPromptLoader
from adalove_extractor.ai.answer_generator import AnswerGenerator, ClaudeNotFoundError
```

- [ ] **Step 8.2: Adicionar constante para pasta de rascunhos**

Após a linha `OUTPUT_DIR = Path(__file__).parent / "output" / "api_extraction"`, adicionar:

```python
RASCUNHOS_SUBDIR = "rascunhos"
```

- [ ] **Step 8.3: Adicionar função salvar_rascunho()**

Adicionar antes da função `menu_ponderada()`:

```python
def salvar_rascunho(turma_nome: str, pond: dict, resposta: str) -> Path:
    """Salva rascunho de resposta gerado por IA em arquivo markdown."""
    import re
    from datetime import date

    rascunhos_dir = OUTPUT_DIR / turma_nome / RASCUNHOS_SUBDIR
    rascunhos_dir.mkdir(parents=True, exist_ok=True)

    titulo_slug = re.sub(r"[^\w\s-]", "", pond["titulo"])[:40].strip().replace(" ", "_")
    filename = f"{date.today().isoformat()}_{titulo_slug}.md"
    filepath = rascunhos_dir / filename

    uuid = pond.get("student_activity_uuid", "desconhecido")
    aval = pond.get("avaliacao", {})
    conteudo = (
        f"---\n"
        f"ponderada: {pond['titulo']}\n"
        f"semana: {pond['semana']}\n"
        f"data: {pond['data_encontro']}\n"
        f"student_activity_uuid: {uuid}\n"
        f"peso: {aval.get('peso', '?')}\n"
        f"---\n\n"
        f"## Pergunta\n\n{aval.get('pergunta', '')}\n\n"
        f"## Resposta Gerada\n\n{resposta}\n"
    )
    filepath.write_text(conteudo, encoding="utf-8")
    return filepath
```

- [ ] **Step 8.4: Implementar função gerar_resposta_ia()**

Adicionar antes da função `menu_ponderada()`:

```python
async def gerar_resposta_ia(
    client: AdaLoveAPIClient,
    turma_nome: str,
    pond: dict,
    extracao_data: dict,
):
    """Fluxo completo de geração de resposta com IA para uma ponderada."""
    import os
    import subprocess as sp

    context_builder = ContextBuilder()
    prompt_loader = SystemPromptLoader()
    generator = AnswerGenerator()

    # --- Passo 1: Exibir contexto disponível ---
    aval = pond.get("avaliacao", {})
    rprint(Panel(
        f"[bold]{pond['titulo']}[/bold]\n"
        f"[dim]{pond['semana']} · {pond['data_encontro']}[/dim]\n\n"
        f"[bold cyan]Pergunta:[/bold cyan]\n{aval.get('pergunta', '')}",
        title="Contexto da Ponderada",
        border_style="cyan",
    ))

    # --- Passo 2: Transcrição (opcional) ---
    transcript_path = await questionary.text(
        f"{icons.folder} Caminho para arquivo .txt de transcrição (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()

    transcript = None
    if transcript_path and transcript_path.strip():
        try:
            transcript = Path(transcript_path.strip()).read_text(encoding="utf-8")
            rprint(f"[green]{icons.success} Transcrição carregada ({len(transcript)} chars)[/green]")
        except Exception as e:
            rprint(f"[yellow]{icons.warning} Não foi possível ler o arquivo: {e}[/yellow]")

    # --- Passo 3: Notas do usuário (opcional) ---
    user_notes = await questionary.text(
        f"{icons.document} Instruções extras ou notas (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()
    user_notes = user_notes.strip() if user_notes else None

    # --- Passo 4: System prompt ---
    rprint(f"\n[dim]System prompt padrão carregado de config/default_system_prompt.md[/dim]")
    sp_additions = await questionary.text(
        f"{icons.robot} Adicionar instruções ao system prompt desta geração (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()
    sp_additions = sp_additions.strip() if sp_additions else None
    system_prompt = prompt_loader.load(session_additions=sp_additions)

    # --- Passo 5a: Gerar esqueleto ---
    with console.status("[bold cyan]Gerando esqueleto da resposta...[/bold cyan]", spinner="dots"):
        skeleton_prompt = context_builder.build(
            pond, extracao_data, transcript=transcript,
            user_notes=user_notes, skeleton_mode=True,
        )
        try:
            skeleton = generator.generate(user_prompt=skeleton_prompt, system_prompt=system_prompt)
        except ClaudeNotFoundError:
            rprint(f"[bold red]{icons.error} claude CLI não encontrado.[/bold red]\n"
                   "Instale com: npm install -g @anthropic-ai/claude-code")
            return
        except RuntimeError as e:
            rprint(f"[bold red]{icons.error} Erro ao gerar esqueleto:[/bold red] {e}")
            return

    # --- Passo 5b: Exibir esqueleto ---
    rprint(Panel(skeleton, title="Esqueleto da Resposta", border_style="yellow"))

    # --- Passo 5c: Aprovação do esqueleto ---
    esqueleto_ok = await questionary.select(
        "O esqueleto está correto?",
        choices=[
            questionary.Choice(title=f"{icons.success} Correto — gerar resposta completa", value="ok"),
            questionary.Choice(title=f"{icons.document} Ajustar com instrução adicional", value="ajustar"),
            questionary.Choice(title=f"{icons.exit} Cancelar", value="cancelar"),
        ],
        style=MENU_STYLE,
    ).ask_async()

    if not esqueleto_ok or esqueleto_ok == "cancelar":
        rprint("[dim]Geração cancelada.[/dim]")
        return

    if esqueleto_ok == "ajustar":
        ajuste = await questionary.text(
            "Instrução adicional para corrigir o esqueleto:",
            style=MENU_STYLE,
        ).ask_async()
        if ajuste and ajuste.strip():
            user_notes = (user_notes or "") + f"\n\nCORREÇÃO DE ESQUELETO: {ajuste.strip()}"

    # --- Passo 6: Gerar resposta completa ---
    with console.status("[bold cyan]Gerando resposta completa...[/bold cyan]", spinner="dots"):
        full_prompt = context_builder.build(
            pond, extracao_data, transcript=transcript,
            user_notes=user_notes, skeleton_mode=False,
        )
        try:
            resposta = generator.generate(user_prompt=full_prompt, system_prompt=system_prompt)
        except RuntimeError as e:
            rprint(f"[bold red]{icons.error} Erro ao gerar resposta:[/bold red] {e}")
            return

    # --- Passo 7: Exibir rascunho ---
    rprint(Panel(resposta, title="Rascunho Gerado", border_style="green"))

    # --- Passo 8: Menu de ação ---
    uuid = pond.get("student_activity_uuid")
    while True:
        acao = await questionary.select(
            "O que deseja fazer com a resposta?",
            choices=[
                questionary.Choice(title=f"{icons.success} Submeter via API AdaLove", value="submeter"),
                questionary.Choice(title=f"{icons.document} Abrir no editor ($EDITOR) e submeter", value="editor"),
                questionary.Choice(title=f"{icons.download} Regenerar com nota adicional", value="regenerar"),
                questionary.Choice(title=f"{icons.folder} Salvar rascunho (sem submeter)", value="salvar"),
                questionary.Choice(title=f"{icons.exit} Cancelar", value="cancelar"),
            ],
            style=MENU_STYLE,
        ).ask_async()

        if not acao or acao == "cancelar":
            rprint("[dim]Operação cancelada.[/dim]")
            return

        if acao == "salvar":
            filepath = salvar_rascunho(turma_nome, pond, resposta)
            rprint(f"[green]{icons.success} Rascunho salvo em: [blue]{filepath}[/blue][/green]")
            return

        if acao == "editor":
            import tempfile
            editor = os.environ.get("EDITOR", "nano")
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(resposta)
                tmp_path = f.name
            sp.run([editor, tmp_path])
            resposta = Path(tmp_path).read_text(encoding="utf-8")
            Path(tmp_path).unlink(missing_ok=True)
            rprint(Panel(resposta, title="Resposta Editada", border_style="blue"))
            continuar = await questionary.confirm("Submeter esta versão editada via API?").ask_async()
            if not continuar:
                continue
            acao = "submeter"

        if acao == "regenerar":
            nota_extra = await questionary.text(
                "Instrução adicional para regenerar:",
                style=MENU_STYLE,
            ).ask_async()
            if nota_extra and nota_extra.strip():
                user_notes = (user_notes or "") + f"\n\nREGENERAÇÃO: {nota_extra.strip()}"
            with console.status("[bold cyan]Regenerando...[/bold cyan]", spinner="dots"):
                full_prompt = context_builder.build(
                    pond, extracao_data, transcript=transcript,
                    user_notes=user_notes, skeleton_mode=False,
                )
                resposta = generator.generate(user_prompt=full_prompt, system_prompt=system_prompt)
            rprint(Panel(resposta, title="Rascunho Regenerado", border_style="green"))
            continue

        if acao == "submeter":
            if not uuid:
                rprint(f"[yellow]{icons.warning} UUID da atividade não disponível. Salvando rascunho como fallback.[/yellow]")
                filepath = salvar_rascunho(turma_nome, pond, resposta)
                rprint(f"[dim]Rascunho salvo em: {filepath}[/dim]")
                return

            with console.status("[bold cyan]Submetendo via API...[/bold cyan]", spinner="dots"):
                sucesso = await client.submit_answer(uuid, resposta)

            if sucesso:
                rprint(Panel(
                    f"[bold green]{icons.success} Resposta submetida com sucesso![/bold green]",
                    title="Submissão Concluída",
                ))
                return
            else:
                rprint(f"[yellow]{icons.warning} Falha na submissão via API.[/yellow]")
                salvar = await questionary.confirm(
                    "Deseja salvar o rascunho em arquivo como alternativa?"
                ).ask_async()
                if salvar:
                    filepath = salvar_rascunho(turma_nome, pond, resposta)
                    rprint(f"[green]{icons.success} Rascunho salvo em: [blue]{filepath}[/blue][/green]")
                return
```

- [ ] **Step 8.5: Corrigir extrair_ponderadas() para propagar student_activity_uuid**

`extrair_ponderadas()` monta dicts de ponderadas mas não inclui o UUID necessário para submissão. Localizar os três blocos `ponderadas.append({...})` dentro de `extrair_ponderadas()` e adicionar o campo em cada um:

Para o bloco de encontros ponderados (primeiro `append`), adicionar:
```python
"student_activity_uuid": encontro.get("student_activity_uuid"),
```

Para o bloco de autoestudos (segundo `append`), adicionar:
```python
"student_activity_uuid": auto_data.get("student_activity_uuid"),
```

Para o bloco de sem_ancora (terceiro `append`), adicionar:
```python
"student_activity_uuid": card.get("student_activity_uuid"),
```

- [ ] **Step 8.6: Adicionar nova opção no menu_ponderada()**

Localizar a função `menu_ponderada()`. Substituir o bloco de `choices` que hoje tem apenas "Voltar":

```python
        # Menu de opções
        choices = [
            questionary.Choice(
                title=f"{icons.robot} Gerar resposta com IA",
                value="ia",
            ),
            questionary.Separator(),
            questionary.Choice(title=f"{icons.back} Voltar", value="__BACK__"),
        ]
```

- [ ] **Step 8.7: Adicionar parâmetros client e turma_nome em menu_ponderada() e tratar nova opção**

A assinatura da função precisa receber `client` e `turma_nome` para que `gerar_resposta_ia` possa ser chamada e `salvar_rascunho` saiba onde salvar. Localizar a definição:

```python
async def menu_ponderada(pond: dict):
```

Substituir por:

```python
async def menu_ponderada(
    pond: dict,
    client: AdaLoveAPIClient,
    turma_nome: str,
    extracao_data: dict,
):
```

Localizar a linha `if not selected or selected == "__BACK__":` e adicionar após o bloco de retorno:

```python
        if selected == "ia":
            await gerar_resposta_ia(client, turma_nome, pond, extracao_data)
```

- [ ] **Step 8.8: Atualizar chamadas de menu_ponderada em ver_ponderadas()**

Localizar em `ver_ponderadas()` a linha:

```python
            await menu_ponderada(ponderadas[selected])
```

Substituir por:

```python
            await menu_ponderada(ponderadas[selected], client, turma_nome, data)
```

- [ ] **Step 8.9: Verificar importação sem erros**

```bash
python -c "import sys; sys.path.insert(0, 'src'); import adalove_cli; print('OK')" 2>&1
```

Esperado: `OK` (ou warning inofensivo de credenciais).

- [ ] **Step 8.10: Rodar suite completa de testes**

```bash
pytest tests/ -v --no-cov
```

Esperado: todos os testes de `unit/ai/` passam. Os testes de `checkpoint/recovery` também devem passar agora com o `conftest.py`.

- [ ] **Step 8.11: Commit final**

```bash
git add adalove_cli.py
git commit -m "feat(cli): integrar geração de resposta com IA no menu_ponderada"
```

---

## Task 9: Verificação final

- [ ] **Step 9.1: Rodar todos os testes**

```bash
pytest tests/ -v --no-cov
```

Esperado: 0 falhas.

- [ ] **Step 9.2: Verificar imports do módulo ai completo**

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from adalove_extractor.ai import ContextBuilder, SystemPromptLoader, AnswerGenerator
from adalove_extractor.api.client import AdaLoveAPIClient
print('Todos os imports OK')
"
```

Esperado: `Todos os imports OK`.

- [ ] **Step 9.3: Verificar .env.example existe**

```bash
test -f .env.example && echo "OK" || echo "FALTA .env.example"
```

Esperado: `OK`.

- [ ] **Step 9.4: Commit de fechamento se necessário**

```bash
git status
# Se houver algo não commitado:
git add -A
git commit -m "chore: verificação final e ajustes pós-implementação"
```

---

## Notas de Implementação

### Endpoint de submissão (Task 7)
O endpoint `PUT /student-activities/{uuid}` com body `{"studyAnswer": "..."}` é a abordagem mais provável baseada no padrão REST e nos campos observados no `section_userdata`. Se a API retornar 404 ou 405, execute o script `scripts/inspect_ponderada_raw.py` e procure por endpoints de escrita nos headers das responses.

### Claude CLI flags (Task 6)
O sistema prompt é injetado no início do prompt do usuário via tags `<system>...</system>`. Caso o `claude` CLI passe a suportar uma flag `--system-prompt` nativa, atualizar o `answer_generator.py` para usá-la — ela garantiria separação mais limpa entre system e user.

### submit_answer e student_activity_uuid (Task 8)
O campo `student_activity_uuid` precisa estar presente no dict `pond`. Verificar que `extrair_ponderadas()` em `adalove_cli.py` propaga esse campo a partir dos dados da extração — ele está disponível como `student_activity_uuid` no JSON de saída.
