# 📐 Estrutura de Roadmap e Planejamento - Visão Geral

Este documento fornece uma visão completa do sistema de planejamento implementado no projeto.

---

## 📂 Arquivos Criados

### Raiz do Projeto

```
adalove_extract_cards_enhanced/
├── ROADMAP.md              ← Visão de longo prazo (features por versão)
├── TODO.md                 ← Tarefas técnicas imediatas
├── CONTRIBUTING.md         ← Guia para contribuidores
└── README.md (atualizado)  ← Com seção de Roadmap
```

### GitHub Templates

```
.github/
├── ISSUE_TEMPLATE/
│   ├── feature_request.md     ← Template para nova feature
│   ├── bug_report.md          ← Template para reportar bugs
│   ├── refactor.md            ← Template para refatoração
│   └── documentation.md       ← Template para documentação
├── PULL_REQUEST_TEMPLATE.md   ← Template para PRs
├── labels.yml                 ← Configuração de labels
└── SETUP_GITHUB.md            ← Guia de setup do GitHub
```

### Documentação

```
documents/
├── COMO_USAR_ROADMAP.md       ← Guia de uso do sistema
└── ESTRUTURA_ROADMAP.md       ← Este arquivo (visão geral)
```

---

## 🎯 Hierarquia de Planejamento

```
┌─────────────────────────────────────────────────────┐
│                   ROADMAP.md                         │
│  • Visão estratégica de longo prazo                 │
│  • Features organizadas por versões (v3.x, v4.x)    │
│  • Benefícios e motivação de cada feature           │
│  • ETAs e prioridades                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ├── Referencia ──────────────────┐
                 │                                 ▼
                 │                    ┌─────────────────────────┐
                 │                    │    GitHub Issues        │
                 │                    │  • Detalhamento técnico │
                 │                    │  • Discussão e decisões │
                 │                    │  • Tracking de progresso│
                 │                    └───────────┬─────────────┘
                 │                                │
                 │                                ├── Implementa ─┐
                 │                                │                ▼
                 │                                │    ┌─────────────────┐
                 │                                │    │  Pull Requests  │
                 │                                │    │  • Código       │
                 │                                │    │  • Testes       │
                 │                                │    │  • Docs         │
                 │                                │    └────────┬────────┘
                 │                                │             │
                 │                                │             ├── Atualiza
                 │                                │             ▼
                 │                                │    ┌─────────────────┐
                 │                                │    │  CHANGELOG.md   │
                 │                                │    │  • Histórico    │
                 │                                │    └─────────────────┘
                 │
                 └── Para tarefas menores ───────┐
                                                 ▼
                                    ┌─────────────────────────┐
                                    │       TODO.md           │
                                    │  • Bugs conhecidos      │
                                    │  • Melhorias pontuais   │
                                    │  • Quick wins           │
                                    └─────────────────────────┘
```

---

## 🔄 Fluxo de Trabalho Típico

### 1. Planejamento Inicial

```
1. Ideia de feature
   ↓
2. Adicionar ao ROADMAP.md (com versão e prioridade)
   ↓
3. Criar GitHub Issue usando template apropriado
   ↓
4. Adicionar labels (versão, prioridade, tipo)
   ↓
5. Adicionar ao GitHub Project Board (opcional)
```

### 2. Desenvolvimento

```
1. Escolher issue do backlog
   ↓
2. Criar branch (feature/nome-da-feature)
   ↓
3. Implementar seguindo CONTRIBUTING.md
   ↓
4. Adicionar testes
   ↓
5. Atualizar documentação
   ↓
6. Commit seguindo Conventional Commits
```

### 3. Entrega

```
1. Abrir PR usando template
   ↓
2. Aguardar revisão
   ↓
3. Fazer ajustes solicitados
   ↓
4. Merge para main
   ↓
5. Atualizar CHANGELOG.md
   ↓
6. Fechar issue
   ↓
7. Mover para "Done" no Project Board
```

---

## 📊 Quando Usar Cada Arquivo

### Use ROADMAP.md quando:

- ✅ Planejar features de médio/longo prazo
- ✅ Organizar versões futuras (v3.x, v4.x)
- ✅ Documentar benefícios e motivações
- ✅ Estimar timelines (Q1, Q2, etc.)
- ✅ Agrupar features relacionadas

