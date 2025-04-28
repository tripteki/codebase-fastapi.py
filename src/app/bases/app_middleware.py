from typing import Callable, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class AppMiddleware (BaseHTTPMiddleware):
    """
    AppMiddleware
    """
    def __init__ (self, app: ASGIApp):
        """
        Args:
            app (ASGIApp)
        """
        super ().__init__ (app)

    async def dispatch (self, request: Request, call_next: Callable) -> Response:
        """
        Args:
            request (Request)
            call_next (Callable)
        Returns:
            Response
        """
        response = await call_next (request)
        return response
