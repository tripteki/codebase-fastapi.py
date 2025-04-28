from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_security import security
from src.app.dependencies.app_database_dependency import get_db
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

async def get_current_user (
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends (security),
    db: Session = Depends (get_db)
) -> User:
    """
    Args:
        request (Request)
        credentials (Optional[HTTPAuthorizationCredentials])
        db (Session)
    Returns:
        User
    """
    i18n = AppI18n.i18n ()

    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    else:
        authorization = request.headers.get ("authorization", "")
        parts = authorization.split (" ")
        if len (parts) == 2 and parts[0] == "Bearer":
            token = parts[1]
    
    if not token:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t ("_v1_user.auth.missing_token")
        )

    isBlacklisted = await AppAuth.isTokenBlacklisted (token)
    if isBlacklisted:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t ("_v1_user.auth.invalid_token")
        )
    
    payload = AppAuth.decodeToken (token)
    if not payload:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t ("_v1_user.auth.invalid_token")
        )
    
    userId = payload.get ("sub")
    if not userId:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t ("_v1_user.auth.invalid_token")
        )

    from sqlmodel import select
    statement = select (User).where (User.id == userId, User.deleted_at == None)
    result = db.exec (statement).first ()
    
    if not result:
        raise HTTPException (
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t ("_v1_user.auth.user_not_found")
        )
    
    return result
