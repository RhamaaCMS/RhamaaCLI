# Phase 01 Research Notes

## Research Areas

### 1. GitHub Branch URLs
**Findings:**
- GitHub branch ZIP URLs follow pattern: `{repo}/archive/refs/heads/{branch}.zip`
- inertia-react branch: `https://github.com/RhamaaCMS/RhamaaCMS/archive/refs/heads/base-inertia-react.zip`
- iot branch: `https://github.com/RhamaaCMS/RhamaaCMS/archive/refs/heads/base-iot.zip`

### 2. Django Settings Parsing Options

**Option A: AST (ast module)**
- Pros: Safe, accurate parsing
- Cons: Complex, loses comments/formatting when unparsing
- Verdict: Too complex for this use case

**Option B: Regex**
- Pros: Simple, preserves formatting
- Cons: Fragile with edge cases
- Verdict: Acceptable with careful patterns

**Option C: RedBaron/Bowler**
- Pros: Best of both worlds
- Cons: External dependency
- Verdict: Good future option, stick with regex for now

**Decision:** Use regex-based parsing with robust patterns.

### 3. Existing Utilities Review

**`rhamaa/utils.py`:**
- `download_github_repo()` - already handles ZIP downloads
- `extract_repo_to_apps()` - handles ZIP extraction
- `check_wagtail_project()` - validates project structure

These can be reused or extended for app templates.

### 4. Template Processing

**Current approach in `startapp.py`:**
```python
def _render_template(content: str, context: dict) -> str:
    for key, value in context.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content
```

This simple placeholder system works well. Extend for new templates.

### 5. Configuration File Locations

**Common Django/Wagtail patterns:**
- `settings/base.py` - Wagtail cookiecutter pattern
- `settings/local.py` - Local overrides
- `settings.py` - Single file
- `{project_name}/settings.py` - Django default

**URL patterns:**
- `urls.py` - Root
- `{project_name}/urls.py` - Django default

### 6. Template Registry Design

**Project templates** (`project_template_list.json`):
```json
{
  "key": {
    "name": "Display Name",
    "description": "...",
    "repository": "https://github.com/...",
    "branch": "main"
  }
}
```

**App templates** (`app_template_list.json`):
```json
{
  "key": {
    "name": "Display Name",
    "description": "...",
    "type": "builtin|remote",
    "method": "django-admin|tpl|zip",
    "repository": "...",  # for remote
    "branch": "main",     # for remote
    "template_path": "..." // for builtin tpl
  }
}
```

### 7. CLI Option Design

**New options for `startapp`:**
- `--template <key>` - Registry lookup
- `--template-url <url>` - Direct ZIP download
- `--template-file <path>` - Local file
- `--dry-run` - Preview mode
- `--backup/--no-backup` - Toggle backups
- `--skip-config` - Skip auto-configuration

Mutually exclusive: `--template`, `--template-url`, `--template-file`, `--prebuild`

### 8. Auto-Configuration Scope

**Settings modifications:**
1. Add to `INSTALLED_APPS`
2. Optional: Add app-specific settings

**URL modifications:**
1. Add `include()` pattern to main urls.py
2. Create app urls.py if not exists

**Safety features:**
- Backup files (.bak)
- Dry-run preview
- Duplicate detection
- Error handling with clear messages

### 9. Template ZIP Structure

**Expected structure:**
```
template-name/
├── README.md
├── models.py.tpl
├── views.py.tpl
├── urls.py.tpl
├── admin.py.tpl
├── apps.py.tpl
├── templates/
│   └── {app_name}/
│       └── *.html.tpl
└── optional/
    └── settings.py.tpl
```

### 10. Backward Compatibility

**Existing behavior must be preserved:**
- `--type minimal` → django-admin startapp
- `--type wagtail` → .tpl templates
- `--prebuild <key>` → GitHub download

New options add functionality without breaking existing.

## Implementation Notes

### Priority Order
1. Update project template registry (Task 1)
2. Create app template registry (Task 2)
3. Implement config utils (Tasks 3-4)
4. Enhance startapp command (Tasks 5-7)
5. Documentation and testing (Tasks 8-9)

### Risk Areas
- **Settings parsing**: Regex may fail with unusual formatting
- **Settings locations**: Multiple patterns to detect
- **ZIP extraction**: Handle nested directories correctly
- **Permissions**: File modifications may fail on read-only files

### Mitigation
- Extensive testing with different project structures
- Clear error messages when auto-config fails
- Manual config instructions as fallback
- Backup files always created by default
