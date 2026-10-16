import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request, status
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_cache import AppCache
from src.app.bases.app_context import AppContext
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.configs.app_config import AppConfig
from src.app.configs.auth_config import AuthConfig
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.dtos.user_transformer_dto import UserAuthTransformerDto, UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import UserAuthDto, UserCreateValidatorDto
from src.v1.api.user.events.user.auth.loggedin.event import UserAuthLoggedInEvent
from src.v1.api.user.events.user.auth.loggedout.event import UserAuthLoggedOutEvent
from src.v1.api.user.events.user.auth.refreshed.event import UserAuthRefreshedEvent
from src.v1.api.user.events.user.auth.registered.event import UserAuthRegisteredEvent
from src.v1.api.user.events.user.auth.reset.event import UserAuthResetEvent
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository
from src.v1.api.user.support.registration_notifier import RegistrationNotifier
from src.v1.api.user.support.security_notifier import SecurityNotifier

class UserAuthService:
    """
    UserAuthService
    """
    @staticmethod
    async def _fullNameForUser (userId: str) -> Optional[str]:
        """
        Args:
            userId (str)
        Returns:
            Optional[str]
        """
        profile = await UserProfileRepository.findProfileByUserId (userId)
        return profile.full_name if profile else None

    @staticmethod
    async def _eventDisplayName (user: User) -> str:
        """
        Args:
            user (User)
        Returns:
            str
        """
        fullName = await UserAuthService._fullNameForUser (user.id)
        return (fullName or "").strip () or user.email

    @staticmethod
    async def _toDto (user: User, role: Optional[str] = None) -> UserTransformerDto:
        """
        Args:
            user (User)
            role (Optional[str])
        Returns:
            UserTransformerDto
        """
        profile = await UserProfileRepository.findProfileByUserId (user.id)
        appUrl = (AppConfig.config ().frontend_url or "").rstrip ("/")
        return UserTransformerDto.fromUser (user, role, profile, appUrl)

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
        if dto.field () == "name":
            user = await UserAuthRepository.findOneByName (dto.identifierValue)
        else:
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
        if user.email_verified_at is None:
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "email_not_verified",
                    "message": i18n.t ("_v1_user.auth.email_not_verified"),
                },
            )
        authConfig = AuthConfig.config ()
        remember = AppAuth.resolveRemember (dto.remember)
        accessToken = AppAuth.createAccessToken ({"sub": user.id, "email": user.email})
        refreshToken = AppAuth.createRefreshToken (
            {"sub": user.id, "email": user.email},
            remember=remember,
        )
        accessTokenTtl = authConfig.jwt_access_token_expire_minutes * 60
        refreshTokenTtl = AppAuth.refreshTokenExpireDays (remember) * 24 * 60 * 60
        eventEmitter = getEventEmitter ()
        event = UserAuthLoggedInEvent (
            id=user.id,
            name=await UserAuthService._eventDisplayName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
        await eventEmitter.emit ("v1.user.auth.loggedin", event)
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
        if await UserAuthRepository.emailTaken (dto.email):
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_user.auth.email_already_exists"),
            )
        if dto.name and await UserAuthRepository.nameTaken (dto.name):
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_user.auth.name_already_exists"),
            )
        hashedPassword = AppAuth.hashPassword (dto.password)
        user = User (
            name=dto.name,
            email=dto.email,
            password=hashedPassword,
        )
        user = await UserAuthRepository.create (user)
        try:
            UserAclRepository.assignSingleRole (user.id, UserRoleEnum.User.value)
        except LookupError:
            await UserAclRepository.syncUserRole (user.id, UserRoleEnum.User.value)
        displayName = (dto.full_name or dto.name or "").strip ()
        await UserAdminRepository ().upsertProfile (user.id, displayName or user.email)

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
            name=await UserAuthService._eventDisplayName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            token=token,
        )
        eventEmitter = getEventEmitter ()
        await eventEmitter.emit ("v1.user.auth.registered", event)
        AdminRefreshBroadcaster.schedule (["users"], user.id)
        return await UserAuthService._toDto (user, UserRoleEnum.User.value)

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
            remember = AppAuth.resolveRemember (payload.get ("remember"))
            accessToken = AppAuth.createAccessToken ({"sub": str (user.id), "email": user.email})
            newRefreshToken = AppAuth.createRefreshToken (
                {"sub": str (user.id), "email": user.email},
                remember=remember,
            )
            await AppAuth.blacklistToken (refreshToken)
            accessTokenTtl = authConfig.jwt_access_token_expire_minutes * 60
            refreshTokenTtl = AppAuth.refreshTokenExpireDays (remember) * 24 * 60 * 60
            eventEmitter = getEventEmitter ()
            event = UserAuthRefreshedEvent (
                id=str (user.id),
                name=await UserAuthService._eventDisplayName (user),
                email=user.email,
                email_verified_at=user.email_verified_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
            )
            await eventEmitter.emit ("v1.user.auth.refreshed", event)
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
            name=await UserAuthService._eventDisplayName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
        await eventEmitter.emit ("v1.user.auth.loggedout", event)
        return await UserAuthService._toDto (user)

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
        return await UserAuthService._toDto (user)

    @staticmethod
    async def verify (userEmail: str, token: str) -> UserTransformerDto:
        """
        Args:
            userEmail (str)
            token (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        signed = (token or "").strip ()
        if not signed:
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.invalid_or_expired_verify_link"),
            )
        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            raise HTTPException (
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
            )
        cachedToken = await cacheRedis.get (f"verifier:{userEmail}")
        if not cachedToken:
            changed = await UserAuthService._confirmEmailChange (userEmail, signed)
            if changed is not None:
                return changed
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.invalid_or_expired_verify_link"),
            )
        if str (cachedToken) != str (signed):
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.invalid_or_expired_verify_link"),
            )
        await cacheRedis.delete (f"verifier:{userEmail}")
        user = await UserAuthRepository.verify (userEmail)
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        await RegistrationNotifier.afterEmailVerified (user)
        AdminRefreshBroadcaster.schedule (["users"], user.id)
        return await UserAuthService._toDto (user)

    @staticmethod
    async def _confirmEmailChange (newEmail: str, signed: str) -> Optional[UserTransformerDto]:
        """
        Args:
            newEmail (str)
            signed (str)
        Returns:
            Optional[UserTransformerDto]
        """
        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            return None
        key = f"email-change:{(newEmail or '').strip ().lower ()}"
        raw = await cacheRedis.get (key)
        if not raw:
            return None
        pending = json.loads (raw)
        if str (pending.get ("token")) != str (signed):
            return None
        await cacheRedis.delete (key)
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (str (pending.get ("user_id")))
        if not user:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        if await UserAuthRepository.emailTaken (newEmail, user.id):
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_user.auth.email_already_exists"),
            )
        previousEmail = user.email
        user.email = newEmail.strip ()
        user = await UserAuthRepository.update (user)
        await SecurityNotifier.emailChanged (user, previousEmail, False)
        AdminRefreshBroadcaster.schedule (["users"], user.id)
        return await UserAuthService._toDto (user)

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
        return await UserAuthService.sendVerificationEmail (user)

    @staticmethod
    async def sendVerificationEmail (user: User) -> str:
        """
        Args:
            user (User)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            raise HTTPException (
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
            )
        token = str (uuid.uuid4 ())
        await cacheRedis.setex (f"verifier:{user.email}", 3600, token)
        await getEventEmitter ().emit ("v1.user.auth.reverify", UserAuthRegisteredEvent (
            id=user.id,
            name=await UserAuthService._eventDisplayName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            token=token,
        ))
        return i18n.t ("_v1_user.auth.verification_email_sent")

    @staticmethod
    async def reverifyByEmail (userEmail: str) -> str:
        """
        Args:
            userEmail (str)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneByEmail (userEmail)
        if not user or user.email_verified_at is not None:
            return i18n.t ("_v1_user.auth.verification_email_sent")
        return await UserAuthService.sendVerificationEmail (user)

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
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.invalid_or_expired_reset_token"),
            )
        await SecurityNotifier.passwordChanged (user)
        return await UserAuthService._toDto (user)

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
            name=await UserAuthService._eventDisplayName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            token=token,
        )

        await eventEmitter.emit ("v1.user.auth.reset", event)
        return i18n.t ("_v1_user.auth.reset_link_sent")
