# Templates Guide

RhamaaCLI provides both **Project Templates** (for `start` command) and **App Templates** (for `startapp` command).

## Project Templates

Used with `rhamaa cms start <project> --template <key>`.

### Available Templates

| Template | Branch | Description | Use Case |
|----------|--------|-------------|----------|
| `base` | `base` | Stable, production-ready | Standard Wagtail projects |
| `dev` | `dev` | Development branch | Testing latest features |
| `inertia-react` | `base-inertia-react` | Wagtail + Inertia.js + React | SPA with Django backend |
| `iot` | `base-iot` | IoT with MQTT | IoT device management |

### Template Registry

Templates are defined in `rhamaa/templates/cms/project_template_list.json`:

```json
{
  "base": {
    "name": "RhamaaCMS Base",
    "description": "Stabil dan siap produksi",
    "repository": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "base"
  },
  "inertia-react": {
    "name": "RhamaaCMS Inertia + React",
    "description": "Wagtail dengan Inertia.js dan React",
    "repository": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "base-inertia-react"
  }
}
```

### Using Project Templates

```bash
# List available templates
rhamaa cms start --list

# Create with specific template
rhamaa cms start MyProject --template inertia-react

# Create with custom URL
rhamaa cms start MyProject --template-url https://example.com/template.zip

# Create from local file
rhamaa cms start MyProject --template-file ./path/to/template.zip

# Use local development template
rhamaa cms start MyProject --local-dev
```

### Custom Project Templates

You can create and distribute your own project templates:

1. Create a Wagtail project with your desired structure
2. Use `rhamaa cms build-template` to package it:
   ```bash
   rhamaa cms build-template . --slug my-template --output my-template.zip
   ```
3. Share the ZIP file or host it on GitHub

**Template Structure:**
```
template/
├── apps/              # App directory (empty or with example apps)
├── manage.py
├── requirements.txt
├── {project_name}/    # Project settings directory
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── .gitignore
```

## App Templates

Used with `rhamaa cms startapp <name> --template <key>`.

### Built-in App Templates

| Template | Type | Description |
|----------|------|-------------|
| `minimal` | builtin | Standard Django app (django-admin startapp) |
| `wagtail` | builtin | Wagtail app with models and templates |

### Using App Templates

```bash
# Create minimal Django app
rhamaa cms startapp blog --type minimal

# Create Wagtail app
rhamaa cms startapp blog --type wagtail

# List available templates
rhamaa cms startapp --list-templates

# Use custom template
rhamaa cms startapp api --template api
```

### Custom App Templates

You can create custom app templates as ZIP files:

**Template Structure:**
```
my-template.zip
├── apps/
│   └── {app_name}/     # App directory with placeholders
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── apps.py
│       ├── templates/
│       │   └── {app_name}/
│       │       └── index.html
│       └── static/
│           └── {app_name}/
│               └── style.css
└── rhamaa-app.json     # Optional: App manifest
```

**Placeholder Support:**
Use these placeholders in your template files:

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `{{app_name}}` | `myblog` | App name |
| `{{app_title}}` | `Myblog` | Title case |
| `{{app_verbose_name}}` | `Myblog` | Verbose name |
| `{{app_config_class}}` | `MyblogConfig` | Config class name |
| `{{app_name_upper}}` | `MYBLOG` | Uppercase |
| `{{app_class_name}}` | `Myblog` | Class name |

**Example `apps.py.tpl`:**
```python
from django.apps import AppConfig

class {{app_config_class}}(AppConfig):
    name = 'apps.{{app_name}}'
    verbose_name = '{{app_verbose_name}}'
```

### App Template Registry

Custom templates can be registered in `rhamaa/templates/cms/app_template_list.json`:

```json
{
  "api": {
    "name": "REST API App",
    "description": "Django REST Framework API app",
    "type": "remote",
    "repository": "https://github.com/RhamaaCMS/template-api",
    "branch": "main"
  }
}
```

## Template Processing

