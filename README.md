# 🚀 Adalove Extract Cards - *Enhanced*

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Playwright](https://img.shields.io/badge/playwright-1.49.1-orange.svg)

> **📋 DISCLAIMER**: Este projeto tem **fins puramente acadêmicos e educacionais**, visando otimizar o aprendizado e organização de materiais de estudo. O autor não se responsabiliza pelo uso inadequado da ferramenta. Use por sua conta e risco, respeitando os termos de uso da plataforma AdaLove e políticas institucionais.

**Extração completa e automatizada de cards do AdaLove com organização inteligente por turma e enriquecimento avançado de dados**

## 🌟 Inspiração e Origem

Este projeto foi **inspirado e desenvolvido a partir** do trabalho original de [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards). A versão atual representa uma **evolução significativa** com funcionalidades expandidas, organização aprimorada e extração completa de materiais acadêmicos.

## 📋 O Que Este Script Faz

✅ **Login automático** na plataforma AdaLove  
✅ **Extração completa** de todos os cards de todas as semanas  
✅ **Captura links e materiais** anexados aos cards (Google Drive, PDFs, etc.)  
✅ **Enriquecimento automático** de dados com ancoragem de autoestudos  
✅ **Organização automática** por pasta da turma com nome personalizado  
✅ **Múltiplos formatos** de saída (CSV básico, CSV enriquecido, JSONL)  
✅ **Logs detalhados** para acompanhamento e debug  

## 🎯 Script Principal

**USE APENAS**: `adalove_extractor.py` 

Este é o script final e definitivo que combina todas as funcionalidades necessárias.

---

## 🚀 Como Usar

### 1. **Preparação**
Crie e ative um ambiente virtual (recomendado) antes de instalar as dependências — isso mantém as dependências isoladas do sistema.

macOS / Linux (zsh/bash):
```bash
# criar e ativar venv
python3 -m venv venv
source venv/bin/activate

# atualizar pip e instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium # instala o navegador usado pelo Playwright
```

Windows (PowerShell):
```powershell
# criar e ativar venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# atualizar pip e instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium # instala o navegador usado pelo Playwright
```

Windows (CMD):
```cmd
REM Criar e ativar venv
python -m venv venv
.\venv\Scripts\activate

REM Atualizar pip e instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Instalar o navegador usado pelo Playwright
playwright install chromium
```

### 2. **Configurar credenciais**
Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:

```bash
# Copiar arquivo de exemplo
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows
```

Edite o arquivo `.env`:
```
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

### 3. **Execução**
```bash
python adalove_extractor.py
```

### 4. **Processo Automatizado**
```
📁 Digite nome da turma: [SEU_INPUT] → Cria pasta organizada
🔑 Login automático → Credenciais do .env  
👆 Selecione turma na interface → Manual (mais confiável)
⚙️ Extração automática → Todas as semanas
🔧 Enriquecimento de dados → Ancoragem e normalização
💾 Salvamento → dados_extraidos/SEU_INPUT/
   ├── cards_completos_TIMESTAMP.csv (formato básico)
   ├── cards_enriquecidos_TIMESTAMP.csv (formato completo)
   └── cards_enriquecidos_TIMESTAMP.jsonl (formato JSON Lines)
```

---

## 📁 Arquivos Gerados

Cada execução gera **3 arquivos** na pasta da turma:

### 1. 📊 `cards_completos_TIMESTAMP.csv` (Formato Básico)
Dados brutos extraídos diretamente da plataforma.

**Colunas (10):** 
- `semana`, `indice`, `id`, `titulo`, `descricao`, `tipo`
- `texto_completo`, `links`, `materiais`, `arquivos`

**Exemplo:**
```csv
semana,indice,id,titulo,descricao,tipo,links,materiais,arquivos,texto_completo
Semana 01,1,card-123,"Intro Python","Conceitos básicos","Atividade","Link: https://example.com","Google Drive: https://drive.google.com/...","exercicios.pdf: https://...","Texto completo do card..."
```

### 2. 🔬 `cards_enriquecidos_TIMESTAMP.csv` (Formato Completo)
Dados processados com **30 colunas** adicionais incluindo:

#### **Campos Adicionados:**
- **Normalização temporal**: `semana_num`, `sprint`, `data_hora_iso`, `data_ddmmaaaa`, `hora_hhmm`
- **Detecção automática**: `professor` (extraído do texto)
- **Classificação inteligente**: 
  - `is_instrucao` (encontros/workshops)
  - `is_autoestudo` (estudos independentes)
  - `is_atividade_ponderada` (atividades com nota)
- **Ancoragem de autoestudos**:
  - `parent_instruction_id` (ID da instrução relacionada)
  - `parent_instruction_title` (título da instrução)
  - `anchor_method` (método usado para ancoragem)
  - `anchor_confidence` (confiança: high/medium/low)
- **URLs normalizadas**: `links_urls`, `materiais_urls`, `arquivos_urls`
- **Contadores**: `num_links`, `num_materiais`, `num_arquivos`
- **Integridade**: `record_hash` (hash único do registro)

**Exemplo de ancoragem:**
```csv
titulo,is_autoestudo,parent_instruction_title,anchor_method,anchor_confidence
"Autoestudo Python 1",True,"Workshop Python","professor,same_date,sim=0.85",high
```

### 3. 📦 `cards_enriquecidos_TIMESTAMP.jsonl` (JSON Lines)
Mesmo conteúdo do CSV enriquecido, mas em formato JSONL (um JSON por linha) para:
- ✅ Pipelines de processamento de dados
- ✅ Integração com ferramentas de análise
- ✅ Backup estruturado com arrays preservados

---

## 📊 Enriquecimento de Dados

### 🧠 **Sistema de Ancoragem Inteligente**

O script utiliza um **algoritmo de pontuação multi-fator** para relacionar autoestudos às suas instruções correspondentes:

#### **Fatores de Pontuação:**
1. **Professor** (+3.0 pontos) - Match exato do nome do professor
2. **Data** (+3.0 pontos) - Mesma data de realização
3. **Similaridade de título** (+2.0 pontos) - Jaccard similarity dos tokens
4. **Proximidade posicional** (+1.5 pontos) - Cards próximos no Kanban

#### **Níveis de Confiança:**
- 🟢 **High**: Professor OU data batem (pontuação ≥ 3.0)
- 🟡 **Medium**: Boa similaridade de título (≥ 0.5) ou proximidade
- 🔴 **Low**: Apenas heurísticas de proximidade

#### **Exemplo de Uso:**
```python
import pandas as pd

# Carregar dados enriquecidos
df = pd.read_csv('dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.csv')

# Filtrar autoestudos com ancoragem de alta confiança
autoestudos_confiantes = df[
    (df['is_autoestudo'] == True) & 
    (df['anchor_confidence'] == 'high')
]

# Ver relacionamentos
print(autoestudos_confiantes[['titulo', 'parent_instruction_title', 'anchor_method']])
```

### 🔍 **Detecção Automática de Professor**

O script identifica o professor usando:
1. **Nomes recorrentes** - Aparições frequentes (≥2) em múltiplos cards
2. **Posição na assinatura** - Última linha do texto do card
3. **Validação por regex** - Padrão de nome completo (2+ palavras, iniciais maiúsculas)

### 📅 **Normalização de Datas**

Extrai e normaliza datas automaticamente:
- **Entrada**: "24/04/2025 - 14:00h"
- **Saída**:
  - `data_ddmmaaaa`: "24/04/2025"
  - `hora_hhmm`: "14:00"
  - `data_hora_iso`: "2025-04-24T14:00:00-03:00"

---

## 📊 Dados Extraídos (Conteúdo Acadêmico Completo)

Para cada card, o script captura **TODOS os materiais acadêmicos**:

### ✅ **Conteúdo Principal**
- 📝 **Título e descrição** completos
- 📄 **Texto completo** do card (incluindo modal)
- 🏷️ **Tipo** (Atividade, Projeto, Material, etc.)
- 📅 **Semana** e posição

### ✅ **Materiais Anexados**
- 🔗 **Links externos** encontrados no card
- 📎 **Google Drive, Docs, Sheets** automaticamente categorizados
- 📁 **Arquivos** (PDFs, DOCs, PPTs, etc.) identificados
- 🖼️ **Imagens** e outros recursos capturados

---

## 📁 Organização Automática por Turma

### 🎯 **Como Funciona**
O script solicita o **nome da turma** no início e cria automaticamente a estrutura organizacional:

### **Exemplo de Uso:**
```bash
$ python adalove_extractor.py
📁 Digite o nome da turma para organizar os dados: modulo6
```

### **Resultado Automático:**
```
dados_extraidos/
└── modulo6/
    ├── cards_completos_20250826_220413.csv
    ├── cards_enriquecidos_20250826_220413.csv
    └── cards_enriquecidos_20250826_220413.jsonl
```

### **Múltiplas Turmas:**
```
dados_extraidos/
├── modulo6/
│   ├── cards_completos_20250826_220413.csv
│   ├── cards_enriquecidos_20250826_220413.csv
│   └── cards_enriquecidos_20250826_220413.jsonl
├── ES06-2025/
│   ├── cards_completos_20250825_201538.csv
│   ├── cards_enriquecidos_20250825_201538.csv
│   └── cards_enriquecidos_20250825_201538.jsonl
└── outro_modulo/
    ├── cards_completos_20250826_084521.csv
    ├── cards_enriquecidos_20250826_084521.csv
    └── cards_enriquecidos_20250826_084521.jsonl
```

### ✅ **Vantagens da Organização:**
- 📁 **Pasta individual** para cada turma
- 🔄 **Timestamping** evita sobrescrever dados
- 📚 **Histórico preservado** de todas as extrações
- 🔍 **Fácil localização** dos dados por turma
- 📊 **3 formatos** por execução (básico, enriquecido, JSONL)

---

## 🔧 Funcionalidades Detalhadas

### 🔐 **Login Inteligente**
- **Automático**: Usa credenciais do arquivo `.env`
- **Fallback manual**: Se automático falhar, permite login manual
- **Detecção**: Reconhece automaticamente redirecionamentos do Google

### 🔍 **Descoberta Automática de Semanas**
- **Scanning**: Encontra todas as semanas disponíveis automaticamente
- **Flexível**: Funciona com qualquer quantidade de semanas
- **Logs**: Mostra quais semanas foram descobertas

### 📎 **Extração Completa de Materiais**
- **Links externos**: Todos os URLs encontrados nos cards
- **Google Workspace**: Drive, Docs, Sheets automaticamente categorizados
- **Arquivos**: PDFs, DOCs, PPTs, etc. identificados separadamente
- **Recursos**: Imagens e outros materiais capturados
- **Categorização**: Separa links, materiais e arquivos automaticamente
- **Modal exploration**: Abre cada card para capturar conteúdo adicional

### 🗂️ **Sistema de Organização**
- **Input personalizado**: Nome da turma definido pelo usuário
- **Criação automática**: Estrutura de pastas gerada automaticamente
- **Preservação**: Dados anteriores nunca são sobrescritos
- **Logs individuais**: Log separado para cada turma e execução

---

## 📝 Sistema de Logs

### **Localização**: `logs/nome_turma_TIMESTAMP.log`

### **Conteúdo dos Logs:**
- ✅ **Processo de login** detalhado (automático ou manual)
- ✅ **Semanas descobertas** e processadas
- ✅ **Cards encontrados** por semana
- ✅ **Links e materiais** capturados por card
- ✅ **Enriquecimento** e ancoragem de autoestudos
- ✅ **Estatísticas finais** da extração
- ❌ **Erros** com contexto para debug

### **Exemplo de Log:**
```
14:30:15 | INFO | 🚀 Iniciando extração para turma: modulo6
14:30:16 | INFO | 🔑 Fazendo login...
14:30:20 | INFO | ✅ Login realizado!
14:30:23 | INFO | 🔍 Descobrindo semanas disponíveis...
14:30:25 | INFO | 📊 10 semanas descobertas
14:30:27 | INFO | 🔄 Semana 01 (1/10)
14:30:30 | INFO |    ✅ 14 cards encontrados
14:30:35 | INFO |    📊 14 cards processados com sucesso
14:31:45 | INFO | 🔧 Enriquecendo registros (ancoragem robusta, normalizações)...
14:31:47 | INFO | 💾 Enriched CSV: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.csv
14:31:47 | INFO | 💾 Enriched JSONL: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.jsonl
```

---

## 📂 Estrutura do Projeto

```
adalove_extract_cards/
├── 🎯 adalove_extractor.py         # SCRIPT PRINCIPAL (USAR ESTE)
├── 💾 main_completo_original.py    # Backup do script original
├── 📋 README.md                    # Este guia
├── 🔧 .env.example                 # Exemplo de configuração
├── 🔐 .env                         # Suas credenciais (criar baseado no .example)
├── 📦 requirements.txt             # Dependências mínimas (playwright, python-dotenv)
├── 📦 requirements-dev.txt         # Dependências de desenvolvimento (pandas, numpy)
├── 📜 LICENSE                      # Licença MIT
├── 🚫 .gitignore                   # Arquivos ignorados pelo Git
├── 📚 documents/                   # Documentação técnica
│   ├── README_reformulacao.md      # Histórico da reformulação
│   ├── GUIA_EXTRACAO.md           # Guias técnicos (legado)
│   └── DADOS_EXTRAIDOS.md         # Especificações dos dados (legado)
├── 💾 dados_extraidos/            # DADOS ORGANIZADOS POR TURMA
│   ├── README.md                   # Explica organização dos dados
│   ├── modulo6/                   # Exemplo de pasta de turma
│   │   ├── cards_completos_*.csv
│   │   ├── cards_enriquecidos_*.csv
│   │   └── cards_enriquecidos_*.jsonl
│   └── ES06-2025/                 # Outra pasta de turma
├── 📝 logs/                        # Logs das execuções (gerado automaticamente)
├── 🗂️ arquivos_antigos/           # Scripts de desenvolvimento (histórico)
└── ⚙️ venv/                       # Ambiente virtual Python (criar localmente)
```

---

## ⚡ Exemplo de Execução Completa

```bash
$ python adalove_extractor.py

🚀 ADALOVE CARDS EXTRACTOR - VERSÃO FINAL
========================================
📋 Este script faz extração completa incluindo:
   ✅ Títulos e descrições dos cards
   ✅ Links e materiais anexados  
   ✅ Arquivos e documentos
   ✅ Organização por pasta da turma
   ✅ Enriquecimento e ancoragem de autoestudos
========================================

📁 Digite o nome da turma para organizar os dados: modulo6
🔑 Fazendo login...
✅ Login realizado!
🏠 Navegando para academic-life...
📁 Dados serão salvos em: dados_extraidos/modulo6/
👆 Agora selecione a turma na interface:
⏸️ Pressione Enter após selecionar a turma na página: [ENTER]
🔍 Descobrindo semanas disponíveis...
📊 10 semanas descobertas:
   📅 Semana 01
   📅 Semana 02
   ...
📚 Processando 10 semanas...
🔄 Semana 01 (1/10)
   ✅ 14 cards encontrados
   📊 14 cards processados com sucesso
🔄 Semana 02 (2/10)
   ✅ 23 cards encontrados
   📊 23 cards processados com sucesso
...

💾 Salvando 127 cards em: dados_extraidos/modulo6/cards_completos_20250826_220413.csv
✅ Dados salvos com sucesso!
📊 Estatísticas por semana:
   Semana 01: 14 cards, 8 links, 12 materiais
   Semana 02: 23 cards, 15 links, 18 materiais
   ...
🔧 Enriquecendo registros (ancoragem robusta, normalizações)...
💾 Enriched CSV: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.csv
💾 Enriched JSONL: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.jsonl

========================================
🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!
========================================
📊 127 cards extraídos
📚 10 semanas processadas  
🔗 89 cards com links
📎 67 cards com materiais
📁 Pasta: dados_extraidos/modulo6
💾 Arquivo básico: cards_completos_20250826_220413.csv
💾 Arquivo enriquecido: cards_enriquecidos_20250826_220413.csv
💾 Arquivo JSONL: cards_enriquecidos_20250826_220413.jsonl
========================================
```

---

## 🎯 Diferenciais da Versão Final

### 🌟 **Evolução do Projeto Original ([Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards))**

#### **🚀 Melhorias Arquitetônicas:**
- **Script Original**: Estrutura básica de extração
- **Esta Versão**: Sistema completo com organização automática, logs detalhados e extração de materiais

#### **📊 Capacidades de Extração:**
- **Script Original**: Foco em dados básicos dos cards
- **Esta Versão**: **Extração acadêmica completa** incluindo:
  - ✅ Links externos e materiais do Google Drive
  - ✅ Arquivos anexados (PDFs, DOCs, etc.)
  - ✅ Categorização automática de conteúdo
  - ✅ Texto completo preservado (card + modal)

#### **🔬 Enriquecimento de Dados:**
- **Script Original**: Dados brutos apenas
- **Esta Versão**: **30 campos enriquecidos**:
  - ✅ Detecção automática de professor
  - ✅ Normalização de datas (ISO 8601)
  - ✅ Classificação de tipo de card
  - ✅ Ancoragem inteligente de autoestudos
  - ✅ URLs normalizadas e contadores

#### **🗂️ Sistema de Organização:**
- **Script Original**: Salvamento simples
- **Esta Versão**: **Organização inteligente**:
  - ✅ Pastas automáticas por turma (nome personalizado)
  - ✅ 3 formatos de saída (CSV básico, CSV enriquecido, JSONL)
  - ✅ Timestamping para preservar histórico
  - ✅ Estrutura de projeto profissional

#### **🔧 Robustez e Confiabilidade:**
- **Script Original**: Automação básica
- **Esta Versão**: **Sistema inteligente**:
  - ✅ Login com fallback manual
  - ✅ Descoberta automática de semanas
  - ✅ Fechamento robusto de modais (múltiplas estratégias)
  - ✅ Logs detalhados para debug
  - ✅ Tratamento de erros robusto

### 🔄 **Evolução Interna do Projeto**

#### **❌ Antes (Desenvolvimento - Confuso):**
- `main_completo.py` → Apenas testava (não extraía dados)
- `extrator_completo.py` → Extraía + CSV + JSON + Relatório
- `extrator_simples.py` → Extraía básico (sem materiais)
- **Múltiplos scripts** gerando confusão

#### **✅ Agora (Final - Simples):**
- `adalove_extractor.py` → **SCRIPT ÚNICO** que faz tudo:
  - ✅ Login automático inteligente
  - ✅ Extração de dados completos + materiais
  - ✅ Enriquecimento automático com ancoragem
  - ✅ Organização automática por turma
  - ✅ 3 formatos de saída (CSV básico/enriquecido/JSONL)
  - ✅ Logs detalhados
  - ✅ Interface confiável

### 🏆 **Principais Inovações desta Versão:**

1. **📎 Extração de Materiais Acadêmicos**
   - Captura **todos os links e arquivos** dos cards
   - **Categorização automática** (links, materiais, arquivos)
   - **Preservação completa** do conteúdo acadêmico
   - **Exploração de modais** para conteúdo adicional

2. **🔬 Enriquecimento Automático**
   - **30 campos enriquecidos** além dos 10 básicos
   - **Ancoragem inteligente** de autoestudos às instruções
   - **Detecção de professor** por heurísticas
   - **Normalização de datas** para ISO 8601
   - **Hash de integridade** para cada registro

3. **🗂️ Organização por Turma**
   - **Input personalizado** do nome da turma
   - **Criação automática** de estrutura de pastas
   - **Histórico preservado** de todas as extrações
   - **3 formatos** simultâneos (CSV básico, CSV enriquecido, JSONL)

4. **🔧 Sistema de Logs Avançado**
   - **Logs detalhados** por turma e timestamp
   - **Debug facilitado** com contexto completo
   - **Acompanhamento** de cada etapa da extração

5. **🎯 Interface Inteligente**
   - **Seleção manual** da turma (mais confiável)
   - **Login com fallback** (automático + manual)
   - **Descoberta automática** de semanas disponíveis

---

## 🚨 Pontos Importantes

### ⚙️ **Configuração Necessária**
- **Arquivo `.env`**: Configure suas credenciais (use `.env.example` como base)
- **Dependências**: Execute `pip install -r requirements.txt`
- **Playwright**: Execute `playwright install chromium`

### 🧩 Dependências mínimas x extras (dev)
O projeto separa as dependências em dois conjuntos:

- **`requirements.txt`** → dependências mínimas necessárias para executar o extractor (recomendado para a maioria dos usuários).
  - `playwright==1.49.1`
  - `python-dotenv==1.0.1`

- **`requirements-dev.txt`** → pacotes opcionais/extra para análises, relatórios e desenvolvimento:
  - `pandas`, `numpy`, `python-dateutil`, `pytz`, etc.

**Instalação (ambiente virtual ativado):**

Instalar apenas o necessário para rodar o extractor:
```bash
pip install -r requirements.txt
playwright install chromium
```

Instalar também as dependências de desenvolvimento/análise:
```bash
pip install -r requirements-dev.txt
```

Manter essa separação reduz o tempo de instalação e o tamanho do ambiente para quem só precisa executar a extração.

### 🎯 **Processo de Uso**
- **Seleção manual** da turma é **intencional** (mais confiável que automação)
- **Nome da turma** é solicitado para **organização automática**
- **Dados nunca são sobrescritos** (timestamping automático)
- **3 arquivos gerados** por execução (básico, enriquecido, JSONL)

### 📊 **Resultados**
- **CSV básico** com 10 campos principais
- **CSV enriquecido** com 30 campos (inclui ancoragem e normalizações)
- **JSONL** para pipelines de dados
- **Organização por turma** em pastas separadas
- **Logs detalhados** para qualquer troubleshooting necessário

---

## 🔧 Troubleshooting

### ❌ **Erro: "Could not find browser"**
**Problema**: Chromium não foi instalado pelo Playwright.

**Solução**:
```bash
playwright install chromium
```

---

### ❌ **Erro: "Login failed" ou timeout no login**
**Problema**: Credenciais incorretas ou redirecionamento não detectado.

**Solução**:
1. Verifique suas credenciais no arquivo `.env`
2. Quando aparecer a mensagem de fallback manual:
   - Complete o login manualmente na janela do navegador
   - Pressione Enter no terminal quando estiver logado

---

### ❌ **Erro: "Modal não fechou" ou navegação travada**
**Problema**: Modal de um card ficou aberto impedindo navegação.

**Solução**: O script já tem múltiplas estratégias de fechamento. Se persistir:
1. Pressione ESC manualmente na janela do navegador
2. Clique fora do modal
3. O script tentará continuar automaticamente

---

### ❌ **Erro: "Nenhuma semana descoberta"**
**Problema**: Turma não foi selecionada ou página não carregou.

**Solução**:
1. Certifique-se de **selecionar a turma** no dropdown antes de pressionar Enter
2. Aguarde a página carregar completamente
3. Se necessário, recarregue a página manualmente e tente novamente

---

### ❌ **Erro: "ModuleNotFoundError: No module named 'playwright'"**
**Problema**: Dependências não foram instaladas.

**Solução**:
```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

### ⚠️ **Cards sem materiais ou links vazios**
**Isso é normal!** Nem todos os cards têm links ou materiais anexados. O script captura tudo que está disponível.

---

### ⚠️ **Arquivo .env não encontrado**
**Problema**: Você esqueceu de criar o arquivo `.env`.

**Solução**:
```bash
# Copie o exemplo e edite
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows

# Edite com suas credenciais
# Linux/macOS: nano .env ou vim .env
# Windows: notepad .env
```

---

### 🐛 **Outros problemas?**
1. Verifique os **logs** em `logs/nome_turma_TIMESTAMP.log`
2. Procure por mensagens de erro com contexto
3. Verifique se está usando a **versão mais recente** do Python (3.8+)
4. Tente executar em **modo headless=False** (padrão) para ver o que está acontecendo

---

## 🏆 Resumo Final

### ✅ **1 Script para Tudo**
`adalove_extractor.py` → Solução completa e definitiva

### ✅ **Extração Acadêmica Total**
Links, materiais, arquivos, Google Drive → Tudo que um módulo contém

### ✅ **Enriquecimento Inteligente**
30 campos enriquecidos + ancoragem de autoestudos + detecção automática

### ✅ **Organização Automática**
Pasta por turma + 3 formatos + timestamping → Zero confusão, máxima organização

### ✅ **Interface Limpa**
Documentação organizada + projeto estruturado → Profissional e fácil de usar

---

## 🚀 **PRONTO PARA USO!**

**Execute agora:**
```bash
python adalove_extractor.py
```

1. ✅ Digite o nome da turma para organização
2. ✅ Login automático (ou manual se necessário)  
3. ✅ Selecione a turma na interface da página
4. ✅ Aguarde extração completa de todas as semanas
5. ✅ Aguarde enriquecimento automático dos dados
6. ✅ Dados completos salvos em 3 formatos: `dados_extraidos/nome_turma/`
   - `cards_completos_TIMESTAMP.csv` (básico)
   - `cards_enriquecidos_TIMESTAMP.csv` (completo)
   - `cards_enriquecidos_TIMESTAMP.jsonl` (JSON Lines)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - uma das licenças open source mais permissivas.

### MIT License

```
Copyright (c) 2025 Fernando Bertholdo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 🌟 **Contribuições**
- **Projeto original**: [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards)
- **Esta versão**: Desenvolvida e expandida por Fernando Bertholdo

### ⚖️ **Responsabilidade**
- Este software é fornecido "como está", sem garantias
- O uso é por **conta e risco** do usuário
- **Fins acadêmicos e educacionais** recomendados
- Respeite os **termos de uso** da plataforma AdaLove

---

**🎉 Ferramenta completa para extração acadêmica do AdaLove com enriquecimento inteligente de dados!**
