# Testing Requirements

## Metadata

- **Versão:** 1.0.0
- **Status:** Ativo
- **Última atualização:** 19/Fevereiro/2026
- **Paths:** tests/**/*.py

---

## Quando Aplicar

**SEMPRE:**
- Toda funcionalidade nova precisa de testes
- Todo bug fix deve reproduzir o bug em teste primeiro
- Refatorações devem manter testes passando

**NUNCA:**
- Pular testes porque "é simples"
- Testar apenas o "happy path"
- Commitar código sem testes

---

## Cobertura Mínima

| Tipo de Código | Meta | Exemplos |
|----------------|------|----------|
| Core business logic | >90% | `extractors/`, `enrichment/` |
| API/integrações | >80% | `api/client.py`, `api/auth.py` |
| IO/writers | >80% | `io/writers.py`, `io/checkpoint.py` |
| Utilitários | >80% | `utils/hash.py`, `utils/text.py` |
| **Overall** | **>80%** | Todo o `src/adalove_extractor/` |

---

## Estrutura de Testes

```
tests/
├── test_checkpoint_manager.py         # Testes de checkpoint
├── test_incremental_writer.py         # Testes de escrita incremental
├── test_integration_checkpoint_flow.py # Integração de checkpoint
└── test_recovery_manager.py           # Testes de recovery
```

### Naming Convention

Formato: `test_<function>_<scenario>_<expected>`

```python
def test_extract_cards_turma_valida_retorna_lista():
    """Testa extração com turma válida."""
    ...

def test_extract_cards_turma_inexistente_retorna_vazio():
    """Testa extração com turma que não existe."""
    ...
```

---

## AAA Pattern (Arrange-Act-Assert)

```python
def test_normalize_card_com_campos_completos():
    """Testa normalização de card com todos os campos."""
    # Arrange
    card_raw = {"id": "123", "titulo": "Teste", "tipo": "autoestudo"}

    # Act
    result = normalize_card(card_raw)

    # Assert
    assert result.id == "123"
    assert result.tipo == "autoestudo"
```

---

## Mocks (Dependências Externas)

Para testes que dependem da API Adalove:

```python
from unittest.mock import patch

def test_get_cards_api_timeout_retorna_none():
    """Testa comportamento quando API da Adalove dá timeout."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        result = client.get_cards("turma_123")
    assert result is None
```

---

## Testes Parametrizados

```python
@pytest.mark.parametrize("tipo,esperado", [
    ("autoestudo", "Autoestudo"),
    ("instrucao", "Instrução"),
    ("ponderada", "Atividade Ponderada"),
])
def test_normalize_tipo(tipo, esperado):
    assert normalize_tipo(tipo) == esperado
```

---

## Execução

```bash
# Todos os testes
pytest -q

# Com cobertura
pytest --cov=src/adalove_extractor --cov-report=term-missing

# Teste específico
pytest tests/test_checkpoint_manager.py -v

# Parar no primeiro erro
pytest -x
```
