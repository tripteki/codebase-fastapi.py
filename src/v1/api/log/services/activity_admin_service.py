from typing import Dict, List
from fastapi import HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.log.dtos.activity_transformer_dto import ActivityTransformerDto
from src.v1.api.log.repositories.activity_admin_repository import ActivityAdminRepository
from src.v1.api.log.support.activity_scope import ActivityScope

class ActivityAdminService:
    """
    ActivityAdminService

    Attributes:
        repository (ActivityAdminRepository)
    """
    repository = ActivityAdminRepository ()

    @staticmethod
    async def all (
        userId: str,
        orders: List[Dict[str, object]] = None,
        filters: List[Dict[str, object]] = None,
        page: Dict[str, object] = None,
    ) -> OffsetPagination[ActivityTransformerDto]:
        """
        Args:
            userId (str)
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
            page (Dict[str, object])
        Returns:
            OffsetPagination[ActivityTransformerDto]
        """
        pageType = OffsetPaginationType (
            currentPage=page.get ("currentPage", 1) if page else 1,
            limitPage=page.get ("limitPage", 10) if page else 10,
        )
        ownerId = await ActivityScope.ownerIdFor (userId)
        return await ActivityAdminService.repository.allOffset (orders, filters, pageType, ownerId)

    @staticmethod
    async def get (userId: str, id: str) -> ActivityTransformerDto:
        """
        Args:
            userId (str)
            id (str)
        Returns:
            ActivityTransformerDto
        """
        i18n = AppI18n.i18n ()
        ownerId = await ActivityScope.ownerIdFor (userId)
        activity = await ActivityAdminService.repository.findById (id, ownerId)
        if not activity:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_log.activity.not_found"),
            )
        causer = await ActivityAdminService.repository.findCauser (activity.causer_id)
        causerFullName = await ActivityAdminService.repository.findCauserFullName (
            activity.causer_id
        )
        return ActivityTransformerDto.fromActivity (
            activity,
            causer=causer,
            causerFullName=causerFullName,
            withDetails=True,
        )
