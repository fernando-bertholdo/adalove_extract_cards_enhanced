---
name: validate-docs-links
description: Validar integridade de links e referências cruzadas na documentação Markdown do projeto. Use após mover/renomear arquivos, periodicamente, ou antes de releases.
---

# Validate Docs Links

Validar que todos os links em arquivos Markdown do projeto estão funcionais.

## Quando Usar

- Após mover ou renomear arquivos/diretórios
- Após adicionar novos documentos
- Periodicamente (a cada 2-3 semanas)
- Antes de releases
- Quando suspeitar de links quebrados

## Escopo de Validação

### Diretórios Escaneados

| Diretório | Pattern | Propósito |
|-----------|---------|-----------|
| `docs/` | `**/*.md` | Documentação técnica |
| `.agent/rules/` | `*.md` | Regras de qualidade |
| `.agent/skills/` | `**/*.md` | Skills operacionais |
| Raiz | `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `QUICK_START.md` | Docs principais |

### Tipos de Links Validados

1. **Links relativos** — `[texto](../docs/API_DOCUMENTATION.md)`
2. **Links de âncora** — `[texto](#seção)`
3. **Links de skill** — referências a SKILL.md de dentro de docs
4. **Links de imagem** — `![alt](path/to/image.png)`

## Workflow

### 1. Escanear Arquivos

```
Para cada arquivo .md nos diretórios escaneados:
  Extrair todos os links markdown: [texto](destino)
  Classificar por tipo:
    - Relativo (começa com ./ ou ../)
    - Âncora (começa com #)
    - Externo (começa com http)
    - Absoluto (começa com /)
```

### 2. Validar Links Relativos

```
Para cada link relativo:
  Resolver path relativo ao arquivo que contém o link
  Verificar se arquivo destino existe
  Se não existir → registrar como QUEBRADO
```

### 3. Validar Âncoras

```
Para cada link de âncora:
  Se âncora aponta para mesmo arquivo:
    Verificar se heading existe no arquivo
  Se âncora aponta para outro arquivo (path#anchor):
    Verificar se arquivo existe
    Verificar se heading existe no arquivo destino
```

### 4. Gerar Relatório

```markdown
# Relatório de Validação de Links

**Data:** [YYYY-MM-DD]
**Arquivos escaneados:** X
**Links validados:** Y

## Resumo

| Tipo | Total | OK | Quebrados |
|------|-------|----|-----------|
| Relativos | X | Y | Z |
| Âncoras | X | Y | Z |
| Externos | X | - | - |

## Links Quebrados

### ❌ docs/API_DOCUMENTATION.md
- Linha 45: `[models](../src/models.py)` → arquivo não encontrado
  - **Sugestão:** `[models](../src/adalove_extractor/models/)`

### ❌ README.md
- Linha 12: `[roadmap](#roadmap)` → âncora não encontrada
  - **Sugestão:** remover link ou adicionar seção

## Ações Corretivas

- [ ] Corrigir link em docs/API_DOCUMENTATION.md:45
- [ ] Corrigir âncora em README.md:12
```

## Auto-Fix (Quando Possível)

O skill pode sugerir correções automáticas para:

- **Paths relativos incorretos** — se arquivo existe em outro path
- **Âncoras malformadas** — normalizar para formato slug do heading
- **Extensões faltando** — adicionar `.md` quando óbvio

```
Para cada link quebrado:
  Se arquivo destino existe em path diferente:
    → Sugerir path correto
  Se heading existe com slug diferente:
    → Sugerir âncora correta
  Caso contrário:
    → Marcar como "requer ação manual"
```

## Rules

1. **Links internos devem funcionar** — link quebrado = bug
2. **Links externos não são validados** — apenas reportados
3. **Auto-fix é sugestão** — confirmar antes de aplicar
4. **Rodar após mover arquivos** — prevenir links quebrados

## Skills Relacionadas

- `update-docs` — atualizar docs (validar links depois)
- `audit-architecture` — auditoria mais ampla de docs
