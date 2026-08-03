# ⚡ Quick Start — Adalove Extract Cards

Requer **Python 3.11+**. Ter o **Google Chrome** instalado é recomendado: o
extrator usa o Chrome do sistema para o login e, sem ele, recorre ao Chromium do
Playwright, que o Google às vezes recusa por "navegador não seguro".

## 1. Configure o ambiente

**macOS / Linux**

```bash
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced

py -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
playwright install chromium
```

Se o PowerShell bloquear o `Activate.ps1`, libere só para esta sessão:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. Configure as credenciais

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Edite o `.env`:

```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

## 3. Execute

```bash
python adalove_cli.py
```

Sem flags, abre o menu interativo. Para automação:

```bash
python adalove_cli.py --list                    # turmas já extraídas localmente
python adalove_cli.py --list --remote           # turmas disponíveis na API
python adalove_cli.py --extrair "2026-1A-T13"   # extrai uma turma
python adalove_cli.py --extrair-todas --paralelo 3
```

## Primeiro login

A janela do navegador abre e **permanece aberta** até você concluir o login,
inclusive a verificação em duas etapas. Depois disso a sessão fica salva em
`.auth_profile/`, e as execuções seguintes autenticam sozinhas, sem abrir janela.

| Situação | macOS / Linux | Windows (PowerShell) |
|---|---|---|
| Mais tempo para o 2FA | `ADALOVE_AUTH_TIMEOUT=600 python adalove_cli.py` | `$env:ADALOVE_AUTH_TIMEOUT=600; python adalove_cli.py` |
| Acompanhar o log | `tail -f adalove_cli.log` | `Get-Content adalove_cli.log -Wait -Tail 30` |
| Recomeçar do zero | `rm -rf .auth_profile .token_cache` | `rmdir /s /q .auth_profile; del .token_cache` |

## ✅ Resultado

```
output/api_extraction/2026-1A-T13/
├── extracao_completa.json    # Todas as semanas
└── semanas/
    ├── semana_01.json
    ├── semana_02.json
    └── ...
```

## 📖 Próximos passos

- [README.md](./README.md) — documentação completa
- [docs/API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) — endpoints da API
- [docs/ESTRUTURA_SAIDA.md](./docs/ESTRUTURA_SAIDA.md) — formato dos arquivos gerados
