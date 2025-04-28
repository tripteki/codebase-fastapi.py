from collections import defaultdict
from typing import Dict, List, Callable, Optional
import asyncio

class AppEventEmitter:
    """
    AppEventEmitter
    """
    def __init__ (self) -> None:
        """
        Args:
            self
        Returns:
            None
        """
        self._listeners: Dict[str, List[Callable[..., object]]] = defaultdict (list)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def setLoop (self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Args:
            loop (asyncio.AbstractEventLoop)
        Returns:
            None
        """
        self._loop = loop

    def on (self, event: str, handler: Callable[..., object]) -> None:
        """
        Args:
            event (str)
            handler (Callable[..., object])
        Returns:
            None
        """
        self._listeners[event].append (handler)

    def off (self, event: str, handler: Callable[..., object]) -> None:
        """
        Args:
            event (str)
            handler (Callable[..., object])
        Returns:
            None
        """
        if event in self._listeners and handler in self._listeners[event]:
            self._listeners[event].remove (handler)

    async def emit (self, event: str, *args: object, **kwargs: object) -> None:
        """
        Args:
            event (str)
            *args (object)
            **kwargs (object)
        Returns:
            None
        """
        if event in self._listeners:
            tasks: List[asyncio.Task[object]] = []
            for handler in self._listeners[event]:
                if asyncio.iscoroutinefunction (handler):
                    tasks.append (handler (*args, **kwargs))
                else:
                    handler (*args, **kwargs)
            if tasks:
                await asyncio.gather (*tasks, return_exceptions=True)

    def emitSync (self, event: str, *args: object, **kwargs: object) -> None:
        """
        Args:
            event (str)
            *args (object)
            **kwargs (object)
        Returns:
            None
        """
        if event in self._listeners:
            for handler in self._listeners[event]:
                try:
                    handler (*args, **kwargs)
                except Exception:
                    pass

_event_emitter_instance: Optional[AppEventEmitter] = None

def getEventEmitter () -> AppEventEmitter:
    """
    Args:
        None
    Returns:
        AppEventEmitter
    """
    global _event_emitter_instance
    if _event_emitter_instance is None:
        _event_emitter_instance = AppEventEmitter ()
    return _event_emitter_instance

def OnEvent (event: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Args:
        event (str)
    Returns:
        Callable[[Callable[..., object]], Callable[..., object]]
    """
    def decorator (handler: Callable[..., object]) -> Callable[..., object]:
        """
        Args:
            handler (Callable[..., object])
        Returns:
            Callable[..., object]
        """
        emitter = getEventEmitter ()
        emitter.on (event, handler)
        return handler
    return decorator
