# ✅ TODO - Tarefas Técnicas

> **SINCRONIZADO COM**: [ROADMAP.md](./ROADMAP.md)  
> Este documento contém detalhes técnicos de implementação das features planejadas no roadmap.

---

## 📍 Status Atual: v3.1.0 (Released) → v3.2.0 (Próxima)

---

## ✅ v3.1.0 - Pipeline Resiliente + Testes (CONCLUÍDA - 2025-10-17)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.1.0](./ROADMAP.md#v310---pipeline-resiliente-planejado)

### Checkpoints e Salvamento Incremental
- [x] ✅ Implementar `CheckpointManager` em `adalove_extractor/io/checkpoint.py`
  - Métodos: `save()`, `load()`, `resume()`, `cleanup()`
  - Schema: JSON com metadata + dados
  - Validação de integridade com checksums
  
- [x] ✅ Adicionar `IncrementalWriter` em `adalove_extractor/io/incremental_writer.py`
  - Modo append-only para JSONL
  - Flush automático a cada N cards
  - Validação de integridade com checksums
  - Backup por semana em `checkpoint_semana_XX.json`

- [x] ✅ Criar `RecoveryManager` para detecção e retomada
  - Scan de checkpoints órfãos
  - Interface interativa para retomada
  - Merge de dados de múltiplas execuções
  - Detecção automática na inicialização

### Processamento Streaming
- [x] ✅ Refatorar extractors para async generators
  - `extract_cards() -> AsyncIterator[Card]`
  - Yield cards conforme extraídos
  - Reduzir uso de memória
  - Processamento incremental

### Testes Básicos de Robustez
- [x] ✅ Setup pytest + pytest-asyncio
  - Configurar `pyproject.toml`
  - Criar estrutura `tests/`
  - Meta de cobertura: >70% nos módulos críticos

- [x] ✅ Testes para checkpoints
  - `tests/test_checkpoint_manager.py`
  - `tests/test_incremental_writer.py`
  - `tests/test_recovery_manager.py`
  - Fixtures com estados simulados

- [x] ✅ Testes de integração
  - `tests/test_integration_checkpoint_flow.py`
  - Simulação de interrupção e recuperação
  - Validação de fluxo completo

### Validação e Idempotência
- [x] ✅ Implementar validação de integridade
  - Checksums para arquivos de checkpoint
  - Validação de estrutura JSON
  - Detecção de corrupção de dados

- [x] ✅ Sistema de idempotência
  - Detecção de duplicatas baseada em conteúdo
  - Merge inteligente de dados de múltiplas execuções
  - Consolidação de dados temporários

### Integração no CLI
- [x] ✅ Integrar sistema resiliente no `cli/main.py`
  - Detecção automática de execuções interrompidas
  - Prompt interativo para recuperação
  - Salvamento incremental após cada semana
  - Tratamento de erros com checkpoint de falha

### Resultados Finais
- [x] ✅ **41 testes** passando (100% de sucesso)
- [x] ✅ **Cobertura >70%** nos módulos críticos
- [x] ✅ **Sistema resiliente** funcionando perfeitamente
- [x] ✅ **Problema de perda de dados** completamente resolvido
  - Validação de integridade

- [ ] Testes para salvamento incremental
  - `tests/test_incremental_writer.py`
  - Verificar append-only
  - Validação de integridade
  - Testar flush automático

- [ ] Testes de recuperação
  - `tests/test_recovery_manager.py`
  - Simular falhas em pontos críticos
  - Verificar retomada correta
  - Testar merge de dados

### Validação e Idempotência
- [ ] Implementar hash-based deduplication
  - Manter mapa persistente de hashes processados
  - Skip de cards já extraídos
  - Opção: `--force-reextract` para ignorar cache
- [ ] Validação de estrutura JSON em checkpoints
- [ ] Contadores e checksums para integridade
- [ ] Limpeza automática de checkpoints antigos

---

## 📋 v3.1.2 - Quick Wins e UX (Planned - Q4 2025)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.1.2](./ROADMAP.md#v312---quick-wins-e-melhorias-ux-planejado)

### Barra de Progresso
- [ ] Adicionar `tqdm` às dependencies
- [ ] Integrar em `cli/main.py`
  - Progresso por semana
  - Progresso global
  - ETA e velocidade
  - Cards/minuto

### Modo Dry-Run
- [ ] Flag `--dry-run` em CLI
- [ ] Simular extração sem I/O
- [ ] Exibir estatísticas estimadas
- [ ] Validação de configurações

### Verbosidade Configurável
- [ ] Flags `-v`, `-vv`, `-vvv`
- [ ] Níveis de log dinâmicos
- [ ] Debug detalhado em modo verbose
- [ ] Configuração por módulo

### Comando Version
- [ ] Implementar `adalove --version`
- [ ] Exibir: versão, Python, Playwright
- [ ] Informações do sistema
- [ ] Dependências principais

