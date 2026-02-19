---
name: pre-commit-check
description: Checklist de qualidade pré-commit. Valida formatação, linting, testes, segurança e status do git antes de cada commit. Use antes de qualquer `git commit`.
---

# Pre-Commit Check

Checklist abrangente de qualidade antes de commitar código.

## Quando Usar

- **OBRIGATÓRIO** antes de cada `git commit`
- Após implementar uma feature ou fix
- Antes de abrir PR

## Workflow

### 0. Stack Check

Confirmar que o ambiente está correto:

```bash
# Verificar que pyproject.toml existe
ls pyproject.toml

# Verificar ambiente virtual ativo
which python  # Deve apontar para venv/
```

### 1. Formatação e Linting

```bash
# Formatar código
ruff format src/ tests/

# Verificar lint (com auto-fix)
ruff check src/ tests/ --fix

# Verificar types (se mypy instalado)
mypy src/
```

**Pass criteria:** 0 erros de formatação, 0 warnings de lint não resolvidos.

**Se falhar:**
- `ruff format` corrige automaticamente — rodar e re-stagear
- `ruff check --fix` corrige o que pode — resolver o resto manualmente

### 2. Testes

```bash
# Executar testes
pytest -q

# Com cobertura (opcional, mas recomendado)
pytest --cov=src/adalove_extractor --cov-report=term-missing
```

**Pass criteria:** 0 failures. Cobertura ≥80% (meta).

**Se falhar:**
- Corrigir testes quebrados antes de commitar
- Se teste quebrou por mudança intencional, atualizar o teste

### 3. Segurança

```
Checklist manual:
- [ ] Nenhum token/senha hardcoded no diff (`git diff --cached`)
- [ ] .env não está sendo commitado (`git status`)
- [ ] .token_cache não está sendo commitado
- [ ] Logs não contêm dados sensíveis de alunos
```

**Validação rápida:**
```bash
# Buscar strings suspeitas no diff staged
git diff --cached | grep -iE "(password|token|secret|api_key|bearer)" || echo "OK: nenhum secret detectado"

# Verificar que .env não está staged
git diff --cached --name-only | grep -E "^\.env$|^\.token_cache$" && echo "ERRO: arquivo sensível staged!" || echo "OK"
```

### 4. Git Status

```bash
# Verificar o que está staged
git diff --cached --stat

# Confirmar que mudanças são intencionais
git diff --cached --name-only
```

**Verificar:**
- [ ] Apenas arquivos intencionais estão staged
- [ ] Nenhum arquivo de debug/temp incluído
- [ ] Commit é atômico (1 tarefa = 1 commit)
- [ ] Máximo ~100 linhas de mudança

### 5. Mensagem de Commit

Formato: `<type>(<scope>): <subject>`

**Validar:**
- [ ] Type é um dos: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`
- [ ] Scope está na lista: `extractor`, `auth`, `cli`, `api`, `config`, `enrichment`, `io`, `models`, `docs`, `deps`
- [ ] Subject é imperativo, em português ou inglês, ≤72 chars
- [ ] Sem menção a IA/Claude/Copilot

## Relatório de Saída

```
🔍 Pre-Commit Check
====================

✅ Stack: pyproject.toml presente, venv ativo
✅ Formatação: ruff format OK
✅ Lint: ruff check OK (0 warnings)
✅ Testes: pytest 15 passed (85% coverage)
✅ Segurança: nenhum secret detectado
✅ Git: 3 arquivos, 47 linhas, commit atômico

📊 Resultado: ✅ PASS — pronto para commit
```

## Se Falhar

Não commitar. Corrigir cada item que falhou e re-rodar o check.

**Prioridade de correção:**
1. 🚨 Segurança (secrets) — corrigir imediatamente
2. ❌ Testes falhando — corrigir antes de commitar
3. ⚠️ Lint/format — rodar auto-fix e re-stagear
4. ℹ️ Cobertura baixa — melhorar se possível

## Skills Relacionadas

- `organize-commits` — para organizar mudanças em commits atômicos
- `validate-testing` — para validar testes em mais detalhe
