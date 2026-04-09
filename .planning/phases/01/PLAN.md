# Phase 01 Plan: Enhanced Templates & Auto-Configuration

## Overview
Implement new project templates (inertia-react, iot) and enhanced app template system with auto-configuration capabilities.

---

## Task 1: Update Project Template Registry
**File:** `rhamaa/templates/cms/project_template_list.json`

### Steps
1. Read existing `project_template_list.json`
2. Add two new entries:
   - `inertia-react`: branch `base-inertia-react`
   - `iot`: branch `base-iot`
3. Validate JSON structure
4. Update `rhamaa/commands/cms/start.py` to handle new templates in `--list` output

### Implementation Notes
```json
{
  "base": { ... },
  "dev": { ... },
  "inertia-react": {
    "name": "RhamaaCMS Inertia + React",
    "description": "Wagtail with Inertia.js and React frontend",
    "repository": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "base-inertia-react"
  },
  "iot": {
    "name": "RhamaaCMS IoT",
    "description": "IoT-focused template with MQTT integration",
    "repository": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "base-iot"
  }
}
```

**Verification:**
- [ ] JSON is valid
- [ ] `rhamaa cms start --list` shows new templates
- [ ] Template URLs resolve correctly

---

## Task 2: Create App Template Registry
**New File:** `rhamaa/templates/cms/app_template_list.json`

### Steps
1. Create new JSON registry for app templates
2. Define structure supporting both builtin and remote templates
3. Add initial entries: minimal, wagtail

### Implementation
```json
{
  "minimal": {
    "name": "Minimal Django App",
    "description": "Standard Django app using django-admin",
    "type": "builtin",
    "method": "django-admin"
  },
  "wagtail": {
    "name": "Wagtail App",
    "description": "Wagtail app with blocks, models, and templates",
    "type": "builtin",
    "method": "tpl",
    "template_path": "APPS_TEMPLATES/wagtail"
  }
}
```

**Verification:**
- [ ] File created and valid JSON
- [ ] Registry loads correctly in startapp.py
- [ ] Backward compatible with existing behavior

---

## Task 3: Implement Settings Parser Utility
**New File:** `rhamaa/config_utils.py`

### Steps
1. Create new utility module for Django settings manipulation
2. Implement `SettingsParser` class
3. Methods needed:
   - `parse_installed_apps()` - find and extract INSTALLED_APPS list
   - `add_installed_app(app_name)` - insert app into list
   - `write()` - save modified settings

### Implementation Approach
Use regex-based parsing for simplicity (Python 3.7+ compatible):

```python
import re
from pathlib import Path

class SettingsParser:
    def __init__(self, settings_path):
        self.path = Path(settings_path)
        self.content = self.path.read_text()
    
    def add_installed_app(self, app_path):
        """Add app to INSTALLED_APPS list."""
        # Find INSTALLED_APPS = [ ... ]
        pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'
        
        def replacer(match):
            start = match.group(1)
            apps_section = match.group(2)
            end = match.group(3)
            
            # Check if already exists
            if f"'{app_path}'" in apps_section or f'"{app_path}"' in apps_section:
                return match.group(0)
            
            # Find last app entry and add after it
            lines = apps_section.rstrip().split('\n')
            indent = self._get_indent(lines[-1]) if lines else '    '
            
            # Add new app line
            new_app = f"{indent}'{app_path}',"
            
            # Insert before closing bracket
            return f"{start}{apps_section.rstrip()}\n{new_app}\n{end}"
        
        self.content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)
    
    def write(self, backup=True):
        """Write changes to file."""
        if backup:
            backup_path = self.path.with_suffix('.py.bak')
            backup_path.write_text(self.path.read_text())
        self.path.write_text(self.content)
```

**Verification:**
- [ ] Parses various INSTALLED_APPS formats
- [ ] Preserves comments and formatting
- [ ] Creates backup before modification
- [ ] Handles existing entries (no duplicates)

---

