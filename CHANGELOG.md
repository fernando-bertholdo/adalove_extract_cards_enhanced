# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [3.1.0] - 2025-10-17

### Contexto
Esta release implementa um **sistema resiliente completo** para evitar perda de dados durante extrações. Baseado na experiência real de perda de 204 cards extraídos por falha simples no salvamento final, esta versão prioriza robustez e recuperação automática.

### Adicionado

#### Sistema de Checkpoints Avançado
- **`CheckpointManager`** (`adalove_extractor/io/checkpoint.py`)
  - Persistência de estado da extração em JSON
  - Salvamento incremental após cada semana processada
  - Detecção automática de execuções interrompidas
  - Validação de integridade dos dados
  - Limpeza automática após conclusão bem-sucedida

#### Salvamento Incremental de Dados
- **`IncrementalWriter`** (`adalove_extractor/io/incremental_writer.py`)
  - Escrita append-only em JSONL para máxima segurança
  - Backup por semana como snapshot de segurança
  - Flush automático após cada semana processada
  - Consolidação de dados ao finalizar execução
  - Validação de integridade dos dados escritos

#### Sistema de Recuperação Inteligente
- **`RecoveryManager`** (`adalove_extractor/io/recovery.py`)
  - Detecção automática de execuções interrompidas
  - Interface interativa para escolha de ação (continuar/recomeçar/abortar)
  - Consolidação de dados de múltiplas execuções
  - Validação de integridade antes de retomar
  - Limpeza inteligente de arquivos temporários

#### Integração Resiliente no CLI
- **`cli/main.py`** completamente refatorado
  - Detecção automática de execuções anteriores na inicialização
  - Prompt interativo mostrando progresso da execução interrompida
  - Salvamento incremental após cada semana (não apenas no final)
  - Tratamento de erros com checkpoint de falha
  - Função `resume_extraction()` para retomada precisa

#### Testes Abrangentes
- **41 testes** implementados com 100% de sucesso
  - 11 testes unitários para CheckpointManager
  - 12 testes unitários para IncrementalWriter
  - 13 testes unitários para RecoveryManager
  - 5 testes de integração para fluxo completo
- **Cobertura de código** >70% nos módulos críticos
- **Teste manual** validando recuperação após interrupção

### Modificado

#### Estrutura de Arquivos de Saída
- **Checkpoint principal**: `progress.json` com estado detalhado
- **Dados incrementais**: `cards_temp_[execution_id].jsonl` (append-only)
- **Backups por semana**: `checkpoint_semana_XX.json` como snapshots
- **Arquivos finais**: `cards.csv`, `enriched_cards.jsonl`, `stats_by_week.json`

#### Fluxo de Execução
- **Detecção automática** de execuções interrompidas na inicialização
- **Salvamento após cada semana** processada (não apenas no final)
- **Validação de integridade** antes de retomar execuções
- **Limpeza automática** de arquivos temporários após sucesso

### Corrigido

#### Problema Crítico de Perda de Dados
- **Zero perda de dados** mesmo com falhas durante extração
- **Recuperação automática** de execuções interrompidas
- **Salvamento incremental** evita perda total em caso de erro
- **Validação robusta** garante integridade dos dados

### Segurança

#### Proteção Contra Perda de Dados
- **Arquivo JSONL append-only**: Impossível corromper dados existentes
- **Backup por semana**: Snapshots de segurança para cada semana
- **Checkpoint detalhado**: Estado completo para recuperação precisa
- **Validação de integridade**: Verificação antes de retomar execuções

---

## [3.0.0] - 2025-10-08

### Contexto
Esta release representa uma refatoração completa da arquitetura, transformando o script monolítico de 1.018 linhas em um **pacote Python profissional modular** com separação clara de responsabilidades e testabilidade completa.

### Adicionado

#### Arquitetura Modular em Pacote Python
Refatoração completa em módulos especializados:

**`adalove_extractor/models/`** - Modelos de dados com Pydantic
- `Card`: Modelo de card bruto (10 campos básicos)
- `EnrichedCard`: Modelo de card enriquecido (30 campos totais)
- Validação automática de dados com type hints completos

**`adalove_extractor/enrichment/`** - Sistema de enriquecimento modular
- `normalizer.py`: Normalização de datas, URLs e textos
- `classifier.py`: Classificação de cards (instrução/autoestudo/ponderada)
- `anchor.py`: Motor de ancoragem com algoritmo multi-fator
- `engine.py`: Orquestração do enriquecimento completo

