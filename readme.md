# **Extração de Cards do AdaLove para CSV**

Este projeto tem como objetivo **auxiliar estudantes a extrair, de forma automatizada**, todas as informações presentes nos *cards* do [AdaLove (Inteli)](https://adalove.inteli.edu.br/) e **salvá-las em um arquivo CSV**. Com isso, é possível **migrar os dados** para plataformas de organização de preferência, como Trello, Notion, Google Sheets ou qualquer outra ferramenta que suporte importação de CSV. 

O projeto é escrito em Python, utilizando **Playwright** para automação de navegação em páginas web, e **asyncio** para gerenciar tarefas de forma assíncrona.

---

## **Índice**
- [**Extração de Cards do AdaLove para CSV**](#extração-de-cards-do-adalove-para-csv)
  - [**Índice**](#índice)
  - [**Visão Geral**](#visão-geral)
  - [**Tecnologias Utilizadas**](#tecnologias-utilizadas)
  - [**Instalação e Configuração**](#instalação-e-configuração)
    - [**Pré-requisitos**](#pré-requisitos)
    - [**Clonando o Repositório**](#clonando-o-repositório)
    - [**Instalando as Dependências**](#instalando-as-dependências)
    - [**Executando o Playwright Install**](#executando-o-playwright-install)
    - [**Configurando Variáveis de Ambiente**](#configurando-variáveis-de-ambiente)
  - [**Como Executar o Script**](#como-executar-o-script)
  - [**Estrutura dos Arquivos**](#estrutura-dos-arquivos)
  - [**Funcionamento Geral do Script**](#funcionamento-geral-do-script)
  - [**Possíveis Erros e Soluções**](#possíveis-erros-e-soluções)
  - [**Contato**](#contato)

---

## **Visão Geral**
Este projeto foi desenvolvido para:
- **Automatizar** o processo de login no AdaLove (via conta do Google).
- **Identificar e percorrer** unidades específicas (ex.: *Unidade 01*, *Unidade 02*, etc.).
- **Coletar informações** de cada *card* presente em cada unidade (título, tipo, professor, data de instrução, descrição, link, e possíveis atividades ponderadas).
- **Organizar** essas informações em uma lista.
- **Salvar** tudo em um arquivo `cards_adalove.csv`, de maneira ordenada, preenchendo eventuais lacunas de datas de forma automática.
- **Liberar** o navegador, encerrar o contexto e apresentar o **tempo de execução** total do script.

O arquivo CSV gerado poderá então ser **importado** em qualquer plataforma que aceite esse formato, como Trello, Notion, Excel, Google Sheets, entre outras.

---

## **Tecnologias Utilizadas**
- **Python 3.9+**  
- **Playwright**: biblioteca de automação de navegadores, permite controlar o Chrome, Firefox e Safari.  
- **asyncio**: biblioteca nativa do Python para gerenciar operações assíncronas.  
- **dotenv** (`python-dotenv`): para carregar variáveis de ambiente com segurança (credenciais).  
- **CSV** (biblioteca nativa do Python): para leitura e escrita de arquivos CSV.

---

## **Instalação e Configuração**

### **Pré-requisitos**
- Python 3.9 ou superior instalado na sua máquina.  
- Pip (gerenciador de pacotes do Python) atualizado para a última versão.  
- Navegador Google Chrome (caso deseje visualizar a automação em modo não-headless).

### **Clonando o Repositório**
Se você ainda não clonou o repositório, utilize:
```bash
git clone https://github.com/tonyJonas/adalove_extract_cards
cd adalove_extract_cards
```

### **Instalando as Dependências**
Há um arquivo `requirements.txt` que lista todas as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

Esse comando instalará:
- **playwright**
- **python-dotenv**
- E quaisquer outras dependências necessárias.

### **Executando o Playwright Install**
Após instalar as bibliotecas, é **fundamental** que você instale os navegadores suportados pelo Playwright. Para isso, rode:
```bash
playwright install
```
Esse comando baixa as versões necessárias de navegadores (Chromium, Firefox, WebKit), garantindo a compatibilidade.

### **Configurando Variáveis de Ambiente**
Este script utiliza o **dotenv** para armazenar credenciais de login de forma mais segura.  

1. Crie um arquivo chamado `.env` na raiz do seu projeto (caso ainda não exista).
2. Dentro deste arquivo, defina as variáveis `LOGIN` e `SENHA`:
   ```
   LOGIN=seu.email@exemplo.com
   SENHA=suaSenha
   ```
3. Salve o arquivo. As credenciais serão carregadas automaticamente no script Python.
4. Caso não queira utilizar o **dotenv**, apenas substitua as variáveis das credenciais com seu login e senha do Adalove.


---

## **Como Executar o Script**
Com todas as dependências instaladas e o arquivo `.env` configurado, execute:
```bash
python main.py
```

Assim que o script iniciar, ele:
1. Abrirá o navegador (Chrome) em modo **não-headless** (visível).
2. Acessará a página de login do AdaLove, clicando em **Entrar com o Google**.
3. Inserirá o seu **e-mail** e **senha** (da variável de ambiente).
4. Esperará o carregamento da página principal (identificando um elemento específico).
5. Processará todas as unidades definidas na lista `unidades` (você pode alterar essa lista no código, conforme sua necessidade).
6. Criará o arquivo `cards_adalove.csv` ao final, caso ele não exista.
7. Exibirá na tela o **tempo total de execução** do script.

---

## **Estrutura dos Arquivos**
A estrutura básica do projeto é:
```
.
├── .env                  # Armazena as credenciais (LOGIN e SENHA)
├── main.py               # Script principal contendo o código de extração
├── requirements.txt      # Todas as dependências necessárias
└── README.md             # Este arquivo de documentação
```

Caso você tenha organizado de outra forma, adeque as instruções para refletir a sua estrutura de pastas.

---

## **Funcionamento Geral do Script**

1. **Carrega variáveis de ambiente**:
   - Utiliza `load_dotenv()` para carregar `LOGIN` e `SENHA` do arquivo `.env`.

2. **Abre o navegador**:
   - A chamada `await p.chromium.launch(channel="chrome", headless=False)` permite abrir o Chrome em modo visual (não-headless).

3. **Faz o login**:
   - Preenche o campo "E-mail ou telefone" com o valor de `LOGIN`.
   - Clica no botão "Próxima".
   - Preenche o campo "Digite sua senha" com o valor de `SENHA`.
   - Clica novamente em "Próxima".
   - Verifica se um *elemento-chave* da página foi carregado.

4. **Processa as unidades**:
   - Para cada item da lista `unidades` (ex.: "Unidade 01", "Unidade 02", ...):
     - Abre uma nova aba no mesmo contexto.
     - Navega até a página de *academic-life*.
     - Clica no texto da unidade.
     - Localiza todos os *cards* (atributo `data-rbd-draggable-id`).
     - Para cada card, coleta título, tipo, professor, data, descrição, link e/ou se a atividade é ponderada.
     - Fecha a aba ao terminar.

5. **Salva no CSV**:
   - Cria ou sobrescreve o arquivo `cards_adalove.csv`.
   - Escreve o cabeçalho e as linhas com as informações coletadas.

6. **Preenche datas ausentes**:
   - Lê o CSV recém-criado.
   - Qualquer linha onde a coluna `Data_instrucao` seja "N/A" recebe a última data válida encontrada no arquivo.

7. **Finaliza**:
   - Fecha o navegador.
   - Imprime o tempo total de execução e a mensagem de conclusão.

---

## **Possíveis Erros e Soluções**

- **Erro de Timeout durante o Login**  
  Se sua conexão for lenta ou a página do Google demorar mais que o esperado para carregar, aumente o valor de `timeout` nos `await expect(...)` ou realize um `page.wait_for_timeout(...)` adicional antes.

- **Erro de Seletor não encontrado**  
  Verifique se o seletor utilizado ainda está válido. Mudanças na interface do AdaLove podem quebrar o script. Atualize a string do seletor para refletir a nova estrutura, caso o repositório esteja desatualizado.

- **Problemas com variáveis de ambiente**  
  Certifique-se de que o arquivo `.env` está presente na raiz do projeto e que seu conteúdo está formatado corretamente:
  ```env
  LOGIN=seu.email@exemplo.com
  SENHA=suaSenha
  ```
  Também confirme se o `.env` está sendo carregado antes de acessar `os.environ`.

- **Navegador não abre**  
  Depois de instalar as dependências com `pip install -r requirements.txt`, é crucial rodar `playwright install`. Caso contrário, o Playwright não terá os binários necessários.

---

## **Contato**
Em caso de dúvidas, sugestões ou problemas, entre em contato comigo:  
**E-mail**: [tony.sousa@sou.inteli.edu.br](mailto:tony.sousa@sou.inteli.edu.br)

---

<p align="center">
  <i>Obrigado por utilizar este projeto, fico feliz por ajudar outras pessoas! Fico à disposição para ajudar no que for preciso.</i>
</p>