#!/usr/bin/env python3
"""
AdaLove CLI - Interface Interativa Navegável para Extração e Consulta de Cards
"""

import sys
import asyncio
import json
import logging
import re
import questionary
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Add src directory to path for package imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from adalove_extractor.api import AdaLoveAPIClient
from adalove_extractor.api.endpoints import Endpoints
from adalove_extractor.api.exceptions import AuthenticationError
from adalove_extractor.config.settings import Settings
from adalove_extractor.extractors.turma_completa import extrair_turma_completa
from adalove_extractor.cli.icons import icons
from adalove_extractor.io.calendar import ICalendarExport

# Configure basic logging to file only to not mess up TUI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='adalove_cli.log',
    filemode='a'
)

console = Console()

OUTPUT_DIR = Path(__file__).parent / "output" / "api_extraction"

# Estilo global para menus questionary
MENU_STYLE = questionary.Style([
    ('qmark', 'fg:#E91E63 bold'),
    ('question', 'fg:#673AB7 bold'),
    ('answer', 'fg:#2196f3 bold'),
    ('pointer', 'fg:#E91E63 bold'),
    ('highlighted', 'fg:#E91E63 bold'),
    ('selected', 'fg:#2196f3'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#6C6C6C'),
])


# ═══════════════════════════════════════════════════════════════
# Utilidades
# ═══════════════════════════════════════════════════════════════

def show_banner():
    """Exibe o banner inicial."""
    title = Text(f"{icons.rocket}{icons.robot} ADALOVE EXTRACTOR by 0xftb", style="bold magenta")
    subtitle = Text("Ferramenta CLI para extração de cards e materiais", style="cyan")
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="magenta",
        expand=False
    )
    rprint(panel)


def is_turma_extraida(turma_nome: str) -> bool:
    """Verifica se uma turma já foi extraída."""
    return (OUTPUT_DIR / turma_nome / "extracao_completa.json").exists()


def limpar_html(html: str) -> str:
    """Remove tags HTML e decodifica entidades."""
    if not html:
        return ""
    # Converte tags de bloco em newlines antes de removê-las
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'</?(p|div|li|ul|ol|h[1-6])[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    # Decodifica entidades HTML comuns residuais
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    # Limpa whitespace
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)


def truncar_texto(texto: str, max_lines: int = 3, max_chars_per_line: int = 80) -> str:
    """Trunca texto a um número máximo de linhas."""
    if not texto:
        return "(vazio)"
    limpo = limpar_html(texto)
    lines = limpo.split('\n')[:max_lines]
    result = []
    for line in lines:
        if len(line) > max_chars_per_line:
            line = line[:max_chars_per_line - 3] + "..."
        result.append(line)
    if len(limpo.split('\n')) > max_lines:
        result[-1] = result[-1].rstrip('.') + "..."
    return '\n'.join(result)


def calcular_prazo_ponderada(data_encontro: str) -> datetime | None:
    """
    Calcula o prazo de entrega de uma ponderada.
    Regra: sexta-feira 23:59 da mesma semana do encontro.
    
    Args:
        data_encontro: Data do encontro no formato 'YYYY-MM-DD'
    
    Returns:
        datetime do prazo ou None se data inválida
    """
    if not data_encontro or data_encontro == "sem data":
        return None
    try:
        dt = datetime.strptime(data_encontro, "%Y-%m-%d")
        # weekday(): 0=segunda, 4=sexta
        dias_ate_sexta = 4 - dt.weekday()
        if dias_ate_sexta < 0:
            # Encontro é sábado/domingo → sexta da PRÓXIMA semana
            dias_ate_sexta += 7
        sexta = dt + timedelta(days=dias_ate_sexta)
        return sexta.replace(hour=23, minute=59, second=59)
    except ValueError:
        return None


