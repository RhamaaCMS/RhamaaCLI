# Phase 02: App Manifest & Plug-and-Play Configuration

## Overview
Implementasi App Manifest System yang memungkinkan prebuilt apps mendefinisikan konfigurasi lengkap (middleware, templates, settings, dll) dalam file JSON, membuat instalasi menjadi benar-benar plug-and-play.

## Goals
1. Buat format manifest JSON standar untuk Rhamaa apps
2. Implementasi parser dan applier untuk manifest
3. Support konfigurasi kompleks: middleware, templates, auth backends, extra settings
4. Dependency resolution antar apps
5. Post-install hooks (fixtures, management commands)
6. Conflict detection dan validation

## Deliverables

### 1. App Manifest Schema (rhamaa-app.json)
Lokasi: Di root setiap prebuilt app repo
```json
{
  "schema_version": "1.0.0",
  "name": "User Management",
  "slug": "users",
  "version": "1.0.0",
  "description": "Complete user management with auth",
  "author": "RhamaaCMS",
  
  "django": {
    "installed_apps": ["apps.{app_name}", "allauth", "allauth.account"],
    "middleware": [
      {
        "class": "apps.{app_name}.middleware.ActivityMiddleware",
        "priority": 50,
        "position": "after:django.contrib.sessions.middleware.SessionMiddleware"
      }
    ],
    "templates": {
      "dirs": ["apps/{app_name}/templates"],
      "context_processors": [
        "apps.{app_name}.context_processors.user_vars"
      ]
    },
    "auth_backends": [
      "apps.{app_name}.backends.EmailBackend"
    ],
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User",
      "LOGIN_URL": "/accounts/login/",
      "LOGIN_REDIRECT_URL": "/dashboard/",
      "LOGOUT_REDIRECT_URL": "/"
    }
  },
  
  "urls": [
    {
      "path": "accounts/",
      "include": "apps.{app_name}.urls",
      "namespace": "accounts"
    },
    {
      "path": "api/auth/",
      "include": "apps.{app_name}.api_urls"
    }
  ],
  
  "dependencies": {
    "apps": [],
    "packages": ["django-allauth>=0.54.0"],
    "optional_apps": ["notifications"]
  },
  
  "staticfiles": {
    "dirs": ["apps/{app_name}/static"]
  },
  
  "post_install": {
    "migrations": true,
    "fixtures": ["apps/{app_name}/fixtures/groups.json"],
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

### 2. Enhanced Config Utils
File: `rhamaa/config_utils.py`

#### Classes/Functions:

**AppManifestParser**
```python
class AppManifestParser:
    def __init__(self, manifest_path: Path)
    def parse() -> AppManifest
    def validate() -> List[str]  # validation errors
    def resolve_placeholders(app_name: str) -> AppManifest
```

**SettingsModifier** (extends SettingsParser)
```python
class SettingsModifier(SettingsParser):
    def add_middleware(self, middleware_config: dict) -> bool
    def add_template_dirs(self, dirs: List[str]) -> bool
    def add_context_processors(self, processors: List[str]) -> bool
    def add_auth_backends(self, backends: List[str]) -> bool
    def set_setting(self, key: str, value: any) -> bool
    def add_staticfiles_dirs(self, dirs: List[str]) -> bool
```

**URLModifier** (extends URLParser)
```python
class URLModifier(URLParser):
    def add_url_pattern(self, url_config: dict) -> bool
    def add_include_with_namespace(self, path: str, include: str, namespace: str) -> bool
```

**ManifestApplier**
```python
class ManifestApplier:
    def __init__(self, manifest: AppManifest, project_path: Path)
    def check_dependencies() -> Tuple[bool, List[str]]
    def check_conflicts() -> List[ConflictReport]
    def apply_settings_changes() -> List[str]
    def apply_url_changes() -> List[str]
    def run_post_install() -> List[str]
    def apply_all(dry_run: bool, backup: bool) -> ApplyResult
```

### 3. Dependency Resolver
File: `rhamaa/dependency_resolver.py`

```python
class DependencyResolver:
    def __init__(self, installed_apps: List[str], available_apps: Registry)
    def resolve_dependencies(target_app: str) -> List[str]  # installation order
    def check_circular_dependencies() -> Optional[List[str]]
    def get_missing_dependencies(app: str) -> List[str]
```

### 4. Conflict Detector
File: `rhamaa/conflict_detector.py`

```python
class ConflictDetector:
    def detect_setting_conflicts(manifests: List[AppManifest]) -> List[SettingConflict]
    def detect_middleware_conflicts(manifests: List[AppManifest]) -> List[MiddlewareConflict]
    def detect_url_conflicts(urls: List[URLConfig]) -> List[URLConflict]
    def generate_resolution_suggestions(conflicts: List[Conflict]) -> List[str]
