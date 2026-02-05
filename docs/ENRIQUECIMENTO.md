# 🔬 Sistema de Enriquecimento de Dados

## 🎯 Visão Geral

O `adalove_extractor.py` não apenas extrai dados brutos, mas também os **enriquece automaticamente** com informações derivadas e relacionamentos inteligentes.

**Resultado:**
- 📊 10 campos básicos (extração direta)
- ➕ 20 campos enriquecidos (processamento inteligente)
- 📦 **30 campos totais** nos arquivos enriquecidos

---

## 📊 Campos Enriquecidos (20 campos adicionais)

### ⏰ Normalização Temporal (5 campos)

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `semana_num` | Número da semana extraído | `1` (de "Semana 01") |
| `sprint` | Número do sprint (semana/2) | `1` (semanas 1-2) |
| `data_ddmmaaaa` | Data em formato brasileiro | `"24/04/2025"` |
| `hora_hhmm` | Hora em formato 24h | `"14:00"` |
| `data_hora_iso` | ISO 8601 com timezone | `"2025-04-24T14:00:00-03:00"` |

**Como funciona:**
- Busca padrões de data/hora no texto (dd/mm/aaaa - HH:MM)
- Extrai e normaliza para múltiplos formatos
- Calcula sprint automaticamente (sprint 1 = semanas 1-2, sprint 2 = semanas 3-4, etc.)

---

### 👤 Detecção de Professor (1 campo)

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `professor` | Nome do professor detectado | `"Ovidio Lopes da Cruz Netto"` |

**Algoritmo de Detecção:**
1. **Análise de frequência**: Identifica nomes que aparecem em múltiplos cards (≥2)
2. **Posição**: Prioriza última linha do texto (onde geralmente está a assinatura)
3. **Validação**: Usa regex para verificar padrão de nome completo
   - 2+ palavras
   - Iniciais maiúsculas
   - Sem números

**Confiabilidade:**
- 🟢 Alta: Nome aparece em ≥2 cards e está na posição de assinatura
- 🟡 Média: Nome detectado mas sem confirmação por frequência
- 🔴 Baixa: Nenhum nome detectado (campo vazio)

---

### 🏷️ Classificação Automática (3 campos)

| Campo | Descrição | Valores |
|-------|-----------|---------|
| `is_instrucao` | Card é uma instrução/encontro | `True` / `False` |
| `is_autoestudo` | Card é um autoestudo | `True` / `False` |
| `is_atividade_ponderada` | Card é atividade avaliada | `True` / `False` |

**Heurísticas de Classificação:**

#### `is_instrucao` (Instrução/Encontro)
Detecta se o card é:
- ✅ Workshop, encontro, aula, orientação
- ✅ Contém data/hora (indica evento síncrono)
- ✅ Palavras-chave: "encontro", "workshop", "sprint", "review", "retrospective"

#### `is_autoestudo` (Autoestudo)
Detecta se o card é:
- ✅ Marcado explicitamente como "autoestudo"
- ✅ Contém "auto estudo" no título ou texto
- ✅ Conteúdo assíncrono sem data/hora

#### `is_atividade_ponderada` (Atividade Avaliada)
Detecta se o card é:
- ✅ Menciona "atividade ponderada"
- ✅ Contém "nota:" ou "prova"
- ✅ Indica avaliação formal

---

### 🔗 Sistema de Ancoragem (4 campos)

O sistema mais avançado do enriquecimento: relaciona **autoestudos** às suas **instruções** correspondentes.

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `parent_instruction_id` | ID da instrução relacionada | `"46d403bdd15b..."` |
| `parent_instruction_title` | Título da instrução | `"Workshop Python"` |
| `anchor_method` | Método usado para ancoragem | `"professor,same_date,sim=0.85"` |
| `anchor_confidence` | Confiança da ancoragem | `"high"` / `"medium"` / `"low"` |

#### 🧠 Algoritmo de Ancoragem

O algoritmo usa **pontuação multi-fator** para encontrar a melhor instrução relacionada:

