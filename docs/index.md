# RhamaaCLI Documentation

> Accelerate Wagtail CMS development with powerful CLI tools

## Overview

RhamaaCLI is a command-line interface tool designed to accelerate development with Wagtail CMS and Django. It provides project scaffolding, app installation, template management, and automatic configuration.

## Quick Start

```bash
# Install RhamaaCLI
pip install "rhamaa[cms]"

# Create a new Wagtail project
rhamaa cms start MyProject

# Navigate to project
cd MyProject

# Create a new app
rhamaa cms startapp blog

# Install a prebuilt app
rhamaa cms startapp users --prebuild users
```

## Features

- **🚀 Project Templates** - Start with pre-configured templates (base, dev, inertia-react, iot)
- **📦 Prebuilt Apps** - Install ready-to-use apps from registry
- **⚙️ Auto-Configuration** - Automatic settings and URL configuration
- **📋 App Manifest System** - Plug-and-play app installation with full configuration
- **🔧 Template System** - Support for custom ZIP-based project templates
- **🛡️ Conflict Detection** - Detect configuration conflicts before installation
- **📊 Dependency Resolution** - Auto-install app dependencies
- **🎯 Dry-Run Mode** - Preview changes without applying

## Documentation Sections

| Section | Description |
|---------|-------------|
| [Commands](commands.md) | Complete CLI command reference |
| [App Manifest](manifest.md) | rhamaa-app.json manifest system |
| [Templates](templates.md) | Project templates |
| [Configuration](configuration.md) | Auto-configuration system |
| [API Reference](api.md) | Python API documentation |
| [Examples](examples.md) | Usage examples |
| [Skills](skills/rhamaa-app-builder.md) | Internal docs: manifest → app builder workflow |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

## System Requirements

- **Python**: 3.7 or higher
- **Django**: 3.2 or higher (for project creation)
- **Wagtail**: 5.0 or higher (for CMS features)

## Installation

### Basic Installation (CLI only)
```bash
pip install rhamaa
```

### With CMS Support (Recommended)
```bash
pip install "rhamaa[cms]"
```

### With Computer Vision Support
```bash
pip install "rhamaa[cv]"
```

### Development Installation
```bash
git clone https://github.com/RhamaaCMS/RhamaaCLI.git
cd RhamaaCLI
pip install -e ".[dev]"
```

## Getting Help

- **Documentation**: https://rhamaacms.github.io/RhamaaCLI
- **GitHub Issues**: https://github.com/RhamaaCMS/RhamaaCLI/issues
- **PyPI**: https://pypi.org/project/rhamaa/

## Next Steps

1. Read [Commands Reference](commands.md) to learn available commands
2. Check [Examples](examples.md) for common workflows
3. Learn about [App Manifest](manifest.md) for creating prebuilt apps

---

**Made with ❤️ by the [RhamaaCMS](https://github.com/RhamaaCMS) team**
