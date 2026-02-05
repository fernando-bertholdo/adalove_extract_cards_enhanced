# 📁 Arquivos Gerados - Guia Completo

## 🎯 Visão Geral

Cada execução do `adalove_extractor.py` gera **3 arquivos** na pasta da turma:

```
dados_extraidos/
└── nome_turma/
    ├── cards_completos_TIMESTAMP.csv         # 10 campos básicos
    ├── cards_enriquecidos_TIMESTAMP.csv      # 30 campos completos
    └── cards_enriquecidos_TIMESTAMP.jsonl    # 30 campos (JSON)
```

**TIMESTAMP**: `YYYYMMDD_HHMMSS` (ex: `20250826_220413`)

---

## 📊 Arquivo 1: CSV Básico

### `cards_completos_TIMESTAMP.csv`

**Descrição**: Dados brutos extraídos diretamente da plataforma AdaLove.

**Campos (10 colunas):**

| # | Campo | Tipo | Descrição | Exemplo |
|---|-------|------|-----------|---------|
| 1 | `semana` | string | Nome da semana | `"Semana 01"` |
| 2 | `indice` | int | Posição do card na semana | `1`, `2`, `3`... |
| 3 | `id` | string | ID único do card | `"46d403bdd15b..."` |
| 4 | `titulo` | string | Primeira linha do card | `"Workshop com Parceiro"` |
| 5 | `descricao` | string | Resto do texto | `"24/04/2025 - 14:00h"` |
| 6 | `tipo` | string | Tipo do card | `"Atividade"`, `"Projeto"`, `"Material"`, `"Outros"` |
| 7 | `texto_completo` | string | Texto completo (card + modal) | `"Workshop...\n24/04..."` |
| 8 | `links` | string | Links externos (pipe-separated) | `"Link: https://... \| Link: ..."` |
| 9 | `materiais` | string | Materiais Google (pipe-separated) | `"Drive: https://... \| Docs: ..."` |
| 10 | `arquivos` | string | Arquivos anexados (pipe-separated) | `"ex.pdf: https://... \| ..."` |

### Exemplo de Registro:

```csv
semana,indice,id,titulo,descricao,tipo,texto_completo,links,materiais,arquivos
Semana 01,1,46d403b,"Workshop com Parceiro","24/04/2025 - 14:00h","Outros","Workshop com Parceiro\n\n24/04/2025 - 14:00h","","",""
Semana 01,2,6ec59e1,"Filtragem Colaborativa","25/04/2025 - 14:00h\nOvidio Lopes","Atividade","Filtragem Colaborativa...\n25/04/2025...","Link: https://example.com","Material: https://drive.google.com/xyz",""
```

### Quando Usar:
- ✅ Visualização rápida no Excel/Google Sheets
- ✅ Busca simples por texto
- ✅ Compartilhar com pessoas não-técnicas
- ✅ Importar em ferramentas de BI simples

---

## 🔬 Arquivo 2: CSV Enriquecido

### `cards_enriquecidos_TIMESTAMP.csv`

**Descrição**: Dados processados com campos derivados e relacionamentos inteligentes.

**Campos (30 colunas):** 10 básicos + 20 enriquecidos

#### Campos Básicos (10):
- `semana`, `indice`, `id`, `titulo`, `descricao`, `tipo`
- `texto_completo`, `links`, `materiais`, `arquivos`

#### Campos Enriquecidos (20):

**Temporais (5):**
- `semana_num` - Número da semana (int)
- `sprint` - Número do sprint (int)
- `data_ddmmaaaa` - Data brasileira (string)
- `hora_hhmm` - Hora 24h (string)
- `data_hora_iso` - ISO 8601 (string)

**Identificação (1):**
- `professor` - Nome detectado (string)

**Classificação (3):**
- `is_instrucao` - É instrução/encontro (bool)
- `is_autoestudo` - É autoestudo (bool)
- `is_atividade_ponderada` - É atividade avaliada (bool)

**Ancoragem (4):**
- `parent_instruction_id` - ID da instrução relacionada (string)
- `parent_instruction_title` - Título da instrução (string)
- `anchor_method` - Método de ancoragem (string)
- `anchor_confidence` - Confiança (high/medium/low)

**URLs Normalizadas (6):**
- `links_urls` - URLs de links (string pipe-separated)
- `materiais_urls` - URLs de materiais (string pipe-separated)
- `arquivos_urls` - URLs de arquivos (string pipe-separated)
- `num_links` - Quantidade de links (int)
- `num_materiais` - Quantidade de materiais (int)
- `num_arquivos` - Quantidade de arquivos (int)

**Integridade (1):**
- `record_hash` - Hash SHA1 único (string)

