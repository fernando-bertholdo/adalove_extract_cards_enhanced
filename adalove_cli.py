#!/usr/bin/env python3
"""
AdaLove CLI - Interface Interativa para Extração de Cards
"""

import sys
import asyncio
import logging
import questionary
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from adalove_extractor.api import AdaLoveAPIClient
from adalove_extractor.api.endpoints import Endpoints
from adalove_extractor.api.exceptions import AuthenticationError
from adalove_extractor.config.settings import Settings
from extrair_turma_completa import extrair_turma_completa

# Configure basic logging to file only to not mess up TUI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='adalove_cli.log',
    filemode='a'
)

console = Console()

def show_banner():
    """Exibe o banner inicial."""
    title = Text("🚀🤖 ADALOVE EXTRACTOR by 0xftb", style="bold magenta")
    subtitle = Text("Ferramenta CLI para extração de cards e materiais", style="cyan")
    
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="magenta",
        expand=False
    )
    rprint(panel)

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
            settings = Settings() # Reload
        else:
            sys.exit(1)

    console.print(f"[dim]Usando conta: {settings.login}[/dim]")
    
    async with AdaLoveAPIClient() as client:
        try:
            with console.status("[bold green]Autenticando e buscando turmas...[/bold green]", spinner="dots"):
                # Authenticate (uses cache if available)
                await client.authenticate(settings.login, settings.senha)
                
                # Fetch sections with auto-retry for 401
                try:
                    sections_resp = await client.get(Endpoints.SECTIONS)
                except AuthenticationError:
                    # Token expired/invalid despite cache check
                    rprint("[yellow]⚠️ Token expirado ou inválido. Renovando autenticação...[/yellow]")
                    client.auth.token = None # Clear invalid token
                    await client.authenticate(settings.login, settings.senha) # Force full login
                    sections_resp = await client.get(Endpoints.SECTIONS) # Retry request
                
            # Extract list from response
            sections_list = []
            if isinstance(sections_resp, dict):
                sections_list = sections_resp.get("sections", [])
            elif isinstance(sections_resp, list):
                sections_list = sections_resp
                
            if not sections_list:
                rprint("[bold red]❌ Nenhuma turma encontrada![/bold red]")
                return

            # Prepare choices for questionary
            # Sort by name descending (usually puts newest dates first)
            sorted_sections = sorted(
                sections_list, 
                key=lambda x: x.get('caption', x.get('name', 'zzz')), 
                reverse=True
            )
            
            choices = []
            for section in sorted_sections:
                name = section.get('caption', section.get('name', 'N/A'))
                uuid = section.get('uuid', 'N/A')
                choices.append(questionary.Choice(
                    title=f"{name}",
                    value=name # We pass the name to the extractor function
                ))
            
            choices.append(questionary.Separator())
            choices.append(questionary.Choice(title="❌ Sair", value="EXIT"))
            
            # Interactive Selection
            selected_turma = await questionary.select(
                "Selecione a turma para extrair:",
                choices=choices,
                style=questionary.Style([
                    ('qmark', 'fg:#E91E63 bold'),
                    ('question', 'fg:#673AB7 bold'),
                    ('answer', 'fg:#2196f3 bold'),
                    ('pointer', 'fg:#E91E63 bold'),
                ])
            ).ask_async()
            
            if not selected_turma or selected_turma == "EXIT":
                rprint("[yellow]Saindo...[/yellow]")
                return
            
            # Confirmation
            if not await questionary.confirm(f"Confirmar extração da turma: {selected_turma}?").ask_async():
                rprint("[yellow]Operação cancelada.[/yellow]")
                return
            
            # Execute Extraction
            console.print(f"\n[bold green]🚀 Iniciando extração de: {selected_turma}[/bold green]")
            console.print("[dim]Acompanhe o log detalhado em: adalove_cli.log[/dim]")
            
            # Run the extraction logic
            result_dir = await extrair_turma_completa(selected_turma)
            
            if result_dir:
                rprint(Panel(
                    f"[bold green]✅ Sucesso![/bold green]\n\nCards salvos em:\n[blue]{result_dir}[/blue]",
                    title="Extração Concluída"
                ))
                
                # Open folder option (Mac specific)
                if sys.platform == "darwin" and await questionary.confirm("Abrir pasta dos arquivos?").ask_async():
                    import subprocess
                    subprocess.run(["open", str(result_dir)])
            else:
                rprint("[bold red]❌ Falha na extração. Verifique o log para detalhes.[/bold red]")

        except Exception as e:
            console.print_exception()
            rprint(f"[bold red]❌ Erro fatal:[/bold red] {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        rprint("\n[yellow]Interrompido pelo usuário[/yellow]")
