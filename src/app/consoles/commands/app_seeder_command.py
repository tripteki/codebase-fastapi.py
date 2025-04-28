import asyncio
import click
import sys
import traceback
from src.app.bases.app_console import Command
from src.app.databases.seeders.app_seeder import Seeder

@Command (name="seeder", help="Command to run database seeders")
@click.option ("--multiple", "-m", default=1, help="Number of datas to seed (default to 1)", type=int)
@click.argument ("seeder_class")
def seederCommand (multiple: int, seeder_class: str) -> None:
    """
    Args:
        multiple (int)
        seeder_class (str)
    Returns:
        None
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
            async def runSeeder () -> None:
                await seeder.run ()
            asyncio.run (runSeeder ())
        click.echo (click.style (f"Successfully seeded {multiple} {className}(s)!", fg="green"))
    except Exception as e:
        traceback.print_exc ()
        click.echo (click.style (f"Error: {str (e)}", fg="red"))
        sys.exit (1)
