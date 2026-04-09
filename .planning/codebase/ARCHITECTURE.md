# Architecture - RhamaaCLI

## Overview

RhamaaCLI is a layered CLI tool that accelerates Wagtail CMS development through:
1. **Project bootstrapping** from RhamaaCMS templates
2. **App scaffolding** with templates or prebuilt repositories
3. **Template reverse-engineering** for distribution
4. **Development workflow** commands

## Architectural Layers

```
┌─────────────────────────────────────────┐
│  CLI Layer (click + rich)               │
│  - Entry point: rhamaa.cli:main         │
│  - Command groups and help system       │
│  - Rich terminal UI (ASCII logo, tables)│
├─────────────────────────────────────────┤
│  Command Layer (rhamaa/commands/cms/)   │
│  - start.py: Project creation            │
│  - startapp.py: App scaffolding          │
│  - build.py: Template reverse-engineer │
│  - server.py: Dev/prod server          │
│  - database.py: Migration commands       │
│  - management.py: Django wrappers        │
│  - info.py: Project status/info          │
├─────────────────────────────────────────┤
│  Utility Layer (rhamaa/utils.py)        │
│  - GitHub repo downloading               │
│  - ZIP extraction to apps/               │
│  - Project validation                    │
├─────────────────────────────────────────┤
│  Template Layer (rhamaa/templates/)     │
│  - App templates (.tpl files)          │
│  - JSON registries                       │
└─────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Command Group Pattern (Click)
```python
@click.group()
def cms():
    """Manage RhamaaCMS development."""
    pass

cms.add_command(start)
cms.add_command(startapp)
# ... etc
```

### 2. Template Engine Pattern
App templates use `.tpl` files with placeholder substitution:
- `{{app_name}}` → actual app name
- Processed via string `.replace()` operations

### 3. Registry Pattern
JSON files define available templates and prebuilt apps:
- `project_template_list.json` - Project template sources
- `app_list.json` - Prebuilt app repositories

### 4. Wrapper Pattern
Django/Wagtail commands are thin wrappers around `manage.py`:
- `rhamaa cms migrate` → `python manage.py migrate`
- Adds project validation and Rich output

## Data Flow

### Project Creation Flow
```
User: rhamaa cms start MyProject
    ↓
CLI: Parse command, validate project name
    ↓
Template: Fetch from registry or custom URL/path
    ↓
Wagtail: Run `wagtail start --template=<source> MyProject`
    ↓
User: New project ready in ./MyProject/
```

### App Creation Flow
```
User: rhamaa cms startapp blog --type wagtail
    ↓
CLI: Validate in Wagtail project, check apps/ folder
    ↓
Template: Load .tpl files from APPS_TEMPLATES/wagtail/
    ↓
Process: Replace {{app_name}} placeholders
    ↓
Output: Write processed files to apps/blog/
```

### Prebuilt App Flow
```
User: rhamaa cms startapp devices --prebuild mqtt
    ↓
CLI: Look up 'mqtt' in app_list.json
    ↓
Download: GitHub repo → ZIP file (with progress)
    ↓
Extract: ZIP → apps/devices/ (with progress)
    ↓
User: App ready, add to INSTALLED_APPS
```

## Project Structure Conventions

RhamaaCLI expects/enforces these conventions:

```
Project/
├── manage.py              # Django entry point
├── apps/                  # Rhamaa convention: apps go here
│   ├── blog/
│   ├── articles/
│   └── ...
├── requirements.txt
└── pyproject.toml
```
