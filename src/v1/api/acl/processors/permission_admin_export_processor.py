from typing import Any, List, Optional
from src.app.bases.app_event import getEventEmitter
from src.app.helpers.datetime_helper import appNow
from src.app.processors.app_export_processor import AppExportProcessor
from src.v1.api.acl.events.permission.admin.exported.event import PermissionAdminExportedEvent
from src.v1.api.acl.events.permission.admin.exported_failed.event import PermissionAdminExportedFailedEvent
from src.v1.api.acl.repositories.permission_admin_repository import PermissionAdminRepository

class PermissionAdminExportProcessor (AppExportProcessor):
    """
    PermissionAdminExportProcessor (AppExportProcessor)

    Attributes:
        repository (PermissionAdminRepository)
    """
    repository = PermissionAdminRepository ()

    @staticmethod
    async def run (
        userId: str,
        export_type: str,
        orders: Optional[List[Any]] = None,
        filters: Optional[List[Any]] = None,
    ) -> None:
        """
        Args:
            userId (str)
            export_type (str)
            orders (Optional[List[Any]])
            filters (Optional[List[Any]])
        Returns:
            None
        """
        try:
            validTypes = ["csv", "xlsx"]
            normalizedType = export_type.lower () if export_type.lower () in validTypes else "csv"

            permissions = await PermissionAdminExportProcessor.repository.allFiltered (orders, filters)
            if not permissions:
                raise Exception ("No permissions found to export")

            exportData = [
                {
                    "name": item.name,
                    "guard_name": item.guard_name,
                }
                for item in permissions
            ]

            filename = f"permissions_export_{appNow ().strftime ('%Y%m%d_%H%M%S')}.{normalizedType}"
            result = AppExportProcessor.export_file (
                data=AppExportProcessor.sanitize_data (exportData),
                filename=filename,
                file_type=normalizedType,
                subfolder="export",
                sheet_name="Permissions",
            )

            await getEventEmitter ().emit (
                "v1.acl.permission.admin.exported",
                PermissionAdminExportedEvent (
                    userId=userId,
                    filename=filename,
                    fileUrl=result["fileUrl"],
                    filePath=result["filePath"],
                ),
            )
        except Exception as e:
            await getEventEmitter ().emit (
                "v1.acl.permission.admin.exported-failed",
                PermissionAdminExportedFailedEvent (
                    userId=userId,
                    error=str (e),
                ),
            )
