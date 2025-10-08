# ⚙️ Setup do GitHub - Guia Rápido

Este guia mostra como configurar recursos do GitHub para aproveitar ao máximo o sistema de roadmap e planejamento do projeto.

---

## 📋 Checklist de Setup

- [ ] Criar labels padronizadas
- [ ] Configurar GitHub Projects (opcional)
- [ ] Habilitar GitHub Discussions (opcional)
- [ ] Configurar proteção de branch `main`
- [ ] Adicionar templates de issues e PRs (✅ já configurado)

---

## 🏷️ Criar Labels

### Opção 1: Usando GitHub CLI (Recomendado)

```bash
# Instale GitHub CLI se necessário
# macOS: brew install gh
# Windows: scoop install gh
# Linux: ver https://github.com/cli/cli#installation

# Autentique
gh auth login

# Navegue até o repositório
cd adalove_extract_cards_enhanced

# Crie labels a partir do arquivo
gh label create enhancement --description "Nova funcionalidade ou feature" --color "0E8A16"
gh label create bug --description "Algo não está funcionando" --color "D73A4A"
gh label create refactor --description "Refatoração de código existente" --color "8B4789"
gh label create documentation --description "Melhorias ou adições à documentação" --color "0075CA"
gh label create "technical-debt" --description "Débito técnico a ser resolvido" --color "795548"
gh label create testing --description "Relacionado a testes automatizados" --color "FBCA04"
gh label create performance --description "Melhorias de performance" --color "FF6D00"
gh label create security --description "Questões de segurança" --color "B60205"
gh label create dependencies --description "Atualização de dependências" --color "0366D6"
gh label create "priority:high" --description "Alta prioridade" --color "D93F0B"
gh label create "priority:medium" --description "Média prioridade" --color "FBCA04"
gh label create "priority:low" --description "Baixa prioridade" --color "0E8A16"
gh label create "v3.0.0" --description "Arquitetura Modular" --color "C5DEF5"
gh label create "v3.1.0" --description "Pipeline Resiliente" --color "C5DEF5"
gh label create "v3.2.0" --description "Configuração e CLI" --color "C5DEF5"
gh label create "v3.3.0" --description "Extração Seletiva" --color "C5DEF5"
gh label create "v4.0.0" --description "Qualidade e Garantias" --color "C5DEF5"
gh label create "status:blocked" --description "Bloqueado por outra issue ou decisão" --color "000000"
gh label create "status:in-progress" --description "Em desenvolvimento" --color "FBCA04"
gh label create "status:needs-review" --description "Precisa de revisão" --color "0075CA"
gh label create "good first issue" --description "Boa para iniciantes" --color "7057FF"
gh label create "help wanted" --description "Ajuda externa é bem-vinda" --color "008672"
gh label create question --description "Dúvida ou pedido de informação" --color "D876E3"
gh label create wontfix --description "Não será trabalhado" --color "FFFFFF"
gh label create duplicate --description "Issue ou PR duplicada" --color "CFD3D7"
gh label create "breaking-change" --description "Mudança que quebra compatibilidade" --color "D93F0B"
```

### Opção 2: Via Interface Web

1. Acesse: `https://github.com/SEU_USUARIO/adalove_extract_cards_enhanced/labels`
2. Clique em "New label" para cada label
3. Use cores e descrições do arquivo `.github/labels.yml`

---

## 🗂️ Configurar GitHub Projects

### 1. Criar Project Board

1. Acesse: `https://github.com/SEU_USUARIO/adalove_extract_cards_enhanced/projects`
2. Clique em "New project"
3. Escolha "Board" como template
4. Nomeie: "Adalove Roadmap"

### 2. Configurar Colunas

Crie as seguintes colunas:

```
📋 Backlog → 🔜 Next → 🔄 In Progress → ✅ Done
```

### 3. Adicionar Issues

- Crie issues baseadas nas features do ROADMAP.md
- Arraste para as colunas apropriadas
- Use labels para categorizar

### 4. Configurar Views (Opcional)

**View por Versão**:
- Agrupe por: Label (v3.0.0, v3.1.0, etc.)
- Ordene por: Prioridade

**View por Prioridade**:
- Agrupe por: Priority labels
- Ordene por: Data de criação

---

## 💬 Habilitar GitHub Discussions (Opcional)

### Por Que Usar?

- Discussões sobre arquitetura
- Perguntas da comunidade
- Ideias e feedback
- Separar issues (ação) de discussões (conversa)

### Como Habilitar

1. Acesse: `Settings` do repositório
2. Role até "Features"
3. Marque "Discussions"
4. Configure categorias:

```
📢 Announcements (somente mantenedores)
💡 Ideas (sugestões de features)
🙋 Q&A (perguntas e respostas)
🗣️ General (discussões gerais)
📊 Show and tell (compartilhar projetos/análises)
```

---

## 🔒 Configurar Proteção de Branch `main`

### Por Que?

- Evitar commits diretos em `main`
- Forçar revisão via PR
- Garantir que CI passa antes de merge

### Como Configurar

1. Acesse: `Settings` → `Branches`
2. Em "Branch protection rules", clique "Add rule"
3. Branch name pattern: `main`
4. Marque:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1 approval mínimo)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging (quando CI estiver configurado)
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings (para enforcement)

---

## 🤖 Configurar GitHub Actions (CI/CD) - Futuro

### Quando Implementar

Quando o projeto tiver:
- [ ] Testes automatizados (`pytest`)
- [ ] Linter configurado (`flake8`, `black`)
- [ ] Type checking (`mypy`)

### Exemplo de Workflow

Criar `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        playwright install chromium
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Check formatting with black
      run: |
        black --check .
    
    - name: Type check with mypy
      run: |
        mypy adalove_extractor.py
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 📊 Badges para README

Quando tiver CI/CD configurado, adicione badges ao README:

```markdown
![CI](https://github.com/SEU_USUARIO/adalove_extract_cards_enhanced/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/SEU_USUARIO/adalove_extract_cards_enhanced/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

---

## 🔗 Links Úteis

**GitHub CLI**:
- Instalação: https://cli.github.com/
- Documentação: https://cli.github.com/manual/

**GitHub Projects**:
- Guia: https://docs.github.com/en/issues/planning-and-tracking-with-projects

**GitHub Actions**:
- Documentação: https://docs.github.com/en/actions
- Marketplace: https://github.com/marketplace?type=actions

---

## ✅ Checklist Pós-Setup

Após configurar tudo:

- [ ] Labels criadas e organizadas
- [ ] Project board configurado (se escolheu usar)
- [ ] Branch protection ativa em `main`
- [ ] Templates de issues funcionando
- [ ] Template de PR funcionando
- [ ] README atualizado com links para ROADMAP, TODO, CONTRIBUTING
- [ ] Primeira issue criada a partir do ROADMAP

---

## 🎯 Próximos Passos

1. **Crie issues iniciais**:
   - Transforme features do ROADMAP.md em issues
   - Use templates apropriados
   - Adicione labels corretas

2. **Organize no Project**:
   - Adicione issues ao board
   - Priorize no backlog
   - Mova para "Next" o que vai trabalhar primeiro

3. **Comece a implementar**:
   - Escolha uma issue
   - Siga o fluxo do CONTRIBUTING.md
   - Abra PR quando pronto

---

**Última atualização**: 2025-10-08


