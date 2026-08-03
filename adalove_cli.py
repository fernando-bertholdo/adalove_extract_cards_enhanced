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
from adalove_extractor.ai.context_builder import ContextBuilder
from adalove_extractor.ai.system_prompt import SystemPromptLoader
from adalove_extractor.ai.answer_generator import AnswerGenerator, ClaudeNotFoundError

# Configure basic logging to file only to not mess up TUI
# No Windows o console e os arquivos usam a codepage local (cp1252 em pt-BR).
# Como as mensagens de status e de log contêm emojis, isso gera
# UnicodeEncodeError — silencioso no logging (a mensagem some) e fatal nos
# prints quando a saída é redirecionada. Forçar UTF-8 resolve ambos.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # stream substituído ou não reconfigurável
        pass

# force=True porque basicConfig é no-op se o root logger já tiver handler:
# basta um módulo importado acima configurar logging para esta chamada ser
# ignorada e os logs vazarem para o terminal, por cima da TUI.
# encoding='utf-8' é obrigatório: sem ele o FileHandler usa o locale do sistema
# e 75 das 109 mensagens de log (as que têm emoji) falham no Windows.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='adalove_cli.log',
    filemode='a',
    encoding='utf-8',
    force=True
)

console = Console()

OUTPUT_DIR = Path(__file__).parent / "output" / "api_extraction"
RASCUNHOS_SUBDIR = "rascunhos"

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


def _turma_slug(turma_nome: str) -> str:
    """Normaliza o nome da turma para o nome da pasta no disco.

    `extrair_turma_completa` salva o diretório como `nome.replace(" ", "_")` —
    ex.: "Trilha de ensino..." vira `Trilha_de_ensino_...`. Toda construção de
    caminho dentro de `output/` deve usar este slug, ou turmas com espaço no
    nome ficam invisíveis (falso negativo em `is_turma_extraida`).
    """
    return turma_nome.replace(" ", "_")


def _turma_dir(turma_nome: str) -> Path:
    """Diretório da turma no disco, com normalização correta do nome."""
    return OUTPUT_DIR / _turma_slug(turma_nome)


def is_turma_extraida(turma_nome: str) -> bool:
    """Verifica se uma turma já foi extraída."""
    return (_turma_dir(turma_nome) / "extracao_completa.json").exists()


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
    filepath = _turma_dir(turma_nome) / "extracao_completa.json"
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
                    "student_activity_uuid": encontro.get("student_activity_uuid"),
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
                        "student_activity_uuid": auto_data.get("student_activity_uuid"),
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
                    "student_activity_uuid": card.get("student_activity_uuid"),
                })

    return ponderadas


async def atualizar_status_ponderadas(client: AdaLoveAPIClient, turma_nome: str, turma_uuid: str) -> bool:
    """
    Atualiza status das ponderadas (resposta, avaliação) sem refazer extração completa.
    Busca apenas userdata e atualiza os campos de avaliação no JSON existente.
    
    Returns:
        True se atualização bem-sucedida, False caso contrário
    """
    filepath = _turma_dir(turma_nome) / "extracao_completa.json"
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
        
    output_path = _turma_dir(turma_nome) / f"{_turma_slug(turma_nome)}_calendario.ics"
    
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
            await menu_ponderada(ponderadas[selected], client, turma_nome, data)


def salvar_rascunho(turma_nome: str, pond: dict, resposta: str) -> Path:
    """Salva rascunho de resposta gerado por IA em arquivo markdown."""
    from datetime import date

    rascunhos_dir = _turma_dir(turma_nome) / RASCUNHOS_SUBDIR
    rascunhos_dir.mkdir(parents=True, exist_ok=True)

    titulo_slug = re.sub(r"[^\w\s-]", "", pond["titulo"])[:40].strip().replace(" ", "_")
    filename = f"{date.today().isoformat()}_{titulo_slug}.md"
    filepath = rascunhos_dir / filename

    uuid = pond.get("student_activity_uuid", "desconhecido")
    aval = pond.get("avaliacao", {})
    conteudo = (
        f"---\n"
        f"ponderada: {pond['titulo']}\n"
        f"semana: {pond['semana']}\n"
        f"data: {pond['data_encontro']}\n"
        f"student_activity_uuid: {uuid}\n"
        f"peso: {aval.get('peso', '?')}\n"
        f"---\n\n"
        f"## Pergunta\n\n{aval.get('pergunta', '')}\n\n"
        f"## Resposta Gerada\n\n{resposta}\n"
    )
    filepath.write_text(conteudo, encoding="utf-8")
    return filepath