### Use TODO.md quando:

- ✅ Rastrear bugs conhecidos
- ✅ Listar melhorias pontuais
- ✅ Documentar quick wins
- ✅ Tarefas técnicas pequenas
- ✅ Infraestrutura e manutenção

### Use GitHub Issues quando:

- ✅ Detalhar implementação técnica
- ✅ Discutir abordagens
- ✅ Rastrear progresso
- ✅ Coletar feedback
- ✅ Documentar decisões

### Use GitHub Projects quando:

- ✅ Visualizar pipeline de trabalho
- ✅ Priorizar entre múltiplas issues
- ✅ Acompanhar status visual
- ✅ Organizar por sprints/milestones

---

## 🏷️ Sistema de Labels

### Por Tipo
```
enhancement      → Nova feature
bug              → Correção de bug
refactor         → Refatoração
documentation    → Documentação
technical-debt   → Débito técnico
testing          → Testes
performance      → Performance
security         → Segurança
```

### Por Prioridade
```
priority:high    → 🔴 Alta prioridade
priority:medium  → 🟡 Média prioridade
priority:low     → 🟢 Baixa prioridade
```

### Por Versão
```
v3.0.0  → Arquitetura Modular
v3.1.0  → Pipeline Resiliente
v3.2.0  → Configuração e CLI
v3.3.0  → Extração Seletiva
v4.0.0  → Qualidade e Garantias
```

### Por Status
```
status:blocked      → Bloqueado
status:in-progress  → Em desenvolvimento
status:needs-review → Precisa revisão
```

---

## 📋 Templates de Issues

### 🚀 Feature Request
**Quando usar**: Propor nova funcionalidade

**Seções principais**:
- Descrição da feature
- Problema que resolve
- Solução proposta
- Relação com ROADMAP
- Critérios de aceitação

### 🐛 Bug Report
**Quando usar**: Reportar problema

**Seções principais**:
- Descrição do bug
- Passos para reproduzir
- Comportamento esperado vs atual
- Ambiente (OS, Python, versão)

### 🔧 Refactoring
**Quando usar**: Melhorar estrutura do código

**Seções principais**:
- Objetivo da refatoração
- Código afetado
- Problemas atuais
- Proposta de melhoria
- Garantias (testes, etc.)

### 📚 Documentation
**Quando usar**: Melhorar documentação

**Seções principais**:
- Tipo de documentação
- Localização
- Problema atual
- Melhoria proposta

---

## 📈 Métricas e Acompanhamento

### Métricas Úteis

1. **Velocity**: Issues fechadas por semana/mês
2. **Lead Time**: Tempo de issue aberta até fechada
3. **Burndown**: Issues restantes por versão
4. **Distribuição**: % de bugs vs features vs docs

### Ferramentas

- **GitHub Insights**: Métricas nativas
- **GitHub Projects**: Views e grouping
- **Milestones**: Agrupar por release
- **Labels**: Categorização e filtering

---

## 🎯 Boas Práticas

### ✅ Faça

1. **Documente decisões** em issues (não só em chat/email)
2. **Referencie issues** em commits e PRs (`Closes #123`)
3. **Mantenha ROADMAP atualizado** conforme prioridades mudam
4. **Use labels consistentemente** para facilitar busca
5. **Atualize CHANGELOG** ao fazer merge
6. **Feche issues antigas** ou marque como `wontfix`
7. **Agrupe PRs pequenos** em vez de um mega-PR

### ❌ Evite

1. ❌ Implementar features não documentadas
2. ❌ PRs sem issue associada
3. ❌ Issues vagas sem critérios de aceitação
4. ❌ Duplicar informação entre arquivos
5. ❌ Deixar TODO.md desatualizado
6. ❌ Fazer commits diretos em `main`
7. ❌ Ignorar templates de issues/PRs

---

## 🔧 Manutenção do Sistema

### Mensal

- [ ] Revisar ROADMAP.md (ajustar prioridades/datas)
- [ ] Limpar TODO.md (remover itens completos)
- [ ] Fechar issues stale (>60 dias sem atividade)
- [ ] Atualizar labels se necessário

### Por Release

- [ ] Atualizar CHANGELOG.md
- [ ] Mover features completadas de `Planned` para `Released` no ROADMAP
- [ ] Criar GitHub Release com notas
- [ ] Anunciar mudanças principais

