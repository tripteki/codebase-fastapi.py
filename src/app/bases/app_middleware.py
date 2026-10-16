from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from src.app.bases.app_i18n import AppI18n

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

class AppLocaleMiddleware:
    """
    AppLocaleMiddleware
    """
    def __init__ (self, app: ASGIApp) -> None:
        """
        Args:
            app (ASGIApp)
        Returns:
            None
        """
        self.app = app

    async def __call__ (self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Args:
            scope (Scope)
            receive (Receive)
            send (Send)
        Returns:
            None
        """
        if scope["type"] != "http":
            await self.app (scope, receive, send)
            return
        acceptLanguage = dict (scope.get ("headers") or []).get (b"accept-language", b"").decode ("latin-1")
        token = AppI18n.useRequestLocale (AppI18n.resolveLocale (acceptLanguage))
        try:
            await self.app (scope, receive, send)
        finally:
            AppI18n.resetRequestLocale (token)
