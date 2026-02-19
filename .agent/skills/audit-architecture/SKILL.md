---
name: audit-architecture
description: Auditoria periódica para detectar redundância e drift entre arquivos de documentação e configuração do agente. Use antes de releases, após criar novos docs, ou periodicamente a cada 2-3 semanas.
---

# Audit Architecture

Auditoria periódica para detectar redundância e drift entre documentação e configuração.

## Quando Usar

- **Periodicamente** — a cada 2-3 semanas de desenvolvimento ativo
- **Antes de releases** — garantir consistência
- **Após criar novo documento** — verificar se não duplica existente
- **Após refatoração grande** — verificar se docs refletem a realidade

## Arquitetura de Documentação

O projeto segue esta hierarquia:

| Tipo de Conteúdo | Fonte Única | Carregamento |
|------------------|-------------|--------------|
| Regras operacionais | `.agent/AGENTS.md` | Sempre |
| Skills/workflows | `.agent/skills/*/SKILL.md` | Sob demanda |
| Regras técnicas | `.agent/rules/*.md` | Por contexto |
| Visão geral | `README.md` | Sempre |
| Guia rápido | `QUICK_START.md` | Sob demanda |
| API docs | `docs/API_DOCUMENTATION.md` | Sob demanda |
| Formato de saída | `docs/ESTRUTURA_SAIDA.md` | Sob demanda |
| Contribuição | `CONTRIBUTING.md` | Sob demanda |
| Changelog | `CHANGELOG.md` | Sob demanda |

## Procedimento de Auditoria

### 1. Verificar Sincronização AGENTS.md ↔ Docs

```
Checklist:
- [ ] AGENTS.md não duplica conteúdo do README.md
- [ ] AGENTS.md referencia docs existentes (não copia)
- [ ] Stack/comandos em AGENTS.md batem com pyproject.toml
- [ ] Skills listadas em AGENTS.md existem em skills/
```

### 2. Verificar Skills vs Rules

```
Checklist:
- [ ] Skills são WORKFLOWS (procedimentos com passos)
- [ ] Rules são REFERÊNCIAS (padrões e diretrizes)
- [ ] Skills NÃO duplicam conteúdo de rules/
- [ ] Cada skill tem <200 linhas
```

### 3. Verificar Duplicação Entre Arquivos

```
Pares a comparar:
1. AGENTS.md vs README.md
2. AGENTS.md vs CONTRIBUTING.md
3. .agent/rules/*.md vs .agent/skills/*/SKILL.md
4. README.md vs QUICK_START.md
5. README.md vs docs/API_DOCUMENTATION.md
```

### 4. Verificar Arquivos Órfãos

```
Checklist:
- [ ] Todo arquivo em docs/ é referenciado em README.md ou AGENTS.md
- [ ] Todo arquivo em .agent/ é referenciado em algum lugar
- [ ] Nenhum arquivo obsoleto sem referência
```

### 5. Verificar Código vs Docs

```
Checklist:
- [ ] Comandos documentados funcionam (testar)
- [ ] Estrutura de diretórios documentada bate com realidade
- [ ] Variáveis de .env.example estão documentadas
- [ ] Módulos em src/ estão representados na documentação
```

## Formato de Relatório

```markdown
# Relatório de Auditoria

**Data:** [YYYY-MM-DD]

## Resumo

| Categoria | Status | Issues |
|-----------|--------|--------|
| Sincronização AGENTS.md ↔ Docs | ✅/❌ | [N] |
| Skills vs Rules | ✅/❌ | [N] |
| Duplicação | ✅/❌ | [N] |
| Arquivos órfãos | ✅/❌ | [N] |
| Código vs Docs | ✅/❌ | [N] |

**Resultado Geral:** ✅ PASS / ❌ FAIL

## Issues Encontrados

### [Categoria]
1. **[Descrição]**
   - Arquivo: [path]
   - Ação sugerida: [como corrigir]

## Ações Corretivas
- [ ] [Ação 1]
- [ ] [Ação 2]
```

## Sinais de Alerta

### 🚨 Crítico
- Mesma informação em 3+ arquivos
- Comando documentado que não funciona
- Link quebrado para arquivo crítico

### ⚠️ Atenção
- Duplicação parcial entre 2 arquivos
- Arquivo órfão não crítico
- Skill com >200 linhas

### ℹ️ Info
- Inconsistência de formatação
- Referências unidirecionais

## Skills Relacionadas

- `validate-docs-links` — validar apenas links
- `update-docs` — atualizar docs após detectar drift
