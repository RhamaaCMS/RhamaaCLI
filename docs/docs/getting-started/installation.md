# Installation

This guide will help you install Rhamaa CLI on your system.

## Prerequisites

Before installing Rhamaa CLI, make sure you have:

- **Python 3.7+** installed on your system
- **pip** package manager
- **Wagtail** installed (for creating projects)

!!! tip "Check Python Version"
    ```bash
    python --version
    # or
    python3 --version
    ```

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Install the latest stable version from PyPI:

```bash
pip install rhamaa
```

For the latest pre-release version:

```bash
pip install --pre rhamaa
```

### Method 2: Install Specific Version

Install a specific version:

```bash
pip install rhamaa==0.1.0b1
```

### Method 3: Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/RhamaaCMS/RhamaaCLI.git
cd RhamaaCLI

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Verify Installation

After installation, verify that Rhamaa CLI is working:

```bash
rhamaa --help
```

You should see the Rhamaa CLI logo and help information.

## Installing Wagtail (Required)

Rhamaa CLI requires Wagtail to create new projects. Install it globally:

```bash
pip install wagtail
```

Or install it in your virtual environment where you plan to work.

## Virtual Environment Setup

It's recommended to use virtual environments for your projects:

```bash
# Create a new virtual environment
python -m venv myproject-env

# Activate it
# On Linux/Mac:
source myproject-env/bin/activate
# On Windows:
# myproject-env\Scripts\activate

# Install Rhamaa CLI and Wagtail
pip install rhamaa wagtail
```

## Troubleshooting

### Permission Errors

If you encounter permission errors on Linux/Mac:

```bash
pip install --user rhamaa
```

### Command Not Found

If `rhamaa` command is not found after installation:

1. Check if the installation directory is in your PATH
2. Try using `python -m rhamaa` instead
3. Reinstall with `--user` flag

### Python Version Issues

Rhamaa CLI requires Python 3.7+. If you have multiple Python versions:

```bash
python3 -m pip install rhamaa
```

## Next Steps

Once installed, proceed to the [Quick Start Guide](quick-start.md) to create your first project.

## Updating

To update to the latest version:

```bash
pip install --upgrade rhamaa
```

To check your current version:

```bash
pip show rhamaa
```