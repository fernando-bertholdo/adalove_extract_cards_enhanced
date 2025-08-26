# 🎯 AdaLove Cards Extractor - Versões Disponíveis

Baseado nos logs de sucesso da validação, agora você tem **3 opções** para extração:

## 📋 Opções Disponíveis

### 1. 🧪 `main_completo.py` - **VALIDAÇÃO/TESTE**
- ✅ **Status**: Funcionando (validado com sucesso)
- 🎯 **Propósito**: Apenas testa acesso e conta cards
- 📊 **Resultado**: 3/3 semanas, 60 cards encontrados
- ⏱️ **Uso**: Para testar se a automação está funcionando

### 2. 🚀 `extrator_completo.py` - **EXTRAÇÃO COMPLETA** 
- ✅ **Status**: Novo, baseado no teste validado
- 🎯 **Propósito**: Extração completa com máximo de dados
- 📊 **Recursos**: 
  - Descobre semanas automaticamente
  - Extrai múltiplos campos por card
  - Salva CSV + JSON + Relatório
  - Logs detalhados
- ⏱️ **Uso**: Para extração completa e análise profunda

### 3. ⚡ `extrator_simples.py` - **EXTRAÇÃO RÁPIDA**
- ✅ **Status**: Novo, otimizado para velocidade
- 🎯 **Propósito**: Extração essencial e eficiente
- 📊 **Recursos**:
  - Seleção manual de turma (mais confiável)
  - Extrai dados básicos dos cards
  - Salva apenas CSV
  - Logs simplificados
- ⏱️ **Uso**: Para extração rápida do dia-a-dia

## 🛠️ Como Escolher?

### Para **PRIMEIRA EXECUÇÃO**:
```bash
# 1. Primeiro, valide se tudo está funcionando:
python main_completo.py

# 2. Se passou no teste, escolha sua versão:
```

### Para **ANÁLISE DETALHADA**:
```bash
python extrator_completo.py
```
- Extrai TUDO: título, descrição, tipo, datas, links, etc.
- Gera relatório completo
- Melhor para análises e relatórios

### Para **USO DIÁRIO/RÁPIDO**:
```bash  
python extrator_simples.py
```
- Foco no essencial: título, descrição, texto completo
- Mais rápido e direto
- Melhor para atualizações regulares

## 📁 Estrutura de Arquivos

```
adalove_extract_cards/
├── main_completo.py          # ✅ Teste/Validação
├── extrator_completo.py      # 🚀 Extração completa  
├── extrator_simples.py       # ⚡ Extração rápida
├── main_completo_original.py # 💾 Backup do original
├── .env                      # 🔐 Credenciais
├── logs/                     # 📝 Todos os logs
│   ├── adalove_extraction_*.log
│   ├── extracao_completa_*.log
│   └── extracao_simples_*.log
└── dados_extraidos/          # 💾 Dados extraídos
    ├── cards_adalove_*.csv
    ├── cards_adalove_*.json
    └── relatorio_extracao_*.txt
```

## ⚙️ Configuração

### Todas as versões usam:
- 🔐 Login automático (com fallback manual)
- 🏠 Navegação direta para `/academic-life` 
- 🎯 **Seleção manual de turma** (mais confiável)
- 📝 Sistema de logging
- 💾 Salvamento automático

### Diferenças principais:

| Característica | Teste | Completo | Simples |
|----------------|-------|----------|---------|
| **Extração** | ❌ Não | ✅ Completa | ✅ Básica |
| **Campos extraídos** | 0 | 10+ | 6 |
| **Formatos salvos** | Nenhum | CSV+JSON | CSV |
| **Relatório** | ❌ | ✅ Detalhado | ❌ |
| **Velocidade** | Rápido | Médio | Rápido |
| **Logs** | Detalhado | Muito detalhado | Simples |

## 🎯 Recomendação

### **Para começar AGORA**:
1. Execute `python extrator_simples.py`
2. Faça a seleção manual da turma
3. Deixe rodar todas as semanas
4. Analise o CSV gerado

### **Para análise completa**:
1. Use `extrator_completo.py` quando precisar de dados detalhados
2. Terá JSON de backup e relatório completo

## 🚨 Pontos Importantes

### ✅ **Seleção Manual de Turma**
- **Mantida por design** (mais confiável que automação)
- Leva ~30 segundos
- Evita erros de automação
- Funciona com qualquer turma

### 📊 **Dados Extraídos**
- **Completo**: id, título, descrição, tipo, data, links, texto completo
- **Simples**: título, descrição, texto completo
- Ambos salvam semana e índice do card

### 🔄 **Próximas Execuções**
- Dados salvos com timestamp
- Não sobrescreve extrações anteriores
- Logs separados por sessão

## 🚀 Execução Imediata

Se quiser começar agora:

```bash
# Extração rápida e eficiente:
python extrator_simples.py

# Quando aparecer a tela de seleção:
# 1. Clique no dropdown de turmas na página
# 2. Digite/selecione sua turma (ex: 2025-1B-T13)
# 3. Pressione Enter no terminal
# 4. Aguarde a extração de todas as semanas
```

O script processará automaticamente todas as semanas e salvará os dados em CSV! 🎉
