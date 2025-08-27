# 📁 Pasta de Dados Extraídos

Esta pasta será automaticamente organizada por turma quando você executar o script.

## 📋 Estrutura Automática

Após executar `adalove_extractor.py`, a estrutura será:

```
dados_extraidos/
├── turma_2025-1B-T13/
│   ├── cards_completos_20250825_190245.csv
│   └── cards_completos_20250826_143012.csv
├── turma_ES06/
│   └── cards_completos_20250825_201538.csv
└── turma_outro_modulo/
    └── cards_completos_20250826_084521.csv
```

## 🎯 Como Funciona

1. **Input do usuário**: Nome da turma digitado no início
2. **Pasta automática**: Script cria pasta com nome da turma  
3. **Arquivo timestampado**: CSV com data/hora da extração
4. **Organização**: Dados de cada turma ficam separados

## 📊 Conteúdo dos Arquivos CSV

Cada arquivo contém **todos os cards** da turma com:
- ✅ Títulos e descrições
- ✅ Links e materiais anexados
- ✅ Arquivos e documentos
- ✅ Organização por semana

**Esta pasta estará sempre organizada e nunca sobrescreverá dados anteriores!**
