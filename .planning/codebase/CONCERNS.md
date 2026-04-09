# Known Concerns - RhamaaCLI

## Technical Debt

### 1. Template Placeholder System
**Issue**: Simple string replacement is fragile
```python
# Current implementation (assumed)
template.replace('{{app_name}}', app_name)
```
**Risk**: Multiple placeholder variations (`{{app_name|upper}}`, `{{app_name|title}}`) require manual handling
**Impact**: Medium - Could miss edge cases
**Mitigation**: Consider proper templating engine (Jinja2) for complex templates

### 2. Network Dependency for Core Workflow
**Issue**: Prebuilt app installation requires GitHub connectivity
```python
# In utils.py - no offline fallback
def download_github_repo(repo_url, branch="main", ...)
```
**Risk**: Users without internet cannot use `--prebuild` feature
**Impact**: Medium - Affects core value proposition
**Mitigation**: Cache downloaded apps locally, provide offline mode

### 3. Subprocess Error Handling
**Issue**: Wrapped Django commands may fail silently
```python
# In database.py, management.py
subprocess.run([sys.executable, "manage.py", "migrate"], check=False)
```
**Risk**: `check=False` means failures don't raise exceptions
**Impact**: Medium - Users may not know migrations failed
**Mitigation**: Check return codes, provide clear error messages

### 4. Hardcoded Path Conventions
**Issue**: Assumes `apps/` folder structure
```python
# In startapp.py
apps_dir = Path("apps")
```
**Risk**: May not work with custom Django project structures
**Impact**: Low-Medium - Limits flexibility
**Mitigation**: Detect apps folder or make configurable

## Security Concerns

### 5. Unverified Downloads
**Issue**: Downloads ZIP files from GitHub without verification
```python
response = requests.get(zip_url, stream=True)
# No checksum verification
```
**Risk**: MITM attacks could inject malicious code
**Impact**: Medium-High - Downloads executable code
**Mitigation**: Add checksum verification, use HTTPS with cert pinning

### 6. Force Overwrite Without Confirmation
**Issue**: `--force` flag can delete existing apps
```python
if app_dir.exists():
    shutil.rmtree(app_dir)  # In extract_repo_to_apps
```
**Risk**: Data loss if user accidentally overwrites
**Impact**: Medium - Destructive operation
**Mitigation**: Add backup option, require explicit confirmation

## Maintainability Issues

### 7. Template File Duplication
**Issue**: `.tpl` files stored in package, may drift from source
**Risk**: Template updates require package release
**Impact**: Low - Release process handles this
**Mitigation**: Consider dynamic template fetching

### 8. Version Management
**Issue**: Version in `pyproject.toml` (0.4.2) may drift from git tags
```toml
[project]
version = "0.4.2"  # Hardcoded
```
**Risk**: setuptools_scm may conflict with hardcoded version
**Impact**: Low - Build system handles this
**Mitigation**: Remove version from pyproject.toml if using setuptools_scm

## Documentation Gaps

### 9. Missing Architecture Documentation
**Issue**: No developer docs for contributing new commands
**Impact**: Medium - Barriers to contribution
**Mitigation**: Add CONTRIBUTING.md with architecture overview

### 10. Template Authoring Guide Missing
**Issue**: No docs on how to create `.tpl` files
**Impact**: Low - Internal use primarily
**Mitigation**: Document placeholder syntax and conventions

## Performance Concerns

### 11. Synchronous Downloads
**Issue**: GitHub repo downloads block CLI
```python
# In utils.py
response = requests.get(zip_url, stream=True)
# No async/await
```
**Impact**: Low - Downloads are typically fast (<5s)
**Mitigation**: Not critical for CLI tool

### 12. No Download Caching
**Issue**: Same prebuilt apps downloaded repeatedly
**Impact**: Low - Minor bandwidth waste
**Mitigation**: Add local cache in `~/.rhamaa/cache/`

## Testing Concerns

### 13. Test Coverage Unknown
**Issue**: No visible test suite in repository
**Risk**: Regressions may go undetected
**Impact**: Medium-High - Quality assurance
**Mitigation**: Add comprehensive test suite (see TESTING.md)

### 14. No Integration Tests for External Services
**Issue**: GitHub download tests would require network
**Impact**: Medium - Tests may be flaky
**Mitigation**: Mock requests for unit tests, integration tests for CI

## Compatibility Risks

### 15. Python 3.7 Support
**Issue**: Supporting 3.7+ limits modern Python features
```toml
requires-python = ">=3.7"
```
**Risk**: Cannot use walrus operator, match statements, etc.
**Impact**: Low - Codebase is simple
**Mitigation**: Evaluate if 3.7 support still needed (EOL June 2023)

### 16. Wagtail Version Compatibility
**Issue**: Assumes Wagtail 5.0+ structure
```toml
[project.optional-dependencies]
cms = ["wagtail>=5.0"]
```
**Risk**: Template structure may change in future Wagtail versions
**Impact**: Medium - May break project creation
**Mitigation**: Test against multiple Wagtail versions

## Recommended Priority Actions

### High Priority
1. Add subprocess error handling with proper return code checks
2. Implement download verification (checksums)
3. Create test suite with mocked external calls

### Medium Priority
4. Add backup before force overwrite
5. Document template authoring
6. Add local download cache

### Low Priority
7. Evaluate Python 3.7 support continuation
8. Add async download option
9. Make apps folder path configurable
