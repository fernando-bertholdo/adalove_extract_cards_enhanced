# 📁 Pasta de Dados Extraídos

Esta pasta é automaticamente organizada por turma quando você executa o script `adalove_extractor.py`.

---

## 📋 Estrutura Automática

Após executar o script, a estrutura será:

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

---

## 🎯 Como Funciona

1. **Input do usuário**: Nome da turma digitado no início da execução
2. **Pasta automática**: Script cria pasta com nome da turma  
3. **3 arquivos gerados**: CSV básico, CSV enriquecido e JSONL
4. **Timestamping**: Cada arquivo tem data/hora da extração
5. **Organização**: Dados de cada turma ficam separados

---

## 📊 Arquivos Gerados por Execução

### 1. `cards_completos_TIMESTAMP.csv` (Formato Básico)
**10 campos principais:**
- Dados brutos extraídos da plataforma
- Melhor para visualização rápida no Excel
- Contém: semana, indice, id, titulo, descricao, tipo, texto_completo, links, materiais, arquivos

### 2. `cards_enriquecidos_TIMESTAMP.csv` (Formato Completo)
**30 campos enriquecidos:**
- Todos os dados básicos + 20 campos adicionais
- Inclui: normalização de datas, detecção de professor, classificação de cards
- Ancoragem de autoestudos às instruções
- Melhor para análises avançadas com pandas/Python

### 3. `cards_enriquecidos_TIMESTAMP.jsonl` (JSON Lines)
**Formato JSONL:**
- Mesmo conteúdo do CSV enriquecido
- Um objeto JSON por linha
- Melhor para pipelines de processamento e integrações
- Compatível com ferramentas modernas de Big Data

---

## 📊 Exemplo de Conteúdo

### CSV Básico:
```csv
semana,indice,id,titulo,descricao,tipo,links,materiais,arquivos,texto_completo
Semana 01,1,card-123,"Intro Python","Conceitos básicos","Atividade","Link: https://...","Drive: https://...","ex.pdf: https://...","Intro Python\nConceitos..."
```

### CSV Enriquecido (campos adicionais):
```csv
...,semana_num,sprint,professor,is_instrucao,is_autoestudo,parent_instruction_id,anchor_confidence,...
...,1,1,"João Silva",true,false,,,,...
```

### JSONL:
```json
{"semana":"Semana 01","semana_num":1,"titulo":"Intro Python","is_autoestudo":false,...}
```

---

## 🗂️ Múltiplas Execuções

Dados **nunca são sobrescritos**! Cada execução gera novos arquivos:

```
dados_extraidos/
└── modulo6/
    ├── cards_completos_20250826_100000.csv      # 1ª execução - manhã
    ├── cards_enriquecidos_20250826_100000.csv
    ├── cards_enriquecidos_20250826_100000.jsonl
    ├── cards_completos_20250826_220413.csv      # 2ª execução - noite
    ├── cards_enriquecidos_20250826_220413.csv
    └── cards_enriquecidos_20250826_220413.jsonl
```

**Vantagens:**
- ✅ Histórico completo preservado
- ✅ Comparação entre versões
- ✅ Backup automático
- ✅ Rastreamento de mudanças

---

## ✅ Vantagens da Organização

- 📁 **Pasta individual** para cada turma
- 🔄 **Timestamping** evita sobrescrever dados
- 📚 **Histórico preservado** de todas as extrações
- 🔍 **Fácil localização** dos dados por turma
- 📊 **3 formatos** por execução (básico, enriquecido, JSONL)
- 🎯 **Flexibilidade** de uso (Excel, Python, pipelines)

---

## 🔧 Como Usar os Dados

### Para Visualização Rápida:
- Abra o **CSV básico** no Excel ou Google Sheets
- Filtre por semana, tipo, etc.
- Busque por palavras-chave no texto

### Para Análises Avançadas:
- Use o **CSV enriquecido** com Python/pandas
- Filtre por professor, sprint, classificação
- Analise ancoragens de autoestudos
- Calcule estatísticas por período

### Para Integrações:
- Use o **JSONL** em pipelines de dados
- Importe em ferramentas de Big Data
- Processe linha a linha em streaming
- Integre com APIs e outras ferramentas

---

## 📝 Exemplo de Análise com Python

```python
import pandas as pd

# Carregar dados enriquecidos
df = pd.read_csv('modulo6/cards_enriquecidos_20250826_220413.csv')

# Estatísticas básicas
print(f"Total de cards: {len(df)}")
print(f"Semanas: {df['semana_num'].nunique()}")
print(f"Cards por tipo:\n{df['tipo'].value_counts()}")

# Filtrar autoestudos
autoestudos = df[df['is_autoestudo'] == True]
print(f"\nAutoestudos: {len(autoestudos)}")

# Ver ancoragens
ancorados = autoestudos[autoestudos['parent_instruction_id'].notna()]
print(f"Ancorados: {len(ancorados)} ({len(ancorados)/len(autoestudos)*100:.1f}%)")
```

---

## 🚀 Gerando Dados

Para criar novos dados extraídos, execute:

```bash
python adalove_extractor.py
```

E siga as instruções:
1. Digite o nome da turma
2. Aguarde o login
3. Selecione a turma na interface
4. Aguarde a extração completa
5. Encontre os 3 arquivos nesta pasta!

---

**Esta pasta estará sempre organizada e nunca sobrescreverá dados anteriores!**

Para mais informações, consulte o [README.md principal](../README.md).
