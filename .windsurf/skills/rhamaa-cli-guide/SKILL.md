---
name: rhamaa-cli-guide
description: |
  Guide users on how to use RhamaaCLI for Wagtail/Django development. 
  
  Use this skill when the user asks about:
  - How to use RhamaaCLI commands
  - Creating Wagtail/Django projects with RhamaaCLI
  - Installing prebuilt apps
  - Using app manifests (rhamaa-app.json)
  - Project templates (base, dev, inertia-react, iot)
  - Auto-configuration features
  - Troubleshooting RhamaaCLI issues
  - Best practices for RhamaaCLI workflows
  - CLI options and flags (--dry-run, --backup, --force, etc.)
  - Custom templates
  
  Covers all commands: rhamaa cms start, rhamaa cms startapp, rhamaa cms build-template, 
  rhamaa cms run, rhamaa cms migrate, and their options.
---

# RhamaaCLI User Guide

## Overview

RhamaaCLI accelerates Wagtail CMS development through:
- **Project scaffolding** - Create pre-configured Wagtail projects
- **App installation** - Install prebuilt or custom apps
- **Auto-configuration** - Automatic settings and URL configuration
- **Template system** - Support for custom project/app templates

## Quick Reference

### Essential Commands

```bash
# Create project
rhamaa cms start <project_name> [--template <key>]

# Create app
rhamaa cms startapp <app_name> [--type minimal|wagtail]

# Install prebuilt app
rhamaa cms startapp <name> --prebuild <key>

# Run server
rhamaa cms run [--prod]

# Run migrations
rhamaa cms migrate
```

### Common Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying |
| `--backup` | Create backup files before modification |
| `--force` / `-f` | Overwrite existing files |
| `--skip-config` | Skip auto-configuration |
| `--list` | List available items |

## Detailed Usage

### 1. Creating Projects

#### Basic Project
```bash
rhamaa cms start MyBlog
```

Creates a standard Wagtail project with:
- `apps/` directory for your apps
- Pre-configured settings structure
- Wagtail and Django setup

#### With Specific Template
```bash
# IoT-focused project
rhamaa cms start MyIoT --template iot

# React SPA project
rhamaa cms start MySPA --template inertia-react

# Latest development features
rhamaa cms start MyProject --template dev
```

**Available Templates:**
- `base` - Stable, production-ready (default)
- `dev` - Latest features, more experimental
- `inertia-react` - Wagtail + Inertia.js + React SPA
- `iot` - IoT with MQTT integration

#### From Custom Template
```bash
# From URL
rhamaa cms start MyProject --template-url https://example.com/template.zip

# From local file
rhamaa cms start MyProject --template-file ./my-template.zip
```

### 2. Creating Apps

#### Minimal Django App
```bash
rhamaa cms startapp blog
```

Creates a standard Django app with:
- models.py, views.py, admin.py
- urls.py
- apps.py (configured for `apps.blog`)
- migrations/

#### Wagtail App
```bash
rhamaa cms startapp blog --type wagtail
```

Creates a Wagtail app with:
- Page models
- Templates directory with sample templates
- Static files directory
- Management commands directory
- Initial migration

#### With Dry-Run (Preview)
```bash
rhamaa cms startapp blog --type wagtail --dry-run
```

Shows what would be created without actually creating files.

### 3. Installing Prebuilt Apps

#### List Available Apps
```bash
rhamaa cms startapp --list
```

**Current Prebuilt Apps:**
- `users` - User management system with auth
- `articles` - Article/blog system
- `mqtt` - MQTT device management for IoT

#### Install with Auto-Configuration
```bash
rhamaa cms startapp myusers --prebuild users
```

This will:
1. Download the users app from GitHub
2. Extract to `apps/myusers/`
3. **Auto-configure:**
   - Add to INSTALLED_APPS
   - Add URL patterns
   - Run migrations
   - Apply manifest configuration (if present)

#### Preview Before Installing
```bash
rhamaa cms startapp myusers --prebuild users --dry-run
```

Shows what changes would be made without applying them.

#### With Backup
```bash
rhamaa cms startapp myusers --prebuild users --backup
```

Creates `.bak` files before modifying settings.py and urls.py.

### 4. Template Management

#### Building Project Templates

If you've customized a project and want to reuse it:

```bash
# Build template from current directory
rhamaa cms build-template .

# With custom slug
rhamaa cms build-template . --slug my-custom-template

# Specify output
rhamaa cms build-template . --output my-template.zip
```

#### Using App Templates

```bash
# List available app templates
rhamaa cms startapp --list-templates

# Use specific template
rhamaa cms startapp api --template api
```

