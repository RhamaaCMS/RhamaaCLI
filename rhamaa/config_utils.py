"""
Configuration utilities for RhamaaCLI - Django settings and URL manipulation.
"""

import re
from pathlib import Path
from typing import Optional, List


class SettingsParser:
    """Parse and modify Django settings files."""

    def __init__(self, settings_path: Path):
        self.path = Path(settings_path)
        self.content = self.path.read_text(encoding='utf-8')
        self.original_content = self.content

    def add_installed_app(self, app_path: str) -> bool:
        """
        Add an app to INSTALLED_APPS list.
        Returns True if added, False if already exists.
        """
        # Check if already exists
        if f"'{app_path}'" in self.content or f'"{app_path}"' in self.content:
            return False

        # Pattern to find INSTALLED_APPS = [ ... ]
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'

        def replacer(match):
            start = match.group(1)
            apps_section = match.group(2)
            end = match.group(3)

            # Find the last app entry to insert after
            lines = apps_section.rstrip().split('\n')
            if not lines or not lines[0].strip():
                # Empty list case
                new_app = f"\n    '{app_path}',\n"
            else:
                # Get indentation from last line
                last_line = lines[-1]
                indent_match = re.match(r'^(\s*)', last_line)
                indent = indent_match.group(1) if indent_match else '    '
                new_app = f"\n{indent}'{app_path}',"

            # Insert before closing bracket
            new_section = apps_section.rstrip() + new_app + '\n'
            return f"{start}{new_section}{end}"

        new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)

        if new_content == self.content:
            # No match found, try alternative patterns
            return False

        self.content = new_content
        return True

    def write(self, backup: bool = True) -> None:
        """Write changes to file, optionally creating backup."""
        if backup:
            backup_path = self.path.with_suffix('.py.bak')
            backup_path.write_text(self.original_content, encoding='utf-8')

        self.path.write_text(self.content, encoding='utf-8')


class URLParser:
    """Parse and modify Django URL configuration files."""

    def __init__(self, urls_path: Path):
        self.path = Path(urls_path)
        self.content = self.path.read_text(encoding='utf-8')
        self.original_content = self.content

    def add_url_pattern(self, app_name: str, prefix: Optional[str] = None) -> bool:
        """
        Add URL include pattern for an app to urlpatterns list.
        Returns True if added, False if already exists.
        """
        path_prefix = prefix or app_name
        app_path = f"apps.{app_name}"
        url_include = f"path('{path_prefix}/', include('{app_path}.urls'))"

        # Check if already included
        if f"{app_path}.urls" in self.content:
            return False

        # Pattern to find urlpatterns = [ ... ]
        pattern = r'(urlpatterns\s*=\s*\[)(.*?)(\])'

        def replacer(match):
            start = match.group(1)
            urls_section = match.group(2)
            end = match.group(3)

            # Get indentation
            lines = urls_section.rstrip().split('\n')
            if lines and lines[0].strip():
                last_line = lines[-1]
                indent_match = re.match(r'^(\s*)', last_line)
                indent = indent_match.group(1) if indent_match else '    '
            else:
                indent = '    '

            new_url = f"\n{indent}{url_include},"

            # Insert before closing bracket
            new_section = urls_section.rstrip() + new_url + '\n'
            return f"{start}{new_section}{end}"

        new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)

        if new_content == self.content:
            return False

        self.content = new_content

        # Add include import if not present
        if 'from django.urls import' in self.content:
            if 'include' not in self.content:
                self.content = self.content.replace(
                    'from django.urls import path',
                    'from django.urls import path, include'
                )

        return True

    def write(self, backup: bool = True) -> None:
        """Write changes to file, optionally creating backup."""
        if backup:
            backup_path = self.path.with_suffix('.py.bak')
            backup_path.write_text(self.original_content, encoding='utf-8')

        self.path.write_text(self.content, encoding='utf-8')


def create_app_urls_py(app_dir: Path, app_name: str) -> Path:
    """
    Create basic urls.py for the app if it doesn't exist.
    Returns the path to the created file.
    """
    urls_path = app_dir / 'urls.py'

    if urls_path.exists():
        return urls_path

    urls_content = f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
]
'''
    urls_path.write_text(urls_content, encoding='utf-8')
    return urls_path


def find_settings_file(project_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find Django settings file in common locations.
    Returns the first match or None.
    """
    search_path = project_path or Path.cwd()

    candidates = [
        search_path / "settings" / "base.py",
        search_path / "settings" / "local.py",
        search_path / "settings" / "production.py",
        search_path / "settings.py",
    ]

    # Also try project-named subdirectory
    for subdir in search_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            candidates.extend([
                subdir / "settings" / "base.py",
                subdir / "settings" / "local.py",
                subdir / "settings" / "production.py",
                subdir / "settings.py",
            ])

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def find_urls_file(project_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find Django urls file in common locations.
    Returns the first match or None.
    """
    search_path = project_path or Path.cwd()

    candidates = [
        search_path / "urls.py",
    ]

    # Also try project-named subdirectory
    for subdir in search_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            candidates.append(subdir / "urls.py")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def auto_configure_app(app_name: str, project_path: Optional[Path] = None,
                       dry_run: bool = False, backup: bool = True) -> List[str]:
    """
    Auto-configure an app in the Django project.
    Returns list of change descriptions.
    """
    from rich.console import Console
    console = Console()

    changes = []
    search_path = project_path or Path.cwd()

    # 1. Add to INSTALLED_APPS
    settings_file = find_settings_file(search_path)
    if settings_file:
        parser = SettingsParser(settings_file)
        if parser.add_installed_app(f'apps.{app_name}'):
            if not dry_run:
                parser.write(backup=backup)
            try:
                rel_path = settings_file.relative_to(search_path)
            except ValueError:
                rel_path = settings_file.name
            changes.append(f"Added 'apps.{app_name}' to INSTALLED_APPS in {rel_path}")
    else:
        changes.append(f"[yellow]Could not find settings file[/yellow]")

    # 2. Add to URLs
    urls_file = find_urls_file(search_path)
    if urls_file:
        parser = URLParser(urls_file)
        if parser.add_url_pattern(app_name):
            if not dry_run:
                parser.write(backup=backup)
            try:
                rel_path = urls_file.relative_to(search_path)
            except ValueError:
                rel_path = urls_file.name
            changes.append(f"Added URL pattern for '{app_name}' in {rel_path}")
    else:
        changes.append(f"[yellow]Could not find urls.py[/yellow]")

    # 3. Create app urls.py if needed
    app_dir = search_path / "apps" / app_name
    if app_dir.exists():
        urls_path = create_app_urls_py(app_dir, app_name)
        if urls_path.exists():
            changes.append(f"Created app urls.py at apps/{app_name}/urls.py")

    return changes
