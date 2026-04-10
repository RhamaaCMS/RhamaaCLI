# Technical Concerns

**Analysis Date:** 2026-04-10

---

## Critical Issues

**No test suite exists:**
- The `pyproject.toml` declares `testpaths = ["tests"]` but the `tests/` directory does not exist on disk.
- There are zero test files anywhere in the project (`test_*.py`, `*_test.py`).
- Every module — including the file-modifying `SettingsParser`, `URLParser`, regex-based `ManifestApplier`, and `DependencyResolver` — runs completely untested.
- Impact: Any regression in regex-based settings/URL manipulation silently corrupts user project files.
- Fix: Create `tests/` and add unit tests for `rhamaa/config_utils.py`, `rhamaa/manifest.py`, `rhamaa/dependency_resolver.py`, and `rhamaa/conflict_detector.py` at minimum.

**Regex-based settings/URL mutation is fragile:**
- `SettingsParser` and `URLParser` in `rhamaa/config_utils.py` use `re.sub` with `re.DOTALL` to modify live Django `settings.py` and `urls.py` files.
- The patterns (`INSTALLED_APPS\s*=\s*\[.*?\]`, `urlpatterns\s*=\s*\[.*?\]`) will silently fail or produce corrupt output on settings files that use non-standard formatting: multiline string joins, conditional blocks (`if DEBUG:`), settings split across multiple files, or tuple-style `INSTALLED_APPS = (...)`.
- If the regex finds no match, the function returns `False` with no user warning and the write never happens — the failure is invisible.
- Files: `rhamaa/config_utils.py` lines 28–58 (`add_installed_app`), lines 60–140 (`add_middleware`), lines 448–509 (`add_url_config`).
- Impact: Silent no-op on complex settings files; partial writes on edge cases.
- Fix: Add pre-flight validation and explicit failure messaging; consider using `ast` parsing instead of regex for Python files.

**`_ensure_include_import` is incomplete:**
- `URLParser._ensure_include_import` in `rhamaa/config_utils.py` (lines 533–540) only patches the exact string `'from django.urls import path'`. Any other import form (`from django.urls import path, re_path` etc.) will not be patched, leaving `include` missing from the import, which causes a `NameError` at runtime in the user's project.
- Files: `rhamaa/config_utils.py` lines 533–540.

**`install_app_with_manifest` uses `Path.cwd()` as the project root:**
- `rhamaa/manifest_applier.py` line 382: `project_path = Path.cwd()`. The CLI assumes it is always run from the Django project root. If the user runs `rhamaa` from any other directory the entire manifest applier targets the wrong tree and writes settings/URL changes to wrong files (or silently does nothing).
- No guard or validation exists to confirm `manage.py` is present at `cwd` before writing files.
- Files: `rhamaa/manifest_applier.py` lines 382, 68–70; `rhamaa/config_utils.py` `auto_configure_app`.

**`rollback` is unreliable:**
- `ManifestApplier.rollback()` in `rhamaa/manifest_applier.py` (lines 337–356) restores `.py.bak` files only if they were created during the same process run. If the process crashes mid-apply the `self.backup_files` list is lost, leaving the user with no automated recovery path.
- Backup path construction in `_apply_settings`/`_apply_urls` stores the backup path in `self.backup_files` but calls `parser.write(backup=backup)` which creates a `.py.bak` at a different computed path — the two paths may diverge when `self.settings_file` has no `.py` suffix already.
- Files: `rhamaa/manifest_applier.py` lines 200–204, 230–234, 337–356.

---

## Security Risks

**Unvalidated fixture paths from remote manifests:**
- `manifest_applier.py` `_run_post_install` (lines 273–289) applies `fixture_path.replace('{app_name}', ...)` substitution on content read from a remote `rhamaa-app.json`. A malicious manifest could set a fixture path to `../../secret`, producing a path traversal in `loaddata`.
- Files: `rhamaa/manifest_applier.py` lines 273–289.
- Fix: Validate fixture paths and management command names against a whitelist pattern (no `..`, no absolute paths, alphanumeric with underscores/slashes only).