## Task 4: Implement URL Configuration Parser
**File:** `rhamaa/config_utils.py` (add methods)

### Steps
1. Add URL parsing methods to `SettingsParser` or create `URLConfigParser`
2. Methods:
   - `parse_urlpatterns()` - find urlpatterns list
   - `add_url_include(app_name, path_prefix)` - add include() pattern
   - `create_app_urls(app_dir, app_name)` - create app urls.py

### Implementation
```pythonndef add_url_pattern(self, app_name, prefix=None):
    """Add URL pattern for app to main urls.py."""
    path_prefix = prefix or app_name
    app_path = f"apps.{app_name}"
    
    pattern = r'(urlpatterns\s*=\s*\[)(.*?)(\])'
    
    def replacer(match):
        start = match.group(1)
        urls_section = match.group(2)
        end = match.group(3)
        
        # Check if already included
        if f"{app_path}.urls" in urls_section:
            return match.group(0)
        
        # Generate new URL pattern
        indent = "    "
        new_url = f"{indent}path('{path_prefix}/', include('{app_path}.urls')),"
        
        return f"{start}{urls_section.rstrip()}\n{new_url}\n{end}"
    
    self.content = re.sub(pattern, replacer, self.content, flags=re.DOTALL)

def create_app_urls_py(self, app_dir, app_name):
    """Create basic urls.py for the app."""
    urls_content = f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
]
'''
    urls_path = app_dir / 'urls.py'
    if not urls_path.exists():
        urls_path.write_text(urls_content)
```

**Verification:**
- [ ] Handles different urlpatterns formats
- [ ] Preserves imports
- [ ] Generates valid urls.py for new apps
- [ ] No duplicate URL patterns

---

## Task 5: Enhance Startapp Command - New Options
**File:** `rhamaa/commands/cms/startapp.py`

### Steps
1. Add new CLI options:
   - `--template <key>` - Use template from registry
   - `--template-url <url>` - Custom ZIP URL
   - `--template-file <path>` - Local template
   - `--dry-run` - Preview changes
   - `--backup` - Create .bak files (default: True)
   - `--skip-config` - Skip auto-configuration

2. Update command signature:
```python
@click.command()
@click.argument('app_name', required=False)
@click.option('--type', 'app_type', type=click.Choice(['minimal', 'wagtail']), default='minimal')
@click.option('--prebuild', type=str, default=None, help='Install prebuilt app from registry')
@click.option('--template', type=str, default=None, help='Use template from registry')
@click.option('--template-url', type=str, default=None, help='Custom template ZIP URL')
@click.option('--template-file', type=str, default=None, help='Local template path')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
@click.option('--backup/--no-backup', default=True, help='Create backup of modified files')
@click.option('--skip-config', is_flag=True, help='Skip auto-configuration')
@click.option('--list', 'list_apps', is_flag=True, help='List available options')
@click.option('--list-templates', is_flag=True, help='List available templates')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing')
def startapp(app_name, app_type, prebuild, template, template_url, template_file, 
             dry_run, backup, skip_config, list_apps, list_templates, force):
    # ... implementation
```

3. Refactor main function to handle new options

**Verification:**
- [ ] All options parse correctly
- [ ] Help text updated
- [ ] Options are mutually exclusive where appropriate

---

## Task 6: Implement ZIP Template Download for Apps
**File:** `rhamaa/commands/cms/startapp.py` (add functions)

### Steps
1. Add function `install_template_app(app_name, template_info, ...)`
2. Download ZIP from remote if `type: "remote"`
3. Extract to `apps/<app_name>/`
4. Process `.tpl` files with placeholders
5. Handle both remote and local templates

