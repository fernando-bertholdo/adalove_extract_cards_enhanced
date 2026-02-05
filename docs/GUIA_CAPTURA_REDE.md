# 🔍 Guia de Captura de Requisições de Rede - AdaLove

## 🎯 Objetivo

Este guia te ajudará a **capturar todas as requisições HTTP** que o AdaLove faz ao navegar pela plataforma. Essas informações são essenciais para implementar a extração via requests ao invés de automação do navegador.

---

## 🛠️ Preparação

### Passo 1: Abrir Chrome DevTools

1. Abra o Google Chrome
2. Acesse: `https://adalove.inteli.edu.br`
3. Pressione `F12` (ou `Cmd+Option+I` no Mac) para abrir DevTools
4. Clique na aba **"Network"** (Rede)

### Passo 2: Configurar DevTools

✅ **Marque a opção**: "Preserve log" (Preservar log)  
✅ **Limpe o log atual**: Clique no ícone 🚫 (Limpar)  
✅ **Opcional**: Filtre por "Fetch/XHR" para ver apenas requisições de API

---

## 📋 O Que Capturar

### 1️⃣ Fluxo de Login (CRÍTICO)

**Ações:**
1. Clique em "Entrar com Google"
2. Faça login com suas credenciais
3. Aguarde redirecionamento para AdaLove

**O que procurar:**
- ✅ URL do callback: `/admin/oauth2callback.php`
- ✅ Cookies recebidos (aba "Application" → Cookies)
- ✅ Response headers com tokens/sessões

**Dados a registrar:**
```
URL: https://adalove.inteli.edu.br/admin/oauth2callback.php?...
Method: GET
Status: 302/200

Cookies:
  - MoodleSession: abc123...
  - MOODLEID1_: xyz789...

Headers:
  - Set-Cookie: ...
  - Location: ...
```

---

### 2️⃣ Navegação por Turmas

**Ações:**
1. Após login, observe o dropdown de turmas
2. Selecione uma turma específica
3. Aguarde a página carregar

**O que procurar:**
- ✅ Requisição que lista turmas disponíveis
- ✅ Requisição que carrega dados da turma selecionada
- ✅ Possível chamada para `/webservice/rest/server.php`

**Exemplo de captura:**
```
URL: https://adalove.inteli.edu.br/webservice/rest/server.php
Method: POST
Query Params:
  wstoken: [TOKEN]
  wsfunction: core_course_get_courses
  moodlewsrestformat: json

Response: [Lista de cursos/turmas]
```

---

### 3️⃣ Listagem de Semanas

**Ações:**
1. Dentro de uma turma, observe as "Semanas" sendo carregadas
2. Role a página para ver se carrega mais conteúdo

**O que procurar:**
- ✅ Como as seções/semanas são carregadas
- ✅ Se é um único request ou múltiplos
- ✅ Estrutura JSON/HTML retornada

**Exemplo esperado:**
```
URL: .../webservice/rest/server.php
wsfunction: core_course_get_contents
courseid: [ID_DA_TURMA]

Response:
[
  {
    "id": 1,
    "name": "Semana 01",
    "modules": [...]
  }
]
```

---

### 4️⃣ Abertura de Cards

**Ações:**
1. Clique em um card/atividade
2. Aguarde o modal abrir
3. Observe os detalhes carregados

**O que procurar:**
- ✅ Request para obter detalhes do card
- ✅ Tipo de atividade (modname: label, assign, resource, etc.)
- ✅ Conteúdo HTML/JSON retornado

---

## 💾 Como Salvar as Capturas

### Método 1: Exportar HAR File

1. No DevTools (aba Network), clique com botão direito
2. Selecione **"Save all as HAR with content"**
3. Salve como: `adalove_network_capture.har`
4. Compartilhe comigo para análise

### Método 2: Screenshots e Anotações

Para cada tipo de requisição importante:

1. **Screenshot da requisição** (clique na requisição → aba Headers)
2. **Copie e cole**:
   - URL completa
   - Method (GET/POST)
   - Request Headers
   - Query Params
   - Response (aba Preview/Response)

**Salve em um documento**: `captura_rede_adalove.txt`

---

## 🔍 Checklist de Captura

Garanta que capturou:

- [ ] **Login OAuth completo**
  - [ ] Redirecionamento para Google
  - [ ] Callback do Google para AdaLove
  - [ ] Cookies de sessão recebidos
  
- [ ] **Listagem de Turmas**
  - [ ] Request que retorna lista de turmas
  - [ ] Estrutura JSON das turmas
  
- [ ] **Conteúdo de Turma (Semanas)**
  - [ ] Request para obter semanas/seções
  - [ ] Estrutura JSON das semanas
  
- [ ] **Detalhes de Cards**
  - [ ] Request ao abrir um card
  - [ ] Conteúdo retornado (descrição, links, etc.)
  
- [ ] **Headers Importantes**
  - [ ] Cookie: MoodleSession
  - [ ] User-Agent
  - [ ] Referer
  - [ ] Qualquer header com "token"

---

## 🎓 Exemplo de Análise

Ao capturar, você verá algo assim no DevTools:

```
Name: server.php
Status: 200
Type: xhr
Size: 15.2 KB
Time: 234 ms

Request URL: https://adalove.inteli.edu.br/webservice/rest/server.php
Request Method: POST

Query String Parameters:
  wstoken: a1b2c3d4e5f6g7h8i9j0
  wsfunction: core_course_get_contents
  courseid: 42
  moodlewsrestformat: json

Response:
[
  {
    "id": 1,
    "name": "Semana 01",
    "summary": "Introdução ao módulo",
    "modules": [
      {
        "id": 789,
        "name": "Instrução - Boas vindas",
        "modname": "label",
        ...
      }
    ]
  }
]
```

✅ **Ótimo!** Isso confirma que AdaLove usa Moodle Web Services!

---

## ❓ Dúvidas Comuns

**P: E se não aparecer nada no Network?**  
R: Certifique-se de que "Preserve log" está marcado e limpe o log antes de começar.

**P: Há muitas requisições, quais são importantes?**  
R: Foque em:
- Qualquer URL com `/webservice/`
- Qualquer URL com `/login/`
- Requisições POST/GET que retornam JSON

**P: Preciso capturar tudo em uma sessão?**  
R: Não! Pode fazer em partes:
1. Sessão 1: Login
2. Sessão 2: Navegação por turmas
3. Sessão 3: Abertura de cards

---

## 📤 O Que Fazer Depois

Após capturar as requisições:

1. ✅ Salve o arquivo HAR ou suas anotações
2. ✅ Compartilhe comigo para análise
3. ✅ Eu vou analisar e documentar os endpoints
4. ✅ Implementaremos o cliente de API com base nisso

---

**Status**: 📖 Guia pronto para uso  
**Última atualização**: 2026-02-03  
**Próximo passo**: Executar a captura e compartilhar resultados
