---
name: fresh-context
description: Gerar CONTEXT.md para handoff entre sessões ou quando o contexto excede 150k tokens. Cria documento conciso e auto-contido para continuar trabalho em ambiente limpo.
---

# Fresh Context

Gerar um CONTEXT.md para handoff de sessão, evitando "context rot" em sessões longas.

## Quando Usar

- **Sessão >150k tokens** — contexto começando a degradar
- **Handoff para outro agente** — fornecer contexto focado
- **Retomada após pausa** — em vez de reler toda sessão anterior
- **Início de nova feature** — criar contexto limpo

## Output

Arquivo: `CONTEXT.md` na raiz do projeto (ou no diretório relevante).

## Workflow

### 1. Avaliar Necessidade

```
Sinais de context rot:
- Agente repete perguntas já respondidas
- Respostas contradizem decisões anteriores
- Agente "esquece" arquivos já editados
- Sessão >150k tokens
```

### 2. Coletar Estado Atual

```
Fontes de informação:
1. README.md — visão geral do projeto
2. docs/ — documentação técnica
3. git log -10 — últimas mudanças
4. git status — trabalho em andamento
5. Sessão atual — decisões e progresso
```

### 3. Gerar CONTEXT.md

```markdown
# CONTEXT.md

**Gerado em:** [data]
**Propósito:** [handoff / retomada / novo agente]

## Estado do Projeto

[Resumo conciso: o que o projeto faz, stack, arquitetura]

## Trabalho em Andamento

[O que estava sendo feito, progresso atual]

### Decisões Tomadas (🔒 Locked)

1. [Decisão 1 — rationale]
2. [Decisão 2 — rationale]

### Ideias Diferidas (📌 Later)

1. [Ideia 1 — por que não agora]

## Próximos Passos

1. [Tarefa imediata]
2. [Tarefa seguinte]

## Arquivos Relevantes

- `path/to/file.py` — [o que faz / por que importa]

## Prompt de Continuação

> [Prompt sugerido para iniciar nova sessão]
```

### 4. Regras de Qualidade

- **Max 200 linhas** — conciso, não verboso
- **Auto-contido** — não depender de contexto da sessão anterior
- **Referências concretas** — paths reais, não genéricos
- **Decisões explícitas** — marcar 🔒 locked vs 📌 deferred
- **Sem duplicação** — referenciar docs existentes, não copiar

### 5. Prompt de Continuação

Incluir no final do CONTEXT.md um prompt pronto para colar na nova sessão:

```
Leia @CONTEXT.md para contexto do trabalho em andamento.

Objetivo: [objetivo conciso]

Por favor:
1. [Tarefa 1]
2. [Tarefa 2]
3. [Tarefa 3]
```

## Anti-Patterns

```
# ❌ CONTEXT.md verboso (>500 linhas)
# ❌ Copiar conteúdo inteiro de docs existentes
# ❌ Incluir código fonte no CONTEXT.md
# ❌ Deixar decisões sem rationale

# ✅ CONTEXT.md conciso (<200 linhas)
# ✅ Referenciar docs existentes
# ✅ Focar em decisões e próximos passos
# ✅ Incluir prompt de continuação pronto
```

## Skills Relacionadas

- `update-docs` — atualizar docs antes de gerar CONTEXT
