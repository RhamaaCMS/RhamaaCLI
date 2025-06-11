import click
import subprocess

@click.command()
@click.argument('project_name')
def start(project_name):
    """Create a new Wagtail project using the RhamaaCMS template."""
    template_url = "https://github.com/rhamaa/RhamaaCMS/archive/refs/heads/main.zip"
    cmd = [
        "wagtail", "start",
        f"--template={template_url}",
        project_name
    ]
    subprocess.run(cmd)
