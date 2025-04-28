import asyncio
import click
import sys
import traceback
from src.app.bases.app_console import Command
from src.app.databases.seeders.app_seeder import Seeder
from src.v1.api.user.databases.seeders.user_seeder import UserSeeder

@Command (name="v1:user:seed", help="Command to seed user data")
@click.option ("--multiple", "-m", default=1, help="Number of datas to seed (default to 1)", type=int)
def userSeedCommand (multiple: int) -> None:
    """
    Args:
        multiple (int)
    Returns:
        None
    """
    try:
        async def runSeeder () -> None:
            click.echo (click.style (f"Seeding {multiple} user(s)!", fg="yellow"))
            await UserSeeder.run (count=multiple)
        asyncio.run (runSeeder ())
        click.echo (click.style (f"Successfully seeded {multiple} user(s)!", fg="green"))
    except Exception as e:
        traceback.print_exc ()
        click.echo (click.style (f"Error: {str (e)}", fg="red"))
        sys.exit (1)
