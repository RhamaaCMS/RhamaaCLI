"""
App Registry for RhamaaCLI
Contains the list of available prebuilt applications that can be installed.
"""

# Registry of available apps
APP_REGISTRY = {
    "mqtt": {
        "name": "MQTT Apps",
        "description": "IoT MQTT integration for Wagtail",
        "repository": "https://github.com/RhamaaCMS/mqtt-apps",
        "branch": "main",
        "category": "IoT"
    },
    "users": {
        "name": "User Management",
        "description": "Advanced user management system",
        "repository": "https://github.com/RhamaaCMS/users-app",
        "branch": "main",
        "category": "Authentication"
    },
    "articles": {
        "name": "Article System",
        "description": "Blog and article management",
        "repository": "https://github.com/RhamaaCMS/articles-app",
        "branch": "main",
        "category": "Content"
    },
    "lms": {
        "name": "Learning Management System",
        "description": "Complete LMS solution for Wagtail",
        "repository": "https://github.com/RhamaaCMS/lms-app",
        "branch": "main",
        "category": "Education"
    }
}

def get_app_info(app_name):
    """Get information about a specific app."""
    return APP_REGISTRY.get(app_name.lower())

def list_available_apps():
    """Get list of all available apps."""
    return APP_REGISTRY

def is_app_available(app_name):
    """Check if an app is available in the registry."""
    return app_name.lower() in APP_REGISTRY