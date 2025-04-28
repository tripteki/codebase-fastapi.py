from typing import Callable, Optional, Dict
import click
from click import Command, Context

class AppConsole:
    """
    AppConsole

    Attributes:
        _group (Optional[click.Group])
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
    def command (cls, name: Optional[str] = None, help: Optional[str] = None, **attrs: Dict[str, object]) -> Callable[[Callable[..., object]], Command]:
        """
        Args:
            name (Optional[str])
            help (Optional[str])
            **attrs (Dict[str, object])
        Returns:
            Callable[[Callable[..., object]], Command]
        """
        return cls.group ().command (name=name, help=help, **attrs)

    @classmethod
    def run (cls, args: Optional[list[str]] = None) -> Optional[int]:
        """
        Args:
            args (Optional[list[str]])
        Returns:
            Optional[int]
        """
        return cls.group () (args=args)

def Command (name: Optional[str] = None, help: Optional[str] = None, **attrs: Dict[str, object]) -> Callable[[Callable[..., object]], Command]:
    """
    Args:
        name (Optional[str])
        help (Optional[str])
        **attrs (Dict[str, object])
    Returns:
        Callable[[Callable[..., object]], Command]
    """
    return AppConsole.command (name=name, help=help, **attrs)