**Remote ZIP extraction without integrity verification:**
- `utils.py` `download_github_repo` performs an unauthenticated HTTP GET and `extract_repo_to_apps` extracts the result directly into the user's project `apps/` directory. There is no checksum, signature, or size limit validation.
- A compromised or man-in-the-middle response injects arbitrary Python files into the user's Django project.
- Files: `rhamaa/utils.py` lines 17–63, 66–121.
- Fix: Add SHA256 checksum verification (the registry JSON could include expected hashes); enforce HTTPS; add max download size limit.

**No HTTPS enforcement on template URLs:**
- `start.py` checks `template_url.lower().startswith(("http://", "https://"))` (line 136) but accepts `http://`. An HTTP URL is vulnerable to MITM injection of arbitrary template code.
- Files: `rhamaa/commands/cms/start.py` line 136.
- Fix: Reject plain `http://` URLs.

**ZIP path traversal (Zip Slip):**
- `extract_repo_to_apps` in `rhamaa/utils.py` calls `zip_ref.extractall(temp_extract_dir)` on an untrusted ZIP file without sanitizing archive member names. Entries with `../` in their names could write files outside the temp directory.
- Files: `rhamaa/utils.py` lines 101–102.
- Fix: Validate all archive member paths before extraction.

**`set_setting` writes arbitrary repr'd values to settings.py:**
- `SettingsParser.set_setting` in `rhamaa/config_utils.py` (lines 274–315) serializes the `value` from the manifest using `repr()`. A manifest with injected content in a settings value will be written verbatim into the user's `settings.py`.
- Files: `rhamaa/config_utils.py` lines 274–315.

---

## Technical Debt

**`check_wagtail_project` does not actually check for Wagtail:**
- `rhamaa/utils.py` lines 128–149: The function is named `check_wagtail_project` but returns `True` if `manage.py`, `requirements.txt`, `setup.py`, or `pyproject.toml` exist — it is effectively `is_python_project()`. The function is not used as a gate anywhere in the command flow despite being imported.

**`run_manage` hardcodes `python` instead of `sys.executable`:**
- `rhamaa/commands/cms/utils.py` line 14: `subprocess.run(['python', 'manage.py'] + args, ...)`. On systems where the active Python is reached via `python3`, `py`, or a virtualenv, this may invoke the wrong interpreter.
- `rhamaa/manifest_applier.py` correctly uses `sys.executable` (lines 249, 261, 279, 304), but the CMS management commands do not.
- Files: `rhamaa/commands/cms/utils.py` line 14.

**`detect_installed_apps_conflicts` is a stub:**
- `ConflictDetector.detect_installed_apps_conflicts` in `rhamaa/conflict_detector.py` (lines 286–323) has a `for package in packages: pass` loop with a comment "simplified check - in real scenario, parse semver". The version conflict check does nothing.
- Files: `rhamaa/conflict_detector.py` lines 312–323.

**`get_safe_install_order` in `ConflictDetector` does not use `DependencyResolver`:**
- `rhamaa/conflict_detector.py` lines 346–364 has a comment: "Full implementation would integrate with DependencyResolver". The two systems exist in parallel but are not wired together.
- Files: `rhamaa/conflict_detector.py` lines 346–364.

**`--type` flag in `startapp` is marked deprecated but kept:**
- `rhamaa/commands/cms/startapp.py` line 81: `help='App template type (deprecated, use --template)'`. The deprecated option is still active, adding confusion.

**`DEFAULT_LOCAL_TEMPLATE` is hard-coded to a sibling directory:**
- `rhamaa/commands/cms/start.py` line 17: `DEFAULT_LOCAL_TEMPLATE = (CLI_ROOT.parent / "RhamaaCMS").resolve()`. This path only exists on the original developer's machine and will silently produce a path-not-found error for all other users.
- Files: `rhamaa/commands/cms/start.py` line 17.

**`gitpython` is in `requirements.txt` but not in `setup.py`/`pyproject.toml`:**
- `requirements.txt` lists `gitpython>=3.1.0` but it does not appear in `install_requires` in either `setup.py` or `pyproject.toml`. Users installing via `pip install rhamaa` will not get `gitpython`. Searching the source finds no `import git` anywhere — the dependency appears entirely unused.
- Files: `requirements.txt`, `setup.py` lines 38–42, `pyproject.toml` lines 35–39.

