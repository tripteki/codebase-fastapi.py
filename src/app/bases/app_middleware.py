from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class AppMiddleware (BaseHTTPMiddleware):
    """
    AppMiddleware (BaseHTTPMiddleware)
    """
    def __init__ (self, app: ASGIApp) -> None:
        """
        Args:
            app (ASGIApp)
        """
        super ().__init__ (app)

    async def dispatch (self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Args:
            request (Request)
            call_next (Callable[[Request], Awaitable[Response]])
        Returns:
            Response
        """
        response = await call_next (request)
        return response
