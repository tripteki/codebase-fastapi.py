import click
import re
import subprocess
import sys
import traceback
from src.app.bases.app_console import Command

def checkPendingMigrations () -> bool:
    """
    Returns:
        bool
    """
    try:
        currentResult = subprocess.run ([sys.executable, "-m", "alembic", "current"], capture_output=True, text=True, check=True)
        headsResult = subprocess.run ([sys.executable, "-m", "alembic", "heads"], capture_output=True, text=True, check=True)
        currentLine = currentResult.stdout.strip ()
        headsLine = headsResult.stdout.strip ()
        currentRev = None
        headRev = None
        if currentLine and not currentLine.startswith ("INFO"):
            currentMatch = re.search (r"(\w+)", currentLine)
            if currentMatch:
                currentRev = currentMatch.group (1)
        if headsLine and not headsLine.startswith ("INFO"):
            headMatch = re.search (r"(\w+)", headsLine)
            if headMatch:
                headRev = headMatch.group (1)
        if currentRev and headRev:
            return currentRev != headRev
        return True
    except Exception:
        return True

@Command (name="migrate:up", help="Run pending migrations")
@click.option ("--revision", "-r", help="Revision to upgrade to (default: head)", default="head", type=str)
def migrateUpCommand (revision: str) -> None:
    """
    Args:
        revision (str)
    Returns:
        None
    """
    try:
        if revision == "head" and not checkPendingMigrations ():
            click.echo (click.style ("No migration can be run.", fg="yellow"))
            return
        subprocess.run ([sys.executable, "-m", "alembic", "upgrade", revision], check=True)
        click.echo (click.style (f"Migration upgraded to {revision}!", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo (click.style (f"Migration failed: {e}", fg="red"))
        sys.exit (1)
    except Exception as e:
        click.echo (click.style (f"Error: {e}", fg="red"))

@Command (name="migrate:down", help="Rollback migrations")
@click.option ("--revision", "-r", help="Revision to downgrade to (default: -1 for one step)", default="-1", type=str)
def migrateDownCommand (revision: str) -> None:
    """
    Args:
        revision (str)
    Returns:
        None
    """
    try:
        subprocess.run ([sys.executable, "-m", "alembic", "downgrade", revision], check=True)
        if revision == "-1":
            click.echo (click.style ("Migration downgraded one step!", fg="green"))
        else:
            click.echo (click.style (f"Migration downgraded to {revision}!", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo (click.style (f"Migration failed: {e}", fg="red"))
        sys.exit (1)
    except Exception as e:
        click.echo (click.style (f"Error: {e}", fg="red"))

@Command (name="migrate:status", help="Show migration status")
def migrateStatusCommand () -> None:
    """
    Returns:
        None
    """
    try:
        click.echo (click.style ("Migration history:", fg="cyan"))
        subprocess.run ([sys.executable, "-m", "alembic", "history"], check=True)
        click.echo ()
        click.echo (click.style ("Current revision:", fg="cyan"))
        subprocess.run ([sys.executable, "-m", "alembic", "current"], check=True)
    except subprocess.CalledProcessError as e:
        click.echo (click.style (f"Failed to list migrations: {e}", fg="red"))
        sys.exit (1)
    except Exception as e:
        click.echo (click.style (f"Error: {e}", fg="red"))
