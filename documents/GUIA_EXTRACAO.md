# 🎯 AdaLove Cards Extractor - Guia de Extração

## 📋 Versão Atual: Script Único

**IMPORTANTE**: Este projeto agora utiliza **um único script** para todas as operações de extração:

### 🚀 **Script Principal: `adalove_extractor.py`**

- ✅ **Status**: Produção - Totalmente funcional
- 🎯 **Propósito**: Extração completa com enriquecimento automático
- 📊 **Recursos**: 
  - Descobre semanas automaticamente
  - Extrai dados completos (10 campos básicos)
  - Enriquece dados (30 campos totais)
  - Ancora autoestudos às instruções
  - Salva 3 formatos (CSV básico, CSV enriquecido, JSONL)
  - Logs detalhados
  - Organização automática por turma
- ⏱️ **Uso**: Para qualquer extração (rápida ou completa)

---

## 📁 Arquivos Históricos

Os seguintes arquivos estão preservados apenas para referência histórica:

### 💾 `main_completo_original.py` - **LEGADO**
- ⚠️ **Status**: Backup histórico (não usar)
- 🎯 **Propósito**: Script original antes da reformulação
- 📝 **Nota**: Mantido apenas para referência

### 🗂️ Pasta `arquivos_antigos/` - **LEGADO**
- ⚠️ **Status**: Arquivos de desenvolvimento (não usar)
- 🎯 **Propósito**: Versões antigas durante o desenvolvimento
- 📝 **Nota**: Mantidos apenas para histórico

---

## 🚀 Como Usar - Guia Passo a Passo

### **Passo 1: Preparação do Ambiente**

```bash
# 1. Clone ou baixe o projeto
git clone <repository-url>
cd adalove_extract_cards

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Instale o navegador Chromium
playwright install chromium
```

### **Passo 2: Configuração de Credenciais**

```bash
# 1. Copie o arquivo de exemplo
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows

# 2. Edite o arquivo .env com suas credenciais
# Abra com seu editor preferido e preencha:
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

### **Passo 3: Execução**

```bash
# Execute o script principal
python adalove_extractor.py
```

### **Passo 4: Interação Durante a Execução**

1. **Digite o nome da turma**:
   ```
   📁 Digite o nome da turma para organizar os dados: modulo6
   ```
   - Este nome será usado para criar a pasta de organização
   - Use nomes descritivos (ex: `modulo6`, `ES06-2025`, `2025-1B-T13`)

2. **Aguarde o login automático**:
   - O script tentará fazer login automaticamente
   - Se falhar, você verá uma mensagem para fazer login manualmente
   - Pressione Enter após fazer login manualmente

3. **Selecione a turma na interface**:
   ```
   👆 Agora selecione a turma na interface:
   ⏸️ Pressione Enter após selecionar a turma na página:
   ```
   - Clique no dropdown de turmas na página do AdaLove
   - Selecione a turma desejada
   - Aguarde a página carregar
   - Pressione Enter no terminal

4. **Aguarde a extração**:
   - O script processará todas as semanas automaticamente
   - Você verá o progresso em tempo real
   - Não feche o navegador ou o terminal

---

## 📊 Dados Extraídos

### Formato 1: CSV Básico (`cards_completos_*.csv`)
**10 campos principais:**
- `semana` - Nome da semana (ex: "Semana 01")
- `indice` - Posição do card na semana
- `id` - ID único do card
- `titulo` - Título do card
- `descricao` - Descrição do card
- `tipo` - Tipo do card (Atividade, Projeto, etc.)
- `texto_completo` - Texto completo do card
- `links` - Links externos encontrados
- `materiais` - Materiais do Google (Drive, Docs, etc.)
- `arquivos` - Arquivos anexados (PDF, DOC, etc.)

### Formato 2: CSV Enriquecido (`cards_enriquecidos_*.csv`)
**30 campos totais** incluindo os 10 básicos + 20 enriquecidos:

#### Campos de Tempo:
- `semana_num` - Número da semana (ex: 1, 2, 3...)
- `sprint` - Número do sprint (ex: 1, 2, 3...)
- `data_ddmmaaaa` - Data em formato dd/mm/aaaa
- `hora_hhmm` - Hora em formato HH:MM
- `data_hora_iso` - Data/hora em formato ISO 8601

#### Campos de Classificação:
- `professor` - Nome do professor (detectado automaticamente)
- `is_instrucao` - True se é uma instrução/encontro
- `is_autoestudo` - True se é um autoestudo
- `is_atividade_ponderada` - True se é atividade com nota

#### Campos de Ancoragem:
- `parent_instruction_id` - ID da instrução relacionada
- `parent_instruction_title` - Título da instrução relacionada
- `anchor_method` - Método usado para ancoragem
- `anchor_confidence` - Confiança da ancoragem (high/medium/low)

#### Campos de URLs:
- `links_urls` - URLs de links normalizadas
- `materiais_urls` - URLs de materiais normalizadas
- `arquivos_urls` - URLs de arquivos normalizadas
- `num_links` - Número de links
- `num_materiais` - Número de materiais
- `num_arquivos` - Número de arquivos

#### Outros:
- `record_hash` - Hash único do registro para integridade

### Formato 3: JSONL (`cards_enriquecidos_*.jsonl`)
Mesmo conteúdo do CSV enriquecido, mas em formato JSON Lines (um JSON por linha).

**Vantagens do JSONL:**
- ✅ Melhor para pipelines de processamento
- ✅ Arrays preservados (não precisam ser strings separadas por |)
- ✅ Fácil de processar linha a linha
- ✅ Compatível com ferramentas de Big Data

---

## 📁 Estrutura de Saída

Cada execução cria 3 arquivos na pasta da turma:

```
dados_extraidos/
└── nome_turma/
    ├── cards_completos_20250826_220413.csv       # Dados básicos
    ├── cards_enriquecidos_20250826_220413.csv    # Dados enriquecidos
    └── cards_enriquecidos_20250826_220413.jsonl  # Formato JSONL
