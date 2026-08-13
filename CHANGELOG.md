# Changelog

All notable changes to RhamaaCLI are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-08-13

### Added

- Current-only version tracking for registered Rhamaa apps.
- `rhamaa cms apps list`, `check`, and `update` workflows for inspecting and
  updating installed prebuilt apps.
- Standard `rhamaa-app.json` manifests for generated and installed apps.
- Manifest-based installation with settings, URL, middleware, dependency, and
  migration integration.
- Conflict detection, dependency resolution, dry-run support, and optional
  backups for app installation and updates.
- Support for installing prebuilt apps from custom GitHub repositories.
- IoT app registry integration and validation of local app identity/version
  against the remote registry.
- Project template registry with default, IoT, Inertia React, and Inertia
  Next.js template variants.
- ZIP URL, local ZIP, and local directory sources for project templates.
- `rhamaa cms build-template` improvements, including automatic WSGI app
  detection and Django `SECRET_KEY` replacement.
- Expanded command, configuration, manifest, template, API, example, and
  troubleshooting documentation.

### Changed

- Consolidated prebuilt app acquisition and installation into one safer shared
  pipeline.
- App updates now install the current registry release; users do not select an
  arbitrary historical app version.
- Backups are opt-in through `--backup` instead of being created by default.
- Settings detection now supports layouts such as `project/settings/base.py`.
- Generated app scaffolds now receive a standard app manifest automatically.
- Improved middleware and URL configuration formatting.
- Production server startup now detects the WSGI module automatically.
- Updated the IoT app installation flow to use the app manifest contract.
- Removed the unused `gitpython` runtime dependency.
- Refreshed CLI output, path feedback, documentation, and package metadata.

### Removed

- Legacy template-install flags superseded by the unified source and manifest
  installation flow.
- Obsolete planning and duplicated documentation files.
- Version pinning from the production upload helper's post-release install
  command.

### Migration notes

- Existing app installations should be checked with `rhamaa cms apps check`
  before running an update.
- Commit or back up project changes before updating an app. Use `--backup` when
  a CLI-created backup is required.
- App repositories should expose the current version and installation metadata
  through `rhamaa-app.json`.

## [0.4.2] - 2025-12-22

### Changed

- Updated package metadata, author contact, and CMS package-data paths.

[Unreleased]: https://github.com/RhamaaCMS/RhamaaCLI/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/RhamaaCMS/RhamaaCLI/compare/v0.4.2...v0.5.0
[0.4.2]: https://github.com/RhamaaCMS/RhamaaCLI/releases/tag/v0.4.2
