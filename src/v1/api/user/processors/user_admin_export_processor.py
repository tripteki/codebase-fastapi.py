from datetime import datetime
from typing import Dict
from sqlmodel import Session, select
from src.app.bases.app_database import AppDatabase
from src.app.bases.app_event import getEventEmitter
from src.app.processors.app_export_processor import AppExportProcessor
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.events.user.admin.exported.event import UserAdminExportedEvent
from src.v1.api.user.events.user.admin.exported_failed.event import UserAdminExportedFailedEvent

class UserAdminExportProcessor (AppExportProcessor):
    """
    UserAdminExportProcessor (AppExportProcessor)
    """

    @staticmethod
    async def run (userId: str, export_type: str) -> None:
        """
        Args:
            userId (str)
            export_type (str)
        Returns:
            None
        """
        try:
            validTypes = ["csv", "xls", "xlsx"]
            normalizedType = export_type.lower () if export_type.lower () in validTypes else "csv"

            engine = AppDatabase.databasePostgresql ()
            session = Session (engine)

            try:
                statement = select (User).where (User.deleted_at == None)
                users = session.exec (statement).all ()

                if not users:
                    raise Exception ("No users found to export")

                export_data = []
                for user in users:
                    export_data.append ({
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "email_verified_at": user.email_verified_at.isoformat () if user.email_verified_at else None,
                        "created_at": user.created_at.isoformat () if user.created_at else None,
                        "updated_at": user.updated_at.isoformat () if user.updated_at else None
                    })

                sanitized_data = AppExportProcessor.sanitize_data (export_data)

                filename = f"users_export_{datetime.now ().strftime ('%Y%m%d_%H%M%S')}.{normalizedType}"

                result = AppExportProcessor.export_file (
                    data=sanitized_data,
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
