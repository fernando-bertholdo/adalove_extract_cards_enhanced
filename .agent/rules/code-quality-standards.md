# Code Quality Standards

## Metadata

- **Versão:** 1.0.0
- **Status:** Ativo
- **Última atualização:** 19/Fevereiro/2026
- **Paths:** src/**/*.py, tests/**/*.py

---

## Escopo

Padrões de qualidade para código Python no projeto adalove_extract_cards_enhanced.

---

## Quando Aplicar Esta Regra

**SEMPRE**, em qualquer mudança em `src/` e/ou `tests/`:
- Todo novo código
- Refatorações
- Correções de bugs
- Antes de commits (via `pre-commit-check`)

---

## Padrões Obrigatórios

### 1) Formatação (PEP 8) e Imports

```bash
ruff format src/ tests/
ruff check src/ tests/ --fix
```

- Linha máxima: **100 caracteres**
- Config centralizada em `pyproject.toml`

### 2) Type Hints

Toda função/classe pública deve ter type hints. Funções internas não-triviais também.

```python
# ✅
def extract_cards(turma_id: str, token: str) -> list[dict]:
    ...

# ❌
def extract_cards(turma_id, token):
    ...
```

### 3) Docstrings (Google Style)

```python
# ✅
def enrich_card(card: dict, anchor_data: dict) -> EnrichedCard:
    """Enriquece um card com dados de âncora.

    Args:
        card: Card bruto da API Adalove.
        anchor_data: Dados de âncora para enriquecimento.

    Returns:
        Card enriquecido com campos normalizados.

    Raises:
        ValueError: Se card não tem campos obrigatórios.
    """
```

### 4) Naming Conventions

- `snake_case` para variáveis e funções
- `PascalCase` para classes (`CardExtractor`, `EnrichedCard`)
- `UPPER_SNAKE_CASE` para constants (`MAX_RETRIES`, `API_BASE_URL`)

### 5) Error Handling

- Prefira exceptions específicas (`ValueError`, `ConnectionError`)
- Evite `except Exception` genérico
- Logue quando capturar e decidir seguir

```python
# ✅
try:
    response = client.get_cards(turma_id)
except requests.exceptions.Timeout:
    logger.error("Timeout ao buscar cards da turma %s", turma_id)
    raise

# ❌
try:
    response = client.get_cards(turma_id)
except Exception:
    pass
```

### 6) Logging

- Obrigatório em todo módulo: `logger = logging.getLogger(__name__)`
- **Nunca** `print()` (exceto no CLI para output intencional via Rich)
- Logar: início/fim de operações, contagens, resultado, chamadas externas
- **Nunca** logar: tokens, senhas, dados pessoais de alunos

### 7) Constants Nomeadas

```python
# ✅
MAX_RETRIES = 3
CHECKPOINT_INTERVAL = 50

# ❌
for _ in range(3):  # magic number
```

---

## Checklist de Code Review

- [ ] Formatado com `ruff format`
- [ ] Type hints em funções públicas
- [ ] Docstrings Google style em classes e funções públicas
- [ ] Logging presente (sem `print()`)
- [ ] Nenhum secret hardcoded
- [ ] Constants nomeadas (sem magic numbers)
- [ ] Error handling específico

---

## Comandos

```bash
# Antes de commit
ruff format src/ tests/
ruff check src/ tests/ --fix
pytest -q
```
