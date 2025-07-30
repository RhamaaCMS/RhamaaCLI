import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm

from rhamaa.registry import (
    APP_REGISTRY, 
    get_app_info, 
    list_available_apps,
    get_template_info, 
    list_available_templates
)

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
@click.argument('template_name')
def template(template_name):
    """Show detailed information about a specific template."""
    template_info = get_template_info(template_name)
    
    if not template_info:
        console.print(Panel(
            f"[red]Template '[bold]{template_name}[/bold]' not found in registry.[/red]",
            title="[red]Template Not Found[/red]",
            expand=False
        ))
        return
    
    console.print(Panel(
        f"[bold cyan]{template_info['name']}[/bold cyan]\n\n"
        f"[bold]Description:[/bold] {template_info['description']}\n"
        f"[bold]Category:[/bold] [green]{template_info['category']}[/green]\n"
        f"[bold]Repository:[/bold] [blue]{template_info['repository']}[/blue]\n\n"
        f"[bold]Features:[/bold]\n" + 
        "\n".join([f"  • {feature}" for feature in template_info['features']]) + "\n\n"
        f"[dim]Use with:[/dim] [cyan]rhamaa start MyProject --template {template_name}[/cyan]",
        title=f"[cyan]{template_name}[/cyan]",
        expand=False
    ))

@registry.command()
def templates():
    """List all available project templates."""
    templates = list_available_templates()
    
    console.print(Panel(
        "[bold cyan]RhamaaCMS Project Templates[/bold cyan]\n"
        "[dim]Available templates for project creation[/dim]",
        expand=False
    ))
    
    # Group templates by category
    categories = {}
    for template_key, template_info in templates.items():
        category = template_info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((template_key, template_info))
    
    for category, category_templates in categories.items():
        console.print(f"\n[bold green]{category}[/bold green]")
        
        table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE)
        table.add_column("Template", style="bold cyan", width=12)
        table.add_column("Name", style="white", width=25)
        table.add_column("Description", style="dim", min_width=35)
        
        for template_key, template_info in category_templates:
            table.add_row(
                template_key,
                template_info['name'],
                template_info['description']
            )
        
        console.print(table)
    
    console.print(f"\n[dim]Total: {len(templates)} templates available[/dim]")
    console.print("\n[bold]Usage:[/bold]")
    console.print("  [cyan]rhamaa start MyProject --template blog[/cyan]")
    console.print("  [cyan]rhamaa registry template blog[/cyan]  [dim]# Show template details[/dim]")

@registry.command()
def update():
    """Update the app registry (placeholder for future implementation)."""
    console.print(Panel(
        "[yellow]Registry update functionality will be implemented in future versions.[/yellow]\n"
        "Currently, the registry is built into the CLI.",
        title="[yellow]Coming Soon[/yellow]",
        expand=False
    ))