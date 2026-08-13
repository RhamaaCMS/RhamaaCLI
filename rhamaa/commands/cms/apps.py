"""Commands for current-only registered app updates."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from rhamaa.app_versioning import (
    installed_manifest,
    parse_version,
    update_registered_app,
)
from rhamaa.commands.cms.startapp import load_app_registry


console = Console()


@click.group("apps")
def apps():
    """Inspect and update registered Rhamaa apps."""


@apps.command("status")
def status():
    """Show locally installed and registry-current app versions."""
    registry = load_app_registry()
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("App")
    table.add_column("Package")
    table.add_column("Installed")
    table.add_column("Current")
    table.add_column("Status")
    for key, info in registry.items():
        app_name, _, manifest, _ = installed_manifest(Path.cwd(), key, info)
        installed = manifest.version if manifest else "-"
        current = str(info.get("version", "?"))
        state = "not installed"
        if manifest:
            try:
                installed_number = parse_version(installed)
                current_number = parse_version(current)
                if installed_number == current_number:
                    state = "current"
                elif installed_number < current_number:
                    state = "update available"
                else:
                    state = "newer than registry"
            except ValueError:
                state = "invalid version"
        table.add_row(key, app_name, installed, current, state)
    console.print(table)


@apps.command("update")
@click.argument("app_key", required=False)
@click.option("--all", "update_all", is_flag=True, help="Update every installed registered app")
@click.option("--dry-run", is_flag=True, help="Validate and preview without replacing files")
@click.option("--reinstall", is_flag=True, help="Replace code even when already current")
def update(app_key, update_all, dry_run, reinstall):
    """Update APP_KEY to registry current version; version selection is unsupported."""
    if bool(app_key) == bool(update_all):
        raise click.UsageError("Provide APP_KEY or --all, but not both.")
    registry = load_app_registry()
    if app_key:
        key = app_key.lower()
        if key not in registry:
            raise click.ClickException(f"Registered app '{app_key}' not found.")
        selected = [(key, registry[key])]
    else:
        selected = []
        for key, info in registry.items():
            _, app_dir, manifest, _ = installed_manifest(Path.cwd(), key, info)
            if app_dir.exists() and manifest:
                selected.append((key, info))

    if not selected:
        console.print("[yellow]No installed registered apps found.[/yellow]")
        return

    failures = []
    for key, info in selected:
        console.print(f"[cyan]Checking {key}...[/cyan]")
        result = update_registered_app(
            registry_key=key,
            app_info=info,
            project_path=Path.cwd(),
            dry_run=dry_run,
            reinstall=reinstall,
        )
        if result.success:
            for change in result.changes:
                console.print(f"  [green]OK[/green] {change}")
            if result.backup_path:
                console.print(f"  [dim]Backup: {result.backup_path}[/dim]")
        else:
            failures.append(key)
            for error in result.errors:
                console.print(f"  [red]ERROR[/red] {error}")
    if failures:
        raise click.ClickException(f"Update failed: {', '.join(failures)}")
