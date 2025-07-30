import click
import subprocess
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Confirm

from rhamaa.registry import (
    get_template_info, 
    list_available_templates, 
    is_template_available,
    get_template_url,
    TEMPLATE_REGISTRY
)

console = Console()

@click.command()
@click.argument('project_name', required=False)
@click.argument('target_dir', required=False)
@click.option('--template', '-t', default='default', help='Template to use from registry')
@click.option('--list-templates', is_flag=True, help='List available templates')
@click.option('--dev', is_flag=True, help='Use local development template (for testing)')
def start(project_name, target_dir, template, list_templates, dev):
    """Create a new Wagtail project using RhamaaCMS templates.
    
    PROJECT_NAME: Name of the project to create
    TARGET_DIR: Optional target directory, use '.' for current directory
    
    Examples:
        rhamaa start MyProject                    # Create MyProject folder with project inside
        rhamaa start MyBlog --template blog       # Create MyBlog folder with blog template
        rhamaa start MyProject .                  # Create MyProject in current directory
        rhamaa start MyProject . --template blog  # Create MyProject in current dir with blog template
        rhamaa start --list-templates             # List available templates
        rhamaa start MyProject --dev              # Use local template (development)
    """
    
    # Show available templates if requested
    if list_templates:
        show_available_templates()
        return
    
    # Validate project_name is provided when not listing templates
    if not project_name:
        console.print(Panel(
            f"[red]Project name is required.[/red]\n\n"
            f"[bold]Usage:[/bold]\n"
            f"  [cyan]rhamaa start MyProject[/cyan]\n"
            f"  [cyan]rhamaa start . --template blog[/cyan]\n"
            f"  [cyan]rhamaa start --list-templates[/cyan]\n\n"
            f"[dim]Use [cyan]rhamaa start --help[/cyan] for more information.[/dim]",
            title="[red]Missing Project Name[/red]",
            expand=False
        ))
        return
    
    # Validate template
    if not is_template_available(template):
        console.print(Panel(
            f"[red]Template '[bold]{template}[/bold]' not found in registry.[/red]\n\n"
            f"[dim]Use [cyan]rhamaa start --list-templates[/cyan] to see available templates.[/dim]",
            title="[red]Template Not Found[/red]",
            expand=False
        ))
        return
    
    # Determine target directory and project setup
    if target_dir == '.':
        # Create project in current directory
        current_dir = Path.cwd()
        
        # Check if directory is empty or confirm overwrite
        if any(current_dir.iterdir()):
            console.print(Panel(
                f"[yellow]Current directory '[bold]{current_dir}[/bold]' is not empty.[/yellow]\n"
                f"Creating project '[cyan]{project_name}[/cyan]' will add files to this directory.",
                title="[yellow]Directory Not Empty[/yellow]",
                expand=False
            ))
            
            if not Confirm.ask("Continue anyway?", default=False):
                console.print("[dim]Operation cancelled.[/dim]")
                return
        
        target_path = current_dir
        use_current_dir = True
        console.print(Panel(
            f"[green]Creating project '[cyan]{project_name}[/cyan]' in current directory:[/green] [bold]{current_dir}[/bold]",
            expand=False
        ))
    else:
        # Standard project creation - create new folder
        target_path = Path(project_name)
        use_current_dir = False
        
        if target_path.exists():
            console.print(Panel(
                f"[red]Directory '[bold]{project_name}[/bold]' already exists.[/red]",
                title="[red]Directory Exists[/red]",
                expand=False
            ))
            return
        
        console.print(Panel(
            f"[green]Creating new Wagtail project:[/green] [bold]{project_name}[/bold]",
            expand=False
        ))
    
    # Get template info and show details
    template_info = get_template_info(template)
    console.print(Panel(
        f"[bold cyan]{template_info['name']}[/bold cyan]\n"
        f"[dim]{template_info['description']}[/dim]\n\n"
        f"[bold]Features:[/bold]\n" + 
        "\n".join([f"  • {feature}" for feature in template_info['features']]),
        title=f"[cyan]Using Template: {template}[/cyan]",
        expand=False
    ))
    
    # Get template URL
    if dev:
        # Use local RhamaaCMS template for development
        current_dir = Path(__file__).parent.parent.parent  # Go up to RhamaaCLI root
        local_template_path = current_dir.parent / "RhamaaCMS"  # Sibling directory
        
        if local_template_path.exists():
            template_url = str(local_template_path)
            console.print(Panel(
                f"[yellow]Development Mode:[/yellow] Using local template\n"
                f"[dim]Path:[/dim] [cyan]{template_url}[/cyan]",
                title="[yellow]Dev Mode[/yellow]",
                expand=False
            ))
        else:
            console.print(Panel(
                f"[red]Local template not found at:[/red]\n[cyan]{local_template_path}[/cyan]\n\n"
                f"[dim]Falling back to registry template...[/dim]",
                title="[yellow]Dev Mode Warning[/yellow]",
                expand=False
            ))
            template_url = get_template_url(template)
    else:
        template_url = get_template_url(template)
    
    # Prepare wagtail start command
    if use_current_dir:
        # Create project in current directory using wagtail's "." syntax
        cmd = [
            "wagtail", "start",
            f"--template={template_url}",
            project_name,
            "."
        ]
        
        console.print(f"[dim]Creating project '{project_name}' in current directory...[/dim]")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(Panel(
                f"[bold green]Project '{project_name}' created successfully in current directory![/bold green]",
                expand=False
            ))
        else:
            console.print(Panel(
                f"[red]Error creating project:[/red]\n{result.stderr}",
                title="[red]Creation Failed[/red]",
                expand=False
            ))
            return
    else:
        # Standard project creation - creates new folder
        cmd = [
            "wagtail", "start",
            f"--template={template_url}",
            project_name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(Panel(
                f"[bold green]Project {project_name} created successfully![/bold green]",
                expand=False
            ))
        else:
            console.print(Panel(
                f"[red]Error creating project:[/red]\n{result.stderr}",
                title="[red]Creation Failed[/red]",
                expand=False
            ))
            return
    
    # Show next steps
    show_next_steps(project_name, target_path, use_current_dir)

def show_available_templates():
    """Display all available templates in a formatted table."""
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
    console.print("  [cyan]rhamaa start . --template portfolio[/cyan]")

def show_next_steps(project_name, target_path, use_current_dir=False):
    """Show next steps after project creation."""
    if use_current_dir:
        cd_command = ""
        cd_text = ""
    else:
        cd_command = f"cd {project_name}\n"
        cd_text = f"[cyan]cd {project_name}[/cyan]\n"
    
    console.print(Panel(
        f"[bold green]🎉 Project created successfully![/bold green]\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"{cd_text}"
        f"[cyan]python -m venv .venv[/cyan]\n"
        f"[cyan]source .venv/bin/activate[/cyan]  [dim]# Linux/Mac[/dim]\n"
        f"[cyan]pip install -r requirements.txt[/cyan]\n"
        f"[cyan]cd node && npm install && cd ..[/cyan]\n"
        f"[cyan]python manage.py migrate[/cyan]\n"
        f"[cyan]python manage.py createsuperuser[/cyan]\n"
        f"[cyan]cd node && npm run build && cd ..[/cyan]\n"
        f"[cyan]python manage.py runserver[/cyan]\n\n"
        f"[bold]Development workflow:[/bold]\n"
        f"[cyan]cd node && npm run watch[/cyan]  [dim]# Watch assets[/dim]\n"
        f"[cyan]python manage.py runserver[/cyan]  [dim]# Django server[/dim]\n\n"
        f"[bold]Add more apps:[/bold]\n"
        f"[cyan]rhamaa add --list[/cyan]  [dim]# List available apps[/dim]\n"
        f"[cyan]rhamaa add users[/cyan]  [dim]# Add user management[/dim]",
        title="[green]Getting Started[/green]",
        expand=False
    ))