---

## 🔧 v3.1.3 - Infraestrutura CI/CD (Planned - Q4 2025)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.1.3](./ROADMAP.md#v313---infraestrutura-e-cicd-planejado)

### GitHub Actions
- [ ] Criar `.github/workflows/test.yml`
  - Matrix: Python 3.11, 3.12
  - Steps: install, lint, test, coverage
  - Cache de dependências
  - Relatórios de cobertura

- [ ] Criar `.github/workflows/release.yml`
  - Build e publish no PyPI
  - Changelog automático
  - Versionamento semântico

### Pre-commit Hooks
- [ ] Criar `.pre-commit-config.yaml`
- [ ] Configurar: black, isort, flake8, mypy
- [ ] Documentar setup em CONTRIBUTING.md
- [ ] Instalação: `pre-commit install`

### Dependabot
- [ ] Criar `.github/dependabot.yml`
- [ ] Schedule semanal
- [ ] Auto-merge para patches
- [ ] Security alerts

### Docker
- [ ] Criar `Dockerfile` multistage
- [ ] Criar `docker-compose.yml` para dev
- [ ] Publicar no Docker Hub
- [ ] Otimização de tamanho

---

## 📊 v3.1.5 - Testes Expandidos (Planned - Q4 2025)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.1.5](./ROADMAP.md#v315---testes-expandidos-planejado)

### Testes de Enriquecimento
- [ ] `tests/unit/test_normalizer.py`
  - Data/hora extraction e normalização
  - Professor detection
  - URL extraction
  - Validação de formatos

- [ ] `tests/unit/test_classifier.py`
  - Detecção de instruções
  - Detecção de autoestudos
  - Detecção de ponderadas
  - Padrões regex

- [ ] `tests/unit/test_anchor.py`
  - Similaridade de títulos
  - Algoritmo de ancoragem
  - Níveis de confiança
  - Multi-fator scoring

### Testes de Extração
- [ ] `tests/unit/test_card_extractor.py`
- [ ] `tests/unit/test_week_extractor.py`
- [ ] Mocks de Playwright responses
- [ ] Simulação de elementos HTML

### Testes de Contrato
- [ ] `tests/unit/test_models.py`
  - Validação Pydantic de Card
  - Validação de EnrichedCard
  - Serialização/deserialização
  - Campos obrigatórios

### CI/CD
- [ ] Integrar com GitHub Actions
- [ ] Badge de coverage no README
- [ ] Fail se coverage <70%
- [ ] Relatórios HTML de cobertura

---

## 📋 v3.2.0 - Configuração e CLI Completa (Planned - Q1 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.2.0](./ROADMAP.md#v320---configuração-e-modos-de-execução-planejado)

### Interface CLI Completa
- [ ] Implementar Typer framework
- [ ] Comandos: `extract`, `resume`, `version`
- [ ] Argumentos: `--turma`, `--headless`, `--no-interactive`
- [ ] Flags: `--weeks`, `--frentes`, `--output`, `--format`

### Configuração via Arquivo
- [ ] Suporte a `adalove.toml`
- [ ] Configuração de extração, enriquecimento
- [ ] Override via CLI
- [ ] Validação de configuração

### Integração com Agendadores
- [ ] Exemplos de cron/Task Scheduler
- [ ] Modo não-interativo para automação
- [ ] Logs estruturados para monitoramento

---

## 📋 v3.3.0 - Extração Seletiva (Planned - Q1 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.3.0](./ROADMAP.md#v330---extração-seletiva-planejado)

### Extração de Semanas Específicas
- [ ] Parser de expressões de semanas (`1,3,7` ou `1-5`)
- [ ] Validação de semanas existentes
- [ ] Skip inteligente de semanas não solicitadas
- [ ] Suporte a ranges e combinações

### Extração de Frentes Específicas
- [ ] Detecção automática de frentes
- [ ] Mapeamento professor → frente
- [ ] Análise de título do card (keywords)
- [ ] Suporte a múltiplas frentes

### Filtros Combinados
- [ ] Semanas + frentes específicas
- [ ] Apenas autoestudos (`--only-autostudy`)
- [ ] Apenas atividades ponderadas (`--only-graded`)
- [ ] Exclusão de frentes (`--exclude-frentes`)

---

## 📋 v3.4.0 - Interface Gráfica (GUI) (Planned - Q2 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v3.4.0](./ROADMAP.md#v340---interface-gráfica-gui-planejado)

### Interface Principal
- [ ] Implementar com Tkinter (MVP)
- [ ] Layout: turma, semanas, frentes, opções avançadas
- [ ] Validação em tempo real
- [ ] Feedback visual de status

### Janela de Progresso
- [ ] Barra de progresso por semana
- [ ] Log em tempo real (scrollable)
- [ ] Estatísticas atualizadas
- [ ] Botão de cancelamento

