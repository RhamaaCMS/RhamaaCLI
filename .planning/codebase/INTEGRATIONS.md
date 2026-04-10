# External Integrations

**Analysis Date:** 2026-04-10

## Package Dependencies

**click >= 8.0.0**
- Purpose: CLI framework powering all commands and option parsing
- Used in: every file under `rhamaa/commands/cms/` and `rhamaa/cli.py`
- Installed by default

**rich >= 12.0.0**
- Purpose: All terminal output — panels, tables, progress spinners, styled text
- Used in: every command module; `Console`, `Panel`, `Table`, `Progress`, `SpinnerColumn`,
  `BarColumn`, `TaskProgressColumn`, `Text`, `Markdown`, `box`
- Installed by default

**requests >= 2.25.0**
- Purpose: Streaming HTTP download of GitHub repository ZIP archives
- Used in: `rhamaa/utils.py:download_github_repo()` (primary) and inline in
  `rhamaa/commands/cms/startapp.py:install_template_app()` for custom `--template-url` downloads
- Auth: none — only downloads from public GitHub URLs
- Installed by default

**gitpython >= 3.1.0**
- Listed in `requirements.txt` only; absent from `pyproject.toml` install_requires
- Not imported in any source file; likely leftover or reserved for future use

## System Integrations

**File System**
- All file operations use `pathlib.Path` and stdlib `shutil`, `zipfile`, `tempfile`
- Reads/writes files in the caller's current working directory (target Django project)
- Key paths manipulated at runtime:
  - `./apps/<app_name>/` — app installation target
  - `./manage.py` — presence check for Django project detection
  - `./settings.py` or `./<project>/settings/base.py` — auto-configured via regex in `rhamaa/config_utils.py`
  - `./<project>/urls.py` — URL patterns injected via regex in `rhamaa/config_utils.py`
  - `./dist/` — template ZIP output from `rhamaa/commands/cms/build.py`
- Backup files written as `<filename>.py.bak` when `--backup` flag is passed

**Subprocess / External CLI Tools**

All subprocess calls use `subprocess.run()` (no shell=True):

| Invoked Command | Triggered By | Source File |
|---|---|---|
| `wagtail start --template=<url> <name>` | `cms start` | `rhamaa/commands/cms/start.py` |
| `django-admin startapp <name> <dir>` | `cms startapp` (minimal type) | `rhamaa/commands/cms/startapp.py` |
| `python manage.py runserver <host:port>` | `cms run` | `rhamaa/commands/cms/server.py` via `utils.run_manage` |
| `gunicorn --bind <host:port> --workers 3 <wsgi>` | `cms run --prod` | `rhamaa/commands/cms/server.py` |
| `python manage.py migrate` | `cms migrate` and manifest post-install | `rhamaa/commands/cms/database.py`, `rhamaa/manifest_applier.py` |
| `python manage.py makemigrations [app]` | `cms makemigrations` and manifest post-install | `rhamaa/commands/cms/database.py`, `rhamaa/manifest_applier.py` |
| `python manage.py check` | `cms check` | `rhamaa/commands/cms/management.py` |
| `python manage.py test [app]` | `cms test` | `rhamaa/commands/cms/management.py` |
| `python manage.py collectstatic --noinput` | `cms collectstatic` | `rhamaa/commands/cms/management.py` |
| `python manage.py createsuperuser` | `cms createsuperuser` | `rhamaa/commands/cms/management.py` |
| `python manage.py shell` | `cms shell` | `rhamaa/commands/cms/management.py` |
| `python manage.py update_index` | `cms update_index` | `rhamaa/commands/cms/management.py` |
| `python manage.py loaddata <fixture>` | manifest post-install | `rhamaa/manifest_applier.py` |
| `python manage.py <custom_cmd>` | manifest post-install management_commands | `rhamaa/manifest_applier.py` |

`gunicorn` and `wagtail` must be independently installed by the user; the CLI prints a
helpful error if `FileNotFoundError` is raised.

**Package Data Reading**
- `pkgutil.get_data('rhamaa.templates.cms', '<file>.json')` — reads bundled JSON registries
  at runtime without needing to know install path; used in `start.py` and `startapp.py`

## External Services

**GitHub (api-less, raw download only)**
- No GitHub API calls; uses raw ZIP archive URLs only:
  `https://github.com/<org>/<repo>/archive/refs/heads/<branch>.zip`
- Triggered by: `cms start` (project templates), `cms startapp --prebuild` (prebuilt apps),
  `cms startapp --template-url` (custom template URLs)
- No authentication required; all repositories must be public
- Implementation: `rhamaa/utils.py:download_github_repo()`

**PyPI**
- RhamaaCLI itself is distributed on PyPI as `rhamaa`
- No PyPI API calls at runtime

## CLI Tools Invoked

**Required at runtime (not bundled):**
- `wagtail` — must be installed in the active Python environment; used by `cms start`
- `django-admin` — must be installed; used by `cms startapp` (minimal app type)
- `gunicorn` — must be installed; used by `cms run --prod`
- `python manage.py` — must exist in cwd; used by all `cms` database/management commands

**Auto-detected:**
- WSGI application module: `rhamaa/commands/cms/server.py:find_wsgi_application()` scans for
  `wsgi.py` one level deep and constructs `<project>.wsgi:application` automatically

## Webhooks & Callbacks

- None. RhamaaCLI is a purely local CLI tool; it makes outbound HTTP requests only for
  downloading templates and does not expose any inbound endpoints.

## Environment Configuration

**Required env vars for RhamaaCLI itself:** None

**Env vars managed in target Django projects (not by RhamaaCLI):**
- `DJANGO_SETTINGS_MODULE` — standard Django; must be set in the target project environment
- `SECRET_KEY` — `rhamaa/commands/cms/build.py` replaces hardcoded values with
  `{{ secret_key }}` template token when building redistributable templates

---

*Integration audit: 2026-04-10*