**Inline `__main__` blocks used as the only integration examples:**
- `rhamaa/manifest.py` lines 371–391, `rhamaa/conflict_detector.py` lines 368–404, and `rhamaa/dependency_resolver.py` lines 239–266 each contain `if __name__ == "__main__":` blocks with inline demos. These are not automated, not verified, and will drift from the API.

---

## Missing Capabilities

**No manifest schema validation beyond field presence:**
- `AppManifest.validate()` in `rhamaa/manifest.py` (lines 294–327) checks only that `name`, `slug`, URL `path`, and `include` are non-empty. It does not validate: Python dotted-path syntax for `installed_apps`/`middleware`/`auth_backends`; version strings; URL path format beyond trailing `/`; or that `position` strings follow the `after:X`/`before:X` convention.

**No automatic rollback on partial failure during `apply_all`:**
- `ManifestApplier.apply_all` in `rhamaa/manifest_applier.py` applies settings, then URLs, then post-install in sequence. If step 2 (URL apply) fails after step 1 (settings write) has already been committed to disk, the project is left in a partially-configured state. The `rollback()` method exists but is never called automatically on failure.
- Files: `rhamaa/manifest_applier.py` lines 83–143.

**No atomic writes for settings/URL mutations:**
- `SettingsParser.write()` and `URLParser.write()` in `rhamaa/config_utils.py` (lines 378–384, 542–548) write directly to the target file. If the process is interrupted mid-write the file is left truncated. No atomic rename pattern (write to temp, then `os.replace`) is used.

**Prebuilt app registry is static and bundled:**
- `rhamaa/templates/cms/app_list.json` contains only 3 apps (mqtt, users, articles) and is updated only by releasing a new version of the CLI. There is no mechanism to refresh the registry from a remote source or to add third-party registries.

**`find_settings_file` does not exclude virtualenv/non-project directories:**
- `rhamaa/config_utils.py` lines 589–601 iterates every non-hidden top-level subdirectory and appends four candidate settings paths per directory. It does not skip `venv`, `node_modules`, `.tox`, or other non-project directories and may pick the wrong settings file.

**No download timeout on HTTP requests:**
- `requests.get(zip_url, stream=True)` in `rhamaa/utils.py` line 41 has no `timeout` parameter. A slow or stalled server hangs the CLI indefinitely.
- Fix: Add `timeout=(10, 60)` to all `requests.get` calls.

**Temp file leak on download failure:**
- `download_github_repo` in `rhamaa/utils.py` creates a `NamedTemporaryFile` (line 45) but has no `finally` block to clean it up on exception. If `requests.RequestException` is raised after the file is created, the temp file is never deleted.
- Files: `rhamaa/utils.py` lines 44–63.

---

## Dependency Risks

**All runtime dependencies have no upper-bound pin:**
- `click>=8.0.0`, `rich>=12.0.0`, `requests>=2.25.0` have no upper bounds. Future breaking versions install silently.

**Python 3.7/3.8 support claim is stale:**
- `pyproject.toml` claims `python_requires=">=3.7"`. Python 3.7 reached end-of-life in June 2023 and 3.8 in October 2024. No CI matrix tests these versions.

**`wagtail>=5.0` in `extras_require` has no upper bound:**
- Wagtail releases breaking changes across minor versions. No upper bound guards against future incompatibility.

**`gitpython>=3.1.0` in `requirements.txt` appears unused:**
- No source file imports `git`. The package adds install weight and attack surface with no apparent benefit.

---

## Scalability Concerns

**`replace_slug_tokens` reads every file in the project including binaries:**
- `rhamaa/commands/cms/build.py` `replace_slug_tokens` (lines 151–167) iterates `project_copy.rglob("*")` and attempts to read every file as UTF-8. Binary assets are not pre-filtered, causing a `UnicodeDecodeError` (caught silently via `continue`) for each one. On large projects this is slow and wastes I/O.

**No caching of downloaded apps or templates:**
- Every `rhamaa cms startapp --prebuild` invocation re-downloads the full ZIP from GitHub. No local cache directory (e.g. `~/.rhamaa/cache/`) is used.

**Single-threaded, no concurrency:**
- All download, extraction, and file mutation operations are single-threaded. For large templates this blocks the terminal with no progress feedback beyond the Rich spinner.

---

*Concerns audit: 2026-04-10*
