from fastapi import FastAPI
import socketio
from src.app.schemas.app_schema import createGraphQLRouter

_socketio_server: socketio.AsyncServer = None

def getSocketIOServer () -> socketio.AsyncServer:
    """
    Args:
        None
    Returns:
        socketio.AsyncServer
    """
    global _socketio_server
    if _socketio_server is None:
        _socketio_server = socketio.AsyncServer (async_mode="asgi", cors_allowed_origins="*")
    return _socketio_server

class AppWsRouter:
    """
    AppWsRouter
    """
    @staticmethod
    def route (app: FastAPI) -> None:
        """
        Args:
            app (FastAPI)
        Returns:
            None
        """
        graphqlRouter = createGraphQLRouter ()
        app.include_router (graphqlRouter)
        socketioServer = getSocketIOServer ()
        app.state.ws = socketioServer
