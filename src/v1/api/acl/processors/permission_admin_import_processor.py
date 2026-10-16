from typing import Any, Dict, Optional, get_args
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.processors.app_import_processor import AppImportProcessor
from src.v1.api.acl.dtos.permission_validator_dto import GuardName
from src.v1.api.acl.events.permission.admin.imported.event import PermissionAdminImportedEvent
from src.v1.api.acl.events.permission.admin.imported_failed.event import PermissionAdminImportedFailedEvent
from src.v1.api.acl.repositories.permission_admin_repository import PermissionAdminRepository
from src.v1.api.acl.support.system_permission_guard import SystemPermissionGuard

class PermissionAdminImportProcessor (AppImportProcessor):
    """
    PermissionAdminImportProcessor (AppImportProcessor)

    Attributes:
        repository (PermissionAdminRepository)
    """
    repository = PermissionAdminRepository ()

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
                    name = PermissionAdminImportProcessor._cell (row, "name")
                    guard = (PermissionAdminImportProcessor._cell (row, "guard_name") or "web").lower ()
                    if not name or guard not in get_args (GuardName):
                        skippedCount += 1
                        continue

                    existing = await PermissionAdminImportProcessor.repository.findByNameGuard (
                        name,
                        guard,
                    )
                    if existing:
                        skippedCount += 1
                        continue

                    if SystemPermissionGuard.isSystem (name):
                        skippedCount += 1
                        continue

                    await PermissionAdminImportProcessor.repository.create (name, guard)
                    importedCount += 1
                except Exception:
                    skippedCount += 1
                    continue

            await getEventEmitter ().emit (
                "v1.acl.permission.admin.imported",
                PermissionAdminImportedEvent (
                    userId=userId,
                    filename=filename,
                    totalImported=importedCount,
                    totalSkipped=skippedCount,
                ),
            )
        except Exception as e:
            await getEventEmitter ().emit (
                "v1.acl.permission.admin.imported-failed",
                PermissionAdminImportedFailedEvent (
                    userId=userId,
                    filename=filename,
                    error=str (e),
                ),
            )
