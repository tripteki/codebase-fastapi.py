import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request, status
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_cache import AppCache
from src.app.bases.app_context import AppContext
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.configs.auth_config import AuthConfig
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_transformer_dto import UserAuthTransformerDto, UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import UserAuthDto, UserCreateValidatorDto
from src.v1.api.user.events.user.auth.loggedin.event import UserAuthLoggedInEvent
from src.v1.api.user.events.user.auth.loggedout.event import UserAuthLoggedOutEvent
from src.v1.api.user.events.user.auth.refreshed.event import UserAuthRefreshedEvent
from src.v1.api.user.events.user.auth.registered.event import UserAuthRegisteredEvent
from src.v1.api.user.events.user.auth.reset.event import UserAuthResetEvent
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

class UserAuthService:
    """
    UserAuthService
    """
    @staticmethod
    def httpBearerToken (request: Request) -> Optional[str]:
        """
        Args:
            request (Request)
        Returns:
            Optional[str]
        """
        authorization = request.headers.get ("authorization", "")
        parts = authorization.split (" ")
        if len (parts) == 2 and parts[0] == "Bearer":
            return parts[1]
        return None

    @staticmethod
    async def validateToken (token: str) -> Optional[str]:
        """
        Args:
            token (str)
        Returns:
            Optional[str]
        """
        if not token:
            return None
        isBlacklisted = await AppAuth.isTokenBlacklisted (token)
        if isBlacklisted:
            return None
        payload = AppAuth.decodeToken (token)
        if not payload:
            return None
        userId = payload.get ("sub")
        return userId

    @staticmethod
    async def login (dto: UserAuthDto) -> UserAuthTransformerDto:
        """
        Args:
            dto (UserAuthDto)
        Returns:
            UserAuthTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneByEmail (dto.identifierValue)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t ("_v1_user.auth.invalid_credentials"),
            )
        if not AppAuth.verifyPassword (dto.password, user.password):
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t ("_v1_user.auth.invalid_credentials"),
            )
        authConfig = AuthConfig.config ()
        accessToken = AppAuth.createAccessToken ({"sub": user.id, "email": user.email})
        refreshToken = AppAuth.createRefreshToken ({"sub": user.id, "email": user.email})
        accessTokenTtl = authConfig.jwt_access_token_expire_minutes * 60
        refreshTokenTtl = authConfig.jwt_refresh_token_expire_days * 24 * 60 * 60
        eventEmitter = getEventEmitter ()
        event = UserAuthLoggedInEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
        await eventEmitter.emit ("user.auth.loggedin", event)
        return UserAuthTransformerDto (
            accessTokenTtl=accessTokenTtl,
            refreshTokenTtl=refreshTokenTtl,
            accessToken=accessToken,
            refreshToken=refreshToken,
        )

    @staticmethod
    async def register (dto: UserCreateValidatorDto) -> UserTransformerDto:
        """
        Args:
            dto (UserCreateValidatorDto)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        existingUser = await UserAuthRepository.findOneByEmail (dto.email)
        if existingUser:
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_user.auth.email_already_exists"),
            )
        hashedPassword = AppAuth.hashPassword (dto.password)
        user = User (
            name=dto.name,
            email=dto.email,
            password=hashedPassword,
        )
        user = await UserAuthRepository.create (user)

        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            raise HTTPException (
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
            )
        token = str (uuid.uuid4 ())
        await cacheRedis.setex (f"verifier:{user.email}", 3600, token)

        event = UserAuthRegisteredEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            token=token,
        )
        eventEmitter = getEventEmitter ()
        await eventEmitter.emit ("user.auth.registered", event)
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def refresh (refreshToken: str) -> UserAuthTransformerDto:
        """
        Args:
            refreshToken (str)
        Returns:
            UserAuthTransformerDto
        """
        i18n = AppI18n.i18n ()
        try:
            isBlacklisted = await AppAuth.isTokenBlacklisted (refreshToken)
            if isBlacklisted:
                raise HTTPException (
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t ("_v1_user.auth.invalid_token"),
                )
            payload = AppAuth.verifyToken (refreshToken, "refresh")
            if not payload:
                raise HTTPException (
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t ("_v1_user.auth.invalid_token"),
                )
            userId = payload.get ("sub")
            if not userId:
                raise HTTPException (
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t ("_v1_user.auth.invalid_token"),
                )
            user = await UserAuthRepository.findOneById (userId)
            if not user:
                raise HTTPException (
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t ("_v1_user.auth.user_not_found"),
                )
            authConfig = AuthConfig.config ()
            accessToken = AppAuth.createAccessToken ({"sub": str (user.id), "email": user.email})
            newRefreshToken = AppAuth.createRefreshToken ({"sub": str (user.id), "email": user.email})
            await AppAuth.blacklistToken (refreshToken)
            accessTokenTtl = authConfig.jwt_access_token_expire_minutes * 60
            refreshTokenTtl = authConfig.jwt_refresh_token_expire_days * 24 * 60 * 60
            eventEmitter = getEventEmitter ()
            event = UserAuthRefreshedEvent (
                id=str (user.id),
                name=user.name,
                email=user.email,
                email_verified_at=user.email_verified_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
            )
            await eventEmitter.emit ("user.auth.refreshed", event)
            return UserAuthTransformerDto (
                accessTokenTtl=accessTokenTtl,
                refreshTokenTtl=refreshTokenTtl,
                accessToken=accessToken,
                refreshToken=newRefreshToken,
            )
        except HTTPException:
            raise
        except Exception:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t ("_v1_user.auth.invalid_token"),
            )

    @staticmethod
    async def logout (userId: str, token: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            token (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.logout (userId)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        await AppAuth.blacklistToken (token)
        eventEmitter = getEventEmitter ()
        event = UserAuthLoggedOutEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
        await eventEmitter.emit ("user.auth.loggedout", event)
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def me (userId: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.me (userId)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def verify (userEmail: str, token: Optional[str] = None) -> UserTransformerDto:
        """
        Args:
            userEmail (str)
            token (Optional[str])
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        if token:
            cacheRedis = AppContext.cacheRedis ()
            if not cacheRedis:
                raise HTTPException (
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
                )
            cachedToken = await cacheRedis.get (f"verifier:{userEmail}")
            if not cachedToken:
                raise HTTPException (
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t ("_v1_user.auth.invalid_token"),
                )
            if str (cachedToken) != str (token):
                raise HTTPException (
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t ("_v1_user.auth.invalid_token"),
                )
            await cacheRedis.delete (f"verifier:{userEmail}")
        user = await UserAuthRepository.verify (userEmail)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def reverify (userId: str) -> str:
        """
        Args:
            userId (str)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.reverify (userId)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            raise HTTPException (
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
            )
        token = str (uuid.uuid4 ())
        await cacheRedis.setex (f"verifier:{user.email}", 3600, token)
        eventEmitter = getEventEmitter ()
        event = UserAuthRegisteredEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            token=token,
        )
        await eventEmitter.emit ("user.auth.reverify", event)
        return i18n.t ("_v1_user.auth.verification_email_sent")

    @staticmethod
    async def reset (token: str, email: str, password: str) -> UserTransformerDto:
        """
        Args:
            token (str)
            email (str)
            password (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.reset (token, email, password)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_user.auth.invalid_or_expired_reset_token"),
            )
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def forget (userEmail: str) -> str:
        """
        Args:
            userEmail (str)
        Returns:
            str
        """
        from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
        from src.app.configs.app_config import AppConfig

        i18n = AppI18n.i18n ()
        appConfig = AppConfig.config ()
        user = await UserAuthRepository.findOneByEmail (userEmail)
        if not user:
            return i18n.t ("_v1_user.auth.reset_link_sent")
        token = str (uuid.uuid4 ())
        resetToken = await UserAuthRepository.forget (token, userEmail)
        if not resetToken:
            return i18n.t ("_v1_user.auth.reset_link_sent")
        baseUrl = f"{appConfig.frontend_url}/auth/reset-password/{userEmail}"
        parsedUrl = urlparse (baseUrl)
        queryParams = parse_qs (parsedUrl.query)
        queryParams["signed"] = [token]
        fullToken = urlunparse ((
            parsedUrl.scheme,
            parsedUrl.netloc,
            parsedUrl.path,
            parsedUrl.params,
            urlencode (queryParams, doseq=True),
            parsedUrl.fragment
        ))
        eventEmitter = getEventEmitter ()
        event = UserAuthResetEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            token=token,
        )

        await eventEmitter.emit ("user.auth.reset", event)
        return i18n.t ("_v1_user.auth.reset_link_sent")
