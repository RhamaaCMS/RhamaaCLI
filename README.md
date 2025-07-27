# Rhamaa CLI

A powerful CLI tool to accelerate Wagtail web development with prebuilt applications and project scaffolding.

## 🚀 Features

### Project Management
- **Project Creation**: Generate new Wagtail projects using RhamaaCMS template
- **App Registry System**: Centralized registry of prebuilt applications
- **Auto Installation**: Download and install apps directly from GitHub repositories

### App Management
- **Prebuilt Apps**: Ready-to-use applications for common use cases
- **Auto Download**: Automatically download apps from GitHub repositories
- **Smart Extraction**: Extract and organize files to proper project structure
- **Force Install**: Overwrite existing apps when needed

### Developer Experience
- **Rich Terminal UI**: Beautiful ASCII art branding and colored output
- **Progress Indicators**: Real-time download and installation progress
- **Error Handling**: Comprehensive error messages and troubleshooting
- **Project Validation**: Automatic detection of Wagtail projects

## 📦 Available Apps

| App Name | Category | Description | Repository |
|----------|----------|-------------|------------|
| **mqtt** | IoT | MQTT integration for Wagtail with real-time messaging | [mqtt-apps](https://github.com/RhamaaCMS/mqtt-apps) |
| **users** | Authentication | Advanced user management system | [users-app](https://github.com/RhamaaCMS/users-app) |
| **articles** | Content | Blog and article management system | [articles-app](https://github.com/RhamaaCMS/articles-app) |
| **lms** | Education | Complete Learning Management System | [lms-app](https://github.com/RhamaaCMS/lms-app) |

## 🛠 Installation

### From PyPI (Beta)
```bash
# Install the latest beta version
pip install rhamaa==0.1.0b1

# Or install the latest pre-release
pip install --pre rhamaa
```

### Development Setup
```bash
# Clone the repository
git clone https://github.com/RhamaaCMS/RhamaaCLI.git
cd RhamaaCLI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .
```

## 📖 Usage

### Basic Commands
```bash
# Show help and available commands
rhamaa

# Create a new Wagtail project
rhamaa start MyProject

# List available apps
rhamaa add --list
rhamaa registry list

# Install an app
rhamaa add mqtt

# Get app information
rhamaa registry info mqtt

# Force install (overwrite existing)
rhamaa add mqtt --force
```

### App Installation Workflow
1. **Check Available Apps**: `rhamaa add --list`
2. **Install App**: `rhamaa add <app_name>`
3. **Follow Instructions**: Add to INSTALLED_APPS and run migrations
4. **Configure**: Check app's README for additional setup

### Registry Management
```bash
# List all apps by category
rhamaa registry list

# Get detailed app information
rhamaa registry info <app_name>

# Update registry (coming soon)
rhamaa registry update
```

## 🏗 Project Structure

```
rhamaa/
├── __init__.py             # Package initialization
├── cli.py                  # Main CLI entry point and help system
├── registry.py             # App registry management
├── utils.py                # Utility functions (download, extract)
└── commands/               # Command modules directory
    ├── __init__.py         # Commands package init
    ├── add.py              # 'add' command implementation
    ├── start.py            # 'start' command implementation
    └── registry.py         # 'registry' command implementation
```

## 🔧 Development

### Adding New Apps to Registry
Edit `rhamaa/registry.py`:
```python
APP_REGISTRY = {
    "your_app": {
        "name": "Your App Name",
        "description": "App description",
        "repository": "https://github.com/RhamaaCMS/your-app",
        "branch": "main",
        "category": "Category"
    }
}
```

### Testing Commands
```bash
# Test main command
rhamaa

# Test project creation
rhamaa start TestProject

# Test app installation
rhamaa add mqtt

# Test registry commands
rhamaa registry list
rhamaa registry info mqtt
```

### Building Distribution
```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/rhamaa-*.whl
```

## 🎯 Use Cases

### For Wagtail Developers
- Quickly bootstrap new projects with proven architecture
- Add common functionality without writing from scratch
- Standardize project structure across team

### For Teams
- Consistent project setup across developers
- Reusable components and applications
- Faster development cycles

### For IoT Projects
- MQTT integration with `rhamaa add mqtt`
- Real-time data monitoring and management
- Wagtail admin integration for IoT devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the RhamaaCMS ecosystem.

## 🔗 Links

- **Documentation**: [GitHub Wiki](https://github.com/RhamaaCMS/RhamaaCLI/wiki)
- **Issues**: [GitHub Issues](https://github.com/RhamaaCMS/RhamaaCLI/issues)
- **RhamaaCMS**: [Main Repository](https://github.com/RhamaaCMS)

---

Made with ❤️ by the RhamaaCMS team
