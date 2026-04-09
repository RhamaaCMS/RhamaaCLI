"""
Configuration utilities for RhamaaCLI - Django settings and URL manipulation.
"""

import re
from pathlib import Path
from typing import Optional, List, Any


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

    def add_middleware(self, middleware_class: str, position: Optional[str] = None) -> bool:
        """
        Add middleware to MIDDLEWARE list.
        
        Args:
            middleware_class: Full Python path to middleware class
            position: Optional positioning hint:
                     - "first": Insert at beginning
                     - "last": Insert at end (default)
                     - "before:X": Insert before middleware X
                     - "after:X": Insert after middleware X
        
        Returns True if added, False if already exists.
        """
        # Check if already exists
        if middleware_class in self.content:
            return False

        # Find MIDDLEWARE list
        pattern = r'(MIDDLEWARE\s*=\s*\[)(.*?)(\])'
        match = re.search(pattern, self.content, re.DOTALL)
        
        if not match:
            # MIDDLEWARE not found, try to add it as new setting
            self._add_new_list_setting('MIDDLEWARE', [middleware_class])
            return True

        def replacer(match):
            start = match.group(1)
            middleware_section = match.group(2)
            end = match.group(3)

            lines = middleware_section.rstrip().split('\n')
            if not lines or not lines[0].strip():
                # Empty list
                new_middleware = f"\n    '{middleware_class}',\n"
            else:
                # Get indentation
                last_line = lines[-1]
                indent_match = re.match(r'^(\s*)', last_line)
                indent = indent_match.group(1) if indent_match else '    '
                new_middleware = f"\n{indent}'{middleware_class}',"

            # Handle positioning
            if position and position.startswith('after:'):
                target = position[6:]
                # Find the target middleware and insert after it
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if target in line and not inserted:
                        new_lines.append(f"{indent}'{middleware_class}',")
                        inserted = True
                if inserted:
                    new_section = '\n'.join(new_lines) + '\n'
                    return f"{start}{new_section}{end}"
            elif position and position.startswith('before:'):
                target = position[7:]
                # Find the target middleware and insert before it
                new_lines = []
                inserted = False
                for line in lines:
                    if target in line and not inserted:
                        new_lines.append(f"{indent}'{middleware_class}',")
                        inserted = True
                    new_lines.append(line)
                if inserted:
                    new_section = '\n'.join(new_lines) + '\n'
                    return f"{start}{new_section}{end}"

            # Default: insert at end
            new_section = middleware_section.rstrip() + new_middleware + '\n'
            return f"{start}{new_section}{end}"

        new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)
        
        if new_content != self.content:
            self.content = new_content
            return True
        return False

    def add_template_dirs(self, dirs: List[str]) -> bool:
        """
        Add template directories to TEMPLATES configuration.
        Returns True if any directory was added.
        """
        if not dirs:
            return False

        # Find TEMPLATES list with 'DIRS' key
        # Pattern matches: 'DIRS': [ ... ] or "DIRS": [ ... ]
        pattern = r'((?:\'|\"|\b)DIRS(?:\'|\"|\b)\s*:\s*\[)(.*?)(\])'
        
        added_any = False
        
        for dir_path in dirs:
            if dir_path in self.content:
                continue  # Already exists
                
            def replacer(match):
                nonlocal added_any
                start = match.group(1)
                dirs_section = match.group(2)
                end = match.group(3)
                
                # Get indentation
                lines = dirs_section.rstrip().split('\n')
                if lines and lines[-1].strip():
                    indent_match = re.match(r'^(\s*)', lines[-1])
                    indent = indent_match.group(1) if indent_match else '        '
                else:
                    indent = '        '
                
                new_dir = f"\n{indent}os.path.join(BASE_DIR, '{dir_path}'),"
                new_section = dirs_section.rstrip() + new_dir + '\n'
                added_any = True
                return f"{start}{new_section}{end}"
            
            new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL, count=1)
            if new_content != self.content:
                self.content = new_content
        
        return added_any

    def add_context_processors(self, processors: List[str]) -> bool:
        """
        Add context processors to TEMPLATES configuration.
        Returns True if any processor was added.
        """
        if not processors:
            return False

        # Find context_processors in TEMPLATES
        pattern = r'(context_processors\s*:\s*\[)(.*?)(\])'
        
        added_any = False
        
        for processor in processors:
            if processor in self.content:
                continue  # Already exists
                
            def replacer(match):
                nonlocal added_any
                start = match.group(1)
                proc_section = match.group(2)
                end = match.group(3)
                
                # Get indentation
                lines = proc_section.rstrip().split('\n')
                if lines and lines[-1].strip():
                    indent_match = re.match(r'^(\s*)', lines[-1])
                    indent = indent_match.group(1) if indent_match else '                '
                else:
                    indent = '                '
                
                new_proc = f"\n{indent}'{processor}',"
                new_section = proc_section.rstrip() + new_proc + '\n'
                added_any = True
                return f"{start}{new_section}{end}"
            
            new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL, count=1)
            if new_content != self.content:
                self.content = new_content
        
        return added_any

    def add_auth_backends(self, backends: List[str]) -> bool:
        """
        Add authentication backends.
        Returns True if any backend was added.
        """
        if not backends:
            return False

        # Check if AUTHENTICATION_BACKENDS exists
        if 'AUTHENTICATION_BACKENDS' not in self.content:
            # Add new setting
            self._add_new_setting('AUTHENTICATION_BACKENDS', backends)
            return True

        # Add to existing list
        pattern = r'(AUTHENTICATION_BACKENDS\s*=\s*\[)(.*?)(\])'
        
        added_any = False
        
        for backend in backends:
            if backend in self.content:
                continue
                
            def replacer(match):
                nonlocal added_any
                start = match.group(1)
                backends_section = match.group(2)
                end = match.group(3)
                
                lines = backends_section.rstrip().split('\n')
                if lines and lines[-1].strip():
                    indent_match = re.match(r'^(\s*)', lines[-1])
                    indent = indent_match.group(1) if indent_match else '    '
                else:
                    indent = '    '
                
                new_backend = f"\n{indent}'{backend}',"
                new_section = backends_section.rstrip() + new_backend + '\n'
                added_any = True
                return f"{start}{new_section}{end}"
            
            new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL, count=1)
            if new_content != self.content:
                self.content = new_content
        
        return added_any

    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a Django setting value.
        If setting already exists, it will be updated.
        Returns True if setting was added/updated.
        """
        # Check if setting already exists
        pattern = rf'^({key}\s*=\s*)(.+?)$'
        
        def format_value(val):
            if isinstance(val, str):
                return f"'{val}'"
            elif isinstance(val, bool):
                return str(val)
            elif isinstance(val, (int, float)):
                return str(val)
            elif isinstance(val, (list, tuple)):
                return repr(val)
            elif isinstance(val, dict):
                return repr(val)
            return str(val)
        
        formatted_value = format_value(value)
        
        if re.search(pattern, self.content, re.MULTILINE):
            # Update existing setting
            new_content = re.sub(
                pattern, 
                rf'\g<1>{formatted_value}', 
                self.content, 
                flags=re.MULTILINE
            )
            if new_content != self.content:
                self.content = new_content
                return True
        else:
            # Add new setting at end of file
            new_setting = f"\n{key} = {formatted_value}\n"
            self.content = self.content.rstrip() + new_setting
            return True
        
        return False

    def add_staticfiles_dirs(self, dirs: List[str]) -> bool:
        """
        Add static files directories.
        Returns True if any directory was added.
        """
        if not dirs:
            return False

        if 'STATICFILES_DIRS' not in self.content:
            # Add new setting
            self._add_new_list_setting('STATICFILES_DIRS', dirs)
            return True

        pattern = r'(STATICFILES_DIRS\s*=\s*\[)(.*?)(\])'
        
        added_any = False
        
        for dir_path in dirs:
            if dir_path in self.content:
                continue
                
            def replacer(match):
                nonlocal added_any
                start = match.group(1)
                dirs_section = match.group(2)
                end = match.group(3)
                
                lines = dirs_section.rstrip().split('\n')
                if lines and lines[-1].strip():
                    indent_match = re.match(r'^(\s*)', lines[-1])
                    indent = indent_match.group(1) if indent_match else '    '
                else:
                    indent = '    '
                
                new_dir = f"\n{indent}os.path.join(BASE_DIR, '{dir_path}'),"
                new_section = dirs_section.rstrip() + new_dir + '\n'
                added_any = True
                return f"{start}{new_section}{end}"
            
            new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL, count=1)
            if new_content != self.content:
                self.content = new_content
        
        return added_any

    def _add_new_list_setting(self, name: str, items: List[str]) -> None:
        """Helper to add a new list-based setting."""
        formatted_items = [f"    '{item}'," for item in items]
        new_setting = f"\n{name} = [\n" + '\n'.join(formatted_items) + '\n]\n'
        self.content = self.content.rstrip() + new_setting

    def _add_new_setting(self, name: str, value: Any) -> None:
        """Helper to add a new setting."""
        if isinstance(value, list):
            formatted_items = [f"    '{item}'," for item in value]
            new_setting = f"\n{name} = [\n" + '\n'.join(formatted_items) + '\n]\n'
        else:
            formatted_value = repr(value)
            new_setting = f"\n{name} = {formatted_value}\n"
        self.content = self.content.rstrip() + new_setting

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

    def add_url_config(self, url_config: dict) -> bool:
        """
        Add a URL pattern from a URLConfig dictionary.
        
        Args:
            url_config: Dict with keys: path, include, namespace (optional), name (optional)
        
        Returns True if added, False if already exists.
        """
        path = url_config.get('path', '')
        include_path = url_config.get('include', '')
        namespace = url_config.get('namespace')
        name = url_config.get('name')
        
        if not path or not include_path:
            return False
        
        # Check if already included
        if include_path in self.content:
            return False
        
        # Build URL pattern
        if namespace:
            url_pattern = f"path('{path}', include('{include_path}', namespace='{namespace}'))"
        else:
            url_pattern = f"path('{path}', include('{include_path}'))"
        
        # Add name comment if provided
        if name:
            url_pattern += f"  # {name}"
        
        # Find urlpatterns list
        pattern = r'(urlpatterns\s*=\s*\[)(.*?)(\])'
        
        def replacer(match):
            start = match.group(1)
            urls_section = match.group(2)
            end = match.group(3)
            
            # Get indentation
            lines = urls_section.rstrip().split('\n')
            if lines and lines[-1].strip():
                indent_match = re.match(r'^(\s*)', lines[-1])
                indent = indent_match.group(1) if indent_match else '    '
            else:
                indent = '    '
            
            new_url = f"\n{indent}{url_pattern},"
            new_section = urls_section.rstrip() + new_url + '\n'
            return f"{start}{new_section}{end}"
        
        new_content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)
        
        if new_content == self.content:
            return False
        
        self.content = new_content
        
        # Ensure include is imported
        self._ensure_include_import()
        
        return True
    
    def add_url_patterns(self, url_configs: List[dict]) -> List[str]:
        """
        Add multiple URL patterns.
        
        Returns list of successfully added URL paths.
        """
        added = []
        for config in url_configs:
            if self.add_url_config(config):
                added.append(config.get('path', 'unknown'))
        return added
    
    def check_url_conflict(self, path: str) -> bool:
        """
        Check if a URL path already exists.
        Returns True if conflict found.
        """
        # Look for path('path/' ... or path("path/" ...
        escaped_path = re.escape(path)
        pattern = rf"path\((['\"]){escaped_path}\1"
        return bool(re.search(pattern, self.content))
    
    def _ensure_include_import(self) -> None:
        """Ensure 'include' is imported from django.urls."""
        if 'from django.urls import' in self.content:
            if 'include' not in self.content:
                self.content = self.content.replace(
                    'from django.urls import path',
                    'from django.urls import path, include'
                )

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
