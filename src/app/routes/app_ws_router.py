import socketio
from typing import Any, Dict, Optional
from urllib.parse import parse_qs
from fastapi import FastAPI
from sqlmodel import Session, select
from src.app.schemas.app_schema import createGraphQLRouter
from src.app.configs.cache_config import CacheConfig
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.user_model import User

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
        cacheConfig = CacheConfig.config ()
        redisUri = cacheConfig.redis_uri ()
        _socketio_server = socketio.AsyncServer (
            async_mode="asgi",
            cors_allowed_origins="*",
            message_queue=redisUri,
        )

        @_socketio_server.event
        async def connect (sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, object]]) -> bool:
            """
            Args:
                sid (str)
                environ (Dict[str, Any])
                auth (Optional[Dict[str, object]])
            Returns:
                bool
            """
            token: Optional[str] = None

            if auth and isinstance (auth, dict):
                rawToken = auth.get ("token")
                if isinstance (rawToken, str) and rawToken:
                    token = rawToken

            if token is None:
                queryString = environ.get ("QUERY_STRING", "")
                if queryString:
                    parsed = parse_qs (queryString)
                    values = parsed.get ("token") or parsed.get ("access_token")
                    if values:
                        token = str (values[0])

            if token is None:
                return False

            isBlacklisted = await AppAuth.isTokenBlacklisted (token)
            if isBlacklisted:
                return False

            payload = AppAuth.verifyToken (token, "access")
            if not payload:
                return False

            userId = payload.get ("sub")
            if not isinstance (userId, str) or not userId:
                return False

            engine = AppDatabase.databasePostgresql ()
            session = Session (engine)
            try:
                statement = select (User).where (User.id == userId, User.deleted_at == None)
                user = session.exec (statement).first ()

                if not user or user.email_verified_at is None:
                    return False
            finally:
                session.close ()

            await _socketio_server.save_session (sid, {"userId": userId})
            return True

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
        socketioApp = socketio.ASGIApp (socketioServer, socketio_path="")

        app.mount ("/socket.io", socketioApp)
