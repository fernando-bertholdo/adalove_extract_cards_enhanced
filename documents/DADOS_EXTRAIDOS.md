# 📊 Dados Extraídos - Campos Disponíveis

## 🎯 Versão Simples (extrator_simples.py)

### Campos Básicos:
```csv
semana,indice,id,titulo,descricao,texto_completo
```

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `semana` | Nome da semana processada | "Semana 01" |
| `indice` | Número do card na semana | 1, 2, 3... |
| `id` | ID único do card (se disponível) | "card-123-abc" |
| `titulo` | Primeira linha do card | "Atividade de Python" |
| `descricao` | Resto do texto do card | "Exercícios sobre loops..." |
| `texto_completo` | Todo o texto do card | "Atividade de Python\nExercícios..." |

## 🚀 Versão Completa (extrator_completo.py)

### Campos Avançados:
```csv
semana,indice,id,titulo,descricao,tipo,status,data_entrega,tags,link,texto_completo
```

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `semana` | Nome da semana | "Semana 01" |
| `indice` | Posição do card | 1, 2, 3... |
| `id` | ID único | "card-123-abc" |
| `titulo` | Título/nome da atividade | "Atividade de Python" |
| `descricao` | Descrição detalhada | "Exercícios sobre loops e condicionais" |
| `tipo` | Tipo/categoria | "Atividade", "Projeto", "Quiz" |
| `status` | Status do card | "Pendente", "Concluído" |
| `data_entrega` | Data limite | "2025-08-30 23:59" |
| `tags` | Tags/marcadores | "python, programação" |
| `link` | URL do card (se houver) | "https://adalove.../card/123" |
| `texto_completo` | Texto integral | Todo o conteúdo do card |

## 📋 Exemplos de Dados

### Exemplo CSV Simples:
```csv
semana,indice,id,titulo,descricao,texto_completo
Semana 01,1,card-python-1,"Introdução ao Python","Conceitos básicos de variáveis","Introdução ao Python\nConceitos básicos de variáveis\nExercícios práticos"
Semana 01,2,card-git-1,"Git e GitHub","Controle de versão","Git e GitHub\nControle de versão\nRepositórios e commits"
```

### Exemplo CSV Completo:
```csv
semana,indice,id,titulo,descricao,tipo,status,data_entrega,tags,link,texto_completo
Semana 01,1,card-python-1,"Introdução ao Python","Conceitos básicos","Atividade","","2025-08-30","python,básico","","Introdução ao Python\nConceitos básicos de variáveis\nExercícios práticos"
Semana 02,1,card-projeto-1,"Projeto Final","Desenvolvimento completo","Projeto","Em andamento","2025-09-15","projeto,python","https://adalove.../123","Projeto Final\nDesenvolvimento completo de uma aplicação\nCritérios de avaliação..."
```

## 📊 Estatísticas dos Dados

Com base no teste validado:
- ✅ **3 semanas processadas**
- ✅ **60 cards extraídos** (14 + 23 + 23)
- ✅ **Taxa de sucesso: 100%**

### Distribuição por Semana:
- **Semana 01**: 14 cards
- **Semana 02**: 23 cards  
- **Semana 03**: 23 cards

## 🔍 Como Analisar os Dados

### 1. **Contagem por Semana:**
```python
import pandas as pd
df = pd.read_csv('cards_extracao_TIMESTAMP.csv')
print(df['semana'].value_counts())
```

### 2. **Cards por Tipo:**
```python
# Apenas versão completa
print(df['tipo'].value_counts())
```

### 3. **Análise de Títulos:**
```python
print(df['titulo'].str.len().describe())  # Estatísticas dos títulos
```

### 4. **Busca por Palavra-chave:**
```python
python_cards = df[df['texto_completo'].str.contains('python', case=False)]
print(f"Cards sobre Python: {len(python_cards)}")
```

## 💡 Dicas de Uso

### ✅ **Dados Limpos**:
- Texto completo preservado
- Quebras de linha mantidas  
- Encoding UTF-8 correto
- Headers padronizados

### ⚡ **Performance**:
- **Simples**: ~2-3 minutos para 10 semanas
- **Completo**: ~5-8 minutos para 10 semanas

### 🔄 **Atualizações**:
- Cada execução gera novo arquivo
- Timestamp no nome do arquivo
- Não sobrescreve dados anteriores

## 📁 Estrutura dos Arquivos

```
dados_extraidos/
├── cards_extracao_20250825_183045.csv      # Versão simples
├── cards_adalove_20250825_184512.csv       # Versão completa  
├── cards_adalove_20250825_184512.json      # Backup JSON
└── relatorio_extracao_20250825_184512.txt  # Relatório
```

## 🎯 Próximos Passos

### Para Análise:
1. Abrir CSV no Excel/Google Sheets
2. Filtrar por semana/tipo
3. Analisar distribuição de atividades

### Para Automação:
1. Executar periodicamente
2. Comparar dados entre execuções
3. Identificar novos cards adicionados

### Para Relatórios:
1. Usar Python/pandas para análises
2. Gerar gráficos de distribuição
3. Criar dashboard com dados
