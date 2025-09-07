import click
import os
from pathlib import Path
import pkgutil
from importlib import resources
from rich.console import Console
from rich.panel import Panel
from rich import box
from rhamaa.registry import get_app_info, is_app_available
from rhamaa.utils import download_github_repo, extract_repo_to_apps, check_wagtail_project
from rich.table import Table
from rich import box as rich_box
from rhamaa.registry import list_available_apps

console = Console()


@click.command()
@click.argument('app_name', required=False)
@click.option('--path', '-p', default='apps', help='Directory to create the app in (default: apps)')
@click.option('--type', 'app_type', type=click.Choice(['wagtail', 'minimal']), default='wagtail', show_default=True, help='App template type')
@click.option('--prebuild', type=str, default=None, help='Install a prebuilt app from registry (e.g. blog, users) into the given app_name directory')
@click.option('--list', 'list_apps', is_flag=True, help='List available prebuilt apps from registry')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing directory when using --prebuild')
def startapp(app_name, path, app_type, prebuild, list_apps, force):
    """Create a new Django app with RhamaaCMS structure."""

    # List available registry apps and exit
    if list_apps:
        show_available_apps()
        return

    if not app_name:
        console.print(Panel(
            "[red]Error:[/red] Please provide an app name, e.g. [cyan]rhamaa startapp blog[/cyan]",
            title="[red]Missing App Name[/red]",
            expand=False
        ))
        return

    # Validate app name
    if not app_name.isidentifier():
        console.print(Panel(
            f"[red]Error:[/red] '[bold]{app_name}[/bold]' is not a valid Python identifier.\n"
            "App names should only contain letters, numbers, and underscores, and cannot start with a number.",
            title="[red]Invalid App Name[/red]",
            expand=False
        ))
        return

    # Create app directory
    app_dir = Path(path) / app_name

    if app_dir.exists() and not prebuild:
        console.print(Panel(
            f"[yellow]Warning:[/yellow] Directory '[bold]{app_dir}[/bold]' already exists.\n"
            "Please choose a different app name or remove the existing directory.",
            title="[yellow]Directory Exists[/yellow]",
            expand=False
        ))
        return

    # If --prebuild provided, install registry app into apps/<app_name>
    if prebuild:
        # Check project validity (heuristic)
        if not check_wagtail_project():
            console.print(Panel(
                "[yellow]Note:[/yellow] Could not verify a Wagtail project in current directory. Continuing anyway...",
                title="[yellow]Project Check[/yellow]",
                expand=False
            ))

        # Validate registry key
        if not is_app_available(prebuild):
            console.print(Panel(
                f"[red]Error:[/red] Prebuilt app '[bold]{prebuild}[/bold]' not found in registry.\n"
                f"Use [cyan]rhamaa startapp --list[/cyan] to see available apps.",
                title="[red]App Not Found[/red]",
                expand=False
            ))
            return

        # If target exists and not force, warn
        if app_dir.exists() and not force:
            console.print(Panel(
                f"[yellow]Warning:[/yellow] Target directory '[bold]{app_dir}[/bold]' already exists.\n"
                f"Use [cyan]--force[/cyan] to overwrite.",
                title="[yellow]Directory Exists[/yellow]",
                expand=False
            ))
            return

        app_info = get_app_info(prebuild)
        console.print(Panel(
            f"[bold cyan]{app_info['name']}[/bold cyan]\n"
            f"[dim]{app_info['description']}[/dim]\n"
            f"Repository: [blue]{app_info['repository']}[/blue]\n"
            f"Branch: [yellow]{app_info['branch']}[/yellow]",
            title=f"[cyan]Installing prebuilt: {prebuild} -> {app_name}[/cyan]",
            expand=False
        ))

        # Download and extract into apps/<app_name>
        zip_path = download_github_repo(app_info['repository'], app_info['branch'])
        if not zip_path:
            console.print(Panel(
                "[red]Failed to download repository.[/red]",
                title="[red]Download Failed[/red]",
                expand=False
            ))
            return
        success = extract_repo_to_apps(zip_path, app_name)
        if not success:
            console.print(Panel(
                "[red]Failed to extract and install the app.[/red]",
                title="[red]Installation Failed[/red]",
                expand=False
            ))
            return

        console.print(Panel(
            f"[green]✓[/green] Successfully installed prebuilt app to '[bold]{app_dir}[/bold]'\n"
            f"Next steps:\n"
            f"1. Add '[cyan]{app_name}[/cyan]' to your INSTALLED_APPS\n"
            f"2. Run migrations",
            title="[green]Prebuilt Installation Successful[/green]",
            expand=False
        ))
        return

    # Otherwise, generate scaffold using selected template type
    console.print(Panel(
        f"[cyan]Creating new app:[/cyan] [bold]{app_name}[/bold]\n"
        f"[dim]Location:[/dim] [blue]{app_dir}[/blue]\n"
        f"Template: [yellow]{app_type}[/yellow]",
        title="[cyan]RhamaaCMS App Generator[/cyan]",
        expand=False
    ))

    # Create app directory structure
    create_app_structure(app_dir, app_name, app_type)

    console.print(Panel(
        f"[green]✓[/green] Successfully created '[bold]{app_name}[/bold]' app!\n\n"
        f"[dim]App location:[/dim] [cyan]{app_dir}[/cyan]\n"
        f"[dim]Next steps:[/dim]\n"
        f"1. The app will be auto-discovered by RhamaaCMS\n"
        f"2. Run migrations: [cyan]python manage.py makemigrations {app_name}[/cyan]\n"
        f"3. Run: [cyan]python manage.py migrate[/cyan]\n"
        f"4. Start developing your models, views, and templates!",
        title="[green]App Created Successfully[/green]",
        expand=False
    ))