### Exemplo de Registro:

```csv
semana_num,sprint,data_hora_iso,professor,is_instrucao,is_autoestudo,is_atividade_ponderada,parent_instruction_id,anchor_confidence,num_links
1,1,"2025-04-24T14:00:00-03:00","",True,False,False,"","",0
1,1,"2025-04-25T14:00:00-03:00","Ovidio Lopes da Cruz Netto",True,False,False,"","",1
```

### Quando Usar:
- ✅ Análises avançadas com pandas/Python
- ✅ Filtrar por professor, sprint, classificação
- ✅ Analisar ancoragens de autoestudos
- ✅ Calcular estatísticas por período
- ✅ Detectar mudanças com hash
- ✅ Integrar com ferramentas analíticas

---

## 📦 Arquivo 3: JSONL

### `cards_enriquecidos_TIMESTAMP.jsonl`

**Descrição**: Mesmo conteúdo do CSV enriquecido, mas em formato JSON Lines.

**Formato**: Um objeto JSON por linha.

### Exemplo de Registro:

```json
{
  "semana": "Semana 01",
  "semana_num": 1,
  "sprint": 1,
  "indice": 1,
  "id": "46d403bdd15b4fe8a68dbf1e9880f00c",
  "titulo": "Workshop com Parceiro",
  "descricao": "24/04/2025 - 14:00h",
  "tipo": "Outros",
  "data_ddmmaaaa": "24/04/2025",
  "hora_hhmm": "14:00",
  "data_hora_iso": "2025-04-24T14:00:00-03:00",
  "professor": null,
  "is_instrucao": true,
  "is_autoestudo": false,
  "is_atividade_ponderada": false,
  "parent_instruction_id": null,
  "parent_instruction_title": null,
  "anchor_method": null,
  "anchor_confidence": null,
  "links_urls": "",
  "materiais_urls": "",
  "arquivos_urls": "",
  "num_links": 0,
  "num_materiais": 0,
  "num_arquivos": 0,
  "record_hash": "93fa506122e2fa6d6019741b0a42ed3912b2ded2",
  "texto_completo": "Workshop com Parceiro\n\n24/04/2025 - 14:00h",
  "links": "",
  "materiais": "",
  "arquivos": ""
}
```

### Vantagens do JSONL:
- ✅ **Streaming**: Pode ser processado linha a linha (eficiente para arquivos grandes)
- ✅ **Tipos nativos**: Booleanos e números preservados (não são strings)
- ✅ **Compatibilidade**: Funciona com BigQuery, Spark, etc.
- ✅ **Arrays**: URLs podem ser arrays JSON (não strings pipe-separated)
- ✅ **Padrão moderno**: Usado em pipelines de dados modernos

### Quando Usar:
- ✅ Pipelines de processamento em lote
- ✅ Importar para BigQuery, Snowflake, etc.
- ✅ Integração com ferramentas modernas de dados
- ✅ Streaming/processamento incremental
- ✅ APIs e serviços web

### Como Usar JSONL:

#### Python:
```python
import json

# Ler linha a linha
with open('cards_enriquecidos_*.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        print(card['titulo'])

# Com pandas
import pandas as pd
df = pd.read_json('cards_enriquecidos_*.jsonl', lines=True)
```

#### jq (command line):
```bash
# Filtrar autoestudos
cat cards_enriquecidos_*.jsonl | jq 'select(.is_autoestudo == true)'

# Contar por tipo
cat cards_enriquecidos_*.jsonl | jq '.tipo' | sort | uniq -c

# Extrair campos específicos
cat cards_enriquecidos_*.jsonl | jq '{titulo, data_ddmmaaaa, professor}'
```

---

## 📏 Tamanho dos Arquivos

### Estimativas (para ~150 cards):
- **CSV Básico**: ~500 KB - 2 MB
- **CSV Enriquecido**: ~800 KB - 3 MB
- **JSONL**: ~1 MB - 4 MB

**Fatores que afetam o tamanho:**
- Quantidade de texto completo
- Número de links/materiais/arquivos
- Quantidade de cards

---

## 🗂️ Organização por Turma

### Estrutura Completa:

