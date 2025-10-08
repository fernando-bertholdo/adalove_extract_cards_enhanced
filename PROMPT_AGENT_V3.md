# 🤖 Prompt para Background Agent - Desenvolvimento v3.0.0 a v3.3.0

## 📋 Contexto do Projeto

Você assumirá o desenvolvimento do **Adalove Extract Cards Enhanced**, um sistema Python de extração automatizada de cards educacionais da plataforma AdaLove, com enriquecimento inteligente de dados.

**Estado atual**: v2.0.0 (script monolítico funcional com 1.018 linhas, enriquecimento de 30 campos)

**Seu objetivo**: Implementar versões v3.0.0 a v3.3.0 conforme roadmap detalhado.

---

## 🎯 Missão Principal

Transformar script monolítico em **sistema modular, resiliente e configurável** com extração seletiva de dados.

**Deliverables esperados**:
1. ✅ v3.0.0 - Arquitetura modular (pacote Python profissional)
2. ✅ v3.1.0 - Pipeline resiliente (checkpoints, retomada, idempotência)
3. ✅ v3.2.0 - CLI completa (Typer, flags, configuração)
4. ✅ v3.3.0 - Extração seletiva (semanas e frentes específicas)

---

## 📚 Documentação Crítica

Leia primeiro (ordem de prioridade):
1. `ROADMAP.md` - Seções v3.0.0 a v3.3.0 (linhas 49-333)
2. `CONTRIBUTING.md` - Padrões de código e commits
3. `adalove_extractor.py` - Código atual (1.018 linhas)
4. `ENRIQUECIMENTO.md` - Sistema de ancoragem (crítico preservar)

---

## 🏗️ v3.0.0 - Arquitetura Modular (PRIORIDADE 1)

### Objetivo
Refatorar script monolítico em pacote Python com separação clara de responsabilidades.

### Estrutura Alvo
```
adalove_extractor/
├── __init__.py
├── cli/              # Interface linha de comando
├── config/           # Configuração (Pydantic Settings)
├── browser/          # Playwright (auth, navegação)
├── extractors/       # Extração (semana, card)
├── enrichment/       # Enriquecimento puro (normalização, ancoragem)
├── io/               # CSV/JSONL/Parquet writers
├── models/           # Card, EnrichedCard (dataclasses/Pydantic)
└── utils/            # Hash, text manipulation
```

### Tarefas Específicas
- [ ] Criar estrutura de pacote com `__init__.py` em cada módulo
- [ ] Extrair lógica de autenticação para `browser/auth.py`
- [ ] Extrair navegação Kanban para `browser/navigator.py`
- [ ] Criar modelos `Card` e `EnrichedCard` com Pydantic
- [ ] Modularizar sistema de enriquecimento (preservar ancoragem!)
- [ ] Criar writers para CSV/JSONL em `io/writers.py`
- [ ] Mover configurações para `config/settings.py` (Pydantic Settings)
- [ ] Setup `pyproject.toml` ou `setup.py` para instalação

### ⚠️ Crítico
- **NÃO QUEBRAR** lógica de ancoragem existente (funções `_title_similarity`, `_guess_professor`, etc.)
- **PRESERVAR** formato de saída atual (compatibilidade retroativa)
- **ADICIONAR** type hints em todas funções
- **DOCUMENTAR** cada módulo com docstrings

---

## 🔄 v3.1.0 - Pipeline Resiliente (PRIORIDADE 2)

### Objetivo
Adicionar sistema de checkpoints para retomar execuções interrompidas.

### Features Principais

#### 1. Sistema de Checkpoints
```python
# Arquivo: .checkpoint.json
{
  "turma": "modulo6",
  "execution_id": "20250826_220413",
  "last_completed_week": 7,
  "last_completed_card_id": "card_123",
  "total_cards_extracted": 89,
  "timestamp": "2025-08-26T22:04:13Z",
  "status": "interrupted"
}
```

#### 2. Escrita Incremental
- Salvar cards conforme extraídos (não só no final)
- JSONL append-only
- CSV com append mode

#### 3. Idempotência
- Usar `record_hash` como chave única
- Manter mapa de hashes processados
- Skip de cards já extraídos

