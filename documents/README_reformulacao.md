# AdaLove Cards Extractor - Reformulação

## 🔄 Principais Mudanças

### Fluxo Reformulado
1. **Login** - Mantido o sistema inteligente de login com Google
2. **Navegação Direta** - Após login, navega diretamente para `/academic-life` (não mais para `/feed`)
3. **Seleção de Turma com Input** - Abre modal de turmas e pede input do usuário no terminal
4. **Sistema de Logging** - Logs detalhados em arquivo e console

### Novo Fluxo de Navegação
```
Login → academic-life → Abrir Modal → Input Usuário → Filtrar Turma → Selecionar
```

### Sistema de Logging
- Logs salvos na pasta `logs/` com timestamp
- Formato: `adalove_extraction_YYYYMMDD_HHMMSS.log`
- Logs simultâneos em arquivo e console
- Níveis: INFO, WARNING, ERROR, DEBUG

## 🚀 Como Usar

### 1. Executar o Script
```bash
python main_completo.py
```

### 2. Input da Turma
Quando solicitado, digite o nome **exato** da turma:
- Exemplos: `2025-1B-T13`, `GRAD ES06`, `Turma 13`
- O script usará este nome para filtrar a lista

### 3. Intervenções Manuais
O script pode solicitar intervenção manual em:
- Login (se automático falhar)
- Seleção do dropdown (se não encontrar automaticamente)
- Digitação no filtro (se campo não for encontrado)
- Clique na turma (se opção não for encontrada)

## 📝 Logs e Debug

### Localização dos Logs
- Pasta: `logs/`
- Arquivo atual: `adalove_extraction_YYYYMMDD_HHMMSS.log`

### Informações Registradas
- ✅ Sucessos e falhas em cada etapa
- 🔍 Seletores tentados e resultados
- 📍 URLs visitadas
- ⏱️ Tempos de execução
- 🎯 Inputs do usuário
- ❌ Erros detalhados

### Exemplo de Log
```
2025-08-25 14:30:15 | INFO | 🚀 Iniciando extração reformulada do AdaLove...
2025-08-25 14:30:16 | INFO | 🌐 Acessando página inicial do AdaLove...
2025-08-25 14:30:20 | INFO | 🔑 Procurando botão 'Entrar com o Google'...
2025-08-25 14:30:21 | INFO | ✅ Botão Google encontrado, clicando...
```

## 📂 Arquivos

### Arquivos Principais
- `main_completo.py` - Script reformulado (novo)
- `main_completo_original.py` - Backup do script anterior

### Estrutura do Projeto
```
adalove_extract_cards/
├── main_completo.py              # Script principal reformulado
├── main_completo_original.py     # Backup do original
├── README_reformulacao.md        # Esta documentação
├── .env                          # Credenciais (LOGIN e SENHA)
└── logs/                         # Pasta de logs (criada automaticamente)
    ├── adalove_extraction_20250825_143015.log
    ├── adalove_extraction_20250825_151230.log
    └── ...
```

## 🛠️ Funcionalidades Novas

### 1. Sistema de Logging Avançado
```python
logger.info("✅ Operação bem-sucedida")
logger.warning("⚠️ Alerta - continuando")  
logger.error("❌ Erro crítico")
```

### 2. Input de Turma no Terminal
```python
nome_turma = input("Digite o nome exato da turma: ").strip()
```

### 3. Navegação Direta
```python
await page.goto("https://adalove.inteli.edu.br/academic-life")
```

### 4. Filtragem Inteligente
- Tenta texto exato primeiro
- Fallback para busca parcial
- Seletores múltiplos para maior compatibilidade

### 5. Intervenções Manuais Guiadas
```python
print("🤚 INTERVENÇÃO MANUAL NECESSÁRIA")
print("👆 Clique manualmente no seletor...")
input("Aguardando... Pressione Enter após clicar: ")
```

## 🔧 Debug e Troubleshooting

### Problemas Comuns

1. **Seletor não encontrado**
   - Verificar logs para seletores tentados
   - Usar intervenção manual quando solicitado

2. **Turma não encontrada**
   - Verificar nome exato da turma
   - Logs mostrarão tentativas de busca

3. **Modal não abre**
   - Usar intervenção manual
   - Verificar se página carregou completamente

### Análise de Logs
- Buscar por `❌` para erros
- Buscar por `⚠️` para warnings
- Verificar seletores tentados com `🔍`

## ⚡ Melhorias Implementadas

1. **Robustez** - Múltiplos seletores para cada elemento
2. **Flexibilidade** - Intervenção manual quando necessário
3. **Transparência** - Logs detalhados de toda operação
4. **Usabilidade** - Input claro e instruções precisas
5. **Manutenibilidade** - Código bem documentado e estruturado

## 📋 Próximos Passos

Após validação bem-sucedida:
1. Implementar extração de todas as semanas
2. Salvar cards em CSV/JSON
3. Adicionar relatórios de progresso
4. Implementar retry automático para falhas
