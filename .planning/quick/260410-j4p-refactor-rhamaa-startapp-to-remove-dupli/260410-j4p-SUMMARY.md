---
phase: quick-refactor-startapp
plan: 01
subsystem: cli
tags: [refactor, startapp, templates, prebuilt, zip-security]
requires: []
provides:
  - shared ZIP extraction + apps/ install pipeline
affects:
  - rhamaa cms startapp (template + prebuilt fallback install paths)
tech_stack:
  - python
  - rich
key_files:
  created: []
  modified:
    - rhamaa/utils.py
    - rhamaa/commands/cms/startapp.py
decisions:
  - Keep manifest install path intact; refactor fallback/template placement only.
metrics:
  completed_date: 2026-04-10
---

# Phase quick-refactor-startapp Plan 01: Refactor `rhamaa cms startapp` to remove duplication — Summary

Centralized safe ZIP extraction + `apps/<app_name>` placement so template installs and prebuilt `--skip-config` fallback share the same underlying pipeline, while preserving CLI flag routing and `--force`/`--dry-run` semantics.

## What Changed

- **Shared install helpers**
  - Added `install_zip_to_apps(...)` in `rhamaa/utils.py` that performs Zip Slip-safe extraction to a temp directory and installs into `apps/<app_name>` via `install_dir_to_apps(...)`.
  - Refactored `extract_repo_to_apps(...)` to delegate to `install_zip_to_apps(...)` (keeps existing call sites intact).

- **Template install refactor**
  - `install_template_app(...)` now separates **acquisition** (local dir, local zip, URL zip, registry remote zip) from **installation into apps/** using the shared helpers.
  - ZIP cleanup is centralized to avoid double-delete and keep prior behavior for URL downloads.

- **Prebuilt fallback alignment**
  - `install_prebuilt_app(..., skip_config=True)` continues to download + extract, but extraction/placement now relies on the shared ZIP install path (via `extract_repo_to_apps` → `install_zip_to_apps`).
  - Manifest-based install path (`install_app_with_manifest`) remains unchanged.

## Verification

- Ran `python -m compileall rhamaa` after each task; compile succeeded.
- CLI routing preserved by inspection:
  - `--prebuild` continues to short-circuit template/standard creation.
  - Built-in templates `minimal|wagtail` still route to `create_standard_app(...)`.
  - `--template-url` / `--template-file` continue to install via template install path.

## Commits (code only)

- `e444cc2`: refactor(quick-refactor-startapp-01): centralize safe apps install pipeline
- `6c52c77`: refactor(quick-refactor-startapp-01): streamline template acquisition/install pipeline
- `a39ec72`: refactor(quick-refactor-startapp-01): align prebuilt fallback with shared install helpers

## Deviations from Plan

None — executed as planned.

## Threat Mitigations (from plan)

- **T-quick-01 (Zip Slip / path traversal)**: `safe_extract_zip(...)` enforces extracted paths remain within the destination root; installation moves/copies only from validated extracted directories into `apps/<app_name>`.
- **T-quick-03 (Overwrite existing app dir)**: `install_dir_to_apps(...)` enforces `--force` gating and refuses to delete outside `apps/`; `--dry-run` returns without filesystem mutations.

## Self-Check: PASSED

Confirmed:
- SUMMARY created at `.planning/quick/260410-j4p-refactor-rhamaa-startapp-to-remove-dupli/260410-j4p-SUMMARY.md`
- All three code commits exist in git history
