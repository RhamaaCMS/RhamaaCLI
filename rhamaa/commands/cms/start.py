import click
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.command()
@click.argument('project_name')
def start(project_name):
    """Create a new Wagtail project using the RhamaaCMS template."""
    template_url = "https://github.com/RhamaaCMS/RhamaaCMS/archive/refs/heads/base.zip"
    cmd = [
        "wagtail", "start",
        f"--template={template_url}",
        project_name
    ]
    console.print(Panel(f"[green]Creating new Wagtail project:[/green] [bold]{project_name}[/bold]", expand=False))
    try:
        subprocess.run(cmd, check=True)
        console.print(Panel(f"[bold green]Project {project_name} created![/bold green]", expand=False))
    except subprocess.CalledProcessError:
        console.print("[red]Error:[/red] Failed to create project. Make sure Wagtail is installed")
    except FileNotFoundError:
        console.print("[red]Error:[/red] wagtail command not found. Install with: pip install wagtail")