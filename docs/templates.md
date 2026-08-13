# Templates Guide

RhamaaCLI provides **Project Templates** for the `start` command.

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

## Template Best Practices

### Project Templates

1. **Include README** with setup instructions
2. **Document features** in the template description
3. **Keep it minimal** - Don't include unnecessary apps
4. **Test thoroughly** before publishing
5. **Version control** your templates on GitHub

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
rhamaa cms start MyProject --template-url https://example.com/template.zip
```

### Local Files

For development:
```bash
rhamaa cms start MyProject --template-file ./path/to/template.zip
```

## Troubleshooting

### Template Not Found
- Check template key exists in registry
- Verify repository URL is accessible
- For custom URLs, ensure ZIP is publicly accessible

## Advanced Topics

### Conditional Files

Use manifest to conditionally include files based on options (future feature).

### Template Inheritance

Templates can reference other templates as base (future feature).

---

See also:
- [Commands Reference](commands.md) for template commands
- [Manifest Guide](manifest.md) for app configuration
