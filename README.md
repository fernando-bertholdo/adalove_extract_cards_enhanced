# Adalove Extract Cards — Enhanced

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/architecture-API--first-brightgreen)](#arquitetura)

> **Aviso:** Este projeto tem fins acadêmicos e educacionais. Use com responsabilidade e respeite os termos de uso da plataforma AdaLove e as políticas institucionais do Inteli.

CLI interativa para extrair cards da plataforma AdaLove via API, organizar encontros e autoestudos por semana, e gerar respostas para atividades ponderadas com IA.

---

## Quick Start

```bash
# 1. Clone e configure o ambiente
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced
python -m venv venv && source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure suas credenciais
cp .env.example .env
# edite .env com seu login e senha do AdaLove

# 4. Execute
python adalove_cli.py
```

---

## O que faz

| Recurso | Descrição |
|---------|-----------|
| **Extração via API** | Extrai cards sem automação de browser (~10s/turma) |
| **Organização por semana** | JSON hierárquico com encontros e autoestudos por data |
| **Ancoragem multi-fator** | Vincula autoestudos aos encontros (professor + proximidade + título) |
| **Viewer de ponderadas** | Lista atividades avaliativas com status de prazo e nota |
| **Exportação de calendário** | Gera `.ics` importável no Google Calendar / Apple Calendar |
| **Resposta com IA** | Gera rascunho de resposta para ponderadas usando Claude |

---

## Estrutura de Saída

```
output/api_extraction/
└── 2026-1A-T13/
    ├── extracao_completa.json      # Todas as semanas consolidadas
    ├── 2026-1A-T13_calendario.ics  # Exportação para calendário
    ├── rascunhos/                  # Rascunhos gerados por IA
    └── semanas/
        ├── semana_01.json
        ├── semana_02.json
        └── ...
```

**Formato do JSON por semana:**

```json
{
  "encontros": {
    "2026-03-23": {
      "dia_semana": "Segunda-feira",
      "titulo": "Suporte ao Projeto — Integração",
      "tipo": "encontro_instrucao",
      "professor": "Nome do Professor",
      "autoestudos": {
        "Título do autoestudo": {
          "descricao": "...",
          "professor": "...",
          "ancora_confianca": "high"
        }
      }
    }
  }
}
```

---

## Arquitetura

```
adalove_extract_cards_enhanced/
├── adalove_cli.py                  # Entry point — CLI interativa
├── src/adalove_extractor/
│   ├── api/                        # Cliente HTTP + autenticação AWS Cognito
│   ├── extractors/                 # Extração completa de turma
│   ├── enrichment/                 # Ancoragem multi-fator de autoestudos
│   ├── ai/                         # Geração de respostas com IA (claude CLI)
│   ├── io/                         # Writers, calendário, checkpoints
│   ├── models/                     # Modelos de dados (Card, EnrichedCard)
│   ├── config/                     # Settings (Pydantic) + system prompt padrão
│   └── utils/                      # Hash, texto, helpers
├── tests/                          # Testes unitários
├── output/                         # Dados extraídos (gerado em runtime)
└── docs/                           # Documentação técnica
```

| Módulo | Responsabilidade |
|--------|-----------------|
| `api/client.py` | HTTP assíncrono com auth, retry e submissão de respostas |
| `api/auth.py` | Autenticação via AWS Cognito / Google OAuth |
| `extractors/turma_completa.py` | Orquestra extração completa de uma turma |
| `enrichment/anchor.py` | Sistema de ancoragem multi-fator |
| `ai/context_builder.py` | Monta contexto para geração de resposta |
| `ai/answer_generator.py` | Chama `claude` CLI como subprocess |
| `io/calendar.py` | Exportação para formato iCalendar (.ics) |

---

## Configuração

Edite o arquivo `.env` (criado a partir de `.env.example`):

```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

### Personalizar estilo das respostas geradas por IA

Edite o arquivo de system prompt padrão para ajustar o estilo de escrita, formato de entrega e qualquer instrução recorrente:

```
src/adalove_extractor/config/default_system_prompt.md
```

---

## Feature: Gerar Resposta com IA

Na tela de uma atividade ponderada, selecione **"Gerar resposta com IA"** para:

1. Usar os materiais dos autoestudos relacionados como contexto
2. Adicionar opcionalmente uma transcrição de aula (arquivo `.txt`)
3. Adicionar notas e instruções extras
4. Validar um esqueleto da resposta antes de gerar o texto completo
5. Revisar, editar no `$EDITOR`, ou submeter diretamente via API

> **Requisito:** O `claude` CLI deve estar instalado e autenticado.
> Instale via: `npm install -g @anthropic-ai/claude-code`

---

## Desenvolvimento

```bash
# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"

# Rodar todos os testes
pytest tests/ -v

# Verificar tipos
mypy src/adalove_extractor/
```

---

## Créditos e Licença

- **Projeto original:** [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards)
- **Esta versão:** Fernando Bertholdo — expandida com extração via API, ancoragem multi-fator e geração de respostas com IA
- **Licença:** MIT — veja [LICENSE](LICENSE)

> Para histórico completo de mudanças, consulte o [CHANGELOG.md](CHANGELOG.md).
