# 🚀 Adalove Extract Cards - *Enhanced* v2.0

![Release](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Architecture](https://img.shields.io/badge/architecture-API--first-brightgreen)

> **📋 DISCLAIMER**: Este projeto tem **fins puramente acadêmicos e educacionais**, visando otimizar o aprendizado e organização de materiais de estudo. O autor não se responsabiliza pelo uso inadequado da ferramenta. Use por sua conta e risco, respeitando os termos de uso da plataforma AdaLove e políticas institucionais.

**Sistema de extração de dados da plataforma AdaLove via API com organização inteligente e ancoragem de autoestudos**

---

## 🎉 Novidades - v2.0.0: Extração via API

A versão 2.0.0 introduz um **novo paradigma de extração**:

### ✨ Principais Mudanças

| Recurso | v1 (Playwright) | v2 (API) |
|---------|-----------------|----------|
| **Método** | Automação de browser | Requisições HTTP diretas |
| **Velocidade** | ~5 min/turma | ~10 seg/turma |
| **Estabilidade** | Depende de UI | Independente de UI |
| **Dados** | Scraping HTML | JSON estruturado da API |
| **Autenticação** | Login visual | Token OAuth |
| **Formato saída** | CSV/JSONL | JSON hierárquico |

### 🆕 Novos Recursos

- 🔗 **Ancoragem multi-fator** de autoestudos (professor + proximidade + similaridade). É possível extrair cards de autoestudo que estejam fora da sua ordem original e ainda assim eles serão atrelados aos encontros corretos
- 📅 **Organização por data** com dia da semana em português
- 📁 **Estrutura por turma** com pastas individuais por semana
- 🎯 **JSON hierárquico** com datas e títulos como chaves de acesso

---

## 📑 Índice

- [Como Funciona](#-como-funciona)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura de Saída](#-estrutura-de-saída)
- [Arquitetura](#-arquitetura)
- [Documentação](#-documentação)
- [Licença](#-licença)

---

## 💡 Como Funciona

### Fluxo de Extração v2

```
1. Autenticação via Google OAuth (token capturado do navegador)
2. Requisição à API para listar turmas
3. Requisição para atividades de cada semana
4. Busca detalhes de cada atividade
5. Ancoragem de autoestudos aos encontros
6. Organização hierárquica por data
7. Salvamento em JSON estruturado
```

### Sistema de Ancoragem

O sistema usa **pontuação multi-fator** para vincular autoestudos aos encontros:

| Fator | Pontos | Descrição |
|-------|--------|-----------|
| **Professor** | +3.0 | Mesmo professor no autoestudo e encontro |
| **Proximidade** | +1.5 - 0.1×delta | Posição de sort próxima |
| **Similaridade** | +2.0 × sim | Títulos semelhantes |

---

## ⚡ Instalação

### 1. Clone e Configure Ambiente

```bash
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: .\venv\Scripts\activate  # Windows

# Dependências
pip install -r requirements.txt
```

### 2. Dependências Principais

- `httpx` - Cliente HTTP assíncrono
- `pydantic` - Validação de dados
- `python-dotenv` - Gerenciamento de credenciais

---

## 🔐 Configuração

### Configure o `.env`

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais do AdaLove:
```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

> ✅ **Autenticação automática**: O sistema faz login via Google OAuth automaticamente usando essas credenciais. Não é necessário capturar tokens manualmente.

---

## 🚀 Uso

### Extração Completa de uma Turma

```bash
python extrair_turma_completa.py "2026-1A-T13"
```

### Saída

```
📊 RESUMO DA EXTRAÇÃO
======================================================================
   🏫 Turma: 2026-1A-T13
   📁 Pasta: output/api_extraction/2026-1A-T13
   📊 Semanas: 10
   📚 Total de atividades: 132
   📝 Ponderadas: 20
   🔗 Cards ancorados: 86
======================================================================
```

---

## 📁 Estrutura de Saída

### Hierarquia de Pastas

```
output/api_extraction/
└── 2026-1A-T13/
    ├── extracao_completa.json    # Todas as semanas
    └── semanas/
        ├── semana_01.json
        ├── semana_02.json
        └── ...
```

### Formato JSON

O JSON usa **datas como chaves** para fácil acesso:

```json
{
  "encontros": {
    "2026-03-23": {
      "dia_semana": "Segunda-feira",
      "titulo": "Suporte ao Projeto - Integração",
      "tipo": "encontro_instrucao",
      "professor": "Ovidio Lopes da Cruz Netto",
      "autoestudos": {
        "Suporte aos projetos dos grupos": {
          "descricao": "...",
          "professor": "Ovidio Lopes da Cruz Netto",
          "conteudos_relacionados": [...],
          "is_ponderada": false,
          "ancora_confianca": "high"
        }
      }
    }
  }
}
```

### Acesso Programático

```python
import json

with open("semana_08.json") as f:
    data = json.load(f)

# Acessar encontro de 23/03
encontro = data["encontros"]["2026-03-23"]
print(encontro["titulo"])  # "Suporte ao Projeto - Integração"

# Acessar autoestudo específico
auto = encontro["autoestudos"]["Suporte aos projetos dos grupos"]
print(auto["professor"])  # "Ovidio Lopes da Cruz Netto"
```

---

## 🏗️ Arquitetura

### Estrutura do Projeto

```
adalove_extract_cards_enhanced/
├── extrair_turma_completa.py     # 🎯 Script principal v2
├── adalove_extractor/            # Pacote Python
│   ├── api/                      # Cliente HTTP
│   │   ├── client.py
│   │   └── endpoints.py
│   ├── extractors/
│   │   └── api/
│   │       └── anchor.py         # Sistema de ancoragem
│   ├── models/
│   │   └── api_card_types.py     # Mapeamento de tipos
│   └── config/
│       └── settings.py           # Configurações
├── output/                       # Dados extraídos
│   └── api_extraction/
└── documents/                    # Documentação
```

### Módulos Principais

| Módulo | Responsabilidade |
|--------|------------------|
| `client.py` | Cliente HTTP com autenticação OAuth |
| `endpoints.py` | Mapeamento de endpoints da API |
| `anchor.py` | Sistema de ancoragem multi-fator |
| `api_card_types.py` | Tradução de tipos de cards |

---

## 📚 Documentação

### Guias de Uso
- 📖 [**GUIA_CAPTURA_REDE.md**](./docs/GUIA_CAPTURA_REDE.md) - Captura de tokens
- 📖 [**api-extraction-design.md**](./docs/api-extraction-design.md) - Design da extração
- 📖 [**ESTRUTURA_SAIDA.md**](./docs/ESTRUTURA_SAIDA.md) - Formato JSON de saída

### Referências
- 📖 [**MAPEAMENTO_TIPOS_CARDS.md**](./referencias/MAPEAMENTO_TIPOS_CARDS.md) - Tipos de cards

### Histórico (v1 - Playwright)
- 📖 [**GUIA_EXTRACAO.md**](./documents/GUIA_EXTRACAO.md) - Extração v1 (legado)
- 📖 [**ENRIQUECIMENTO.md**](./documents/ENRIQUECIMENTO.md) - Sistema de enriquecimento v1

---

## 🔄 Migração v1 → v2

### Principais Diferenças

| Aspecto | v1 (Playwright) | v2 (API) |
|---------|-----------------|----------|
| **Script principal** | `adalove_extractor.py` | `extrair_turma_completa.py` |
| **Entrada** | Interativo no browser | Argumento de linha de comando |
| **Saída** | `dados_extraidos/` (CSV) | `output/api_extraction/` (JSON) |
| **Ancoragem** | Pelo índice visual | Multi-fator (professor, sort, título) |

### Comandos

```bash
# v1 (Playwright - legado)
python adalove_extractor.py

# v2 (API - recomendado)
python extrair_turma_completa.py "NOME-DA-TURMA"
```

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

### 🌟 Créditos
- **Projeto original**: [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards)
- **Esta versão**: Desenvolvida e expandida por Fernando Bertholdo

### ⚖️ Responsabilidade
- Este software é fornecido "como está", sem garantias
- O uso é por **conta e risco** do usuário
- **Fins acadêmicos e educacionais** recomendados
- Respeite os **termos de uso** da plataforma AdaLove

---

**🎉 Adalove Extract Cards v2.0 - Extração rápida e inteligente via API!**