def status_prazo(data_encontro: str, respondida: bool) -> tuple[str, str]:
    """
    Determina o status de prazo de uma ponderada.
    
    Returns:
        Tupla (icone, label) com o status
    """
    if respondida:
        return icons.success, "Entregue"
    
    prazo = calcular_prazo_ponderada(data_encontro)
    if not prazo:
        return icons.status_none, "Sem prazo"
    
    agora = datetime.now()
    diferenca = prazo - agora
    
    if diferenca.total_seconds() < 0:
        dias_atraso = abs(diferenca.days)
        if dias_atraso == 0:
            return icons.status_error, "Atrasada (hoje)"
        return icons.status_error, f"Atrasada ({dias_atraso}d)"
    elif diferenca.days == 0:
        return icons.status_warning, "Vence hoje!"
    elif diferenca.days == 1:
        return icons.status_warning, "Vence amanhã"
    else:
        return icons.status_ok, f"Prazo: {prazo.strftime('%d/%m')} ({diferenca.days}d)"


def carregar_extracao(turma_nome: str) -> dict | None:
    """Carrega o JSON de extração de uma turma."""
    filepath = OUTPUT_DIR / turma_nome / "extracao_completa.json"
    if not filepath.exists():
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extrair_ponderadas(data: dict) -> list[dict]:
    """
    Extrai todas as atividades ponderadas do JSON de extração,
    organizadas por semana com informações do encontro ancorado.
    """
    ponderadas = []

    for semana_key, semana_data in data.get("semanas", {}).items():
        if not isinstance(semana_data, dict):
            continue

        encontros = semana_data.get("encontros", {})
        for data_encontro, encontro in encontros.items():
            # Ponderadas do próprio encontro
            if encontro.get("is_ponderada") and "avaliacao" in encontro:
                ponderadas.append({
                    "semana": semana_key,
                    "data_encontro": data_encontro,
                    "encontro_titulo": encontro.get("titulo", ""),
                    "titulo": encontro.get("titulo", ""),
                    "professor": encontro.get("professor", ""),
                    "descricao": "",
                    "avaliacao": encontro.get("avaliacao", {}),
                    "tipo": "encontro",
                })

            # Ponderadas dos autoestudos ancorados neste encontro
            for auto_titulo, auto_data in encontro.get("autoestudos", {}).items():
                if auto_data.get("is_ponderada") and "avaliacao" in auto_data:
                    ponderadas.append({
                        "semana": semana_key,
                        "data_encontro": data_encontro,
                        "encontro_titulo": encontro.get("titulo", ""),
                        "titulo": auto_titulo,
                        "professor": auto_data.get("professor", ""),
                        "descricao": auto_data.get("descricao", ""),
                        "avaliacao": auto_data.get("avaliacao", {}),
                        "tipo": "autoestudo",
                    })

        # Ponderadas sem âncora
        for card in semana_data.get("sem_ancora", []):
            if card.get("is_ponderada") and "avaliacao" in card:
                ponderadas.append({
                    "semana": semana_key,
                    "data_encontro": "sem data",
                    "encontro_titulo": "(sem âncora)",
                    "titulo": card.get("titulo", ""),
                    "professor": card.get("professor", ""),
                    "descricao": card.get("descricao", ""),
                    "avaliacao": card.get("avaliacao", {}),
                    "tipo": "sem_ancora",
                })

    return ponderadas


