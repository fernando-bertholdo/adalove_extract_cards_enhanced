---
name: organize-commits
description: Organizar mudanças pendentes em commits atômicos seguindo Conventional Commits. Use quando há múltiplas mudanças no working tree que precisam ser separadas em commits individuais por tarefa.
---

# Organize Commits

Organizar mudanças em commits atômicos com rastreamento e formato padronizado.

## Quando Usar

- Múltiplas mudanças não-commitadas no working tree
- Após sessão de desenvolvimento com várias features/fixes
- Antes de push (organizar histórico limpo)

## Regras Hard-Coded

1. **NUNCA** usar `git add .` ou `git add -A`
2. **SEMPRE** stage arquivos individualmente por task
3. **MÁXIMO** 100 linhas por commit
4. **FORMATO:** `<type>(<scope>): <subject>`
5. **NUNCA** mencionar IA em commits — sem co-autoria

## Scopes do Projeto

| Scope | Diretório / Área |
|-------|------------------|
| `extractor` | `src/adalove_extractor/extractors/` |
| `auth` | `src/adalove_extractor/api/auth.py` |
| `api` | `src/adalove_extractor/api/` |
| `cli` | `adalove_cli.py`, `src/adalove_extractor/cli/` |
| `config` | `src/adalove_extractor/config/` |
| `enrichment` | `src/adalove_extractor/enrichment/` |
| `io` | `src/adalove_extractor/io/` |
| `models` | `src/adalove_extractor/models/` |
| `docs` | `docs/`, `README.md`, `CONTRIBUTING.md` |
| `deps` | `requirements*.txt`, `pyproject.toml` |
| `test` | `tests/` |

## Workflow

### 1. Analisar Mudanças

```bash
# Ver status completo
git status

# Ver diff detalhado
git diff --stat

# Listar arquivos modificados
git diff --name-only
```

### 2. Mapear Mudanças → Tasks

Para cada arquivo modificado, classificar:
- Qual **type** (feat/fix/refactor/docs/test/chore)?
- Qual **scope** (ver tabela acima)?
- Qual **tarefa lógica** este arquivo pertence?

### 3. Criar Commits Atômicos

Para cada task identificada:

```bash
# Stage APENAS os arquivos da task
git add src/adalove_extractor/api/client.py
git add src/adalove_extractor/api/endpoints.py

# Verificar o que está staged
git diff --cached --stat

# Commit com formato correto
git commit -m "feat(api): adicionar endpoint de extração por turma"
```

### 4. Verificar Resultado

```bash
# Ver últimos commits
git log --oneline -5

# Verificar que cada commit é atômico
git log --stat -5
```

## Formato de Commit

```
<type>(<scope>): <subject>

[corpo opcional — max 72 chars por linha]
```

### Types

| Type | Quando Usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem mudar comportamento |
| `docs` | Documentação |
| `test` | Testes |
| `chore` | Manutenção (deps, configs, CI) |
| `ci` | Pipeline CI/CD |

## Anti-Patterns

```
# ❌ NUNCA
git add .
git commit -m "várias mudanças"
git commit -m "WIP"
git commit -m "feat: atualizar código (Assisted by Claude)"

# ✅ CORRETO
git add src/adalove_extractor/api/client.py
git commit -m "fix(api): corrigir timeout em chamadas à API Adalove"
```

## Quebrando Commits Grandes

Se uma mudança tem >100 linhas:

1. Separar em etapas lógicas (ex: modelos → lógica → testes)
2. Usar `git add -p` para stage parcial de arquivo
3. Cada commit deve ser independente e compilável

## Skills Relacionadas

- `pre-commit-check` — rodar antes de cada commit
