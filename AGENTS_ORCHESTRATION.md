# 🤖 Orquestração de Background Agents - Desenvolvimento Paralelo

## 🎯 Estratégia de Paralelização

**Objetivo**: Maximizar paralelismo minimizando conflitos e dependências.

**Resultado esperado**: Reduzir tempo de desenvolvimento de ~12-16 semanas para ~6-8 semanas.

---

## 📊 Análise de Dependências

```
v3.0.0 (Arquitetura Modular) ← BASE BLOQUEANTE
    ↓
    ├─→ v3.1.0 (Pipeline Resiliente)     ← Depende de io/, models/
    ├─→ v3.2.0 (CLI)                     ← Depende de estrutura geral
    └─→ Sub-módulos v3.0.0 podem ser paralelos internamente
         ↓
v3.3.0 (Seletiva) ← Depende de v3.2.0 (CLI)
```

---

## 🚀 Estratégia Recomendada: 2 Fases

### 📍 FASE 1: Modularização (Paralela)

**4 Agents trabalhando simultaneamente em v3.0.0**

- 🤖 **Agent A**: Core (models, config)
- 🤖 **Agent B**: Extractors (browser, extractors)
- 🤖 **Agent C**: Enrichment (enrichment, utils)
- 🤖 **Agent D**: IO & CLI básico (io, cli skeleton)

**Tempo estimado**: 2-3 semanas (paralelo) vs 6-8 semanas (sequencial)

### 📍 FASE 2: Features Avançadas (Paralela)

**2 Agents trabalhando após FASE 1**

- 🤖 **Agent E**: v3.1.0 (Checkpoints) + v3.3.0 parte 1
- 🤖 **Agent F**: v3.2.0 (CLI completa) + v3.3.0 parte 2

**Tempo estimado**: 3-4 semanas (paralelo) vs 6-8 semanas (sequencial)

---

## 🤖 FASE 1: Divisão de v3.0.0

### Agent A: Core & Models (FUNDAÇÃO)

**Prioridade**: 🔴 Crítica (outros dependem)

**Responsabilidades**:
```python
adalove_extractor/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── card.py          # Card (dataclass/Pydantic)
│   └── enriched_card.py # EnrichedCard
└── config/
    ├── __init__.py
    ├── settings.py      # Pydantic Settings
    └── logging.py       # Config centralizada
```

**Tarefas**:
- [ ] Criar estrutura de pacote base
- [ ] Definir modelos `Card` e `EnrichedCard` com Pydantic
- [ ] Implementar `Settings` com Pydantic Settings
- [ ] Configurar logging centralizado
- [ ] Criar `pyproject.toml` ou `setup.py`

**Arquivos do código atual a extrair**:
- Linhas 1-50: Imports e configurações → `config/settings.py`
- Linhas 700-800: Definições implícitas de Card → `models/card.py`

**Tempo estimado**: 3-5 dias

**Bloqueador**: Nenhum (pode começar imediatamente)

---

### Agent B: Extractors (NAVEGAÇÃO & EXTRAÇÃO)

**Prioridade**: 🟡 Alta (depende de Agent A para models)

**Responsabilidades**:
```python
adalove_extractor/
├── browser/
│   ├── __init__.py
│   ├── auth.py         # Autenticação
│   └── navigator.py    # Navegação Kanban
└── extractors/
    ├── __init__.py
    ├── week.py         # Extração por semana
    └── card.py         # Extração de card individual
```

**Tarefas**:
- [ ] Extrair lógica de login → `browser/auth.py`
- [ ] Extrair navegação Kanban → `browser/navigator.py`
- [ ] Modularizar extração de semanas → `extractors/week.py`
- [ ] Modularizar extração de cards → `extractors/card.py`
- [ ] Integrar com models de Agent A

**Arquivos do código atual a extrair**:
- Linhas 51-300: Login e navegação → `browser/`
- Linhas 301-500: Extração de cards → `extractors/`

**Tempo estimado**: 5-7 dias

**Aguarda**: Agent A completar models (dia 3-5)

---

### Agent C: Enrichment (PROCESSAMENTO)

**Prioridade**: 🟡 Alta (depende de Agent A para models)

