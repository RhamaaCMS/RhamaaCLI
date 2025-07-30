"""
Template Registry for RhamaaCLI
Contains the list of available project templates that can be used with 'rhamaa start'.
"""

# Registry of available templates
TEMPLATE_REGISTRY = {
    "default": {
        "name": "RhamaaCMS Default",
        "description": "Default RhamaaCMS template with design system",
        "repository": "https://github.com/RhamaaCMS/RhamaaCMS/archive/refs/heads/main.zip",
        "category": "Standard",
        "features": [
            "RHAMAA Global Design System",
            "Tailwind CSS + SCSS",
            "Preline UI Components",
            "Dark Mode Support",
            "Responsive Design",
            "Modern Build System"
        ]
    },
    "minimal": {
        "name": "Minimal Template",
        "description": "Minimal Wagtail setup without extra styling",
        "repository": "https://github.com/wagtail/wagtail/archive/refs/heads/main.zip",  # Using official Wagtail as minimal template
        "category": "Standard",
        "features": [
            "Basic Wagtail setup",
            "Minimal styling",
            "Essential pages only"
        ]
    },
    "blog": {
        "name": "Blog Template",
        "description": "Blog-focused template with article system",
        "repository": "https://github.com/RhamaaCMS/blog-template/archive/refs/heads/main.zip",
        "category": "Content",
        "features": [
            "Built-in blog system",
            "Article management",
            "SEO optimized",
            "Social sharing",
            "Comment system ready"
        ]
    },
    "ecommerce": {
        "name": "E-commerce Template",
        "description": "E-commerce ready template with shop features",
        "repository": "https://github.com/RhamaaCMS/ecommerce-template/archive/refs/heads/main.zip",
        "category": "E-commerce",
        "features": [
            "Product catalog",
            "Shopping cart",
            "Payment integration ready",
            "Inventory management",
            "Order tracking"
        ]
    },
    "portfolio": {
        "name": "Portfolio Template",
        "description": "Creative portfolio template for designers and developers",
        "repository": "https://github.com/RhamaaCMS/portfolio-template/archive/refs/heads/main.zip",
        "category": "Creative",
        "features": [
            "Project showcase",
            "Image galleries",
            "Contact forms",
            "Resume/CV section",
            "Client testimonials"
        ]
    },
    "corporate": {
        "name": "Corporate Template",
        "description": "Professional corporate website template",
        "repository": "https://github.com/RhamaaCMS/corporate-template/archive/refs/heads/main.zip",
        "category": "Business",
        "features": [
            "Professional design",
            "Team pages",
            "Service listings",
            "Case studies",
            "Contact management"
        ]
    },
    "iot": {
        "name": "IoT Dashboard Template",
        "description": "IoT dashboard template with MQTT integration",
        "repository": "https://github.com/RhamaaCMS/iot-template/archive/refs/heads/main.zip",
        "category": "IoT",
        "features": [
            "MQTT integration",
            "Real-time dashboards",
            "Device management",
            "Data visualization",
            "Alert system"
        ]
    },
    "education": {
        "name": "Education Template",
        "description": "Educational institution template with LMS features",
        "repository": "https://github.com/RhamaaCMS/education-template/archive/refs/heads/main.zip",
        "category": "Education",
        "features": [
            "Course management",
            "Student portal",
            "Assignment system",
            "Grade tracking",
            "Event calendar"
        ]
    }
}

def get_template_info(template_name):
    """Get information about a specific template."""
    return TEMPLATE_REGISTRY.get(template_name.lower())

def list_available_templates():
    """Get list of all available templates."""
    return TEMPLATE_REGISTRY

def is_template_available(template_name):
    """Check if a template is available in the registry."""
    return template_name.lower() in TEMPLATE_REGISTRY

def get_template_url(template_name):
    """Get the repository URL for a template."""
    template_info = get_template_info(template_name)
    return template_info['repository'] if template_info else None