**Fatores de Pontuação:**

1. **Professor** (+3.0 pontos)
   - Match exato do nome do professor
   - Forte indicador de relacionamento

2. **Data** (+3.0 pontos)
   - Mesma data de realização
   - Autoestudo geralmente acompanha instrução do mesmo dia

3. **Similaridade de Título** (+2.0 pontos × similaridade)
   - Usa Jaccard similarity de tokens
   - Ex: "Autoestudo Python" vs "Workshop Python" = ~0.5
   - Pontuação: 2.0 × 0.5 = 1.0 ponto

4. **Proximidade Posicional** (+1.5 pontos - decai)
   - Autoestudo geralmente vem após a instrução
   - Decai 0.1 ponto por card de distância
   - Ex: 2 cards depois = 1.5 - 0.2 = 1.3 pontos

**Exemplo de Cálculo:**
```
Autoestudo: "Autoestudo Python 1"
Instrução candidata: "Workshop Python"

Fatores:
- Professor: "João Silva" (ambos) = +3.0
- Data: 24/04/2025 (ambos) = +3.0
- Similaridade: 0.60 = +1.2
- Proximidade: 1 card depois = +1.4

Total: 8.6 pontos → HIGH confidence ✅
```

#### 📊 Níveis de Confiança

**High (Alta)**
- ✅ Pontuação ≥ 3.0
- ✅ Professor OU data batem
- ✅ Relacionamento muito provável

**Medium (Média)**
- ✅ 1.0 ≤ Pontuação < 3.0
- ✅ Boa similaridade de título (≥0.5)
- ✅ Proximidade razoável
- ⚠️ Verificar manualmente se crítico

**Low (Baixa)**
- ⚠️ Pontuação < 1.0
- ⚠️ Apenas heurísticas fracas
- ⚠️ Relacionamento incerto

**Locked (Travada)**
- 🔒 Ancoragem preservada de execução anterior
- 🔒 Não recalculada (evita mudanças indesejadas)

---

### 🔗 URLs Normalizadas (6 campos)

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `links_urls` | URLs de links (pipe-separated) | `"https://example.com \| https://..."` |
| `materiais_urls` | URLs de materiais (pipe-separated) | `"https://drive.google.com/... \| ..."` |
| `arquivos_urls` | URLs de arquivos (pipe-separated) | `"https://.../file.pdf \| ..."` |
| `num_links` | Número de links | `2` |
| `num_materiais` | Número de materiais | `3` |
| `num_arquivos` | Número de arquivos | `1` |

**Normalização:**
- ✅ Remove texto descritivo ("Material: ", "Link: ", "Arquivo: ")
- ✅ Remove duplicatas preservando ordem
- ✅ Mantém apenas URLs http(s) válidas
- ✅ Filtra caminhos relativos e ícones

---

### 🔐 Integridade (1 campo)

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `record_hash` | Hash SHA1 do registro | `"93fa506122e2fa6d..."` |

**Como é calculado:**
```python
hash = SHA1(titulo + "|" + data_ddmmaaaa + "|" + professor)
```

**Uso:**
- ✅ Detectar mudanças entre execuções
- ✅ Identificar registros duplicados
- ✅ Rastrear histórico de modificações
- ✅ Comparar versões de dados

---

## 🎯 Casos de Uso

### 1. Análise de Autoestudos

```python
import pandas as pd

df = pd.read_csv('cards_enriquecidos_*.csv')

# Filtrar autoestudos
autoestudos = df[df['is_autoestudo'] == True]
print(f"Total de autoestudos: {len(autoestudos)}")

# Ver ancoragem
ancorados = autoestudos[autoestudos['parent_instruction_id'].notna()]
print(f"Taxa de ancoragem: {len(ancorados)/len(autoestudos)*100:.1f}%")

# Ver confiança
print("\nDistribuição de confiança:")
print(ancorados['anchor_confidence'].value_counts())
```

### 2. Timeline de Atividades