### Tarefas Específicas
- [ ] Criar `io/checkpoint.py` com save/load de estado
- [ ] Modificar extrator para salvar após cada semana
- [ ] Implementar flag `--resume` no CLI
- [ ] Adicionar detecção automática de checkpoint existente
- [ ] Implementar escrita incremental em JSONL
- [ ] Criar sistema de cache de hashes (`processed_hashes.json`)

---

## ⚙️ v3.2.0 - CLI Completa (PRIORIDADE 3)

### Objetivo
Interface profissional com Typer e configuração via arquivo.

### CLI Desejada
```bash
# Básico
adalove extract --turma modulo6

# Avançado
adalove extract --turma modulo7 --headless --no-interactive

# Retomar
adalove extract --resume

# Configurado
adalove extract --config adalove.toml
```

### Tarefas Específicas
- [ ] Instalar e configurar Typer
- [ ] Criar comando `extract` com argumentos:
  * `--turma` (required)
  * `--headless` (flag)
  * `--no-interactive` (flag)
  * `--resume` (flag)
  * `--output` (path)
  * `--log-level` (choice: DEBUG, INFO, WARNING)
- [ ] Implementar leitura de `adalove.toml` (ou pyproject.toml)
- [ ] Mover configurações hardcoded para arquivo
- [ ] Adicionar `--version` flag
- [ ] Criar help messages descritivos

### Arquivo de Configuração
```toml
[adalove]
default_output_dir = "dados_extraidos"
headless = true
interactive = true

[adalove.extraction]
max_retries = 3
timeout_seconds = 30

[adalove.enrichment]
enable_anchoring = true
anchor_confidence_threshold = 0.6
```

---

## 🎯 v3.3.0 - Extração Seletiva (PRIORIDADE 4)

### Objetivo
Permitir extração granular de semanas e frentes específicas.

### Features

#### 1. Semanas Específicas
```bash
# Semana única
adalove extract --turma modulo6 --weeks 5

# Múltiplas
adalove extract --turma modulo6 --weeks 1,3,7

# Intervalo
adalove extract --turma modulo6 --weeks 1-5

# Combinado
adalove extract --turma modulo6 --weeks 1-3,7,9-10
```

#### 2. Frentes Específicas
```bash
# Frente única
adalove extract --turma modulo6 --frentes "Programação"

# Múltiplas
adalove extract --turma modulo6 --frentes "Programação,Matemática"
```

### Tarefas Específicas
- [ ] Implementar parser de expressões de semanas (`1,3,7` e `1-5`)
- [ ] Validar semanas contra disponíveis
- [ ] Skip de semanas não solicitadas no loop
- [ ] Implementar detecção de frente por:
  * Professor (mapping)
  * Palavras-chave no título
  * Tags no HTML
- [ ] Filtrar cards por frente após extração
- [ ] Adicionar flags `--weeks` e `--frentes` ao CLI
- [ ] Criar testes para parser de semanas

---

## 🎨 Padrões de Código (OBRIGATÓRIO)

### Python Style
```python
# ✅ Correto
def extract_cards(week: int, turma: str) -> list[Card]:
    """
    Extrai cards de uma semana específica.
    
    Args:
        week: Número da semana (1-10)
        turma: Nome da turma
        
    Returns:
        Lista de cards extraídos
    """
    cards: list[Card] = []
    # implementação...
    return cards

# ❌ Evitar
def extractCards(week,turma):
    cards=[]
    return cards
```

### Commits
```bash
# Formato: <tipo>(<escopo>): <descrição>

# Exemplos:
feat(cli): add --weeks flag for selective extraction
fix(enrichment): handle cards without date/time
refactor(extractors): modularize card extraction logic
docs(readme): update installation guide
test(enrichment): add tests for title similarity
```

### Princípios
1. **Type hints** em todas funções públicas
2. **Docstrings** em formato Google/NumPy
3. **Testes** para cada módulo novo (`pytest`)
4. **Documentação** atualizada (README, ROADMAP)
5. **CHANGELOG** atualizado em cada versão

---

## ✅ Critérios de Sucesso

### v3.0.0 - Modular
- [ ] Código organizado em pacote com camadas claras
- [ ] Instalável via `pip install -e .`
- [ ] Import funciona: `from adalove_extractor import Card`
- [ ] Todos imports relativos corretos
- [ ] Testes passam (mínimo 50% cobertura)