async def atualizar_status_ponderadas(client: AdaLoveAPIClient, turma_nome: str, turma_uuid: str) -> bool:
    """
    Atualiza status das ponderadas (resposta, avaliação) sem refazer extração completa.
    Busca apenas userdata e atualiza os campos de avaliação no JSON existente.
    
    Returns:
        True se atualização bem-sucedida, False caso contrário
    """
    filepath = OUTPUT_DIR / turma_nome / "extracao_completa.json"
    if not filepath.exists():
        return False
    
    try:
        # Buscar userdata atual
        from adalove_extractor.api.endpoints import Endpoints
        userdata = await client.get(Endpoints.section_userdata(turma_uuid))
        activities = userdata.get("activities", [])
        
        # Mapear por studentActivityUuid
        activity_map = {}
        for act in activities:
            uuid = act.get("studentActivityUuid")
            if uuid:
                activity_map[uuid] = act
        
        # Carregar JSON existente
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Função helper para atualizar avaliacao de um card
        def atualizar_avaliacao(card_or_autoestudo: dict):
            uuid = card_or_autoestudo.get("student_activity_uuid")
            if not uuid or uuid not in activity_map:
                return
            
            act = activity_map[uuid]
            if not card_or_autoestudo.get("is_ponderada"):
                return
            
            # Atualizar campos de avaliação
            study_question = act.get("studyQuestion", "") or ""
            study_answer = act.get("studyAnswer", "") or ""
            grade_result_raw = act.get("gradeResult", "-1.0")
            
            try:
                grade_result = float(grade_result_raw)
            except (ValueError, TypeError):
                grade_result = -1.0
            
            from adalove_extractor.utils.text import decode_html_entities
            
            card_or_autoestudo["avaliacao"] = {
                "peso": act.get("gradeWeight", 0) or 0,
                "pergunta": decode_html_entities(study_question),
                "resposta": decode_html_entities(study_answer) if study_answer else None,
                "respondida": bool(study_answer.strip()),
                "nota": grade_result if grade_result >= 0 else None,
                "avaliada": act.get("evaluated", 0) == 1,
                "bloqueada": act.get("blocked", 0) == 1,
            }
        
        # Percorrer estrutura e atualizar
        updated_count = 0
        for semana_key, semana_data in data.get("semanas", {}).items():
            if not isinstance(semana_data, dict):
                continue
            
            for data_key, encontro in semana_data.get("encontros", {}).items():
                # Encontros ponderados
                if encontro.get("is_ponderada"):
                    atualizar_avaliacao(encontro)
                    updated_count += 1
                
                # Autoestudos
                for auto_titulo, auto_data in encontro.get("autoestudos", {}).items():
                    if auto_data.get("is_ponderada"):
                        atualizar_avaliacao(auto_data)
                        updated_count += 1
            
            # Sem âncora
            for card in semana_data.get("sem_ancora", []):
                if card.get("is_ponderada"):
                    atualizar_avaliacao(card)
                    updated_count += 1
        
        # Salvar JSON atualizado
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Erro ao atualizar status ponderadas: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# Menus
# ═══════════════════════════════════════════════════════════════

async def menu_principal(client: AdaLoveAPIClient, sections_list: list):
    """
    Menu principal: lista de turmas com status de extração.
    Loop até o usuário sair.
    """
    while True:
        # Ordena por nome (descendente = mais recente primeiro)
        sorted_sections = sorted(
            sections_list,
            key=lambda x: x.get('caption', x.get('name', 'zzz')),
            reverse=True
        )

        choices = []
        for section in sorted_sections:
            name = section.get('caption', section.get('name', 'N/A'))
            extraida = is_turma_extraida(name)
            icon = icons.check if extraida else icons.folder
            choices.append(questionary.Choice(
                title=f"{icon} {name}",
                value=name
            ))

        choices.append(questionary.Separator())
        choices.append(questionary.Choice(title=f"{icons.exit} Sair", value="__EXIT__"))

        selected = await questionary.select(
            "Selecione uma turma:",
            choices=choices,
            style=MENU_STYLE,
            instruction="(Use ↑↓ para navegar, Enter para selecionar)"
        ).ask_async()

        if not selected or selected == "__EXIT__":
            rprint("[yellow]Até logo! 👋[/yellow]")
            return

        # Encontrar UUID da turma
        turma_uuid = None
        for section in sections_list:
            if section.get('caption', section.get('name')) == selected:
                turma_uuid = section.get('uuid')
                break

        await menu_turma(client, selected, turma_uuid)


async def menu_turma(client: AdaLoveAPIClient, turma_nome: str, turma_uuid: str):
    """
    Sub-menu de uma turma: opções de ação.
    """
    while True:
        extraida = is_turma_extraida(turma_nome)
        status = f"[green]{icons.check} Já extraída[/green]" if extraida else f"[dim]{icons.uncheck} Não extraída[/dim]"
        rprint(f"\n[bold]{icons.clipboard} Turma:[/bold] {turma_nome}  {status}")

        choices = [
            questionary.Choice(title=f"{icons.download} Extrair cards", value="extrair"),
        ]

        if extraida:
            choices.append(
                questionary.Choice(title=f"{icons.view} Ver atividades ponderadas", value="ponderadas")
            )
            # Add Exportar Calendário here
            choices.append(
                questionary.Choice(title=f"{icons.calendar} Exportar Calendário (.ics)", value="calendario")
            )

        choices.append(questionary.Separator())
        choices.append(questionary.Choice(title=f"{icons.back} Voltar", value="__BACK__"))

        selected = await questionary.select(
            "O que deseja fazer?",
            choices=choices,
            style=MENU_STYLE,
        ).ask_async()

        if not selected or selected == "__BACK__":
            return

        if selected == "extrair":
            await executar_extracao(turma_nome)

        elif selected == "ponderadas":
            await ver_ponderadas(client, turma_nome, turma_uuid)
            
        elif selected == "calendario":
            await exportar_calendario(turma_nome)


