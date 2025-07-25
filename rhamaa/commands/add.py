import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box
from pathlib import Path

from rhamaa.registry import get_app_info, list_available_apps, is_app_available
from rhamaa.utils import download_github_repo, extract_repo_to_apps, check_wagtail_project

console = Console()

@click.command()
@click.argument('app_name', required=False)
@click.option('--list', '-l', is_flag=True, help='List all available apps')
@click.option('--force', '-f', is_flag=True, help='Force install even if app already exists')
def add(app_name, list, force):
    """Add a prebuilt app to the project (mqtt, users, articles, lms, etc)."""
    
    # Show available apps if --list flag is used or no app_name provided
    if list or not app_name:
        show_available_apps()
        return
    
    # Check if we're in a Wagtail project
    if not check_wagtail_project():
        console.print(Panel(
            "[red]Error:[/red] This doesn't appear to be a Wagtail project.\n"
            "Please run this command from the root of your Wagtail project.",
            title="[red]Not a Wagtail Project[/red]",
            expand=False
        ))
        return
    
    # Check if app exists in registry
    if not is_app_available(app_name):
        console.print(Panel(
            f"[red]Error:[/red] App '[bold]{app_name}[/bold]' not found in registry.\n"
            f"Use [cyan]rhamaa add --list[/cyan] to see available apps.",
            title="[red]App Not Found[/red]",
            expand=False
        ))
        return
    
    # Check if app already exists
    app_dir = Path("apps") / app_name
    if app_dir.exists() and not force:
        console.print(Panel(
            f"[yellow]Warning:[/yellow] App '[bold]{app_name}[/bold]' already exists in apps/ directory.\n"
            f"Use [cyan]--force[/cyan] flag to overwrite existing app.",
            title="[yellow]App Already Exists[/yellow]",
            expand=False
        ))
        return
    
    # Get app information
    app_info = get_app_info(app_name)
    
    # Show app information
    console.print(Panel(
        f"[bold cyan]{app_info['name']}[/bold cyan]\n"
        f"[dim]{app_info['description']}[/dim]\n"
        f"Repository: [blue]{app_info['repository']}[/blue]\n"
        f"Category: [green]{app_info['category']}[/green]",
        title=f"[cyan]Installing {app_name}[/cyan]",
        expand=False
    ))
    
    # Download and install app
    install_app(app_name, app_info)

def show_available_apps():
    """Display all available apps in a formatted table."""
    apps = list_available_apps()
    
    console.print(Panel(
        "[bold cyan]Available Prebuilt Apps[/bold cyan]\n"
        "[dim]Use 'rhamaa add <app_name>' to install an app[/dim]",
        expand=False
    ))
    
    table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
    table.add_column("App Name", style="bold cyan", width=12)
    table.add_column("Description", style="white", min_width=30)
    table.add_column("Category", style="green", width=15)
    
    for app_key, app_info in apps.items():
        table.add_row(
            app_key,
            app_info['description'],
            app_info['category']
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(apps)} apps available[/dim]")

def install_app(app_name, app_info):
    """Install an app from the registry."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        # Download repository
        download_task = progress.add_task("Starting download...", total=100)
        
        zip_path = download_github_repo(
            app_info['repository'], 
            app_info['branch'], 
            progress, 
            download_task
        )
        
        if not zip_path:
            console.print(Panel(
                "[red]Failed to download repository.[/red]\n"
                "Please check your internet connection and try again.",
                title="[red]Download Failed[/red]",
                expand=False
            ))
            return
        
        # Extract repository
        extract_task = progress.add_task("Extracting files...", total=100)
        
        success = extract_repo_to_apps(
            zip_path, 
            app_name, 
            progress, 
            extract_task
        )
        
        if success:
            progress.update(extract_task, completed=100, description="[green]Installation complete!")
            
            console.print(Panel(
                f"[green]✓[/green] Successfully installed '[bold]{app_name}[/bold]' app!\n\n"
                f"[dim]App location:[/dim] [cyan]apps/{app_name}/[/cyan]\n"
                f"[dim]Next steps:[/dim]\n"
                f"1. Add '[cyan]{app_name}[/cyan]' to your INSTALLED_APPS in settings\n"
                f"2. Run migrations: [cyan]python manage.py makemigrations && python manage.py migrate[/cyan]\n"
                f"3. Check the app's README for additional setup instructions",
                title="[green]Installation Successful[/green]",
                expand=False
            ))
        else:
            console.print(Panel(
                "[red]Failed to extract and install the app.[/red]\n"
                "Please try again or install manually.",
                title="[red]Installation Failed[/red]",
                expand=False
            ))
