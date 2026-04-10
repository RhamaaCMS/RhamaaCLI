# Auto-Configuration System

RhamaaCLI automatically configures Django projects when apps are installed. This document explains how the auto-configuration works and how to customize it.

## Overview

When you run `rhamaa cms startapp`, RhamaaCLI can automatically:

1. **Add to INSTALLED_APPS** - Register the app in Django settings
2. **Configure URLs** - Wire up URL patterns in project's urls.py
3. **Add Middleware** - Insert middleware in correct order
4. **Configure Templates** - Add template directories and context processors
5. **Set Authentication** - Configure auth backends
6. **Apply Custom Settings** - Set any Django setting
7. **Configure Static Files** - Add static files directories
8. **Create App URLs** - Generate urls.py for the app

## Basic Auto-Configuration

### Standard App Creation

```bash
# Creates app and configures INSTALLED_APPS + URLs
rhamaa cms startapp blog

# Creates Wagtail app with full structure
rhamaa cms startapp blog --type wagtail
```

When creating a standard app, RhamaaCLI also generates a default manifest file:

- `apps/<app_name>/rhamaa-app.json`

This keeps standard apps aligned with the prebuilt app manifest convention used by RhamaaCMS.

### Prebuilt App Installation

```bash
# Install with full manifest configuration
rhamaa cms startapp myusers --prebuild users
```

## Configuration Modes

### 1. Basic Auto-Config (Default)

For standard apps without manifest:

```python
# Changes made:
INSTALLED_APPS += ['apps.blog']  # settings.py

urlpatterns += [
    path('blog/', include('apps.blog.urls')),  # urls.py
]
```

### 2. Manifest-Based Auto-Config

For apps with `rhamaa-app.json`:

```bash
rhamaa cms startapp myusers --prebuild users
```

Applies complete configuration from manifest:
- All INSTALLED_APPS entries
- Middleware with positioning
- Template configuration
- Auth backends
- Custom settings
- URL patterns
- Post-install tasks

### 3. Skip Configuration

To install without auto-configuration:

```bash
rhamaa cms startapp blog --skip-config
```

You'll need to manually:
1. Add to INSTALLED_APPS
2. Configure URLs
3. Run migrations

## Dry-Run Mode

Preview changes without applying:

```bash
rhamaa cms startapp myusers --prebuild users --dry-run
```

Output example:
```
[dry-run] Would install app into 'apps/myusers'
[dry-run] Would auto-configure in project settings
  + Added 'apps.myusers' to INSTALLED_APPS
  + Added middleware: apps.myusers.middleware.ActivityMiddleware
  + Added template dir: apps/myusers/templates
  + Set AUTH_USER_MODEL = myusers.User
  + Added URL: accounts/ -> apps.myusers.urls
```

## Backup System

### Creating Backups

```bash
# Enable backup creation
rhamaa cms startapp myusers --prebuild users --backup
```

This creates `.bak` files:
- `settings/base.py` → `settings/base.py.bak`
- `urls.py` → `urls.py.bak`

### Default Behavior

By default, **backups are disabled**:
```bash
rhamaa cms startapp myusers --prebuild users  # No backup
```

### Restoring from Backup

If something goes wrong, restore manually:

```bash
cp settings/base.py.bak settings/base.py
cp urls.py.bak urls.py
rm settings/base.py.bak urls.py.bak
```

## Configuration File Detection

RhamaaCLI automatically finds configuration files in common locations:

### Settings Files (in order of priority)

1. `settings/base.py`
2. `settings/local.py`
3. `settings/production.py`
4. `settings.py`
5. `{project_name}/settings/base.py`
6. `{project_name}/settings.py`

### URL Files

1. `urls.py`
2. `{project_name}/urls.py`

## Conflict Detection

RhamaaCLI detects potential conflicts before applying changes:

### Setting Conflicts

When two apps define the same setting with different values:

```
⚠️  Found 1 potential conflict(s):

1. [ERROR] setting
   Apps: users, members
   Setting 'AUTH_USER_MODEL' has different values across apps
   Suggestions:
   - Choose one value for AUTH_USER_MODEL
   - Consider creating a shared configuration
```

**Resolution:**
- Use `--ignore-conflicts` to proceed
- Manually resolve in settings file
- Redesign app architecture

### URL Conflicts

When URL paths collide:

```
⚠️  URL path 'accounts/' is used by multiple apps
```

**Resolution:**
- Use different path prefixes
- Use URL namespaces
- Merge functionality

### Middleware Conflicts

When middleware has conflicting position requirements:

```
⚠️  Middleware 'X' has conflicting position requirements
```

## Configuration Classes

### SettingsParser

Located in `rhamaa/config_utils.py`:

```python
from rhamaa.config_utils import SettingsParser

parser = SettingsParser(Path("settings/base.py"))

# Add to INSTALLED_APPS
parser.add_installed_app("apps.myapp")

# Add middleware
parser.add_middleware(
    "myapp.middleware.X",
    position="after:django.contrib.sessions.middleware.SessionMiddleware"
)

# Add template directories
parser.add_template_dirs(["apps/myapp/templates"])

# Add context processors
parser.add_context_processors(["myapp.context_processors.vars"])

# Add auth backends
parser.add_auth_backends(["myapp.backends.EmailBackend"])

# Set custom setting
parser.set_setting("MY_SETTING", "value")
parser.set_setting("MY_BOOL", True)
parser.set_setting("MY_LIST", ["a", "b"])

# Add static files dirs
parser.add_staticfiles_dirs(["apps/myapp/static"])

# Save changes
parser.write(backup=True)
```

