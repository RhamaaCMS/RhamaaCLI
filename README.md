# Rhamaa CLI

A powerful CLI tool to accelerate Wagtail web development with prebuilt applications, project templates, and modern tooling.

## 🚀 Features

### 🎯 Project Creation
- **Template System**: Choose from multiple project templates (default, blog, e-commerce, portfolio, etc.)
- **Current Directory Support**: Create projects in existing directories with `rhamaa start MyProject .`
- **Development Mode**: Use local templates for development with `--dev` flag
- **Built-in Design System**: Every project includes RHAMAA Global Design System

### 📦 App Registry System
- **Prebuilt Apps**: Ready-to-use applications for common use cases
- **Auto Installation**: Download and install apps directly from GitHub repositories
- **Smart Extraction**: Extract and organize files to proper project structure
- **Force Install**: Overwrite existing apps when needed

### 🎨 Modern Frontend Stack
Every project includes:
- **RHAMAA Global Design System** - CSS Custom Properties with `--g` prefix
- **Tailwind CSS + SCSS** - Modern styling architecture
- **Preline UI Components** - Pre-built interactive components
- **Dark Mode Support** - Built-in theme switching
- **Responsive Design** - Mobile-first approach
- **Modern Build System** - esbuild for fast compilation

### 🎭 Developer Experience
- **Rich Terminal UI**: Beautiful ASCII art branding and colored output
- **Progress Indicators**: Real-time download and installation progress
- **Error Handling**: Comprehensive error messages and troubleshooting
- **Project Validation**: Automatic detection of Wagtail projects

## 📋 Available Templates

| Template | Category | Description | Features |
|----------|----------|-------------|----------|
| **default** | Standard | RhamaaCMS with full design system | Design system, Tailwind, Preline UI, Dark mode |
| **minimal** | Standard | Basic Wagtail setup | Essential pages only, minimal styling |
| **blog** | Content | Blog-focused template | Article system, SEO optimized, social sharing |
| **ecommerce** | E-commerce | Shop-ready template | Product catalog, cart, payment integration |
| **portfolio** | Creative | Designer/developer portfolio | Project showcase, galleries, testimonials |
| **corporate** | Business | Professional website | Team pages, services, case studies |
| **iot** | IoT | IoT dashboard template | MQTT integration, real-time dashboards |
| **education** | Education | Educational institution | Course management, student portal, LMS |

## 📦 Available Apps

