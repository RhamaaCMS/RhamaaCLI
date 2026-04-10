# Architecture

**Analysis Date:** 2026-04-10

## Overview

RhamaaCLI is a Python CLI tool distributed as a PyPI package (`rhamaa`) that scaffolds and manages Wagtail/Django CMS projects. It delegates heavy lifting to external tools (`wagtail start`, `django-admin`, `manage.py`) while providing a structured app-installation pipeline built around a declarative JSON manifest system (`rhamaa-app.json`).

## Architectural Layers

```
┌──────────────────────────────────────────────────────────┐
│  CLI Layer                                               │
│  rhamaa/cli.py, rhamaa/__main__.py                       │
│  - click group/command routing                           │
│  - ASCII logo + Rich help display on bare invocation     │
├──────────────────────────────────────────────────────────┤
│  Command Layer                                           │
│  rhamaa/commands/cms/                                    │
│  - One file per concern (start, startapp, server, ...)   │
│  - Each file exports one or more click commands          │
│  - Registered explicitly in commands/cms/__init__.py     │
├──────────────────────────────────────────────────────────┤
│  Manifest System                                         │
│  rhamaa/manifest.py + rhamaa/manifest_applier.py         │
│  - Parse rhamaa-app.json into typed dataclasses          │
│  - Apply settings/URL changes to target Django project   │
│  - Driven by conflict_detector.py + dependency_resolver  │
├──────────────────────────────────────────────────────────┤
│  Config Utilities                                        │
│  rhamaa/config_utils.py                                  │
│  - Regex-based read/write of settings.py and urls.py     │
│  - SettingsParser, URLParser classes                     │
├──────────────────────────────────────────────────────────┤
│  Shared Utilities                                        │
│  rhamaa/utils.py                                         │
│  - Download GitHub repos as ZIP                          │
│  - Extract ZIP to apps/ directory                        │
│  - Wagtail project detection                             │
├──────────────────────────────────────────────────────────┤
│  Template Registry                                       │
│  rhamaa/templates/cms/                                   │
│  - JSON registries for projects and apps                 │
│  - .tpl scaffold files for app creation                  │
│  - All data accessed via pkgutil.get_data()              │
└──────────────────────────────────────────────────────────┘
```

## Core Components

### CLI Entry (`rhamaa/cli.py`, `rhamaa/__main__.py`)
- `main` is the root `click.group`; only `cms` sub-group is registered (`main.add_command(cms)`)
- Invoked with no subcommand → renders ASCII logo + Rich command table
- `rhamaa/__main__.py` enables `python -m rhamaa` invocation

### Command Group — `cms` (`rhamaa/commands/cms/__init__.py`)
All commands live under `rhamaa cms ...`. Subcommands are imported from individual modules and registered with `cms.add_command()`.

| File | Commands registered | Primary responsibility |
|---|---|---|
| `start.py` | `start` | Scaffold new Wagtail project from template registry or custom source |
| `startapp.py` | `startapp` | Create/install Django apps (standard, prebuilt, or ZIP template) |
| `server.py` | `run` | Dev server via `manage.py runserver`; prod via `gunicorn` |
| `database.py` | `migrate`, `makemigrations` | Proxy to `manage.py` DB commands |
| `management.py` | `check`, `test`, `collectstatic`, `createsuperuser`, `shell`, `update_index` | Thin `manage.py` wrappers |
| `info.py` | `status`, `info` | Inspect current Django/Wagtail project state |
| `build.py` | `build-template` | Package a live project as a redistributable ZIP template (scrubs `SECRET_KEY`) |
| `utils.py` | — | `run_manage()` shared by all management command modules |

### Manifest System (`rhamaa/manifest.py`)
Typed dataclasses representing a `rhamaa-app.json` file:
- `AppManifest` — top-level container; metadata + sub-configs
- `DjangoConfig` — `INSTALLED_APPS`, middleware, templates, auth backends, arbitrary settings dict
- `URLConfig` — path + include + optional namespace
- `Dependencies` — required apps, pip packages, optional apps
- `PostInstallConfig` — `migrate` flag, fixtures, management commands, user-facing messages
- `MiddlewareConfig` — class path + priority + optional `before:/after:` positioning

`AppManifest.resolve_placeholders(app_name)` substitutes `{app_name}`, `{app_class}`, `{app_upper}` recursively throughout the manifest before application.

`ManifestParser.find_manifest(app_dir)` searches for `rhamaa-app.json`, `manifest.json`, or `.rhamaa/manifest.json`.

### Manifest Applier (`rhamaa/manifest_applier.py`)
`ManifestApplier` orchestrates the full installation pipeline:
1. Locate `settings.py` and `urls.py` in the target project
2. Run `DependencyResolver` to check and order inter-app deps
3. Run `ConflictDetector` to surface setting/middleware conflicts
4. Apply resolved manifest via `SettingsParser` and `URLParser`
5. Execute post-install hooks (migrations, fixtures, management commands)

Returns `ApplyResult` dataclass (success, changes list, errors, warnings, backup_files).

### Configuration Utilities (`rhamaa/config_utils.py`)
Regex-based file modification (no AST parsing):
- `SettingsParser` — `add_installed_app()`, `add_middleware()`, `add_setting()`; reads file on init, writes on `save()`
- `URLParser` — `add_url_pattern()` to append `include()` entries to `urlpatterns`
- `find_settings_file(project_path)` — searches common Django settings locations
- `find_urls_file(project_path)` — finds root `urls.py`
- `auto_configure_app(app_name)` — convenience wrapper used by `startapp` for standard app creation

