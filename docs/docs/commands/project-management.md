# Project Management

Rhamaa CLI provides powerful commands for creating and managing Wagtail projects. This section covers all project-related commands and their usage.

## Creating New Projects

### `rhamaa start`

Create a new Wagtail project using the RhamaaCMS template.

```bash
rhamaa start <ProjectName>
```

**Example:**
```bash
rhamaa start MyBlog
```

#### What it does:

1. **Downloads Template**: Fetches the latest RhamaaCMS template from GitHub
2. **Creates Project**: Uses Wagtail's `start` command with the template
3. **Sets Up Structure**: Configures the project with RhamaaCMS best practices
4. **Provides Feedback**: Shows progress and success confirmation

#### Template Features:

The RhamaaCMS template includes:

- **Modern Django/Wagtail Setup**: Latest versions and best practices
- **Organized Structure**: Logical app organization and settings management
- **Development Tools**: Pre-configured development dependencies
- **Production Ready**: Settings for deployment and scaling
- **Documentation**: README and setup instructions

### Project Structure

When you create a project with `rhamaa start`, you get:

```
MyProject/
├── MyProject/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                    # Directory for custom apps
├── static/                  # Static files
├── media/                   # Media files
├── templates/               # Template files
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # Project documentation
```

## Creating Django Apps

### `rhamaa startapp`

Create a new Django app with RhamaaCMS structure within your project.

```bash
rhamaa startapp <AppName>
```

**Example:**
```bash
rhamaa startapp blog
```

#### Features:

- **Structured Layout**: Creates apps in the `apps/` directory
- **RhamaaCMS Standards**: Follows RhamaaCMS app conventions
- **Ready to Use**: Includes basic model, view, and admin setup
- **Template Types**: `--type wagtail` (default) or `--type minimal`
- **Prebuilt Apps**: Install with `--prebuild <key>` and view availability with `--list`

## Project Validation

Rhamaa CLI automatically validates your project environment:

### Wagtail Project Detection

Before allowing certain operations, Rhamaa CLI checks if you're in a valid Wagtail project by looking for:

- `manage.py` file
- Django settings files
- Common project indicators

### Error Handling

If you're not in a Wagtail project, you'll see:

```
Error: This doesn't appear to be a Wagtail project.
Please run this command from the root of your Wagtail project.
```

## Best Practices

### Project Naming

- Use **PascalCase** for project names: `MyBlog`, `CompanyWebsite`
- Avoid spaces and special characters
- Keep names descriptive but concise

### Directory Structure

- Keep custom apps in the `apps/` directory
- Use the `static/` directory for static files
- Store templates in the `templates/` directory
- Keep media files in `media/` (for development)

### Settings Management

The RhamaaCMS template uses environment-based settings:

- `base.py` - Common settings
- `dev.py` - Development settings
- `production.py` - Production settings

## Advanced Usage

### Custom Templates

While Rhamaa CLI uses the RhamaaCMS template by default, you can still use Wagtail's native template system:

```bash
wagtail start --template=https://github.com/your-org/your-template.git MyProject
```

### Environment Variables

Set up environment variables for your project:

```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

## Troubleshooting

### Template Download Issues

If template download fails:

1. **Check Internet Connection**: Ensure you have a stable connection
2. **GitHub Access**: Verify you can access GitHub
3. **Wagtail Installation**: Make sure Wagtail is installed

### Permission Errors

On some systems, you might need elevated permissions:

```bash
sudo rhamaa start MyProject
```

Or use a virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
pip install rhamaa wagtail
rhamaa start MyProject
```

### Project Already Exists

If a directory with the same name exists:

```
Error: Directory 'MyProject' already exists
```

Choose a different name or remove the existing directory.

## Integration with Other Tools

### Version Control

Initialize Git repository after project creation:

```bash
rhamaa start MyProject
cd MyProject
git init
git add .
git commit -m "Initial commit"
```

### IDE Setup

The RhamaaCMS template works well with:

- **VS Code**: Includes recommended extensions
- **PyCharm**: Django project detection
- **Sublime Text**: Python syntax highlighting

### Deployment

The template is ready for deployment to:

- **Heroku**: Includes Procfile and requirements
- **Docker**: Dockerfile included
- **Traditional Hosting**: WSGI configuration ready

## Next Steps

After creating your project:

1. **Set Up Environment**: Create virtual environment and install dependencies
2. **Add Applications**: Use `rhamaa startapp <AppName> --prebuild <key>` to install prebuilt apps (see `rhamaa startapp --list`)
3. **Configure Settings**: Customize settings for your needs
4. **Run Migrations**: Set up the database
5. **Create Superuser**: Access the admin interface

See the [App Management](app-management.md) section for adding prebuilt applications to your project.