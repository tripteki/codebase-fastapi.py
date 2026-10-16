from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlmodel import Session, select
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.app.configs.app_config import AppConfig
from src.app.utils.app_avatar_storage import saveAvatar
from src.app.bases.app_disk import AppDisk
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.processors.app_export_processor import AppExportProcessor
from src.app.processors.app_import_processor import AppImportProcessor
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.log.support.activity_recorder import ActivityRecorder
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.support.account_notifier import AccountNotifier
from src.v1.api.user.support.registration_notifier import RegistrationNotifier
from src.v1.api.user.support.security_notifier import SecurityNotifier
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import UserCreateValidatorDto, UserUpdateValidatorDto
from src.v1.api.user.events.user.admin.activated.event import UserAdminActivatedEvent
from src.v1.api.user.events.user.admin.deactivated.event import UserAdminDeactivatedEvent
from src.v1.api.user.processors.user_admin_import_processor import UserAdminImportProcessor
from src.v1.api.user.processors.user_admin_export_processor import UserAdminExportProcessor
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository
from src.v1.api.user.repositories.user_profile_repository import UserProfileRepository

class UserAdminService:
    """
    UserAdminService

    Attributes:
        repository (UserAdminRepository)
    """
    repository = UserAdminRepository ()

    @staticmethod
    async def _toDto (user: User) -> UserTransformerDto:
        """
        Args:
            user (User)
        Returns:
            UserTransformerDto
        """
        role = await UserAclRepository.getUserRole (user.id)
        profile = await UserProfileRepository.findProfileByUserId (user.id)
        appUrl = (AppConfig.config ().frontend_url or "").rstrip ("/")
        return UserTransformerDto.fromUser (user, role, profile, appUrl)

    @staticmethod
    async def _eventName (user: User) -> str:
        """
        Args:
            user (User)
        Returns:
            str
        """
        profile = await UserProfileRepository.findProfileByUserId (user.id)
        fullName = (profile.full_name or "").strip () if profile else ""
        return fullName or user.email

    @staticmethod
    async def _assertCanAssign (actorId: str, roleName: str, targetId: Optional[str] = None) -> None:
        """
        Args:
            actorId (str)
            roleName (str)
            targetId (Optional[str])
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        actorRole = await UserAclRepository.getUserRole (actorId)
        if actorRole != UserRoleEnum.Superadmin and roleName != UserRoleEnum.User:
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.role_forbidden"),
            )
        if targetId is None:
            return
        if targetId == actorId:
            currentRole = await UserAclRepository.getUserRole (targetId)
            if currentRole != roleName:
                raise HTTPException (
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t ("_v1_user.auth.role_self_forbidden"),
                )
        await UserAdminService._assertCanMutate (actorId, targetId)

    @staticmethod
    async def _assertCanMutate (actorId: str, targetId: str) -> None:
        """
        Args:
            actorId (str)
            targetId (str)
        Returns:
            None
        """
        if actorId == targetId:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.account_locked"),
            )
        actorRole = await UserAclRepository.getUserRole (actorId)
        targetRole = await UserAclRepository.getUserRole (targetId)
        if targetRole in UserRoleEnum.privileged () and actorRole != UserRoleEnum.Superadmin:
            i18n = AppI18n.i18n ()
            raise HTTPException (
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t ("_v1_user.auth.account_locked"),
            )

    @staticmethod
    async def _assignRole (userId: str, roleName: str) -> None:
        """
        Args:
            userId (str)
            roleName (str)
        Returns:
            None
        """
        stored = roleName.value if isinstance (roleName, UserRoleEnum) else roleName
        try:
            UserAclRepository.assignSingleRole (userId, stored)
        except LookupError:
            await UserAclRepository.syncUserRole (userId, stored)

    @staticmethod
    async def all (userId: str, orders: List[Dict[str, object]] = None, filters: List[Dict[str, object]] = None, page: Dict[str, object] = None) -> OffsetPagination[UserTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
            page (Dict[str, object])
        Returns:
            OffsetPagination[UserTransformerDto]
        """
        pageType = OffsetPaginationType (
            currentPage=page.get ("currentPage", 1) if page else 1,
            limitPage=page.get ("limitPage", 10) if page else 10
        )
        return await UserAdminService.repository.allOffset (userId, orders, filters, pageType)

    @staticmethod
    async def get (userId: str, id: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (id)
        if not user:
            user = await UserAuthRepository.findOneByIdIncludingDeleted (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        return await UserAdminService._toDto (user)

    @staticmethod
    async def create (
        userId: str,
        data: UserCreateValidatorDto,
        avatar: Optional[UploadFile] = None,
    ) -> UserTransformerDto:
        """
        Args:
            userId (str)
            data (UserCreateValidatorDto)
            avatar (Optional[UploadFile])
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        roleName = data.role or UserRoleEnum.User
        await UserAdminService._assertCanAssign (userId, roleName)
        if await UserAuthRepository.emailTaken (data.email):
            raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.email_already_exists"))
        hashedPassword = AppAuth.hashPassword (data.password)
        displayName = (data.full_name or data.name).strip ()
        if await UserAuthRepository.nameTaken (displayName):
            raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.name_already_exists"))
        user = User (
            name=displayName,
            email=data.email,
            password=hashedPassword,
            email_verified_at=datetime.utcnow ()
        )
        user = await UserAuthRepository.create (user)
        avatarPath = await saveAvatar (avatar) if avatar is not None else None
        await UserAdminService.repository.upsertProfile (user.id, displayName, avatarPath)
        await UserAdminService._assignRole (user.id, roleName)
        storedRole = roleName.value if isinstance (roleName, UserRoleEnum) else roleName
        ActivityRecorder.userCreated (
            causerId=userId,
            userId=user.id,
            attributes={"full_name": displayName, "email": user.email, "role": storedRole},
        )
        await AccountNotifier.accountCreated (user, storedRole)
        return await UserAdminService._toDto (user)

    @staticmethod
    async def update (
        userId: str,
        id: str,
        data: UserUpdateValidatorDto,
        avatar: Optional[UploadFile] = None,
    ) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
            data (UserUpdateValidatorDto)
            avatar (Optional[UploadFile])
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        await UserAdminService._assertCanMutate (userId, id)
        if data.role is not None:
            await UserAdminService._assertCanAssign (userId, data.role, id)
        previousEmail = user.email
        previousRole = await UserAclRepository.getUserRole (id)
        displayName = data.full_name or data.name
        if displayName is not None:
            if await UserAuthRepository.nameTaken (displayName, id):
                raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.name_already_exists"))
            user.name = displayName
        avatarPath = await saveAvatar (avatar) if avatar is not None else None
        if displayName is not None or avatarPath is not None:
            await UserAdminService.repository.upsertProfile (user.id, displayName, avatarPath)
        if data.email is not None:
            if await UserAuthRepository.emailTaken (data.email, id):
                raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.email_already_exists"))
            user.email = data.email
        if data.password is not None:
            user.password = AppAuth.hashPassword (data.password)
        user = await UserAuthRepository.update (user)
        storedRole = data.role.value if isinstance (data.role, UserRoleEnum) else data.role
        if storedRole is not None:
            await UserAdminService._assignRole (user.id, storedRole)
        attributes = {}
        if displayName is not None:
            attributes["full_name"] = displayName
        if data.email is not None:
            attributes["email"] = data.email
        if storedRole is not None:
            attributes["role"] = storedRole
        if attributes:
            ActivityRecorder.userUpdated (
                causerId=userId,
                userId=user.id,
                attributes=attributes,
            )
        if data.email is not None and data.email.lower () != (previousEmail or "").lower ():
            await SecurityNotifier.emailChanged (user, previousEmail, True)
        if data.password is not None:
            await SecurityNotifier.passwordChanged (user, userId)
        if storedRole is not None and storedRole != previousRole:
            await AccountNotifier.roleChanged (user, storedRole)
        return await UserAdminService._toDto (user)

    @staticmethod
    async def delete (userId: str, id: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        await UserAdminService._assertCanMutate (userId, id)
        user.deleted_at = datetime.utcnow ()
        user = await UserAuthRepository.update (user)
        eventEmitter = getEventEmitter ()
        event = UserAdminDeactivatedEvent (
            id=user.id,
            name=await UserAdminService._eventName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )
        await eventEmitter.emit ("v1.user.admin.deactivated", event)
        ActivityRecorder.userDeactivated (causerId=userId, userId=user.id)
        return await UserAdminService._toDto (user)

    @staticmethod
    async def forceDelete (userId: str, id: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        await UserAdminService._assertCanMutate (userId, id)
        user = await UserAuthRepository.findOneByIdIncludingDeleted (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        dto = await UserAdminService._toDto (user)
        deleted = await UserAdminRepository.forceDelete (id)
        if not deleted:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        ActivityRecorder.log (
            description="user force deleted",
            event="deleted",
            subjectType="User",
            subjectId=user.id,
            causerId=userId,
            properties={"email": user.email},
        )
        return dto

    @staticmethod
    async def restore (userId: str, id: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneDeletedById (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        await UserAdminService._assertCanMutate (userId, id)
        user.deleted_at = None
        user = await UserAuthRepository.update (user)
        eventEmitter = getEventEmitter ()
        event = UserAdminActivatedEvent (
            id=user.id,
            name=await UserAdminService._eventName (user),
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )
        await eventEmitter.emit ("v1.user.admin.activated", event)
        ActivityRecorder.userActivated (causerId=userId, userId=user.id)
        return await UserAdminService._toDto (user)

    @staticmethod
    async def verify (userId: str, id: str) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        await UserAdminService._assertCanMutate (userId, id)
        if user.email_verified_at is None:
            user.email_verified_at = datetime.utcnow ()
            user = await UserAuthRepository.update (user)
            ActivityRecorder.userVerified (causerId=userId, userId=user.id)
            await RegistrationNotifier.afterEmailVerified (user, userId)
        return await UserAdminService._toDto (user)

    @staticmethod
    async def importUsers (background_tasks: BackgroundTasks, userId: str, fileContent: bytes, filename: str) -> str:
        """
        Args:
            background_tasks (BackgroundTasks)
            userId (str)
            fileContent (bytes)
            filename (str)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        background_tasks.add_task (
            UserAdminImportProcessor.run,
            userId,
            fileContent,
            filename,
        )
        return i18n.t ("_v1_user.import.started.message")

    @staticmethod
    async def exportUsers (
        background_tasks: BackgroundTasks,
        userId: str,
        export_type: str,
        orders: List[Dict[str, object]] = None,
        filters: List[Dict[str, object]] = None,
    ) -> str:
        """
        Args:
            background_tasks (BackgroundTasks)
            userId (str)
            export_type (str)
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        background_tasks.add_task (
            UserAdminExportProcessor.run,
            userId,
            export_type,
            orders,
            filters,
        )
        return i18n.t ("_v1_user.export.started.message")
