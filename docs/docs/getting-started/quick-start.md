# Quick Start

Get up and running with Rhamaa CLI in minutes! This guide will walk you through creating your first Wagtail project and adding prebuilt applications.

## Step 1: Create Your First Project

Create a new Wagtail project using the RhamaaCMS template:

```bash
rhamaa start MyBlog
```

This command will:

- Download the RhamaaCMS template
- Create a new directory called `MyBlog`
- Set up the basic Wagtail project structure
- Configure initial settings and dependencies

!!! success "Project Created!"
    You should see a success message with the Rhamaa CLI logo and confirmation that your project was created.

## Step 2: Navigate to Your Project

```bash
cd MyBlog
```

## Step 3: Set Up Your Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Explore Available Apps

See what prebuilt applications are available:

```bash
rhamaa startapp --list
```

You'll see a table showing available apps like:

- **mqtt** - IoT MQTT integration
- **users** - Advanced user management
- **articles** - Blog and article system
- **lms** - Learning Management System

## Step 5: Add Your First App

Let's add the articles app for blog functionality:

```bash
rhamaa startapp articles --prebuild articles
```

This will:

- Download the articles app from GitHub
- Extract it to your `apps/` directory (apps/articles)
- Show you next steps for configuration

## Step 6: Configure the App

Follow the instructions shown after installation:

1. **Add to INSTALLED_APPS** in your settings:

```python
# settings/base.py or settings.py
INSTALLED_APPS = [
    # ... existing apps
    'apps.articles',  # Add this line (matches apps/<name>)
]
```

2. **Run migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create a superuser**:

```bash
python manage.py createsuperuser
```

## Step 7: Start Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the Wagtail admin interface.

## What's Next?

### Add More Apps

Explore other available apps:

```bash
# Add user management
rhamaa startapp users --prebuild users

# Add IoT capabilities
rhamaa startapp iot --prebuild mqtt

# Add LMS functionality
rhamaa startapp lms --prebuild lms
```

### Get App Information

Learn more about any app before installing:

```bash
rhamaa startapp --list
# Then open the app repo linked in the table for details
```

### Registry Commands

The standalone `registry` command group is deprecated. Use:

```bash
rhamaa startapp --list
```

## Common Workflows

### Starting a Blog Project

```bash
rhamaa start MyBlog
cd MyBlog
rhamaa startapp articles --prebuild articles
# Configure and run migrations
```

### Starting an IoT Project

```bash
rhamaa start IoTDashboard
cd IoTDashboard
rhamaa startapp iot --prebuild mqtt
rhamaa startapp users --prebuild users
# Configure MQTT settings and run migrations
```

### Starting an Educational Platform

```bash
rhamaa start EduPlatform
cd EduPlatform
rhamaa startapp lms --prebuild lms
rhamaa startapp users --prebuild users
# Configure LMS settings and run migrations
```

## Tips for Success

!!! tip "Project Structure"
    Rhamaa CLI creates apps in the `apps/` directory. This keeps your project organized and follows Django best practices.

!!! tip "Force Installation"
    If you need to reinstall a prebuilt app into the same folder, use the `--force` flag:
    ```bash
    rhamaa startapp articles --prebuild articles --force
    ```

!!! tip "Check Project Type"
    Rhamaa CLI automatically detects if you're in a Wagtail project before allowing app installation.

## Troubleshooting

### App Already Exists

If you see "App already exists" during prebuilt installation, use the `--force` flag to overwrite:

```bash
rhamaa startapp articles --prebuild articles --force
```

### Not a Wagtail Project

Make sure you're in the root directory of your Wagtail project (where `manage.py` is located).

### Download Issues

If downloads fail, check your internet connection and try again. The CLI will show detailed error messages.

## Next Steps

- Learn more about [Project Management](../commands/project-management.md)
- Explore [App Management](../commands/app-management.md) features
- Check out [Available Apps](../apps/index.md) in detail
- Read about [Contributing](../development/contributing.md) to the ecosystem