```
dados_extraidos/
├── modulo6/
│   ├── cards_completos_20250826_100000.csv      # 1ª execução
│   ├── cards_enriquecidos_20250826_100000.csv
│   ├── cards_enriquecidos_20250826_100000.jsonl
│   ├── cards_completos_20250826_220413.csv      # 2ª execução
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

### Vantagens:
- ✅ **Isolamento**: Dados de cada turma separados
- ✅ **Histórico**: Múltiplas execuções preservadas
- ✅ **Comparação**: Fácil comparar versões
- ✅ **Backup**: Dados nunca sobrescritos

---

## 🎯 Qual Formato Usar?

### Use o **CSV Básico** quando:
- ✅ Quiser apenas visualizar os dados
- ✅ Abrir no Excel/Google Sheets
- ✅ Fazer buscas simples por texto
- ✅ Compartilhar com pessoas não-técnicas
- ✅ Não precisa de análises avançadas

### Use o **CSV Enriquecido** quando:
- ✅ Precisar de análises avançadas
- ✅ Quiser filtrar por professor, data, tipo
- ✅ Precisar rastrear ancoragens de autoestudos
- ✅ Calcular estatísticas por sprint/semana
- ✅ Usar pandas/Python para análise
- ✅ Detectar mudanças entre execuções (hash)

### Use o **JSONL** quando:
- ✅ Construir pipelines de dados
- ✅ Processar em lote (BigQuery, Spark, etc.)
- ✅ Integrar com ferramentas modernas
- ✅ Processar linha a linha (streaming)
- ✅ Precisar de tipos nativos (não strings)
- ✅ Exportar para APIs/serviços web

---

## 💡 Exemplos de Uso

### Análise Rápida (CSV Básico):

**Excel:**
1. Abrir arquivo
2. Filtrar por coluna "semana"
3. Buscar palavras-chave em "texto_completo"
4. Copiar links da coluna "links"

### Análise Avançada (CSV Enriquecido):

**Python/pandas:**
```python
import pandas as pd

df = pd.read_csv('cards_enriquecidos_*.csv')

# Estatísticas por sprint
print(df.groupby('sprint').agg({
    'id': 'count',
    'is_atividade_ponderada': 'sum',
    'num_materiais': 'sum'
}))

# Filtrar autoestudos ancorados com alta confiança
autoestudos = df[
    (df['is_autoestudo'] == True) &
    (df['anchor_confidence'] == 'high')
]
```

### Pipeline de Dados (JSONL):

**BigQuery:**
```sql
-- Carregar JSONL
CREATE TABLE dataset.cards AS
SELECT * FROM `gs://bucket/cards_enriquecidos_*.jsonl`;

-- Análise SQL
SELECT 
  sprint,
  COUNT(*) as total_cards,
  SUM(CASE WHEN is_atividade_ponderada THEN 1 ELSE 0 END) as atividades
FROM dataset.cards
GROUP BY sprint;
```

---

## 📊 Comparação de Formatos

| Característica | CSV Básico | CSV Enriquecido | JSONL |
|----------------|------------|-----------------|-------|
| **Campos** | 10 | 30 | 30 |
| **Tamanho** | Menor | Médio | Maior |
| **Análise Simples** | ✅ Ótimo | ✅ Ótimo | ⚠️ Requer ferramenta |
| **Análise Avançada** | ❌ Limitado | ✅ Excelente | ✅ Excelente |
| **Excel** | ✅ Direto | ✅ Direto | ❌ Não direto |
| **Python/pandas** | ✅ Sim | ✅ Sim | ✅ Sim |
| **BigQuery/Spark** | ⚠️ Limitado | ⚠️ Limitado | ✅ Ideal |
| **Pipelines** | ❌ Limitado | ⚠️ OK | ✅ Excelente |
| **Tipos Nativos** | ❌ Tudo string | ❌ Tudo string | ✅ Tipos corretos |

---

## 🔧 Resolução de Problemas

### Problema: "Arquivo muito grande para Excel"

**Causa**: Excel tem limite de ~1M linhas

**Solução**:
```python
import pandas as pd

# Ler em chunks
for chunk in pd.read_csv('cards_*.csv', chunksize=10000):
    # Processar chunk
    pass

# Ou filtrar antes
df = pd.read_csv('cards_*.csv')
df_filtrado = df[df['semana_num'] <= 5]  # Só primeiras 5 semanas
df_filtrado.to_csv('cards_filtrado.csv', index=False)
```

### Problema: "Encoding errado no Excel"

**Causa**: Excel não detecta UTF-8 automaticamente

**Solução**:
1. Abrir Excel → Data → From Text/CSV
2. Selecionar arquivo
3. Encoding: UTF-8
4. Delimiter: Comma
5. Import

### Problema: "JSONL não abre no Excel"

**Causa**: Excel não suporta JSONL

**Solução**:
```python
# Converter JSONL para CSV
import pandas as pd
df = pd.read_json('cards_*.jsonl', lines=True)
df.to_csv('cards_convertido.csv', index=False)
```

---

**📁 Guia completo dos arquivos gerados pelo AdaLove Extractor!**

Para mais detalhes sobre enriquecimento, veja [ENRIQUECIMENTO.md](./ENRIQUECIMENTO.md).