```

### 5. Enhanced startapp.py
Integrasi manifest system ke command:

```python
@click.command()
@click.argument('app_name', required=False)
@click.option('--prebuild', type=str, default=None, help='Install prebuilt app with manifest')
@click.option('--resolve-deps/--no-resolve-deps', default=True, help='Auto-install dependencies')
@click.option('--ignore-conflicts', is_flag=True, help='Skip conflict warnings')
def startapp(...):
    # ... existing code ...
    if prebuild:
        # New manifest-based installation
        install_prebuilt_app_with_manifest(
            app_name, 
            prebuild_key, 
            force, 
            dry_run, 
            backup,
            resolve_deps=True,
            ignore_conflicts=False
        )
```

### 6. Enhanced App Registry
Update `app_list.json` dengan field manifest:

```json
{
  "users": {
    "name": "User Management",
    "repository": "https://github.com/RhamaaCMS/rhamaa-users",
    "branch": "main",
    "manifest_path": "rhamaa-app.json",
    "has_manifest": true,
    "complexity": "high",
    "requires": []
  }
}
```

## Implementation Tasks

### Task 1: Define Manifest Schema
- Buat JSON Schema untuk validasi rhamaa-app.json
- Definisikan semua field yang didukung
- Dokumentasi format manifest

### Task 2: Create AppManifest Classes
- `AppManifest` dataclass
- `MiddlewareConfig`, `URLConfig`, `Dependency` sub-classes
- Placeholder resolution (`{app_name}`, `{project_name}`)

### Task 3: Enhanced Settings Parser
- `add_middleware()` dengan position support (before/after)
- `add_template_dirs()` dan `add_context_processors()`
- `add_auth_backends()`
- `set_setting()` untuk key-value pairs
- `add_staticfiles_dirs()`

### Task 4: Enhanced URL Parser
- Support namespace dalam include
- Multiple URL patterns
- URL conflict detection

### Task 5: Dependency Resolver
- Parse dependencies dari manifest
- BFS/DFS untuk resolve urutan instalasi
- Circular dependency detection

### Task 6: Conflict Detector
- Setting key conflicts (same key, different values)
- Middleware order conflicts
- URL path conflicts
- UI untuk pilih resolve strategy

### Task 7: Manifest Applier
- Orchestrate semua changes
- Transaction-like apply (all or nothing)
- Rollback on failure
- Post-install execution

### Task 8: Update CLI Integration
- Download dan parse manifest sebelum install
- Tampilkan preview changes dari manifest
- Interactive conflict resolution
- Progress indicator untuk multi-step install

### Task 9: Example Manifests
- Buat rhamaa-app.json untuk app existing (users, mqtt, articles)
- Test dengan berbagai skenario

### Task 10: Documentation
- Guide membuat app dengan manifest
- Troubleshooting conflicts
- Best practices

## Verification Criteria (UAT)

1. Install app dengan manifest sederhana (hanya INSTALLED_APPS + URLs)
2. Install app dengan middleware, template dirs
3. Install app dengan dependencies (auto-resolve)
4. Install app dengan setting conflicts (detection works)
5. Install app dengan post-install fixtures
6. Install 2 apps yang saling depend (urutan benar)
7. Dry-run menampilkan semua changes dari manifest
8. Backup file dibuat untuk setiap modified file
9. Rollback berhasil jika install gagal di tengah

## Success Criteria

- ✅ Semua prebuilt apps punya manifest
- ✅ Instalasi users app hanya 1 command: `rhamaa cms startapp myusers --prebuild users`
- ✅ Auto-configuration mencakup: apps, middleware, templates, auth, settings, urls
- ✅ Conflict detection mencegah masalah sebelum terjadi
- ✅ Dependency resolver otomatis install app yang dibutuhkan
- ✅ Post-install hooks jalan otomatis

## Dependencies

- Phase 01 (selesai) - Auto-configuration system dasar
- Python 3.7+ compatibility
- jsonschema untuk validasi (optional, bisa built-in)

## Estimated Effort

- Development: 3-4 jam
- Testing: 2 jam
- Dokumentasi: 1 jam
- Total: ~6-7 jam

## Risks

1. **Complexity**: Manifest bisa jadi terlalu kompleks
   - Mitigasi: Mulai dengan subset fitur minimal

2. **Conflict Resolution**: UX untuk resolve conflicts bisa tricky
   - Mitigasi: Default behavior yang aman, override dengan --force

3. **Rollback**: Implementasi transaction sulit
   - Mitigasi: Backup-based rollback (restore dari .bak)

## Next Steps

1. Approve design manifest format
2. Implementasi Task 1-3 (core classes)
3. Test dengan app users (paling kompleks)
4. Iterate berdasarkan feedback

---

**Status**: Ready for implementation
**Priority**: High (akan membuat UX sangat mulus)
