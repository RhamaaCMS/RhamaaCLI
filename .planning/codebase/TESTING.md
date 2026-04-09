# Testing - RhamaaCLI

## Current Testing Status

### Test Framework
- **Primary**: pytest >=6.0
- **Coverage**: pytest-cov
- **Configured in**: `pyproject.toml` (lines 105-109)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Test Directory Structure
```
RhamaaCLI/
└── tests/              # Configured but not visible in root listing
    ├── __init__.py
    ├── test_cli.py
    ├── test_commands/
    │   ├── test_start.py
    │   ├── test_startapp.py
    │   └── ...
    └── test_utils.py
```

**Note**: Tests directory was not visible in initial exploration - needs verification.

## Testing Gaps

### Areas Without Tests

| Component | Test Coverage | Risk Level |
|-----------|---------------|------------|
| `cli.py` | Unknown | Low (UI only) |
| `start.py` | Unknown | High (core feature) |
| `startapp.py` | Unknown | High (complex logic) |
| `build.py` | Unknown | Medium |
| `utils.py` | Unknown | High (network/IO) |
| `server.py` | Unknown | Low |
| `database.py` | Unknown | Low |
| `management.py` | Unknown | Low |
| `info.py` | Unknown | Low |

### Critical Untested Paths

1. **GitHub Download Failure** - `download_github_repo()` network error handling
2. **ZIP Extraction Edge Cases** - Corrupted ZIPs, permission errors
3. **Template Placeholder Substitution** - Complex replacement logic
4. **Project Validation** - `check_wagtail_project()` edge cases
5. **Subprocess Wrappers** - Django command failure scenarios

## Recommended Test Cases

### Unit Tests

#### `test_utils.py`
```python
def test_check_wagtail_project_with_manage_py(tmp_path):
    """Should return True if manage.py exists."""
    (tmp_path / "manage.py").touch()
    # Test implementation

def test_download_github_repo_invalid_url():
    """Should handle 404 errors gracefully."""
    # Mock requests.get to return 404
    # Assert returns None and prints error

def test_extract_repo_to_apps_success(tmp_path):
    """Should extract ZIP to apps/<app_name>/."""
    # Create test ZIP, extract, verify structure
```

#### `test_startapp.py`
```python
def test_startapp_minimal_creates_structure(tmp_path):
    """Should create apps/<name>/ with standard Django files."""
    
def test_startapp_wagtail_includes_blocks_py(tmp_path):
    """Should include Wagtail-specific files."""
    
def test_startapp_prebuild_downloads_from_github(tmp_path):
    """Should download and extract prebuilt app."""
    # Mock github download
```

#### `test_start.py`
```python
def test_start_project_with_template_url(tmp_path):
    """Should use custom template URL."""
    
def test_start_project_invalid_name():
    """Should reject invalid Python identifiers."""
```

### Integration Tests

```python
def test_full_workflow_create_project_and_app(tmp_path):
    """
    1. Create project with rhamaa cms start
    2. Create app with rhamaa cms startapp
    3. Verify both are functional
    """
```

## Testing Commands

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=rhamaa --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_utils.py -v
```

## CI/CD Testing

### Recommended GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=rhamaa
```

## Code Quality Tools

| Tool | Purpose | Config Location |
|------|---------|-----------------|
| black | Code formatting | `pyproject.toml` [tool.black] |
| flake8 | Linting | Not configured (needs setup.cfg) |
| pytest-cov | Coverage | `pyproject.toml` |

## Testing Debt

### Immediate Actions Needed
1. Verify `tests/` directory exists
2. Add unit tests for `utils.py` functions
3. Add integration tests for `start` and `startapp`
4. Mock external network calls (GitHub downloads)
5. Add test fixtures for template files

### Estimated Coverage Needed
- Minimum target: 70% code coverage
- Critical paths: 90% coverage (utils.py, startapp.py, start.py)
