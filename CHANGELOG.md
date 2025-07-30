# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0b4] - 2024-01-XX

### Added

- **Template System**: Multiple project templates (default, blog, e-commerce, portfolio, corporate, IoT, education)
- **Current Directory Support**: Create projects in existing directories with `rhamaa start MyProject .`
- **Template Registry**: Centralized template management with `rhamaa registry templates`
- **Template Info Command**: Get detailed template information with `rhamaa registry template <name>`
- **Development Mode**: Use local templates with `--dev` flag for development
- **Wagtail Dependency**: Wagtail now included as core dependency
- **Modular Registry**: Restructured registry system with separate app and template modules

### Changed

- **Project Structure**: Moved registry files to `rhamaa/registry/` directory
- **Import System**: Cleaner imports from `rhamaa.registry`
- **Command Syntax**: Enhanced `start` command with template options
- **Documentation**: Comprehensive README update with all new features

### Fixed

- **Current Directory Creation**: Improved logic for creating projects in existing directories
- **Error Handling**: Better error messages and validation
- **Template URL Handling**: Proper template URL resolution

## [0.1.0b3] - 2024-01-XX

### Added

- **App Registry System**: Centralized registry of prebuilt applications
- **Auto Installation**: Download and install apps directly from GitHub repositories
- **Rich Terminal UI**: Beautiful ASCII art branding and colored output
- **Progress Indicators**: Real-time download and installation progress

### Features

- **Available Apps**: mqtt, users, articles, lms
- **Registry Commands**: `rhamaa registry list`, `rhamaa registry info <app>`
- **Force Install**: Overwrite existing apps with `--force` flag
- **Project Validation**: Automatic detection of Wagtail projects

## [0.1.0b2] - 2024-01-XX

### Added

- **Basic CLI Structure**: Main CLI entry point with Click framework
- **Project Creation**: Basic `rhamaa start` command
- **Command System**: Modular command architecture

## [0.1.0b1] - 2024-01-XX

### Added

- **Initial Release**: Basic CLI framework
- **Project Scaffolding**: Initial project creation functionality
