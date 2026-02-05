# AdaLove API Research - Mapeamento de Endpoints

## 📋 Visão Geral

Este documento registra a pesquisa sobre como extrair dados do **AdaLove** (LMS baseado em Moodle do Inteli) usando **requisições HTTP diretas** ao invés de automação de navegador.

---

## 🔍 Descobertas Chave

### Plataforma Base: Moodle

✅ **AdaLove é baseado em Moodle** → pode usar APIs padrão do Moodle  
✅ **Moodle suporta Web Services REST** → endpoint: `/webservice/rest/server.php`  
✅ **Autenticação via tokens** → tokens específicos por usuário/contexto  
✅ **Google OAuth2 integrado** → login via Google, depois obter token Moodle  

---

## 🔐 Autenticação

### Fluxo Atual (Playwright)

```
1. Usuário → Clica "Entrar com Google" → Redireciona para accounts.google.com
2. Google → Autentica credenciais → Redireciona para adalove.inteli.edu.br/admin/oauth2callback.php
3. AdaLove → Estabelece sessão Moodle → Cookies armazenados no navegador
```

### Fluxo Proposto (Requests)

**Opção 1: Token de Web Service (Recomendado)**
```
1. Autenticar via Google OAuth (similar ao flow atual)
2. Obter sessão Moodle (MoodleSession cookie)
3. Gerar token de Web Service para API calls
4. Usar token em todas as requisições: wstoken={token}
```

**Opção 2: Login Direto (Se disponível)**
```
POST https://adalove.inteli.edu.br/login/token.php
Body: username={email}&password={senha}&service={service_name}

Response: {"token": "abc123..."}
```

### Endpoints de Autenticação

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/admin/oauth2callback.php` | GET | Callback do Google OAuth |
| `/login/token.php` | POST | Obter token via credenciais (se habilitado) |
| `/webservice/rest/server.php` | GET/POST | API REST principal |

---

## 📊 APIs do Moodle

### Estrutura de Requisição

```
GET/POST https://adalove.inteli.edu.br/webservice/rest/server.php

Query Parameters:
  wstoken={token}               # Token de autenticação
  wsfunction={function_name}    # Função a executar
  moodlewsrestformat=json       # Formato da resposta
  ...{outros parâmetros}        # Específicos por função
```

### Funções Essenciais para Extração

#### 1. Listar Cursos (Turmas)
```
wsfunction: core_course_get_courses

Response:
[
  {
    "id": 123,
    "fullname": "Módulo 6 - Engenharia de Software",
    "shortname": "ES06",
    "categoryid": 5,
    "visible": 1,
    ...
  }
]
```

#### 2. Obter Conteúdo do Curso
```
wsfunction: core_course_get_contents
courseid: {course_id}

Response:
[
  {
    "id": 1,
    "name": "Semana 01",
    "section": 1,
    "modules": [
      {
        "id": 456,
        "name": "Instrução - Introdução ao Módulo",
        "modname": "label",
        "description": "...",
        "url": "...",
        ...
      }
    ]
  }
]
```

#### 3. Detalhes de Atividades
```
wsfunction: mod_{modname}_view_{modname}
{modname}id: {module_id}

Exemplo para "assign" (tarefa):
wsfunction: mod_assign_view_assign
assignid: 789
```

### Mapeamento: Conceitos AdaLove ↔ Moodle

| AdaLove | Moodle | API Call |
|---------|--------|----------|
| **Turma** | Course | `core_course_get_courses` |
| **Semana** | Section/Topic | `core_course_get_contents` |
| **Card** | Module/Activity | Dentro de `sections[].modules[]` |
| **Tipo de Card** | Module Type | `modname` (label, assign, resource, etc.) |

---

## 🎯 Endpoints Descobertos (Captura Real)

### ✅ Captura Realizada em: 2026-02-03

Usando browser automation, capturamos as requisições reais do AdaLove durante:
- ✅ Login via Google OAuth
- ✅ Seleção de turma (2025-1A-T13)
- ✅ Navegação por semanas
- ✅ Abertura de cards/atividades

---

### 🔐 Autenticação

#### 1. OAuth Token Endpoint
```
POST https://adalove.auth.us-east-2.amazoncognito.com/oauth2/token

Descrição: Obtém token de acesso após autenticação Google
Tipo: AWS Cognito OAuth2
```

**Descoberta Importante**: AdaLove usa **AWS Cognito** para autenticação, não autenticação Moodle tradicional!

---

### 👤 Dados do Usuário

#### 2. User Details
```
GET https://apiv2.inteli.edu.br/users/details

Headers:
  Authorization: Bearer {token}

Response:
{
  "id": "...",
  "name": "Fernando Bertholdo",
  "email": "fernando.bertholdo@sou.inteli.edu.br",
  ...
}
```

#### 3. User Menus
```
GET https://apiv2.inteli.edu.br/users/menus

Descrição: Retorna estrutura de menus/navegação do usuário
```

---

### 📚 Estrutura de Cursos/Turmas

#### 4. Sections (Semanas)
```
GET https://apiv2.inteli.edu.br/sections

