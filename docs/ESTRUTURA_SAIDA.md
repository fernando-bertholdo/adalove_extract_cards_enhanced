# Estrutura de Saída - v2 (Extração via API)

## Hierarquia de Pastas

```
output/
└── {turma}/                      # Ex: 2026-1A-T13
    ├── extracao_completa.json    # Todas as semanas consolidadas
    └── semanas/
        ├── semana_01.json
        ├── semana_02.json
        └── ...
```

---

## Formato JSON

### Arquivo de Semana (`semana_XX.json`)

Estrutura hierárquica onde **datas são chaves** para encontros e **títulos são chaves** para autoestudos:

```json
{
  "turma": "2026-1A-T13",
  "semana": "Semana 08",
  "extração_timestamp": "2026-02-04T10:00:00.000000",
  "encontros": {
    "2026-03-23": {
      "dia_semana": "Segunda-feira",
      "titulo": "Suporte ao Projeto - Integração",
      "tipo": "encontro_instrucao",
      "professor": "Ovidio Lopes da Cruz Netto",
      "assuntos_relacionados": [...],
      "conteudos_relacionados": [...],
      "is_ponderada": false,
      "autoestudos": {
        "Suporte aos projetos dos grupos": {
          "descricao": "<p>Descrição HTML...</p>",
          "professor": "Ovidio Lopes da Cruz Netto",
          "conteudos_relacionados": [
            {"titulo": "...", "url": "https://..."}
          ],
          "assuntos_relacionados": [...],
          "is_ponderada": false,
          "ancora_metodo": "professor,sort_prox=1.40,sim=0.74",
          "ancora_confianca": "high"
        }
      }
    }
  },
  "sem_ancora": []
}
```

---

## Campos

### Encontro (Card de Instrução/Orientação)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `dia_semana` | string | Dia da semana em português |
| `titulo` | string | Título do encontro |
| `tipo` | string | `encontro_instrucao` ou `encontro_orientacao` |
| `professor` | string\|null | Nome do professor |
| `assuntos_relacionados` | array | Lista de assuntos |
| `conteudos_relacionados` | array | Lista de links |
| `is_ponderada` | boolean | Se é atividade avaliativa |
| `autoestudos` | object | Autoestudos ancorados a este encontro |

### Autoestudo

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `descricao` | string | Descrição HTML |
| `professor` | string\|null | Professor responsável |
| `conteudos_relacionados` | array | Lista de `{titulo, url}` |
| `assuntos_relacionados` | array | Lista de assuntos |
| `is_ponderada` | boolean | Se é atividade avaliativa |
| `ancora_metodo` | string | Fatores de ancoragem usados |
| `ancora_confianca` | string | `high`, `medium`, ou `low` |

---

## Acesso Programático

```python
import json

# Carregar dados
with open("output/2026-1A-T13/semanas/semana_08.json") as f:
    data = json.load(f)

# Acessar encontro por data
encontro = data["encontros"]["2026-03-23"]
print(encontro["titulo"])  # "Suporte ao Projeto - Integração"

# Acessar autoestudo por título
auto = encontro["autoestudos"]["Suporte aos projetos dos grupos"]
print(auto["professor"])  # "Ovidio Lopes da Cruz Netto"

# Listar todas as datas
for data_encontro in data["encontros"]:
    print(data_encontro)  # "2026-03-23", "2026-03-24", ...
```

---

## Sistema de Ancoragem

Autoestudos são vinculados a encontros usando pontuação multi-fator:

| Fator | Pontos | Descrição |
|-------|--------|-----------|
| **Professor** | +3.0 | Mesmo professor no autoestudo e encontro |
| **Proximidade** | +1.5 - 0.1×delta | Posição de sort próxima |
| **Similaridade** | +2.0 × sim | Títulos semelhantes |

### Níveis de Confiança

- **`high`**: Professor corresponde OU score > 4.0
- **`medium`**: Proximidade alta OU similaridade > 0.4
- **`low`**: Apenas proximidade básica
