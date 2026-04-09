# Code Conventions - RhamaaCLI

## Python Style

### Code Formatting
- **Tool**: Black (configured in `pyproject.toml`)
- **Line length**: 88 characters
- **Target Python version**: 3.7+
- **Include pattern**: `\.pyi?$`

### Import Style
```python
# Standard library imports first
import os
import shutil
import tempfile
from pathlib import Path

# Third-party imports
import click
import requests
from rich.console import Console
from rich.progress import Progress

# Local imports last
from rhamaa.commands.cms import cms
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `startapp.py`, `build_template.py` |
| Functions | snake_case | `download_github_repo()`, `check_wagtail_project()` |
| Variables | snake_case | `app_name`, `zip_path` |
| Constants | UPPER_SNAKE_CASE | `ASCII_LOGO`, `HELP_COMMANDS` |
| Classes | PascalCase | (none currently) |
| CLI commands | lowercase with hyphens | `build-template`, `startapp` |

## CLI Conventions

### Command Structure
```python
@click.command()
@click.argument('name')
@click.option('--type', default='minimal', help='App type')
@click.option('--force/--no-force', default=False, help='Overwrite existing')
def startapp(name, type, force):
    """Brief description for help text."""
    pass
```

### Help Text Format
- Short description in docstring
- Rich terminal output for main help (`cli.py`)
- Color-coded command descriptions:
  - `[green]` - Creation commands
  - `[yellow]` - App commands
  - `[blue]` - Info commands
  - `[cyan]` - Installation commands

### Error Handling
```python
from rich.console import Console
console = Console()

try:
    # operation
except requests.RequestException as e:
    console.print(f"[red]Error downloading repository: {e}[/red]")
    return None
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")
    return False
```

## Template Conventions

### .tpl File Placeholders
| Placeholder | Meaning | Example Output |
|-------------|---------|----------------|
| `{{app_name}}` | Raw app name | `blog` |
| `{{app_name\|lower}}` | Lowercase | `blog` |
| `{{app_name\|upper}}` | Uppercase | `BLOG` |
| `{{app_name\|title}}` | Title case | `Blog` |
| `{{app_name\|slug}}` | Slug format | `my-app` |

### Template Processing
```python
template_content = template_file.read_text()
processed = template_content.replace('{{app_name}}', app_name)
processed = processed.replace('{{app_name|upper}}', app_name.upper())
# ... etc
output_file.write_text(processed)
```

## Project Structure Conventions

### App Location
- All apps created in `apps/` folder (not project root)
- This follows RhamaaCMS architecture pattern

### File Organization
```
apps/
├── blog/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── templates/
```

## Rich UI Conventions

### Progress Bars
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    task = progress.add_task("[cyan]Downloading...", total=None)
    # ... work with progress.update(task, advance=...)
```

### Panel Usage
```python
from rich.panel import Panel
from rich.text import Text
from rich import box

console.print(Panel(
    Text(ASCII_LOGO, justify="center"),
    style="bold magenta",
    box=box.DOUBLE,
    expand=False
))
```

## Git Conventions

### Version Management
- Uses `setuptools_scm` for git-based versioning
- Version derived from git tags
- No hardcoded version in source (only in `pyproject.toml` as fallback)

### Commit Messages
- Standard format assumed (not explicitly documented)

## Documentation Conventions

### README.md Structure
1. Quick Start (installation + basic usage)
2. Command documentation
3. Available prebuilt apps table
4. Usage examples
5. Requirements and links

### Code Documentation
- Docstrings for functions with Args/Returns sections
- Type hints not currently used (Python 3.7+ compatible)
