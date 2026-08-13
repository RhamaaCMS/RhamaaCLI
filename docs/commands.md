# Command Reference

Complete reference for all RhamaaCLI commands.

## Global Options

All commands support these global options:

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version information |

## Command Groups

- [`rhamaa cms`](#rhamaa-cms) - CMS-related commands
- [`rhamaa cv`](#rhamaa-cv) - Computer vision commands (optional)

---

## `rhamaa cms`

CMS-focused commands for Wagtail/Django development.

### `rhamaa cms start`

Create a new Wagtail project from template.

**Usage:**
```bash
rhamaa cms start <project_name> [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `project_name` | Name of the project to create |

**Options:**
| Option | Description |
|--------|-------------|
| `--template <key>` | Use template from registry (base, dev, inertia-react, iot) |
| `--template-url <url>` | Custom template ZIP URL |
| `--template-file <path>` | Local template ZIP or directory |
| `--local-dev` | Use template from `../RhamaaCMS` |
| `--list` | List available templates |
| `--force` | Overwrite existing directory |

**Examples:**
```bash
# Create project with default template
rhamaa cms start MyBlog

# Create with specific template
rhamaa cms start MyShop --template iot

# Create from custom URL
rhamaa cms start MyProject --template-url https://example.com/template.zip

# List available templates
rhamaa cms start --list
```

**Available Templates:**
| Template | Description |
|----------|-------------|
| `base` | Stable production-ready template |
| `dev` | Development branch with latest features |
| `inertia-react` | Wagtail with Inertia.js and React SPA |
| `iot` | IoT-focused with MQTT integration |

---

### `rhamaa cms startapp`

Create a new Django app or install prebuilt app.

**Usage:**
```bash
rhamaa cms startapp <app_name> [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `app_name` | Name of the app to create/install |

**Options:**
| Option | Description |
|--------|-------------|
| `--type <type>` | App template type: `minimal` or `wagtail` (default: minimal) |
| `--prebuild <key|url>` | Install prebuilt app from registry or GitHub repo URL |
| `--dry-run` | Preview changes without applying |
| `--backup` | Create backup of modified files |
| `--no-backup` | Don't create backup (default) |
| `--skip-config` | Skip auto-configuration |
| `--list` | List available prebuilt apps |
| `--force` / `-f` | Overwrite existing app |

**Examples:**
```bash
# Create minimal Django app
rhamaa cms startapp blog

# Create Wagtail app
rhamaa cms startapp blog --type wagtail

### `rhamaa cms startapp`
```bash
# Install prebuilt app from registry
rhamaa cms startapp myusers --prebuild users

# Install prebuilt app from GitHub repository
rhamaa cms startapp myiot --prebuild https://github.com/owner/repo --branch main
```

# Preview installation
rhamaa cms startapp myusers --prebuild users --dry-run

# Install with backup
rhamaa cms startapp myusers --prebuild users --backup

# List available apps
rhamaa cms startapp --list
```

**Notes:**
- Standard apps created with `--type minimal|wagtail` also generate a default `apps/<app_name>/rhamaa-app.json` manifest for RhamaaCMS standardization.

**Available Prebuilt Apps:**
| App | Category | Description |
|-----|----------|-------------|
| `iot` | IoT | Connected-device extension for `base-iot` |
| `users` | Authentication | User management system |
| `articles` | Content | Article/blog system |

---

### `rhamaa cms apps`

Inspect and update registered apps using current-only releases.

```bash
rhamaa cms apps status
rhamaa cms apps update iot
rhamaa cms apps update --all
rhamaa cms apps update iot --dry-run
rhamaa cms apps update iot --reinstall
```

`update` intentionally has no version or branch option. Registry `version` and
downloaded `rhamaa-app.json` must match. Code backup is always created in
`.rhamaa/backups/apps/<package>/` before full replacement.

If migrations fail, CLI keeps new code and backup because database changes may
already be partially applied. Review migration state before manual restoration.

---

### `rhamaa cms build-template`

Convert a RhamaaCMS project back into a reusable template.

**Usage:**
```bash
rhamaa cms build-template [source] [OPTIONS]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `source` | Source directory (default: current directory) |

**Options:**
| Option | Description |
|--------|-------------|
| `--slug <name>` | Project slug (default: directory name) |
| `--output <zip>` | Output ZIP filename |
| `--no-wrap-templates` | Skip wrapping HTML templates with verbatim |
| `--wrap-templates` | Enable template wrapping (default) |

**Examples:**
```bash
# Build template from current project
rhamaa cms build-template .

# Build with custom slug
rhamaa cms build-template . --slug my-custom-project

# Specify output
rhamaa cms build-template . --output my-template.zip
```

---

### `rhamaa cms run`

Development and production server management.

**Usage:**
```bash
rhamaa cms run [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--prod` | Run with Gunicorn (production) |
| `--check` | Run system checks |
| `--status` | Show project status |

**Examples:**
```bash
# Start development server
rhamaa cms run

# Start production server
rhamaa cms run --prod

# Run system checks
rhamaa cms run --check

# Show project status
rhamaa cms run --status
```

---

### `rhamaa cms migrate`

Run Django migrations.

**Usage:**
```bash
rhamaa cms migrate [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--app <name>` | Run migrations for specific app |
| `--fake` | Mark migrations as run without applying |
| `--plan` | Show migration plan without running |

**Examples:**
```bash
# Run all migrations
rhamaa cms migrate

# Run migrations for specific app
rhamaa cms migrate --app blog

# Show migration plan
rhamaa cms migrate --plan
```

---

## Command Workflows

### Creating a New Project

```bash
# 1. Create project
rhamaa cms start MyProject

# 2. Navigate to project
cd MyProject

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
rhamaa cms migrate

# 5. Start development server
rhamaa cms run
```

### Installing Multiple Apps

```bash
# Install users app with manifest
rhamaa cms startapp myusers --prebuild users

# Install blog app
rhamaa cms startapp blog --type wagtail

# Install IoT domain extension (package name is case-sensitive)
rhamaa cms startapp IoT --prebuild iot

# Run migrations for all
rhamaa cms migrate
```

---

## Environment Variables

RhamaaCLI respects these environment variables:

| Variable | Description |
|----------|-------------|
| `RHAMAA_DEBUG` | Enable debug mode (set to `1` or `true`) |
| `RHAMAA_REGISTRY_URL` | Custom app registry URL |
| `DJANGO_SETTINGS_MODULE` | Django settings module |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Network error (download failed) |
| `4` | Configuration error |
| `5` | App not found in registry |
