"""
Registry module for RhamaaCLI
Contains app and template registries.
"""

# Import all registry functions for easy access
from .app import (
    APP_REGISTRY,
    get_app_info,
    list_available_apps,
    is_app_available
)

from .template import (
    TEMPLATE_REGISTRY,
    get_template_info,
    list_available_templates,
    is_template_available,
    get_template_url
)

__all__ = [
    # App registry
    'APP_REGISTRY',
    'get_app_info',
    'list_available_apps',
    'is_app_available',
    
    # Template registry
    'TEMPLATE_REGISTRY',
    'get_template_info',
    'list_available_templates',
    'is_template_available',
    'get_template_url'
]