# Python API Reference

Complete reference for RhamaaCLI's Python API.

## Overview

RhamaaCLI can be used programmatically in Python scripts and applications.

```python
# Core modules
from rhamaa.manifest import AppManifest, ManifestParser
from rhamaa.config_utils import SettingsParser, URLParser, auto_configure_app
from rhamaa.manifest_applier import ManifestApplier
from rhamaa.dependency_resolver import DependencyResolver
from rhamaa.conflict_detector import ConflictDetector
```

## Manifest API

### `AppManifest`

Complete app configuration dataclass.

```python
from rhamaa.manifest import AppManifest

# Create from file
manifest = AppManifest.from_file(Path("rhamaa-app.json"))

# Create from dict
manifest = AppManifest.from_dict({
    "name": "My App",
    "slug": "myapp",
    "django": {
        "installed_apps": ["apps.{app_name}"],
        "settings": {"KEY": "value"}
    },
    "urls": [{"path": "myapp/", "include": "apps.{app_name}.urls"}]
})

# Resolve placeholders
resolved = manifest.resolve_placeholders("myapp")
# {app_name} -> myapp, {app_class} -> Myapp, etc.

# Validate
errors = manifest.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")

# Convert to dict
data = manifest.to_dict()
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `schema_version` | str | Manifest version |
| `name` | str | App name |
| `slug` | str | App slug |
| `version` | str | Version string |
| `description` | str | Description |
| `author` | str | Author name |
| `django` | DjangoConfig | Django configuration |
| `urls` | List[URLConfig] | URL patterns |
| `dependencies` | Dependencies | App dependencies |
| `staticfiles` | StaticfilesConfig | Static files config |
| `post_install` | PostInstallConfig | Post-install tasks |

### `ManifestParser`

Utility class for loading manifests.

```python
from rhamaa.manifest import ManifestParser

# Load and validate
manifest, errors = ManifestParser.load(Path("rhamaa-app.json"))
if errors:
    print("Failed to load:", errors)
else:
    print("Loaded:", manifest.name)

# Find manifest in directory
manifest_path = ManifestParser.find_manifest(Path("apps/myapp"))
if manifest_path:
    print(f"Found at: {manifest_path}")
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `load(path)` | `(AppManifest \| None, List[str])` | Load and validate manifest |
| `find_manifest(dir)` | `Path \| None` | Find manifest in directory |

## Configuration API

### `SettingsParser`

Parse and modify Django settings files.

```python
from rhamaa.config_utils import SettingsParser

parser = SettingsParser(Path("settings/base.py"))
```

#### Methods

##### `add_installed_app(app_path: str) -> bool`

Add app to INSTALLED_APPS.

```python
added = parser.add_installed_app("apps.myapp")
print(f"Added: {added}")  # True if added, False if already exists
```

##### `add_middleware(middleware_class: str, position: Optional[str]) -> bool`

Add middleware with optional positioning.

```python
# Simple add (at end)
parser.add_middleware("myapp.middleware.X")

# Positioned add
parser.add_middleware(
    "myapp.middleware.X",
    position="after:django.contrib.sessions.middleware.SessionMiddleware"
)

# Position options:
# - "first": Beginning of list
# - "last": End of list (default)
# - "before:X": Before middleware X
# - "after:X": After middleware X
```

##### `add_template_dirs(dirs: List[str]) -> bool`

Add template directories to TEMPLATES['DIRS'].

```python
added = parser.add_template_dirs(["apps/myapp/templates"])
print(f"Added {added} directories")
```

##### `add_context_processors(processors: List[str]) -> bool`

Add context processors.

```python
parser.add_context_processors([
    "myapp.context_processors.vars",
    "myapp.context_processors.notifications"
])
```

##### `add_auth_backends(backends: List[str]) -> bool`

Add authentication backends.

```python
parser.add_auth_backends([
    "myapp.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend"
])
```

##### `set_setting(key: str, value: Any) -> bool`

Set or update a Django setting.

```python
# String
parser.set_setting("AUTH_USER_MODEL", "myapp.User")

# Boolean
parser.set_setting("MYAPP_ENABLED", True)

# Number
parser.set_setting("MYAPP_TIMEOUT", 30)

# List
parser.set_setting("MYAPP_ADMINS", ["admin@example.com"])

# Dict
parser.set_setting("MYAPP_CONFIG", {"key": "value"})
```