| App Name | Category | Description | Repository |
|----------|----------|-------------|------------|
| **mqtt** | IoT | MQTT integration for Wagtail with real-time messaging | [mqtt-apps](https://github.com/RhamaaCMS/mqtt-apps) |
| **users** | Authentication | Advanced user management system | [users-app](https://github.com/RhamaaCMS/users-app) |
| **articles** | Content | Blog and article management system | [articles-app](https://github.com/RhamaaCMS/articles-app) |
| **lms** | Education | Complete Learning Management System | [lms-app](https://github.com/RhamaaCMS/lms-app) |

## 🛠 Installation

### From PyPI (Recommended)
```bash
# Install the latest version (includes Wagtail)
pip install rhamaa
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

### Project Creation
```bash
# Show help and available commands
rhamaa

# Create a new project with default template
rhamaa start MyProject

# Create project with specific template
rhamaa start MyBlog --template blog
rhamaa start MyShop --template ecommerce
rhamaa start MyPortfolio --template portfolio

# Create project in current directory
rhamaa start MyProject .

# List available templates
rhamaa start --list-templates

# Use local template for development
rhamaa start MyProject --dev
```

### App Management
```bash
# List available apps
rhamaa add --list
rhamaa registry list

# Install an app
rhamaa add mqtt
rhamaa add users
rhamaa add articles

# Get app information
rhamaa registry info mqtt

# Force install (overwrite existing)
rhamaa add mqtt --force
```

### Registry Commands
```bash
# List all apps by category
rhamaa registry list

# List all templates
rhamaa registry templates

# Get detailed app information
rhamaa registry info <app_name>

# Get detailed template information
rhamaa registry template <template_name>
```

### Complete Project Setup
```bash
# 1. Create project
rhamaa start MyBlog --template blog

# 2. Setup environment
cd MyBlog
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Setup frontend
cd node && npm install && cd ..

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser

# 5. Build assets
cd node && npm run build && cd ..

# 6. Start development
python manage.py runserver
```

### Development Workflow
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Asset watching (in node directory)
cd node && npm run watch
```

## 🏗 Project Structure

### CLI Structure
```
rhamaa/
├── __init__.py             # Package initialization
├── cli.py                  # Main CLI entry point and help system
├── registry/               # Registry modules
│   ├── __init__.py         # Registry exports
│   ├── app.py              # App registry management
│   └── template.py         # Template registry management
├── utils.py                # Utility functions (download, extract)
└── commands/               # Command modules directory
    ├── __init__.py         # Commands package init
    ├── add.py              # 'add' command implementation
    ├── start.py            # 'start' command implementation
    └── registry.py         # 'registry' command implementation
```

### Generated Project Structure
```
MyProject/
├── MyProject/              # Django project settings
├── apps/                   # Custom Django apps
├── node/                   # Frontend build tools
├── static_src/             # Source assets (SCSS, JS)
├── static_compiled/        # Compiled assets
├── templates/              # Django templates with components
├── media/                  # User uploads
└── requirements.txt        # Python dependencies
```

## 🎨 Design System

Every project includes the RHAMAA Global Design System:

### CSS Architecture
- **CSS Custom Properties** with `--g` prefix for global design tokens
- **Modular SCSS** architecture with variables, components, and utilities
- **Tailwind CSS** integration for utility-first styling
- **Component Library** with consistent styling patterns

### Built-in Components
- **Buttons** - Primary, outline, critical variants
- **Forms** - Inputs, selects, textareas with validation states
- **Layout** - Containers, sections, panels, cards
- **Navigation** - Headers, footers, breadcrumbs
- **Typography** - Headings, body text, captions with proper hierarchy

### Theme System
- **Dark Mode** - Built-in theme switching with Preline UI
- **Custom Themes** - Easy theme creation with CSS custom properties
- **Responsive Design** - Mobile-first approach with consistent breakpoints

## 🔧 Development

### Adding New Templates
Edit `rhamaa/registry/template.py`:
```python
TEMPLATE_REGISTRY = {
    "your_template": {
        "name": "Your Template Name",
        "description": "Template description",
        "repository": "https://github.com/RhamaaCMS/your-template/archive/main.zip",
        "category": "Category",
        "features": [
            "Feature 1",
            "Feature 2"
        ]
    }
}
```

### Adding New Apps
Edit `rhamaa/registry/app.py`:
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
rhamaa start TestBlog --template blog

# Test app installation
rhamaa add mqtt

# Test registry commands
rhamaa registry list
rhamaa registry templates
rhamaa registry info mqtt
rhamaa registry template blog
```

### Building Distribution
```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/rhamaa-*.whl

# Upload to PyPI
twine upload dist/*
```

## 🎯 Use Cases

### For Individual Developers
- **Quick Prototyping**: Bootstrap projects with modern tooling in seconds
- **Design System**: Consistent styling without starting from scratch
- **Template Variety**: Choose the right template for your project type

### For Development Teams
- **Standardization**: Consistent project structure across team members
- **Reusable Components**: Share apps and templates across projects
- **Modern Workflow**: Built-in asset pipeline and development tools

### For Agencies
- **Client Projects**: Quick setup for different project types
- **Brand Consistency**: Customize design system for client branding
- **Scalable Architecture**: Add functionality with prebuilt apps

### For IoT Projects
- **MQTT Integration**: Real-time device communication with `rhamaa add mqtt`
- **Dashboard Templates**: IoT-specific templates with data visualization
- **Device Management**: Wagtail admin integration for IoT devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Update tests for new features
- Update documentation for user-facing changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [RhamaaCLI Docs](https://rhamaacms.github.io/RhamaaCLI/)
- **Issues**: [GitHub Issues](https://github.com/RhamaaCMS/RhamaaCLI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RhamaaCMS/RhamaaCLI/discussions)
- **RhamaaCMS**: [Main Repository](https://github.com/RhamaaCMS/RhamaaCMS)
- **PyPI**: [Package Page](https://pypi.org/project/rhamaa/)

## 🙏 Acknowledgments

- **Wagtail CMS** - The amazing CMS framework that powers RhamaaCMS
- **Rich** - Beautiful terminal formatting library
- **Click** - Elegant command-line interface framework
- **Tailwind CSS** - Utility-first CSS framework
- **Preline UI** - Beautiful UI components

---

Made with ❤️ by the RhamaaCMS team

**Ready to accelerate your Wagtail development?** 🚀

```bash
pip install rhamaa
rhamaa start MyProject
```