async def executar_extracao(turma_nome: str):
    """Executa extração, com aviso se já existir."""
    if is_turma_extraida(turma_nome):
        rprint(Panel(
            f"[yellow]{icons.warning} Esta turma já foi extraída anteriormente.[/yellow]\n"
            "A extração existente será substituída.",
            title="Aviso",
            border_style="yellow"
        ))
        confirmar = await questionary.confirm(
            "Deseja extrair novamente e sobrescrever?",
            default=False
        ).ask_async()
        if not confirmar:
            rprint("[dim]Extração cancelada.[/dim]")
            return
    else:
        confirmar = await questionary.confirm(
            f"Confirmar extração da turma {turma_nome}?"
        ).ask_async()
        if not confirmar:
            rprint("[dim]Extração cancelada.[/dim]")
            return

    console.print(f"\n[bold green]{icons.rocket} Iniciando extração de: {turma_nome}[/bold green]")
    console.print("[dim]Acompanhe o log detalhado em: adalove_cli.log[/dim]")

    result_dir = await extrair_turma_completa(turma_nome)

    if result_dir:
        rprint(Panel(
            f"[bold green]{icons.success} Sucesso![/bold green]\n\n"
            f"Cards salvos em:\n[blue]{result_dir}[/blue]",
            title="Extração Concluída"
        ))
        if sys.platform == "darwin":
            abrir = await questionary.confirm("Abrir pasta dos arquivos?").ask_async()
            if abrir:
                import subprocess
                subprocess.run(["open", str(result_dir)])
    else:
        rprint(f"[bold red]{icons.error} Falha na extração. Verifique adalove_cli.log[/bold red]")


async def exportar_calendario(turma_nome: str):
    """Exporta os encontros da extração para formato .ics."""
    data = carregar_extracao(turma_nome)
    if not data:
        rprint(f"[red]{icons.error} Dados de extração não encontrados para a turma {turma_nome}.[/red]")
        return
        
    output_path = OUTPUT_DIR / turma_nome / f"{turma_nome.replace(' ', '_')}_calendario.ics"
    
    # Perguntar sobre o horário de início (padrão assumido: 10:00)
    horario_padrao = await questionary.text(
        "Qual o horário de início que os encontros dessa turma começam? (ex: 10:00 ou 14:00)",
        default="10:00"
    ).ask_async()

    if not horario_padrao:
        return
        
    # Perguntar sobre a duração dos encontros (padrão assumido: 2 horas)
    duracao_str = await questionary.text(
        "Qual a duração dos encontros em horas?",
        default="2"
    ).ask_async()
    
    if not duracao_str:
        return
        
    try:
        duracao_padrao = int(duracao_str)
    except ValueError:
        duracao_padrao = 2

    with console.status("[bold cyan]Gerando arquivo de calendário...[/bold cyan]", spinner="dots"):
        exporter = ICalendarExport(horario_padrao=horario_padrao, duracao_padrao=duracao_padrao)
        sucesso = exporter.gerar_calendario(data, output_path)
        
    if sucesso:
        rprint(Panel(
            f"[bold green]{icons.success} Calendário gerado com sucesso![/bold green]\n\n"
            f"Arquivo salvo em:\n[blue]{output_path}[/blue]",
            title="Exportação Concluída"
        ))
        if sys.platform == "darwin":
            abrir = await questionary.confirm("Abrir pasta do arquivo?").ask_async()
            if abrir:
                import subprocess
                subprocess.run(["open", "-R", str(output_path)])
    else:
        rprint(f"[bold yellow]{icons.warning} Não foi possível gerar o calendário (sem dados ou erro).[/bold yellow]")


