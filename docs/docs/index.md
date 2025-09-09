# Rhamaa CLI

<div align="center">
  <h2>🚀 Accelerate your Wagtail development</h2>
  <p>Simple CLI tool for Wagtail CMS development with prebuilt apps and project scaffolding.</p>
</div>

## What is Rhamaa CLI?

Rhamaa CLI streamlines Wagtail development with:

- **Quick Project Setup** - Generate Wagtail projects instantly
- **Prebuilt Apps** - Install ready-to-use applications
- **Simple Commands** - Just two main commands to remember
- **Rich UI** - Beautiful terminal interface

## Core Commands

### `rhamaa start <project>`
Create new Wagtail project with RhamaaCMS template.

### `rhamaa startapp <name>`
Create Django apps or install prebuilt apps.

## Quick Start

```bash
# Install
pip install rhamaa

# Create project
rhamaa start MyProject
cd MyProject

# Create minimal app
rhamaa startapp blog

# Create Wagtail app
rhamaa startapp pages --type wagtail

# Install prebuilt app
rhamaa startapp iot --prebuild mqtt

# List available prebuilt apps
rhamaa startapp --list
```

## Available Prebuilt Apps

- **mqtt** - IoT MQTT integration
- **users** - User management system  
- **articles** - Blog and content management
- **lms** - Learning management system
- **ecommerce** - E-commerce functionality

## Target Users

- **Wagtail Developers** looking to bootstrap projects quickly
- **Development Teams** wanting standardized project structures
- **IoT Developers** needing CMS integration with real-time capabilities
- **Educational Institutions** requiring LMS functionality

## Getting Started

Ready to accelerate your Wagtail development? Check out our [Installation Guide](getting-started/installation.md) and [Quick Start Tutorial](getting-started/quick-start.md).

---

<div align="center">
  <p><strong>Made with ❤️ by the RhamaaCMS team</strong></p>
  <p>
    <a href="https://github.com/RhamaaCMS/RhamaaCLI">GitHub</a> •
    <a href="https://pypi.org/project/rhamaa/">PyPI</a> •
    <a href="https://github.com/RhamaaCMS/RhamaaCLI/issues">Issues</a>
  </p>
</div>