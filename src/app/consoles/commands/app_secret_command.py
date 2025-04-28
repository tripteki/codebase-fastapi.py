import click
import secrets
from src.app.bases.app_console import Command

@Command (name="secret", help="Command to generating app secret")
def secretCommand () -> None:
    """
    Returns:
        None
    """
    secret = secrets.token_urlsafe (32)
    click.echo (click.style ("Generated app secret : ", fg="yellow") + click.style (secret, fg="green") + click.style (" !", fg="yellow"))
