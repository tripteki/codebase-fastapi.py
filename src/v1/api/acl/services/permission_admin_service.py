from typing import Any, Dict, List
from fastapi import BackgroundTasks, HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.acl.dtos.permission_transformer_dto import PermissionTransformerDto
from src.v1.api.acl.dtos.permission_validator_dto import (
    PermissionCreateValidatorDto,
    PermissionUpdateValidatorDto,
)
from src.v1.api.acl.processors.permission_admin_export_processor import PermissionAdminExportProcessor
from src.v1.api.acl.processors.permission_admin_import_processor import PermissionAdminImportProcessor
from src.v1.api.acl.repositories.permission_admin_repository import PermissionAdminRepository
from src.v1.api.acl.support.system_permission_guard import SystemPermissionGuard
from src.v1.api.log.support.activity_recorder import ActivityRecorder

class PermissionAdminService:
    """
    PermissionAdminService

    Attributes:
        repository (PermissionAdminRepository)
    """
    repository = PermissionAdminRepository ()

    @staticmethod
    async def all (
        orders: List[Dict[str, object]] = None,
        filters: List[Dict[str, object]] = None,
        page: Dict[str, object] = None,
    ) -> OffsetPagination[PermissionTransformerDto]:
        """
        Args:
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
            page (Dict[str, object])
        Returns:
            OffsetPagination[PermissionTransformerDto]
        """
        pageType = OffsetPaginationType (
            currentPage=page.get ("currentPage", 1) if page else 1,
            limitPage=page.get ("limitPage", 10) if page else 10,
        )
        return await PermissionAdminService.repository.allOffset (orders, filters, pageType)

    @staticmethod
    async def get (id: str) -> PermissionTransformerDto:
        """
        Args:
            id (str)
        Returns:
            PermissionTransformerDto
        """
        i18n = AppI18n.i18n ()
        permission = await PermissionAdminService.repository.findById (id)
        if not permission:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.permission.not_found"),
            )
        return PermissionTransformerDto.fromPermission (permission)

    @staticmethod
    async def create (causerId: str, data: PermissionCreateValidatorDto) -> PermissionTransformerDto:
        """
        Args:
            causerId (str)
            data (PermissionCreateValidatorDto)
        Returns:
            PermissionTransformerDto
        """
        i18n = AppI18n.i18n ()
        existing = await PermissionAdminService.repository.findByNameGuard (
            data.name,
            data.guard_name,
        )
        if existing:
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_acl.permission.name_exists"),
            )
        permission = await PermissionAdminService.repository.create (
            data.name.strip (),
            data.guard_name,
        )
        ActivityRecorder.permissionCreated (
            causerId=causerId,
            permissionId=permission.id,
            attributes={"name": permission.name, "guard_name": permission.guard_name},
        )
        return PermissionTransformerDto.fromPermission (permission)

    @staticmethod
    async def update (causerId: str, id: str, data: PermissionUpdateValidatorDto) -> PermissionTransformerDto:
        """
        Args:
            causerId (str)
            id (str)
            data (PermissionUpdateValidatorDto)
        Returns:
            PermissionTransformerDto
        """
        i18n = AppI18n.i18n ()
        permission = await PermissionAdminService.repository.findById (id)
        if not permission:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.permission.not_found"),
            )

        if data.name is not None or data.guard_name is not None:
            SystemPermissionGuard.assertMutable (permission.name)

        nextName = data.name.strip () if data.name is not None else permission.name
        nextGuard = data.guard_name if data.guard_name is not None else permission.guard_name

        if nextName != permission.name or nextGuard != permission.guard_name:
            existing = await PermissionAdminService.repository.findByNameGuard (nextName, nextGuard)
            if existing and existing.id != permission.id:
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=i18n.t ("_v1_acl.permission.name_exists"),
                )

        permission.name = nextName
        permission.guard_name = nextGuard
        permission = await PermissionAdminService.repository.update (permission)
        ActivityRecorder.permissionUpdated (
            causerId=causerId,
            permissionId=permission.id,
            attributes={"name": permission.name, "guard_name": permission.guard_name},
        )
        return PermissionTransformerDto.fromPermission (permission)

    @staticmethod
    async def delete (causerId: str, id: str) -> PermissionTransformerDto:
        """
        Args:
            causerId (str)
            id (str)
        Returns:
            PermissionTransformerDto
        """
        i18n = AppI18n.i18n ()
        permission = await PermissionAdminService.repository.findById (id)
        if not permission:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.permission.not_found"),
            )
        SystemPermissionGuard.assertMutable (permission.name)
        dto = PermissionTransformerDto.fromPermission (permission)
        await PermissionAdminService.repository.delete (permission)
        ActivityRecorder.permissionDeleted (
            causerId=causerId,
            permissionId=dto.id,
            attributes={"name": dto.name, "guard_name": dto.guard_name},
        )
        return dto

    @staticmethod
    async def importPermissions (
        background_tasks: BackgroundTasks,
        userId: str,
        fileContent: bytes,
        filename: str,
    ) -> str:
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
            PermissionAdminImportProcessor.run,
            userId,
            fileContent,
            filename,
        )
        return i18n.t ("_v1_acl.import.started.message")

    @staticmethod
    async def exportPermissions (
        background_tasks: BackgroundTasks,
        userId: str,
        export_type: str,
        orders: List[Any] = None,
        filters: List[Any] = None,
    ) -> str:
        """
        Args:
            background_tasks (BackgroundTasks)
            userId (str)
            export_type (str)
            orders (List[Any])
            filters (List[Any])
        Returns:
            str
        """
        i18n = AppI18n.i18n ()
        background_tasks.add_task (
            PermissionAdminExportProcessor.run,
            userId,
            export_type,
            orders,
            filters,
        )
        return i18n.t ("_v1_acl.export.started.message")