### Implementation
```python
def install_template_app(app_name, template_key, template_url=None, 
                       template_file=None, dry_run=False, backup=True):
    """Install app from ZIP template."""
    
    # Determine template source
    if template_file:
        zip_path = Path(template_file)
    elif template_url:
        zip_path = download_file(template_url)
    elif template_key:
        registry = load_app_template_registry()
        template_info = registry.get(template_key)
        if not template_info:
            console.print(f"[red]Template '{template_key}' not found[/red]")
            return False
        
        if template_info['type'] == 'remote':
            zip_path = download_github_repo(
                template_info['repository'], 
                template_info.get('branch', 'main')
            )
        else:
            # builtin type - use existing logic
            return create_standard_app(app_name, template_key)
    
    # Extract and process
    return extract_and_configure_app(zip_path, app_name, dry_run)

def extract_and_configure_app(zip_path, app_name, dry_run=False):
    """Extract ZIP and process templates."""
    import zipfile
    import tempfile
    import shutil
    
    app_dir = Path("apps") / app_name
    
    if dry_run:
        console.print(f"[dry-run] Would extract to: {app_dir}")
        return True
    
    # Extract to temp first
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        # Find template root (handle nested dirs)
        tmp_path = Path(tmpdir)
        contents = list(tmp_path.iterdir())
        if len(contents) == 1 and contents[0].is_dir():
            template_root = contents[0]
        else:
            template_root = tmp_path
        
        # Move to apps directory
        if app_dir.exists():
            shutil.rmtree(app_dir)
        shutil.move(str(template_root), str(app_dir))
        
        # Process .tpl files
        process_template_files(app_dir, app_name)
    
    return True

def process_template_files(app_dir, app_name):
    """Replace placeholders in .tpl files."""
    context = {
        'app_name': app_name,
        'app_title': app_name.replace('_', ' ').title(),
        'app_class': app_name.title().replace('_', ''),
    }
    
    for tpl_file in app_dir.rglob('*.tpl'):
        content = tpl_file.read_text()
        for key, value in context.items():
            content = content.replace(f'{{{{{key}}}}}', value)
        
        # Remove .tpl extension
        dest_file = tpl_file.with_suffix('')
        dest_file.write_text(content)
        tpl_file.unlink()  # Remove original .tpl
```

**Verification:**
- [ ] Downloads remote templates
- [ ] Extracts correctly (handles nested dirs)
- [ ] Processes all .tpl files
- [ ] Removes .tpl extension after processing
- [ ] Handles dry-run mode

---

## Task 7: Implement Auto-Configuration
**File:** `rhamaa/commands/cms/startapp.py` (integrate)

### Steps
1. After app creation, detect project structure
2. Find settings file (common locations)
3. Apply configuration changes
4. Report results

### Implementation
```python
def auto_configure_app(app_name, dry_run=False, backup=True):
    """Auto-configure app in Django project."""
    console.print(f"[cyan]Auto-configuring app '{app_name}'...[/cyan]")
    
    changes = []
    
    # 1. Add to INSTALLED_APPS
    settings_file = find_settings_file()
    if settings_file:
        parser = SettingsParser(settings_file)
        if parser.add_installed_app(f'apps.{app_name}'):
            if not dry_run:
                parser.write(backup=backup)
            changes.append(f"Added 'apps.{app_name}' to INSTALLED_APPS")
    else:
        changes.append("[yellow]Could not find settings file[/yellow]")
    
    # 2. Add to URLs
    urls_file = find_urls_file()
    if urls_file:
        parser = SettingsParser(urls_file)
        if parser.add_url_pattern(app_name):
            if not dry_run:
                parser.write(backup=backup)
            changes.append(f"Added URL pattern for '{app_name}'")
    else:
        changes.append("[yellow]Could not find urls.py[/yellow]")
    
    # 3. Create app urls.py if needed
    app_dir = Path("apps") / app_name
    create_app_urls_py(app_dir, app_name)
    
    # Report
    console.print("\n[bold green]Configuration Changes:[/bold green]")
    for change in changes:
        console.print(f"  • {change}")
    
    if dry_run:
        console.print("\n[dry-run] No changes applied. Run without --dry-run to apply.")
    else:
        console.print("\n[dim]Backup files created: *.py.bak[/dim]" if backup else "")
        console.print("[green]Next:[/green] Run migrations: python manage.py migrate")

def find_settings_file():
    """Find Django settings file."""
    candidates = [
        "settings/base.py",
        "settings/local.py",
        "settings.py",
        Path.cwd().name / "settings.py",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path
    return None

def find_urls_file():
    """Find Django urls file."""
    candidates = [
        "urls.py",
        Path.cwd().name / "urls.py",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path
    return None
```

