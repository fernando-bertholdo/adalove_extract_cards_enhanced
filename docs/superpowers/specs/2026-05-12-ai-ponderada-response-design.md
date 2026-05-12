# Spec: Geração Automática de Respostas para Ponderadas com IA

**Data:** 2026-05-12  
**Projeto:** adalove_extract_cards_enhanced  
**Status:** Aprovado pelo usuário

---

## Contexto

O projeto extrai cards da plataforma AdaLove via API e os exibe numa CLI interativa. Atividades ponderadas são avaliações que exigem resposta escrita. O objetivo deste spec é cobrir três entregas:

1. **Correção de bugs e inconsistências** no projeto atual
2. **Modernização do README**
3. **Feature:** opção "Gerar resposta com IA" no `menu_ponderada`

---

## Parte 1 — Bugs e Inconsistências

### 1.1 Tests não rodam (`ModuleNotFoundError`)

**Problema:** Os 4 arquivos em `tests/` importam `adalove_extractor` diretamente, mas o pacote está em `src/`. Sem um `conftest.py` adicionando `src/` ao `sys.path`, o pytest não encontra o módulo.

**Fix:** Criar `tests/conftest.py` com:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### 1.2 `requirements.txt` com dependências erradas

**Problema:** Lista `playwright==1.49.1` (projeto migrou para API HTTP) e não lista `httpx` (dependência real do `api/client.py`).

**Fix:** Remover `playwright`, adicionar `httpx>=0.27.0`, manter restantes.

### 1.3 `pyproject.toml` desatualizado

**Problemas:**
- Versão declarada `3.0.0` mas projeto é `2.0.0` (README + CHANGELOG)
- Lista `playwright` como dependência obrigatória

**Fix:** Sincronizar versão para `2.0.0`, substituir `playwright` por `httpx` nas dependências.

### 1.4 Arquivo `.env.example` inexistente

**Problema:** README instrui `cp .env.example .env` mas o arquivo não existe no repositório.

**Fix:** Criar `.env.example` com todas as variáveis documentadas (sem valores reais).

---

## Parte 2 — Modernização do README

O README atual mistura versões, tem seções duplicadas e carece de badges funcionais. O novo README deve:

- Badge de versão, Python, licença, e status de testes
- Seção "Quick Start" com no máximo 5 comandos
- Demonstração visual do fluxo (screenshot ou ASCII art do CLI)
- Separação clara entre instalação, configuração e uso
- Seção de arquitetura concisa com tabela de módulos
- Seção de contribuição e licença no final
- Remover referências a v1/Playwright da documentação principal (manter apenas no CHANGELOG)

---

## Parte 3 — Feature: Gerar Resposta com IA

### 3.1 Arquitetura

Novo módulo em `src/adalove_extractor/ai/`:

```
src/adalove_extractor/ai/
├── __init__.py
├── context_builder.py     # Monta prompt completo (ponderada + autoestudos + transcript + notas)
├── answer_generator.py    # Chama claude CLI como subprocess, retorna string
└── system_prompt.py       # Carrega default_system_prompt.md + adições por sessão

src/adalove_extractor/config/
└── default_system_prompt.md   # Template padrão editável pelo usuário
```

O `adalove_cli.py` chama esses módulos — sem lógica de IA no arquivo de UI.

### 3.2 Mecanismo de Geração (claude CLI como subprocess)

A geração usa o `claude` CLI instalado localmente como subprocess. Não requer `ANTHROPIC_API_KEY` separada — usa a autenticação já existente do Claude Code do usuário.

```python
import subprocess

result = subprocess.run(
    ["claude", "-p", prompt_full],
    capture_output=True,
    text=True,
    timeout=120
)
answer = result.stdout.strip()
```

**Fallback:** Se `claude` não estiver disponível no PATH, exibir mensagem clara com instrução de instalação.

### 3.3 System Prompt

**Hybrid (Opção C):**
- Template padrão em `src/adalove_extractor/config/default_system_prompt.md`
- Carregado automaticamente a cada geração
- Conteúdo padrão: instruções de estilo (escrever como aluno em aprendizado, português coloquial porém correto, sem hífens/travessões, sem clichês de LLM, resposta completa objetivando nota máxima)
- Por sessão: o CLI pergunta se o usuário quer adicionar instruções extras (texto livre, opcional)

