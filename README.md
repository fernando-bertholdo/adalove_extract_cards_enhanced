# 🚀 Adalove Extract Cards - *Enhanced*

![Release](https://img.shields.io/github/v/release/fernando-bertholdo/adalove_extract_cards_enhanced?label=vers%C3%A3o)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Playwright](https://img.shields.io/badge/playwright-1.49.1-orange.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/fernando-bertholdo/adalove_extract_cards_enhanced)
![GitHub repo size](https://img.shields.io/github/repo-size/fernando-bertholdo/adalove_extract_cards_enhanced)

> **📋 DISCLAIMER**: Este projeto tem **fins puramente acadêmicos e educacionais**, visando otimizar o aprendizado e organização de materiais de estudo. O autor não se responsabiliza pelo uso inadequado da ferramenta. Use por sua conta e risco, respeitando os termos de uso da plataforma AdaLove e políticas institucionais.

**Extração completa e automatizada de cards do AdaLove com organização inteligente por turma e enriquecimento avançado de dados**

---

## 📑 Índice

- [O Que Este Script Faz](#-o-que-este-script-faz)
- [Instalação Rápida](#-instalação-rápida)
- [Como Usar](#-como-usar)
- [Arquivos Gerados](#-arquivos-gerados)
- [Documentação Completa](#-documentação-completa)
- [Troubleshooting](#-troubleshooting)
- [Releases e Changelog](#-releases-e-changelog)
- [Licença](#-licença)

---

## 🌟 Inspiração e Origem

Este projeto foi **inspirado e desenvolvido a partir** do trabalho original de [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards). A versão atual representa uma **evolução significativa** com funcionalidades expandidas, organização aprimorada e extração completa de materiais acadêmicos.

---

## 📋 O Que Este Script Faz

✅ **Login automático** na plataforma AdaLove  
✅ **Extração completa** de todos os cards de todas as semanas  
✅ **Captura links e materiais** anexados aos cards (Google Drive, PDFs, etc.)  
✅ **Enriquecimento automático** de dados com ancoragem de autoestudos ([saiba mais](./documents/ENRIQUECIMENTO.md))  
✅ **Organização automática** por pasta da turma com nome personalizado  
✅ **Múltiplos formatos** de saída (CSV básico, CSV enriquecido, JSONL) - [detalhes](./documents/ARQUIVOS_GERADOS.md)  
✅ **Logs detalhados** para acompanhamento e debug  

### 🎯 Script Principal

**USE APENAS**: `adalove_extractor.py` 

Este é o script final e definitivo que combina todas as funcionalidades necessárias.

---

## ⚡ Instalação Rápida

### 1. **Instale Dependências**

```bash
# Crie e ative ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Instale pacotes
pip install -r requirements.txt
playwright install chromium
```

> 📖 **Instalação detalhada**: Ver [INSTALACAO.md](./documents/INSTALACAO.md) para instruções completas por sistema operacional e resolução de problemas.

### 2. **Configure Credenciais**

```bash
# Copie o arquivo de exemplo
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows

# Edite .env com suas credenciais
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

---

## 🚀 Como Usar

### Execução

```bash
python adalove_extractor.py
```

### Processo Interativo

1. **Digite nome da turma** → Cria pasta organizada
2. **Login automático** → Usa credenciais do `.env`
3. **Selecione turma na interface** → Manual (mais confiável)
4. **Extração automática** → Processa todas as semanas
5. **Enriquecimento** → Adiciona 20 campos inteligentes
6. **Salvamento** → 3 arquivos gerados em `dados_extraidos/SEU_INPUT/`

### Exemplo de Execução

```
📁 Digite o nome da turma: modulo6
🔑 Fazendo login...
✅ Login realizado!
👆 Agora selecione a turma na interface
⏸️ Pressione Enter após selecionar: [ENTER]
📚 Processando 10 semanas...
🔄 Semana 01 (1/10) - ✅ 14 cards
🔄 Semana 02 (2/10) - ✅ 23 cards
...
🔧 Enriquecendo registros...
🎉 EXTRAÇÃO CONCLUÍDA!
📊 127 cards extraídos em 3 formatos
```

> 📖 **Guia completo de uso**: Ver [GUIA_EXTRACAO.md](./documents/GUIA_EXTRACAO.md)

---

## 📁 Arquivos Gerados

Cada execução gera **3 arquivos** na pasta da turma:

```
dados_extraidos/
└── nome_turma/
    ├── cards_completos_TIMESTAMP.csv         # 10 campos básicos
    ├── cards_enriquecidos_TIMESTAMP.csv      # 30 campos completos
    └── cards_enriquecidos_TIMESTAMP.jsonl    # Formato JSON Lines
```

> **📌 Nota**: As pastas `dados_extraidos/` e `logs/` são **criadas automaticamente** pelo script na primeira execução. Não é necessário criá-las manualmente.

### Resumo dos Formatos

| Formato | Campos | Uso Recomendado |
|---------|--------|-----------------|
| **CSV Básico** | 10 | Visualização rápida (Excel) |
| **CSV Enriquecido** | 30 | Análises avançadas (pandas) |
| **JSONL** | 30 | Pipelines de dados |

> 📖 **Especificação completa**: Ver [ARQUIVOS_GERADOS.md](./documents/ARQUIVOS_GERADOS.md)

### Campos Básicos (10)
- `semana`, `indice`, `id`, `titulo`, `descricao`, `tipo`
- `texto_completo`, `links`, `materiais`, `arquivos`

### Campos Enriquecidos Adicionais (20)
- **Temporais**: `semana_num`, `sprint`, `data_hora_iso`, `data_ddmmaaaa`, `hora_hhmm`
- **Identificação**: `professor` (detectado automaticamente)
- **Classificação**: `is_instrucao`, `is_autoestudo`, `is_atividade_ponderada`
- **Ancoragem**: `parent_instruction_id`, `parent_instruction_title`, `anchor_method`, `anchor_confidence`
- **URLs Normalizadas**: `links_urls`, `materiais_urls`, `arquivos_urls`, `num_links`, `num_materiais`, `num_arquivos`
- **Integridade**: `record_hash`

> 📖 **Como funciona o enriquecimento**: Ver [ENRIQUECIMENTO.md](./documents/ENRIQUECIMENTO.md)

---

## 📚 Documentação Completa

### Guias de Uso
- 📖 [**INSTALACAO.md**](./documents/INSTALACAO.md) - Instalação detalhada por sistema operacional
- 📖 [**GUIA_EXTRACAO.md**](./documents/GUIA_EXTRACAO.md) - Guia passo a passo de uso

### Especificações Técnicas
- 📖 [**ARQUIVOS_GERADOS.md**](./documents/ARQUIVOS_GERADOS.md) - Detalhes dos 3 formatos de saída
- 📖 [**ENRIQUECIMENTO.md**](./documents/ENRIQUECIMENTO.md) - Sistema de enriquecimento e ancoragem
- 📖 [**DADOS_EXTRAIDOS.md**](./documents/DADOS_EXTRAIDOS.md) - Especificação completa dos 30 campos

### Histórico
- 📖 [**README_reformulacao.md**](./documents/README_reformulacao.md) - Evolução do projeto

---

## 📂 Estrutura do Projeto

```
adalove_extract_cards/
├── adalove_extractor.py           # 🎯 SCRIPT PRINCIPAL (USE ESTE)
├── README.md                      # Este arquivo
├── .env.example                   # Template de configuração
├── requirements.txt               # Dependências mínimas (playwright, python-dotenv)
├── requirements-dev.txt           # Dependências opcionais (pandas, numpy)
├── LICENSE                        # Licença MIT
├── documents/                     # 📚 Documentação detalhada
│   ├── INSTALACAO.md
│   ├── GUIA_EXTRACAO.md
│   ├── ARQUIVOS_GERADOS.md
│   ├── ENRIQUECIMENTO.md
│   └── DADOS_EXTRAIDOS.md
├── dados_extraidos/               # 💾 Dados organizados por turma (gerado)
├── logs/                          # 📝 Logs das execuções (gerado)
└── arquivos_antigos/              # 🗂️ Scripts históricos (legado)
```

---

## 🔧 Troubleshooting

### Erro: "python: command not found"
**Solução**: Instale Python 3.8+ do [python.org](https://www.python.org/downloads/)

### Erro: "playwright install" falha
**Solução**: 
```bash
playwright install --force chromium
```

### Erro: Login falhou
**Solução**: 
1. Verifique credenciais no `.env`
2. Use o modo manual quando solicitado
3. Complete o login no navegador e pressione Enter

### Erro: "Nenhum card encontrado"
**Solução**:
1. Certifique-se de **selecionar a turma** no dropdown
2. Aguarde a página carregar completamente
3. Pressione Enter apenas quando ver os cards

### Arquivo .env não encontrado
**Solução**:
```bash
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows
# Depois edite o arquivo .env com suas credenciais
```

> 📖 **Mais problemas?** Ver [INSTALACAO.md](./documents/INSTALACAO.md) (seção "Resolução de Problemas")

---

## 🎯 Dependências

### Instalação Mínima (Recomendada)
```bash
pip install -r requirements.txt
```
**Contém:**
- `playwright==1.49.1` - Automação do navegador
- `python-dotenv==1.0.1` - Gerenciamento de credenciais

### Instalação Completa (Opcional - Para Análise)
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
**Adiciona:**
- `pandas==2.2.3` - Análise de dados
- `numpy==2.2.1` - Operações numéricas
- Outras bibliotecas de análise

> 📖 **Quando usar cada instalação?** Ver [INSTALACAO.md](./documents/INSTALACAO.md)

---

## 🎉 Diferenciais desta Versão

### 🌟 Evolução do Projeto Original

#### Do Script Original (Tony Jonas):
- ✅ Script básico de extração
- ✅ Login automático
- ❌ Sem organização por turma
- ❌ Sem enriquecimento de dados

#### Para Esta Versão:
- ✅ **Sistema completo** com organização automática
- ✅ **30 campos enriquecidos** (vs 10 básicos)
- ✅ **3 formatos de saída** (CSV básico, CSV enriquecido, JSONL)
- ✅ **Ancoragem inteligente** de autoestudos
- ✅ **Detecção automática** de professor
- ✅ **Classificação** de tipos de card
- ✅ **Logs detalhados** para debug
- ✅ **Documentação completa** e profissional

> 📖 **História completa**: Ver [README_reformulacao.md](./documents/README_reformulacao.md)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

```
Copyright (c) 2025 Fernando Bertholdo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

Ver [LICENSE](./LICENSE) para texto completo.

### 🌟 Contribuições
- **Projeto original**: [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards)
- **Esta versão**: Desenvolvida e expandida por Fernando Bertholdo

### ⚖️ Responsabilidade
- Este software é fornecido "como está", sem garantias
- O uso é por **conta e risco** do usuário
- **Fins acadêmicos e educacionais** recomendados
- Respeite os **termos de uso** da plataforma AdaLove

---

## 📦 Releases e Changelog

### Versões Disponíveis

Este projeto segue [Semantic Versioning](https://semver.org/). 

📋 **Histórico completo**: [`CHANGELOG.md`](./CHANGELOG.md)  
🏷️ **Releases**: [GitHub Releases](https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced/releases)

#### [v2.0.0 - Sistema de Enriquecimento Inteligente](https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced/releases/tag/v2.0.0) **(Atual)**
- Sistema de enriquecimento automático de dados (30 campos)
- Ancoragem inteligente de autoestudos
- Múltiplos formatos de saída (CSV básico, CSV enriquecido, JSONL)
- Documentação profissional completa

#### [v1.0.0 - Consolidação](https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced/releases/tag/v1.0.0)
- Primeira versão consolidada e funcional
- Script único unificado
- Extração automatizada completa
- Estrutura organizacional básica

---

## 🏆 Começando Agora

### 3 Passos Rápidos:

```bash
# 1. Instale
pip install -r requirements.txt && playwright install chromium

# 2. Configure
cp .env.example .env && nano .env  # edite com suas credenciais

# 3. Execute
python adalove_extractor.py
```

**Pronto!** Os dados estarão em `dados_extraidos/nome_turma/` em 3 formatos.

---

**🎉 Ferramenta completa para extração acadêmica do AdaLove com enriquecimento inteligente de dados!**

📖 **Dúvidas?** Consulte a [documentação completa](./documents/)
