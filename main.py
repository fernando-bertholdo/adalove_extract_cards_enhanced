import asyncio
import csv
import time
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Substitua aqui as credenciais
LOGIN = os.environ.get("LOGIN")
SENHA = os.environ.get("SENHA")

async def processar_unidade(context, unidade_nome, rows):
    """
    Processa uma unidade específica em uma aba separada dentro de um mesmo contexto de navegador.

    Parâmetros:
        context (playwright.async_api.BrowserContext):
            Contexto de navegador onde a página será aberta.
        unidade_nome (str):
            Nome da unidade (ex.: "Unidade 01", "Unidade 02").
        rows (list):
            Lista onde serão armazenados os dados coletados sobre os cards.

    Retorna:
        None
    """

    # Cria uma nova página para a unidade atual
    page = await context.new_page()
    print(f"Processando {unidade_nome}...")

    # Acessa a página geral de "academic-life" e clica na unidade desejada
    await page.goto("https://adalove.inteli.edu.br/academic-life")
    await page.get_by_text(unidade_nome).click()

    # Localiza todos os cards na unidade pelo seletor "data-rbd-draggable-id"
    cards = await page.query_selector_all('[data-rbd-draggable-id]')
    print(f"Total de cards encontrados na {unidade_nome}: {len(cards)}")

    # Loop pelos cards encontrados
    for i, card in enumerate(cards):
        print(f"Processando card {i + 1} na {unidade_nome}...")

        # Clica no card para abrir seu conteúdo
        await card.click()
        await expect(page.locator('.MuiTypography-bodyLarge.title-name-activity')).to_be_visible()

        # Captura o título do card
        titulo_card = await page.query_selector('.MuiTypography-bodyLarge.title-name-activity')
        titulo = await titulo_card.text_content() if titulo_card else "N/A"

        # Captura o tipo do card
        tipo_card = await page.query_selector('.title-type-activity span')
        tipo = await tipo_card.text_content() if tipo_card else "N/A"

        # Captura o professor (se não for atividade de Projeto ou Orientação)
        if tipo not in ["Desenvolvimento de Projeto", "Encontro de Orientação"]:
            professor_card = await page.query_selector('(//span[contains(@class, "MuiTypography-root MuiTypography-body3 css-je8uwo")])[last()]')
            professor = await professor_card.text_content() if professor_card else "N/A"
        else:
            professor = "N/A"

        # Captura a data (somente se for Encontro de Instrução ou Orientação)
        if tipo in ["Encontro de Instrução", "Encontro de Orientação"]:
            data_card = await page.query_selector(
                '.general-information-activity > .general-information-activity-row:first-child > .information-activity:first-child span'
            )
            data_completa = await data_card.text_content() if data_card else "N/A"
            data = data_completa.split(" - ")[0] if data_completa != "N/A" else "N/A"
        else:
            data = "N/A"

        # Captura a descrição
        # Tenta localizar e clicar no botão "Ver mais" (caso exista) antes de capturar a descrição completa
        if await page.query_selector('button:has-text("Ver mais")'):
            await page.locator('button:has-text("Ver mais")').click()

        descricao_elemento = await page.query_selector('.content-description-text')
        descricao = await descricao_elemento.text_content() if descricao_elemento else "N/A"

        # Captura o link (se não for atividade de Projeto ou Orientação)
        if tipo not in ["Desenvolvimento de Projeto", "Encontro de Orientação"]:
            link_elemento = await page.query_selector('.content-related-content-list a')
            link = await link_elemento.get_attribute('href') if link_elemento else "N/A"
        else:
            link = "N/A"

        # Verifica se é uma atividade ponderada
        modal = await page.query_selector('section.sc-kAyceB.liGrJT')
        ponderada = await modal.query_selector('p:has-text("Atividade ponderada")') is not None
        if ponderada:
            tipo = "Ponderada"
            await page.locator('button:has-text("Avaliação")').click()
            pergunta_ponderada_card = await page.query_selector('.assessment-question-content > p')
            pergunta_ponderada = await pergunta_ponderada_card.text_content() if pergunta_ponderada_card else "N/A"
        else:
            pergunta_ponderada = "N/A"

        # Adiciona os dados coletados à lista de linhas
        rows.append({
            "Semana": unidade_nome,
            "Titulo": titulo,
            "Data_instrucao": data,
            "Tipo": tipo,
            "Professor": professor,
            "Descricao": descricao,
            "Link": link,
            "Pergunta_ponderada": pergunta_ponderada
        })

        # Fecha o modal atual para processar o próximo card
        await page.locator('button[label="Fechar"]').click()
        # Pequena espera para garantir que o modal foi fechado
        await asyncio.sleep(0.5)

    # Fecha a aba da unidade após processar todos os cards
    await page.close()