```

---

## 🔧 Configuração Avançada

### Dependências de Desenvolvimento

Se você quiser analisar os dados extraídos com Python, instale também as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Isso instala:
- `pandas` - Para análise de dados
- `numpy` - Para operações numéricas
- Outras bibliotecas úteis para análise

### Exemplo de Análise com Pandas

```python
import pandas as pd

# Carregar dados enriquecidos
df = pd.read_csv('dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.csv')

# Ver estatísticas básicas
print(f"Total de cards: {len(df)}")
print(f"Total de semanas: {df['semana_num'].nunique()}")

# Filtrar autoestudos
autoestudos = df[df['is_autoestudo'] == True]
print(f"Total de autoestudos: {len(autoestudos)}")

# Ver ancoragem de autoestudos
ancorados = autoestudos[autoestudos['parent_instruction_id'].notna()]
print(f"Autoestudos ancorados: {len(ancorados)}")
print(f"Taxa de ancoragem: {len(ancorados)/len(autoestudos)*100:.1f}%")

# Ver distribuição de confiança
print("\nDistribuição de confiança de ancoragem:")
print(ancorados['anchor_confidence'].value_counts())

# Cards por tipo
print("\nCards por tipo:")
print(df['tipo'].value_counts())

# Cards com materiais
print(f"\nCards com links: {(df['num_links'] > 0).sum()}")
print(f"Cards com materiais: {(df['num_materiais'] > 0).sum()}")
print(f"Cards com arquivos: {(df['num_arquivos'] > 0).sum()}")
```

---

## 🎯 Casos de Uso

### **Caso 1: Extração Rápida para Backup**
```bash
# Execute o script normalmente
python adalove_extractor.py

# Você terá 3 formatos de backup
# Use o CSV básico para visualização rápida
```

### **Caso 2: Análise de Dados Acadêmicos**
```bash
# Execute o script
python adalove_extractor.py

# Use o CSV enriquecido para análises
# Campos como professor, tipo, datas permitem análises profundas
```

### **Caso 3: Integração com Outras Ferramentas**
```bash
# Execute o script
python adalove_extractor.py

# Use o JSONL para pipelines de processamento
# Fácil de importar em ferramentas de Big Data ou análise
```

### **Caso 4: Acompanhamento de Mudanças**
```bash
# Execute periodicamente (ex: semanal)
python adalove_extractor.py

# Compare os hashes (record_hash) entre execuções
# Identifique cards novos, modificados ou removidos
```

---

## 🚨 Resolução de Problemas

### Problema: "Nenhum card encontrado"
**Possíveis causas:**
- Turma não foi selecionada corretamente
- Página não carregou completamente
- Turma não tem cards

**Solução:**
1. Certifique-se de selecionar a turma no dropdown
2. Aguarde a página carregar completamente (3-5 segundos)
3. Pressione Enter apenas quando ver os cards na página

### Problema: "Modal não fecha"
**Possíveis causas:**
- Conexão lenta
- Navegador travado

**Solução:**
- O script tem múltiplas estratégias de fechamento
- Se travar, pressione ESC manualmente no navegador
- O script continuará automaticamente

### Problema: "Login falhou"
**Possíveis causas:**
- Credenciais incorretas no .env
- Redirecionamento do Google mudou

**Solução:**
1. Verifique o arquivo .env
2. Use o modo de fallback manual quando solicitado
3. Complete o login manualmente e pressione Enter

---

## 📚 Recursos Adicionais

### Documentação Complementar
- `README.md` - Documentação principal completa
- `DADOS_EXTRAIDOS.md` - Especificações dos dados (legado)
- `README_reformulacao.md` - Histórico da reformulação

### Logs
Todos os logs são salvos em:
```
logs/nome_turma_TIMESTAMP.log
```

Use os logs para:
- ✅ Depurar problemas
- ✅ Verificar o progresso da extração
- ✅ Auditar operações realizadas

---

## 🎉 Resumo

**Um único comando:**
```bash
python adalove_extractor.py
```

**Três arquivos gerados:**
1. `cards_completos_*.csv` - Dados básicos (10 campos)
2. `cards_enriquecidos_*.csv` - Dados completos (30 campos)
3. `cards_enriquecidos_*.jsonl` - Formato JSON Lines

**Zero configuração complexa:**
- ✅ Um script
- ✅ Um comando
- ✅ Tudo automático
- ✅ Três formatos
- ✅ Organização por turma

---

**🚀 Pronto para extrair dados acadêmicos do AdaLove!**
