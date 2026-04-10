# Troubleshooting Guide

Common issues and solutions when using RhamaaCLI.

## Quick Diagnostics

```bash
# Check RhamaaCLI version
rhamaa --version

# Check if installation is complete
rhamaa cms run --check

# Show project status
rhamaa cms run --status
```

---

## Installation Issues

### Command Not Found

**Problem:**
```bash
$ rhamaa cms start MyProject
rhamaa: command not found
```

**Solutions:**

1. **Install RhamaaCLI:**
   ```bash
   pip install "rhamaa[cms]"
   ```

2. **Check PATH:**
   ```bash
   # Find where pip installs packages
   pip show rhamaa
   
   # Ensure local bin is in PATH (Linux/Mac)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Or for Windows, add Python Scripts folder to PATH
   ```

3. **Reinstall:**
   ```bash
   pip uninstall rhamaa
   pip install "rhamaa[cms]"
   ```

### Permission Denied

**Problem:**
```bash
$ pip install rhamaa
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use --user flag:**
   ```bash
   pip install --user rhamaa
   ```

2. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows
   pip install rhamaa
   ```

3. **On macOS with Homebrew:**
   ```bash
   # Don't use sudo with pip
   pip3 install --user rhamaa
   ```

---

## Project Creation Issues

### Template Download Fails

