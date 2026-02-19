---
name: validate-testing
description: Validar execução da suíte de testes e cobertura de código. Use antes de completar uma feature, antes de PR, ou ao validar critérios de qualidade.
---

# Validate Testing

Validar que os testes passam e a cobertura atende as metas do projeto.

## Quando Usar

- Antes de completar uma feature
- Antes de abrir PR
- Após refatoração (validar não-regressão)
- Quando revisar qualidade do código

## Workflow

### 1. Executar Testes

```bash
# Testes rápidos
pytest -q

# Testes com verbose (se falhar)
pytest -v

# Parar no primeiro erro
pytest -x
```

**Meta:** 100% dos testes passando (0 failures).

### 2. Verificar Cobertura

```bash
# Cobertura com relatório no terminal
pytest --cov=src/adalove_extractor --cov-report=term-missing

# Gerar relatório HTML (mais detalhado)
pytest --cov=src/adalove_extractor --cov-report=html
```

### 3. Avaliar Cobertura

| Tipo de Código | Meta Mínima |
|----------------|-------------|
| Core business logic (`extractors/`, `enrichment/`) | >90% |
| API/integrações (`api/`) | >80% |
| IO/writers (`io/`) | >80% |
| Utilitários (`utils/`) | >80% |
| Config/CLI (`config/`, `cli/`) | >70% |
| **Overall** | **>80%** |

### 4. Relatório

```
🧪 Validação de Testes
======================

Testes: 15 passed, 0 failed
Cobertura: 85% overall

Por módulo:
  extractors/     92%  ✅
  enrichment/     88%  ✅
  api/            81%  ✅
  io/             79%  ⚠️ (meta: 80%)
  utils/          95%  ✅

📊 Resultado: ✅ PASS
```

## Se Falhar

### Testes Falhando

1. Ler o traceback completo
2. Identificar se é bug no código ou no teste
3. Corrigir e re-rodar

### Cobertura Baixa

1. Identificar linhas não cobertas (`--cov-report=term-missing`)
2. Priorizar: edge cases > happy path > error handling
3. Adicionar testes para as linhas mais críticas

## Estrutura de Testes Esperada

```
tests/
├── test_checkpoint_manager.py
├── test_incremental_writer.py
├── test_integration_checkpoint_flow.py
└── test_recovery_manager.py
```

## Skills Relacionadas

- `pre-commit-check` — inclui testes no checklist
