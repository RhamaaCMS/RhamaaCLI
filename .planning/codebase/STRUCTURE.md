# Project Structure - RhamaaCLI

## Directory Tree

```
RhamaaCLI/
├── .planning/
│   └── codebase/              # Generated analysis documents
│       ├── STACK.md
│       ├── INTEGRATIONS.md
│       ├── ARCHITECTURE.md
│       ├── STRUCTURE.md
│       ├── CONVENTIONS.md
│       ├── TESTING.md
│       └── CONCERNS.md
├── docs/                      # Documentation (26 items)
├── scripts/                   # Utility scripts (4 items)
├── rhamaa/                    # Main package
│   ├── __init__.py            # Empty
│   ├── __main__.py            # Entry point: python -m rhamaa
│   ├── cli.py                 # Main CLI with ASCII logo
│   ├── utils.py               # Shared utilities
│   ├── commands/
│   │   ├── __init__.py        # Command registration
│   │   └── cms/               # CMS command group
│   │       ├── __init__.py    # CMS group definition
│   │       ├── build.py       # build-template command (6976 bytes)
│   │       ├── database.py    # migrate, makemigrations (622 bytes)
│   │       ├── info.py        # status, info commands (3036 bytes)
│   │       ├── management.py  # Django wrappers (1257 bytes)
│   │       ├── server.py      # run command (2185 bytes)
│   │       ├── start.py       # start command (7076 bytes)
│   │       ├── startapp.py    # startapp command (12631 bytes)
│   │       └── utils.py       # CMS utilities (614 bytes)
│   └── templates/
│       └── cms/
│           ├── APPS_TEMPLATES/
│           │   ├── minimal/     # Django app .tpl files
│           │   └── wagtail/     # Wagtail app .tpl files
│           ├── app_list.json    # Prebuilt app registry
│           └── project_template_list.json  # Project template registry
├── .git/                      # Git repository
├── .gitignore                 # Git ignore rules
├── .pypirc.template           # PyPI config template
├── LICENSE                    # MIT License (1090 bytes)
├── MANIFEST.in                # Package manifest (201 bytes)
├── README.md                  # User documentation (3744 bytes)
├── DEPLOYMENT.md              # Deployment guide (3159 bytes)
├── pyproject.toml             # Project config (2687 bytes)
├── requirements.txt           # Dependencies (66 bytes)
├── setup.py                   # Legacy setup (2212 bytes)
└── rhamaa.egg-info/           # Package metadata
```

## File Sizes and Significance

| File | Size | Significance |
|------|------|--------------|
| `startapp.py` | 12,631 bytes | Most complex command - handles app scaffolding with multiple modes |
| `start.py` | 7,076 bytes | Project creation with template handling |
| `build.py` | 6,976 bytes | Template reverse-engineering |
| `cli.py` | 5,044 bytes | Main entry with ASCII art and help |
| `utils.py` | 4,712 bytes | GitHub download and extraction utilities |
| `info.py` | 3,036 bytes | Project status and info display |
| `server.py` | 2,185 bytes | Dev/prod server management |
| `setup.py` | 2,212 bytes | Legacy package configuration |

## Module Dependencies

```
rhamaa/
├── __main__.py
│   └── imports: cli (for `python -m rhamaa`)
├── cli.py
│   └── imports: commands.cms.cms, rich.*
├── utils.py
│   └── imports: os, shutil, tempfile, zipfile, pathlib, requests, rich.progress
└── commands/
    ├── __init__.py
    │   └── imports: all cms submodules
    └── cms/
        ├── __init__.py
        │   └── imports: all cms command modules
        ├── start.py
        │   └── imports: click, requests, json, pathlib, subprocess, rich
        ├── startapp.py
        │   └── imports: click, json, pathlib, shutil, requests, rich, utils
        ├── build.py
        │   └── imports: click, pathlib, zipfile, re, shutil, json
        ├── server.py
        │   └── imports: click, subprocess, sys, rich
        ├── database.py
        │   └── imports: click, subprocess
        ├── management.py
        │   └── imports: click, subprocess
        ├── info.py
        │   └── imports: click, pathlib, json, subprocess, rich
        └── utils.py
            └── imports: click, pathlib
```

## Configuration Files

### Package Configuration (`pyproject.toml`)
- Build system: setuptools
- Project metadata: name, version (0.4.2), description
- Dependencies: click, rich, requests
- Optional extras: [cms], [cv], [dev]
- Entry point: `rhamaa = "rhamaa.cli:main"`
- Package data includes: `*.py`, templates, JSON files

### Template Registry Files

**`project_template_list.json`**
```json
{
  "base": {
    "name": "RhamaaCMS Base",
    "url": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "main"
  },
  "dev": {
    "name": "RhamaaCMS Dev",
    "url": "https://github.com/RhamaaCMS/RhamaaCMS",
    "branch": "dev"
  }
}
```

**`app_list.json`**
```json
{
  "mqtt": {
    "name": "MQTT Apps",
    "repo": "https://github.com/RhamaaCMS/rhamaa-mqtt",
    "category": "IoT"
  },
  "users": { ... },
  "articles": { ... }
}
```
