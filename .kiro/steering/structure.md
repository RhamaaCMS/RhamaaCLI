# Project Structure

## Root Directory
```
rhamaa/
├── .git/                    # Git repository
├── .kiro/                   # Kiro IDE configuration
├── .venv/                   # Python virtual environment
├── .vscode/                 # VS Code settings
├── rhamaa/                  # Main package directory
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies (currently empty)
├── setup.py                 # Package configuration
└── .gitignore              # Git ignore rules
```

## Package Architecture (`rhamaa/`)
```
rhamaa/
├── __init__.py             # Package initialization
├── cli.py                  # Main CLI entry point and help system
└── commands/               # Command modules directory
    ├── __init__.py         # Commands package init
    ├── add.py              # 'add' command implementation
    └── start.py            # 'start' command implementation
```

## Architectural Patterns

### Command Structure
- **Main CLI** (`cli.py`): Contains the main Click group, ASCII logo, and help system
- **Command Modules** (`commands/`): Each subcommand gets its own module
- **Rich Integration**: All user output uses Rich console for consistent styling

### File Organization Rules
- One command per file in `commands/` directory
- Command files should be named after the command they implement
- Each command module exports a single Click command function
- Import and register commands in `cli.py` using `main.add_command()`

### Naming Conventions
- Package name: `rhamaa` (lowercase)
- Command functions: Match command name (e.g., `start`, `add`)
- Module files: Lowercase, match command name
- Console variable: Always named `console` for Rich Console instances

### Dependencies Management
- Core dependencies defined in `setup.py`
- Development dependencies can be added to `requirements.txt`
- Use `install_requires` in setup.py for package dependencies