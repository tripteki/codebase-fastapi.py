from typing import Optional
from strawberry.types import Info
from sqlmodel import Session, select
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.services.user_auth_service import UserAuthService

async def get_current_user_graphql (info: Info) -> Optional[User]:
    """
    Args:
        info (Info)
    Returns:
        Optional[User]
    """
    request = info.context.get ("request")
    if not request:
        return None

    token = UserAuthService.httpBearerToken (request)
    if not token:
        return None

    isBlacklisted = await AppAuth.isTokenBlacklisted (token)
    if isBlacklisted:
        return None

    payload = AppAuth.decodeToken (token)
    if not payload:
        return None

    userId = payload.get ("sub")
    if not userId:
        return None

    engine = AppDatabase.databasePostgresql ()
    session = Session (engine)
    try:
        statement = select (User).where (User.id == userId, User.deleted_at == None)
        result = session.exec (statement).first ()
        return result
    finally:
        session.close ()
