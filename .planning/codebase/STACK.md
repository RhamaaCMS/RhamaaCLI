# Technology Stack - RhamaaCLI

## Core Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Language | Python | 3.7+ | Runtime environment |
| CLI Framework | Click | >=8.0.0 | Command-line interface framework |
| Terminal UI | Rich | >=12.0.0 | Beautiful terminal output, progress bars, tables |
| HTTP Client | Requests | >=2.25.0 | Download repositories from GitHub |
| Build System | setuptools | >=45 | Package building and distribution |
| Version Control | setuptools_scm | >=6.2 | Git-based versioning |

## Optional Dependencies

### CMS Extras
- **Wagtail** >=5.0 - CMS framework (optional for end-users)

### Computer Vision Extras
- **ultralytics** >=8.0.0 - YOLO object detection
- **opencv-python** >=4.8.0 - Computer vision operations

### Development Extras
- **pytest** >=6.0 - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **flake8** - Linting
- **twine** - PyPI publishing
- **build** - Package building

## Package Distribution

- **PyPI Package**: `rhamaa` (v0.4.2)
- **License**: MIT
- **Entry Point**: `rhamaa` → `rhamaa.cli:main`

## Key Libraries Usage

### Click
- Command groups and subcommands (`@click.group()`)
- Argument and option parsing
- Help text generation

### Rich
- Console output with `Console()`
- ASCII art logo display with `Panel` and `Text`
- Help tables with `Table`
- Progress bars with `Progress`, `SpinnerColumn`, `BarColumn`
- Styled markdown rendering

### Requests
- GitHub repository ZIP downloads
- Streaming download with progress tracking
