# 📊 Dados Extraídos - Especificação Completa

## 🎯 Formatos de Saída

O script `adalove_extractor.py` gera **3 arquivos** por execução:

1. **CSV Básico** - Dados brutos da extração
2. **CSV Enriquecido** - Dados processados com 30 campos
3. **JSONL** - Formato JSON Lines para pipelines

---

## 📊 Formato 1: CSV Básico (`cards_completos_*.csv`)

### Campos (10 colunas):

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `semana` | string | Nome da semana processada | "Semana 01" |
| `indice` | int | Número do card na semana | 1, 2, 3... |
| `id` | string | ID único do card | "46d403bdd15b4fe8a68dbf1e9880f00c" |
| `titulo` | string | Primeira linha do card | "Workshop com Parceiro" |
| `descricao` | string | Resto do texto do card | "Conceitos básicos..." |
| `tipo` | string | Tipo do card | "Atividade", "Projeto", "Material", "Avaliação", "Outros" |
| `texto_completo` | string | Todo o texto do card (card + modal) | "Workshop com Parceiro\n\n24/04/2025 - 14:00h\n..." |
| `links` | string | Links externos (pipe-separated) | "Link: https://example.com \| Link: https://..." |
| `materiais` | string | Materiais Google (pipe-separated) | "Material: https://drive.google.com/... \| Docs: https://..." |
| `arquivos` | string | Arquivos anexados (pipe-separated) | "exercicios.pdf: https://... \| slides.pptx: https://..." |

### Exemplo de Registro:

```csv
semana,indice,id,titulo,descricao,tipo,texto_completo,links,materiais,arquivos
Semana 01,1,46d403b,"Workshop com Parceiro","24/04/2025 - 14:00h","Outros","Workshop com Parceiro\n24/04/2025 - 14:00h","","",""
Semana 01,2,6ec59e1,"Filtragem Colaborativa baseada em Item","25/04/2025 - 14:00h\nOvidio Lopes","Atividade","Filtragem Colaborativa...\n25/04/2025...","Link: https://example.com","Material: https://drive.google.com/xyz",""
```

---

## 🔬 Formato 2: CSV Enriquecido (`cards_enriquecidos_*.csv`)

### Campos (30 colunas):

#### 🗂️ Campos Básicos (10 colunas - mesmos do CSV básico)
- `semana`, `indice`, `id`, `titulo`, `descricao`, `tipo`
- `texto_completo`, `links`, `materiais`, `arquivos`

#### ⏰ Campos Temporais (5 colunas)
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `semana_num` | int | Número da semana | 1, 2, 3... |
| `sprint` | int | Número do sprint (semana/2 arredondado) | 1, 2, 3... |
| `data_ddmmaaaa` | string | Data em formato brasileiro | "24/04/2025" |
| `hora_hhmm` | string | Hora em formato 24h | "14:00" |
| `data_hora_iso` | string | ISO 8601 com timezone | "2025-04-24T14:00:00-03:00" |

#### 👤 Campos de Identificação (1 coluna)
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `professor` | string | Nome do professor detectado | "Ovidio Lopes da Cruz Netto" |

#### 🏷️ Campos de Classificação (3 colunas)
| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| `is_instrucao` | boolean | Card é uma instrução/encontro | True/False |
| `is_autoestudo` | boolean | Card é um autoestudo | True/False |
| `is_atividade_ponderada` | boolean | Card é atividade com nota | True/False |

#### 🔗 Campos de Ancoragem (4 colunas)
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `parent_instruction_id` | string | ID da instrução relacionada | "46d403bdd15b4fe8..." |
| `parent_instruction_title` | string | Título da instrução relacionada | "Workshop Python" |
| `anchor_method` | string | Método usado para ancoragem | "professor,same_date,sim=0.85" |
| `anchor_confidence` | string | Confiança da ancoragem | "high", "medium", "low", "locked" |

**Métodos de ancoragem:**
- `professor` - Match exato do nome do professor (+3.0 pts)
- `same_date` - Mesma data de realização (+3.0 pts)
- `sim=X.XX` - Similaridade de título 0-1 (+2.0 pts × sim)
- `prev_prox=X.XX` - Proximidade posicional (+1.5 pts)
- `preserved_previous` - Ancoragem preservada de execução anterior

