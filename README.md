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

# List available apps
rhamaa cms startapp --list
```

## 🎯 CMS-Focused Commands

### `rhamaa cms start <project>`
Creates new Wagtail project using RhamaaCMS template.

### `rhamaa cms startapp <name>`
Creates Django apps or installs prebuilt apps:
- `--type minimal` - Standard Django app (default)
- `--type wagtail` - Wagtail app with models/templates
- `--prebuild <key>` - Install from registry
- `--list` - Show available prebuilt apps

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
cd MyBlog
rhamaa cms startapp articles --prebuild articles

# IoT dashboard
rhamaa cms start IoTDash
cd IoTDash
rhamaa cms startapp devices --prebuild mqtt

# Educational platform
rhamaa cms start EduSite
cd EduSite
rhamaa cms startapp courses --prebuild lms

# Build template kembali dari proyek lokal
rhamaa cms build-template .
```

## 🔧 After Installing Apps

1. Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'apps.your_app_name',
]
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Features

- **Rich Terminal UI** - Beautiful ASCII art and progress bars
- **Auto Directory Structure** - Apps created in `apps/` folder
- **GitHub Integration** - Downloads apps from repositories
- **Force Install** - Overwrite existing apps with `--force`
- **Project Detection** - Validates Wagtail project structure

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
