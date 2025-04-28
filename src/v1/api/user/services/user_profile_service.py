from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from src.app.bases.app_i18n import AppI18n
from src.app.configs.app_config import AppConfig
from src.app.utils.app_avatar_storage import saveAvatar
from src.v1.api.user.dtos.user_transformer_dto import (
    UserAccessTransformerDto,
    UserMeTransformerDto,
)
from src.v1.api.user.dtos.user_validator_dto import UserMeUpdateValidatorDto
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
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
        return UserMeTransformerDto.fromUser (user, profile, getattr (appConfig, "app_url", ""))

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
        userData = {
            "name": dto.name,
            "email": dto.email,
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
        appConfig = AppConfig.config ()
        return UserMeTransformerDto.fromUser (user, profile, getattr (appConfig, "app_url", ""))

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
