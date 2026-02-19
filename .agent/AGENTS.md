# AGENTS.md — adalove_extract_cards_enhanced

Regras operacionais para agentes de codificação neste projeto.

## Sobre o Projeto

CLI Python para extrair cards de atividades da plataforma Adalove (Inteli), via API + Playwright para autenticação. Gera JSON estruturado com enriquecimento de dados.

## Dev Environment

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Rodar CLI
python adalove_cli.py

# Rodar testes
pytest -q

# Lint + format
ruff format src/ tests/
ruff check src/ tests/ --fix
```

## Stack

- **Linguagem:** Python 3.11+
- **Autenticação:** Playwright (browser automation p/ captura de token)
- **API:** requests (chamadas REST à API Adalove)
- **Modelos:** Pydantic (validação de dados)
- **Config:** pydantic-settings + `.env`
- **Testes:** pytest + pytest-cov
- **Lint:** ruff
- **CLI:** Rich (terminal UI)

## Estrutura do Projeto

```
src/adalove_extractor/
├── api/           # Autenticação, client HTTP, endpoints, modelos API
├── cli/           # Interface terminal (Rich)
├── config/        # Settings (.env) e logging
├── enrichment/    # Normalização e enriquecimento de cards
├── extractors/    # Lógica de extração (turma completa)
├── io/            # Writers, checkpoint, recovery
├── models/        # Modelos Pydantic (Card, EnrichedCard, tipos)
└── utils/         # Hash, text utils
tests/             # Testes unitários e integração
docs/              # Documentação técnica
```

## Code Style

1. **Formatação:** `ruff format` (PEP 8, linha max 100 chars)
2. **Type hints:** obrigatório em funções públicas
3. **Docstrings:** Google style
4. **Logging:** `logging.getLogger(__name__)` — nunca `print()`
5. **Naming:** `snake_case` funções/vars, `PascalCase` classes, `UPPER_SNAKE` constants
6. **Imports:** stdlib → third-party → local, organizado por ruff

## Commit Strategy

### Conventional Commits

Formato: `<type>(<scope>): <subject>`

**Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`

**Scopes:** `extractor`, `auth`, `cli`, `api`, `config`, `enrichment`, `io`, `models`, `docs`, `deps`

### Regras

- **1 task = 1 commit** (atômico)
- **Max 100 linhas** por commit
- **NUNCA** `git add .` — stage individual
- **NUNCA** mencionar IA em commits ou co-autoria

## Segurança

- **Token Adalove:** vive em `.env` (gitignored), nunca hardcoded
- **`.token_cache`:** contém token persistido, gitignored
- **Logs:** nunca logar tokens, senhas ou dados pessoais de alunos
- **`.env.example`:** mantém template sem valores reais

## Skills Disponíveis

| Skill | Quando Usar |
|-------|-------------|
| `pre-commit-check` | Antes de cada commit |
| `organize-commits` | Ao organizar múltiplas mudanças |
| `validate-testing` | Antes de completar uma feature |
| `fresh-context` | Sessão longa (>150k tokens) ou handoff |
| `update-docs` | Após mudanças de arquitetura/API |
| `validate-docs-links` | Periodicamente ou após mover docs |
| `audit-architecture` | A cada 2-3 semanas |

## Rules (Detalhes Técnicos)

- `rules/code-quality-standards.md` — padrões de qualidade Python
- `rules/testing-requirements.md` — requisitos de testes e cobertura
- `rules/security-best-practices.md` — segurança e secrets

## Referências

- [README.md](../README.md) — visão geral do projeto
- [docs/API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md) — documentação da API
- [docs/ESTRUTURA_SAIDA.md](../docs/ESTRUTURA_SAIDA.md) — formato do JSON de saída
- [CONTRIBUTING.md](../CONTRIBUTING.md) — guia de contribuição
