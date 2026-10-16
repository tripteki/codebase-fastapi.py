from typing import Dict, List, Optional
from sqlmodel import Session, col, select
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_event import getEventEmitter
from src.app.helpers.datetime_helper import appNow, formatAppDatetime
from src.app.processors.app_export_processor import AppExportProcessor
from src.app.repositories.app_repository import Filterization, Orderization
from src.v1.api.user.databases.models.acl_model import ModelHasRole, Role
from src.v1.api.user.databases.models.profile_model import Profile
from src.v1.api.user.events.user.admin.exported.event import UserAdminExportedEvent
from src.v1.api.user.events.user.admin.exported_failed.event import UserAdminExportedFailedEvent
from src.v1.api.user.repositories.user_acl_repository import GUARD_NAME, USER_MODEL_TYPE
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository

class UserAdminExportProcessor (AppExportProcessor):
    """
    UserAdminExportProcessor (AppExportProcessor)
    """

    @staticmethod
    async def run (
        userId: str,
        export_type: str,
        orders: Optional[List[Orderization]] = None,
        filters: Optional[List[Filterization]] = None,
    ) -> None:
        """
        Args:
            userId (str)
            export_type (str)
            orders (Optional[List[Orderization]])
            filters (Optional[List[Filterization]])
        Returns:
            None
        """
        try:
            validTypes = ["csv", "xls", "xlsx"]
            normalizedType = export_type.lower () if export_type.lower () in validTypes else "csv"

            engine = AppDatabase.databasePostgresql ()
            session = Session (engine)

            try:
                users = await UserAdminRepository ().allFiltered (orders, filters)
                if not users:
                    raise Exception ("No users found to export")

                userIds = [user.id for user in users]
                profiles: Dict[str, Profile] = {
                    profile.user_id: profile
                    for profile in session.exec (
                        select (Profile).where (col (Profile.user_id).in_ (userIds))
                    ).all ()
                }
                roleByUser: Dict[str, str] = {}
                roleRows = session.exec (
                    select (ModelHasRole.model_id, Role.name)
                    .join (Role, Role.id == ModelHasRole.role_id)
                    .where (
                        ModelHasRole.model_type == USER_MODEL_TYPE,
                        ModelHasRole.model_id.in_ (userIds),
                        Role.guard_name == GUARD_NAME,
                    )
                ).all ()
                for modelId, roleName in roleRows:
                    roleByUser[str (modelId)] = str (roleName)

                exportData = []
                for user in users:
                    profile = profiles.get (user.id)
                    if user.deleted_at is not None:
                        status = "deactivated"
                    elif user.email_verified_at is None:
                        status = "unverified"
                    else:
                        status = "active"
                    exportData.append ({
                        "full_name": profile.full_name if profile and profile.full_name else user.name,
                        "email": user.email,
                        "role": roleByUser.get (user.id),
                        "status": status,
                        "created_at": formatAppDatetime (user.created_at),
                    })

                sanitizedData = AppExportProcessor.sanitize_data (exportData)
                filename = f"users_export_{appNow ().strftime ('%Y%m%d_%H%M%S')}.{normalizedType}"
                result = AppExportProcessor.export_file (
                    data=sanitizedData,
                    filename=filename,
                    file_type=normalizedType,
                    subfolder="export",
                    sheet_name="Users"
                )
                eventEmitter = getEventEmitter ()
                event = UserAdminExportedEvent (
                    userId=userId,
                    filename=filename,
                    fileUrl=result["fileUrl"],
                    filePath=result["filePath"]
                )
                await eventEmitter.emit ("v1.user.admin.exported", event)
            finally:
                session.close ()
        except Exception as e:
            eventEmitter = getEventEmitter ()
            event = UserAdminExportedFailedEvent (
                userId=userId,
                error=str (e)
            )
            await eventEmitter.emit ("v1.user.admin.exported-failed", event)
