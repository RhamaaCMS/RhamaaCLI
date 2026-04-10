# Code Conventions

**Analysis Date:** 2026-04-10

## Naming

**Files:**
- Snake_case module names: `config_utils.py`, `manifest_applier.py`, `conflict_detector.py`, `dependency_resolver.py`
- Command files named after their CLI verb: `start.py`, `startapp.py`, `server.py`, `database.py`, `management.py`
- Template files use `.tpl` extension: `apps.py.tpl`, `models.py.tpl`, `views.py.tpl`

**Classes:**
- PascalCase throughout: `AppManifest`, `ManifestApplier`, `ManifestParser`, `ConflictDetector`, `DependencyResolver`, `SettingsParser`, `URLParser`
- Dataclasses for value objects: `MiddlewareConfig`, `URLConfig`, `DjangoConfig`, `ApplyResult`, `DependencyNode`, `Conflict`
- Conflict subclasses follow `<Type>Conflict` pattern: `SettingConflict`, `URLConflict`, `MiddlewareConflict`, `TemplateDirConflict`

**Functions:**
- Snake_case for all functions and methods: `load_app_registry()`, `find_settings_file()`, `create_standard_app()`
- Private methods prefixed with underscore: `_apply_settings()`, `_apply_urls()`, `_run_post_install()`, `_build_graph()`, `_resolve_dict()`
- Helper functions prefixed with underscore: `_render_template()`, `_read_template()`, `_write_from_template()`
- Boolean check functions prefixed `is_` or `check_`: `is_app_available()`, `is_django_project()`, `check_wagtail_project()`

**Variables:**
- Snake_case: `app_name`, `manifest_path`, `project_path`, `dry_run`, `backup_files`
- Constants in UPPER_SNAKE_CASE: `ASCII_LOGO`, `HELP_COMMANDS`, `TEMPLATE_REGISTRY_PKG`, `DEFAULT_TEMPLATE_KEY`, `CLI_ROOT`
- Module-level `console = Console()` declared once per file that needs Rich output

## Code Style

**Formatter:** Black (configured in `pyproject.toml`)
- Line length: 88 characters
- Target Python version: `py37`
- Applied to `*.py` and `*.pyi` files
- Excludes `.eggs`, `.git`, `.venv`, `build`, `dist`

**Linting:** flake8 is a dev dependency but has no project config file — defaults apply.

**Imports:**
- Standard library first, then third-party, then local
- Local imports within command subpackage use relative paths: `from .utils import run_manage`, `from .manifest import AppManifest`
- Cross-package imports use absolute paths: `from rhamaa.utils import download_github_repo`, `from rhamaa.config_utils import auto_configure_app`

**Type hints:**
- Used consistently in library modules: `rhamaa/manifest.py`, `rhamaa/manifest_applier.py`, `rhamaa/config_utils.py`, `rhamaa/conflict_detector.py`, `rhamaa/dependency_resolver.py`
- Omitted in simpler/older files: `rhamaa/utils.py`, most command files
- Return types annotated: `-> "AppManifest"`, `-> List[str]`, `-> bool`, `-> Optional[Path]`
- String forward references used for self-referencing dataclasses: `-> "AppManifest"`

## Patterns

**Dataclasses for configuration objects:**
Every configuration concept is a `@dataclass` with a `from_dict(cls, data: dict)` classmethod for deserialization and a `to_dict()` method where serialization is needed. All fields default to safe empty values. From `rhamaa/manifest.py`:
```python
@dataclass
class MiddlewareConfig:
    class_path: str
    priority: int = 50
    position: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MiddlewareConfig":
        if isinstance(data, str):
            return cls(class_path=data)
        return cls(
            class_path=data.get("class", data.get("middleware", "")),
            priority=data.get("priority", 50),
            position=data.get("position")
        )
```

**Result objects for operations:**
Operations that can partially fail return a result dataclass rather than raising. `ApplyResult` in `rhamaa/manifest_applier.py` carries `success`, `changes`, `errors`, `warnings`, and `backup_files`. Implements `__bool__` so callers can do `if result:`.

**Module-level console singleton:**
Every module using Rich output declares `console = Console()` at module level. This is repeated in `rhamaa/cli.py`, `rhamaa/utils.py`, `rhamaa/manifest_applier.py`, `rhamaa/config_utils.py` (inside a function), and all command files. There is no shared console instance.

