import json
import uuid
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from src.app.bases.app_context import AppContext
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.configs.app_config import AppConfig
from src.app.utils.app_avatar_storage import saveAvatar
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.user.events.user.auth.registered.event import UserAuthRegisteredEvent
from src.v1.api.user.support.security_notifier import SecurityNotifier
from src.v1.api.user.dtos.user_transformer_dto import (
    UserAccessTransformerDto,
    UserMeTransformerDto,
)
from src.v1.api.user.dtos.user_validator_dto import UserMeUpdateValidatorDto
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository

class UserProfileService:
    """
    UserProfileService
    """
    @staticmethod
    async def getMe (userId: str) -> UserMeTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            UserMeTransformerDto
        """
        i18n = AppI18n.i18n ()
        user, profile = await UserProfileRepository.getMe (userId)
        if user is None:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        appConfig = AppConfig.config ()
        return UserMeTransformerDto.fromUser (user, profile, appConfig.frontend_url)

    @staticmethod
    async def updateMe (
        userId: str,
        dto: UserMeUpdateValidatorDto,
        avatar: Optional[UploadFile] = None,
    ) -> UserMeTransformerDto:
        """
        Args:
            userId (str)
            dto (UserMeUpdateValidatorDto)
            avatar (Optional[UploadFile])
        Returns:
            UserMeTransformerDto
        """
        current, _profile = await UserProfileRepository.getMe (userId)
        if current is None:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        nextEmail = str (dto.email).strip ()
        emailChanged = nextEmail.lower () != (current.email or "").lower ()
        if emailChanged:
            if await UserAuthRepository.emailTaken (nextEmail, userId):
                i18n = AppI18n.i18n ()
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=i18n.t ("_v1_user.auth.email_already_exists"),
                )
            displayName = (dto.full_name or dto.name or current.email or "").strip ()
            await UserProfileService._requestEmailChange (current, nextEmail, displayName)
        nextName = (dto.name or "").strip ()
        if nextName and nextName != (current.name or ""):
            if await UserAuthRepository.nameTaken (nextName, userId):
                i18n = AppI18n.i18n ()
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=i18n.t ("_v1_user.auth.name_already_exists"),
                )
        userData = {
            "name": dto.name,
        }
        if dto.password:
            userData["password"] = dto.password

        profileData = {
            "full_name": dto.full_name,
            "interests": [
                value.strip ()
                for value in (dto.interests or [])
                if str (value).strip ()
            ],
        }

        avatarPath = await saveAvatar (avatar) if avatar is not None else None
        userData = UserProfileRepository.hashPasswordIfPresent (userData)
        user, profile = await UserProfileRepository.updateMe (
            userId,
            userData,
            profileData,
            avatarPath,
        )
        if user is None:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_user.auth.user_not_found"),
            )
        if dto.password:
            await SecurityNotifier.passwordChanged (user, user.id)
        AdminRefreshBroadcaster.schedule (["users"], user.id)
        appConfig = AppConfig.config ()
        return UserMeTransformerDto.fromUser (user, profile, appConfig.frontend_url)

    @staticmethod
    async def _requestEmailChange (user, newEmail: str, displayName: str) -> None:
        """
        Args:
            user (User)
            newEmail (str)
            displayName (str)
        Returns:
            None
        """
        cacheRedis = AppContext.cacheRedis ()
        if not cacheRedis:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=i18n.t ("_v1_user.auth.cache_service_unavailable"),
            )
        token = str (uuid.uuid4 ())
        await cacheRedis.setex (
            f"email-change:{newEmail.lower ()}",
            3600,
            json.dumps ({"user_id": user.id, "token": token}),
        )
        await getEventEmitter ().emit ("v1.user.profile.email-change", UserAuthRegisteredEvent (
            id=user.id,
            name=displayName or user.email,
            email=newEmail,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
            token=token,
        ))

    @staticmethod
    async def profileInterests () -> List[str]:
        """
        Returns:
            List[str]
        """
        return await UserProfileRepository.profileInterests ()

    @staticmethod
    async def accesses (userId: str) -> UserAccessTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            UserAccessTransformerDto
        """
        permissions, roles = await UserAclRepository.getUserAccesses (userId)
        return UserAccessTransformerDto (permissions=permissions, roles=roles)
