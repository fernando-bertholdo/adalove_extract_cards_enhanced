# 🚀 AdaLove Cards Extractor - Versão Final

Script para extração completa de cards do AdaLove, incluindo materiais e organização por turma.

## 📁 Estrutura do Projeto

```
adalove_extract_cards/
├── adalove_extractor.py         # 🎯 Script principal (USAR ESTE)
├── main_completo_original.py    # 💾 Backup do script original
├── .env                         # 🔐 Credenciais (LOGIN e SENHA)
├── requirements.txt             # 📦 Dependências
├── documents/                   # 📚 Documentação
├── logs/                        # 📝 Logs das execuções
└── dados_extraidos/            # 💾 Dados extraídos organizados por turma
    ├── turma_2025-1B-T13/
    ├── turma_ES06/
    └── ...
```

## 🚀 Como Usar

### 1. Instalar dependências:
```bash
pip install playwright python-dotenv
playwright install chromium
```

### 2. Configurar credenciais no `.env`:
```
LOGIN=seu.email@inteli.edu.br
SENHA=suasenha
```

### 3. Executar extração:
```bash
python adalove_extractor.py
```

### 4. Processo de execução:
1. **Nome da turma**: Digite o nome para criar a pasta organizacional
2. **Login automático**: Script tenta login automático (fallback manual se necessário)  
3. **Seleção de turma**: Selecione manualmente a turma na interface
4. **Extração automática**: Script processa todas as semanas automaticamente
5. **Dados salvos**: CSV completo na pasta `dados_extraidos/nome_turma/`

## 📊 Dados Extraídos

O script extrai **dados completos** de cada card:

- ✅ **Título e descrição** 
- ✅ **Texto completo** do card
- ✅ **Links externos** encontrados
- ✅ **Materiais** (Google Drive, Docs, etc.)
- ✅ **Arquivos** (PDFs, DOCs, etc.)
- ✅ **Tipo** (Atividade, Projeto, etc.)
- ✅ **Organização** por semana e índice

### Exemplo de saída CSV:
```csv
semana,indice,titulo,descricao,links,materiais,arquivos
Semana 01,1,"Introdução ao Python","Conceitos básicos...","Link: https://...","Material: https://drive.google.com/...","Arquivo: exercicios.pdf"
```

## 📁 Organização por Turma

- Cada extração cria uma **pasta com nome da turma**
- Dados de **cada turma ficam separados**
- **Múltiplas execuções** não sobrescrevem dados anteriores
- **Logs individuais** por turma e timestamp

## 🔧 Funcionalidades

### ✅ **Login Inteligente**
- Tenta login automático com Google
- Fallback manual se necessário
- Suporte a credenciais do `.env`

### ✅ **Extração Completa**
- Descobre **todas as semanas** automaticamente
- Extrai **links e materiais** dos cards
- Categoriza **tipos de conteúdo**
- **Logging detalhado** para debug

### ✅ **Organização Automática**
- **Pastas por turma** em `dados_extraidos/`
- **Timestamps** nos arquivos
- **Logs separados** por execução

## 📝 Logs

Logs salvos em: `logs/nome_turma_TIMESTAMP.log`

- ✅ **Processo de login**
- ✅ **Semanas descobertas**
- ✅ **Cards processados por semana**
- ✅ **Links e materiais encontrados**
- ✅ **Estatísticas finais**

## ⚡ Exemplo de Execução

```
🚀 ADALOVE CARDS EXTRACTOR - VERSÃO FINAL
📁 Digite o nome da turma para organizar os dados: 2025-1B-T13
🔑 Fazendo login...
✅ Login realizado!
🏠 Navegando para academic-life...
👆 Agora selecione a turma na interface:
⏸️ Pressione Enter após selecionar a turma na página: [ENTER]
🔍 Descobrindo semanas disponíveis...
📊 10 semanas descobertas
📚 Processando 10 semanas...
🔄 Semana 01 (1/10)
   ✅ 14 cards encontrados
   📊 14 cards processados com sucesso
...
🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!
📊 127 cards extraídos
📚 10 semanas processadas
🔗 89 cards com links
📎 67 cards com materiais
📁 Pasta: dados_extraidos/2025-1B-T13/
💾 Arquivo: cards_completos_20250825_190245.csv
```

## 🎯 Diferenças da Versão Final

### ✅ **Script Único**
- Um só arquivo para usar: `adalove_extractor.py`
- Não há mais confusão entre versões

### ✅ **Extração de Materiais**  
- Links externos, Google Drive, documentos
- Categorização automática de tipos de conteúdo
- Máximo de informações extraídas

### ✅ **Organização por Turma**
- Pasta individual para cada turma
- Fácil localização dos dados
- Histórico preservado

### ✅ **Interface Simplificada**
- Input claro do nome da turma
- Seleção manual confiável
- Feedback visual do progresso

## 🚨 Importante

- **Use apenas**: `adalove_extractor.py` 
- **Seleção manual** da turma é **intencional** (mais confiável)
- **Dados organizados** por turma automaticamente
- **Logs detalhados** para qualquer problema

---
🎉 **Versão final pronta para uso em produção!**
