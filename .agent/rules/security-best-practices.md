# Security Best Practices

## Metadata

- **Versão:** 1.0.0
- **Status:** Ativo
- **Última atualização:** 19/Fevereiro/2026
- **Paths:** src/**/*.py, .env*

---

## Regra de Ouro

**"NUNCA commitar dados sensíveis no repositório."**

- **NUNCA** hardcodear credentials (tokens, senhas, API keys)
- **NUNCA** commitar `.env` ou `.token_cache`
- **NUNCA** logar tokens de autenticação Adalove
- **NUNCA** logar dados pessoais de alunos

---

## 1. Secrets Management

### Correto: pydantic-settings + .env

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    adalove_token: str = ""
    headless: bool = True
    output_dir: str = "output"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ADALOVE_",
    )
```

### Incorreto: Hardcoded

```python
# ❌ NUNCA
TOKEN = "eyJhbGciOiJSUzI1NiIs..."
```

### .env (NUNCA COMMITAR)

```bash
# .env — gitignored
ADALOVE_TOKEN=seu_token_real
```

### .env.example (COMMITAR)

```bash
# .env.example — sem valores reais
ADALOVE_TOKEN=seu_token_aqui
ADALOVE_HEADLESS=true
```

---

## 2. .gitignore — Arquivos Sensíveis

O `.gitignore` DEVE conter:

```gitignore
.env
.env.local
.token_cache
output/
logs/
*.log
data/
```

---

## 3. Logging Seguro

### Correto: Mascarar tokens

```python
# ✅
logger.info("Autenticação configurada: token=%s", "***" if token else "ausente")
logger.info("Extraindo cards da turma: %s", turma_id)

# ✅ Mascarar Authorization header
headers_log = {k: ("***" if k == "Authorization" else v) for k, v in headers.items()}
logger.debug("Request headers: %s", headers_log)
```

### Incorreto: Logar dados sensíveis

```python
# ❌
logger.info("Token: %s", token)
logger.info("Dados do aluno: %s", aluno_data)  # PII!
```

---

## 4. Error Handling Seguro

```python
# ✅ Mensagem genérica, log detalhado interno
try:
    response = requests.get(url, headers=auth_headers)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    logger.error("Erro HTTP %d ao acessar %s", e.response.status_code, url)
    raise ValueError("Erro ao acessar API Adalove") from e

# ❌ Expõe detalhes internos
except Exception as e:
    print(f"Erro: {e}")  # Pode expor URL com token!
```

---

## 5. Validação de Inputs

```python
# ✅ Validar turma_id antes de usar
def extract_turma(turma_id: str) -> dict:
    if not turma_id or not isinstance(turma_id, str):
        raise ValueError("turma_id deve ser string não-vazia")
    ...
```

---

## 6. Dados de Alunos (PII)

O projeto extrai dados de cards que podem conter nomes e informações de alunos:

- **Nunca** logar dados completos de resposta da API
- **Nunca** incluir dados de alunos em mensagens de erro
- **Output JSON** deve ser armazenado em `output/` (gitignored)
- **Fixtures de teste** devem usar dados fictícios

---

## Checklist de Segurança

Antes de cada commit:

- [ ] Nenhum token/senha hardcoded no diff
- [ ] `.env` e `.token_cache` não estão sendo commitados
- [ ] Logs não contêm tokens ou dados de alunos
- [ ] `.env.example` não tem valores reais
- [ ] Error messages não expõem detalhes internos
