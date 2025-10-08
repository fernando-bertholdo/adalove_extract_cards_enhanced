# 🤖 Prompts dos Background Agents

## 📂 Estrutura

```
prompts/
├── README_AGENTS.md              ← Este arquivo
├── PROMPT_AGENT_A_CORE.md       ← Models & Config (FUNDAÇÃO)
├── PROMPT_AGENT_B_EXTRACTORS.md ← Browser & Extractors
├── PROMPT_AGENT_C_ENRICHMENT.md ← Enrichment & Utils
├── PROMPT_AGENT_D_IO.md         ← IO & CLI Skeleton
├── PROMPT_AGENT_E_RESILIENCE.md ← v3.1.0 + v3.3.0 parte 1
└── PROMPT_AGENT_F_CLI.md        ← v3.2.0 + v3.3.0 parte 2
```

##  🚀 Ordem de Execução

### FASE 1: Modularização (Paralela)

```bash
# Iniciar simultaneamente
1. Agent A (COMEÇA PRIMEIRO) - 3-5 dias
2. Agent D (pode começar após dia 2 de A) - 4-6 dias
3. Agent B (aguarda Agent A concluir) - 5-7 dias
4. Agent C (aguarda Agent A concluir) - 5-7 dias

# Integration Sprint - 2-3 dias
```

### FASE 2: Features Avançadas (Paralela)

```bash
# Após FASE 1 completa
5. Agent E + Agent F (paralelos) - 3-4 semanas cada

# Final Integration - 1-2 dias
```

## 🎯 Responsabilidades

| Agent | Módulos | Prioridade | Depende de |
|-------|---------|------------|------------|
| **A** | models/, config/ | 🔴 Crítica | - |
| **B** | browser/, extractors/ | 🟡 Alta | Agent A |
| **C** | enrichment/, utils/ | 🟡 Alta | Agent A |
| **D** | io/, cli/ (skeleton) | 🟢 Média | Agent A (parcial) |
| **E** | v3.1.0 + v3.3.0 p1 | 🟡 Alta | FASE 1 |
| **F** | v3.2.0 + v3.3.0 p2 | 🟡 Alta | FASE 1 |

## 📊 Métricas

| Agent | LoC | Modules | Tests | Tempo |
|-------|-----|---------|-------|-------|
| A | ~200 | 4 | 20+ | 3-5 dias |
| B | ~300 | 4 | 15+ | 5-7 dias |
| C | ~400 | 5 | 30+ | 5-7 dias |
| D | ~200 | 3 | 10+ | 4-6 dias |
| E | ~300 | 3 | 20+ | 3-4 sem |
| F | ~250 | 2 | 15+ | 3-4 sem |

## 🔄 Integração

### Após FASE 1

```bash
git checkout main
git merge feature/v3.0.0-agent-a-core
git merge feature/v3.0.0-agent-d-io
git merge feature/v3.0.0-agent-b-extractors
git merge feature/v3.0.0-agent-c-enrichment

# Testar integração
pytest tests/ -v --cov
python -m adalove_extractor.cli --help
```

### Após FASE 2

```bash
git merge feature/v3.1.0-resilience
git merge feature/v3.2.0-cli-complete

# Testar todos cenários
adalove extract --turma test --weeks 1-3
adalove extract --resume
```

## ✅ Critérios de Sucesso

### FASE 1
- [ ] Todos agents completaram
- [ ] Zero conflitos de merge
- [ ] Testes passando (>70% cobertura)
- [ ] Output idêntico ao v2.0.0
- [ ] Instalável via pip

### FASE 2
- [ ] v3.1.0-v3.3.0 completas
- [ ] CLI funcional com todas flags
- [ ] Checkpoints funcionando
- [ ] Extração seletiva operacional
- [ ] Documentação atualizada

## 📞 Contato

Ver `AGENTS_ORCHESTRATION.md` para detalhes completos da estratégia.

