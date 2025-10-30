# ⚡ Quick Start - Como Executar

## 🚀 Execução Rápida

### Opção 1: Script v3.0.0 Modular (Recomendado)

```bash
./venv/bin/python main_v3.py
```

### Opção 2: Script v2.0.0 Legacy

```bash
./venv/bin/python adalove_extractor.py
```

---

## 📝 Passo a Passo Completo

### 1. Navegue até o projeto

```bash
cd ~/Documents/Inteli/adalove_extract_cards_enhanced
```

### 2. Execute o script

```bash
# v3.0.0 Modular (novo)
./venv/bin/python main_v3.py

# OU v2.0.0 Legacy (original)
./venv/bin/python adalove_extractor.py
```

### 3. Siga as instruções

1. Digite o nome da turma (ex: `modulo6`)
2. Aguarde o login automático
3. **Selecione a turma na interface do navegador**
4. Pressione Enter
5. Aguarde a extração completa

---

## 🔧 Por Que Usar `./venv/bin/python`?

O venv (ambiente virtual) contém todas as dependências instaladas:
- playwright
- pydantic
- pydantic-settings
- python-dotenv

**Alternativa**: Ativar o venv primeiro

```bash
# Ativar venv (macOS/Linux)
source venv/bin/activate

# Agora pode usar 'python' diretamente
python main_v3.py

# Desativar quando terminar
deactivate
```

---

## ✅ Verificação Rápida

### Testar se está funcionando:

```bash
# Verificar Python
./venv/bin/python --version
# Deve mostrar: Python 3.13.3

# Verificar dependências
./venv/bin/pip list | grep -E "(pydantic|playwright)"
# Deve mostrar: playwright, pydantic, pydantic-settings
```

---

## 📊 Arquivos Gerados

Após a execução, você terá em `dados_extraidos/[nome_turma]/`:

```
dados_extraidos/modulo6/
├── cards_completos_20251008_153634.csv        # 10 campos básicos
├── cards_enriquecidos_20251008_153634.csv     # 30 campos enriquecidos
└── cards_enriquecidos_20251008_153634.jsonl   # JSON Lines
```

---

## 🐛 Troubleshooting

### Erro: "command not found: python"

**Solução**: Use `./venv/bin/python` em vez de apenas `python`

### Erro: "No module named 'playwright'"

**Solução**: Instale as dependências

```bash
./venv/bin/pip install -r requirements.txt
```

### Erro: "LOGIN or SENHA not set"

**Solução**: Configure o arquivo `.env`

```bash
# Copie o exemplo
cp .env.example .env

# Edite com suas credenciais
nano .env
```

---

## 🎯 Comandos Mais Usados

```bash
# Executar extração (v3.0.0)
./venv/bin/python main_v3.py

# Executar extração (v2.0.0)
./venv/bin/python adalove_extractor.py

# Ver logs
tail -f logs/*.log

# Ver últimos arquivos gerados
ls -lhtr dados_extraidos/*/
```

---

## 📚 Documentação Completa

- [README Principal](./README.md)
- [Guia de Migração v3.0.0](./MIGRATION_v3.md)
- [Guia de Extração](./documents/GUIA_EXTRACAO.md)
- [Dados Extraídos](./documents/DADOS_EXTRAIDOS.md)

---

**Dica**: Adicione um alias no seu `.zshrc` ou `.bashrc`:

```bash
# Adicione ao final do arquivo ~/.zshrc
alias adalove-v3="cd ~/Documents/Inteli/adalove_extract_cards_enhanced && ./venv/bin/python main_v3.py"
alias adalove-v2="cd ~/Documents/Inteli/adalove_extract_cards_enhanced && ./venv/bin/python adalove_extractor.py"

# Depois basta executar:
adalove-v3
```

---

**Pronto para usar! 🚀**








