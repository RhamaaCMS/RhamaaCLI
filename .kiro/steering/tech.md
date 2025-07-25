# Technology Stack

## Core Dependencies
- **Click**: Command-line interface framework for Python
- **Rich**: Terminal formatting and styling library for enhanced UX
- **Wagtail**: Django-based CMS framework (primary target platform)

## Build System
- **setuptools**: Package building and distribution
- **Python 3.7+**: Minimum Python version requirement

## Package Structure
- Entry point: `rhamaa.cli:main`
- Console script: `rhamaa` command
- Modular command architecture under `rhamaa/commands/`

## Common Commands

### Development Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .
```

### Testing the CLI
```bash
# Test main command
rhamaa

# Test project creation
rhamaa start TestProject

# Test app addition
rhamaa add users
```

### Package Building
```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/rhamaa-*.whl
```

## Code Style Guidelines
- Use Rich console for all user-facing output
- Implement commands as separate modules in `rhamaa/commands/`
- Follow Click decorators pattern for command definition
- Use subprocess for external tool integration (wagtail command)