### 5. Development Server

#### Start Development Server
```bash
rhamaa cms run
```

Starts Django development server (equivalent to `python manage.py runserver`).

#### Production Mode
```bash
rhamaa cms run --prod
```

Starts with Gunicorn (requires gunicorn installed).

#### System Checks
```bash
rhamaa cms run --check
```

Runs Django system checks.

#### Project Status
```bash
rhamaa cms run --status
```

Shows project status information.

### 6. Database Management

#### Run All Migrations
```bash
rhamaa cms migrate
```

#### Migrations for Specific App
```bash
rhamaa cms migrate --app blog
```

#### Show Migration Plan
```bash
rhamaa cms migrate --plan
```

## App Manifest System

Apps can include a `rhamaa-app.json` manifest for full auto-configuration:

### Example Manifest Structure
```json
{
  "schema_version": "1.0.0",
  "name": "User Management",
  "slug": "users",
  "django": {
    "installed_apps": ["apps.{app_name}", "allauth"],
    "middleware": [
      {
        "class": "apps.{app_name}.middleware.ActivityMiddleware",
        "position": "after:django.contrib.sessions.middleware.SessionMiddleware"
      }
    ],
    "templates": {
      "dirs": ["apps/{app_name}/templates"],
      "context_processors": ["apps.{app_name}.context_processors.user_vars"]
    },
    "auth_backends": ["apps.{app_name}.backends.EmailBackend"],
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User",
      "LOGIN_URL": "/accounts/login/"
    }
  },
  "urls": [
    {
      "path": "accounts/",
      "include": "apps.{app_name}.urls",
      "namespace": "accounts"
    }
  ],
  "post_install": {
    "migrations": true,
    "fixtures": ["apps/{app_name}/fixtures/groups.json"],
    "messages": ["Configure email backend settings"]
  }
}
```

### Placeholders in Manifests

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `{app_name}` | `myusers` | The installed app name |
| `{app_class}` | `Myusers` | CamelCase version |
| `{app_upper}` | `MYUSERS` | Uppercase version |

## Workflows

### Complete Project Setup

```bash
# 1. Create project
rhamaa cms start MyBlog
cd MyBlog

# 2. Install apps
rhamaa cms startapp accounts --prebuild users
rhamaa cms startapp articles --prebuild articles

# 3. Run migrations
rhamaa cms migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start server
rhamaa cms run
```

### IoT Project Setup

```bash
# 1. Create IoT project
rhamaa cms start MyIoT --template iot
cd MyIoT

# 2. Install MQTT app
rhamaa cms startapp devices --prebuild mqtt

# 3. Configure MQTT (edit settings)
# Add MQTT_BROKER_HOST, MQTT_BROKER_PORT

# 4. Run migrations
rhamaa cms migrate

# 5. Start Celery (if needed)
celery -A MyIoT worker -l info

# 6. Start server
rhamaa cms run
```

### Safe App Installation (With Backup)

```bash
# Preview first
rhamaa cms startapp myusers --prebuild users --dry-run

# Install with backup
rhamaa cms startapp myusers --prebuild users --backup

# If something goes wrong, restore:
cp settings/base.py.bak settings/base.py
cp urls.py.bak urls.py
```

## Troubleshooting

### Command Not Found
```bash
# Ensure RhamaaCLI is installed
pip install "rhamaa[cms]"

# Check PATH
which rhamaa  # Linux/Mac
where rhamaa  # Windows
```

### App Not Found
```bash
# List available apps
rhamaa cms startapp --list
```

### Settings Not Applied
```bash
# Check if settings file exists
ls settings/base.py
ls settings.py

# Use --dry-run to debug
rhamaa cms startapp myapp --prebuild users --dry-run
```

### Migration Issues
```bash
# Reset database (careful!)
rm db.sqlite3
rhamaa cms migrate

# Or just for one app
python manage.py migrate blog zero
python manage.py migrate blog
```

## Best Practices

1. **Always use --dry-run first** on production projects
2. **Enable --backup** when experimenting
3. **Test in development** before production
4. **Use virtual environments**
5. **Keep .bak files** until confirming everything works
6. **Check conflicts** before installing multiple apps

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `RHAMAA_DEBUG` | Enable debug output |
| `DJANGO_SETTINGS_MODULE` | Django settings module |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Network error |
| 4 | Configuration error |
| 5 | App not found |

## Getting More Help

- **Documentation**: See `docs/` directory in the project
- **GitHub Issues**: https://github.com/RhamaaCMS/RhamaaCLI/issues
- **PyPI**: https://pypi.org/project/rhamaa/
