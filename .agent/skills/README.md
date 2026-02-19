# Skills

Skills são workflows executáveis que guiam o agente em tarefas recorrentes.

## Índice

| Skill | Descrição | Quando Usar |
|-------|-----------|-------------|
| [pre-commit-check](pre-commit-check/SKILL.md) | Checklist de qualidade pré-commit | Antes de cada `git commit` |
| [organize-commits](organize-commits/SKILL.md) | Organizar mudanças em commits atômicos | Múltiplas mudanças pendentes |
| [validate-testing](validate-testing/SKILL.md) | Validar testes e cobertura | Feature completa |
| [fresh-context](fresh-context/SKILL.md) | Handoff entre sessões | Sessão >150k tokens |
| [update-docs](update-docs/SKILL.md) | Atualizar documentação | Mudanças de arquitetura/API |
| [validate-docs-links](validate-docs-links/SKILL.md) | Validar links em markdown | Após mover/renomear docs |
| [audit-architecture](audit-architecture/SKILL.md) | Auditoria de redundância em docs | A cada 2-3 semanas |

## Formato

Cada skill segue o padrão [agentskills.io](https://agentskills.io):
- `SKILL.md` com frontmatter YAML (`name`, `description`)
- Corpo em markdown com instruções passo-a-passo
