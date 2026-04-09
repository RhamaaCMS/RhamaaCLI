# Phase 02 Context

## Problem Statement

Saat ini, instalasi prebuilt apps memerlukan manual setup tambahan setelah `startapp`:

1. **Users App** membutuhkan:
   - Add `AUTH_USER_MODEL = 'users.User'` ke settings
   - Add middleware activity tracking
   - Add allauth ke INSTALLED_APPS
   - Add template context processors
   - Setup email backend config
   - Load fixtures untuk default groups

2. **MQTT App** membutuhkan:
   - Add MQTT broker settings
   - Setup celery tasks (jika ada)
   - Konfigurasi database untuk timeseries

Semua ini dilakukan manual dengan copy-paste dari README, rentan error dan tidak scalable.

## Solution: App Manifest

Setiap app punya `rhamaa-app.json` yang mendefinisikan SELURUH konfigurasi yang dibutuhkan. CLI akan:

1. Parse manifest
2. Detect conflicts dengan existing config
3. Apply semua changes atomically
4. Run post-install hooks

## User Journey (After)

```bash
# Before Phase 02
rhamaa cms startapp myusers --prebuild users
# Then manually edit settings/base.py, urls.py, etc.

# After Phase 02
rhamaa cms startapp myusers --prebuild users
# Done! Everything configured automatically.
```

## Example Use Cases

### Use Case 1: E-commerce Setup
```bash
rhamaa cms startapp shop --prebuild ecommerce
# Manifest akan:
# - Install shop, products, cart, orders apps
# - Setup Stripe keys placeholder
# - Add payment middleware
# - Konfigurasi shipping calculation
```

### Use Case 2: LMS Setup
```bash
rhamaa cms startapp academy --prebuild lms
# Manifest akan:
# - Install courses, lessons, quizzes, progress
# - Setup video streaming config
# - Konfigurasi enrollment logic
# - Setup email notifications
```

## Technical Context

### File Structure yang Diharapkan

```
users-repo/
├── rhamaa-app.json          ← manifest utama
├── requirements.txt         ← python dependencies
├── README.md               ← human docs
└── apps/
    └── users/
        ├── __init__.py
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── templates/
        ├── static/
        └── fixtures/
            └── groups.json
```

### Integration dengan Phase 01

Phase 01 sudah membuat:
- `config_utils.py` dengan SettingsParser dan URLParser
- Auto-configure untuk INSTALLED_APPS dan URLs dasar

Phase 02 akan extend ini dengan:
- Middleware management
- Template configuration
- Auth backends
- Custom settings injection
- Post-install automation

### Conflict Scenarios

1. **Setting Override**: App A set `AUTH_USER_MODEL = 'users.User'`, App B set `AUTH_USER_MODEL = 'members.Member'`
   - Solution: Conflict detection, user must choose

2. **Middleware Order**: App A want middleware before Session, App B want after
   - Solution: Position-based insertion (before/after/position index)

3. **URL Path Collision**: App A use `accounts/`, App B juga use `accounts/`
   - Solution: Detect and suggest alternative prefix

### Placeholder System

Manifest menggunakan placeholder untuk dinamis:
- `{app_name}` → nama app saat install (e.g., "myusers")
- `{project_name}` → nama project (e.g., "MySite")
- `{app_class}` → CamelCase version (e.g., "Myusers")

Contoh:
```json
{
  "django": {
    "settings": {
      "AUTH_USER_MODEL": "{app_name}.User"
    }
  }
}
```

Saat install `myusers`, menjadi:
```python
AUTH_USER_MODEL = "myusers.User"
```

## Key Design Decisions

1. **JSON vs Python**: Pilih JSON untuk manifest karena:
   - Safe (no code execution)
   - Easy to parse and validate
   - Language agnostic
   - Can be served statically

2. **Manifest Location**: Di root repo, bukan di registry CLI:
   - Versioned dengan app code
   - App author maintain sendiri
   - Bisa berbeda per branch

3. **Dependency Resolution**: Simple list, bukan semver complex:
   - App dependencies cukup nama
   - Version checking via git tags/branches
   - Circular dependency detection saat parse

4. **Post-Install**: Sequential execution, stop on first error:
   - Fail-fast untuk prevent broken state
   - Clear error message which step failed
   - No automatic rollback (complex), use backup restore

## References

- Phase 01 PLAN: `.planning/phases/01/PLAN.md`
- Phase 01 VERIFICATION: `.planning/phases/01/VERIFICATION.md`
- Current config_utils: `rhamaa/config_utils.py`
- Current startapp: `rhamaa/commands/cms/startapp.py`
