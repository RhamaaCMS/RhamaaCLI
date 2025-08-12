# Registry System

The Rhamaa CLI registry system manages the catalog of available prebuilt applications. This section covers all registry-related commands and how the system works.

## Registry Commands

### `rhamaa registry`

The main registry command group provides access to app catalog management.

```bash
rhamaa registry <subcommand>
```

## Listing Apps

### `rhamaa registry list`

Display all apps in the registry, organized by category.

```bash
rhamaa registry list
```

#### Output Format

The command shows apps grouped by category with detailed information:

```
IoT
┌──────────┬─────────────────────┬──────────────────────────────────┬─────────────────────────────────────┐
│ App      │ Name                │ Description                      │ Repository                          │
├──────────┼─────────────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ mqtt     │ MQTT Apps           │ IoT MQTT integration for Wagtail│ https://github.com/RhamaaCMS/mqtt-apps │
└──────────┴─────────────────────┴──────────────────────────────────┴─────────────────────────────────────┘

Authentication
┌──────────┬─────────────────────┬──────────────────────────────────┬─────────────────────────────────────┐
│ App      │ Name                │ Description                      │ Repository                          │
├──────────┼─────────────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ users    │ User Management     │ Advanced user management system  │ https://github.com/RhamaaCMS/users-app │
└──────────┴─────────────────────┴──────────────────────────────────┴─────────────────────────────────────┘
```

#### Categories

Apps are organized into these categories:

- **IoT**: Internet of Things and device management
- **Authentication**: User management and authentication
- **Content**: Content management and publishing
- **Education**: Learning management and educational tools

## App Information

### `rhamaa registry info`

Get detailed information about a specific app.

```bash
rhamaa registry info <app_name>
```

#### Example

```bash
rhamaa registry info mqtt
```

#### Output

```
┌─────────────────────────────────────────────────────────────────┐
│                              mqtt                               │
├─────────────────────────────────────────────────────────────────┤
│ MQTT Apps                                                       │
│                                                                 │
│ Description: IoT MQTT integration for Wagtail                  │
│ Category: IoT                                                   │
│ Repository: https://github.com/RhamaaCMS/mqtt-apps             │
│ Branch: main                                                    │
│                                                                 │
│ Install with: rhamaa add mqtt                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Information Provided

- **App Name**: Display name of the application
- **Description**: Detailed description of functionality
- **Category**: The app's category classification
- **Repository**: GitHub repository URL
- **Branch**: Git branch used for installation
- **Install Command**: Quick reference for installation

## Registry Structure

### App Registry Format

Each app in the registry contains:

```python
"app_key": {
    "name": "Display Name",
    "description": "Detailed description",
    "repository": "https://github.com/RhamaaCMS/app-repo",
    "branch": "main",
    "category": "Category Name"
}
```

### Current Registry

The current registry includes:

#### IoT Category

- **mqtt**: MQTT integration for IoT devices and real-time messaging

#### Authentication Category

- **users**: Advanced user management with profiles and permissions

#### Content Category

- **articles**: Blog and article management system with rich content features

#### Education Category

- **lms**: Complete Learning Management System with courses and assessments

## Registry Updates

### `rhamaa registry update`

Update the app registry (planned feature).

```bash
rhamaa registry update
```

Currently shows:

```
Registry update functionality will be implemented in future versions.
Currently, the registry is built into the CLI.
```

#### Future Features

- **Remote Registry**: Fetch registry from remote sources
- **Custom Registries**: Add custom app repositories
- **Version Management**: Track app versions and updates
- **Dependency Resolution**: Handle app dependencies automatically

## How the Registry Works

### Built-in Registry

The current registry is built into the CLI in `rhamaa/registry.py`:

```python
APP_REGISTRY = {
    "mqtt": {
        "name": "MQTT Apps",
        "description": "IoT MQTT integration for Wagtail",
        "repository": "https://github.com/RhamaaCMS/mqtt-apps",
        "branch": "main",
        "category": "IoT"
    },
    # ... more apps
}
```

### Registry Functions

The registry system provides these functions:

- `get_app_info(app_name)`: Get information about a specific app
- `list_available_apps()`: Get all available apps
- `is_app_available(app_name)`: Check if an app exists

### App Resolution

When you install an app:

1. **Lookup**: CLI searches the registry for the app name
2. **Validation**: Checks if the app exists and is available
3. **Repository Access**: Uses the repository URL for download
4. **Branch Selection**: Downloads from the specified branch

## Adding Apps to Registry

### For Contributors

To add a new app to the registry, edit `rhamaa/registry.py`:

```python
APP_REGISTRY = {
    # ... existing apps
    "your_app": {
        "name": "Your App Name",
        "description": "Description of your app functionality",
        "repository": "https://github.com/RhamaaCMS/your-app",
        "branch": "main",
        "category": "Appropriate Category"
    }
}
```

### Requirements for Registry Apps

Apps must meet these requirements:

1. **GitHub Repository**: Hosted on GitHub with public access
2. **Standard Structure**: Follow Django app conventions
3. **Documentation**: Include README with setup instructions
4. **Wagtail Compatibility**: Work with current Wagtail versions
5. **License**: Include appropriate open-source license

### App Categories

Choose the appropriate category:

- **IoT**: Device management, sensors, real-time data
- **Authentication**: User management, permissions, profiles
- **Content**: Publishing, blogs, media management
- **Education**: Learning, courses, assessments
- **E-commerce**: Shopping, payments, inventory
- **Analytics**: Reporting, statistics, monitoring

## Registry API

### Python API

You can use the registry programmatically:

```python
from rhamaa.registry import get_app_info, list_available_apps

# Get all apps
apps = list_available_apps()

# Get specific app info
mqtt_info = get_app_info('mqtt')
```

### Command Line Integration

The registry integrates with other commands:

```bash
# List apps (uses registry)
rhamaa add --list

# Install app (uses registry)
rhamaa add mqtt

# Get app info (uses registry)
rhamaa registry info mqtt
```

## Best Practices

### For Users

1. **Explore Registry**: Use `registry list` to discover apps
2. **Read Information**: Check `registry info` before installing
3. **Verify Compatibility**: Ensure apps work with your Wagtail version
4. **Check Dependencies**: Review app requirements

### For Developers

1. **Follow Conventions**: Use standard Django app structure
2. **Document Thoroughly**: Provide clear README and setup instructions
3. **Test Compatibility**: Ensure apps work with multiple Wagtail versions
4. **Maintain Quality**: Keep apps updated and bug-free

## Troubleshooting

### App Not Found

If `registry info` shows "App not found":

1. Check spelling of the app name
2. Use `registry list` to see available apps
3. Verify the app exists in the current registry

### Registry Access Issues

If registry commands fail:

1. Check CLI installation
2. Verify Python environment
3. Update to latest CLI version

## Future Enhancements

### Planned Features

- **Remote Registry**: Fetch from external sources
- **Version Control**: Track app versions and updates
- **Custom Sources**: Add private or custom registries
- **Dependency Management**: Handle app dependencies
- **Rating System**: Community ratings and reviews

### Community Contributions

The registry will expand with community contributions:

- Submit apps through GitHub pull requests
- Follow contribution guidelines
- Maintain app quality standards
- Provide ongoing support

## Next Steps

- Explore [Available Apps](../apps/index.md) in detail
- Learn about [App Management](app-management.md)
- Check [Development Guide](../development/contributing.md) for contributing apps