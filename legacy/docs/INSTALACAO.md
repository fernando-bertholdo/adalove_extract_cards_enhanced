# 🔧 Guia de Instalação Completo

## 📋 Requisitos

- **Python 3.8+**
- **Sistema Operacional**: Windows, macOS ou Linux
- **Conexão com internet** (para instalar dependências e acessar AdaLove)

---

## 🚀 Instalação Passo a Passo

### **1. Clone o Repositório**

```bash
git clone <repository-url>
cd adalove_extract_cards
```

---

### **2. Crie um Ambiente Virtual**

É **altamente recomendado** usar um ambiente virtual para isolar as dependências do projeto.

#### macOS / Linux (bash/zsh):
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD):
```cmd
python -m venv venv
.\venv\Scripts\activate
```

**Como saber se está ativo?**
- Você verá `(venv)` no início da linha do terminal

---

### **3. Atualize o pip**

```bash
python -m pip install --upgrade pip
```

---

### **4. Instale as Dependências**

#### Opção A: Instalação Mínima (Recomendada)
Apenas o necessário para executar o extractor:

```bash
pip install -r requirements.txt
```

**Dependências instaladas:**
- `playwright==1.49.1` - Automação do navegador
- `python-dotenv==1.0.1` - Gerenciamento de variáveis de ambiente

#### Opção B: Instalação Completa (Com Ferramentas de Análise)
Inclui pandas, numpy e outras bibliotecas para análise de dados:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Dependências adicionais:**
- `pandas==2.2.3` - Análise de dados
- `numpy==2.2.1` - Operações numéricas
- `python-dateutil==2.9.0.post0` - Manipulação de datas
- `pytz==2024.2` - Fusos horários
- E outras bibliotecas auxiliares

**Quando usar a instalação completa?**
- ✅ Se você pretende analisar os dados com Python
- ✅ Se você vai usar pandas/numpy para análises
- ❌ Se você só quer extrair e abrir no Excel

---

### **5. Instale o Navegador Chromium**

O Playwright precisa do navegador Chromium para funcionar:

```bash
playwright install chromium
```

**Tempo estimado:** 30 segundos - 2 minutos (depende da sua conexão)

**O que isso faz?**
- Baixa uma versão específica do Chromium (~100 MB)
- Instala em uma pasta gerenciada pelo Playwright
- Não interfere com seu navegador Chrome/Edge instalado

---

### **6. Configure as Credenciais**

#### Passo 1: Copie o arquivo de exemplo

```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```

#### Passo 2: Edite o arquivo `.env`

Abra o arquivo `.env` com seu editor preferido:

```bash
# Linux/macOS
nano .env
# ou
vim .env
# ou
code .env  # se tiver VSCode

# Windows
notepad .env
```

#### Passo 3: Preencha suas credenciais

```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha_aqui
```

**⚠️ IMPORTANTE:**
- Use seu email institucional completo
- A senha é a mesma que você usa para entrar no AdaLove
- O arquivo `.env` está no `.gitignore` e nunca será commitado
- Nunca compartilhe este arquivo ou suas credenciais

---

## ✅ Verificação da Instalação

Após seguir todos os passos, verifique se está tudo certo:

### 1. Verifique o Python
```bash
python --version
# Deve mostrar: Python 3.8.x ou superior
```

### 2. Verifique o ambiente virtual
```bash
# Você deve ver (venv) no início da linha
which python  # Linux/macOS
where python  # Windows
# Deve apontar para o Python do venv
```

### 3. Verifique as dependências
```bash
pip list
# Deve incluir: playwright, python-dotenv
```

### 4. Verifique o Chromium
```bash
playwright show-trace
# Se não der erro, está instalado
```

### 5. Verifique o arquivo .env
```bash
# Linux/macOS
cat .env

# Windows
type .env

# Deve mostrar suas credenciais (sem compartilhar com ninguém!)
```

---

## 🔧 Resolução de Problemas na Instalação

### Erro: "python: command not found"

**Causa**: Python não está instalado ou não está no PATH

**Solução**:
1. Instale Python 3.8+ do [python.org](https://www.python.org/downloads/)
2. Durante instalação no Windows, marque "Add Python to PATH"
3. Reinicie o terminal após instalar

---

### Erro: "pip: command not found"

**Causa**: pip não está instalado

**Solução**:
```bash
# Linux/macOS
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

---

### Erro: "playwright install" falha

**Causa**: Falta de permissões ou problemas de rede

**Solução**:
```bash
# Tente com sudo (Linux/macOS)
sudo playwright install chromium

# Ou especifique o browser explicitamente
playwright install --force chromium
```

---

### Erro: "Permission denied" ao criar venv

**Causa**: Falta de permissões na pasta

**Solução**:
```bash
# Verifique permissões da pasta
ls -la

# Mude as permissões se necessário (Linux/macOS)
chmod +x .

# Ou crie em outro local com permissões
```

---

### Erro: "Activate.ps1 cannot be loaded"

**Causa**: PowerShell com política de execução restritiva

**Solução**:
```powershell
# Execute como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois ative o venv normalmente
.\venv\Scripts\Activate.ps1
```

---

### Erro: Importação falha após instalar requirements

**Causa**: Ambiente virtual não está ativo

**Solução**:
```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Depois reinstale
pip install -r requirements.txt
```

---

## 📦 Estrutura de Dependências

### `requirements.txt` (Mínimo)
```
playwright==1.49.1
python-dotenv==1.0.1
```

**Por que essas?**
- `playwright`: Automação do navegador para acessar o AdaLove
- `python-dotenv`: Carrega credenciais do arquivo .env com segurança

### `requirements-dev.txt` (Análise)
```
pandas==2.2.3
numpy==2.2.1
python-dateutil==2.9.0.post0
pytz==2024.2
tzdata==2024.2
typing_extensions==4.12.2
six==1.17.0
pyee==12.0.0
greenlet==3.1.1
```

**Por que essas?**
- `pandas/numpy`: Análise de dados científica
- `python-dateutil/pytz`: Manipulação avançada de datas
- Outras: Dependências transitivas

---

## 🎯 Próximos Passos

Após instalar tudo:
1. ✅ Execute o script: `python adalove_extractor.py`
2. ✅ Consulte o [README principal](../README.md) para instruções de uso
3. ✅ Veja [GUIA_EXTRACAO.md](./GUIA_EXTRACAO.md) para casos de uso

---

## 💡 Dicas de Instalação

### Dica 1: Sempre use ambiente virtual
- ✅ Isola dependências do projeto
- ✅ Evita conflitos com outros projetos
- ✅ Facilita desinstalação (basta deletar a pasta venv/)

### Dica 2: Mantenha o pip atualizado
```bash
python -m pip install --upgrade pip
```

### Dica 3: Instale apenas o que precisa
- Use `requirements.txt` se só vai extrair
- Use `requirements-dev.txt` se vai analisar com Python

### Dica 4: Verifique sua conexão
- O download do Chromium precisa de boa conexão
- Se falhar, tente em outro horário ou rede

---

**✅ Instalação completa! Pronto para extrair dados do AdaLove!**