**Verification:**
- [ ] Detects settings/urls files in common locations
- [ ] Correctly modifies files
- [ ] Creates backup files
- [ ] Reports all changes clearly
- [ ] Handles errors gracefully

---

## Task 8: Update CLI Help and Documentation
**File:** `rhamaa/commands/cms/startapp.py`, `README.md`

### Steps
1. Update help text to show new options
2. Update README with new features
3. Add examples for new workflows

### README Updates
```markdown
### Enhanced App Creation

Create apps from remote templates:
\`\`\`bash
# Use template from registry
rhamaa cms startapp blog --template api

# Use custom template URL
rhamaa cms startapp blog --template-url https://example.com/template.zip

# Use local template
rhamaa cms startapp blog --template-file ./my-template.zip
\`\`\`

Auto-configuration features:
- Automatically adds app to INSTALLED_APPS
- Automatically wires up URLs
- Creates backup files (.bak)
- Dry-run mode to preview changes
\`\`\`bash
# Preview changes without applying
rhamaa cms startapp blog --template api --dry-run

# Skip auto-configuration
rhamaa cms startapp blog --template api --skip-config
\`\`\`
```

**Verification:**
- [ ] README updated
- [ ] Help text clear
- [ ] Examples work as documented

---

## Task 9: Testing & Validation
**Files:** Test scripts, validation

### Steps
1. Create test scenarios:
   - Create project with new templates
   - Create apps with different template types
   - Test auto-configuration
   - Test dry-run and backup

2. Manual test checklist:
   ```bash
   # Test project templates
   rhamaa cms start TestInertia --template inertia-react
   rhamaa cms start TestIoT --template iot
   
   # Test app templates
   cd TestInertia
   rhamaa cms startapp api --template api --dry-run
   rhamaa cms startapp api --template api
   rhamaa cms startapp blog --template-url <custom-url>
   
   # Verify auto-config
   cat settings/base.py | grep INSTALLED_APPS -A 20
   cat urls.py | grep api
   ls *.bak  # Check backups
   ```

**Verification:**
- [ ] All manual tests pass
- [ ] No syntax errors in generated code
- [ ] Backups created correctly
- [ ] Changes idempotent (safe to run twice)

---

## Summary

### Modified Files
- `rhamaa/templates/cms/project_template_list.json`
- `rhamaa/commands/cms/startapp.py`
- `rhamaa/commands/cms/start.py` (minor)
- `README.md`

### New Files
- `rhamaa/templates/cms/app_template_list.json`
- `rhamaa/config_utils.py`
- `rhamaa/commands/cms/startapp.py` (enhanced)

### Key Features Delivered
1. ✅ inertia-react and iot project templates
2. ✅ ZIP-based app template system
3. ✅ Auto-configuration (settings + URLs)
4. ✅ Dry-run and backup safety features
5. ✅ Enhanced CLI options

---

## UAT Criteria

**User Acceptance Testing Checklist:**

- [ ] User can list new project templates
- [ ] User can create project with inertia-react template
- [ ] User can create project with iot template
- [ ] User can list app templates
- [ ] User can create app from remote template
- [ ] User can create app from custom URL
- [ ] User can create app from local file
- [ ] App auto-adds to INSTALLED_APPS
- [ ] App auto-adds to urls.py
- [ ] Dry-run shows preview without changes
- [ ] Backup files created before modification
- [ ] Clear error messages when config fails
- [ ] Documentation is clear and accurate
