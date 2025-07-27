import click
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.argument('app_name')
@click.option('--path', '-p', default='apps', help='Directory to create the app in (default: apps)')
def startapp(app_name, path):
    """Create a new Django app with RhamaaCMS structure."""

    # Validate app name
    if not app_name.isidentifier():
        console.print(Panel(
            f"[red]Error:[/red] '[bold]{app_name}[/bold]' is not a valid Python identifier.\n"
            "App names should only contain letters, numbers, and underscores, and cannot start with a number.",
            title="[red]Invalid App Name[/red]",
            expand=False
        ))
        return

    # Create app directory
    app_dir = Path(path) / app_name

    if app_dir.exists():
        console.print(Panel(
            f"[yellow]Warning:[/yellow] Directory '[bold]{app_dir}[/bold]' already exists.\n"
            "Please choose a different app name or remove the existing directory.",
            title="[yellow]Directory Exists[/yellow]",
            expand=False
        ))
        return

    console.print(Panel(
        f"[cyan]Creating new app:[/cyan] [bold]{app_name}[/bold]\n"
        f"[dim]Location:[/dim] [blue]{app_dir}[/blue]",
        title="[cyan]RhamaaCMS App Generator[/cyan]",
        expand=False
    ))

    # Create app directory structure
    create_app_structure(app_dir, app_name)

    console.print(Panel(
        f"[green]✓[/green] Successfully created '[bold]{app_name}[/bold]' app!\n\n"
        f"[dim]App location:[/dim] [cyan]{app_dir}[/cyan]\n"
        f"[dim]Next steps:[/dim]\n"
        f"1. The app will be auto-discovered by RhamaaCMS\n"
        f"2. Run migrations: [cyan]python manage.py makemigrations {app_name}[/cyan]\n"
        f"3. Run: [cyan]python manage.py migrate[/cyan]\n"
        f"4. Start developing your models, views, and templates!",
        title="[green]App Created Successfully[/green]",
        expand=False
    ))