**Problem:**
```bash
rhamaa cms start MyProject --template dev
Failed to download template: Connection timeout
```

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping github.com
   ```

2. **Try different template:**
   ```bash
   rhamaa cms start MyProject --template base
   ```

3. **Use local template:**
   ```bash
   rhamaa cms start MyProject --template-file ./template.zip
   ```

4. **Increase timeout (future feature)**

### Directory Already Exists

**Problem:**
```bash
rhamaa cms start MyProject
Error: Directory 'MyProject' already exists
```

**Solutions:**

1. **Use different name:**
   ```bash
   rhamaa cms start MyProject2
   ```

2. **Use --force to overwrite:**
   ```bash
   rhamaa cms start MyProject --force
   ```

3. **Remove existing directory:**
   ```bash
   rm -rf MyProject  # Linux/Mac
   # or: rmdir /s MyProject  # Windows
   rhamaa cms start MyProject
   ```

### Template Extraction Fails

**Problem:**
```bash
rhamaa cms start MyProject
Failed to extract template
```

**Solutions:**

1. **Check ZIP file integrity:**
   ```bash
   unzip -t template.zip
   ```

2. **Check disk space:**
   ```bash
   df -h  # Linux/Mac
   # or: wmic logicaldisk get size,freespace,caption  # Windows
   ```

3. **Check permissions:**
   ```bash
   ls -la
   # Ensure you have write permission
   ```

---

## App Installation Issues

### App Not Found in Registry

**Problem:**
```bash
rhamaa cms startapp myusers --prebuild users
Error: Prebuilt app 'users' not found
```

**Solutions:**

1. **List available apps:**
   ```bash
   rhamaa cms startapp --list
   ```

2. **Check spelling:**
   ```bash
   # Case-insensitive, but check for typos
   rhamaa cms startapp myusers --prebuild users  # correct
   rhamaa cms startapp myusers --prebuild user   # wrong
   ```

3. **Update RhamaaCLI:**
   ```bash
   pip install --upgrade rhamaa
   ```

### Download Fails

**Problem:**
```bash
rhamaa cms startapp myusers --prebuild users
Failed to download repository
```

**Solutions:**

1. **Check GitHub status:**
   - Visit https://www.githubstatus.com/

2. **Check network:**
   ```bash
   curl -I https://github.com
   ```

3. **Use proxy if needed:**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

4. **Try again later:**
   ```bash
   # Sometimes just a temporary issue
   rhamaa cms startapp myusers --prebuild users
   ```

### Extraction Fails

**Problem:**
```bash
rhamaa cms startapp myusers --prebuild users
Failed to extract app
```

**Solutions:**

1. **Check if app already exists:**
   ```bash
   ls apps/
   ```

2. **Use --force:**
   ```bash
   rhamaa cms startapp myusers --prebuild users --force
   ```

3. **Clean up partial extraction:**
   ```bash
   rm -rf apps/myusers
   rhamaa cms startapp myusers --prebuild users
   ```

### Auto-Configuration Fails

**Problem:**
```bash
rhamaa cms startapp myusers --prebuild users
Could not find settings file
```

**Solutions:**

1. **Check project structure:**
   ```bash
   # Should have one of:
   ls settings/base.py
   ls settings.py
   ls */settings.py
   ```

2. **Create missing settings:**
   ```bash
   # If no settings file exists
   echo "INSTALLED_APPS = []" > settings.py
   ```

3. **Skip auto-config:**
   ```bash
   rhamaa cms startapp myusers --prebuild users --skip-config
   # Then manually configure
   ```

4. **Specify project path (future feature):**
   ```bash
   # rhamaa cms startapp myapp --project-path ./myproject
   ```

---

## Configuration Issues

### Settings Not Modified

**Problem:**
After installing app, settings.py is unchanged.

**Solutions:**

1. **Check backup files:**
   ```bash
   ls *.bak
   ls settings/*.bak
   # If .bak exists, write was attempted
   ```

2. **Check file permissions:**
   ```bash
   ls -la settings/base.py
   # Should be writable
   ```

3. **Use --dry-run to debug:**
   ```bash
   rhamaa cms startapp myapp --prebuild users --dry-run
   # See what would be changed
   ```

4. **Manual configuration:**
   ```bash
   # Edit settings.py manually
   nano settings/base.py
   ```

### URL Configuration Fails

**Problem:**
URLs are not added to urls.py

**Solutions:**

1. **Check urls.py exists:**
   ```bash
   find . -name "urls.py" -type f
   ```

2. **Check file structure:**
   ```python
   # urls.py should have:
   from django.urls import path
   
   urlpatterns = [
       # existing patterns
   ]
   ```

3. **Manual URL addition:**
   ```python
   # Add to urls.py:
   path('myapp/', include('apps.myapp.urls')),
   ```

### Syntax Errors After Configuration

**Problem:**
```bash
python manage.py check
SyntaxError: invalid syntax
```

**Solutions:**

1. **Restore from backup:**
   ```bash
   cp settings/base.py.bak settings/base.py
   cp urls.py.bak urls.py
   ```

2. **Check Python syntax:**
   ```bash
   python -m py_compile settings/base.py
   python -m py_compile urls.py
   ```

3. **Check for conflicts:**
   ```bash
   # Look for:
   # - Missing commas in lists
   # - Mismatched parentheses
   # - Invalid Python syntax
   ```

---

## Manifest Issues

### Manifest Not Found

**Problem:**
```bash
rhamaa cms startapp myusers --prebuild users
No manifest found, using basic auto-configuration
```

**Solutions:**

1. **Check if manifest exists:**
   ```bash
   ls apps/myusers/rhamaa-app.json
   ```

2. **Manifest should be in app root:**
   ```
   apps/myusers/
   ├── rhamaa-app.json  ← Here
   └── ...
   ```

3. **Create basic manifest:**
   ```bash
   cat > apps/myusers/rhamaa-app.json << 'EOF'
   {
     "schema_version": "1.0.0",
     "name": "User Management",
     "slug": "users",
     "django": {
       "installed_apps": ["apps.{app_name}"],
       "settings": {}
     },
     "urls": [{"path": "accounts/", "include": "apps.{app_name}.urls"}]
   }
   EOF
   ```

### Manifest Validation Fails

**Problem:**
```bash
Validation errors:
  - Missing required field: name
  - URL[0]: missing path
```

**Solutions:**

1. **Check JSON syntax:**
   ```bash
   python -m json.tool rhamaa-app.json
   ```

2. **Validate manifest:**
   ```python
   from rhamaa.manifest import AppManifest
   import json
   
   with open('rhamaa-app.json') as f:
       data = json.load(f)
   
   manifest = AppManifest.from_dict(data)
   errors = manifest.validate()
   
   for error in errors:
       print(error)
   ```

3. **Check required fields:**
   ```json
   {
     "schema_version": "1.0.0",
     "name": "Required",
     "slug": "required",
     "version": "1.0.0",
     "description": "Required",
     "django": {}
   }
   ```

### Placeholders Not Replaced

**Problem:**
Settings contain literal `{app_name}` instead of actual value.

**Solutions:**

1. **Check placeholder syntax:**
   ```json
   {
     "django": {
       "settings": {
         "AUTH_USER_MODEL": "{app_name}.User"  // Correct
         // Not: {{app_name}} or { app_name }
       }
     }
   }
   ```

2. **Check app name:**
   ```bash
   # App name should be valid Python identifier
   rhamaa cms startapp my_app --prebuild users  # OK
   rhamaa cms startapp 123app --prebuild users  # Invalid
   ```

---

## Conflict Issues

### Setting Conflicts

**Problem:**
```
⚠️  Setting 'AUTH_USER_MODEL' conflict:
   App1: users.User
   App2: members.Member
```

**Solutions:**

1. **Use --ignore-conflicts:**
   ```bash
   rhamaa cms startapp myapp2 --prebuild members --ignore-conflicts
   ```

2. **Choose one user model:**
   ```python
   # In settings.py, manually set:
   AUTH_USER_MODEL = "users.User"  # or "members.Member"
   ```

3. **Design apps to share user model:**
   - Use dependency: `"apps": ["users"]`
   - Reference `settings.AUTH_USER_MODEL`

### URL Path Conflicts

**Problem:**
```
⚠️  URL path 'accounts/' is used by multiple apps
```

**Solutions:**

1. **Use different paths:**
   ```json
   {
     "urls": [
       {"path": "users/", "include": "apps.users.urls"},
       {"path": "members/", "include": "apps.members.urls"}
     ]
   }
   ```

2. **Use namespaces:**
   ```json
   {
     "urls": [
       {"path": "accounts/", "include": "apps.users.urls", "namespace": "users"},
       {"path": "profile/", "include": "apps.members.urls", "namespace": "members"}
     ]
   }
   ```

3. **Merge functionality:**
   - Consider if apps should be combined

---

## Database Issues

### Migration Failures

**Problem:**
```bash
rhamaa cms migrate
django.db.utils.OperationalError: no such table
```

**Solutions:**

1. **Create database:**
   ```bash
   python manage.py migrate --run-syncdb
   ```

2. **Check database settings:**
   ```python
   # settings/base.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

3. **Reset database:**
   ```bash
   rm db.sqlite3  # Delete database
   rhamaa cms migrate  # Recreate
   ```

### Missing Tables

**Problem:**
```bash
python manage.py shell
>>> from apps.blog.models import Post
django.db.utils.ProgrammingError: relation "blog_post" does not exist
```

**Solutions:**

1. **Run migrations:**
   ```bash
   rhamaa cms migrate
   ```

2. **Make migrations first:**
   ```bash
   python manage.py makemigrations blog
   rhamaa cms migrate
   ```

3. **Check app is in INSTALLED_APPS:**
   ```python
   # settings/base.py
   INSTALLED_APPS = [
       ...
       'apps.blog',
   ]
   ```

---

## Server Issues

### Server Won't Start

**Problem:**
```bash
rhamaa cms run
Error: That port is already in use
```

**Solutions:**

1. **Kill existing process:**
   ```bash
   # Find process using port 8000
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   
   # Kill the process
   kill <PID>  # Mac/Linux
   taskkill /PID <PID> /F  # Windows
   ```

2. **Use different port:**
   ```bash
   python manage.py runserver 8001
   ```

3. **Check for zombie processes:**
   ```bash
   pkill -f runserver  # Kill all runserver processes
   ```

### Static Files Not Loading

**Problem:**
CSS/JS files return 404 in development.

**Solutions:**

1. **Check STATIC_URL:**
   ```python
   # settings/base.py
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [
       BASE_DIR / 'apps' / 'appname' / 'static',
   ]
   ```

2. **Run collectstatic:**
   ```bash
   python manage.py collectstatic
   ```

3. **Check debug mode:**
   ```python
   DEBUG = True  # Required for static files in development
   ```

---

## Getting Help

### Debug Output

Enable debug mode for more information:

```bash
export RHAMAA_DEBUG=1  # Linux/Mac
set RHAMAA_DEBUG=1     # Windows
rhamaa cms startapp myapp --prebuild users
```

### Check Versions

```bash
# Python
python --version

# Django
python -c "import django; print(django.__version__)"

# Wagtail
python -c "import wagtail; print(wagtail.__version__)"

# RhamaaCLI
rhamaa --version
```

### Report Issues

When reporting issues, include:

1. **RhamaaCLI version:**
   ```bash
   rhamaa --version
   ```

2. **Python version:**
   ```bash
   python --version
   ```

3. **Error message:**
   - Full traceback if available
   - Relevant log output

4. **Steps to reproduce:**
   - Exact commands used
   - Expected vs actual result

5. **Project structure:**
   ```bash
   tree -L 2  # or: find . -maxdepth 2 -type f
   ```

### Community Resources

- **GitHub Issues:** https://github.com/RhamaaCMS/RhamaaCLI/issues
- **Documentation:** https://rhamaacms.github.io/RhamaaCLI
- **PyPI:** https://pypi.org/project/rhamaa/

---

## FAQ

**Q: Can I use RhamaaCLI with existing Django projects?**
A: Yes, but ensure you have the expected directory structure (apps/ folder).

**Q: Does RhamaaCLI support Python 2?**
A: No, Python 3.7+ is required.

**Q: Can I uninstall a prebuilt app?**
A: Currently no automatic uninstall. Manually remove from apps/ and settings.

**Q: How do I update a prebuilt app?**
A: Use `--force` to overwrite, but be careful with database migrations.

**Q: Can I use RhamaaCLI without Wagtail?**
A: Yes, use `--type minimal` for pure Django apps.

---

For more help, see:
- [Commands Reference](commands.md)
- [Configuration Guide](configuration.md)
- [API Reference](api.md)
