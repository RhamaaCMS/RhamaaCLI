import click
from rhamaa.commands.start import start
from rhamaa.commands.add import add

@click.group()
def main():
    """Rhamaa CLI for Wagtail development."""
    pass

main.add_command(start)
main.add_command(add)
