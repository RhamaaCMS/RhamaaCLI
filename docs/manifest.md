# App Manifest System

The `rhamaa-app.json` manifest enables **plug-and-play installation** for prebuilt Rhamaa apps. When a manifest is present, `rhamaa cms startapp <name> --prebuild <key>` automatically configures everything.

## Overview

Without manifest:
```bash
rhamaa cms startapp myusers --prebuild users
# Then manually:
# - Add to INSTALLED_APPS
# - Configure middleware
# - Set AUTH_USER_MODEL
# - Add template dirs
# - etc.
```

With manifest:
```bash
rhamaa cms startapp myusers --prebuild users
# Done! Everything is configured automatically.
```

## Manifest Location

Place `rhamaa-app.json` in the **root of your app repository**:

```
your-app-repo/
├── rhamaa-app.json      ← The manifest
├── apps/
│   └── yourapp/
├── requirements.txt
└── README.md
```

## Minimal Manifest

```json
{
  "schema_version": "1.0.0",
  "name": "My App",
  "slug": "myapp",
  "version": "1.0.0",
  "description": "Brief description",
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
| `schema_version` | string | Yes | Manifest format version ("1.0.0") |
| `name` | string | Yes | Human-readable app name |
| `slug` | string | Yes | Unique identifier |
| `version` | string | Yes | App version (semver) |
| `description` | string | Yes | Brief description |
| `author` | string | No | Author or organization |

### Django Configuration (`django`)

#### Installed Apps

```json
{
  "django": {
    "installed_apps": [
      "apps.{app_name}",
      "third_party_app",
      "third_party_app.submodule"
    ]
  }
}
```

#### Middleware

Add middleware with optional positioning:

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

#### Templates

Configure template directories and context processors:

```json
{
  "django": {
    "templates": {
      "dirs": ["apps/{app_name}/templates"],
      "context_processors": [
        "apps.{app_name}.context_processors.user_vars",
        "apps.{app_name}.context_processors.notifications"
      ]
    }
  }
}
```

#### Authentication Backends

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

#### Custom Settings

Set any Django setting:

```json
{
  "django": {
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User",
      "LOGIN_URL": "/accounts/login/",
      "LOGIN_REDIRECT_URL": "/dashboard/",
      "MYAPP_SETTING": "value",
      "MYAPP_NUMBER": 42,
      "MYAPP_BOOLEAN": true
    }
  }
}
```

### URL Configuration (`urls`)

Define URL patterns:

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
      "path": "api/v1/",
      "include": "apps.{app_name}.api_urls",
      "name": "API v1"
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `path` | Yes | URL path (should end with `/`) |
| `include` | Yes | Python path to URL module |
| `namespace` | No | URL namespace |
| `name` | No | Human-readable name |

### Dependencies (`dependencies`)

Declare app and package dependencies:

```json
{
  "dependencies": {
    "apps": ["notifications", "analytics"],
    "packages": [
      "django-allauth>=0.54.0",
      "django-crispy-forms>=2.0",
      "stripe>=5.0.0"
    ],
    "optional_apps": ["debug_toolbar", "django_extensions"]
  }
}
```

### Static Files (`staticfiles`)

```json
{
  "staticfiles": {
    "dirs": ["apps/{app_name}/static"]
  }
}
```

### Post-Install Tasks (`post_install`)

Define tasks to run after installation:

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
      },
      {
        "command": "loaddata",
        "args": ["initial_data"],
        "kwargs": {}
      }
    ],
    "messages": [
      "Add SOCIAL_AUTH_KEYS to your environment variables",
      "Configure email backend in settings",
      "Review allauth_settings.py for customization"
    ]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `migrations` | boolean | Run makemigrations and migrate |
| `fixtures` | list | Fixture files to load |
| `management_commands` | list | Management commands to run |
| `messages` | list | Post-install messages to display |

## Placeholders

Use placeholders for dynamic values:

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

When user installs with `rhamaa cms startapp myusers --prebuild users`:
```python
AUTH_USER_MODEL = "myusers.User"
```

## Real-World Examples

### User Management App

See `.planning/phases/02/example-manifests/rhamaa-app.users.json`

### IoT Device Management

See `.planning/phases/02/example-manifests/rhamaa-app.iot.json`

### Simple Blog App

```json
{
  "schema_version": "1.0.0",
  "name": "Blog System",
  "slug": "blog",
  "version": "1.0.0",
  "description": "Simple blog with articles and categories",
  "author": "RhamaaCMS",
  
  "django": {
    "installed_apps": [
      "apps.{app_name}",
      "taggit"
    ],
    "templates": {
      "dirs": ["apps/{app_name}/templates"]
    },
    "settings": {}
  },
  
  "urls": [
    {
      "path": "blog/",
      "include": "apps.{app_name}.urls",
      "namespace": "blog"
    }
  ],
  
  "dependencies": {
    "packages": ["django-taggit>=4.0.0"]
  },
  
  "staticfiles": {
    "dirs": ["apps/{app_name}/static"]
  },
  
  "post_install": {
    "migrations": true,
    "fixtures": [],
    "management_commands": [],
    "messages": [
      "Blog app installed successfully!",
      "Add 'blog' to your navigation menu"
    ]
  }
}
```

## Validation

Validate your manifest before publishing:

```python
import json
from rhamaa.manifest import AppManifest

# Load and validate
with open('rhamaa-app.json') as f:
    data = json.load(f)

manifest = AppManifest.from_dict(data)
errors = manifest.validate()

if errors:
    print("Validation errors:")
    for e in errors:
        print(f"  - {e}")
else:
    print("✓ Manifest is valid")
```

## Best Practices

1. **Start Simple** - Begin with minimal required fields
2. **Test Thoroughly** - Test with different app names
3. **Document Settings** - Add comments in post-install messages
4. **Version Pinning** - Pin package versions to avoid conflicts
5. **Optional Dependencies** - Use `optional_apps` for nice-to-haves
6. **Clear Messages** - Make post-install messages actionable

## Conflict Detection

RhamaaCLI automatically detects:

- **Setting Conflicts**: Same key with different values
- **URL Conflicts**: Same path used by multiple apps
- **Middleware Conflicts**: Same middleware with different positions

Use `--ignore-conflicts` to proceed despite warnings.

## Troubleshooting

### Manifest Not Found
Ensure `rhamaa-app.json` is in the repository root (not in a subdirectory).

### Placeholders Not Replaced
Use exact syntax: `{app_name}` (with curly braces).

### Settings Not Applied
Verify settings file path. Rhamaa looks for:
- `settings/base.py`
- `settings.py`
- `{project_name}/settings.py`

### URL Conflicts
Use namespaces and unique paths:
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

## Migration from Basic Auto-Config

If you have a prebuilt app without manifest:

1. Create `rhamaa-app.json` with basic info
2. Test with `--dry-run` flag
3. Iterate until installation is automatic
4. Remove manual setup from README

---

For more details, see the [Configuration Guide](configuration.md).
