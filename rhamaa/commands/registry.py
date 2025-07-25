import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm

from rhamaa.registry import APP_REGISTRY, get_app_info, list_available_apps

console = Console()

@click.group()
def registry():
    """Manage app registry."""
    pass

@registry.command()
def list():
    """List all apps in the registry."""
    apps = list_available_apps()
    
    console.print(Panel(
        "[bold cyan]RhamaaCMS App Registry[/bold cyan]\n"
        "[dim]Available prebuilt applications[/dim]",
        expand=False
    ))
    
    # Group apps by category
    categories = {}
    for app_key, app_info in apps.items():
        category = app_info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((app_key, app_info))
    
    for category, category_apps in categories.items():
        console.print(f"\n[bold green]{category}[/bold green]")
        
        table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE)
        table.add_column("App", style="bold cyan", width=12)
        table.add_column("Name", style="white", width=25)
        table.add_column("Description", style="dim", min_width=30)
        table.add_column("Repository", style="blue", width=35)
        
        for app_key, app_info in category_apps:
            table.add_row(
                app_key,
                app_info['name'],
                app_info['description'],
                app_info['repository']
            )
        
        console.print(table)
    
    console.print(f"\n[dim]Total: {len(apps)} apps available[/dim]")

@registry.command()
@click.argument('app_name')
def info(app_name):
    """Show detailed information about a specific app."""
    app_info = get_app_info(app_name)
    
    if not app_info:
        console.print(Panel(
            f"[red]App '[bold]{app_name}[/bold]' not found in registry.[/red]",
            title="[red]App Not Found[/red]",
            expand=False
        ))
        return
    
    console.print(Panel(
        f"[bold cyan]{app_info['name']}[/bold cyan]\n\n"
        f"[bold]Description:[/bold] {app_info['description']}\n"
        f"[bold]Category:[/bold] [green]{app_info['category']}[/green]\n"
        f"[bold]Repository:[/bold] [blue]{app_info['repository']}[/blue]\n"
        f"[bold]Branch:[/bold] [yellow]{app_info['branch']}[/yellow]\n\n"
        f"[dim]Install with:[/dim] [cyan]rhamaa add {app_name}[/cyan]",
        title=f"[cyan]{app_name}[/cyan]",
        expand=False
    ))

@registry.command()
def update():
    """Update the app registry (placeholder for future implementation)."""
    console.print(Panel(
        "[yellow]Registry update functionality will be implemented in future versions.[/yellow]\n"
        "Currently, the registry is built into the CLI.",
        title="[yellow]Coming Soon[/yellow]",
        expand=False
    ))