### Dependency Resolver (`rhamaa/dependency_resolver.py`)
`DependencyResolver` builds a directed graph from app manifests and runs Kahn's topological sort algorithm to determine safe installation order. Detects circular dependencies.

### Conflict Detector (`rhamaa/conflict_detector.py`)
`ConflictDetector` compares manifests of apps being installed together and reports:
- `SettingConflict` — same Django setting key with conflicting values
- `MiddlewareConflict` — incompatible middleware ordering requirements

Severity levels: `info`, `warning`, `error`.

### Shared Utilities (`rhamaa/utils.py`)
- `download_github_repo(repo_url, branch, progress, task_id)` — converts GitHub URL to archive ZIP URL, streams download with Rich progress
- `extract_repo_to_apps(zip_path, app_name, progress, task_id)` — extracts ZIP, handles GitHub's nested root dir, moves to `apps/<name>/`
- `check_wagtail_project()` — checks for `manage.py`, `settings.py`, or common config files

### Template Registry (`rhamaa/templates/cms/`)
All data files accessed at runtime via `pkgutil.get_data('rhamaa.templates.cms', filename)` so they work from any install method:
- `project_template_list.json` — keys: `base`, `dev`, `inertia-react`, `iot` → GitHub repo + branch
- `app_list.json` — prebuilt apps: `mqtt` (IoT), `users` (Auth), `articles` (Content) → GitHub repo + branch
- `app_template_list.json` — app scaffold templates for `startapp --template`
- `APPS_TEMPLATES/minimal/` — bare Django app `.tpl` files
- `APPS_TEMPLATES/wagtail/` — Wagtail-extended app `.tpl` files (includes migrations, HTML templates, settings override)

## Data Flow

### Project Creation (`rhamaa cms start <name>`)
1. Load `project_template_list.json` via `pkgutil`
2. Resolve template key → GitHub ZIP URL (or accept `--template-url` / `--template-file` / `--local-dev`)
3. Delegate entirely to `subprocess.run(['wagtail', 'start', '--template=<url>', project_name])`

### Standard App Creation (`rhamaa cms startapp <name>`)
1. Validate app name is a Python identifier
2. **Minimal:** call `django-admin startapp <name> apps/<name>`; patch `apps.py` to set `name = 'apps.<name>'`
3. **Wagtail:** read `.tpl` files via `pkgutil`, render `{{var}}` placeholders, write to `apps/<name>/`
4. Call `auto_configure_app(app_name)` → `SettingsParser` edits `settings.py`, `URLParser` edits `urls.py`

### Prebuilt App Installation (`rhamaa cms startapp <name> --prebuild <key>`)
1. Look up key in `app_list.json` registry
2. Download GitHub archive ZIP via `utils.download_github_repo()` with Rich progress bar
3. Extract to `apps/<name>/` via `extract_repo_to_apps()`
4. `ManifestParser.find_manifest()` locates `rhamaa-app.json` inside the extracted directory
5. `AppManifest.from_file()` parses into typed dataclasses; `resolve_placeholders(app_name)` substitutes tokens
6. `ManifestApplier.apply_all()` runs the full pipeline: deps → conflicts → settings → URLs → post-install hooks

### Management Command Proxy (`rhamaa cms run/check/migrate/...`)
```
User invokes: rhamaa cms migrate
  → commands/cms/database.py: run_manage(['migrate'])
    → commands/cms/utils.py: subprocess.run(['python', 'manage.py', 'migrate'])
```

## Design Patterns

**Command Group Hierarchy (Click):**
```python
# rhamaa/cli.py
@click.group(invoke_without_command=True)
def main(ctx): ...

main.add_command(cms)  # only top-level subgroup

# rhamaa/commands/cms/__init__.py
@click.group()
def cms(): ...

cms.add_command(start)
cms.add_command(startapp)
# ... all other commands
```

**Manifest-Driven Plug-and-Play Installation:**
Prebuilt apps carry `rhamaa-app.json` describing all Django integration requirements. The CLI applies all changes automatically — no manual `settings.py` / `urls.py` editing required.

**`{{var}}` Template Rendering:**
`_render_template()` in `startapp.py` replaces `{{key}}` tokens in `.tpl` files with plain `str.replace()`. Intentionally avoids Jinja2 to keep the package lightweight.

**`pkgutil.get_data()` for Bundled Assets:**
All JSON registries and `.tpl` files use `pkgutil.get_data(package, resource)`. This is the correct pattern for data files inside installed Python packages — it works from wheel installs, egg installs, and editable installs equally.

**Subprocess Delegation:**
The CLI does not re-implement Django/Wagtail internals. It wraps external CLIs (`wagtail`, `django-admin`, `python manage.py`, `gunicorn`) via `subprocess.run(..., check=True)`.

## Key Architectural Decisions

**Single `cms` namespace:** All commands sit under `rhamaa cms`. The `commands/__init__.py` notes this was a deliberate namespace reorganization.

**Regex-based settings editing:** `config_utils.py` modifies `settings.py` and `urls.py` with regex rather than AST manipulation. Simpler, but fragile against unusual formatting.

**`apps/` subdirectory convention:** All installed apps are placed in `apps/<app_name>/`. `startapp` enforces this and patches `apps.py` to set `name = 'apps.<name>'`. RhamaaCLI expects/creates this structure in target projects.

**Dry-run and opt-in backup:** `startapp` and `ManifestApplier` support `--dry-run` (preview without writing) and `--backup` (write `.bak` files). Backup is disabled by default since `0.4.x`.

**Static JSON registries:** App and template registries are JSON files bundled with the package. Adding new prebuilt apps or project templates requires a new package release.

---

*Architecture analysis: 2026-04-10*
