from typing import Any, Callable, Optional
import click
from click import Command, Context

class AppConsole:
    """
    AppConsole
    """
    _group: Optional[click.Group] = None

    @classmethod
    def group (cls) -> click.Group:
        """
        Args:
            cls
        Returns:
            click.Group
        """
        if cls._group is None:
            cls._group = click.Group ("app", help="Application CLI commands")
        return cls._group

    @classmethod
    def command (cls, name: Optional[str] = None, help: Optional[str] = None, **attrs) -> Callable:
        """
        Args:
            name (Optional[str])
            help (Optional[str])
            **attrs
        Returns:
            Callable
        """
        return cls.group ().command (name=name, help=help, **attrs)

    @classmethod
    def run (cls, args: Optional[list] = None) -> Any:
        """
        Args:
            args (Optional[list])
        Returns:
            Any
        """
        return cls.group () (args=args)

def Command (name: Optional[str] = None, help: Optional[str] = None, **attrs):
    """
    Args:
        name (Optional[str])
        help (Optional[str])
        **attrs
    Returns:
        Callable
    """
    return AppConsole.command (name=name, help=help, **attrs)