**`adalove_extractor/browser/`** - Automação de navegador
- `auth.py`: Autenticação no AdaLove via Google OAuth
- `navigator.py`: Navegação, descoberta de semanas e manipulação de modais

**`adalove_extractor/extractors/`** - Extração de dados
- `card.py`: Extração detalhada de cards individuais
- `week.py`: Extração por semana

**`adalove_extractor/io/`** - Input/Output
- `writers.py`: Exportação para CSV e JSONL
- Funções de escrita incremental e estatísticas

**`adalove_extractor/utils/`** - Utilitários
- `hash.py`: Geração de hashes de integridade
- `text.py`: Manipulação e comparação de texto (similaridade)

**`adalove_extractor/config/`** - Configuração
- `settings.py`: Configurações centralizadas com Pydantic Settings
- `logging.py`: Setup de logging configurável
- Carregamento de `.env` e variáveis de ambiente

**`adalove_extractor/cli/`** - Interface de linha de comando
- `main.py`: Ponto de entrada modular para execução

#### Empacotamento Profissional
- `pyproject.toml`: Configuração moderna de pacote Python
  - Metadados completos do projeto
  - Dependências separadas (runtime vs dev)
  - Configuração de ferramentas (black, isort, mypy, pytest)
  - Entry point para instalação: `adalove-extract`
- Instalável via `pip install -e .`
- Importável: `from adalove_extractor import Card, EnrichedCard`

#### Documentação de Código
- **100% de docstrings** em funções públicas
- Type hints completos em todas as assinaturas
- Comentários explicativos em português para lógica complexa
- Exemplos de uso em docstrings

### Modificado

#### Preservação de Funcionalidades Críticas
✅ **Sistema de ancoragem intacto**:
- Algoritmo multi-fator de pontuação preservado
- Lógica de confiança (high/medium/low) mantida
- Similaridade de títulos com Jaccard preservada
- Proximidade posicional mantida

✅ **Formato de saída compatível**:
- CSV básico: mesmos 10 campos
- CSV enriquecido: mesmos 30 campos
- JSONL: formato preservado
- Nomes de arquivos: mesmo padrão com timestamp

✅ **Comportamento idêntico**:
- Fluxo de extração preservado
- Interação com usuário mantida
- Logs no mesmo formato
- Estatísticas por semana preservadas

#### Melhorias Técnicas
- **Reusabilidade**: Cada módulo pode ser usado independentemente
- **Testabilidade**: Funções puras e injeção de dependências
- **Manutenibilidade**: Código organizado por responsabilidade
- **Extensibilidade**: Fácil adicionar novos extractors ou enrichers
- **Type Safety**: Pydantic valida dados em runtime

#### Estrutura de Arquivos
```
adalove_extract_cards_enhanced/
├── adalove_extractor/          # Novo pacote Python
│   ├── __init__.py
│   ├── browser/                # Automação
│   ├── cli/                    # Interface
│   ├── config/                 # Configuração
│   ├── enrichment/             # Enriquecimento
│   ├── extractors/             # Extração
│   ├── io/                     # I/O
│   ├── models/                 # Modelos
│   └── utils/                  # Utilitários
├── main_v3.py                  # Script de execução modular
├── adalove_extractor.py        # Script original (legacy)
├── pyproject.toml              # Config do pacote
└── requirements.txt            # Dependências atualizadas
```

### Compatibilidade
- ✅ Python 3.11+
- ✅ Backward compatible: `adalove_extractor.py` original mantido
- ✅ Mesmos outputs: CSV e JSONL com formatos preservados
- ✅ Mesma experiência de usuário

### Dependências Adicionadas
- `pydantic>=2.7.0`: Validação de modelos de dados
- `pydantic-settings>=2.0.0`: Configuração via variáveis de ambiente

### Próximos Passos (Roadmap)
- v3.1.0: Pipeline resiliente com checkpoints
- v3.2.0: CLI completa com Typer
- v3.3.0: Extração seletiva (semanas e frentes)

### Benefícios para Desenvolvedores
1. **Código mais limpo**: 15+ arquivos vs 1 monolito de 1.018 linhas
2. **Melhor organização**: Separação clara de responsabilidades
3. **Facilita contribuições**: Módulos independentes e testáveis
4. **Preparado para testes**: Arquitetura permite pytest completo
5. **Evolução segura**: Type hints e validação previnem regressões

---

## [2.0.0] - 2025-10-07

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

