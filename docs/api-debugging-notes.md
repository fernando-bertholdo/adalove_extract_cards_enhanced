# Descobertas e Problemas da API - Fase 3

## ✅ Sucessos

### 1. Autenticação Funcionando
- ✅ Login via Google OAuth com Playwright
- ✅ Extração de `accessToken` do localStorage
- ✅ Token aceito pela API (não retorna 401)

### 2. Estrutura da API Descoberta
- ✅ Base URL: `https://apiv2.inteli.edu.br`
- ✅ Autenticação: `Authorization: Bearer {accessToken}`
- ✅ Endpoints mapeados via browser agent

---

## ❌ Problemas Encontrados

### Problema 1: Endpoint `/sections` Retorna 500

**Sintoma**:
```
HTTP Request: GET https://apiv2.inteli.edu.br/sections "HTTP/1.1 500 Internal Server Error"
```

**Contexto**:
- ✅ Funciona no browser (browser agent conseguiu fazer fetch)
- ❌ Falha no script Python com httpx
- ✅ Token está correto (não é erro 401)

**Possíveis Causas**:
1. **Headers faltando**: Browser envia headers adicionais (User-Agent, Origin, Referer, etc.)
2. **CORS**: API pode rejeitar requests de fora do browser
3. **Cookies adicionais**: Além do token, pode precisar de cookies de sessão
4. **Endpoint instável**: API pode estar com problemas temporários

**Investigação Necessária**:
- [ ] Comparar headers enviados pelo browser vs script
- [ ] Adicionar headers do browser (Origin, Referer, etc.)
- [ ] Verificar se precisa de cookies adicionais
- [ ] Testar endpoint em horário diferente

---

## 🔄 Próximas Ações

### Opção 1: Fix Headers
Adicionar todos os headers que o browser envia:
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 ...",  # User-Agent realista
    "Origin": "https://adalove.inteli.edu.br",
    "Referer": "https://adalove.inteli.edu.br/academic-life",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}
```

### Opção 2: Usar Endpoint Alternativo
Se `/sections` não funcionar, usar endpoint conhecido que funciona:
- `/sections/{uuid}/userdata` - sabemos que funciona
- Hardcode UUID de uma turma conhecida para testes
- Extrair lista de turmas de outra forma

### Opção 3: Modo Híbrido Temporário
- Usar Playwright para obter lista de seções
- Usar API para extrair atividades (mais rápido)
- Melhor dos dois mundos

---

## 📊 Status Atual

| Componente | Status | Notas |
|------------|--------|-------|
| **Autenticação** | ✅ OK | accessToken funciona |
| **Cliente HTTP** | ✅ OK | Retry e error handling funcionando |
| **Endpoint /sections** | ❌ FALHA | 500 error |
| **Endpoint /userdata** | ❓ NÃO TESTADO | Precisa UUID de seção |
| **Extração de atividades** | ❓ NÃO TESTADO | Depende de /userdata |

---

**Próximo passo**: Adicionar headers realistas do browser e re-testar