**Responsabilidades**:
```python
adalove_extractor/
├── enrichment/
│   ├── __init__.py
│   ├── normalizer.py   # Normalização de dados
│   ├── anchor.py       # Ancoragem de autoestudos
│   └── classifier.py   # Classificação de cards
└── utils/
    ├── __init__.py
    ├── hash.py         # Geração de hashes
    └── text.py         # Manipulação de texto
```

**Tarefas**:
- [ ] Extrair normalização de datas → `enrichment/normalizer.py`
- [ ] Extrair sistema de ancoragem → `enrichment/anchor.py`
- [ ] Extrair classificação → `enrichment/classifier.py`
- [ ] Extrair utilitários → `utils/`
- [ ] ⚠️ **PRESERVAR** lógica de ancoragem existente

**Arquivos do código atual a extrair**:
- Linhas 501-900: Sistema de enriquecimento → `enrichment/`
- Funções auxiliares → `utils/`

**Tempo estimado**: 5-7 dias

**Aguarda**: Agent A completar models (dia 3-5)

---

### Agent D: IO & CLI Skeleton (INTERFACES)

**Prioridade**: 🟢 Média (pode começar em paralelo)

**Responsabilidades**:
```python
adalove_extractor/
├── io/
│   ├── __init__.py
│   ├── writers.py      # CSV/JSONL/Parquet writers
│   └── readers.py      # Leitura de dados (futuro)
└── cli/
    ├── __init__.py
    ├── main.py         # Entry point básico
    └── commands.py     # Esqueleto de comandos
```

**Tarefas**:
- [ ] Criar writers para CSV → `io/writers.py`
- [ ] Criar writer para JSONL → `io/writers.py`
- [ ] Setup Typer básico → `cli/main.py`
- [ ] Criar comando `extract` skeleton → `cli/commands.py`
- [ ] Configurar entry point no `pyproject.toml`

**Arquivos do código atual a extrair**:
- Linhas 901-1018: Salvamento de dados → `io/writers.py`
- Script de execução → `cli/main.py`

**Tempo estimado**: 4-6 dias

**Aguarda**: Agent A completar models (dia 3-5, parcial)

---

## 🔄 FASE 1: Ponto de Sincronização

**Após todos Agents A-D completarem**:

### Integration Sprint (2-3 dias)
- [ ] Integrar todos os módulos
- [ ] Resolver conflitos de imports
- [ ] Testar fluxo completo end-to-end
- [ ] Ajustar interfaces entre módulos
- [ ] Executar testes de regressão
- [ ] Validar: output idêntico ao v2.0.0

### Critério de Sucesso FASE 1:
```bash
# Deve funcionar igual ao v2.0.0
adalove extract --turma modulo6
# Output: mesmos 3 arquivos, dados idênticos
```

---

## 🚀 FASE 2: Features Avançadas (Paralela)

### Agent E: Resilience & Selective Part 1

**Responsabilidades**:
- ✅ v3.1.0 completa (Pipeline Resiliente)
- ✅ v3.3.0 parte 1 (Parser de semanas)

**Tarefas v3.1.0**:
- [ ] Implementar `io/checkpoint.py`
- [ ] Sistema de escrita incremental
- [ ] Idempotência com record_hash
- [ ] Cache de hashes processados

**Tarefas v3.3.0 (parte 1)**:
- [ ] Parser de expressões de semanas
- [ ] Validação de semanas
- [ ] Lógica de skip no extractor

**Tempo estimado**: 3-4 semanas

**Dependências**: FASE 1 completa

---

### Agent F: CLI & Selective Part 2

**Responsabilidades**:
- ✅ v3.2.0 completa (CLI Completa)
- ✅ v3.3.0 parte 2 (Filtro de frentes)

**Tarefas v3.2.0**:
- [ ] Expandir CLI com todos os argumentos
- [ ] Implementar leitura de `adalove.toml`
- [ ] Adicionar flags: `--headless`, `--no-interactive`, `--resume`
- [ ] Help messages completos

**Tarefas v3.3.0 (parte 2)**:
- [ ] Detecção de frente (professor, keywords)
- [ ] Filtro de cards por frente
- [ ] Flag `--frentes`

**Tempo estimado**: 3-4 semanas

**Dependências**: FASE 1 completa

---

## 🔄 FASE 2: Ponto de Sincronização Final

**Após Agents E e F completarem**:

### Final Integration (1-2 dias)
- [ ] Integrar checkpoints com CLI
- [ ] Integrar seletiva (semanas + frentes)
- [ ] Testes end-to-end completos
- [ ] Validar todos cenários de uso