**Níveis de confiança:**
- `high` - Professor OU data batem (pontuação ≥ 3.0)
- `medium` - Boa similaridade ou proximidade (1.0 ≤ pontuação < 3.0)
- `low` - Apenas heurísticas fracas (pontuação < 1.0)
- `locked` - Ancoragem preservada de execução anterior (não recalculada)

#### 🔗 Campos de URLs Normalizadas (6 colunas)
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `links_urls` | string | URLs de links (pipe-separated) | "https://example.com \| https://..." |
| `materiais_urls` | string | URLs de materiais (pipe-separated) | "https://drive.google.com/... \| https://..." |
| `arquivos_urls` | string | URLs de arquivos (pipe-separated) | "https://.../file.pdf \| https://..." |
| `num_links` | int | Número de links | 0, 1, 2... |
| `num_materiais` | int | Número de materiais | 0, 1, 2... |
| `num_arquivos` | int | Número de arquivos | 0, 1, 2... |

**Normalização de URLs:**
- ✅ Remove texto descritivo ("Material: ", "Link: ", etc.)
- ✅ Remove duplicatas
- ✅ Mantém apenas URLs http(s)
- ✅ Filtra caminhos relativos e ícones

#### 🔐 Campo de Integridade (1 coluna)
| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `record_hash` | string | Hash SHA1 do registro (titulo+data+professor) | "93fa506122e2fa6d..." |

**Uso do hash:**
- ✅ Detectar mudanças em cards entre execuções
- ✅ Identificar duplicatas
- ✅ Rastrear histórico de modificações
- ✅ Comparar versões

---

## 📦 Formato 3: JSONL (`cards_enriquecidos_*.jsonl`)

### Estrutura:
Um objeto JSON por linha, contendo **todos os 30 campos** do CSV enriquecido.

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
- ✅ **Streaming**: Pode ser processado linha a linha
- ✅ **Arrays nativos**: URLs não precisam ser strings com separador
- ✅ **Tipagem**: Booleanos e números preservados
- ✅ **Compatibilidade**: Funciona com ferramentas modernas de dados
- ✅ **Performance**: Mais rápido que JSON grande para processar

### Como usar JSONL:

#### Python:
```python
import json

# Ler linha a linha
with open('cards_enriquecidos_20250826_220413.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        print(card['titulo'])

# Ou usar pandas
import pandas as pd
df = pd.read_json('cards_enriquecidos_20250826_220413.jsonl', lines=True)
```

#### jq (command line):
```bash
# Filtrar autoestudos
cat cards_enriquecidos_*.jsonl | jq 'select(.is_autoestudo == true)'

# Contar por tipo
cat cards_enriquecidos_*.jsonl | jq '.tipo' | sort | uniq -c

# Extrair apenas títulos e datas
cat cards_enriquecidos_*.jsonl | jq '{titulo, data_ddmmaaaa}'
```

---

## 📊 Estatísticas de Dados

### Exemplo de Execução (modulo6):
Com base em execução real do script:

```
Total de cards: 127
Semanas processadas: 10
Cards com links: 89 (70%)
Cards com materiais: 67 (53%)
Cards com arquivos: 12 (9%)

Distribuição por tipo:
- Atividade: 45 cards (35%)
- Projeto: 28 cards (22%)
- Material: 32 cards (25%)
- Outros: 22 cards (18%)

Classificação:
- Instruções: 38 cards (30%)
- Autoestudos: 52 cards (41%)
- Atividades ponderadas: 18 cards (14%)

Ancoragem de autoestudos:
- Total de autoestudos: 52
- Ancorados: 48 (92%)
- Confiança alta: 42 (88%)
- Confiança média: 6 (12%)
- Confiança baixa: 0 (0%)
```

---

## 🔍 Análises Comuns

### 1. Cards por Semana
```python
import pandas as pd

df = pd.read_csv('cards_enriquecidos_*.csv')
print(df.groupby('semana_num').size())
```

### 2. Distribuição por Tipo
```python
print(df['tipo'].value_counts())
```

### 3. Taxa de Ancoragem
```python
autoestudos = df[df['is_autoestudo'] == True]
ancorados = autoestudos[autoestudos['parent_instruction_id'].notna()]
print(f"Taxa de ancoragem: {len(ancorados)/len(autoestudos)*100:.1f}%")
```

### 4. Professores Mais Frequentes
```python
print(df['professor'].value_counts())
```

