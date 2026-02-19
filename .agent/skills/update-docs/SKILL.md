---
name: update-docs
description: Atualizar documentação do projeto após mudanças de arquitetura, API, ou funcionalidades. Use após implementar features significativas, após refatorações, ou quando docs ficarem desatualizados.
---

# Update Docs

Atualizar documentação do projeto para refletir o estado atual do código.

## Quando Usar

- Após implementar feature significativa
- Após refatoração que muda estrutura/API
- Quando documentação está desatualizada
- Antes de PR que muda comportamento público

## Documentos do Projeto

| Documento | Descrição | Quando Atualizar |
|-----------|-----------|------------------|
| `README.md` | Visão geral, setup, uso básico | Novas funcionalidades |
| `QUICK_START.md` | Guia de início rápido | Mudanças na CLI |
| `CONTRIBUTING.md` | Guia de contribuição | Mudanças no fluxo de dev |
| `CHANGELOG.md` | Histórico de mudanças | Cada release |
| `docs/API_DOCUMENTATION.md` | Documentação da API Adalove | Novos endpoints |
| `docs/ESTRUTURA_SAIDA.md` | Formato do JSON de saída | Mudanças nos modelos |
| `docs/ESTRUTURA_ROADMAP.md` | Roadmap do projeto | Progresso de features |
| `.env.example` | Template de configuração | Novas variáveis de ambiente |

## Workflow

### 1. Identificar O Que Mudou

```bash
# Mudanças desde último commit de docs
git log --oneline --diff-filter=M -- src/ | head -10

# Arquivos de docs que podem estar desatualizados
git log --oneline -1 -- docs/ README.md CONTRIBUTING.md
```

### 2. Atualizar Documentação

Para cada documento afetado:

1. **Ler** o documento atual
2. **Comparar** com o estado real do código
3. **Atualizar** seções desatualizadas
4. **Adicionar** novas seções se necessário
5. **Remover** informações obsoletas

### 3. Atualizar CHANGELOG

Se a mudança é significativa o suficiente para entrar no CHANGELOG:

```markdown
## [Unreleased]

### Added
- [Descrição da feature]

### Changed
- [Descrição da mudança]

### Fixed
- [Descrição do fix]
```

### 4. Verificar Consistência

```
Checklist:
- [ ] README.md reflete funcionalidades atuais
- [ ] Comandos de setup funcionam (testar)
- [ ] Exemplos de uso estão corretos
- [ ] Links internos funcionam
- [ ] .env.example tem todas as variáveis necessárias
```

## Tipos de Atualização

### Tipo: feature

Após adicionar funcionalidade:
- Atualizar `README.md` (se feature é pública)
- Atualizar `QUICK_START.md` (se muda o fluxo de uso)
- Adicionar ao `CHANGELOG.md`
- Atualizar `docs/API_DOCUMENTATION.md` (se novos endpoints)

### Tipo: refactor

Após refatoração:
- Atualizar `CONTRIBUTING.md` (se muda estrutura)
- Atualizar docstrings nos módulos afetados
- Verificar se exemplos ainda funcionam

### Tipo: config

Após mudanças de configuração:
- Atualizar `.env.example`
- Atualizar `README.md` seção de setup
- Atualizar `QUICK_START.md`

## Skills Relacionadas

- `validate-docs-links` — validar links após atualizar docs
- `pre-commit-check` — check antes de commitar mudanças de docs
