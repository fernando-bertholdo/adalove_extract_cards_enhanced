# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.0.0] - 2025-10-08

### Contexto
Esta release representa uma evolução significativa do projeto, transformando um extrator básico em um sistema completo de enriquecimento e análise de dados acadêmicos. O trabalho envolveu refatoração profunda do código, implementação de algoritmos inteligentes e documentação profissional.

### Adicionado

#### Sistema de Enriquecimento Automático
- **Normalização de datas**: Conversão automática para ISO 8601 com timezone
- **Detecção de professor**: Algoritmo heurístico para identificar docente responsável
- **Classificação de cards**: Identificação automática de instruções, autoestudos e atividades ponderadas
- **Cálculo de sprint**: Derivação inteligente da sprint a partir do número da semana
- **Hash de registro**: Identificador único para cada card baseado em conteúdo

#### Ancoragem Inteligente de Autoestudos
Sistema multi-fator que relaciona automaticamente autoestudos às instruções correspondentes:
- Análise de professor (mesma instrução)
- Comparação de datas (proximidade temporal)
- Similaridade de títulos (algoritmo de distância)
- Proximidade posicional no Kanban
- Níveis de confiança: high, medium, low

#### Múltiplos Formatos de Saída
- CSV básico (10 campos) - mantido para compatibilidade
- CSV enriquecido (30 campos) - dados completos para análise
- JSONL (JSON Lines) - formato para pipelines de dados

#### Documentação Profissional
- README principal expandido (330+ linhas)
- Guia de extração passo a passo (`documents/GUIA_EXTRACAO.md`)
- Especificação completa de campos e formatos (`documents/DADOS_EXTRAIDOS.md`)
- Documentação de enriquecimento de dados (`documents/ENRIQUECIMENTO.md`)
- Seção de troubleshooting expandida
- Histórico de reformulação do projeto (`documents/README_reformulacao.md`)

### Modificado

#### Melhorias Técnicas
- Código comentado com documentação inline completa em português
- Gitignore otimizado para exclusão apropriada de outputs e histórico de desenvolvimento
- Estrutura limpa com pastas criadas automaticamente pelo script
- Separação de dependências: `requirements.txt` (runtime) e `requirements-dev.txt` (desenvolvimento)

#### Campos de Dados Expandidos
**Básicos (10)**: `semana`, `indice`, `id`, `titulo`, `descricao`, `tipo`, `texto_completo`, `links`, `materiais`, `arquivos`

**Enriquecidos Adicionais (20)**:
- Contexto temporal: `semana_num`, `sprint`, `data_ddmmaaaa`, `hora_hhmm`, `data_hora_iso`
- Metadados: `professor`, `record_hash`
- Classificação: `is_instrucao`, `is_autoestudo`, `is_atividade_ponderada`
- Ancoragem: `parent_instruction_id`, `parent_instruction_title`, `anchor_method`, `anchor_confidence`
- Recursos estruturados: `links_urls`, `materiais_urls`, `arquivos_urls`, `num_links`, `num_materiais`, `num_arquivos`

### Comparação com v1.0.0

| Aspecto | v1.0.0 | v2.0.0 | Evolução |
|---------|--------|--------|----------|
| **Campos de dados** | 10 | 30 | +200% |
| **Formatos de saída** | 1 (CSV) | 3 (CSV x2, JSONL) | +200% |
| **Documentação** | Básica | Completa | ~400% |
| **Ancoragem de dados** | ❌ | ✅ Inteligente | Novo |
| **Enriquecimento** | ❌ | ✅ Automático | Novo |

### Casos de Uso Habilitados
1. **Análise estatística**: Dados estruturados para pandas/R
2. **Integração com pipelines**: Formato JSONL pronto para consumo
3. **Auditoria de conteúdo**: Preservação completa de texto original
4. **Cruzamento de dados**: Hash único e ancoragem relacional
5. **Visualizações**: Dados temporais e categóricos estruturados

---

## [1.0.0] - 2025-08-26

### Contexto
Esta release marca a consolidação de múltiplos scripts experimentais em uma solução unificada e funcional. O projeto evoluiu de uma base original (Tony Jonas) através de diversas iterações até atingir estabilidade estrutural.

### Adicionado

#### Extração Automatizada
- Login automático na plataforma AdaLove com fallback para seleção manual
- Descoberta automática de semanas disponíveis no Kanban
- Extração completa de cards com título, descrição e texto integral
- Captura de links, materiais e arquivos anexados

#### Organização de Dados
- Estrutura automatizada por turma (pasta personalizada)
- Versionamento por timestamp para múltiplas execuções
- Exportação em formato CSV com 10 campos essenciais
- Sistema de logs detalhados para auditoria e debug

#### Qualidade Técnica
- Script único consolidado (`adalove_extractor.py`)
- Tratamento robusto de erros e timeouts
- Navegação inteligente com Playwright
- Documentação inicial do projeto

### Estrutura de Saída
```
dados_extraidos/
└── nome_turma/
    └── cards_completos_TIMESTAMP.csv (10 campos)
```

### Limitações Conhecidas
- Enriquecimento de dados ainda não implementado
- Formato único de saída (CSV básico)
- Ancoragem de autoestudos não disponível
- Documentação ainda em desenvolvimento

---

## Agradecimentos

Projeto inspirado e desenvolvido a partir do trabalho original de [Tony Jonas](https://github.com/tonyJonas/adalove_extract_cards).

---

[2.0.0]: https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced/releases/tag/v2.0.0
[1.0.0]: https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced/releases/tag/v1.0.0

