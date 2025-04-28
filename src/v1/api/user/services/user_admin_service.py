from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_disk import AppDisk
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_queue import AppQueue
from src.app.constants.queue_constants import USER_ADMIN_QUEUE
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_transformer_dto import UserTransformerDto
from src.v1.api.user.dtos.user_validator_dto import UserCreateValidatorDto, UserUpdateValidatorDto
from src.v1.api.user.events.user.admin.activated.event import UserAdminActivatedEvent
from src.v1.api.user.events.user.admin.deactivated.event import UserAdminDeactivatedEvent
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository

class UserAdminService:
    """
    UserAdminService

    Attributes:
        repository (UserAdminRepository)
    """
    repository = UserAdminRepository ()

    @staticmethod
    async def all (userId: str, orders: List[Dict[str, object]] = None, filters: List[Dict[str, object]] = None, page: Dict[str, object] = None) -> OffsetPagination[UserTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Orderization])
            filters (List[Filterization])
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
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def create (userId: str, data: UserCreateValidatorDto) -> UserTransformerDto:
        """
        Args:
            userId (str)
            data (UserCreateValidatorDto)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        existingUser = await UserAuthRepository.findOneByEmail (data.email)
        if existingUser:
            raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.email_already_exists"))
        hashedPassword = AppAuth.hashPassword (data.password)
        user = User (
            name=data.name,
            email=data.email,
            password=hashedPassword,
            email_verified_at=datetime.utcnow ()
        )
        user = await UserAuthRepository.create (user)
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def update (userId: str, id: str, data: UserUpdateValidatorDto) -> UserTransformerDto:
        """
        Args:
            userId (str)
            id (str)
            data (UserUpdateValidatorDto)
        Returns:
            UserTransformerDto
        """
        i18n = AppI18n.i18n ()
        user = await UserAuthRepository.findOneById (id)
        if not user:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_user.auth.user_not_found"))
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            existingUser = await UserAuthRepository.findOneByEmail (data.email)
            if existingUser and existingUser.id != id:
                raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=i18n.t ("_v1_user.auth.email_already_exists"))
            user.email = data.email
        if data.password is not None:
            user.password = AppAuth.hashPassword (data.password)
        user = await UserAuthRepository.update (user)
        return UserTransformerDto.fromUser (user)

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
        user.deleted_at = datetime.utcnow ()
        user = await UserAuthRepository.update (user)
        eventEmitter = getEventEmitter ()
        event = UserAdminDeactivatedEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )
        await eventEmitter.emit ("v1.user.admin.deactivated", event)
        return UserTransformerDto.fromUser (user)

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
        user.deleted_at = None
        user = await UserAuthRepository.update (user)
        eventEmitter = getEventEmitter ()
        event = UserAdminActivatedEvent (
            id=user.id,
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at
        )
        await eventEmitter.emit ("v1.user.admin.activated", event)
        return UserTransformerDto.fromUser (user)

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
        if user.email_verified_at is None:
            user.email_verified_at = datetime.utcnow ()
            user = await UserAuthRepository.update (user)
        return UserTransformerDto.fromUser (user)

    @staticmethod
    async def import_users (userId: str, fileContent: bytes, filename: str) -> str:
        """
        Args:
            userId (str)
            fileContent (bytes)
            filename (str)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()

        AppQueue.enqueue (USER_ADMIN_QUEUE, "import", {
            "userId": userId,
            "file": filename,
            "fileContent": fileContent
        })

        return i18n.t ("_v1_user.import.started.message")

    @staticmethod
    async def export_users (userId: str, export_type: str) -> str:
        """
        Args:
            userId (str)
            export_type (str)
        Returns:
            str
        """
        i18n = AppI18n.i18n ()

        validTypes = ["csv", "xls", "xlsx"]
        normalizedType = export_type.lower () if export_type.lower () in validTypes else "csv"

        AppQueue.enqueue (USER_ADMIN_QUEUE, "export", {
            "userId": userId,
            "type": normalizedType
        })

        return i18n.t ("_v1_user.export.started.message")
