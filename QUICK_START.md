# ⚡ Quick Start - Adalove Extract Cards v2

## 3 Passos para Extrair Dados

### 1. Configure o Ambiente

```bash
# Clone o repositório
git clone https://github.com/fernando-bertholdo/adalove_extract_cards_enhanced.git
cd adalove_extract_cards_enhanced

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: .\venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure Credenciais

```bash
cp .env.example .env
```

Edite `.env`:
```env
LOGIN=seu.email@sou.inteli.edu.br
SENHA=sua_senha
```

### 3. Execute a Extração

```bash
# Extrair turma completa
python extrair_turma_completa.py "2026-1A-T13"
```

## ✅ Resultado

Os dados estarão em:

```
output/api_extraction/2026-1A-T13/
├── extracao_completa.json    # Todas as semanas
└── semanas/
    ├── semana_01.json
    ├── semana_02.json
    └── ...
```

## 📖 Próximos Passos

- [README.md](./README.md) - Documentação completa
- [GUIA_CAPTURA_REDE.md](./documents/GUIA_CAPTURA_REDE.md) - Captura de tokens

---

**🎉 Pronto! Extração completa em ~1 minuto!**