async def ver_ponderadas(client: AdaLoveAPIClient, turma_nome: str, turma_uuid: str):
    """
    Viewer de atividades ponderadas: lista agrupada por semana,
    com preview de descrição e pergunta.
    Atualiza status antes de exibir.
    """
    # Atualizar status das ponderadas
    with console.status("[bold cyan]Atualizando status das ponderadas...[/bold cyan]", spinner="dots"):
        sucesso = await atualizar_status_ponderadas(client, turma_nome, turma_uuid)
        if not sucesso:
            rprint(f"[yellow]{icons.warning} Não foi possível atualizar status. Mostrando dados do cache.[/yellow]")
    
    data = carregar_extracao(turma_nome)
    if not data:
        rprint(f"[red]{icons.error} Dados de extração não encontrados.[/red]")
        return

    ponderadas = extrair_ponderadas(data)

    if not ponderadas:
        rprint("[yellow]Nenhuma atividade ponderada encontrada nesta turma.[/yellow]")
        return

    while True:
        rprint(f"\n[bold]📝 Atividades Ponderadas — {turma_nome}[/bold]")
        rprint(f"[dim]Total: {len(ponderadas)} atividades[/dim]\n")

        choices = []
        semana_atual = ""

        for i, pond in enumerate(ponderadas):
            # Separador por semana (com espaçamento)
            if pond["semana"] != semana_atual:
                semana_atual = pond["semana"]
                if i > 0:
                    choices.append(questionary.Separator(" "))
                choices.append(questionary.Separator(
                    f"━━━━━━━━━━ {icons.calendar} {semana_atual} ━━━━━━━━━━"
                ))
                choices.append(questionary.Separator(" "))

            # Montar label do item
            aval = pond.get("avaliacao", {})
            peso = aval.get("peso", "?")
            is_respondida = aval.get("respondida", False)
            tem_conteudo = aval.get("resposta") is not None

            # Indicadores de status
            ico_resp = icons.file_edit if tem_conteudo else icons.file_empty
            ico_entrega = icons.check if is_respondida else icons.uncheck
            ico_prazo, lbl_prazo = status_prazo(pond["data_encontro"], is_respondida)

            desc_preview = truncar_texto(pond.get("descricao", ""), max_lines=1, max_chars_per_line=60)
            perg_preview = truncar_texto(aval.get("pergunta", ""), max_lines=1, max_chars_per_line=60)

            titulo_curto = pond["titulo"]
            if len(titulo_curto) > 50:
                titulo_curto = titulo_curto[:47] + "..."

            line1 = f"{ico_entrega} {ico_resp} {titulo_curto}"
            prof = pond.get('professor') or '?'
            line2 = f"   {icons.calendar} {pond['data_encontro']} · {icons.teacher} {prof[:25]} · {icons.weight} Peso {peso}"
            line3 = f"   {ico_prazo} {lbl_prazo} · {icons.document} {desc_preview}"
            line4 = f"   {icons.question} {perg_preview}"

            label = f"{line1}\n{line2}\n{line3}\n{line4}"

            choices.append(questionary.Choice(
                title=label,
                value=i
            ))

            # Espaçamento entre ponderadas
            if i < len(ponderadas) - 1:
                choices.append(questionary.Separator(" "))

        choices.append(questionary.Separator())
        choices.append(questionary.Choice(title=f"{icons.back} Voltar", value="__BACK__"))

        selected = await questionary.select(
            "Navegue pelas ponderadas (↑↓) ou selecione para ver detalhes:",
            choices=choices,
            style=MENU_STYLE,
        ).ask_async()

        if selected is None or selected == "__BACK__":
            return

        if isinstance(selected, int):
            await menu_ponderada(ponderadas[selected])