def preencher_datas(csv_file):
    """
    Lê um arquivo CSV e preenche as datas ausentes com base na última data válida encontrada.

    Parâmetros:
        csv_file (str):
            Caminho do arquivo CSV que será lido e atualizado.

    Retorna:
        None
    """

    with open(csv_file, mode="r", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        ultima_data = "N/A"

        # Atualiza as linhas com base na última data válida
        for row in reader:
            if row["Data_instrucao"] == "N/A":
                row["Data_instrucao"] = ultima_data
            else:
                ultima_data = row["Data_instrucao"]

    # Reescreve o CSV com as datas atualizadas
    with open(csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Semana", "Titulo", "Data_instrucao", "Tipo", "Professor", "Descricao", "Link", "Pergunta_ponderada"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

async def main():
    """
    Função principal que:
      1. Inicia o navegador e realiza login no ambiente 'adalove'.
      2. Processa unidades específicas em paralelo (ex.: "Unidade 01", "Unidade 02").
      3. Grava as informações dos cards em um arquivo CSV.
      4. Preenche datas ausentes no CSV.
      5. Fecha o navegador.

    Retorna:
        None
    """

    # Inicia o timer
    start_time = time.time()

    async with async_playwright() as p:
        # Lança o navegador (canal "chrome", headless=False para visualização)
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()

        # Abre uma nova página para efetuar o login
        page = await context.new_page()
        await page.goto("https://adalove.inteli.edu.br/")
        await page.get_by_role("button", name="Entrar com o Google").click()

        # Preenche as credenciais
        await expect(page.get_by_label("E-mail ou telefone")).to_be_visible()
        await page.get_by_label("E-mail ou telefone").click()
        await page.get_by_label("E-mail ou telefone").fill(LOGIN)
        await expect(page.get_by_role("button", name="Próxima")).to_be_visible()
        await page.get_by_role("button", name="Próxima").click()

        # Preenche a senha
        await expect(page.get_by_label("Digite sua senha")).to_be_visible(timeout=15000)
        await page.get_by_label("Digite sua senha").click()
        await page.get_by_label("Digite sua senha").fill(SENHA)  # Substituir caso tenha credenciais seguras
        await expect(page.get_by_role("button", name="Próxima")).to_be_visible()
        await page.get_by_role("button", name="Próxima").click()

        # Aguarda o login concluir (verifica se um elemento-chave aparece)
        await expect(page.get_by_label("bb1a35a8df2349ef87bb47fece39a062")).to_be_visible(timeout=15000)

        # Lista das unidades que se deseja processar
        unidades = ["Unidade 01", "Unidade 02", "Unidade 03", "Unidade 04", "Unidade 05", "Unidade 06", "Unidade 07", "Unidade 08", "Unidade 09", "Unidade 10"]

        # Lista onde serão armazenados os dados coletados
        rows = []

        # Cria tarefas para processar as unidades em paralelo
        tarefas = [processar_unidade(context, unidade, rows) for unidade in unidades]
        await asyncio.gather(*tarefas)

        # Ordena as linhas pela coluna "Semana" (ex.: Unidade 01, Unidade 02, etc.)
        rows.sort(key=lambda row: row["Semana"])

        # Nome do arquivo CSV de saída
        csv_file = "cards_adalove.csv"

        # Grava os dados ordenados no CSV
        with open(csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Semana", "Titulo", "Data_instrucao", "Tipo", "Professor", "Descricao", "Link", "Pergunta_ponderada"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # Preenche as datas ausentes no CSV
        preencher_datas(csv_file)

        # Fecha o contexto e o navegador
        await context.close()
        await browser.close()

    # Calcula o tempo de execução total
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Exibe mensagem final com o tempo de execução
    print(f"Processamento concluído em {elapsed_time:.2f} segundos. "
          f"Dados salvos e ordenados em '{csv_file}'.")
    

# Executa o script principal
asyncio.run(main())
