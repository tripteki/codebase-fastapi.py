from typing import Optional, List, Dict
from fastapi import HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.dtos.app_dto import BatchPayloadType
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.notification.databases.models.notification_model import Notification
from src.v1.api.notification.dtos.notification_transformer_dto import NotificationTransformerDto, NotificationCountTransformerDto, NotificationReadTransformerDto, NotificationUnreadTransformerDto
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.repositories.notification_user_repository import NotificationUserRepository

class NotificationUserService:
    """
    NotificationUserService

    Attributes:
        repository (NotificationUserRepository)
    """
    repository = NotificationUserRepository ()

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
        result = await NotificationUserService.repository.allOffset (userId, orders, filters, page)
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
    async def count (userId: str) -> NotificationCountTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            NotificationCountTransformerDto
        """
        counts = await NotificationUserService.repository.count (userId)
        return NotificationCountTransformerDto (count=counts)

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
        notification = await NotificationUserRepository.get (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def readAll (userId: str) -> BatchPayloadType:
        """
        Args:
            userId (str)
        Returns:
            BatchPayloadType
        """
        result = await NotificationUserService.repository.readAll (userId)
        return BatchPayloadType (count=result)

    @staticmethod
    async def unreadAll (userId: str) -> NotificationUnreadTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            NotificationUnreadTransformerDto
        """
        return NotificationUnreadTransformerDto (unread=0)

    @staticmethod
    async def unreadCount (userId: str) -> NotificationUnreadTransformerDto:
        """
        Args:
            userId (str)
        Returns:
            NotificationUnreadTransformerDto
        """
        return NotificationUnreadTransformerDto (unread=0)

    @staticmethod
    async def read (userId: str, id: str) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationUserRepository.read (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def unread (userId: str, id: str) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            NotificationTransformerDto
        """
        i18n = AppI18n.i18n ()
        notification = await NotificationUserRepository.unread (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)

    @staticmethod
    async def countReadUnread (userId: str) -> Dict[str, int]:
        """
        Args:
            userId (str)
        Returns:
            Dict[str, int]
        """
        return await NotificationUserRepository.count (userId)

    @staticmethod
    async def notify (userId: str, data: NotificationCreateValidatorDto) -> NotificationTransformerDto:
        """
        Args:
            userId (str)
            data (NotificationCreateValidatorDto)
        Returns:
            NotificationTransformerDto
        """
        dataDict = data.dict ()
        dataDict.pop ("user_id", None)
        i18n = AppI18n.i18n ()
        notification = await NotificationUserRepository.create (userId, dataDict)
        if not notification:
            raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=i18n.t ("_v1_notification.failed_to_create"))
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
        notification = await NotificationUserRepository.delete (userId, id)
        if not notification:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail=i18n.t ("_v1_notification.notification_not_found"))
        return NotificationTransformerDto.fromNotification (notification)
