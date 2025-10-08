# 🗺️ Roadmap - Adalove Extract Cards Enhanced

Este documento descreve a visão de longo prazo para o desenvolvimento do projeto, organizando features planejadas por versões futuras e prioridades.

---

## 📋 Índice

- [Princípios de Desenvolvimento](#-princípios-de-desenvolvimento)
- [Visão Geral de Versões](#-visão-geral-de-versões)
- [v3.0.0 - Arquitetura Modular](#v300---arquitetura-modular-planejado)
- [v3.1.0 - Pipeline Resiliente](#v310---pipeline-resiliente-planejado)
- [v3.2.0 - Configuração e Modos de Execução](#v320---configuração-e-modos-de-execução-planejado)
- [v3.3.0 - Extração Seletiva](#v330---extração-seletiva-planejado)
- [v3.4.0 - Interface Gráfica (GUI)](#v340---interface-gráfica-gui-planejado)
- [v4.0.0 - Qualidade e Garantias](#v400---qualidade-e-garantias-planejado)
- [v4.1.0 - Observabilidade](#v410---observabilidade-planejado)
- [v4.2.0 - Extensibilidade](#v420---extensibilidade-planejado)
- [Features em Backlog](#-features-em-backlog)
- [Como Contribuir](#-como-contribuir)

---

## 🎯 Princípios de Desenvolvimento

> **Compromisso**: Nunca comprometer a qualidade da documentação em favor de velocidade de desenvolvimento.

### Para cada nova implementação, considerar:
1. **Arquitetura**: Como isso se encaixa na arquitetura atual?
2. **Garantias**: Quais garantias preciso estabelecer para que minhas implementações não quebrem o projeto?
3. **Testes**: Quais testes serão necessários no futuro para garantir o funcionamento de novas features?

---

## 📅 Visão Geral de Versões

| Versão | Status | Tema Principal | ETA |
|--------|--------|----------------|-----|
| **v2.0.0** | ✅ Released | Sistema de Enriquecimento Inteligente | 2025-10-08 |
| **v3.0.0** | 📋 Planned | Arquitetura Modular | Q3 2025 |
| **v3.1.0** | 📋 Planned | Pipeline Resiliente | Q3 2025 |
| **v3.2.0** | 📋 Planned | Configuração e CLI | Q4 2025 |
| **v3.3.0** | 📋 Planned | Extração Seletiva | Q4 2025 |
| **v3.4.0** | 📋 Planned | Interface Gráfica (GUI) | Q1 2026 |
| **v4.0.0** | 🔮 Future | Qualidade e Garantias | Q1 2026 |
| **v4.1.0** | 🔮 Future | Observabilidade | Q2 2026 |
| **v4.2.0** | 🔮 Future | Extensibilidade | Q2 2026 |

---

## [v3.0.0] - Arquitetura Modular (Planejado)

### 🎯 Objetivo
Transformar o script monolítico em um pacote Python profissional com camadas bem definidas, aumentando testabilidade, reuso e clareza de dependências.

### 📦 Features

#### 1. Estrutura de Pacote Python
**Prioridade**: 🔴 Alta

```
adalove_extractor/
├── __init__.py
├── cli/                    # Interface de linha de comando
│   ├── __init__.py
│   ├── main.py            # Entry point (Typer/Click)
│   └── commands.py        # Comandos CLI
├── config/                 # Configuração centralizada
│   ├── __init__.py
│   ├── settings.py        # Pydantic Settings
│   └── logging.py         # Config de logs
├── browser/               # Automação do navegador
│   ├── __init__.py
│   ├── auth.py           # Autenticação
│   └── navigator.py      # Navegação no Kanban
├── extractors/            # Extração de dados
│   ├── __init__.py
│   ├── week.py           # Extração por semana
│   └── card.py           # Extração de cards
├── enrichment/            # Enriquecimento puro
│   ├── __init__.py
│   ├── normalizer.py     # Normalização de dados
│   ├── anchor.py         # Ancoragem de autoestudos
│   └── classifier.py     # Classificação de cards
├── io/                    # Input/Output
│   ├── __init__.py
│   ├── writers.py        # CSV/JSONL/Parquet
│   └── checkpoint.py     # Persistência de estado
├── models/                # Modelos de dados
│   ├── __init__.py
│   ├── card.py           # Card (dataclass/Pydantic)
│   └── enriched_card.py  # EnrichedCard
└── utils/                 # Utilitários
    ├── __init__.py
    ├── hash.py           # Geração de hashes
    └── text.py           # Manipulação de texto
```

**Benefícios**:
- ✅ Testabilidade (cada módulo isolado)
- ✅ Reuso de componentes
- ✅ Clareza de dependências
- ✅ Melhor documentação
- ✅ Facilita contribuições

**Issues Relacionadas**: TBD

---

## [v3.1.0] - Pipeline Resiliente (Planejado)

### 🎯 Objetivo
Implementar pipeline robusto com streaming, checkpoints e idempotência para execuções mais seguras e eficientes.

### 📦 Features

#### 1. Processamento Streaming
**Prioridade**: 🔴 Alta

- **Descrição**: Produzir `Card` como iterável/async generator
- **Implementação**:
  ```python
  async def extract_cards() -> AsyncIterator[Card]:
      for week in weeks:
          for card in week.cards:
              yield card
  ```
- **Benefícios**: Menor uso de memória, processamento incremental

#### 2. Sistema de Checkpoints
**Prioridade**: 🔴 Alta

- **Descrição**: Salvar estado durante execução para retomada
- **Implementação**:
  - Arquivo `.checkpoint.json` em `dados_extraidos/turma/`
  - Rastrear: última semana processada, último card, timestamp
  - Comando: `--resume` para retomar execução
- **Estrutura do Checkpoint**:
  ```json
  {
    "turma": "modulo6",
    "execution_id": "20250826_220413",
    "last_completed_week": 7,
    "last_completed_card_id": "card_123",
    "total_cards_extracted": 89,
    "timestamp": "2025-08-26T22:04:13Z",
    "status": "interrupted"
  }
  ```

#### 3. Idempotência com Record Hash
**Prioridade**: 🟡 Média

- **Descrição**: Usar `record_hash` como chave idempotente
- **Implementação**:
  - Manter mapa persistente de hashes processados
  - Skip de cards já extraídos em execuções anteriores
  - Opção: `--force-reextract` para ignorar cache

#### 4. Escrita Incremental
**Prioridade**: 🟡 Média

- **Descrição**: Escrever cards conforme são extraídos (não apenas no final)
- **Formato**: JSONL (append-only), CSV incremental
- **Benefícios**: Dados parciais salvos mesmo em caso de falha

**Issues Relacionadas**: TBD

---

## [v3.2.0] - Configuração e Modos de Execução (Planejado)

### 🎯 Objetivo
Adicionar interface CLI profissional com argumentos, flags e múltiplos modos de execução para automação.

### 📦 Features

#### 1. Interface CLI Completa
**Prioridade**: 🔴 Alta

**Framework**: Typer (recomendado) ou Click

**Comandos propostos**:
```bash
# Extração completa (interativo)
adalove extract --turma modulo6

# Modo headless (sem interface gráfica)
adalove extract --turma modulo7 --headless

# Modo não-interativo (CI/CD)
adalove extract --turma modulo8 --no-interactive --output dados/

# Retomar execução
adalove extract --resume

# Extração seletiva (ver v3.3.0)
adalove extract --turma modulo6 --weeks 1,2,3
adalove extract --turma modulo6 --frentes "Programação,Matemática"
```

#### 2. Configuração via Arquivo
**Prioridade**: 🟡 Média

**Formato**: `adalove.toml` ou `pyproject.toml`

```toml
[adalove]
default_output_dir = "dados_extraidos"
headless = false
interactive = true
log_level = "INFO"

[adalove.extraction]
max_retries = 3
timeout_seconds = 30
parallel_weeks = false

[adalove.enrichment]
enable_anchoring = true
anchor_confidence_threshold = 0.6
```

#### 3. Argumentos Suportados
**Prioridade**: 🔴 Alta

| Argumento | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `--turma` | str | Nome da turma | `--turma modulo6` |
| `--headless` | flag | Navegador sem interface | `--headless` |
| `--no-interactive` | flag | Sem interação do usuário | `--no-interactive` |
| `--weeks` | str | Semanas específicas | `--weeks 1,2,5-8` |
| `--frentes` | str | Frentes específicas | `--frentes "Prog,Mat"` |
| `--output` | path | Diretório de saída | `--output ./data` |
| `--format` | choice | Formato de saída | `--format jsonl` |
| `--resume` | flag | Retomar execução | `--resume` |
| `--log-level` | choice | Nível de log | `--log-level DEBUG` |

#### 4. Integração com Agendadores
**Prioridade**: 🟢 Baixa

- **Descrição**: Execução automatizada via cron/Task Scheduler
- **Exemplo cron**:
  ```bash
  # Extração diária às 2h da manhã
  0 2 * * * cd /path/to/project && adalove extract --turma modulo6 --headless --no-interactive
  ```

**Issues Relacionadas**: TBD

---

## [v3.3.0] - Extração Seletiva (Planejado)

### 🎯 Objetivo
Permitir extração granular por semanas específicas, sequências de semanas, ou frentes temáticas específicas.

### 📦 Features

#### 1. Extração de Semanas Específicas
**Prioridade**: 🔴 Alta

**Casos de uso**:
```bash
# Semana única
adalove extract --turma modulo6 --weeks 5

# Múltiplas semanas
adalove extract --turma modulo6 --weeks 1,3,7

# Intervalo (range)
adalove extract --turma modulo6 --weeks 1-5

# Combinação
adalove extract --turma modulo6 --weeks 1-3,7,9-10
```

**Implementação**:
- Parser de expressões de semanas
- Validação de semanas existentes
- Skip inteligente de semanas não solicitadas

#### 2. Extração de Frentes Específicas
**Prioridade**: 🟡 Média

**Casos de uso**:
```bash
# Frente única
adalove extract --turma modulo6 --frentes "Programação"

# Múltiplas frentes
adalove extract --turma modulo6 --frentes "Programação,Matemática"

# Todas exceto uma
adalove extract --turma modulo6 --exclude-frentes "Liderança"
```

**Desafio**: Necessário detectar frente do card (título, professor, tags?)

#### 3. Filtros Combinados
**Prioridade**: 🟢 Baixa

```bash
# Semanas específicas + frentes específicas
adalove extract --turma modulo6 --weeks 1-5 --frentes "Programação"

# Apenas autoestudos
adalove extract --turma modulo6 --only-autostudy

# Apenas atividades ponderadas
adalove extract --turma modulo6 --only-graded
```

#### 4. Detecção Automática de Frentes
**Prioridade**: 🟡 Média

**Estratégias**:
1. Análise de título do card (keywords)
2. Detecção de professor (mapping professor → frente)
3. Tags/categorias se disponíveis no HTML
4. Machine Learning (classificador treinado)

**Mapeamento professor → frente** (exemplo):
```python
PROFESSOR_FRENTE_MAP = {
    "Afonso": "Programação",
    "Fellipe": "Matemática",
    "Bruna": "UX",
    "Sergio": "Negócios",
    # ...
}
```

**Issues Relacionadas**: TBD

---

## [v3.4.0] - Interface Gráfica (GUI) (Planejado)

### 🎯 Objetivo
Criar interface gráfica intuitiva para usuários não-técnicos, permitindo configuração visual de todas as opções de extração e salvamento de perfis de configuração.

### 📦 Features

#### 1. Interface Principal
**Prioridade**: 🟡 Média

**Opções de Tecnologia**:

| Framework | Prós | Contras | Recomendação |
|-----------|------|---------|--------------|
| **Tkinter** | ✅ Nativo Python<br>✅ Zero dependências<br>✅ Cross-platform | ⚠️ Visual datado<br>⚠️ Menos moderno | ⭐⭐⭐ Boa para MVP |
| **PyQt6/PySide6** | ✅ Visual profissional<br>✅ Muito completo<br>✅ Qt Designer | ⚠️ Licença complexa<br>⚠️ Dependência pesada | ⭐⭐⭐⭐ Melhor UX |
| **Streamlit** | ✅ Muito rápido desenvolver<br>✅ Visual moderno<br>✅ Web-based | ⚠️ Requer servidor<br>⚠️ Menos controle | ⭐⭐⭐ Alternativa web |
| **Dear PyGui** | ✅ Performance alta<br>✅ Visual moderno | ⚠️ Menos maduro<br>⚠️ Comunidade menor | ⭐⭐ Experimental |
| **Flet** | ✅ Modern UI<br>✅ Flutter-based<br>✅ Cross-platform | ⚠️ Relativamente novo<br>⚠️ Docs limitadas | ⭐⭐⭐ Promissor |

**Recomendação inicial**: **Tkinter** (MVP) → **PyQt6** (versão final)

**Layout proposto**:
```
┌────────────────────────────────────────────────┐
│  Adalove Extractor - Configuração             │
├────────────────────────────────────────────────┤
│                                                │
│  📁 Turma                                      │
│  ┌──────────────────────────────────────────┐ │
│  │ modulo6                            [...]│ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  📅 Semanas (opcional)                         │
│  ☐ Todas  ☑ Específicas:                      │
│  ┌──────────────────────────────────────────┐ │
│  │ 1-5, 7, 9-10                             │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  🎯 Frentes (opcional)                         │
│  ☑ Todas  ☐ Específicas:                      │
│  ☐ Programação  ☐ Matemática  ☐ UX           │
│  ☐ Negócios     ☐ Liderança                  │
│                                                │
│  ⚙️ Opções Avançadas                           │
│  ☑ Modo headless                               │
│  ☐ Não-interativo                              │
│  ☐ Retomar execução anterior                  │
│                                                │
│  📂 Saída: [dados_extraidos/modulo6/]  [...]  │
│                                                │
│  💾 Perfil: [Padrão ▼]  [Salvar] [Carregar]  │
│                                                │
│  ┌──────────┐  ┌──────────┐                   │
│  │ Executar │  │ Cancelar │                   │
│  └──────────┘  └──────────┘                   │
│                                                │
└────────────────────────────────────────────────┘
```

#### 2. Janela de Progresso
**Prioridade**: 🔴 Alta

**Features**:
- Barra de progresso por semana
- Log em tempo real (scrollable)
- Estatísticas atualizadas (cards extraídos, tempo decorrido)
- Botão de cancelamento (graceful stop)

```
┌────────────────────────────────────────────────┐
│  Extração em Progresso - modulo6              │
├────────────────────────────────────────────────┤
│                                                │
│  Semana 07/10                                  │
│  ████████████████░░░░░░░░░░  70%              │
│                                                │
│  Cards extraídos: 89/127                       │
│  Tempo decorrido: 05:23                        │
│  Tempo estimado: 01:52                         │
│                                                │
│  📋 Log:                                       │
│  ┌──────────────────────────────────────────┐ │
│  │ [14:32:15] Semana 07 iniciada           │ │
│  │ [14:32:18] Card "Autoestudo Python"...  │ │
│  │ [14:32:21] Ancoragem: high confidence   │ │
│  │ ▼                                        │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ┌──────────┐  ┌──────────┐                   │
│  │ Cancelar │  │ Pausar   │                   │
│  └──────────┘  └──────────┘                   │
│                                                │
└────────────────────────────────────────────────┘
```

#### 3. Sistema de Perfis
**Prioridade**: 🟡 Média

**Descrição**: Salvar e carregar configurações para reutilização

**Arquivo de perfil** (`~/.adalove/profiles.json`):
```json
{
  "profiles": {
    "Padrão": {
      "turma": "",
      "weeks": null,
      "frentes": null,
      "headless": true,
      "interactive": true,
      "output_dir": "dados_extraidos"
    },
    "Modulo6 Completo": {
      "turma": "modulo6",
      "weeks": null,
      "frentes": null,
      "headless": true,
      "interactive": false,
      "output_dir": "dados_extraidos/modulo6"
    },
    "Apenas Programação": {
      "turma": "",
      "weeks": null,
      "frentes": ["Programação"],
      "headless": true,
      "interactive": true,
      "output_dir": "dados_extraidos"
    }
  },
  "last_used": "Modulo6 Completo"
}
```

**Operações**:
- Salvar perfil atual
- Carregar perfil existente
- Deletar perfil
- Exportar/importar perfis (para compartilhar)

#### 4. Validação e Feedback
**Prioridade**: 🔴 Alta

**Validações em tempo real**:
- Formato de semanas válido (`1,3,7` ou `1-5`)
- Diretório de saída acessível
- Credenciais configuradas (.env existe)
- Playwright instalado

**Feedback visual**:
```
✅ Credenciais configuradas
⚠️  Playwright não instalado (executar: playwright install chromium)
❌ Formato de semanas inválido (use: 1,3,7 ou 1-5)
```

#### 5. Integração com CLI
**Prioridade**: 🟡 Média

**Descrição**: GUI gera e executa comando CLI internamente

**Exemplo**:
```python
# GUI constrói comando baseado nas opções
command = [
    "adalove", "extract",
    "--turma", "modulo6",
    "--weeks", "1-5,7",
    "--frentes", "Programação,Matemática",
    "--headless",
    "--output", "dados_extraidos/modulo6"
]

# Executa em subprocess com streaming de output
process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Atualiza GUI com output em tempo real
for line in process.stdout:
    log_widget.append(line)
    update_progress(line)
```

**Benefícios**:
- Reuso total da lógica CLI
- Fácil debug (mostra comando equivalente)
- Consistência entre CLI e GUI

---

### 🎨 Experiência do Usuário

#### Fluxo Típico:

```
1. Abrir GUI
   ↓
2. Carregar perfil salvo (opcional)
   ↓
3. Configurar opções visualmente
   ↓
4. [Salvar perfil] (opcional)
   ↓
5. [Executar]
   ↓
6. Acompanhar progresso em tempo real
   ↓
7. Ver relatório final
   ↓
8. [Abrir pasta de saída] (botão)
```

#### Atalhos:

- `Ctrl+S` - Salvar perfil
- `Ctrl+L` - Carregar perfil
- `Ctrl+Enter` - Executar
- `Esc` - Cancelar

---

### 🏗️ Arquitetura Proposta

```
adalove_extractor/
├── gui/                        # Novo módulo GUI
│   ├── __init__.py
│   ├── main_window.py         # Janela principal
│   ├── progress_window.py     # Janela de progresso
│   ├── widgets/               # Componentes reutilizáveis
│   │   ├── week_selector.py
│   │   ├── frente_selector.py
│   │   └── log_viewer.py
│   ├── profiles.py            # Gerenciamento de perfis
│   └── validators.py          # Validação de inputs
└── cli/
    ├── commands.py
    └── gui_command.py         # Comando: adalove gui
```

**Entry point**:
```bash
# Abrir GUI
adalove gui

# Ou executar script standalone
python -m adalove_extractor.gui
```

---

### 📋 Implementação Faseada

#### Fase 1: MVP (Tkinter) - 2-3 semanas
- [ ] Janela principal com opções básicas
- [ ] Validação de inputs
- [ ] Execução via subprocess
- [ ] Log em tempo real

#### Fase 2: Features Avançadas - 2-3 semanas
- [ ] Sistema de perfis
- [ ] Janela de progresso com estatísticas
- [ ] Validações complexas
- [ ] Atalhos de teclado

#### Fase 3: Polish (PyQt6 opcional) - 2-4 semanas
- [ ] Migração para PyQt6 (se desejado)
- [ ] Temas (claro/escuro)
- [ ] Ícones e visual profissional
- [ ] Animações sutis
- [ ] Sistema de notificações

---

### ✅ Benefícios

1. **Acessibilidade**: Usuários sem experiência em terminal
2. **Produtividade**: Salvar configurações evita repetir argumentos
3. **Descobribilidade**: Todas as opções visíveis (vs flags escondidas)
4. **Feedback**: Ver progresso em tempo real
5. **Educacional**: Mostra comando CLI equivalente (aprende CLI)

---

### ⚠️ Considerações

#### Dependências
- **Requer v3.0.0**: Arquitetura modular (separar GUI de lógica)
- **Requer v3.2.0**: Sistema de configuração (Pydantic Settings)
- **Requer v3.3.0**: Flags de extração seletiva implementadas

#### Complexidade
- **Testes**: GUI é mais difícil de testar automaticamente
- **Manutenção**: Mais código para manter
- **Distribuição**: Pode requerer packaging especial

#### Alternativas
- **Streamlit**: GUI web muito rápida de desenvolver
  - Vantagem: Desenvolvimento rápido, visual moderno
  - Desvantagem: Requer servidor, menos "nativo"

---

### 🎯 Casos de Uso

#### 1. Usuário Iniciante
**Perfil**: Primeiro contato com o projeto, não sabe CLI

**Fluxo**:
1. Baixa e instala
2. Executa `adalove gui`
3. Preenche formulário intuitivo
4. Clica "Executar"
5. ✅ Sucesso sem tocar no terminal!

#### 2. Usuário Recorrente
**Perfil**: Extrai múltiplos módulos, sempre mesmas configurações

**Fluxo**:
1. Abre GUI
2. Seleciona perfil salvo "Modulo 6"
3. Clica "Executar"
4. ✅ 2 cliques vs 5+ argumentos CLI

#### 3. Usuário Power
**Perfil**: Prefere CLI, mas usa GUI para explorar opções

**Fluxo**:
1. Configura na GUI
2. Clica "Mostrar comando equivalente"
3. Copia comando CLI para script/automação
4. ✅ GUI como ferramenta de aprendizado

---

**Issues Relacionadas**: TBD

---

## [v4.0.0] - Qualidade e Garantias (Planejado)

### 🎯 Objetivo
Estabelecer suite completa de testes automatizados para garantir robustez e evolução segura do código.

### 📦 Features

#### 1. Testes Unitários
**Prioridade**: 🔴 Alta

**Framework**: `pytest`

**Módulos a testar**:
```python
# tests/test_enrichment.py
def test_extract_date_time():
    """Testa extração de data/hora de strings variadas"""
    assert extract_date_time("Data: 01/01/2025 14:30") == ...

def test_normalize_datetime():
    """Testa normalização para ISO 8601"""
    assert normalize_datetime("01/01/2025", "14:30") == "2025-01-01T14:30:00-03:00"

# tests/test_anchor.py
def test_title_similarity():
    """Testa cálculo de similaridade entre títulos"""
    assert title_similarity("Autoestudo Programação", "Instrução Programação") > 0.7

def test_guess_professor():
    """Testa detecção de professor em textos"""
    assert guess_professor("Aula com Prof. Afonso") == "Afonso"

# tests/test_models.py
def test_card_validation():
    """Testa validação de modelo Card com Pydantic"""
    card = Card(titulo="Test", semana="01", ...)
    assert card.titulo == "Test"
```

#### 2. Testes de Contrato
**Prioridade**: 🟡 Média

- **Descrição**: Garantir que modelos Pydantic mantêm contratos
- **Validações**: Tipos, campos obrigatórios, formatos

#### 3. Testes de Snapshot
**Prioridade**: 🟡 Média

- **Descrição**: Verificar que enriquecimento produz resultados consistentes
- **Implementação**: `pytest-snapshot` ou similar

#### 4. Testes de Integração
**Prioridade**: 🟢 Baixa

- **Descrição**: Testar fluxo completo (mock de navegador)
- **Framework**: `pytest-playwright`

#### 5. Cobertura de Testes
**Prioridade**: 🟡 Média

- **Meta**: > 80% de cobertura
- **Tool**: `pytest-cov`
- **CI/CD**: Integração com GitHub Actions

**Issues Relacionadas**: TBD

---

## [v4.1.0] - Observabilidade (Planejado)

### 🎯 Objetivo
Implementar logs estruturados, métricas e relatórios para melhor depuração e análise quantitativa.

### 📦 Features

#### 1. Logs Estruturados
**Prioridade**: 🔴 Alta

**Formato**: JSON Lines

```json
{
  "timestamp": "2025-08-26T22:04:13.123Z",
  "level": "INFO",
  "module": "extractors.card",
  "message": "Card extracted successfully",
  "context": {
    "week": 7,
    "card_id": "card_123",
    "card_title": "Autoestudo Python",
    "extraction_time_ms": 234
  }
}
```

**Benefícios**:
- Parsing automatizado (jq, grep, análise)
- Integração com ferramentas de observabilidade
- Debug mais eficiente

#### 2. Métricas de Execução
**Prioridade**: 🟡 Média

**Contadores a rastrear**:
- Total de cards extraídos
- Cards por semana
- Tempo de extração por card
- Taxa de sucesso de ancoragem
- Distribuição de confiança (high/medium/low)
- Taxas de erro e retry

**Formato de relatório**:
```
📊 RELATÓRIO DE EXECUÇÃO
=======================
Turma: modulo6
Período: 2025-08-26 22:04:13 → 22:15:45
Duração: 11m 32s

Cards Extraídos: 127
  ├─ Instruções: 45 (35%)
  ├─ Autoestudos: 72 (57%)
  └─ Ativ. Ponderadas: 10 (8%)

Ancoragem:
  ├─ High confidence: 65 (90%)
  ├─ Medium confidence: 6 (8%)
  └─ Low confidence: 1 (1%)

Performance:
  ├─ Tempo médio/card: 5.4s
  └─ Cards/minuto: 11.0
```

#### 3. Contexto Rico em Logs
**Prioridade**: 🔴 Alta

**Campos contextuais**:
- `week`: Número da semana
- `card_id`: ID único do card
- `anchor_method`: Método usado para ancoragem
- `anchor_confidence`: Nível de confiança
- `professor`: Professor detectado
- `execution_id`: ID único da execução

#### 4. Integração com Ferramentas
**Prioridade**: 🟢 Baixa

- **Elasticsearch/Kibana**: Para análise visual de logs
- **Grafana**: Para dashboards de métricas
- **Sentry**: Para rastreamento de erros

**Issues Relacionadas**: TBD

---

## [v4.2.0] - Extensibilidade (Planejado)

### 🎯 Objetivo
Tornar heurísticas e regras facilmente extensíveis e configuráveis através de padrões de design.

### 📦 Features

#### 1. Strategy Pattern para Ancoragem
**Prioridade**: 🟡 Média

**Arquitetura**:
```python
# enrichment/anchor/strategies.py
class AnchorStrategy(ABC):
    @abstractmethod
    def score(self, autostudy: Card, instruction: Card) -> float:
        """Retorna score de 0.0 a 1.0"""
        pass

class ProfessorMatchStrategy(AnchorStrategy):
    weight = 0.4
    
    def score(self, autostudy, instruction):
        return 1.0 if autostudy.professor == instruction.professor else 0.0

class DateProximityStrategy(AnchorStrategy):
    weight = 0.3
    
    def score(self, autostudy, instruction):
        delta_days = abs((autostudy.date - instruction.date).days)
        return max(0, 1.0 - delta_days / 7.0)  # Decay de 7 dias

class TitleSimilarityStrategy(AnchorStrategy):
    weight = 0.2
    
    def score(self, autostudy, instruction):
        return calculate_similarity(autostudy.titulo, instruction.titulo)

class PositionProximityStrategy(AnchorStrategy):
    weight = 0.1
    
    def score(self, autostudy, instruction):
        delta_pos = abs(autostudy.indice - instruction.indice)
        return max(0, 1.0 - delta_pos / 10.0)  # Decay de 10 posições
```

**Uso**:
```python
# enrichment/anchor/engine.py
class AnchorEngine:
    def __init__(self, strategies: list[AnchorStrategy]):
        self.strategies = strategies
    
    def find_best_anchor(self, autostudy: Card, candidates: list[Card]) -> tuple[Card, float]:
        scores = []
        for candidate in candidates:
            weighted_score = sum(
                strategy.score(autostudy, candidate) * strategy.weight
                for strategy in self.strategies
            )
            scores.append((candidate, weighted_score))
        return max(scores, key=lambda x: x[1])
```

#### 2. Configuração de Pesos
**Prioridade**: 🟡 Média

**Arquivo**: `adalove.toml`
```toml
[adalove.enrichment.anchor.weights]
professor_match = 0.4
date_proximity = 0.3
title_similarity = 0.2
position_proximity = 0.1

[adalove.enrichment.anchor.thresholds]
high_confidence = 0.8
medium_confidence = 0.5
```

#### 3. Estratégias Customizáveis
**Prioridade**: 🟢 Baixa

**Permitir**:
- Desabilitar estratégias específicas
- Adicionar novas estratégias via plugin
- Ajustar pesos dinamicamente por módulo/turma

#### 4. Regras de Classificação
**Prioridade**: 🟡 Média

**Sistema de regras para detectar**:
- Instruções (palavras-chave, padrões)
- Autoestudos (prefixos, títulos)
- Atividades ponderadas (keywords: "ponderada", "entrega", "rubrica")

**Configurável via**:
```python
# config/classification_rules.py
INSTRUCTION_PATTERNS = [
    r"^Instrução",
    r"^Aula",
    r"^Encontro",
]

AUTOSTUDY_PATTERNS = [
    r"^Autoestudo",
    r"^Estudo",
    r"^Material de apoio",
]

GRADED_KEYWORDS = [
    "ponderada",
    "entrega",
    "rubrica",
    "avaliação",
]
```

**Issues Relacionadas**: TBD

---

## 🗃️ Features em Backlog

Features ainda sem versão definida, em ordem aproximada de prioridade:

### Alta Prioridade
- [ ] **Suporte a Parquet**: Formato otimizado para análise de dados
- [ ] **Export para banco de dados**: SQLite, PostgreSQL
- [ ] **Detecção de duplicatas**: Evitar re-extração de cards idênticos
- [ ] **Validação de integridade**: Checksums de dados extraídos

### Média Prioridade
- [ ] **API REST**: Servir dados extraídos via API
- [ ] **Dashboard Web**: Visualização de dados em tempo real
- [ ] **Notificações**: Email/Slack ao completar extração
- [ ] **Diff entre execuções**: Detectar novos cards ou mudanças

### Baixa Prioridade
- [ ] **ML para classificação**: Modelo treinado para detectar tipos de card
- [ ] **Análise de sentimento**: Classificar tom dos cards
- [ ] **Extração de entidades**: NLP para detectar tópicos/conceitos
- [ ] **Integração com Notion/Trello**: Export direto para ferramentas

### Exploratórias
- [ ] **Plugin system**: Extensões desenvolvidas por terceiros
- [ ] **Multi-plataforma**: Suporte a outras plataformas além do AdaLove
- [ ] **Cloud deployment**: Deploy em AWS/GCP/Azure
- [ ] **Containerização**: Docker image oficial

---

## 🤝 Como Contribuir

### Para implementar uma feature deste roadmap:

1. **Crie uma Issue no GitHub**
   - Referencie a seção do ROADMAP
   - Descreva a implementação proposta
   - Discuta trade-offs e alternativas

2. **Abra um PR com**
   - Código implementado
   - Testes automatizados
   - Documentação atualizada
   - Entrada no CHANGELOG.md

3. **Siga os princípios**
   - Qualidade > Velocidade
   - Documentação completa
   - Testes robustos
   - Compatibilidade retroativa quando possível

---

## 📚 Referências

- [Keep a Changelog](https://keepachangelog.com/pt-BR/)
- [Semantic Versioning](https://semver.org/lang/pt-BR/)
- [Conventional Commits](https://www.conventionalcommits.org/pt-br/)

---

**Última atualização**: 2025-10-08  
**Próxima revisão planejada**: 2026-01-01