### Sistema de Perfis
- [ ] Salvar/carregar configurações
- [ ] Arquivo `~/.adalove/profiles.json`
- [ ] Exportar/importar perfis
- [ ] Perfil padrão

### Integração com CLI
- [ ] GUI gera comando CLI internamente
- [ ] Execução via subprocess
- [ ] Streaming de output
- [ ] Mostrar comando equivalente

---

## 🔮 v4.0.0 - Qualidade e Garantias (Planned - Q2 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v4.0.0](./ROADMAP.md#v400---qualidade-e-garantias-planejado)

### Testes Unitários Avançados
- [ ] Estrutura completa de testes
- [ ] Fixtures com dados de exemplo
- [ ] Testes parametrizados
- [ ] Cobertura >80%

### Testes de Integração
- [ ] Fluxo completo com mocks
- [ ] Testes de performance
- [ ] Testes de stress
- [ ] Validação de outputs

### CI/CD Avançado
- [ ] Pipeline completo
- [ ] Testes em múltiplas versões Python
- [ ] Deploy automático
- [ ] Notificações

---

## 🔮 v4.1.0 - Observabilidade (Planned - Q3 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v4.1.0](./ROADMAP.md#v410---observabilidade-planejado)

### Logs Estruturados
- [ ] Schema JSON Lines definido
- [ ] Rotação de logs (7 dias ou 100MB)
- [ ] Níveis configuráveis por módulo
- [ ] Output: arquivo + stdout

### Métricas de Execução
- [ ] Contadores: cards extraídos, erros, retries
- [ ] Timers: tempo de extração, enriquecimento
- [ ] Distribuição de confiança
- [ ] Relatórios formatados

### Integração com Ferramentas
- [ ] Elasticsearch/Kibana
- [ ] Grafana dashboards
- [ ] Sentry para rastreamento de erros
- [ ] Alertas automáticos

---

## 🔮 v4.2.0 - Extensibilidade (Planned - Q3 2026)

> 📋 **Visão geral**: Ver [ROADMAP.md - v4.2.0](./ROADMAP.md#v420---extensibilidade-planejado)

### Plugin System
- [ ] Interface base `Plugin` (ABC)
- [ ] `EnrichmentPlugin` para enriquecimento
- [ ] `ExtractionPlugin` para extração
- [ ] Sistema de registro e carregamento

### Strategy Pattern
- [ ] `AnchorStrategy` para ancoragem
- [ ] Estratégias: professor, data, título, posição
- [ ] Configuração de pesos via TOML
- [ ] Estratégias customizáveis

### Regras Configuráveis
- [ ] Padrões de classificação
- [ ] Keywords para tipos de card
- [ ] Thresholds de confiança
- [ ] Mapeamentos professor → frente

---

## 🐛 Bugs Conhecidos (Backlog Técnico)

### Alta Prioridade
- [ ] **Timeout em semanas com muitos cards (>50)**
  - Investigar: Aumentar timeout? Paralelizar?
  - Módulo afetado: `extractors/week.py`
  - Solução: Implementar timeout dinâmico

- [ ] **Cards sem data/hora quebram normalização**
  - Adicionar fallback values
  - Módulo afetado: `enrichment/normalizer.py`
  - Solução: Valores padrão para campos obrigatórios

### Média Prioridade
- [ ] **Professor não detectado com múltiplos nomes**
  - Melhorar regex de detecção
  - Módulo afetado: `enrichment/normalizer.py`
  - Solução: Algoritmo de matching mais robusto

---

## 🔧 Melhorias Técnicas (Backlog)

### Código
- [ ] Completar type hints em `browser/navigator.py`
- [ ] Refatorar `enrich_cards()` (>100 linhas)
- [ ] Extrair magic numbers para `config/constants.py`
- [ ] Padronizar docstrings (Google style)

### Performance
- [ ] Profiling com cProfile
- [ ] Cache de elementos Playwright já visitados
- [ ] Avaliar paralelização com `asyncio.gather()`
- [ ] Otimizar uso de memória

### Documentação
- [ ] Exemplos avançados no README
- [ ] FAQ de troubleshooting
- [ ] Mapear estrutura HTML do AdaLove
- [ ] Guias de contribuição

---

## 📊 Análise de Dados (Backlog)

- [ ] Notebook Jupyter: `notebooks/exploratory_analysis.ipynb`
- [ ] Script de relatórios: `scripts/generate_report.py`
- [ ] Visualizações com matplotlib/plotly
- [ ] Dashboard com Streamlit (opcional)
- [ ] Análise de correlações entre frentes e horários

---

**Legenda de Prioridades**:
- 🔥 URGENTE (v3.1.0)
- 📋 Planejado (v3.1.x, v3.2.x, v3.3.x, v3.4.x)
- 🔮 Futuro (v4.x)
- 🐛 Bug
- 🔧 Melhoria
- 📊 Análise

---

**Última sincronização entre ROADMAP.md e TODO.md**: 2025-10-16