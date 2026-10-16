from typing import Any, List, Optional
from src.app.bases.app_event import getEventEmitter
from src.app.helpers.datetime_helper import appNow
from src.app.processors.app_export_processor import AppExportProcessor
from src.v1.api.acl.events.role.admin.exported.event import RoleAdminExportedEvent
from src.v1.api.acl.events.role.admin.exported_failed.event import RoleAdminExportedFailedEvent
from src.v1.api.acl.repositories.role_admin_repository import RoleAdminRepository

class RoleAdminExportProcessor (AppExportProcessor):
    """
    RoleAdminExportProcessor (AppExportProcessor)

    Attributes:
        repository (RoleAdminRepository)
    """
    repository = RoleAdminRepository ()

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

            roles = await RoleAdminExportProcessor.repository.allFiltered (orders, filters)
            if not roles:
                raise Exception ("No roles found to export")

            exportData = []
            for role in roles:
                permissions = await RoleAdminExportProcessor.repository.getPermissions (role.id)
                exportData.append ({
                    "name": role.name,
                    "guard_name": role.guard_name,
                    "permissions": ",".join (item.name for item in permissions),
                })

            filename = f"roles_export_{appNow ().strftime ('%Y%m%d_%H%M%S')}.{normalizedType}"
            result = AppExportProcessor.export_file (
                data=AppExportProcessor.sanitize_data (exportData),
                filename=filename,
                file_type=normalizedType,
                subfolder="export",
                sheet_name="Roles",
            )

            await getEventEmitter ().emit (
                "v1.acl.role.admin.exported",
                RoleAdminExportedEvent (
                    userId=userId,
                    filename=filename,
                    fileUrl=result["fileUrl"],
                    filePath=result["filePath"],
                ),
            )
        except Exception as e:
            await getEventEmitter ().emit (
                "v1.acl.role.admin.exported-failed",
                RoleAdminExportedFailedEvent (
                    userId=userId,
                    error=str (e),
                ),
            )