### Critério de Sucesso FASE 2:
```bash
# Todos comandos funcionais
adalove extract --turma modulo6 --weeks 1-5 --frentes "Programação"
adalove extract --turma modulo7 --headless --no-interactive
adalove extract --resume
```

---

## 📋 Timeline Consolidado

### Sequencial (1 pessoa)
```
v3.0.0: ████████ 6-8 semanas
v3.1.0: ████ 3-4 semanas
v3.2.0: ████ 3-4 semanas
v3.3.0: ██ 2-3 semanas
Total: 14-19 semanas (~4-5 meses)
```

### Paralelo (6 agents)
```
FASE 1 (A+B+C+D): ███ 3 semanas (paralelo)
Integration:       █ 0.5 semana
FASE 2 (E+F):     ████ 4 semanas (paralelo)
Integration:       █ 0.5 semana
Total: 8 semanas (~2 meses)
```

**Economia**: ~60% de tempo! 🚀

---

## ⚠️ Gestão de Conflitos

### Estratégia de Branches

```bash
# Cada agent trabalha em sua branch
main
  ├─ feature/v3.0.0-agent-a-core
  ├─ feature/v3.0.0-agent-b-extractors
  ├─ feature/v3.0.0-agent-c-enrichment
  └─ feature/v3.0.0-agent-d-io

# Merge sequencial após cada agent completar
# Resolver conflitos incrementalmente
```

### Arquivos Propensos a Conflito

| Arquivo | Agents | Estratégia |
|---------|--------|------------|
| `__init__.py` (raiz) | A, B, C, D | Agent A cria primeiro |
| `pyproject.toml` | A, D | Agent A cria, D adiciona entry points |
| `README.md` | Todos | Editar em branches separadas, merge cuidadoso |

### Comunicação entre Agents

**Não há comunicação direta**, mas cada agent deve:
1. ✅ Documentar interfaces públicas (docstrings)
2. ✅ Criar stubs para dependências não implementadas
3. ✅ Fazer commits frequentes (integração contínua)

---

## 🎯 Divisão de Responsabilidades

### Por Complexidade

| Agent | Complexidade | Dependências | Pode Começar |
|-------|--------------|--------------|--------------|
| **A** | 🟢 Baixa | Nenhuma | ✅ Imediato |
| **B** | 🟡 Média | Agent A (models) | Dia 3-5 |
| **C** | 🔴 Alta | Agent A (models) | Dia 3-5 |
| **D** | 🟢 Baixa | Agent A (parcial) | Dia 2-3 |
| **E** | 🟡 Média | FASE 1 completa | Semana 4 |
| **F** | 🟡 Média | FASE 1 completa | Semana 4 |

### Por Risco

| Agent | Risco de Quebrar | Mitigação |
|-------|------------------|-----------|
| **A** | Baixo | Modelos são novos |
| **B** | Médio | Testar navegação Playwright |
| **C** | 🔴 Alto | **Preservar ancoragem!** Testes de regressão |
| **D** | Baixo | Writers são independentes |
| **E** | Médio | Checkpoints não afetam lógica |
| **F** | Baixo | CLI é wrapper |

---

## 📦 Dependências entre Agents

### FASE 1

```
Agent A (Core)
  ↓ models, config
  ├─→ Agent B (usa models)
  ├─→ Agent C (usa models)
  └─→ Agent D (usa models parcialmente)

Agent B, C, D → trabalham em paralelo após A
```

### FASE 2

```
FASE 1 Completa
  ↓
  ├─→ Agent E (usa io/, models/)
  └─→ Agent F (usa cli skeleton de Agent D)

Agent E, F → trabalham em paralelo
```

---

## 🛠️ Ferramentas e Coordenação

### Tracking de Progresso

**GitHub Projects Board**:
```
📋 Backlog
├─ [Agent A] Criar models
├─ [Agent B] Extrair navegação
├─ [Agent C] Modularizar enrichment
└─ [Agent D] Criar writers

🔄 In Progress (até 4 simultâneos)
├─ [Agent A] Implementing Card model
├─ [Agent B] Waiting for Agent A
├─ [Agent C] Waiting for Agent A
└─ [Agent D] Creating CSV writer

✅ Done
└─ [Agent A] Package structure created
```