### 3.4 Fontes de Contexto

O `context_builder.py` monta o contexto nesta ordem:

1. **Ponderada:** título, pergunta, peso, data, professor
2. **Encontro ancorado:** título do encontro de instrução, tipo, descrição
3. **Autoestudos relacionados:** todos os autoestudos vinculados ao mesmo encontro (título, descrição, conteúdos relacionados)
4. **Transcrição (opcional):** conteúdo de arquivo `.txt` fornecido pelo usuário via path
5. **Notas do usuário (opcional):** texto livre digitado pelo usuário no CLI

### 3.5 Fluxo UX Completo

```
menu_ponderada()
  └─ "🤖 Gerar resposta com IA"
        │
        ├─ 1. Exibe contexto já carregado (ponderada + autoestudos)
        │
        ├─ 2. [Pergunta] "Deseja adicionar transcrição de aula? (path do .txt)"
        │       → opcional, Enter para pular
        │
        ├─ 3. [Pergunta] "Alguma instrução ou nota extra para guiar a resposta?"
        │       → opcional, Enter para pular
        │
        ├─ 4. [Exibe] System prompt padrão carregado
        │     [Pergunta] "Quer adicionar instruções ao system prompt desta geração?"
        │       → opcional, Enter para pular
        │
        ├─ 5a. [Spinner] "Gerando esqueleto da resposta..."
        │       → claude CLI com instrução de gerar só estrutura
        │
        ├─ 5b. [Exibe] Esqueleto:
        │       - Formato detectado (ex: "entrega via link GitHub")
        │       - Tópicos principais a abordar
        │       - Instruções do professor identificadas
        │       - Fontes de contexto utilizadas
        │
        ├─ 5c. [Menu]
        │       ✅ Esqueleto correto — gerar resposta completa
        │       ✏️  Ajustar com instrução adicional (volta ao passo 3)
        │       ✖️  Cancelar
        │
        ├─ 6. [Spinner] "Gerando resposta completa..."
        │       → claude CLI com contexto completo + esqueleto aprovado
        │
        ├─ 7. [Exibe] Rascunho completo formatado com Rich
        │
        └─ 8. [Menu]
                ✅ Submeter via API AdaLove
                ✏️  Abrir no $EDITOR para ajustar e submeter
                🔄 Regenerar com nota adicional
                💾 Salvar rascunho em arquivo (sem submeter)
                ✖️  Cancelar
```

### 3.6 Submissão via API

A submissão usa o endpoint de atualização de `studyAnswer` já descoberto na API AdaLove (mesmo padrão de `atualizar_status_ponderadas`). Será implementada como método `submit_answer(student_activity_uuid, answer_text)` no `AdaLoveAPIClient`.

**Fallback:** Se a submissão falhar (rede, endpoint não encontrado, etc.), salvar o rascunho em `output/api_extraction/{turma}/rascunhos/{uuid}.md` e exibir instrução de entrega manual.

### 3.7 Salvamento de Rascunho

Rascunhos salvos em:
```
output/api_extraction/{turma}/rascunhos/{data}_{titulo_slug}.md
```

Formato: markdown com frontmatter (ponderada, data, contexto utilizado) + resposta gerada.

---

## Restrições e Decisões

| Decisão | Escolha | Razão |
|---------|---------|-------|
| Motor de IA | `claude` CLI como subprocess | Usa autenticação existente, sem custo extra de API |
| System prompt | Hybrid: template padrão + adições por sessão | Flexibilidade sem repetição |
| Review da geração | Skeleton → aprovação → resposta final | Detecta erros de contexto antes de gastar tokens |
| Submissão | API com fallback manual | Conveniência máxima sem bloquear o fluxo |
| Novos módulos | `src/adalove_extractor/ai/` | Segue padrão modular existente do projeto |

---

## Ordem de Implementação

1. Bugs + inconsistências (conftest, requirements, pyproject, .env.example)
2. README modernizado
3. Módulo `ai/` (context_builder → system_prompt → answer_generator)
4. Método de submissão no `AdaLoveAPIClient`
5. Integração no `adalove_cli.py` (menu_ponderada → nova opção)
6. `default_system_prompt.md` com conteúdo padrão