##### `add_staticfiles_dirs(dirs: List[str]) -> bool`

Add static files directories.

```python
parser.add_staticfiles_dirs(["apps/myapp/static"])
```

##### `write(backup: bool = True) -> None`

Write changes to file.

```python
parser.write(backup=True)  # Creates .bak file
parser.write(backup=False)  # No backup
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `path` | Path | File path |
| `content` | str | Current file content |
| `original_content` | str | Original file content |

### `URLParser`

Parse and modify Django URL configuration.

```python
from rhamaa.config_utils import URLParser

parser = URLParser(Path("urls.py"))
```

#### Methods

##### `add_url_pattern(app_name: str, prefix: Optional[str]) -> bool`

Add simple URL include pattern.

```python
# Adds: path('myapp/', include('apps.myapp.urls'))
parser.add_url_pattern("myapp")

# With custom prefix
parser.add_url_pattern("myapp", prefix="api/")
# Adds: path('api/', include('apps.myapp.urls'))
```

##### `add_url_config(config: dict) -> bool`

Add URL pattern from dict.

```python
parser.add_url_config({
    "path": "accounts/",
    "include": "apps.myapp.urls",
    "namespace": "accounts",
    "name": "User accounts"
})
```

##### `add_url_patterns(configs: List[dict]) -> List[str]`

Add multiple URL patterns.

```python
added = parser.add_url_patterns([
    {"path": "app1/", "include": "apps.app1.urls"},
    {"path": "app2/", "include": "apps.app2.urls", "namespace": "app2"},
])
print(f"Added: {added}")
```

##### `check_url_conflict(path: str) -> bool`

Check if URL path already exists.

```python
if parser.check_url_conflict("accounts/"):
    print("Warning: Path already defined")
```

##### `write(backup: bool = True) -> None`

Write changes to file.

```python
parser.write(backup=True)
```

## Manifest Applier API

### `ManifestApplier`

Apply complete manifest configuration.

```python
from rhamaa.manifest import AppManifest
from rhamaa.manifest_applier import ManifestApplier, ApplyResult

# Load manifest
manifest = AppManifest.from_file(Path("rhamaa-app.json"))
manifest = manifest.resolve_placeholders("myapp")

# Create applier
applier = ManifestApplier(
    manifest=manifest,
    project_path=Path("."),
    app_name="myapp"
)
```

#### Methods

##### `apply_all(dry_run: bool, backup: bool) -> ApplyResult`

Apply all manifest configurations.

```python
result = applier.apply_all(dry_run=False, backup=True)

if result.success:
    print("Success!")
    for change in result.changes:
        print(f"  {change}")
else:
    print("Failed:")
    for error in result.errors:
        print(f"  {error}")
```

##### `preview_changes() -> List[str]`

Preview changes without applying.

```python
changes = applier.preview_changes()
for change in changes:
    print(change)
```

##### `rollback() -> bool`

Rollback changes using backup files.

```python
if applier.rollback():
    print("Rolled back successfully")
else:
    print("No backup files found")
```

#### ApplyResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | bool | Whether application succeeded |
| `changes` | List[str] | List of changes made |
| `errors` | List[str] | List of errors |
| `warnings` | List[str] | List of warnings |
| `backup_files` | List[Path] | Paths to backup files |

### `install_app_with_manifest()`

High-level function for complete app installation.

```python
from rhamaa.manifest_applier import install_app_with_manifest

result = install_app_with_manifest(
    app_name="myusers",
    prebuild_key="users",
    force=False,           # Overwrite existing
    dry_run=False,         # Preview only
    backup=True,           # Create backups
    resolve_deps=True,     # Auto-install dependencies
    ignore_conflicts=False # Skip conflict warnings
)

print(f"Success: {result.success}")
```

## Dependency Resolution API

### `DependencyResolver`

Resolve dependencies between apps.

```python
from rhamaa.dependency_resolver import DependencyResolver

# Define available apps
available = {
    "articles": {
        "dependencies": {"apps": ["users", "categories"]}
    },
    "users": {
        "dependencies": {"apps": []}
    },
    "categories": {
        "dependencies": {"apps": []}
    }
}

