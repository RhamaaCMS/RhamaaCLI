# Phase 01: Enhanced Templates & Auto-Configuration

## Overview
Enhance RhamaaCLI with new project templates and a sophisticated app template system with automatic Django project integration.

## Requirements

### 1. New Project Templates
Add two new project template options to `project_template_list.json`:

| Template Key | Repository | Branch | Description |
|--------------|------------|--------|-------------|
| `inertia-react` | https://github.com/RhamaaCMS/RhamaaCMS | `base-inertia-react` | Wagtail + Inertia.js + React setup |
| `iot` | https://github.com/RhamaaCMS/RhamaaCMS | `base-iot` | IoT-focused template with MQTT support |

### 2. Enhanced Startapp Template System
Transform `startapp` command to support ZIP-based templates like project creation:

**Current Behavior:**
- `--type minimal`: Uses `django-admin startapp`
- `--type wagtail`: Uses local `.tpl` template files

**New Behavior:**
- `--type minimal`: Keep existing django-admin behavior
- `--type wagtail`: Keep existing .tpl template behavior
- `--template <key>`: NEW - Download ZIP template from registry
- `--template-url <url>`: NEW - Custom ZIP URL
- `--template-file <path>`: NEW - Local ZIP/directory

**App Template Registry** (`app_template_list.json`):
```json
{
  "minimal": {
    "name": "Minimal Django App",
    "description": "Standard Django app structure",
    "type": "builtin"
  },
  "wagtail": {
    "name": "Wagtail App",
    "description": "Wagtail app with blocks and models",
    "type": "builtin"
  },
  "api": {
    "name": "API App",
    "description": "Django REST Framework API app",
    "repository": "https://github.com/RhamaaCMS/rhamaa-app-template-api",
    "branch": "main",
    "type": "remote"
  }
}
```

### 3. Auto-Configuration System
When creating an app, automatically:

1. **Add to INSTALLED_APPS**
   - Parse `settings/base.py` or `settings.py`
   - Add `'apps.<app_name>'` to INSTALLED_APPS list
   - Preserve formatting and comments

2. **Add to URL Configuration**
   - Parse `urls.py` or `<project>/urls.py`
   - Add `path('<app_name>/', include('apps.<app_name>.urls'))`
   - Handle existing URL patterns gracefully

3. **Create App URLs** (if not exists)
   - Generate `apps/<app_name>/urls.py` with basic pattern

4. **Settings Integration** (optional templates)
   - Add app-specific settings if template provides `settings.py.tpl`
   - Merge with existing settings intelligently

**Configuration Files to Modify:**
- `settings/base.py` or `settings.py` - INSTALLED_APPS
- `urls.py` - URL patterns
- `apps/<app_name>/urls.py` - Create if not exists

### 4. User Experience
- Show summary of changes after app creation
- Dry-run mode (`--dry-run`) to preview changes
- Backup modified files (`--backup`)
- Clear error messages if auto-config fails

## Acceptance Criteria

### Project Templates
- [ ] `rhamaa cms start MyProject --template inertia-react` works
- [ ] `rhamaa cms start MyProject --template iot` works
- [ ] Both templates appear in `rhamaa cms start --list`

### App Template System
- [ ] `rhamaa cms startapp blog --template api` downloads and installs
- [ ] `rhamaa cms startapp blog --template-url <zip>` works
- [ ] `rhamaa cms startapp blog --template-file <path>` works
- [ ] Template registry is extensible

### Auto-Configuration
- [ ] App automatically added to INSTALLED_APPS
- [ ] URLs automatically wired up
- [ ] Settings merged correctly (no syntax errors)
- [ ] Dry-run shows preview without modifying files
- [ ] Backup creates .bak files before modification
- [ ] Clear success/failure messages for each step

## Technical Notes

### Settings Parsing Strategy
```python
# Approach 1: AST parsing (safe, complex)
import ast
# Parse to AST, modify INSTALLED_APPS node, unparse

# Approach 2: Regex (simpler, riskier)
# Find INSTALLED_APPS = [...] pattern, insert new item

# Approach 3: Config patching (recommended)
# Use existing libraries like `redbaron` or `bowler`
```

### URL Parsing Strategy
```python
# Similar approach - find urlpatterns list
# Insert include() call at end or before catch-all
```

### Template Structure (ZIP format)
```
template-name/
├── README.md              # Template documentation
├── config.py              # Auto-config instructions
├── files/                 # Files to extract
│   ├── models.py.tpl
│   ├── views.py.tpl
│   └── ...
└── optional/
    ├── settings.py.tpl    # Settings to merge
    └── urls.py.tpl        # URL patterns
```

## Related Code
- `rhamaa/commands/cms/start.py` - Project creation
- `rhamaa/commands/cms/startapp.py` - App creation (primary target)
- `rhamaa/templates/cms/project_template_list.json` - Project registry
- `rhamaa/utils.py` - Download utilities

## Dependencies
- `ast` module (builtin) - for safe Python parsing
- `pathlib` (existing) - file operations
- `click` (existing) - CLI options
- `rich` (existing) - output formatting
