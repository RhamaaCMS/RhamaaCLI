import click

@click.command()
@click.argument('app_name')
def add(app_name):
    """Add a prebuilt app to the project (users, article, LMS, IoT, etc)."""
    click.echo(f"Pretend to add app: {app_name}. (Implement logic here)")