resolver = DependencyResolver(
    available_apps=available,
    installed_apps=[]
)
```

#### Methods

##### `get_missing_dependencies(target_app: str) -> List[str]`

Get list of missing dependencies.

```python
missing = resolver.get_missing_dependencies("articles")
print(f"Missing: {missing}")  # ['users', 'categories']
```

##### `resolve_dependencies(target_app: str) -> List[str]`

Get installation order.

```python
order = resolver.resolve_dependencies("articles")
print(order)  # ['users', 'categories', 'articles']
```

##### `check_circular_dependencies() -> Optional[List[str]]`

Check for circular dependencies.

```python
cycle = resolver.check_circular_dependencies()
if cycle:
    print(f"Circular: {' -> '.join(cycle)}")
```

##### `is_installable(target_app: str) -> Tuple[bool, str]`

Check if app can be installed.

```python
is_ok, reason = resolver.is_installable("articles")
print(f"Installable: {is_ok}, {reason}")
```

##### `get_installation_plan(target_app: str) -> List[dict]`

Get detailed installation plan.

```python
plan = resolver.get_installation_plan("articles")
for step in plan:
    print(f"Install: {step['app_key']}")
    print(f"Dependencies: {step['dependencies']}")
```

## Conflict Detection API

### `ConflictDetector`

Detect configuration conflicts.

```python
from rhamaa.conflict_detector import ConflictDetector

# Define manifests
manifests = {
    "app1": app1_manifest.to_dict(),
    "app2": app2_manifest.to_dict()
}

detector = ConflictDetector(manifests)
```

#### Methods

##### `detect_all_conflicts() -> List[Conflict]`

Detect all types of conflicts.

```python
conflicts = detector.detect_all_conflicts()
for conflict in conflicts:
    print(f"[{conflict.severity}] {conflict.conflict_type}")
    print(f"  Apps: {', '.join(conflict.apps)}")
    print(f"  {conflict.description}")
```

##### `detect_setting_conflicts() -> List[SettingConflict]`

Detect setting conflicts only.

```python
conflicts = detector.detect_setting_conflicts()
for c in conflicts:
    print(f"Setting '{c.setting_key}' conflict:")
    for app, value in c.values.items():
        print(f"  {app}: {value}")
```

##### `detect_middleware_conflicts() -> List[MiddlewareConflict]`

Detect middleware conflicts.

```python
conflicts = detector.detect_middleware_conflicts()
```

##### `detect_url_conflicts() -> List[URLConflict]`

Detect URL conflicts.

```python
conflicts = detector.detect_url_conflicts()
```

##### `generate_resolution_report(conflicts: List[Conflict]) -> str`

Generate human-readable report.

```python
report = detector.generate_resolution_report(conflicts)
print(report)
```

## Utility Functions

### `find_settings_file()`

Find Django settings file.

```python
from rhamaa.config_utils import find_settings_file
from pathlib import Path

settings = find_settings_file(Path("."))
if settings:
    print(f"Found: {settings}")
```

### `find_urls_file()`

Find Django URLs file.

```python
from rhamaa.config_utils import find_urls_file

urls = find_urls_file(Path("."))
```

### `auto_configure_app()`

Basic auto-configuration.

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

### `create_app_urls_py()`

Create app urls.py.

```python
from rhamaa.config_utils import create_app_urls_py

urls_path = create_app_urls_py(
    app_dir=Path("apps/myapp"),
    app_name="myapp"
)
print(f"Created: {urls_path}")
```

## Error Handling

### Common Exceptions

```python
from rhamaa.dependency_resolver import CircularDependencyError
from rhamaa.manifest import ManifestParser

try:
    resolver = DependencyResolver(apps)
    order = resolver.resolve_dependencies("app1")
except CircularDependencyError as e:
    print(f"Circular dependency: {e}")

try:
    manifest, errors = ManifestParser.load(Path("rhamaa-app.json"))
    if errors:
        print("Validation errors:", errors)
except FileNotFoundError:
    print("Manifest not found")
except json.JSONDecodeError:
    print("Invalid JSON")
```

## Type Hints

All APIs include type hints for better IDE support:

```python
from typing import List, Optional, Dict, Any
from pathlib import Path
from rhamaa.manifest import AppManifest

def process_manifest(manifest: AppManifest) -> List[str]:
    changes: List[str] = []
    # ... process ...
    return changes
```

## Async Support

Currently synchronous only. Future versions may add async support.

---

For more details, see:
- [Configuration Guide](configuration.md) - Auto-configuration details
- [Manifest Guide](manifest.md) - Manifest format
