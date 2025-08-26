# 🚀 Adalove Extract Cards v2

> **📋 DISCLAIMER**: Este projeto tem **fins puramente acadêmicos e educacionais**, visando otimizar o aprendizado e organização de materiais de estudo. O autor não se responsabiliza pelo uso inadequado da ferramenta. Use por sua conta e risco, respeitando os termos de uso da plataforma AdaLove e políticas institucionais.

**Extração completa e automatizada de cards do AdaLove com organização inteligente por turma**

## 🌟 Inspiração e Origem

Este projeto foi **inspirado e desenvolvido a partir** do trabalho original de [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards). A versão atual representa uma **evolução significativa** com funcionalidades expandidas, organização aprimorada e extração completa de materiais acadêmicos.

## 📋 O Que Este Script Faz

✅ **Login automático** na plataforma AdaLove  
✅ **Extração completa** de todos os cards de todas as semanas  
✅ **Captura links e materiais** anexados aos cards (Google Drive, PDFs, etc.)  
✅ **Organização automática** por pasta da turma com nome personalizado  
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
<!-- criar e ativar venv -->
python -m venv venv
.\venv\Scripts\activate

<!-- # atualizar pip e instalar dependências -->
python -m pip install --upgrade pip
pip install -r requirements.txt

<!-- # instala o navegador usado pelo Playwright -->
playwright install chromium 
```

# Configurar credenciais no .env (copie do .env.example)
```
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

### 2. **Execução**
```bash
python adalove_extractor.py
```

### 3. **Processo Automatizado**
```
📁 Digite nome da turma: [SEU_INPUT] → Cria pasta organizada
🔑 Login automático → Credenciais do .env  
👆 Selecione turma na interface → Manual (mais confiável)
⚙️ Extração automática → Todas as semanas
💾 Salvamento → dados_extraidos/SEU_INPUT/cards_completos_TIMESTAMP.csv
```

---

## 📊 Dados Extraídos (Conteúdo Acadêmico Completo)

Para cada card, o script captura **TODOS os materiais acadêmicos**:

### ✅ **Conteúdo Principal**
- 📝 **Título e descrição** completos
- 📄 **Texto completo** do card
- 🏷️ **Tipo** (Atividade, Projeto, Material, etc.)
- 📅 **Semana** e posição

### ✅ **Materiais Anexados**
- 🔗 **Links externos** encontrados no card
- 📎 **Google Drive, Docs, Sheets** automaticamente categorizados
- 📁 **Arquivos** (PDFs, DOCs, PPTs, etc.) identificados
- 🖼️ **Imagens** e outros recursos capturados

### 📊 **Exemplo de Saída CSV:**
```csv
semana,indice,id,titulo,descricao,tipo,links,materiais,arquivos,texto_completo
Semana 01,1,card-123,"Intro Python","Conceitos básicos","Atividade","Link: https://example.com","Google Drive: https://drive.google.com/...","exercicios.pdf: https://...","Texto completo do card..."
Semana 01,2,card-124,"Git Básico","Controle de versão","Material","","Docs: https://docs.google.com/...","tutorial.pdf: https://...","Git Básico\nControle de versão\nComandos essenciais..."
```

---

## 📁 Organização Automática por Turma

### 🎯 **Como Funciona**
O script solicita o **nome da turma** no início e cria automaticamente a estrutura organizacional:

### **Exemplo de Uso:**
```bash
$ python adalove_extractor.py
📁 Digite o nome da turma para organizar os dados: 2025-1B-T13
```

### **Resultado Automático:**
```
dados_extraidos/
└── 2025-1B-T13/
    └── cards_completos_20250825_194523.csv
```

### **Múltiplas Turmas:**
```
dados_extraidos/
├── 2025-1B-T13/
│   ├── cards_completos_20250825_194523.csv
│   └── cards_completos_20250826_143012.csv
├── ES06-2025/
│   └── cards_completos_20250825_201538.csv
└── outro_modulo/
    └── cards_completos_20250826_084521.csv
```

### ✅ **Vantagens da Organização:**
- 📁 **Pasta individual** para cada turma
- 🔄 **Timestamping** evita sobrescrever dados
- 📚 **Histórico preservado** de todas as extrações
- 🔍 **Fácil localização** dos dados por turma

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
- ✅ **Estatísticas finais** da extração
- ❌ **Erros** com contexto para debug

### **Exemplo de Log:**
```
14:30:15 | INFO | 🚀 Iniciando extração para turma: 2025-1B-T13
14:30:16 | INFO | 🔑 Fazendo login...
14:30:20 | INFO | ✅ Login realizado!
14:30:23 | INFO | 🔍 Descobrindo semanas disponíveis...
14:30:25 | INFO | 📊 10 semanas descobertas
14:30:27 | INFO | 🔄 Semana 01 (1/10)
14:30:30 | INFO |    ✅ 14 cards encontrados
14:30:35 | INFO |    📊 14 cards processados com sucesso
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
├── 📦 requirements.txt             # Dependências Python
├── 📚 documents/                   # Documentação técnica detalhada
│   ├── README_reformulacao.md      # Histórico da reformulação
│   ├── GUIA_EXTRACAO.md           # Guias técnicos
│   └── DADOS_EXTRAIDOS.md         # Especificações dos dados
├── 💾 dados_extraidos/            # DADOS ORGANIZADOS POR TURMA
│   ├── README.md                   # Explica organização dos dados
│   ├── turma_2025-1B-T13/        # Exemplo de pasta de turma
│   └── turma_ES06/                # Outra pasta de turma
├── 📝 logs/                        # Logs das execuções
├── 🗂️ arquivos_antigos/           # Scripts de desenvolvimento (histórico)
└── ⚙️ venv/                       # Ambiente virtual Python
```

