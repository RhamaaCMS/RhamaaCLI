# Rhamaa App Manifest Guide

## Overview

The `rhamaa-app.json` manifest file allows prebuilt Rhamaa apps to define their complete configuration requirements. This enables **plug-and-play installation** where a single command (`rhamaa cms startapp myapp --prebuild users`) automatically configures everything.

## Manifest Location

Place `rhamaa-app.json` in the **root of your app repository**:

```
your-app-repo/
├── rhamaa-app.json      ← The manifest file
├── apps/
│   └── yourapp/
├── requirements.txt
└── README.md
```

## Minimal Example

```json
{
  "schema_version": "1.0.0",
  "name": "My App",
  "slug": "myapp",
  "version": "1.0.0",
  "description": "Brief description of my app",
  "author": "Your Name",
  
  "django": {
    "installed_apps": ["apps.{app_name}"],
    "settings": {}
  },
  
  "urls": [
    {
      "path": "myapp/",
      "include": "apps.{app_name}.urls"
    }
  ]
}
```

## Complete Reference

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | Manifest format version (currently "1.0.0") |
| `name` | string | Yes | Human-readable app name |
| `slug` | string | Yes | Unique identifier (e.g., "users", "blog") |
| `version` | string | Yes | App version (e.g., "1.0.0") |
| `description` | string | Yes | Brief description |
| `author` | string | No | Author or organization |

### Django Configuration

#### `django.installed_apps`
List of Django apps to add to `INSTALLED_APPS`.

```json
{
  "django": {
    "installed_apps": [
      "apps.{app_name}",
      "allauth",
      "allauth.account"
    ]
  }
}
```

#### `django.middleware`
List of middleware classes with optional positioning.

```json
{
  "django": {
    "middleware": [
      {
        "class": "apps.{app_name}.middleware.ActivityMiddleware",
        "position": "after:django.contrib.sessions.middleware.SessionMiddleware"
      },
      "django.middleware.security.SecurityMiddleware"
    ]
  }
}
```

**Position options:**
- `"first"` - Insert at beginning
- `"last"` - Insert at end (default)
- `"before:X"` - Insert before middleware X
- `"after:X"` - Insert after middleware X

#### `django.templates`
Template configuration.

```json
{
  "django": {
    "templates": {
      "dirs": ["apps/{app_name}/templates"],
      "context_processors": [
        "apps.{app_name}.context_processors.user_vars"
      ]
    }
  }
}
```

#### `django.auth_backends`
Authentication backends.

```json
{
  "django": {
    "auth_backends": [
      "apps.{app_name}.backends.EmailBackend",
      "django.contrib.auth.backends.ModelBackend"
    ]
  }
}
```

#### `django.settings`
Custom Django settings.

```json
{
  "django": {
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User",
      "LOGIN_URL": "/accounts/login/",
      "MYAPP_SETTING": "value"
    }
  }
}
```

### URL Configuration

```json
{
  "urls": [
    {
      "path": "accounts/",
      "include": "apps.{app_name}.urls",
      "namespace": "accounts",
      "name": "User accounts"
    },
    {
      "path": "api/auth/",
      "include": "apps.{app_name}.api_urls",
      "name": "Auth API"
    }
  ]
}
```

### Dependencies

```json
{
  "dependencies": {
    "apps": ["notifications", "analytics"],
    "packages": [
      "django-allauth>=0.54.0",
      "django-crispy-forms>=2.0"
    ],
    "optional_apps": ["debug_toolbar"]
  }
}
```

### Static Files

```json
{
  "staticfiles": {
    "dirs": ["apps/{app_name}/static"]
  }
}
```

### Post-Install Tasks

```json
{
  "post_install": {
    "migrations": true,
    "fixtures": [
      "apps/{app_name}/fixtures/groups.json",
      "apps/{app_name}/fixtures/permissions.json"
    ],
    "management_commands": [
      {
        "command": "create_default_groups",
        "args": [],
        "kwargs": {}
      }
    ],
    "messages": [
      "Add SOCIAL_AUTH_KEYS to your environment variables",
      "Configure email backend for password reset"
    ]
  }
}
```

## Placeholders

Use these placeholders for dynamic values:

| Placeholder | Example | Description |
|-------------|---------|-------------|
| `{app_name}` | `myusers` | The app name provided during install |
| `{app_class}` | `Myusers` | CamelCase version |
| `{app_upper}` | `MYUSERS` | UPPERCASE version |

**Example:**
```json
{
  "django": {
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User"
    }
  }
}
```

If user installs with `rhamaa cms startapp myusers --prebuild users`, this becomes:
```python
AUTH_USER_MODEL = "myusers.User"
```

## Best Practices

1. **Start Simple**: Begin with minimal required fields, add complexity as needed
2. **Test Placeholders**: Always test with different app names
3. **Document Settings**: Add comments about what settings do
4. **Optional Dependencies**: Use `optional_apps` for nice-to-have dependencies
5. **Clear Messages**: Post-install messages should be actionable
6. **Version Pinning**: Pin package versions to avoid conflicts

## Validation

Before publishing your app, validate the manifest:

```bash
# In your app directory
python -c "
import json
from rhamaa.manifest import AppManifest

with open('rhamaa-app.json') as f:
    data = json.load(f)

manifest = AppManifest.from_dict(data)
errors = manifest.validate()

if errors:
    print('Validation errors:')
    for e in errors:
        print(f'  - {e}')
else:
    print('✓ Manifest is valid')
"
```

## Conflict Detection

RhamaaCLI automatically detects conflicts:

- **Setting conflicts**: Same setting key with different values
- **URL conflicts**: Same URL path used by multiple apps
- **Middleware conflicts**: Same middleware with different positions

Use `--ignore-conflicts` to skip conflict warnings.

## Example Apps

See `example-manifests/` directory for complete examples:
- `rhamaa-app.users.json` - Complex user management app
- `rhamaa-app.iot.json` - IoT with MQTT and Celery

## Troubleshooting

### Manifest Not Found
Ensure `rhamaa-app.json` is in the repository root.

### Placeholders Not Replaced
Check that you're using the exact placeholder syntax: `{app_name}`

### Settings Not Applied
Verify the settings file path is detected. Rhamaa looks for:
- `settings/base.py`
- `settings.py`
- `{project_name}/settings.py`

### URL Conflicts
Use unique path prefixes or namespaces:
```json
{
  "urls": [
    {
      "path": "myapp/",
      "include": "apps.{app_name}.urls",
      "namespace": "myapp"
    }
  ]
}
```

## Migration Guide

If you have an existing prebuilt app without a manifest:

1. Create `rhamaa-app.json` with basic info
2. Document what manual steps are currently required
3. Test with `rhamaa cms startapp testapp --prebuild yourapp --dry-run`
4. Iterate until installation is fully automatic
5. Remove manual setup instructions from README

## Support

For questions or issues with the manifest system:
- Open an issue on GitHub
- Check existing example manifests
- Review the validation output
