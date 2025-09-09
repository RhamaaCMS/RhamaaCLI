# Rhamaa CLI

Simple CLI tool for Wagtail CMS development. Create projects and install prebuilt apps instantly.

## ⚡ Quick Start

```bash
# Install
pip install rhamaa

# Create Wagtail project
rhamaa start MyProject
cd MyProject

# Create minimal Django app
rhamaa startapp blog

# Install prebuilt app
rhamaa startapp iot --prebuild mqtt

# List available apps
rhamaa startapp --list
```

## 🎯 Two Simple Commands

### `rhamaa start <project>`
Creates new Wagtail project using RhamaaCMS template.

### `rhamaa startapp <name>`
Creates Django apps or installs prebuilt apps:
- `--type minimal` - Standard Django app (default)
- `--type wagtail` - Wagtail app with models/templates
- `--prebuild <key>` - Install from registry
- `--list` - Show available prebuilt apps

## 📦 Available Prebuilt Apps

| Key | Name | Category |
|-----|------|----------|
| `mqtt` | MQTT Apps | IoT |
| `users` | User Management | Authentication |
| `articles` | Article System | Content |

## 💡 Usage Examples

```bash
# Blog project
rhamaa start MyBlog
cd MyBlog
rhamaa startapp articles --prebuild articles

# IoT dashboard
rhamaa start IoTDash
cd IoTDash
rhamaa startapp devices --prebuild mqtt

# Educational platform
rhamaa start EduSite
cd EduSite
rhamaa startapp courses --prebuild lms
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
