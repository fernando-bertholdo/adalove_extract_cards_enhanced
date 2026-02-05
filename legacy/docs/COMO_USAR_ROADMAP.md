# 🗺️ Como Usar o Roadmap

Este guia explica como usar o sistema de planejamento do projeto para organizar e acompanhar o desenvolvimento.

---

## 📚 Arquivos de Planejamento

O projeto possui três níveis de planejamento:

### 1. **ROADMAP.md** - Visão de Longo Prazo
**Quando usar**: Features grandes, mudanças arquiteturais, planejamento de versões

**Conteúdo**:
- Features agrupadas por versões futuras (v3.0.0, v3.1.0, etc.)
- Descrição detalhada de cada feature
- Benefícios e motivação
- Priorização (Alta/Média/Baixa)
- Estimativas de tempo (Q1 2026, Q2 2026, etc.)

**Exemplo**:
```markdown
## [v3.1.0] - Pipeline Resiliente (Planejado)

### Features
- Sistema de checkpoints
- Retomada de execução
- Escrita incremental
```

---

### 2. **TODO.md** - Tarefas Técnicas Imediatas
**Quando usar**: Bugs, melhorias pontuais, tarefas técnicas rápidas

**Conteúdo**:
- Lista de tarefas técnicas (bugs, refactors, quick wins)
- Organizado por categoria (Bugs, Melhorias, Infraestrutura)
- Sem planejamento de versões
- Foco em ação imediata

**Exemplo**:
```markdown
## 🐛 Bugs Conhecidos
- [ ] Timeout em semanas com muitos cards (>50)
- [ ] Professor não detectado quando há múltiplos nomes
```

---

### 3. **GitHub Issues** - Execução e Discussão
**Quando usar**: Implementar qualquer feature ou bug, discussões técnicas

**Conteúdo**:
- Issues individuais para cada tarefa
- Discussão técnica nos comentários
- Rastreamento de progresso
- Linkadas a PRs (Pull Requests)

**Templates disponíveis**:
- 🚀 Feature Request
- 🐛 Bug Report
- 🔧 Refactoring
- 📚 Documentation

---

## 🔄 Fluxo de Trabalho

### Para adicionar uma nova feature:

#### 1️⃣ **Adicione ao ROADMAP.md**
```markdown
## [v3.X.0] - Nome da Versão

### Feature: Nome da Feature
**Prioridade**: 🔴 Alta

**Descrição**: ...
**Benefícios**: ...
**Implementação**: ...
```

#### 2️⃣ **Crie uma Issue no GitHub**
- Use o template "🚀 Feature Request"
- Referencie a seção do ROADMAP
- Adicione labels apropriadas (`enhancement`, `v3.x.0`)
- Discuta implementação nos comentários

#### 3️⃣ **Implemente a Feature**
- Crie uma branch: `git checkout -b feature/nome-da-feature`
- Desenvolva seguindo os princípios do projeto
- Adicione testes
- Atualize documentação

#### 4️⃣ **Abra um Pull Request**
- Referencie a issue: `Closes #123`
- Descreva as mudanças
- Aguarde revisão

#### 5️⃣ **Atualize o CHANGELOG.md**
- Adicione entrada na versão correspondente
- Documente breaking changes (se houver)

---

### Para corrigir um bug:

#### 1️⃣ **Adicione ao TODO.md** (opcional)
```markdown
## 🐛 Bugs Conhecidos
- [ ] Descrição do bug
```

#### 2️⃣ **Crie uma Issue no GitHub**
- Use o template "🐛 Bug Report"
- Descreva passos para reproduzir
- Adicione logs e screenshots

#### 3️⃣ **Corrija e abra PR**
- Branch: `git checkout -b fix/nome-do-bug`
- Adicione teste que reproduz o bug
- Corrija o problema
- Abra PR referenciando a issue

---

## 📊 Acompanhamento de Progresso

### Usando GitHub Projects (Recomendado)

**Setup**:
1. Acesse: `github.com/seu-usuario/repo/projects`
2. Crie um Project Board
3. Adicione colunas: `📋 Backlog` → `🔄 In Progress` → `✅ Done`
4. Adicione issues ao board

**Visualização**:
```
📋 Backlog          🔄 In Progress       ✅ Done
─────────────       ─────────────        ──────────
Issue #1            Issue #5             Issue #2
Issue #3            Issue #6             Issue #4
Issue #7
```

---

## 🏷️ Sistema de Labels

Use labels para organizar issues:

