from typing import Any, Dict, Optional, get_args
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.processors.app_import_processor import AppImportProcessor
from src.v1.api.acl.dtos.role_validator_dto import GuardName
from src.v1.api.acl.events.role.admin.imported.event import RoleAdminImportedEvent
from src.v1.api.acl.events.role.admin.imported_failed.event import RoleAdminImportedFailedEvent
from src.v1.api.acl.repositories.permission_admin_repository import PermissionAdminRepository
from src.v1.api.acl.repositories.role_admin_repository import RoleAdminRepository
from src.v1.api.acl.support.system_role_guard import SystemRoleGuard

class RoleAdminImportProcessor (AppImportProcessor):
    """
    RoleAdminImportProcessor (AppImportProcessor)

    Attributes:
        roleRepository (RoleAdminRepository)
        permissionRepository (PermissionAdminRepository)
    """
    roleRepository = RoleAdminRepository ()
    permissionRepository = PermissionAdminRepository ()

    @staticmethod
    def _cell (row: Dict[str, Any], key: str) -> Optional[str]:
        """
        Args:
            row (Dict[str, Any])
            key (str)
        Returns:
            Optional[str]
        """
        value = row.get (key)
        if value is None:
            return None
        text = str (value).strip ()
        if not text or text.lower () == "nan":
            return None
        return text

    @staticmethod
    async def run (userId: str, fileContent: bytes, filename: str) -> None:
        """
        Args:
            userId (str)
            fileContent (bytes)
            filename (str)
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        try:
            if not fileContent or not filename:
                raise ValueError (i18n.t ("_app.processor.import.missing_file"))

            parsed = AppImportProcessor.import_file (fileContent, filename)
            AppImportProcessor.validate_columns (parsed, ["name", "guard_name"])

            importedCount = 0
            skippedCount = 0

            for row in parsed:
                try:
                    name = RoleAdminImportProcessor._cell (row, "name")
                    guard = (RoleAdminImportProcessor._cell (row, "guard_name") or "web").lower ()
                    if not name or guard not in get_args (GuardName):
                        skippedCount += 1
                        continue

                    if SystemRoleGuard.isSystem (name):
                        skippedCount += 1
                        continue

                    permissionsRaw = RoleAdminImportProcessor._cell (row, "permissions") or ""
                    permissionNames = [
                        item.strip ()
                        for item in permissionsRaw.split (",")
                        if item.strip ()
                    ]
                    permissions = await RoleAdminImportProcessor.permissionRepository.findByNamesGuard (
                        permissionNames,
                        guard,
                    )
                    permissionIds = [item.id for item in permissions]

                    existing = await RoleAdminImportProcessor.roleRepository.findByNameGuard (
                        name,
                        guard,
                    )
                    if existing:
                        await RoleAdminImportProcessor.roleRepository.update (
                            existing,
                            permissionIds=permissionIds,
                        )
                        importedCount += 1
                        continue

                    await RoleAdminImportProcessor.roleRepository.create (
                        name,
                        guard,
                        permissionIds,
                    )
                    importedCount += 1
                except Exception:
                    skippedCount += 1
                    continue

            await getEventEmitter ().emit (
                "v1.acl.role.admin.imported",
                RoleAdminImportedEvent (
                    userId=userId,
                    filename=filename,
                    totalImported=importedCount,
                    totalSkipped=skippedCount,
                ),
            )
        except Exception as e:
            await getEventEmitter ().emit (
                "v1.acl.role.admin.imported-failed",
                RoleAdminImportedFailedEvent (
                    userId=userId,
                    filename=filename,
                    error=str (e),
                ),
            )
