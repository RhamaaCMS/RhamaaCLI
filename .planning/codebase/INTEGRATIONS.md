# Integrations - RhamaaCLI

## External Services

### GitHub Integration
**Purpose**: Download prebuilt apps from external repositories

**Implementation**: `rhamaa/utils.py`
- `download_github_repo(repo_url, branch)` - Downloads repos as ZIP files
- Converts GitHub URLs to ZIP download URLs (`{repo}/archive/refs/heads/{branch}.zip`)
- Streaming download with progress tracking via `requests.get(stream=True)`

**Prebuilt App Registry** (`rhamaa/templates/cms/app_list.json`):
| Key | Repository | Category |
|-----|------------|----------|
| `mqtt` | github.com/RhamaaCMS/rhamaa-mqtt | IoT |
| `users` | github.com/RhamaaCMS/rhamaa-users | Authentication |
| `articles` | github.com/RhamaaCMS/rhamaa-articles | Content |

### PyPI Distribution
**Purpose**: Package distribution and installation

**Configuration**: `pyproject.toml`
- Package name: `rhamaa`
- Entry point: `rhamaa = "rhamaa.cli:main"`
- Optional extras: `[cms]`, `[cv]`, `[dev]`

## Wagtail/Django Integration

### Project Template Sources
**Base Template**: RhamaaCMS main branch (production-ready)
**Dev Template**: RhamaaCMS dev branch (development)

**Registry**: `rhamaa/templates/cms/project_template_list.json`
- Supports custom `--template-url` (remote ZIP)
- Supports `--template-file` (local ZIP/directory)
- Supports `--local-dev` (local development path `../RhamaaCMS`)

### App Templates
**Location**: `rhamaa/templates/cms/APPS_TEMPLATES/`

| Type | Path | Description |
|------|------|-------------|
| `minimal` | `APPS_TEMPLATES/minimal/*.tpl` | Standard Django apps |
| `wagtail` | `APPS_TEMPLATES/wagtail/*.tpl` | Wagtail-specific apps |

Template files use `.tpl` extension with Jinja2-style placeholders:
- `{{app_name}}` - App name substitution
- `{{app_name|upper}}` - Uppercase app name
- `{{app_name|title}}` - Title case app name

## Internal Integrations

### CLI Structure
```
rhamaa (main entry)
└── cms (command group)
    ├── start (project creation)
    ├── startapp (app scaffolding)
    ├── build-template (template reverse-engineering)
    ├── run (server management)
    ├── migrate/makemigrations (database)
    ├── check/test/collectstatic/createsuperuser/shell/update_index (Django)
    └── status/info (project info)
```

### Utility Functions (`rhamaa/utils.py`)
- `check_wagtail_project()` - Validates Django/Wagtail project structure
- `download_github_repo()` - Downloads external app repositories
- `extract_repo_to_apps()` - Extracts ZIP to `apps/` directory
