import click
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.command()
@click.argument('app_name')
def add(app_name):
    """Add a prebuilt app to the project (users, article, LMS, IoT, etc)."""
    console.print(Panel(f"[yellow]Pretend to add app:[/yellow] [bold]{app_name}[/bold]\n[italic]Implement logic here[/italic]", expand=False))