| Label | Uso | Cor |
|-------|-----|-----|
| `enhancement` | Nova feature | 🟦 Azul |
| `bug` | Correção de bug | 🟥 Vermelho |
| `refactor` | Refatoração | 🟪 Roxo |
| `documentation` | Documentação | 📘 Azul claro |
| `technical-debt` | Débito técnico | 🟫 Marrom |
| `v3.0.0`, `v3.1.0` | Versão alvo | 🟩 Verde |
| `priority:high` | Alta prioridade | 🔴 Vermelho |
| `priority:medium` | Média prioridade | 🟡 Amarelo |
| `priority:low` | Baixa prioridade | 🟢 Verde |
| `good first issue` | Para iniciantes | 💚 Verde claro |

---

## 🎯 Princípios de Organização

### 1. **Roadmap = Visão**
- Foque em **O QUE** e **POR QUE**
- Descreva benefícios e motivação
- Organize por versões lógicas

### 2. **Issues = Execução**
- Foque em **COMO**
- Discussão técnica detalhada
- Rastreamento de progresso

### 3. **TODO = Ação Imediata**
- Tarefas pequenas e rápidas
- Bugs conhecidos
- Melhorias pontuais

### 4. **Não Duplique**
- Não repita a mesma informação em múltiplos lugares
- ROADMAP aponta para Issues
- Issues apontam para PRs
- PRs atualizam CHANGELOG

---

## 📝 Exemplo Completo

### Cenário: Implementar "Extração de Semanas Específicas"

#### 1. **ROADMAP.md**
```markdown
## [v3.3.0] - Extração Seletiva

### Feature: Extração de Semanas Específicas
**Prioridade**: 🔴 Alta

**Casos de uso**:
\`\`\`bash
adalove extract --turma modulo6 --weeks 1,3,7
adalove extract --turma modulo6 --weeks 1-5
\`\`\`

**Issues Relacionadas**: #45
```

#### 2. **GitHub Issue #45**
```markdown
# [FEATURE] Extração de Semanas Específicas

## Relação com Roadmap
- [x] Está no ROADMAP: [v3.3.0 - Extração Seletiva](link)

## Descrição
Permitir que usuário especifique quais semanas quer extrair...

## Implementação Proposta
1. Adicionar argumento `--weeks` ao CLI
2. Parser de expressões (1,3,7 ou 1-5)
3. Skip de semanas não solicitadas

## Critérios de Aceitação
- [ ] Aceita semanas individuais: `--weeks 1,3,7`
- [ ] Aceita intervalos: `--weeks 1-5`
- [ ] Aceita combinação: `--weeks 1-3,7,9-10`
- [ ] Valida semanas existentes
- [ ] Testes unitários para parser
```

#### 3. **TODO.md** (opcional)
```markdown
## 🎯 Quick Wins
- [ ] Implementar parser de expressões de semanas
- [ ] Adicionar flag `--weeks` ao CLI
```

#### 4. **Desenvolvimento**
```bash
git checkout -b feature/selective-week-extraction
# ... desenvolvimento ...
git commit -m "feat: add --weeks flag for selective extraction"
git push origin feature/selective-week-extraction
```

#### 5. **Pull Request**
```markdown
# Add selective week extraction

Closes #45

## Changes
- Added `--weeks` CLI argument
- Implemented expression parser
- Added unit tests
- Updated documentation

## Testing
\`\`\`bash
pytest tests/test_week_parser.py
adalove extract --turma modulo6 --weeks 1,3,7
\`\`\`
```

#### 6. **CHANGELOG.md**
```markdown
## [v3.3.0] - 2026-06-15

### Added
- **Extração seletiva de semanas** (#45)
  - Argumento `--weeks` aceita semanas individuais, intervalos e combinações
  - Exemplos: `--weeks 1,3,7` ou `--weeks 1-5`
```

---

## 🤝 Dicas para Contribuidores

### ✅ Boas Práticas

1. **Antes de implementar**:
   - Verifique ROADMAP para entender o contexto
   - Crie ou comente em issue existente
   - Discuta a abordagem

2. **Durante desenvolvimento**:
   - Mantenha escopo focado (uma feature por vez)
   - Adicione testes
   - Atualize documentação
   - Faça commits semânticos

3. **Após implementação**:
   - Marque issue como completa no TODO.md
   - Adicione entrada no CHANGELOG.md
   - Considere atualizar ROADMAP se houver mudanças

### ❌ Evite

- ❌ Implementar features não documentadas
- ❌ Fazer PRs sem issue associada
- ❌ Ignorar testes e documentação
- ❌ Fazer breaking changes sem discussão

---

## 📞 Suporte

**Dúvidas sobre o roadmap?**
- Abra uma issue com label `question`
- Referencie a seção do ROADMAP que não está clara

**Quer sugerir uma nova feature?**
- Use o template "🚀 Feature Request"
- Explique o problema que resolve
- Proponha onde deveria entrar no ROADMAP

---

**Última atualização**: 2025-10-08


