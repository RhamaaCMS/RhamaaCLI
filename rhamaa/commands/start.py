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
    subprocess.run(cmd)
    console.print(Panel(f"[bold green]Project {project_name} created![/bold green]", expand=False))
