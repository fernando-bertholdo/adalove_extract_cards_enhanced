# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o **Adalove Extract Cards Enhanced**! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

- [Como Posso Contribuir?](#-como-posso-contribuir)
- [Processo de Desenvolvimento](#-processo-de-desenvolvimento)
- [Padrões de Código](#-padrões-de-código)
- [Commits e Mensagens](#-commits-e-mensagens)
- [Pull Requests](#-pull-requests)
- [Reportar Bugs](#-reportar-bugs)
- [Sugerir Features](#-sugerir-features)
- [Perguntas e Suporte](#-perguntas-e-suporte)

---

## 🎯 Como Posso Contribuir?

Existem várias formas de contribuir:

### 1. 🐛 Reportar Bugs
- Use o template de [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
- Forneça informações detalhadas para reprodução
- Inclua logs e screenshots quando relevante

### 2. ✨ Sugerir Features
- Use o template de [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
- Consulte o [ROADMAP.md](./ROADMAP.md) antes
- Explique o problema que a feature resolve

### 3. 📚 Melhorar Documentação
- Use o template de [Documentation](.github/ISSUE_TEMPLATE/documentation.md)
- Corrija typos, melhore exemplos, adicione clareza
- Documentação é tão importante quanto código!

### 4. 🔧 Contribuir com Código
- Implemente features do roadmap
- Corrija bugs conhecidos
- Melhore performance ou qualidade do código

### 5. 🧪 Adicionar Testes
- Aumente cobertura de testes
- Adicione casos de teste que faltam
- Melhore robustez da suite de testes

---

## 🔄 Processo de Desenvolvimento

### 1. Fork e Clone

```bash
# Fork via GitHub UI, depois:
git clone https://github.com/SEU_USUARIO/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced

# Adicione upstream
git remote add upstream https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
```

### 2. Configure o Ambiente

```bash
# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Instale dependências de desenvolvimento
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instale Playwright
playwright install chromium

# Configure credenciais
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Crie uma Branch

```bash
# Mantenha main atualizada
git checkout main
git pull upstream main

# Crie branch para sua feature/fix
git checkout -b tipo/nome-descritivo

# Exemplos:
# git checkout -b feature/selective-week-extraction
# git checkout -b fix/timeout-on-large-weeks
# git checkout -b docs/improve-installation-guide
# git checkout -b refactor/modularize-enrichment
```

**Convenção de nomes de branch**:
- `feature/` - Nova funcionalidade
- `fix/` - Correção de bug
- `docs/` - Documentação
- `refactor/` - Refatoração
- `test/` - Adição de testes
- `chore/` - Manutenção (deps, config, etc.)

### 4. Desenvolva

```bash
# Faça suas alterações
# Teste localmente
# Adicione testes
# Atualize documentação
```

### 5. Commit

```bash
git add .
git commit -m "tipo: descrição curta"

# Exemplos de mensagens:
# feat: add --weeks flag for selective extraction
# fix: handle timeout on large weeks
# docs: improve installation guide
# refactor: modularize enrichment functions
# test: add tests for week parser
```

Ver [Commits e Mensagens](#-commits-e-mensagens) para detalhes.

### 6. Push e PR

```bash
# Push para seu fork
git push origin tipo/nome-descritivo

# Abra PR via GitHub UI
```

---

## 📝 Padrões de Código

### Python Style

Seguimos **PEP 8** com algumas adaptações:

```python
# ✅ BOM
def extract_cards(week: int, turma: str) -> list[Card]:
    """
    Extrai cards de uma semana específica.
    
    Args:
        week: Número da semana (1-10)
        turma: Nome da turma
        
    Returns:
        Lista de cards extraídos
    """
    cards = []
    # ... implementação ...
    return cards


# ❌ EVITAR
def extractCards(week,turma):
    cards=[]
    # ... sem documentação ...
    return cards
```

### Princípios

1. **Clareza > Concisão**: Código explícito é melhor que implícito
2. **Type Hints**: Sempre adicione em funções públicas
3. **Docstrings**: Documente o "porquê", não o "o que"
4. **Comentários**: Em português, explicando lógica complexa
5. **Constantes**: UPPER_CASE, extraídas para topo do arquivo
6. **Funções**: Pequenas e focadas (idealmente < 50 linhas)

### Formatação

**Recomendamos**:
- `black` para formatação automática
- `isort` para organizar imports
- `flake8` para linting
- `mypy` para type checking

```bash
# Formatar código
black adalove_extractor.py

# Organizar imports
isort adalove_extractor.py

# Verificar style
flake8 adalove_extractor.py

# Type checking
mypy adalove_extractor.py
```

### Estrutura de Arquivo

```python
"""
Descrição do módulo.

Explicação mais detalhada se necessário.
"""

# Imports da biblioteca padrão
import os
import sys
from datetime import datetime

# Imports de terceiros
from playwright.sync_api import Page, sync_playwright
import pandas as pd

# Imports locais (quando modularizado)
from .models import Card
from .utils import normalize_text

# Constantes
MAX_RETRIES = 3
TIMEOUT_MS = 30000

# Classes e funções
class ExtractorEngine:
    """Motor de extração de cards."""
    
    def __init__(self):
        """Inicializa o motor."""
        pass
```

---

## 💬 Commits e Mensagens

### Formato (Conventional Commits)

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova feature | `feat: add --weeks flag` |
| `fix` | Correção de bug | `fix: handle timeout on large weeks` |
| `docs` | Documentação | `docs: improve installation guide` |
| `style` | Formatação | `style: apply black formatting` |
| `refactor` | Refatoração | `refactor: extract card parser` |
| `test` | Testes | `test: add tests for enrichment` |
| `chore` | Manutenção | `chore: update dependencies` |
| `perf` | Performance | `perf: optimize card extraction` |

### Exemplos Completos

#### Feature
```
feat(cli): add --weeks argument for selective extraction

Implements selective week extraction allowing users to specify
which weeks to extract using formats like "1,3,7" or "1-5".

Closes #45
```

#### Bug Fix
```
fix(enrichment): handle cards without date/time

Cards without explicit date/time now fallback to week start date
instead of crashing the enrichment process.

Fixes #78
```

#### Documentation
```
docs: add troubleshooting section to README

Added common errors and solutions based on user feedback.
```

### Boas Práticas

- ✅ Use imperativo ("add" não "added" ou "adds")
- ✅ Primeira letra minúscula
- ✅ Sem ponto final na descrição
- ✅ Limite de 50 caracteres na primeira linha
- ✅ Corpo opcional com mais detalhes (limite 72 chars/linha)
- ✅ Referencie issues quando relevante (`Closes #123`, `Fixes #45`)

---

## 🔀 Pull Requests

### Antes de Abrir um PR

**Checklist**:
- [ ] Branch está atualizada com `main`
- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados e passando
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado (se relevante)
- [ ] Sem conflitos com `main`

### Título do PR

Siga o mesmo formato de commits:

```
feat: add selective week extraction
fix: handle timeout on large weeks
docs: improve installation guide
```

### Descrição do PR

Use o [template de PR](.github/PULL_REQUEST_TEMPLATE.md) que será preenchido automaticamente.

**Elementos essenciais**:
1. **Descrição clara** do que muda
2. **Motivação** (por que é necessário)
3. **Como foi testado**
4. **Checklist completo**
5. **Screenshots** (se aplicável)

### Processo de Revisão

1. **CI Checks**: Aguarde pipelines passarem (quando implementado)
2. **Revisão de código**: Responda a comentários construtivamente
3. **Mudanças solicitadas**: Faça commits adicionais na mesma branch
4. **Aprovação**: Aguarde aprovação de um mantenedor
5. **Merge**: Mantenedor fará o merge

### Etiqueta de Revisão

- ✅ Seja receptivo a feedback
- ✅ Faça perguntas se não entender
- ✅ Explique decisões de design quando questionado
- ✅ Mantenha discussões técnicas focadas
- ❌ Não leve feedback como pessoal

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. **Verifique se é realmente um bug** (não um problema de configuração)
2. **Procure em issues existentes** para evitar duplicatas
3. **Teste na versão mais recente**
4. **Colete informações** do ambiente (OS, Python, logs)

### Como Reportar

Use o [template de Bug Report](.github/ISSUE_TEMPLATE/bug_report.md).

**Informações essenciais**:
- Descrição clara do problema
- Passos para reproduzir (detalhados!)
- Comportamento esperado vs atual
- Ambiente (OS, Python, versão do projeto)
- Logs relevantes
- Screenshots (se aplicável)

**Exemplo de bom report**:

```markdown
## Descrição
Extração falha com timeout ao processar semanas com mais de 50 cards.

## Passos para Reproduzir
1. Execute: `python adalove_extractor.py`
2. Digite turma: `modulo6`
3. Selecione turma na interface
4. Aguarde chegar na semana 7 (67 cards)
5. Observe timeout após 30 segundos

## Comportamento Esperado
Extração deveria completar mesmo com muitos cards.

## Comportamento Atual
Erro: `playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded.`

## Ambiente
- OS: macOS 14.0
- Python: 3.11.5
- Projeto: v2.0.0
- Playwright: 1.49.1

## Logs
[Anexar arquivo de log completo]
```

---

## ✨ Sugerir Features

### Antes de Sugerir

1. **Verifique o [ROADMAP.md](./ROADMAP.md)** - pode já estar planejado
2. **Procure em issues** - pode já ter sido sugerido
3. **Considere escopo** - a feature faz sentido para o projeto?

### Como Sugerir

Use o [template de Feature Request](.github/ISSUE_TEMPLATE/feature_request.md).

**Elementos essenciais**:
1. **Problema que resolve** (o "porquê")
2. **Solução proposta** (o "como")
3. **Critérios de aceitação**
4. **Relação com roadmap**
5. **Alternativas consideradas**

**Exemplo de boa sugestão**:

```markdown
## Problema que Resolve
Atualmente não é possível extrair apenas semanas específicas, 
forçando extração completa mesmo quando só preciso de dados 
de algumas semanas.

## Solução Proposta
Adicionar argumento `--weeks` ao CLI:

\`\`\`bash
adalove extract --turma modulo6 --weeks 1,3,7
adalove extract --turma modulo6 --weeks 1-5
\`\`\`

## Critérios de Aceitação
- [ ] Aceita semanas individuais
- [ ] Aceita intervalos
- [ ] Valida semanas existentes
- [ ] Testes unitários

## Relação com Roadmap
Esta feature está prevista em v3.3.0 do ROADMAP.

## Alternativas
- Extrair tudo e filtrar depois (ineficiente)
- Executar múltiplas vezes (trabalhoso)
```

---

## ❓ Perguntas e Suporte

### Onde Pedir Ajuda

1. **Dúvidas de uso**: Abra issue com label `question`
2. **Problemas técnicos**: Use template de Bug Report
3. **Discussões**: Use GitHub Discussions (se habilitado)

### Não Sabe Por Onde Começar?

Procure issues com labels:
- `good first issue` - Boas para iniciantes
- `help wanted` - Ajuda é bem-vinda
- `documentation` - Melhorias de docs (menos complexo)

---

## 🏆 Reconhecimento

Todos os contribuidores são reconhecidos:
- Mencionados em releases
- Listados no README (para contribuições significativas)
- Agradecimentos no CHANGELOG

---

## 📚 Recursos Úteis

### Documentação do Projeto
- [README.md](./README.md) - Visão geral
- [ROADMAP.md](./ROADMAP.md) - Planejamento futuro
- [CHANGELOG.md](./CHANGELOG.md) - Histórico de mudanças
- [TODO.md](./TODO.md) - Tarefas técnicas
- [documents/](./documents/) - Documentação detalhada

### Guias Externos
- [Conventional Commits](https://www.conventionalcommits.org/pt-br/)
- [Keep a Changelog](https://keepachangelog.com/pt-BR/)
- [Semantic Versioning](https://semver.org/lang/pt-BR/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)

---

## 📜 Código de Conduta

### Nossos Princípios

1. **Respeito**: Trate todos com respeito e empatia
2. **Inclusão**: Bem-vindo a pessoas de todas as origens
3. **Colaboração**: Trabalhe junto construtivamente
4. **Qualidade**: Mantenha altos padrões de código e documentação

### Comportamentos Esperados

✅ Uso de linguagem acolhedora e inclusiva  
✅ Respeito a diferentes pontos de vista  
✅ Aceitação graciosa de crítica construtiva  
✅ Foco no que é melhor para a comunidade  

### Comportamentos Inaceitáveis

❌ Assédio ou comentários depreciativos  
❌ Trolling ou ataques pessoais  
❌ Conduta não profissional  
❌ Violação de privacidade  

---

## 📞 Contato

**Mantenedor**: Fernando Bertholdo

**Dúvidas?** Abra uma issue com label `question`.

---

**Obrigado por contribuir! 🎉**

Cada contribuição, grande ou pequena, é valiosa para o projeto.


