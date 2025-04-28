from typing import Optional, List, Dict
from fastapi import HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.notification.databases.models.notification_model import Notification
from src.v1.api.notification.dtos.notification_transformer_dto import NotificationTransformerDto
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.repositories.notification_admin_repository import NotificationAdminRepository

class NotificationAdminService:
    """
    NotificationAdminService

    Attributes:
        repository (NotificationAdminRepository)
    """
    repository = NotificationAdminRepository ()

    @staticmethod
    async def all (userId: str, orders: List[Dict[str, object]] = None, filters: List[Dict[str, object]] = None, page: OffsetPaginationType = None) -> OffsetPagination[NotificationTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
            page (OffsetPaginationType)
        Returns:
            OffsetPagination[NotificationTransformerDto]
        """
        result = await NotificationAdminService.repository.allOffset (userId, orders, filters, page)
        data = [NotificationTransformerDto.fromNotification (item) for item in result.data]
        return OffsetPagination (
            totalPage=result.totalPage,
            perPage=result.perPage,
            currentPage=result.currentPage,
            nextPage=result.nextPage,
            previousPage=result.previousPage,
            firstPage=result.firstPage,
            lastPage=result.lastPage,
            data=data
        )

    @staticmethod
    async def get (userId: str, id: str) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationAdminRepository.get (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def create (userId: str, data: NotificationCreateValidatorDto) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            data (NotificationCreateValidatorDto)
        Returns:
            NotificationTransformerDto
        """
        notificationData = {
            "user_id": data.user_id,
            "type": data.type,
            "data": data.data
        }
        notification = await NotificationAdminRepository.create (userId, notificationData)
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def update (userId: str, id: str, data: Dict[str, object]) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
            data (Dict[str, object])
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationAdminRepository.update (userId, id, data)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def delete (userId: str, id: str) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationAdminRepository.delete (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def restore (userId: str, id: str) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationAdminRepository.restore (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)