**Guard block for runnable examples:**
Several library modules include usage examples under `if __name__ == "__main__":` — present in `rhamaa/manifest.py`, `rhamaa/conflict_detector.py`, `rhamaa/dependency_resolver.py`. These double as smoke tests.

**Click command registration pattern:**
```
rhamaa/cli.py          → @click.group() main
rhamaa/commands/cms/__init__.py → @click.group() cms, registered via main.add_command(cms)
rhamaa/commands/cms/*.py       → @click.command() functions, registered via cms.add_command(...)
```
Each command file exports exactly one `@click.command()` function. The `__init__.py` imports and registers all of them.

**Template rendering:**
Double-brace placeholder syntax `{{var}}` in `.tpl` files. Rendered by `_render_template()` in `rhamaa/commands/cms/startapp.py` using plain string replacement (no Jinja2). Template files read via `pkgutil.get_data()` for package-safe access:
```python
def _read_template(rel_path: str) -> str:
    pkg = 'rhamaa.templates.cms.APPS_TEMPLATES'
    data = pkgutil.get_data(pkg, rel_path)
    return data.decode('utf-8')
```
Manifest placeholder system uses single-brace syntax `{app_name}`, `{app_class}`, `{app_upper}` — distinct from template placeholders.

**Regex-based file modification:**
`SettingsParser` and `URLParser` in `rhamaa/config_utils.py` use `re.sub()` with `re.DOTALL` to locate and modify Python source file lists (`INSTALLED_APPS`, `MIDDLEWARE`, `urlpatterns`) in memory, then write atomically. Each mutating method returns `bool` indicating whether a change was actually made. Backup via `.bak` file on write.

**Numbered inline steps:**
Complex orchestration methods label steps numerically in comments:
```python
# 1. Add INSTALLED_APPS
# 2. Add middleware
# 3. Add template directories
# 4. Add auth backends
# 5. Set custom settings
```
This pattern appears in `ManifestApplier._apply_settings()` and `ManifestApplier.apply_all()`.

## Documentation

**Module docstrings:**
All core library modules have a top-level docstring stating the module's purpose:
```python
"""
App Manifest System for RhamaaCLI
Parses and applies rhamaa-app.json configuration
"""
```

**Class docstrings:**
Dataclasses and main classes have short docstrings. `AppManifest` documents its placeholder system inline in the class docstring.

**Method docstrings:**
Non-trivial public methods use Google-style with `Args:` and `Returns:` sections. Simple methods use one-liners:
```python
def apply_all(self, dry_run: bool = False, backup: bool = False) -> ApplyResult:
    """
    Apply all manifest configurations.

    Args:
        dry_run: If True, preview changes without applying
        backup: If True, create .bak files before modifications

    Returns:
        ApplyResult with status and details
    """
```

**Inline comments:**
Used to explain regex patterns, fallback logic, and numbered orchestration steps. Not used for self-evident code.

## Error Handling

**User-facing commands** catch exceptions and print Rich-formatted errors, then return without raising:
```python
except subprocess.CalledProcessError:
    console.print("[red]Error:[/red] Failed to create project. Make sure Wagtail is installed")
except FileNotFoundError:
    console.print("[red]Error:[/red] wagtail command not found. Install with: pip install wagtail")
```

**Library functions** return `(None, [error_strings])` or `ApplyResult(success=False, errors=[...])` rather than raising:
```python
try:
    manifest = AppManifest.from_file(manifest_path)
    errors = manifest.validate()
    if errors:
        return None, errors
    return manifest, []
except json.JSONDecodeError as e:
    return None, [f"Invalid JSON: {e}"]
except Exception as e:
    return None, [f"Error loading manifest: {e}"]
```

**Validation is decoupled from parsing:** `AppManifest.validate()` returns `List[str]` of errors and is called after construction, not inside `from_dict()`.

**`subprocess.run()` usage:**
- `check=False` in library code — caller inspects `.returncode`
- `check=True` in command code — `CalledProcessError` is caught by the surrounding handler

**Custom exception:** `CircularDependencyError(Exception)` in `rhamaa/dependency_resolver.py` is the only project-defined exception. All other error states use return values.

**Rich color convention for output:**
- `[red]Error:[/red]` — hard errors
- `[yellow]Warning:[/yellow]` — non-fatal issues
- `[cyan]...[/cyan]` — progress/action messages
- `[green]✓[/green]` — success confirmations
- `[dim]...[/dim]` — secondary/informational text
