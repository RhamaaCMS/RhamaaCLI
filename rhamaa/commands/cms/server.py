import click
import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console
from .utils import run_manage

console = Console()


def find_wsgi_application() -> Optional[str]:
    """Auto-detect WSGI application module from the project structure.

    Looks for a wsgi.py file one level deep (e.g. myproject/wsgi.py)
    whose parent directory is a Python package (contains __init__.py).
    Returns a dotted module string such as 'myproject.wsgi:application',
    or None if detection fails.
    """
    cwd = Path.cwd()
    for wsgi_path in sorted(cwd.rglob("wsgi.py")):
        rel = wsgi_path.relative_to(cwd)
        parts = rel.parts
        if len(parts) == 2 and (cwd / parts[0] / "__init__.py").exists():
            return f"{parts[0]}.wsgi:application"
    return None


@click.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default='8000', help='Port to bind to')
@click.option('--prod', is_flag=True, help='Run with Gunicorn for production')
def run(host, port, prod):
    """Start development or production server."""
    if prod:
        wsgi_app = find_wsgi_application()
        if not wsgi_app:
            console.print(
                "[red]Error:[/red] Could not detect WSGI application. "
                "Make sure you are in the root of a Django project directory."
            )
            return
        console.print(f"[cyan]Starting production server with Gunicorn ({wsgi_app})...[/cyan]")
        try:
            subprocess.run([
                'gunicorn',
                '--bind', f'{host}:{port}',
                '--workers', '3',
                wsgi_app,
            ], check=True)
        except FileNotFoundError:
            console.print("[red]Error:[/red] Gunicorn not installed. Install with: pip install gunicorn")
        except subprocess.CalledProcessError:
            console.print("[red]Error:[/red] Failed to start Gunicorn server")
    else:
        console.print(f"[cyan]Starting development server on {host}:{port}...[/cyan]")
        run_manage(['runserver', f'{host}:{port}'])