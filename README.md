# Rhamaa CLI

Simple CLI tool for Wagtail CMS development. Create projects and install prebuilt apps instantly.

## ⚡ Quick Start

```bash
# Basic install (CLI only)
pip install rhamaa

# With CMS support (includes Wagtail) - Recommended
pip install "rhamaa[cms]"

# With Computer Vision support
pip install "rhamaa[cv]"

# Create Wagtail project
rhamaa cms start MyProject
cd MyProject

# Create minimal Django app
rhamaa cms startapp blog

# Install prebuilt app
rhamaa cms startapp iot --prebuild mqtt

# Install prebuilt app from a custom GitHub repository
rhamaa cms startapp myiot --prebuild https://github.com/owner/repo --branch main

# List available apps
rhamaa cms startapp --list
```

## 🎯 CMS-Focused Commands

### `rhamaa cms start <project>`
Creates new Wagtail project using RhamaaCMS template.
- `--template-url <zip>` gunakan URL ZIP kustom
- `--template-file <path>` arahkan ke ZIP/direktori lokal
- `--local-dev` pakai template di `../RhamaaCMS`
- `--list` tampilkan katalog template registry

- `--prebuild <key|url>` - Install from registry or GitHub URL
- `--branch <branch>` - GitHub branch to download for custom repo installs
- `--dry-run` - Preview changes without applying
- `--backup/--no-backup` - Create backup files (default: false)
- `--skip-config` - Skip auto-configuration
- `--list` - Show available prebuilt apps

**Auto-Configuration Features:**
When creating apps, RhamaaCLI automatically:
1. Adds app to `INSTALLED_APPS` in settings
2. Wires up URLs in `urls.py`
3. Creates app `urls.py` if not exists
4. Creates `.bak` backup files before modification (use `--backup`)

**App Manifest System (rhamaa-app.json):**
Prebuilt apps can include a `rhamaa-app.json` manifest that defines:
- INSTALLED_APPS and dependencies
- Middleware configuration with positioning
- Template directories and context processors
- Authentication backends
- Custom Django settings
- URL patterns with namespaces
- Post-install tasks (migrations, fixtures, management commands)

This enables **plug-and-play installation**:
```bash
rhamaa cms startapp myusers --prebuild users
# Automatically configures everything from the manifest
```

### `rhamaa cms build-template [source]`
Konversi proyek RhamaaCMS hasil eksplorasi kembali menjadi template siap pakai:
- `--slug <name>` tentukan slug proyek asli (default: nama folder sumber)
- `--output <zip>` nama arsip output (disimpan di `dist/`)
- `--no-wrap-templates` lewati pembungkusan `{% verbatim %}` pada file HTML
- `--wrap-templates` aktif secara default untuk menjaga tag template saat di-render `wagtail start`

### `rhamaa cms run`
Development and production server management:
- `rhamaa cms run` - Start development server
- `rhamaa cms run --prod` - Start with Gunicorn
- `rhamaa cms check` - Run system checks
- `rhamaa cms status` - Show project status

## 📦 Available Project Templates

| Key | Name | Description |
|-----|------|-------------|
| `base` | RhamaaCMS Base | Stable production-ready template |
| `dev` | RhamaaCMS Dev | Development branch with latest features |
| `inertia-react` | RhamaaCMS Inertia + React | Wagtail with Inertia.js and React SPA |
| `iot` | RhamaaCMS IoT | IoT-focused with MQTT integration |

## 📦 Available Prebuilt Apps

| Key | Name | Category |
|-----|------|----------|
| `mqtt` | MQTT Apps | IoT |
| `users` | User Management | Authentication |
| `articles` | Article System | Content |

## 💡 Usage Examples

```bash
# Blog project
rhamaa cms start MyBlog
rhamaa cms startapp articles --prebuild articles

# IoT dashboard with IoT template
rhamaa cms start IoTDash --template iot
rhamaa cms startapp devices --prebuild mqtt

# Inertia + React SPA project
rhamaa cms start MySPA --template inertia-react
rhamaa cms startapp dashboard

# Custom template sources
rhamaa cms start MyLocal --template-file ./dist/rhamaacms-template.zip
rhamaa cms start Latest --template-url https://example.com/custom-template.zip

# Build template kembali dari proyek lokal
rhamaa cms build-template .

# List available options
rhamaa cms start --list
```

## 🔧 After Installing Apps (Manual Steps - Auto-Config Disabled)

If you use `--skip-config`, manually add:

1. Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'apps.your_app_name',
]
```

2. Add to project's `urls.py`:
```python
urlpatterns = [
    # ... existing patterns
    path('your_app/', include('apps.your_app_name.urls')),
]
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Features

- **Rich Terminal UI** - Beautiful ASCII art and progress bars
- **Auto Directory Structure** - Apps created in `apps/` folder
- **GitHub Integration** - Downloads apps from repositories
- **Auto-Configuration** - Automatically adds apps to settings and URLs
- **App Manifest System** - Plug-and-play app installation with full configuration
- **Template System** - ZIP-based templates for projects and apps
- **Dry-Run Mode** - Preview changes without applying
- **Backup Safety** - Creates `.bak` files before modifications (use `--backup`)
- **Conflict Detection** - Detects setting/URL conflicts before installation
- **Dependency Resolution** - Auto-installs app dependencies in correct order
- **Force Install** - Overwrite existing apps with `--force`

## 📋 Requirements

- Python 3.7+
- Django/Wagtail (for project creation)

## 🔗 Links

- [Documentation](https://rhamaacms.github.io/RhamaaCLI)
- [PyPI Package](https://pypi.org/project/rhamaa/)
- [GitHub Repository](https://github.com/RhamaaCMS/RhamaaCLI)
- [Issues & Support](https://github.com/RhamaaCMS/RhamaaCLI/issues)

---

Made with ❤️ by the [RhamaaCMS](https://github.com/RhamaaCMS) team