---

## ⚡ Exemplo de Execução Completa

```bash
$ python adalove_extractor.py

🚀 ADALOVE CARDS EXTRACTOR - VERSÃO FINAL
📋 Este script faz extração completa incluindo:
   ✅ Títulos e descrições dos cards
   ✅ Links e materiais anexados  
   ✅ Arquivos e documentos
   ✅ Organização por pasta da turma

📁 Digite o nome da turma para organizar os dados: 2025-1B-T13
🔑 Fazendo login...
✅ Login realizado!
🏠 Navegando para academic-life...
📁 Dados serão salvos em: dados_extraidos/2025-1B-T13/
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

🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!
📊 127 cards extraídos
📚 10 semanas processadas  
🔗 89 cards com links
📎 67 cards com materiais
📁 Pasta: dados_extraidos/2025-1B-T13/
💾 Arquivo: cards_completos_20250825_194523.csv
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
  - ✅ Texto completo preservado

#### **🗂️ Sistema de Organização:**
- **Script Original**: Salvamento simples
- **Esta Versão**: **Organização inteligente**:
  - ✅ Pastas automáticas por turma (nome personalizado)
  - ✅ Timestamping para preservar histórico
  - ✅ Estrutura de projeto profissional

#### **🔧 Robustez e Confiabilidade:**
- **Script Original**: Automação básica
- **Esta Versão**: **Sistema inteligente**:
  - ✅ Login com fallback manual
  - ✅ Descoberta automática de semanas
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
  - ✅ Organização automática por turma
  - ✅ Salva CSV otimizado
  - ✅ Logs detalhados
  - ✅ Interface confiável

### 🏆 **Principais Inovações desta Versão:**

1. **📎 Extração de Materiais Acadêmicos**
   - Captura **todos os links e arquivos** dos cards
   - **Categorização automática** (links, materiais, arquivos)
   - **Preservação completa** do conteúdo acadêmico

2. **🗂️ Organização por Turma**
   - **Input personalizado** do nome da turma
   - **Criação automática** de estrutura de pastas
   - **Histórico preservado** de todas as extrações

3. **🔧 Sistema de Logs Avançado**
   - **Logs detalhados** por turma e timestamp
   - **Debug facilitado** com contexto completo
   - **Acompanhamento** de cada etapa da extração

4. **🎯 Interface Inteligente**
   - **Seleção manual** da turma (mais confiável)
   - **Login com fallback** (automático + manual)
   - **Descoberta automática** de semanas disponíveis

---

## 🚨 Pontos Importantes

### ⚙️ **Configuração Necessária**
- **Arquivo `.env`**: Configure suas credenciais (use `.env.example` como base)
- **Dependências**: Execute `pip install playwright python-dotenv`
- **Playwright**: Execute `playwright install chromium`

### 🧩 Dependências mínimas x extras (dev)
O projeto agora separa as dependências em dois conjuntos:

- `requirements.txt` → dependências mínimas necessárias para executar o extractor (recomendado para a maioria dos usuários).
- `requirements-dev.txt` → pacotes opcionais/extra para análises, relatórios e desenvolvimento (p.ex. `pandas`, `numpy`).

Instalação (ambiente virtual ativado):

Instalar apenas o necessário para rodar o extractor:
```bash
pip install -r requirements.txt
playwright install chromium
```

Instalar também as dependências de desenvolvimento/analise:
```bash
pip install -r requirements-dev.txt
```

Manter essa separação reduz o tempo de instalação e o tamanho do ambiente para quem só precisa executar a extração.

### 🎯 **Processo de Uso**
- **Seleção manual** da turma é **intencional** (mais confiável que automação)
- **Nome da turma** é solicitado para **organização automática**
- **Dados nunca são sobrescritos** (timestamping automático)

### 📊 **Resultados**
- **CSV completo** com todos os dados acadêmicos
- **Organização por turma** em pastas separadas
- **Logs detalhados** para qualquer troubleshooting necessário

---

## 🏆 Resumo Final

### ✅ **1 Script para Tudo**
`adalove_extractor.py` → Solução completa e definitiva

### ✅ **Extração Acadêmica Total**
Links, materiais, arquivos, Google Drive → Tudo que um módulo contém

### ✅ **Organização Automática**
Pasta por turma + timestamping → Zero confusão, máxima organização

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
5. ✅ Dados completos salvos em `dados_extraidos/nome_turma/`

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

**🎉 Ferramenta completa para extração acadêmica do AdaLove!**