### Trimestral

- [ ] Revisar visão de longo prazo no ROADMAP
- [ ] Reavaliar versões futuras (v4.x, v5.x)
- [ ] Analisar métricas de contribuição
- [ ] Coletar feedback de usuários

---

## 📚 Recursos Adicionais

### Documentação do Projeto

| Arquivo | Propósito |
|---------|-----------|
| [README.md](../README.md) | Visão geral e getting started |
| [ROADMAP.md](../ROADMAP.md) | Planejamento de futuro |
| [TODO.md](../TODO.md) | Tarefas técnicas |
| [CHANGELOG.md](../CHANGELOG.md) | Histórico de mudanças |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Guia de contribuição |
| [COMO_USAR_ROADMAP.md](./COMO_USAR_ROADMAP.md) | Guia de uso do sistema |

### Templates GitHub

| Arquivo | Propósito |
|---------|-----------|
| [feature_request.md](../.github/ISSUE_TEMPLATE/feature_request.md) | Template de feature |
| [bug_report.md](../.github/ISSUE_TEMPLATE/bug_report.md) | Template de bug |
| [refactor.md](../.github/ISSUE_TEMPLATE/refactor.md) | Template de refactor |
| [documentation.md](../.github/ISSUE_TEMPLATE/documentation.md) | Template de docs |
| [PULL_REQUEST_TEMPLATE.md](../.github/PULL_REQUEST_TEMPLATE.md) | Template de PR |

### Setup

| Arquivo | Propósito |
|---------|-----------|
| [labels.yml](../.github/labels.yml) | Configuração de labels |
| [SETUP_GITHUB.md](../.github/SETUP_GITHUB.md) | Guia de setup |

---

## 🎓 Exemplos Práticos

### Exemplo 1: Adicionar Feature do Roadmap

**Cenário**: Implementar "Extração de Semanas Específicas" (v3.3.0)

**Passos**:
1. Feature já está no ROADMAP.md ✅
2. Criar issue: `feat: add --weeks flag for selective extraction`
3. Usar template "Feature Request"
4. Adicionar labels: `enhancement`, `v3.3.0`, `priority:high`
5. Referenciar ROADMAP: "Ver ROADMAP.md seção v3.3.0"
6. Adicionar ao Project Board na coluna "Next"
7. Criar branch: `feature/selective-week-extraction`
8. Implementar, testar, documentar
9. Abrir PR referenciando issue: `Closes #45`
10. Merge e atualizar CHANGELOG.md

### Exemplo 2: Corrigir Bug Urgente

**Cenário**: Timeout em semanas com >50 cards

**Passos**:
1. Adicionar ao TODO.md em "🐛 Bugs Conhecidos" ✅
2. Criar issue: `fix: handle timeout on large weeks`
3. Usar template "Bug Report"
4. Adicionar labels: `bug`, `priority:high`
5. Criar branch: `fix/timeout-on-large-weeks`
6. Corrigir, adicionar testes
7. Abrir PR referenciando issue: `Fixes #78`
8. Merge e remover do TODO.md
9. Atualizar CHANGELOG.md

### Exemplo 3: Melhorar Documentação

**Cenário**: Guia de instalação está confuso

**Passos**:
1. Criar issue: `docs: improve installation guide clarity`
2. Usar template "Documentation"
3. Adicionar labels: `documentation`, `priority:medium`
4. Criar branch: `docs/improve-installation-guide`
5. Melhorar documentação
6. Abrir PR referenciando issue: `Closes #92`
7. Merge e atualizar CHANGELOG.md (seção "Documentation")

---

## 💡 Dicas Finais

1. **Comece pequeno**: Não precisa usar tudo de uma vez
2. **Adapte ao contexto**: Ajuste o sistema conforme seu fluxo
3. **Seja consistente**: Use sempre os mesmos padrões
4. **Documente decisões**: Issues são seu histórico
5. **Revise regularmente**: Roadmap é um documento vivo

---

## 📞 Precisa de Ajuda?

- **Dúvidas sobre o sistema**: Abra issue com label `question`
- **Sugestões de melhoria**: Use template "Feature Request"
- **Algo não está claro**: Use template "Documentation"

---

**Última atualização**: 2025-10-08  
**Mantenedor**: Fernando Bertholdo