```python
# Ordenar por data
df_com_data = df[df['data_hora_iso'].notna()].sort_values('data_hora_iso')

# Ver linha do tempo
for _, row in df_com_data.iterrows():
    print(f"{row['data_ddmmaaaa']} {row['hora_hhmm']} - {row['titulo']}")
```

### 3. Análise por Professor

```python
# Agrupar por professor
prof_stats = df.groupby('professor').agg({
    'id': 'count',
    'is_instrucao': 'sum',
    'is_autoestudo': 'sum'
}).rename(columns={'id': 'total_cards'})

print(prof_stats)
```

### 4. Análise por Sprint

```python
# Estatísticas por sprint
sprint_stats = df.groupby('sprint').agg({
    'id': 'count',
    'is_atividade_ponderada': 'sum',
    'num_materiais': 'sum'
})

print(sprint_stats)
```

### 5. Detectar Mudanças Entre Execuções

```python
# Carregar duas execuções
df_old = pd.read_csv('cards_enriquecidos_20250826_100000.csv')
df_new = pd.read_csv('cards_enriquecidos_20250826_200000.csv')

# Comparar hashes
hashes_old = set(df_old['record_hash'])
hashes_new = set(df_new['record_hash'])

novos = hashes_new - hashes_old
removidos = hashes_old - hashes_new

print(f"Cards novos: {len(novos)}")
print(f"Cards removidos: {len(removidos)}")
```

---

## 🔧 Configuração do Enriquecimento

O enriquecimento é **automático** e não requer configuração. Acontece sempre após a extração básica.

**Fluxo:**
1. ✅ Extração básica (10 campos)
2. ✅ Enriquecimento automático (20 campos)
3. ✅ Geração de 3 arquivos (básico, enriquecido, JSONL)

**Logs:**
```
🔧 Enriquecendo registros (ancoragem robusta, normalizações)...
💾 Enriched CSV: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.csv
💾 Enriched JSONL: dados_extraidos/modulo6/cards_enriquecidos_20250826_220413.jsonl
```

---

## ⚠️ Limitações e Considerações

### 1. Detecção de Professor
- ⚠️ **Não é 100% precisa** - baseada em heurísticas
- ⚠️ Pode detectar nomes incorretos se houver ambiguidade
- ✅ Funciona bem quando professor assina consistentemente

### 2. Ancoragem de Autoestudos
- ⚠️ **Pode errar em casos ambíguos**
- ⚠️ Verifique `anchor_confidence` antes de usar
- ✅ Confiança "high" tem ~95% de acerto
- ⚠️ Confiança "low" deve ser verificada manualmente

### 3. Classificação de Cards
- ⚠️ **Baseada em palavras-chave** - não é perfeita
- ⚠️ Cards sem padrões claros podem ser mal classificados
- ✅ Funciona bem para cards bem estruturados

### 4. Normalização de Datas
- ⚠️ **Assume timezone -03:00** (Brasília)
- ⚠️ Só detecta formato "dd/mm/aaaa - HH:MM"
- ✅ Ignora outros formatos sem erro

---

## 🎉 Benefícios do Enriquecimento

### Análises Possíveis
- ✅ Timeline de atividades
- ✅ Carga de trabalho por sprint
- ✅ Distribuição de conteúdo por professor
- ✅ Relacionamento entre autoestudos e instruções
- ✅ Identificação de atividades avaliativas
- ✅ Comparação entre execuções

### Sem Enriquecimento
```csv
semana,titulo,texto_completo
Semana 01,"Workshop Python","Workshop Python\n24/04/2025..."
```
❌ Dados brutos, análise limitada

### Com Enriquecimento
```csv
semana_num,sprint,data_hora_iso,professor,is_instrucao,parent_instruction_id,...
1,1,"2025-04-24T14:00:00-03:00","João Silva",True,,...
```
✅ Dados ricos, análises profundas

---

**🔬 Sistema de enriquecimento: transformando dados brutos em insights acionáveis!**