### URLParser

```python
from rhamaa.config_utils import URLParser

parser = URLParser(Path("urls.py"))

# Add basic URL pattern
parser.add_url_pattern("myapp", prefix="custom/")

# Add URL with namespace
parser.add_url_config({
    "path": "api/v1/",
    "include": "apps.myapp.api_urls",
    "namespace": "api",
    "name": "API v1"
})

# Add multiple URLs
parser.add_url_patterns([
    {"path": "app1/", "include": "apps.app1.urls"},
    {"path": "app2/", "include": "apps.app2.urls"},
])

# Check for conflicts
if parser.check_url_conflict("accounts/"):
    print("Warning: URL path already exists")

# Save changes
parser.write(backup=True)
```

### ManifestApplier

For complete manifest-based configuration:

```python
from rhamaa.manifest import AppManifest
from rhamaa.manifest_applier import ManifestApplier

# Load and resolve manifest
manifest = AppManifest.from_file(Path("rhamaa-app.json"))
manifest = manifest.resolve_placeholders("myapp")

# Apply to project
applier = ManifestApplier(manifest, Path("."), "myapp")

# Preview changes
changes = applier.preview_changes()
for change in changes:
    print(change)

# Apply with backup
result = applier.apply_all(dry_run=False, backup=True)

# Rollback if needed
if not result.success:
    applier.rollback()
```

## Advanced Configuration

### Custom Settings Modification

For complex modifications, use the Python API directly:

```python
from pathlib import Path
from rhamaa.config_utils import SettingsParser

# Read settings
parser = SettingsParser(Path("settings/base.py"))

# Make custom modifications
parser.content = parser.content.replace(
    "OLD_VALUE",
    "NEW_VALUE"
)

# Save
parser.write(backup=True)
```

### Conditional Configuration

Use manifests for conditional logic:

```json
{
  "django": {
    "settings": {
      "DEBUG": false,
      "MYAPP_FEATURE_X": true,
      "MYAPP_API_KEY": "{env:MYAPP_API_KEY}"
    }
  }
}
```

### Environment-Specific Configuration

Support different environments via post-install messages:

```json
{
  "post_install": {
    "messages": [
      "Development: Set DEBUG=True in settings",
      "Production: Configure EMAIL_BACKEND for notifications"
    ]
  }
}
```

## Troubleshooting

### Settings Not Found

If RhamaaCLI can't find your settings:

```bash
# Check current directory
pwd

# List settings files
ls settings/
ls */settings.py

# Specify project path (future feature)
# rhamaa cms startapp app --project-path ./myproject
```

### Changes Not Applied

1. Check file permissions
2. Verify Python syntax in settings
3. Look for `.bak` files (indicates write was attempted)
4. Run with `--backup` to preserve originals

### Partial Configuration

If configuration stops mid-way:

```bash
# Check backup files exist
ls *.bak
ls settings/*.bak

# Restore from backup
cp settings/base.py.bak settings/base.py

# Try again with --force
rhamaa cms startapp app --prebuild users --force
```

### Syntax Errors After Configuration

If settings.py becomes invalid:

1. Restore from backup:
   ```bash
   cp settings/base.py.bak settings/base.py
   ```

2. Check Python syntax:
   ```bash
   python -m py_compile settings/base.py
   ```

3. Report issue with `--dry-run` output

## Best Practices

### For App Users

1. **Always use --dry-run first** on production projects
2. **Enable --backup** when experimenting
3. **Review changes** in the output
4. **Test in development** before production
5. **Keep .bak files** until confirming everything works

### For App Developers

1. **Test with different project structures**
2. **Handle missing settings gracefully**
3. **Provide clear error messages**
4. **Document all configuration changes**
5. **Test with --dry-run mode**

### For Project Maintainers

1. **Use standard settings locations**
2. **Keep settings files valid Python**
3. **Version control before adding apps**
4. **Review auto-generated changes**
5. **Test apps in isolation first**

## Configuration API Reference

### Functions

#### `find_settings_file(project_path)`

Find Django settings file in common locations.

```python
from rhamaa.config_utils import find_settings_file

settings = find_settings_file(Path("."))
if settings:
    print(f"Found: {settings}")
```

#### `find_urls_file(project_path)`

Find Django urls.py file.

```python
from rhamaa.config_utils import find_urls_file

urls = find_urls_file(Path("."))
```

#### `auto_configure_app(app_name, project_path, dry_run, backup)`

Basic auto-configuration function.

```python
from rhamaa.config_utils import auto_configure_app

changes = auto_configure_app(
    app_name="myapp",
    project_path=Path("."),
    dry_run=False,
    backup=True
)

for change in changes:
    print(change)
```

#### `create_app_urls_py(app_dir, app_name)`

Create basic urls.py for an app.

```python
from rhamaa.config_utils import create_app_urls_py

urls_path = create_app_urls_py(
    app_dir=Path("apps/myapp"),
    app_name="myapp"
)
print(f"Created: {urls_path}")
```

---

## See Also

- [App Manifest](manifest.md) - Full configuration with manifests
- [Commands Reference](commands.md) - CLI commands
- [Troubleshooting](troubleshooting.md) - Common issues
