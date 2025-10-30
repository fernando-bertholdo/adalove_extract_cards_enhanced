# 🗺️ Roadmap - Adalove Extract Cards Enhanced

Este documento descreve a visão de longo prazo para o desenvolvimento do projeto, organizando features planejadas por versões futuras e prioridades.

---

## 📋 Índice

- [Princípios de Desenvolvimento](#-princípios-de-desenvolvimento)
- [Visão Geral de Versões](#-visão-geral-de-versões)
- [v3.0.0 - Arquitetura Modular](#v300---arquitetura-modular-released)
- [v3.1.0 - Pipeline Resiliente](#v310---pipeline-resiliente-planejado)
- [v3.2.0 - Configuração e Modos de Execução](#v320---configuração-e-modos-de-execução-planejado)
- [v3.3.0 - Extração Seletiva](#v330---extração-seletiva-planejado)
- [v3.4.0 - Interface Gráfica (GUI)](#v340---interface-gráfica-gui-planejado)
- [v4.0.0 - Qualidade e Garantias](#v400---qualidade-e-garantias-planejado)
- [v4.1.0 - Observabilidade](#v410---observabilidade-planejado)
- [v4.2.0 - Extensibilidade](#v420---extensibilidade-planejado)
- [Lições Aprendidas](#-lições-aprendidas)
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

| Versão | Status | Tema Principal | ETA | Prioridade |
|--------|--------|----------------|-----|------------|
| **v2.0.0** | ✅ Released | Sistema de Enriquecimento Inteligente | 2025-10-08 | - |
| **v3.0.0** | ✅ Released | Arquitetura Modular | 2025-10-08 | - |
| **v3.1.0** | ✅ **RELEASED** | Pipeline Resiliente + Checkpoints | 2025-10-17 | **CONCLUÍDA** |
| **v3.2.0** | 📋 Planned | Configuração e CLI | Q1 2026 | Alta |
| **v3.3.0** | 📋 Planned | Extração Seletiva | Q1 2026 | Média |
| **v3.4.0** | 📋 Planned | Interface Gráfica (GUI) | Q2 2026 | Média |
| **v4.0.0** | 🔮 Future | Qualidade e Garantias | Q2 2026 | Baixa |
| **v4.1.0** | 🔮 Future | Observabilidade | Q3 2026 | Baixa |
| **v4.2.0** | 🔮 Future | Extensibilidade | Q3 2026 | Baixa |

> **🚨 ATUALIZAÇÃO**: v3.1.0 elevada para **URGENTE** devido à experiência real de perda de dados (204 cards extraídos perdidos por falha simples no salvamento final).

---

## [v3.0.0] - Arquitetura Modular (✅ Released)

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

## [v3.1.0] - Pipeline Resiliente (✅ Released)

### 🎯 Objetivo
Implementar pipeline robusto com streaming, checkpoints e idempotência para execuções mais seguras e eficientes.

> **✅ CONCLUÍDO**: Sistema resiliente implementado com sucesso! Resolve completamente o problema de perda de dados.

### 📦 Features

#### 1. Sistema de Checkpoints Avançado
**Prioridade**: 🔴 **CRÍTICA** (elevada devido a experiência real)

- **Descrição**: Salvar progresso incrementalmente para evitar perda total de dados
- **Implementação**:
  - Arquivo `progress.json` em `dados_extraidos/turma/`
  - Salvamento após cada semana processada
  - Detecção automática de execuções interrompidas
  - Interface para retomar execuções
- **Estrutura do Checkpoint**:
  ```json
  {
    "turma": "modulo8",
    "execution_id": "modulo8_20251016_172829",
    "status": "extracting",
    "semanas_descobertas": ["Semana 01", "Semana 02", "Semana 03", "Semana 04", "Semana 05", "Semana 06", "Semana 07", "Semana 08", "Semana 09", "Semana 10"],
    "semanas_processadas": ["Semana 01", "Semana 02", "Semana 03", "Semana 04", "Semana 05", "Semana 06", "Semana 07", "Semana 08", "Semana 09", "Semana 10"],
    "cards_extraidos": 204,
    "ultima_atualizacao": "2025-10-16T17:36:54Z",
    "sessao_id": "modulo8_20251016_172829",
    "checkpoints": {
      "semana_01": {"cards": 6, "timestamp": "2025-10-16T17:30:01Z"},
      "semana_02": {"cards": 22, "timestamp": "2025-10-16T17:30:47Z"},
      "semana_03": {"cards": 27, "timestamp": "2025-10-16T17:31:43Z"}
    }
  }
  ```

#### 2. Salvamento Incremental de Dados
**Prioridade**: 🔴 **CRÍTICA**

- **Descrição**: Salvar cards conforme são extraídos (não apenas no final)
- **Implementação**:
  - Arquivo `cards_temp.jsonl` (append-only)
  - Backup por semana em `checkpoint_semana_XX.json`
  - Validação de integridade dos dados salvos
- **Benefícios**: 
  - ✅ **Zero perda de dados** mesmo com falhas
  - ✅ **Progresso visível** em tempo real
  - ✅ **Retomada rápida** de execuções interrompidas

#### 3. Processamento Streaming
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

#### 4. Idempotência com Record Hash
**Prioridade**: 🟡 Média

- **Descrição**: Usar `record_hash` como chave idempotente
- **Implementação**:
  - Manter mapa persistente de hashes processados
  - Skip de cards já extraídos em execuções anteriores
  - Opção: `--force-reextract` para ignorar cache

#### 5. Sistema de Recuperação Inteligente
**Prioridade**: 🔴 **CRÍTICA**

- **Descrição**: Detectar e recuperar execuções interrompidas automaticamente
- **Implementação**:
  ```python
  # Detecção automática na inicialização
  if os.path.exists("progress.json"):
      print("🔄 Execução anterior detectada!")
      print(f"📊 Progresso: {cards_extraidos}/{total_estimado} cards extraídos")
      print("❓ Deseja continuar de onde parou? (s/n)")
      
      if continuar:
          carregar_estado_anterior()
          retomar_de_ultima_semana_processada()
  ```
- **Casos de uso**:
  - ✅ **Falha no salvamento final** (como aconteceu com Fernando)
  - ✅ **Interrupção por erro de rede**
  - ✅ **Cancelamento manual pelo usuário**
  - ✅ **Falha do navegador/Playwright**

#### 6. Validação de Integridade
**Prioridade**: 🟡 Média

- **Descrição**: Verificar integridade dos dados salvos incrementalmente
- **Implementação**:
  - Checksums de arquivos de checkpoint
  - Validação de estrutura JSON
  - Contagem de cards por semana
- **Benefícios**: Detectar corrupção de dados antes da finalização

#### 7. Limpeza Automática de Checkpoints
**Prioridade**: 🟢 Baixa

- **Descrição**: Remover checkpoints antigos automaticamente
- **Implementação**:
  - Retenção de 7 dias para checkpoints
  - Limpeza após execução bem-sucedida
  - Preservação de checkpoints com falhas para debug

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

#### 2. Janela de Progresso
**Prioridade**: 🔴 Alta

**Features**:
- Barra de progresso por semana
- Log em tempo real (scrollable)
- Estatísticas atualizadas (cards extraídos, tempo decorrido)
- Botão de cancelamento (graceful stop)

#### 3. Sistema de Perfis
**Prioridade**: 🟡 Média

**Descrição**: Salvar e carregar configurações para reutilização

#### 4. Validação e Feedback
**Prioridade**: 🔴 Alta

**Validações em tempo real**:
- Formato de semanas válido (`1,3,7` ou `1-5`)
- Diretório de saída acessível
- Credenciais configuradas (.env existe)
- Playwright instalado

#### 5. Integração com CLI
**Prioridade**: 🟡 Média

**Descrição**: GUI gera e executa comando CLI internamente

**Issues Relacionadas**: TBD

---

## [v4.0.0] - Qualidade e Garantias (Planejado)

### 🎯 Objetivo
Estabelecer suite completa de testes automatizados para garantir robustez e evolução segura do código.

### 📦 Features

#### 1. Testes Unitários
**Prioridade**: 🔴 Alta

**Framework**: `pytest`

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

#### 2. Métricas de Execução
**Prioridade**: 🟡 Média

**Contadores a rastrear**:
- Total de cards extraídos
- Cards por semana
- Tempo de extração por card
- Taxa de sucesso de ancoragem
- Distribuição de confiança (high/medium/low)
- Taxas de erro e retry

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

#### 2. Configuração de Pesos
**Prioridade**: 🟡 Média

#### 3. Estratégias Customizáveis
**Prioridade**: 🟢 Baixa

#### 4. Regras de Classificação
**Prioridade**: 🟡 Média

**Issues Relacionadas**: TBD

---

## 📚 Lições Aprendidas

### 🚨 Experiência Crítica: Perda de Dados (2025-10-16)

**Situação**: Execução completa de 204 cards extraídos perdida por falha simples no salvamento final.

**Impacto**:
- ⏰ **8+ minutos** de trabalho perdido
- 😤 **Frustração** do usuário
- 🔄 **Necessidade** de re-execução completa

**Lições**:
1. **Salvamento incremental** é crítico para robustez
2. **Checkpoints** devem ser prioridade máxima
3. **Recuperação de dados** deve ser automática
4. **Validação de integridade** deve ser contínua

**Ações tomadas**:
- ✅ Fix imediato: Criação automática de diretórios
- 🔥 Elevação de prioridade: v3.1.0 para URGENTE
- 📋 Atualização do roadmap com foco em robustez

---

## 🗃️ Features em Backlog

Features ainda sem versão definida, em ordem aproximada de prioridade:

### 🔥 **CRÍTICA** (Baseado na experiência real) ✅ **CONCLUÍDA v3.1.0**
- [x] ✅ **Sistema de checkpoints robusto**: Evitar perda total de dados
- [x] ✅ **Recuperação automática**: Detectar e retomar execuções interrompidas
- [x] ✅ **Validação de integridade**: Checksums e verificação contínua
- [x] ✅ **Salvamento incremental**: Dados salvos em tempo real

### Alta Prioridade
- [ ] **Suporte a Parquet**: Formato otimizado para análise de dados
- [ ] **Export para banco de dados**: SQLite, PostgreSQL
- [ ] **Detecção de duplicatas**: Evitar re-extração de cards idênticos

### Média Prioridade
- [ ] **Feedback Visual em Tempo Real**: Mostrar tipo, frente e classificação durante extração
  - **Complexidade**: 🔴 Alta (requer refatoração significativa)
  - **Desafio**: Informações só disponíveis após enriquecimento completo
  - **Solução**: Enriquecimento incremental ou classificação básica em tempo real
  - **Benefício**: UX melhorada + validação visual da qualidade da extração
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

**Última atualização**: 2025-10-16  
**Próxima revisão planejada**: 2026-01-01
