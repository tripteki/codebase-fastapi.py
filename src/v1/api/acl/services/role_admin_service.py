from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks, HTTPException, status
from src.app.bases.app_i18n import AppI18n
from src.app.repositories.app_repository import OffsetPagination, OffsetPaginationType
from src.v1.api.acl.dtos.role_transformer_dto import RoleTransformerDto
from src.v1.api.acl.dtos.role_validator_dto import RoleCreateValidatorDto, RoleUpdateValidatorDto
from src.v1.api.acl.processors.role_admin_export_processor import RoleAdminExportProcessor
from src.v1.api.acl.processors.role_admin_import_processor import RoleAdminImportProcessor
from src.v1.api.acl.repositories.permission_admin_repository import PermissionAdminRepository
from src.v1.api.acl.repositories.role_admin_repository import RoleAdminRepository
from src.v1.api.acl.support.system_role_guard import SystemRoleGuard
from src.v1.api.log.support.activity_recorder import ActivityRecorder
from src.v1.api.user.databases.models.acl_model import Role

class RoleAdminService:
    """
    RoleAdminService

    Attributes:
        repository (RoleAdminRepository)
        permissionRepository (PermissionAdminRepository)
    """
    repository = RoleAdminRepository ()
    permissionRepository = PermissionAdminRepository ()

    @staticmethod
    async def _toDto (role: Role) -> RoleTransformerDto:
        """
        Args:
            role (Role)
        Returns:
            RoleTransformerDto
        """
        permissions = await RoleAdminService.repository.getPermissions (role.id)
        usersCount = await RoleAdminService.repository.countUsers (role.id)
        return RoleTransformerDto.fromRole (role, permissions, usersCount)

    @staticmethod
    async def _assertPermissionIds (permissionIds: List[str]) -> None:
        """
        Args:
            permissionIds (List[str])
        Returns:
            None
        """
        if not permissionIds:
            return
        i18n = AppI18n.i18n ()
        found = await RoleAdminService.permissionRepository.findByIds (permissionIds)
        foundIds = {item.id for item in found}
        missing = [item for item in permissionIds if item not in foundIds]
        if missing:
            raise HTTPException (
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=i18n.t ("_v1_acl.role.permissions_not_found"),
            )

    @staticmethod
    async def all (
        orders: List[Dict[str, object]] = None,
        filters: List[Dict[str, object]] = None,
        page: Dict[str, object] = None,
    ) -> OffsetPagination[RoleTransformerDto]:
        """
        Args:
            orders (List[Dict[str, object]])
            filters (List[Dict[str, object]])
            page (Dict[str, object])
        Returns:
            OffsetPagination[RoleTransformerDto]
        """
        pageType = OffsetPaginationType (
            currentPage=page.get ("currentPage", 1) if page else 1,
            limitPage=page.get ("limitPage", 10) if page else 10,
        )
        return await RoleAdminService.repository.allOffset (orders, filters, pageType)

    @staticmethod
    async def get (id: str) -> RoleTransformerDto:
        """
        Args:
            id (str)
        Returns:
            RoleTransformerDto
        """
        i18n = AppI18n.i18n ()
        role = await RoleAdminService.repository.findById (id)
        if not role:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.role.not_found"),
            )
        return await RoleAdminService._toDto (role)

    @staticmethod
    async def create (causerId: str, data: RoleCreateValidatorDto) -> RoleTransformerDto:
        """
        Args:
            causerId (str)
            data (RoleCreateValidatorDto)
        Returns:
            RoleTransformerDto
        """
        i18n = AppI18n.i18n ()
        name = data.name.strip ()
        SystemRoleGuard.assertCreatableName (name)

        existing = await RoleAdminService.repository.findByNameGuard (name, data.guard_name)
        if existing:
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=i18n.t ("_v1_acl.role.name_exists"),
            )

        await RoleAdminService._assertPermissionIds (data.permission_ids)
        role = await RoleAdminService.repository.create (
            name,
            data.guard_name,
            data.permission_ids,
        )
        ActivityRecorder.roleCreated (
            causerId=causerId,
            roleId=role.id,
            attributes={
                "name": role.name,
                "guard_name": role.guard_name,
                "permission_ids": data.permission_ids,
            },
        )
        return await RoleAdminService._toDto (role)

    @staticmethod
    async def update (causerId: str, id: str, data: RoleUpdateValidatorDto) -> RoleTransformerDto:
        """
        Args:
            causerId (str)
            id (str)
            data (RoleUpdateValidatorDto)
        Returns:
            RoleTransformerDto
        """
        i18n = AppI18n.i18n ()
        role = await RoleAdminService.repository.findById (id)
        if not role:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.role.not_found"),
            )

        nextName: Optional[str] = None
        nextGuard: Optional[str] = None

        if data.name is not None:
            nextName = data.name.strip ()
            if nextName != role.name:
                SystemRoleGuard.assertMutableName (role.name)
                SystemRoleGuard.assertCreatableName (nextName)

        if data.guard_name is not None and data.guard_name != role.guard_name:
            SystemRoleGuard.assertMutableName (role.name)
            nextGuard = data.guard_name

        checkName = nextName if nextName is not None else role.name
        checkGuard = nextGuard if nextGuard is not None else role.guard_name
        if checkName != role.name or checkGuard != role.guard_name:
            existing = await RoleAdminService.repository.findByNameGuard (checkName, checkGuard)
            if existing and existing.id != role.id:
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=i18n.t ("_v1_acl.role.name_exists"),
                )

        if data.permission_ids is not None:
            await RoleAdminService._assertPermissionIds (data.permission_ids)

        role = await RoleAdminService.repository.update (
            role,
            name=nextName,
            guardName=nextGuard,
            permissionIds=data.permission_ids,
        )
        ActivityRecorder.roleUpdated (
            causerId=causerId,
            roleId=role.id,
            attributes={
                "name": role.name,
                "guard_name": role.guard_name,
                "permission_ids": data.permission_ids,
            },
        )
        return await RoleAdminService._toDto (role)

    @staticmethod
    async def delete (causerId: str, id: str) -> RoleTransformerDto:
        """
        Args:
            causerId (str)
            id (str)
        Returns:
            RoleTransformerDto
        """
        i18n = AppI18n.i18n ()
        role = await RoleAdminService.repository.findById (id)
        if not role:
            raise HTTPException (
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t ("_v1_acl.role.not_found"),
            )
        SystemRoleGuard.assertMutableName (role.name)
        dto = await RoleAdminService._toDto (role)
        if dto.users_count > 0:
            raise HTTPException (
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=i18n.t ("_v1_acl.role.in_use", args={"count": dto.users_count}),
            )
        await RoleAdminService.repository.delete (role)
        ActivityRecorder.roleDeleted (
            causerId=causerId,
            roleId=dto.id,
            attributes={"name": dto.name, "guard_name": dto.guard_name},
        )
        return dto

    @staticmethod
    async def importRoles (
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
            RoleAdminImportProcessor.run,
            userId,
            fileContent,
            filename,
        )
        return i18n.t ("_v1_acl.import.started.message")

    @staticmethod
    async def exportRoles (
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
            RoleAdminExportProcessor.run,
            userId,
            export_type,
            orders,
            filters,
        )
        return i18n.t ("_v1_acl.export.started.message")