Descrição: Lista todas as seções/semanas disponíveis para o usuário
Response: Array de seções com IDs, nomes, datas
```

#### 5. Section User Data
```
GET https://apiv2.inteli.edu.br/sections/{section_uuid}/userdata

Descrição: Dados de progresso do aluno em uma seção específica
Parâmetros:
  - section_uuid: UUID da seção/semana
```

#### 6. Student Course Descriptions
```
GET https://apiv2.inteli.edu.br/student-course-descriptions/section/{section_uuid}

Descrição: Lista de atividades/cards de uma seção específica
Response: Array de atividades com:
  - id
  - title
  - description
  - type
  - materials
  - due_date
  ...
```

---

### 🔔 Outros Endpoints

#### 7. Notifications
```
GET https://apiv2.inteli.edu.br/notifications

Descrição: Sistema de notificações do usuário
```

#### 8. Versions
```
GET https://apiv2.inteli.edu.br/versions

Descrição: Verificação de versão da API
```

---

## 🎨 Estrutura da API

### Base URL
```
https://apiv2.inteli.edu.br
```

### Padrão de Autenticação
```
Authorization: Bearer {cognito_token}
```

### Mapeamento: AdaLove ↔ API

| Conceito AdaLove | Endpoint API | Método |
|------------------|--------------|--------|
| **Login** | `adalove.auth.us-east-2.amazoncognito.com/oauth2/token` | POST |
| **Perfil do Usuário** | `/users/details` | GET |
| **Lista de Semanas** | `/sections` | GET |
| **Atividades de uma Semana** | `/student-course-descriptions/section/{uuid}` | GET |
| **Progresso do Aluno** | `/sections/{uuid}/userdata` | GET |

---

## 🔍 Descoberta Crítica: NÃO é Moodle Padrão!

**IMPORTANTE**: A captura revelou que AdaLove **NÃO usa APIs padrão do Moodle**.

### Diferenças Identificadas:

| Aspecto | Esperado (Moodle) | Real (AdaLove) |
|---------|-------------------|----------------|
| **Autenticação** | Session cookies | AWS Cognito OAuth2 |
| **Base URL** | `/webservice/rest/server.php` | `apiv2.inteli.edu.br` |
| **Formato** | `wstoken` + `wsfunction` | REST API moderna |
| **Estrutura** | Moodle Web Services | API customizada |

### Conclusão

AdaLove é uma **plataforma customizada** que:
- ✅ Usa conceitos do Moodle (sections, activities)
- ✅ Mas tem API REST própria e moderna
- ✅ Autenticação via AWS Cognito (não Moodle auth)
- ✅ Endpoints bem estruturados e RESTful

---

## 📝 Próximos Passos

### 1. Verificar se Web Services estão habilitados no AdaLove

**Teste manual:**
```bash
curl "https://adalove.inteli.edu.br/webservice/rest/server.php?wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
```

**Esperado:**
- ✅ Se retornar JSON: Web Services habilitados
- ❌ Se retornar 404/403: Web Services desabilitados (precisa usar Playwright)

### 2. Capturar Requisições Reais

Precisamos capturar o tráfego de rede durante uso manual do AdaLove:

**O que capturar:**
- [ ] Fluxo completo de login Google OAuth
- [ ] Cookies recebidos após autenticação
- [ ] Requisições ao navegar pelas turmas
- [ ] Requisições ao abrir semanas
- [ ] Requisições ao abrir cards
- [ ] Headers enviados em cada requisição

**Ferramentas:**
- Chrome DevTools (aba Network)
- Extensão: "ModHeader" para inspecionar headers
- Exportar HAR file para análise offline

### 3. Obter Token de Web Service

Se Web Services estiverem habilitados, precisaremos:

**Opção A:** Gerar token manualmente via interface Moodle
1. Login no AdaLove como admin/usuário
2. Navegar para: `Site administration > Plugins > Web services > Manage tokens`
3. Criar token para o usuário

**Opção B:** Obter token programaticamente
1. Autenticar via Google OAuth (requests)
2. Extrair cookies/sessão
3. Fazer request para endpoint de geração de token

---

## 📝 Documentação de Referência

- [Moodle Web Services Documentation](https://docs.moodle.org/dev/Web_services)
- [Moodle REST Protocol](https://docs.moodle.org/dev/Creating_a_web_service_client#REST)
- [OAuth 2 Services in Moodle](https://docs.moodle.org/en/OAuth_2_services)
- [Core Web Service Functions](https://docs.moodle.org/dev/Web_service_API_functions)

---

## ⚠️ Riscos e Limitações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Web Services desabilitados | Média | Crítico | Manter Playwright como fallback |
| Função específica não disponível | Alta | Médio | Usar múltiplas funções combinadas |
| Rate limiting | Baixa | Médio | Implementar delays entre requests |
| Mudanças na configuração | Baixa | Alto | Manter compatibilidade com Playwright |

---

**Status**: 🔄 Em progresso  
**Última atualização**: 2026-02-03  
**Próxima ação**: Capturar requisições de rede do AdaLove
