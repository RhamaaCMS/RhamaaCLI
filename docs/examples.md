# Usage Examples

Practical examples of common RhamaaCLI workflows.

## Table of Contents

1. [Basic Workflows](#basic-workflows)
2. [Project Creation](#project-creation)
3. [App Development](#app-development)
4. [Prebuilt Apps](#prebuilt-apps)
5. [API Usage](#api-usage)
6. [Advanced Scenarios](#advanced-scenarios)

---

## Basic Workflows

### Creating Your First Project

```bash
# Install RhamaaCLI
pip install "rhamaa[cms]"

# Create a new project
rhamaa cms start MyBlog

# Navigate to project
cd MyBlog

# Install dependencies
pip install -r requirements.txt

# Run migrations
rhamaa cms migrate

# Start development server
rhamaa cms run
```

### Project Structure After Creation

```
MyBlog/
├── apps/                  # Your apps will go here
├── manage.py
├── requirements.txt
├── db.sqlite3
└── MyBlog/               # Project settings
    ├── __init__.py
    ├── settings/
    │   ├── base.py
    │   ├── dev.py
    │   └── production.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

---

## Project Creation

### Different Project Types

```bash
# Standard blog/site (base template)
rhamaa cms start MyBlog

# With latest features (dev template)
rhamaa cms start MyExperimental --template dev

# SPA with React (inertia-react template)
rhamaa cms start MySPA --template inertia-react

# IoT project (iot template)
rhamaa cms start MyIoT --template iot
```

### Custom Project from URL

```bash
# From GitHub release
rhamaa cms start MyProject --template-url https://github.com/user/repo/releases/download/v1.0/template.zip

# From direct URL
rhamaa cms start MyProject --template-url https://example.com/my-template.zip
```

### Using Local Template

```bash
# From local ZIP
rhamaa cms start MyProject --template-file ./my-custom-template.zip

# From local directory
rhamaa cms start MyProject --template-file ./path/to/template/
```

---

## App Development

### Creating Apps

```bash
# Minimal Django app
rhamaa cms startapp blog

# Wagtail app with templates
rhamaa cms startapp blog --type wagtail

# Preview what will be created
rhamaa cms startapp blog --type wagtail --dry-run
```

### Standard App Manifest (`rhamaa-app.json`)

When you create a standard app (`--type minimal|wagtail`), RhamaaCLI also creates:

- `apps/<app_name>/rhamaa-app.json`

This standardizes local apps to the same manifest format used by prebuilt apps, so your app can be promoted into a prebuilt app later without changing formats.

### App Structure

**Minimal app (`--type minimal`):**
```
apps/blog/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

**Wagtail app (`--type wagtail`):**
```
apps/blog/
├── __init__.py
├── admin.py
├── apps.py
├── management/
│   ├── __init__.py
│   └── commands/
│       └── __init__.py
├── migrations/
│   └── __init__.py
├── models.py
├── static/
├── templates/
│   └── blog/
│       ├── example_page.html
│       └── index.html
├── tests.py
├── urls.py
└── views.py
```

### Multiple Apps Workflow

```bash
# Create project
cd MyBlog

# Create blog app
rhamaa cms startapp blog --type wagtail

# Create comments app
rhamaa cms startapp comments --type minimal

# Create newsletter app
rhamaa cms startapp newsletter --type wagtail

# Run migrations for all
rhamaa cms migrate

# Start server
rhamaa cms run
```

---

## Prebuilt Apps

### Installing Prebuilt Apps

```bash
# List available apps
rhamaa cms startapp --list

# Install users app
rhamaa cms startapp myusers --prebuild users

# Preview installation
rhamaa cms startapp myusers --prebuild users --dry-run

# Install with backup
rhamaa cms startapp myusers --prebuild users --backup
```

### Users + Articles Combo

```bash
# Create base project
rhamaa cms start MyContentSite
cd MyContentSite

# Install users system
rhamaa cms startapp accounts --prebuild users

# Install articles system
rhamaa cms startapp articles --prebuild articles

# Run migrations
rhamaa cms migrate

# Create superuser
python manage.py createsuperuser

# Start server
rhamaa cms run
```

### IoT Project Setup

```bash
# Create IoT project
rhamaa cms start MyIoT --template iot
cd MyIoT

# Install MQTT app
rhamaa cms startapp devices --prebuild mqtt

# Configure MQTT (edit settings)
# Add: MQTT_BROKER_HOST, MQTT_BROKER_PORT, etc.

# Run migrations
rhamaa cms migrate

# Start Celery (if using)
celery -A MyIoT worker -l info

# Start development server
rhamaa cms run
```

---
## API Usage

### Programmatic App Installation

```python
# install_app.py
from rhamaa.manifest_applier import install_app_with_manifest

result = install_app_with_manifest(
    app_name="myusers",
    prebuild_key="users",
    force=False,
    dry_run=False,
    backup=True,
    resolve_deps=True,
    ignore_conflicts=False
)

if result.success:
    print("✓ Installation successful!")
    for change in result.changes:
        print(f"  {change}")
else:
    print("✗ Installation failed:")
    for error in result.errors:
        print(f"  {error}")
```

### Custom Configuration Script

```python
# configure_project.py
from pathlib import Path
from rhamaa.config_utils import SettingsParser, URLParser

# Modify settings
settings = SettingsParser(Path("settings/base.py"))

# Add multiple apps
apps = ["apps.blog", "apps.comments", "apps.newsletter"]
for app in apps:
    if settings.add_installed_app(app):
        print(f"Added: {app}")

# Add custom settings
settings.set_setting("SITE_NAME", "My Blog")
settings.set_setting("POSTS_PER_PAGE", 10)
settings.set_setting("ENABLE_COMMENTS", True)

# Add middleware
settings.add_middleware(
    "blog.middleware.AnalyticsMiddleware",
    position="after:django.contrib.sessions.middleware.SessionMiddleware"
)

# Save changes
settings.write(backup=True)

# Modify URLs
urls = URLParser(Path("urls.py"))
urls.add_url_config({
    "path": "blog/",
    "include": "apps.blog.urls",
    "namespace": "blog"
})
urls.write(backup=True)

print("✓ Configuration complete!")
```

### Manifest Validation

```python
# validate_manifest.py
import json
import sys
from rhamaa.manifest import AppManifest

def validate(manifest_path):
    try:
        with open(manifest_path) as f:
            data = json.load(f)
        
        manifest = AppManifest.from_dict(data)
        errors = manifest.validate()
        
        if errors:
            print(f"❌ Validation failed for {manifest_path}:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print(f"✅ {manifest_path} is valid")
            return True
            
    except FileNotFoundError:
        print(f"❌ File not found: {manifest_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {manifest_path}: {e}")
        return False

# Validate multiple manifests
manifests = [
    "rhamaa-app.json",
    "apps/myapp/rhamaa-app.json"
]

results = [validate(m) for m in manifests]
sys.exit(0 if all(results) else 1)
```

### Dependency Resolution

```python
# check_dependencies.py
from rhamaa.dependency_resolver import DependencyResolver

# Define app registry
registry = {
    "articles": {
        "dependencies": {"apps": ["users", "categories", "tags"]}
    },
    "users": {
        "dependencies": {"apps": []}
    },
    "categories": {
        "dependencies": {"apps": []}
    },
    "tags": {
        "dependencies": {"apps": []}
    }
}

# Check dependencies
resolver = DependencyResolver(registry, installed_apps=[])

# Check specific app
target = "articles"
missing = resolver.get_missing_dependencies(target)
print(f"Missing for {target}: {missing}")

# Get installation order
order = resolver.resolve_dependencies(target)
print(f"Install order: {order}")

# Check if installable
is_ok, reason = resolver.is_installable(target)
print(f"Can install {target}: {is_ok} ({reason})")

# Check for circular dependencies
cycle = resolver.check_circular_dependencies()
if cycle:
    print(f"⚠️  Circular dependency: {' -> '.join(cycle)}")
else:
    print("✅ No circular dependencies")
```

---

## Advanced Scenarios

### Multi-Environment Setup

```bash
# Development
rhamaa cms start MyProject --template dev
cd MyProject
pip install -r requirements-dev.txt
rhamaa cms migrate
rhamaa cms run

# Staging (using custom template)
rhamaa cms start MyProject --template-file ./templates/staging-template.zip
cd MyProject
pip install -r requirements.txt
rhamaa cms migrate
rhamaa cms run --prod

# Production
rhamaa cms start MyProject --template base
cd MyProject
pip install -r requirements.txt
rhamaa cms migrate
rhamaa cms run --prod
```

### Batch App Installation

```bash
#!/bin/bash
# install-apps.sh

APPS=("users" "articles" "comments" "newsletter")
PROJECT_NAME=$1

cd $PROJECT_NAME || exit 1

for app in "${APPS[@]}"; do
    echo "Installing $app..."
    rhamaa cms startapp ${app} --prebuild $app --backup
    if [ $? -ne 0 ]; then
        echo "Failed to install $app"
        exit 1
    fi
done

echo "Running migrations..."
rhamaa cms migrate

echo "✓ All apps installed!"
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install RhamaaCLI
        run: pip install rhamaa
      
      - name: Create Project
        run: rhamaa cms start deploy-test --template base
      
      - name: Install Apps
        run: |
          cd deploy-test
          rhamaa cms startapp testusers --prebuild users --dry-run
      
      - name: Run Tests
        run: |
          cd deploy-test
          python manage.py test
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install RhamaaCLI
RUN pip install "rhamaa[cms]"

# Create project
RUN rhamaa cms start MyProject --template base

WORKDIR /app/MyProject

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install apps
COPY install-apps.sh .
RUN chmod +x install-apps.sh && ./install-apps.sh

# Collect static
RUN python manage.py collectstatic --noinput

# Run migrations
RUN rhamaa cms migrate

EXPOSE 8000

CMD ["rhamaa", "cms", "run", "--prod"]
```

### Testing Custom Apps

```python
# test_app_installation.py
import tempfile
import shutil
from pathlib import Path
from rhamaa.manifest_applier import install_app_with_manifest

def test_app_install(app_key, app_name="testapp"):
    """Test installing a prebuilt app in temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal project structure
        project_path = Path(tmpdir)
        (project_path / "apps").mkdir()
        (project_path / "manage.py").write_text("# placeholder")
        (project_path / "settings.py").write_text("INSTALLED_APPS = []\n")
        (project_path / "urls.py").write_text("urlpatterns = []\n")
        
        # Change to project directory
        import os
        original_dir = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Try to install app
            result = install_app_with_manifest(
                app_name=app_name,
                prebuild_key=app_key,
                dry_run=True,  # Don't actually install
                backup=False
            )
            
            return result.success, result.changes, result.errors
            
        finally:
            os.chdir(original_dir)

# Test multiple apps
test_apps = ["users", "articles", "mqtt"]

for app in test_apps:
    print(f"\nTesting {app}...")
    success, changes, errors = test_app_install(app)
    
    if success:
        print(f"✅ {app}: OK ({len(changes)} changes)")
    else:
        print(f"❌ {app}: FAILED")
        for error in errors:
            print(f"   {error}")
```

---

## Tips & Tricks

### Quick Project Reset

```bash
# Remove and recreate project
rm -rf MyProject
rhamaa cms start MyProject
```

### Backup Before Changes

```bash
# Always backup before installing apps
rhamaa cms startapp myusers --prebuild users --backup

# Or backup manually
cp -r MyProject MyProject-backup
```

### View Available Options

```bash
# Help for specific command
rhamaa cms start --help
rhamaa cms startapp --help
rhamaa cms build-template --help
```

### Debug Mode

```bash
# Enable debug output
export RHAMAA_DEBUG=1
rhamaa cms startapp myapp --prebuild users
```

---

For more examples, check the [API Reference](api.md) and [Configuration Guide](configuration.md).