async def menu_ponderada(pond: dict):
    """
    Sub-menu de uma atividade ponderada individual.
    Mostra detalhes completos e opções futuras.
    """
    while True:
        aval = pond.get("avaliacao", {})

        # Header
        rprint(Panel(
            f"[bold]{pond['titulo']}[/bold]\n"
            f"[dim]{pond['semana']} · {pond['data_encontro']}[/dim]\n"
            f"[dim]Encontro: {pond['encontro_titulo']}[/dim]",
            border_style="magenta",
            expand=False
        ))

        # Detalhes
        rprint(f"  👨‍🏫 [bold]Professor:[/bold] {pond.get('professor', 'N/A')}")
        rprint(f"  ⚖️  [bold]Peso:[/bold] {aval.get('peso', '?')}")
        rprint(f"  📊 [bold]Status:[/bold] {'✅ Respondida' if aval.get('respondida') else '⬜ Não respondida'}")

        nota = aval.get('nota')
        if nota is not None:
            rprint(f"  📝 [bold]Nota:[/bold] {nota}")
        else:
            rprint(f"  📝 [bold]Nota:[/bold] [dim]não avaliada[/dim]")

        rprint(f"  🔒 [bold]Bloqueada:[/bold] {'Sim' if aval.get('bloqueada') else 'Não'}")

        # Descrição completa
        desc = limpar_html(pond.get("descricao", ""))
        if desc:
            rprint(f"\n  [bold]📄 Descrição:[/bold]")
            for line in desc.split('\n'):
                rprint(f"     {line}")

        # Pergunta completa
        pergunta = limpar_html(aval.get("pergunta", ""))
        if pergunta:
            rprint(f"\n  [bold]❓ Pergunta da Avaliação:[/bold]")
            for line in pergunta.split('\n'):
                rprint(f"     {line}")

        # Resposta se existir
        resposta = aval.get("resposta")
        if resposta:
            rprint(f"\n  [bold]💬 Resposta submetida:[/bold]")
            resp_limpa = limpar_html(resposta)
            for line in resp_limpa.split('\n'):
                rprint(f"     {line}")

        rprint("")

        # Menu de opções
        choices = [
            questionary.Separator(),
            questionary.Choice(title=f"{icons.back} Voltar", value="__BACK__"),
        ]

        selected = await questionary.select(
            "Opções:",
            choices=choices,
            style=MENU_STYLE,
        ).ask_async()

        if not selected or selected == "__BACK__":
            return


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

async def main():
    show_banner()

    settings = Settings()
    if not settings.login or not settings.senha:
        rprint("[bold red]❌ Erro:[/bold red] Credenciais não encontradas no arquivo .env")
        if questionary.confirm("Deseja criar um arquivo .env agora?").ask():
            email = questionary.text("Email do Inteli:").ask()
            senha = questionary.password("Senha:").ask()
            with open(".env", "w") as f:
                f.write(f"LOGIN={email}\nSENHA={senha}\n")
            rprint("[green]✅ Arquivo .env criado com sucesso![/green]")
            settings = Settings()
        else:
            sys.exit(1)

    console.print(f"[dim]Usando conta: {settings.login}[/dim]")

    async with AdaLoveAPIClient() as client:
        try:
            with console.status("[bold green]Autenticando e buscando turmas...[/bold green]", spinner="dots"):
                await client.authenticate(settings.login, settings.senha)

                try:
                    sections_resp = await client.get(Endpoints.SECTIONS)
                except AuthenticationError:
                    rprint("[yellow]⚠️ Token expirado. Renovando autenticação...[/yellow]")
                    client.auth.token = None
                    await client.authenticate(settings.login, settings.senha)
                    sections_resp = await client.get(Endpoints.SECTIONS)

            # Extract list
            sections_list = []
            if isinstance(sections_resp, dict):
                sections_list = sections_resp.get("sections", [])
            elif isinstance(sections_resp, list):
                sections_list = sections_resp

            if not sections_list:
                rprint("[bold red]❌ Nenhuma turma encontrada![/bold red]")
                return

            # Entrar no menu principal (loop)
            await menu_principal(client, sections_list)

        except Exception as e:
            console.print_exception()
            rprint(f"[bold red]❌ Erro fatal:[/bold red] {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        rprint("\n[yellow]Interrompido pelo usuário[/yellow]")