### Daily Sync (Assíncrono)

**Cada agent atualiza diariamente**:
```markdown
## Agent A - Day 3
✅ Completado:
- Card model with Pydantic
- Settings class

🔄 Em andamento:
- EnrichedCard model (70%)

⏭️ Próximo:
- Logging config

🚧 Bloqueadores:
- Nenhum
```

---

## 🎮 Como Executar (Prático)

### Setup Inicial

```bash
# 1. Criar branches para cada agent
git checkout -b feature/v3.0.0-agent-a-core
git push -u origin feature/v3.0.0-agent-a-core

git checkout main
git checkout -b feature/v3.0.0-agent-b-extractors
git push -u origin feature/v3.0.0-agent-b-extractors

# ... repetir para C e D
```

### Iniciar Agents (Cursor)

**Terminal 1 - Agent A**:
```bash
cursor-agent --prompt-file=PROMPT_AGENT_A.md --branch=feature/v3.0.0-agent-a-core
```

**Terminal 2 - Agent B** (aguardar Agent A dia 3-5):
```bash
cursor-agent --prompt-file=PROMPT_AGENT_B.md --branch=feature/v3.0.0-agent-b-extractors
```

**Terminal 3 - Agent C** (aguardar Agent A dia 3-5):
```bash
cursor-agent --prompt-file=PROMPT_AGENT_C.md --branch=feature/v3.0.0-agent-c-enrichment
```

**Terminal 4 - Agent D**:
```bash
cursor-agent --prompt-file=PROMPT_AGENT_D.md --branch=feature/v3.0.0-agent-d-io
```

### Integração Incremental

```bash
# Conforme cada agent completa
git checkout main
git merge feature/v3.0.0-agent-a-core    # Primeiro
git merge feature/v3.0.0-agent-d-io      # Segundo
git merge feature/v3.0.0-agent-b-extractors  # Terceiro
git merge feature/v3.0.0-agent-c-enrichment  # Último (mais crítico)

# Resolver conflitos manualmente
# Testar integração
pytest tests/ -v
```

---

## 📊 Métricas de Sucesso

### Por Agent

| Agent | LoC | Modules | Tests | Coverage |
|-------|-----|---------|-------|----------|
| A | ~200 | 4 | 20+ | >80% |
| B | ~300 | 4 | 15+ | >70% |
| C | ~400 | 5 | 30+ | >85% (crítico!) |
| D | ~200 | 3 | 10+ | >60% |

### Global (FASE 1)

- [ ] Todos agents completaram suas tarefas
- [ ] Integração funcionando sem erros
- [ ] Output idêntico ao v2.0.0
- [ ] Testes passando (>70% cobertura total)
- [ ] Documentação atualizada

---

## 🚨 Pontos de Atenção

### ⚠️ Riscos

1. **Agent C (Enrichment)**: Maior risco de quebrar lógica
   - **Mitigação**: Testes de regressão antes/depois
   - **Validação**: Comparar output v2.0.0 vs v3.0.0

2. **Conflitos de merge**: Múltiplos agents editando estrutura
   - **Mitigação**: Merge incremental (A → D → B → C)
   - **Validação**: Testar após cada merge

3. **Dependências não sincronizadas**: Agent B espera Agent A
   - **Mitigação**: Stubs temporários
   - **Validação**: Daily sync de progresso

### ✅ Boas Práticas

1. **Commits atômicos**: Cada agent commita frequentemente
2. **Testes primeiro**: TDD onde possível
3. **Documentação inline**: Docstrings imediatas
4. **Integração contínua**: Merge assim que agent completa

---

## 📞 Próximos Passos

1. **Revisar estratégia**: Concordar com divisão
2. **Criar prompts individuais**: Um por agent (A, B, C, D, E, F)
3. **Setup branches**: Criar branches para cada agent
4. **Iniciar FASE 1**: Disparar 4 agents simultaneamente
5. **Monitor progress**: Daily sync assíncrono
6. **Integration sprint**: Após todos completarem
7. **Iniciar FASE 2**: Agents E e F
8. **Final integration**: v3.0-v3.3 completas

---

**Economia de tempo esperada: ~60%** (4 meses → 2 meses) 🚀

**Próximo arquivo a criar**: Prompts individuais para cada agent (PROMPT_AGENT_A.md, B, C, D, E, F)