### v3.1.0 - Resiliente
- [ ] Checkpoint salvo após cada semana
- [ ] Flag `--resume` funciona corretamente
- [ ] Escrita incremental em JSONL
- [ ] Idempotência: rodar 2x produz mesmo resultado
- [ ] Teste: interromper e retomar extração

### v3.2.0 - CLI
- [ ] Comando `adalove extract` funcional
- [ ] `--help` mostra todas opções
- [ ] Configuração via `adalove.toml`
- [ ] Flags: `--headless`, `--no-interactive`, `--resume`
- [ ] Logs configuráveis por nível

### v3.3.0 - Seletiva
- [ ] `--weeks 1,3,7` funciona
- [ ] `--weeks 1-5` funciona
- [ ] `--frentes "Programação"` funciona
- [ ] Validação de semanas inválidas
- [ ] Testes para parser de expressões

---

## ⚠️ Restrições e Cuidados

### NÃO FAZER
❌ Remover funcionalidades existentes sem equivalente  
❌ Quebrar formato de saída (CSV/JSONL)  
❌ Modificar lógica de ancoragem sem preservar comportamento  
❌ Commits diretos em `main` (usar PRs)  
❌ Ignorar testes  

### SEMPRE FAZER
✅ Criar branch por feature (`feature/nome`)  
✅ Adicionar testes para código novo  
✅ Atualizar documentação  
✅ Preservar compatibilidade retroativa  
✅ Usar type hints e docstrings  

---

## 📦 Dependências Permitidas

**Core**:
- `playwright` (já existe)
- `python-dotenv` (já existe)
- `typer` (adicionar para CLI)
- `pydantic` (adicionar para models/config)
- `pydantic-settings` (config)

**Dev**:
- `pytest` (testes)
- `pytest-cov` (cobertura)
- `black` (formatação)
- `isort` (imports)
- `mypy` (type checking)

**Opcional**:
- `pyarrow` (se implementar Parquet)
- `rich` (CLI visual aprimorada)

---

## 🚀 Fluxo de Trabalho Recomendado

```bash
# Para cada versão (v3.X.0)

1. Criar branch
git checkout -b feature/v3.X.0-nome

2. Implementar conforme ROADMAP.md

3. Adicionar testes
pytest tests/ -v --cov

4. Documentar
# Atualizar docstrings, README, etc.

5. Commit
git commit -m "feat(modulo): implementa feature X"

6. PR e merge
# Após revisão

7. Atualizar CHANGELOG.md
# Adicionar entrada na versão v3.X.0

8. Tag release
git tag v3.X.0
git push origin v3.X.0
```

---

## 📊 Métricas de Qualidade Esperadas

| Métrica | Meta |
|---------|------|
| Cobertura de testes | > 60% |
| Type hints | 100% em funções públicas |
| Docstrings | 100% em classes/funções públicas |
| Linhas por função | < 50 (idealmente) |
| Complexidade ciclomática | < 10 |

---

## 🆘 Troubleshooting

### Se algo quebrar
1. **Preservar funcionalidade**: Sempre manter script original funcionando
2. **Testes de regressão**: Comparar output antes/depois
3. **Documentar breaking changes**: No CHANGELOG com path de migração

### Recursos de Ajuda
- `ROADMAP.md` - Detalhes técnicos completos
- `CONTRIBUTING.md` - Padrões e processo
- `adalove_extractor.py` - Código atual (referência)
- `ENRIQUECIMENTO.md` - Sistema de ancoragem
- Issues no GitHub - Discussões técnicas

---

## 📞 Contato e Revisão

**Mantenedor**: Fernando Bertholdo

**Revisão esperada**:
- Code review em cada PR
- Discussão de decisões arquiteturais
- Validação de testes

---

## 🎯 TL;DR - Quick Start

```bash
# 1. Ler documentação base
cat ROADMAP.md | grep -A 100 "v3.0.0"

# 2. Entender código atual
less adalove_extractor.py

# 3. Começar v3.0.0
git checkout -b feature/v3.0.0-modular-architecture
mkdir -p adalove_extractor/{cli,config,browser,extractors,enrichment,io,models,utils}

# 4. Implementar, testar, documentar

# 5. Seguir para v3.1.0, v3.2.0, v3.3.0
```

---

**Boa sorte! 🚀 O roadmap está bem definido, basta seguir passo a passo.**

Ver `ROADMAP.md` para detalhes completos de cada versão.