### 5. Cards por Sprint
```python
print(df.groupby('sprint').agg({
    'id': 'count',
    'is_instrucao': 'sum',
    'is_autoestudo': 'sum',
    'is_atividade_ponderada': 'sum'
}))
```

### 6. Materiais Mais Comuns
```python
# Cards com mais materiais
top_materiais = df.nlargest(10, 'num_materiais')[['titulo', 'num_materiais', 'materiais_urls']]
print(top_materiais)
```

### 7. Timeline de Atividades
```python
# Ordenar por data
df_com_data = df[df['data_hora_iso'].notna()].sort_values('data_hora_iso')
print(df_com_data[['data_ddmmaaaa', 'hora_hhmm', 'titulo', 'tipo']])
```

---

## 💡 Dicas de Uso

### ✅ **Dados Limpos**:
- Texto completo preservado com quebras de linha
- Encoding UTF-8 correto (suporta acentuação)
- Headers padronizados em todos os arquivos
- Timestamps consistentes (YYYYMMDD_HHMMSS)

### ⚡ **Performance**:
- CSV básico: ~2-5 MB para 100-200 cards
- CSV enriquecido: ~3-8 MB para 100-200 cards
- JSONL: ~4-10 MB para 100-200 cards
- Tempo de extração: ~5-15 minutos para 10 semanas

### 🔄 **Atualizações**:
- Cada execução gera novos arquivos (não sobrescreve)
- Use o `record_hash` para comparar versões
- Timestamps permitem rastrear histórico

### 📊 **Ferramentas Recomendadas**:
- **Excel/Google Sheets**: CSV básico (mais simples)
- **Python/pandas**: CSV enriquecido (análises complexas)
- **jq/BigQuery**: JSONL (processamento em lote)
- **Power BI/Tableau**: CSV enriquecido (visualizações)

---

## 📁 Organização dos Arquivos

### Estrutura Completa:
```
dados_extraidos/
└── nome_turma/
    ├── cards_completos_20250826_220413.csv         # 10 campos
    ├── cards_enriquecidos_20250826_220413.csv      # 30 campos
    └── cards_enriquecidos_20250826_220413.jsonl    # 30 campos (JSON)
```

### Múltiplas Execuções:
```
dados_extraidos/
└── modulo6/
    ├── cards_completos_20250826_100000.csv         # 1ª execução
    ├── cards_enriquecidos_20250826_100000.csv
    ├── cards_enriquecidos_20250826_100000.jsonl
    ├── cards_completos_20250827_150000.csv         # 2ª execução
    ├── cards_enriquecidos_20250827_150000.csv
    └── cards_enriquecidos_20250827_150000.jsonl
```

---

## 🎯 Qual Formato Usar?

### Use o **CSV Básico** quando:
- ✅ Quiser apenas visualizar os dados
- ✅ Abrir no Excel/Google Sheets
- ✅ Fazer buscas simples por texto
- ✅ Compartilhar com pessoas não-técnicas

### Use o **CSV Enriquecido** quando:
- ✅ Precisar de análises avançadas
- ✅ Quiser filtrar por professor, data, tipo
- ✅ Precisar rastrear ancoragens de autoestudos
- ✅ Quiser calcular estatísticas por sprint/semana
- ✅ Precisar de integridade (hash)

### Use o **JSONL** quando:
- ✅ Estiver construindo pipelines de dados
- ✅ Precisar processar em lote (BigQuery, Spark, etc.)
- ✅ Quiser integrar com ferramentas modernas
- ✅ Precisar de streaming/processamento linha a linha
- ✅ Quiser preservar tipos nativos (booleanos, números)

---

## 📝 Notas Importantes

### Sobre o Enriquecimento:
- ⚠️ O enriquecimento é **automático** e baseado em **heurísticas**
- ⚠️ A detecção de professor pode não ser 100% precisa
- ⚠️ A ancoragem usa múltiplos fatores mas pode errar em casos ambíguos
- ✅ Sempre verifique a coluna `anchor_confidence` ao usar ancoragens
- ✅ O hash permite detectar mudanças entre execuções

### Sobre os Dados:
- ⚠️ Nem todos os cards têm links/materiais/arquivos
- ⚠️ Campos vazios são representados como "" (string vazia)
- ⚠️ Campos nulos são representados como null (JSONL) ou "" (CSV)
- ✅ O texto completo é sempre extraído (mesmo sem links)

---

**📊 Especificação completa dos dados extraídos pelo AdaLove Extractor!**