def create_app_structure(app_dir, app_name):
    """Create the complete app directory structure with RhamaaCMS templates."""

    # Create main directory
    app_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    subdirs = ['migrations', 'templates', 'static',
               'management', 'management/commands']
    for subdir in subdirs:
        (app_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create templates subdirectory for the app
    (app_dir / 'templates' / app_name).mkdir(parents=True, exist_ok=True)

    # Create __init__.py files
    init_files = [
        '',
        'migrations',
        'management',
        'management/commands'
    ]

    for init_path in init_files:
        init_file = app_dir / init_path / \
            '__init__.py' if init_path else app_dir / '__init__.py'
        init_file.touch()

    # Create app files with templates
    create_apps_py(app_dir, app_name)
    create_models_py(app_dir, app_name)
    create_views_py(app_dir, app_name)
    create_admin_py(app_dir, app_name)
    create_urls_py(app_dir, app_name)
    create_settings_py(app_dir, app_name)
    create_tests_py(app_dir, app_name)
    create_initial_migration(app_dir)
    create_template_files(app_dir, app_name)


def create_apps_py(app_dir, app_name):
    """Create apps.py with RhamaaCMS configuration."""
    content = f'''from django.apps import AppConfig


class {app_name.title().replace('_', '')}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{app_name.replace("_", " ").title()}'
'''

    (app_dir / 'apps.py').write_text(content)


def create_models_py(app_dir, app_name):
    """Create models.py with RhamaaCMS base imports."""
    content = '''from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from utils.models import BasePage
from utils.blocks import StoryBlock


# Create your models here.

class ExamplePage(BasePage):
    """Example page model for demonstration."""
    
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True
    )
    
    body = StreamField(
        StoryBlock(),
        verbose_name="Page body",
        blank=True,
        use_json_field=True
    )
    
    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
    
    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    class Meta:
        verbose_name = "Example Page"
        verbose_name_plural = "Example Pages"
'''

    (app_dir / 'models.py').write_text(content)


def create_views_py(app_dir, app_name):
    """Create views.py with basic structure."""
    app_title = app_name.replace("_", " ").title()
    content = f'''from django.shortcuts import render
from django.http import HttpResponse
from wagtail.models import Page


# Create your views here.

def index(request):
    """Example view function."""
    return HttpResponse("Hello from {app_name} app!")


def example_view(request):
    """Example view with template rendering."""
    context = {{
        'app_name': '{app_name}',
        'title': '{app_title}'
    }}
    return render(request, '{app_name}/index.html', context)
'''

    (app_dir / 'views.py').write_text(content)


def create_admin_py(app_dir, app_name):
    """Create admin.py with Wagtail integration."""
    content = '''from django.contrib import admin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import ExamplePage


# Register your models here.

@admin.register(ExamplePage)
class ExamplePageAdmin(admin.ModelAdmin):
    list_display = ['title', 'live', 'first_published_at']
    list_filter = ['live', 'first_published_at']
    search_fields = ['title', 'introduction']


# Wagtail ModelAdmin (optional - for non-page models)
# class ExampleModelAdmin(ModelAdmin):
#     model = ExamplePage
#     menu_label = 'Example Pages'
#     menu_icon = 'doc-full'
#     list_display = ('title', 'live', 'first_published_at')
#     search_fields = ('title', 'introduction')

# modeladmin_register(ExampleModelAdmin)
'''

    (app_dir / 'admin.py').write_text(content)


def create_urls_py(app_dir, app_name):
    """Create urls.py for the app."""
    content = f'''from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
    path('example/', views.example_view, name='example'),
]
'''

    (app_dir / 'urls.py').write_text(content)


def create_settings_py(app_dir, app_name):
    """Create settings.py for app-specific configurations."""
    content = f'''"""
Settings for {app_name} app
This file contains app-specific settings that will be automatically
imported by RhamaaCMS auto-discovery system.
"""

# App-specific settings
{app_name.upper()}_SETTINGS = {{
    'ENABLED': True,
    'VERSION': '1.0.0',
    'DESCRIPTION': '{app_name.replace("_", " ").title()} application for RhamaaCMS',
}}

# Example: Custom app configurations
# {app_name.upper()}_CONFIG = {{
#     'MAX_ITEMS': 100,
#     'CACHE_TIMEOUT': 300,
#     'ENABLE_NOTIFICATIONS': True,
# }}

# Example: Add to Django settings if needed
# INSTALLED_APPS_EXTRA = [
#     'some_third_party_app',
# ]

# Example: Middleware additions
# MIDDLEWARE_EXTRA = [
#     'path.to.custom.middleware',
# ]
'''

    (app_dir / 'settings.py').write_text(content)


def create_tests_py(app_dir, app_name):
    """Create tests.py with basic test structure."""
    content = f'''from django.test import TestCase, Client
from django.urls import reverse
from wagtail.test.utils import WagtailPageTests
from wagtail.models import Page

from .models import ExamplePage


class {app_name.title().replace('_', '')}ViewTests(TestCase):
    """Test views for {app_name} app."""
    
    def setUp(self):
        self.client = Client()
    
    def test_index_view(self):
        """Test the index view."""
        response = self.client.get(reverse('{app_name}:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello from {app_name}')
    
    def test_example_view(self):
        """Test the example view."""
        response = self.client.get(reverse('{app_name}:example'))
        self.assertEqual(response.status_code, 200)


class ExamplePageTests(WagtailPageTests):
    """Test ExamplePage model."""
    
    def test_can_create_example_page(self):
        """Test that we can create an ExamplePage."""
        # Get the root page
        root_page = Page.objects.get(id=2)
        
        # Create an ExamplePage
        example_page = ExamplePage(
            title="Test Example Page",
            introduction="This is a test page",
            slug="test-example-page"
        )
        
        # Add it as a child of the root page
        root_page.add_child(instance=example_page)
        
        # Check that the page was created
        self.assertTrue(ExamplePage.objects.filter(title="Test Example Page").exists())
    
    def test_example_page_str(self):
        """Test the string representation of ExamplePage."""
        page = ExamplePage(title="Test Page")
        self.assertEqual(str(page), "Test Page")
'''

    (app_dir / 'tests.py').write_text(content)


def create_initial_migration(app_dir):
    """Create initial migration file."""
    content = '''# Generated by RhamaaCMS CLI

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0089_log_entry_data_json_null_to_object'),
        ('utils', '0001_initial'),
    ]

    operations = [
        # Initial migration - models will be added when you run makemigrations
    ]
'''

    (app_dir / 'migrations' / '0001_initial.py').write_text(content)


def create_template_files(app_dir, app_name):
    """Create template files for the app."""

    # Create index.html template
    index_template = f'''{{% extends "base.html" %}}
{{% load static %}}

{{% block title %}}{app_name.replace("_", " ").title()}{{% endblock %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-bold text-gray-900 mb-6">
            {{{{ title }}}}
        </h1>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">
                Welcome to {{{{ app_name }}}} App
            </h2>
            
            <p class="text-gray-600 mb-4">
                This is a starter template for your new RhamaaCMS app. 
                You can customize this template and add your own content.
            </p>
            
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
                <div class="flex">
                    <div class="ml-3">
                        <p class="text-sm text-blue-700">
                            <strong>Next Steps:</strong>
                        </p>
                        <ul class="text-sm text-blue-600 mt-2 list-disc list-inside">
                            <li>Customize your models in <code>models.py</code></li>
                            <li>Add your views in <code>views.py</code></li>
                            <li>Update this template in <code>templates/{app_name}/index.html</code></li>
                            <li>Add your static files in <code>static/</code> directory</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-gray-800 mb-2">Models</h3>
                    <p class="text-sm text-gray-600">
                        Define your data models in <code>models.py</code>
                    </p>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-gray-800 mb-2">Views</h3>
                    <p class="text-sm text-gray-600">
                        Create your view functions in <code>views.py</code>
                    </p>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-gray-800 mb-2">Templates</h3>
                    <p class="text-sm text-gray-600">
                        Design your HTML templates in <code>templates/</code>
                    </p>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-gray-800 mb-2">Static Files</h3>
                    <p class="text-sm text-gray-600">
                        Add CSS, JS, and images in <code>static/</code>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
'''

    (app_dir / 'templates' / app_name / 'index.html').write_text(index_template)

    # Create example page template
    page_template = f'''{{% extends "base_page.html" %}}
{{% load static wagtailcore_tags %}}

{{% block title %}}{{% if page.seo_title %}}{{% endif %}}{{% endblock %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-bold text-gray-900 mb-6">
            {{{{ page.title }}}}
        </h1>
        
        {{% if page.introduction %}}
        <div class="text-xl text-gray-600 mb-8">
            {{{{ page.introduction|linebreaks }}}}
        </div>
        {{% endif %}}
        
        {{% if page.body %}}
        <div class="prose prose-lg max-w-none">
            {{% for block in page.body %}}
                {{% include_block block %}}
            {{% endfor %}}
        </div>
        {{% endif %}}
    </div>
</div>
{{% endblock %}}
'''

    (app_dir / 'templates' / app_name / 'example_page.html').write_text(page_template)