def _render_template(content: str, context: dict) -> str:
    """Very small placeholder renderer using {{var}} tokens."""
    rendered = content
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    return rendered


def _read_template(rel_path: str) -> str:
    """Read template file from rhamaa/templates/APPS_TEMPLATES using pkgutil for broad Py support."""
    pkg = 'rhamaa.templates.APPS_TEMPLATES'
    data = pkgutil.get_data(pkg, rel_path)
    if data is None:
        raise FileNotFoundError(f"Template not found: {rel_path}")
    return data.decode('utf-8')


def _write_from_template(rel_template_path: str, dest_path: Path, context: dict):
    content = _read_template(rel_template_path)
    rendered = _render_template(content, context)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(rendered, encoding='utf-8')


def create_app_structure(app_dir, app_name, app_type='wagtail'):
    """Create the complete app directory structure with RhamaaCMS templates."""

    # Create main directory
    app_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    subdirs = ['migrations', 'templates', 'static',
               'management', 'management/commands']
    for subdir in subdirs:
        (app_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create templates subdirectory for the app
    (app_dir / 'templates' / app_name).mkdir(parents=True, exist_ok=True)

    # Create __init__.py files
    init_files = [
        '',
        'migrations',
        'management',
        'management/commands'
    ]

    for init_path in init_files:
        init_file = app_dir / init_path / \
            '__init__.py' if init_path else app_dir / '__init__.py'
        init_file.touch()

    # Context for templates
    context = {
        'app_name': app_name,
        'app_title': app_name.replace('_', ' ').title(),
        'app_verbose_name': app_name.replace('_', ' ').title(),
        'app_config_class': f"{app_name.title().replace('_', '')}Config",
        'app_name_upper': app_name.upper(),
        'app_class_name': app_name.title().replace('_', ''),
    }

    # Choose template prefix based on type
    prefix = 'minimal/' if app_type == 'minimal' else 'wagtail/'

    # Create app files with templates
    create_apps_py(app_dir, app_name, context, prefix)
    create_models_py(app_dir, app_name, context, prefix)
    create_views_py(app_dir, app_name, context, prefix)
    create_admin_py(app_dir, app_name, context, prefix)
    create_urls_py(app_dir, app_name, context, prefix)
    create_settings_py(app_dir, app_name, context, prefix)
    create_tests_py(app_dir, app_name, context, prefix)
    create_initial_migration(app_dir, context, prefix)
    create_template_files(app_dir, app_name, context, prefix)


def create_apps_py(app_dir, app_name, context, prefix=''):
    """Create apps.py with RhamaaCMS configuration from template."""
    _write_from_template(f'{prefix}apps.py.tpl', app_dir / 'apps.py', context)


def create_models_py(app_dir, app_name, context, prefix=''):
    """Create models.py from template."""
    _write_from_template(f'{prefix}models.py.tpl', app_dir / 'models.py', context)


def create_views_py(app_dir, app_name, context, prefix=''):
    """Create views.py from template."""
    _write_from_template(f'{prefix}views.py.tpl', app_dir / 'views.py', context)


def create_admin_py(app_dir, app_name, context, prefix=''):
    """Create admin.py from template."""
    _write_from_template(f'{prefix}admin.py.tpl', app_dir / 'admin.py', context)


def create_urls_py(app_dir, app_name, context, prefix=''):
    """Create urls.py for the app from template."""
    _write_from_template(f'{prefix}urls.py.tpl', app_dir / 'urls.py', context)


def create_settings_py(app_dir, app_name, context, prefix=''):
    """Create settings.py from template."""
    _write_from_template(f'{prefix}settings.py.tpl', app_dir / 'settings.py', context)


def create_tests_py(app_dir, app_name, context, prefix=''):
    """Create tests.py from template."""
    _write_from_template(f'{prefix}tests.py.tpl', app_dir / 'tests.py', context)


def create_initial_migration(app_dir, context, prefix=''):
    """Create initial migration file from template."""
    # Minimal template might not include migrations; guard safely
    try:
        _write_from_template(f'{prefix}migrations/0001_initial.py.tpl', app_dir / 'migrations' / '0001_initial.py', context)
    except FileNotFoundError:
        pass


def create_template_files(app_dir, app_name, context, prefix=''):
    """Create template files for the app from .tpl files."""
    # HTML template files are only for wagtail type
    if prefix == 'wagtail/':
        _write_from_template('wagtail/templates/index.html.tpl', app_dir / 'templates' / app_name / 'index.html', context)
        _write_from_template('wagtail/templates/example_page.html.tpl', app_dir / 'templates' / app_name / 'example_page.html', context)


def show_available_apps():
    """Display all available apps in a formatted table (inline to avoid add dependency)."""
    apps = list_available_apps()

    console.print(Panel(
        "[bold cyan]Available Prebuilt Apps[/bold cyan]\n"
        "[dim]Use 'rhamaa startapp <app_name> --prebuild <registry_key>' to install an app[/dim]",
        expand=False
    ))

    table = Table(show_header=True, header_style="bold blue", box=rich_box.ROUNDED)
    table.add_column("Key", style="bold cyan", width=12)
    table.add_column("Name", style="white", width=25)
    table.add_column("Description", style="white", min_width=30)
    table.add_column("Category", style="green", width=15)

    for app_key, app_info in apps.items():
        table.add_row(
            app_key,
            app_info.get('name', ''),
            app_info.get('description', ''),
            app_info.get('category', '')
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(apps)} apps available[/dim]")
