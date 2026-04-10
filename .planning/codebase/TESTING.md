# Testing

**Analysis Date:** 2026-04-10

## Test Framework

**Runner:** pytest >= 6.0 (dev dependency in `pyproject.toml`)
**Coverage:** pytest-cov (dev dependency in `pyproject.toml`)

pytest configuration in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**Install dev dependencies:**
```bash
pip install -e ".[dev]"
```

## Test Structure

**No `tests/` directory exists.** The `pyproject.toml` configures pytest to look in `tests/` but no such directory is present in the repository. There are zero test files anywhere in the project.

The only testing artifacts present are:
- `if __name__ == "__main__":` blocks in three library modules serving as manual smoke tests:
  - `rhamaa/manifest.py` — creates an `AppManifest`, resolves placeholders, prints JSON
  - `rhamaa/conflict_detector.py` — builds two conflicting manifests, runs `detect_all_conflicts()`
  - `rhamaa/dependency_resolver.py` — builds a dependency graph, resolves install order

The wagtail app template generator in `rhamaa/commands/cms/startapp.py` calls `create_tests_py()` which writes a `tests.py` stub into generated apps — but that stub is for the *target Django project*, not for the CLI itself.

## Running Tests

```bash
# Run all tests (will find no tests currently)
pytest

# Run with coverage
pytest --cov=rhamaa --cov-report=html

# Run specific file (once tests exist)
pytest tests/test_manifest.py -v

# Run and show stdout
pytest -s
```

## Coverage

**Current coverage: 0%** — no automated tests exist.

## Gaps

Every module is untested. Prioritized by complexity and risk:

**Critical — complex logic with high regression risk:**

- `rhamaa/manifest.py` — `AppManifest.from_dict()`, `resolve_placeholders()`, `validate()`, `to_dict()` round-trip. The placeholder system (`{app_name}`, `{app_class}`, `{app_upper}`) is a core feature with no test coverage.
- `rhamaa/config_utils.py` — `SettingsParser` and `URLParser` regex-based file modification. These methods mutate Python source files in place. Edge cases: empty lists, already-present values, missing sections, indentation detection. Files: `rhamaa/config_utils.py`.
- `rhamaa/dependency_resolver.py` — `DependencyResolver.resolve_dependencies()` uses Kahn's topological sort. Circular dependency detection via DFS in `check_circular_dependencies()`. Both are pure algorithms with no side effects — easy to unit test.
- `rhamaa/conflict_detector.py` — `ConflictDetector.detect_all_conflicts()` aggregates five conflict types. Pure function logic, no I/O.

**High — I/O and subprocess coordination:**

- `rhamaa/utils.py` — `download_github_repo()` makes HTTP requests; `extract_repo_to_apps()` manipulates the filesystem. Both need mocking for reliable tests.
- `rhamaa/manifest_applier.py` — `ManifestApplier.apply_all()` orchestrates settings, URL, and post-install steps. `_run_post_install()` calls `subprocess.run()` for migrations and management commands.
- `rhamaa/commands/cms/startapp.py` — `create_standard_app()`, `install_prebuilt_app()`, `install_template_app()`, `process_zip_template_files()`. Core user workflow.

**Medium — CLI entry points:**

- `rhamaa/cli.py` — Click group wiring, `show_logo_and_help()` output.
- `rhamaa/commands/cms/start.py` — `start` command; template registry loading, URL validation, `wagtail start` subprocess invocation.
- `rhamaa/commands/cms/management.py` — thin wrappers over `run_manage()`; low risk but untested.

**Low — simple delegating wrappers:**

- `rhamaa/commands/cms/utils.py` — `is_django_project()`, `run_manage()` (2 functions, trivial)
- `rhamaa/commands/cms/server.py`, `database.py`, `info.py`, `build.py` — subprocess delegation commands

## Recommended Test Approach

**Use `tmp_path` fixture** (built into pytest) for all filesystem operations. No need for a separate temp directory library.

**Mock network calls** with `unittest.mock.patch` on `requests.get` in `rhamaa/utils.py`.

**Mock subprocess calls** with `unittest.mock.patch` on `subprocess.run` in command tests.

**Start with pure-logic tests** (no mocking needed):
- `AppManifest.from_dict()` / `to_dict()` round-trip
- `AppManifest.validate()` — test required-field errors, URL path validation
- `AppManifest.resolve_placeholders()` — verify `{app_name}`, `{app_class}`, `{app_upper}` substitution
- `DependencyResolver.resolve_dependencies()` — linear chain, diamond, missing dep
- `DependencyResolver.check_circular_dependencies()` — cycle vs. no cycle
- `ConflictDetector.detect_url_conflicts()` — duplicate paths
- `ConflictDetector.detect_setting_conflicts()` — same key, different values

**Then filesystem tests with `tmp_path`:**
- `SettingsParser.add_installed_app()` — write a minimal `settings.py`, parse, assert content
- `SettingsParser.add_middleware()` with `position` variants
- `URLParser.add_url_pattern()` — write minimal `urls.py`, parse, assert
- `check_wagtail_project()` — create/omit `manage.py`, assert return value
- `create_app_structure()` — verify directory and file tree created correctly

**No CI pipeline is configured.** No `.github/workflows/` directory exists.