### How Templates Work

1. **Download** - Template is downloaded as ZIP
2. **Extract** - Files are extracted to target directory
3. **Process** - `.tpl` files are processed with placeholders
4. **Configure** - `rhamaa-app.json` manifest is applied (if present)

### File Extensions

| Extension | Processing |
|-----------|------------|
| `.tpl` | Processed with placeholder substitution, then renamed to remove `.tpl` |
| Regular files | Copied as-is |

### Example Processing

Template file `apps.py.tpl`:
```python
class {{app_config_class}}(AppConfig):
    name = 'apps.{{app_name}}'
```

With app name `blog`, becomes `apps.py`:
```python
class BlogConfig(AppConfig):
    name = 'apps.blog'
```

## Creating Templates

### Project Template Workflow

```bash
# 1. Create a Rhamaa project
rhamaa cms start TemplateSource

# 2. Customize the project
cd TemplateSource
# ... make your changes ...

# 3. Build the template
rhamaa cms build-template . --slug my-template

# 4. Template is created in dist/my-template.zip
```

### App Template Workflow

```bash
# 1. Create app structure manually
mkdir -p my-app-template/apps/{app_name}

# 2. Create template files with placeholders
cat > my-app-template/apps/{app_name}/apps.py.tpl << 'EOF'
from django.apps import AppConfig

class {{app_config_class}}(AppConfig):
    name = 'apps.{{app_name}}'
    verbose_name = '{{app_verbose_name}}'
EOF

# 3. Create manifest (optional but recommended)
cat > my-app-template/rhamaa-app.json << 'EOF'
{
  "schema_version": "1.0.0",
  "name": "My Custom App",
  "slug": "myapp",
  "django": {
    "installed_apps": ["apps.{app_name}"]
  },
  "urls": [{"path": "myapp/", "include": "apps.{app_name}.urls"}]
}
EOF

# 4. Create ZIP
cd my-app-template && zip -r ../my-app-template.zip .

# 5. Test
cd ..
rhamaa cms startapp test --template-file ./my-app-template.zip --dry-run
```

## Template Best Practices

### Project Templates

1. **Include README** with setup instructions
2. **Document features** in the template description
3. **Keep it minimal** - Don't include unnecessary apps
4. **Test thoroughly** before publishing
5. **Version control** your templates on GitHub

### App Templates

1. **Use placeholders** for all dynamic values
2. **Include example files** but keep them minimal
3. **Add rhamaa-app.json** for auto-configuration
4. **Test with different app names**
5. **Document dependencies** in requirements.txt

## Template Storage

### GitHub Repositories

Best for version control and distribution:
```json
{
  "my-template": {
    "repository": "https://github.com/user/template-repo",
    "branch": "main"
  }
}
```

### Direct URLs

For quick sharing:
```bash
rhamaa cms startapp app --template-url https://example.com/template.zip
```

### Local Files

For development:
```bash
rhamaa cms startapp app --template-file ./path/to/template.zip
```

## Troubleshooting

### Template Not Found
- Check template key exists in registry
- Verify repository URL is accessible
- For custom URLs, ensure ZIP is publicly accessible

### Placeholders Not Replaced
- Use double braces: `{{app_name}}`
- File must have `.tpl` extension
- Check for typos in placeholder names

### Extraction Fails
- Ensure ZIP has single root folder (GitHub format)
- Check ZIP isn't corrupted
- Verify file permissions

### Manifest Not Applied
- Ensure `rhamaa-app.json` is in template root
- Validate JSON syntax
- Check manifest version compatibility

## Advanced Topics

### Conditional Files

Use manifest to conditionally include files based on options (future feature).

### Template Inheritance

Templates can reference other templates as base (future feature).

### Private Templates

For private templates, use direct file path or authenticated URLs:
```bash
rhamaa cms startapp app --template-file /secure/path/template.zip
```

---

See also:
- [Commands Reference](commands.md) for template commands
- [Manifest Guide](manifest.md) for app configuration