async def gerar_resposta_ia(
    client: AdaLoveAPIClient,
    turma_nome: str,
    pond: dict,
    extracao_data: dict,
):
    """Fluxo completo de geração de resposta com IA para uma ponderada."""
    import os
    import subprocess as sp

    context_builder = ContextBuilder()
    prompt_loader = SystemPromptLoader()
    generator = AnswerGenerator()

    # Passo 1: Exibir contexto disponível
    aval = pond.get("avaliacao", {})
    rprint(Panel(
        f"[bold]{pond['titulo']}[/bold]\n"
        f"[dim]{pond['semana']} · {pond['data_encontro']}[/dim]\n\n"
        f"[bold cyan]Pergunta:[/bold cyan]\n{aval.get('pergunta', '')}",
        title="Contexto da Ponderada",
        border_style="cyan",
    ))

    # Passo 2: Transcrição (opcional)
    transcript_path = await questionary.text(
        f"{icons.folder} Caminho para arquivo .txt de transcrição (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()

    transcript = None
    if transcript_path and transcript_path.strip():
        try:
            transcript = Path(transcript_path.strip()).read_text(encoding="utf-8")
            rprint(f"[green]{icons.success} Transcrição carregada ({len(transcript)} chars)[/green]")
        except Exception as e:
            rprint(f"[yellow]{icons.warning} Não foi possível ler o arquivo: {e}[/yellow]")

    # Passo 3: Notas do usuário (opcional)
    user_notes_raw = await questionary.text(
        f"{icons.document} Instruções extras ou notas (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()
    user_notes = user_notes_raw.strip() if user_notes_raw else None

    # Passo 4: System prompt
    rprint(f"\n[dim]System prompt padrão carregado de config/default_system_prompt.md[/dim]")
    sp_additions_raw = await questionary.text(
        f"{icons.robot} Adicionar instruções ao system prompt desta geração (Enter para pular):",
        default="",
        style=MENU_STYLE,
    ).ask_async()
    sp_additions = sp_additions_raw.strip() if sp_additions_raw else None
    system_prompt = prompt_loader.load(session_additions=sp_additions)

    # Passo 5a: Gerar esqueleto
    with console.status("[bold cyan]Gerando esqueleto da resposta...[/bold cyan]", spinner="dots"):
        skeleton_prompt = context_builder.build(
            pond, extracao_data,
            transcript=transcript,
            user_notes=user_notes,
            skeleton_mode=True,
        )
        try:
            skeleton = generator.generate(user_prompt=skeleton_prompt, system_prompt=system_prompt)
        except ClaudeNotFoundError:
            rprint(
                f"[bold red]{icons.error} claude CLI não encontrado.[/bold red]\n"
                "Instale com: npm install -g @anthropic-ai/claude-code"
            )
            return
        except RuntimeError as e:
            rprint(f"[bold red]{icons.error} Erro ao gerar esqueleto:[/bold red] {e}")
            return

    # Passo 5b: Exibir esqueleto
    rprint(Panel(skeleton, title="Esqueleto da Resposta", border_style="yellow"))

    # Passo 5c: Aprovação do esqueleto
    esqueleto_ok = await questionary.select(
        "O esqueleto está correto?",
        choices=[
            questionary.Choice(title=f"{icons.success} Correto — gerar resposta completa", value="ok"),
            questionary.Choice(title=f"{icons.document} Ajustar com instrução adicional", value="ajustar"),
            questionary.Choice(title=f"{icons.exit} Cancelar", value="cancelar"),
        ],
        style=MENU_STYLE,
    ).ask_async()

    if not esqueleto_ok or esqueleto_ok == "cancelar":
        rprint("[dim]Geração cancelada.[/dim]")
        return

    if esqueleto_ok == "ajustar":
        ajuste = await questionary.text(
            "Instrução adicional para corrigir o esqueleto:",
            style=MENU_STYLE,
        ).ask_async()
        if ajuste and ajuste.strip():
            user_notes = (user_notes or "") + f"\n\nCORREÇÃO DE ESQUELETO: {ajuste.strip()}"

    # Passo 6: Gerar resposta completa
    with console.status("[bold cyan]Gerando resposta completa...[/bold cyan]", spinner="dots"):
        full_prompt = context_builder.build(
            pond, extracao_data,
            transcript=transcript,
            user_notes=user_notes,
            skeleton_mode=False,
        )
        try:
            resposta = generator.generate(user_prompt=full_prompt, system_prompt=system_prompt)
        except RuntimeError as e:
            rprint(f"[bold red]{icons.error} Erro ao gerar resposta:[/bold red] {e}")
            return

    # Passo 7: Exibir rascunho
    rprint(Panel(resposta, title="Rascunho Gerado", border_style="green"))

    # Passo 8: Menu de ação
    uuid = pond.get("student_activity_uuid")
    while True:
        acao = await questionary.select(
            "O que deseja fazer com a resposta?",
            choices=[
                questionary.Choice(title=f"{icons.success} Submeter via API AdaLove", value="submeter"),
                questionary.Choice(title=f"{icons.document} Abrir no editor ($EDITOR) e submeter", value="editor"),
                questionary.Choice(title=f"{icons.download} Regenerar com nota adicional", value="regenerar"),
                questionary.Choice(title=f"{icons.folder} Salvar rascunho (sem submeter)", value="salvar"),
                questionary.Choice(title=f"{icons.exit} Cancelar", value="cancelar"),
            ],
            style=MENU_STYLE,
        ).ask_async()

        if not acao or acao == "cancelar":
            rprint("[dim]Operação cancelada.[/dim]")
            return

        if acao == "salvar":
            filepath = salvar_rascunho(turma_nome, pond, resposta)
            rprint(f"[green]{icons.success} Rascunho salvo em: [blue]{filepath}[/blue][/green]")
            return

        if acao == "editor":
            import tempfile
            editor = os.environ.get("EDITOR", "nano")
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(resposta)
                tmp_path = f.name
            sp.run([editor, tmp_path])
            resposta = Path(tmp_path).read_text(encoding="utf-8")
            Path(tmp_path).unlink(missing_ok=True)
            rprint(Panel(resposta, title="Resposta Editada", border_style="blue"))
            continuar = await questionary.confirm(
                "Submeter esta versão editada via API?"
            ).ask_async()
            if not continuar:
                continue
            acao = "submeter"

        if acao == "regenerar":
            nota_extra = await questionary.text(
                "Instrução adicional para regenerar:",
                style=MENU_STYLE,
            ).ask_async()
            if nota_extra and nota_extra.strip():
                user_notes = (user_notes or "") + f"\n\nREGENERAÇÃO: {nota_extra.strip()}"
            with console.status("[bold cyan]Regenerando...[/bold cyan]", spinner="dots"):
                full_prompt = context_builder.build(
                    pond, extracao_data,
                    transcript=transcript,
                    user_notes=user_notes,
                    skeleton_mode=False,
                )
                resposta = generator.generate(user_prompt=full_prompt, system_prompt=system_prompt)
            rprint(Panel(resposta, title="Rascunho Regenerado", border_style="green"))
            continue

        if acao == "submeter":
            if not uuid:
                rprint(
                    f"[yellow]{icons.warning} UUID da atividade não disponível. "
                    "Salvando rascunho como alternativa.[/yellow]"
                )
                filepath = salvar_rascunho(turma_nome, pond, resposta)
                rprint(f"[dim]Rascunho salvo em: {filepath}[/dim]")
                return

            with console.status("[bold cyan]Submetendo via API...[/bold cyan]", spinner="dots"):
                sucesso = await client.submit_answer(uuid, resposta)

            if sucesso:
                rprint(Panel(
                    f"[bold green]{icons.success} Resposta submetida com sucesso![/bold green]",
                    title="Submissão Concluída",
                ))
                return
            else:
                rprint(f"[yellow]{icons.warning} Falha na submissão via API.[/yellow]")
                salvar = await questionary.confirm(
                    "Deseja salvar o rascunho em arquivo como alternativa?"
                ).ask_async()
                if salvar:
                    filepath = salvar_rascunho(turma_nome, pond, resposta)
                    rprint(
                        f"[green]{icons.success} Rascunho salvo em: "
                        f"[blue]{filepath}[/blue][/green]"
                    )
                return


async def menu_ponderada(pond: dict, client: AdaLoveAPIClient, turma_nome: str, extracao_data: dict):
    """
    Sub-menu de uma atividade ponderada individual.
    Mostra detalhes completos e opções de ação.
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
            questionary.Choice(title=f"{icons.robot} Gerar resposta com IA", value="ia"),
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

        if selected == "ia":
            await gerar_resposta_ia(client, turma_nome, pond, extracao_data)


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
            # Autenticação fica FORA do spinner: o login pode exigir que o
            # usuário aja na janela do navegador, e o spinner do Rich sobrescreve
            # as instruções de 2FA impressas no terminal.
            await client.authenticate(settings.login, settings.senha)

            try:
                with console.status("[bold green]Buscando turmas...[/bold green]", spinner="dots"):
                    sections_resp = await client.get(Endpoints.SECTIONS)
            except AuthenticationError:
                rprint("[yellow]⚠️ Token expirado. Renovando autenticação...[/yellow]")
                client.auth.token = None
                await client.authenticate(settings.login, settings.senha)
                with console.status("[bold green]Buscando turmas...[/bold green]", spinner="dots"):
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

        except AuthenticationError as e:
            # Falha de login é condição esperada, não defeito: traceback aqui só
            # esconde a orientação útil no meio de ruído.
            rprint(f"\n[bold red]❌ Não foi possível autenticar:[/bold red] {e}")
            rprint("[yellow]O que tentar:[/yellow]")
            rprint("  • Concluir o login na janela do navegador antes do tempo acabar")
            rprint("  • Dar mais tempo: [cyan]ADALOVE_AUTH_TIMEOUT=600 python adalove_cli.py[/cyan]")
            limpar = (
                "rmdir /s /q .auth_profile & del .token_cache"
                if sys.platform == "win32"
                else "rm -rf .auth_profile .token_cache"
            )
            rprint(f"  • Recomeçar a sessão: [cyan]{limpar}[/cyan]")
            rprint("  • Detalhes em [cyan]adalove_cli.log[/cyan]")
        except Exception as e:
            console.print_exception()
            rprint(f"[bold red]❌ Erro fatal:[/bold red] {e}")


# ============================================================================
# Modo não-interativo (CLI flags) — para ambientes sem TTY ou automação
# ============================================================================

async def _carregar_sections_via_api():
    """Autentica e retorna a lista de sections da API. Reusa cache de token."""
    settings = Settings()
    if not settings.login or not settings.senha:
        print("ERRO: .env sem LOGIN/SENHA", file=sys.stderr)
        sys.exit(1)
    client = AdaLoveAPIClient()
    await client.__aenter__()
    try:
        await client.authenticate(settings.login, settings.senha)
        try:
            resp = await client.get(Endpoints.SECTIONS)
        except AuthenticationError:
            client.auth.token = None
            await client.authenticate(settings.login, settings.senha)
            resp = await client.get(Endpoints.SECTIONS)
        sections = resp.get("sections", []) if isinstance(resp, dict) else resp
        return sections, client
    except Exception:
        await client.__aexit__(None, None, None)
        raise


async def _listar_cli(remote: bool):
    """Lista turmas em formato tabular. --remote=True consulta API; senão usa output/."""
    if not remote:
        if not OUTPUT_DIR.exists():
            print("(nenhuma turma extraída localmente em output/api_extraction/)")
            return
        rows = []
        for d in sorted(OUTPUT_DIR.iterdir()):
            arq = d / "extracao_completa.json"
            if arq.exists():
                try:
                    ts = json.loads(arq.read_text(encoding="utf-8")).get("extração_timestamp", "?")
                except Exception:
                    ts = "?"
                rows.append((d.name, ts))
        if not rows:
            print("(nenhuma turma extraída)")
            return
        print(f"{'STATUS':6} {'TURMA':50} TIMESTAMP")
        for nome, ts in rows:
            print(f"{'EXTR':6} {nome:50} {ts}")
        return

    sections, client = await _carregar_sections_via_api()
    try:
        ordenadas = sorted(
            sections,
            key=lambda x: x.get("caption", x.get("name", "zzz")),
            reverse=True,
        )
        print(f"{'STATUS':6} {'TURMA':50} UUID")
        for s in ordenadas:
            nome = s.get("caption", s.get("name", "N/A"))
            uuid = s.get("uuid", "")
            status = "EXTR" if is_turma_extraida(nome) else "--"
            print(f"{status:6} {nome:50} {uuid}")
    finally:
        await client.__aexit__(None, None, None)


async def _extrair_cli(nomes: list[str], force: bool, dry_run: bool, todas: bool, paralelo: int = 1):
    """Extrai uma ou mais turmas (ou todas via API). Honra --force, --dry-run, --paralelo."""
    sections, client = await _carregar_sections_via_api()
    nomes_disponiveis = {s.get("caption", s.get("name", "")): s for s in sections}

    if todas:
        alvos = list(nomes_disponiveis.keys())
    else:
        alvos = nomes
        faltantes = [n for n in alvos if n not in nomes_disponiveis]
        if faltantes:
            print(f"ERRO: turmas não encontradas na API: {faltantes}", file=sys.stderr)
            print(f"Use --list --remote para ver os nomes exatos.", file=sys.stderr)
            await client.__aexit__(None, None, None)
            sys.exit(1)

    # Fechar o client de listagem — `extrair_turma_completa` abre o seu próprio
    await client.__aexit__(None, None, None)

    plano = []
    for nome in alvos:
        ja = is_turma_extraida(nome)
        if ja and not force:
            plano.append((nome, "PULAR (já extraída; use --force)"))
        else:
            plano.append((nome, "RE-EXTRAIR" if ja else "EXTRAIR"))

    print("Plano de execução:")
    for nome, acao in plano:
        print(f"  [{acao}] {nome}")

    if dry_run:
        print("\n--dry-run: nada foi executado.")
        return

    a_executar = [nome for nome, acao in plano if acao in ("EXTRAIR", "RE-EXTRAIR")]
    if not a_executar:
        print("\nNada para executar (tudo pulado).")
        return

    print(f"\nExecutando {len(a_executar)} extração(ões) com paralelismo={paralelo}...\n")
    falhas: list[tuple[str, str]] = []
    sem = asyncio.Semaphore(max(1, paralelo))
    contador = {"feitas": 0}

    async def _executar_uma(nome: str):
        async with sem:
            idx = contador["feitas"] + 1
            contador["feitas"] = idx
            print(f"=== [{idx}/{len(a_executar)}] iniciando: {nome} ===", flush=True)
            try:
                await extrair_turma_completa(nome)
                print(f"✅ {nome}", flush=True)
            except Exception as e:
                print(f"❌ Falhou {nome}: {e}", file=sys.stderr, flush=True)
                falhas.append((nome, str(e)))

    await asyncio.gather(*[_executar_uma(n) for n in a_executar])

    print(f"\n{'=' * 60}")
    print(f"Concluído: {len(a_executar) - len(falhas)}/{len(a_executar)} sucesso(s)")
    if falhas:
        print(f"Falhas:")
        for nome, err in falhas:
            print(f"  - {nome}: {err}")
        sys.exit(1)


def _parse_args(argv: list[str]):
    """Argparse — retorna (args, modo_interativo: bool)."""
    import argparse
    parser = argparse.ArgumentParser(
        description="AdaLove Extractor CLI. Sem flags: menu interativo. Com flags: modo não-interativo (script-friendly).",
    )
    parser.add_argument("--list", action="store_true", help="Lista turmas. Sem --remote, usa cache local (output/).")
    parser.add_argument("--remote", action="store_true", help="Para --list: consulta API (precisa auth).")
    parser.add_argument("--extrair", action="append", default=[], metavar="NOME",
                        help="Extrai uma turma pelo nome exato. Pode ser repetido. Bloqueia se já extraída (use --force).")
    parser.add_argument("--extrair-todas", action="store_true", help="Extrai todas as turmas listadas pela API.")
    parser.add_argument("--force", action="store_true", help="Sobrescreve extrações existentes.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o plano de extração sem executar.")
    parser.add_argument("--paralelo", type=int, default=1, metavar="N",
                        help="Número de extrações concorrentes (asyncio.Semaphore). Default=1 (sequencial). "
                             "Recomendado: 3-5. Maior risco de rate-limit acima disso.")
    args = parser.parse_args(argv)
    modo_interativo = not (args.list or args.extrair or args.extrair_todas)
    return args, modo_interativo


if __name__ == "__main__":
    args, interativo = _parse_args(sys.argv[1:])
    try:
        if interativo:
            asyncio.run(main())
        elif args.list:
            asyncio.run(_listar_cli(remote=args.remote))
        else:
            asyncio.run(_extrair_cli(
                nomes=args.extrair,
                force=args.force,
                dry_run=args.dry_run,
                todas=args.extrair_todas,
                paralelo=args.paralelo,
            ))
    except KeyboardInterrupt:
        rprint("\n[yellow]Interrompido pelo usuário[/yellow]")
