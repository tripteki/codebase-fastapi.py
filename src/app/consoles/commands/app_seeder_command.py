import asyncio
import click
from src.app.bases.app_console import Command
from src.app.databases.seeders.app_seeder import Seeder

@Command (name="seeder", help="Command to run database seeders")
@click.option ("--multiple", "-m", default=1, help="Number of datas to seed (default to 1)", type=int)
@click.argument ("seeder_class")
def seederCommand (multiple: int, seeder_class: str):
    """
    Run database seeder
    Args:
        multiple (int)
        seeder_class (str)
    """
    try:
        modulePath, className = seeder_class.rsplit (".", 1)
        module = __import__ (modulePath, fromlist=[className])
        seederClass = getattr (module, className)
        if not issubclass (seederClass, Seeder):
            click.echo (click.style (f"Error: {seeder_class} is not a Seeder class", fg="red"))
            return
        seeder = seederClass ()
        for i in range (multiple):
            click.echo (click.style (f"Seeding #{i + 1} of {className}!", fg="yellow"))
