from typing import Dict
import asyncio
from rq.job import Job
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_event_listener import AppEventListener
from src.app.bases.app_i18n import AppI18n
from src.app.bases.app_queue import Processor, Process
from src.app.constants.queue_constants import USER_ADMIN_QUEUE
from src.app.processors.app_import_processor import AppImportProcessor
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

@Processor (USER_ADMIN_QUEUE)
class UserAdminImportProcessor (AppImportProcessor):
    """
    UserAdminImportProcessor (AppImportProcessor)
    """
    @staticmethod
    @Process ("import")
    def handle (data: Dict[str, object]) -> None:
        """
        Args:
            data (Dict[str, object])
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        try:
            AppEventListener.loadListeners (None)
            userId = data.get ("userId")
            filename = data.get ("file")
            fileContent = data.get ("fileContent")

            if not fileContent or not filename:
                raise ValueError (i18n.t ("_app.processor.import.missing_file"))

            parsed_data = AppImportProcessor.import_file (fileContent, filename)

            required_columns = ["name", "email", "password"]
            AppImportProcessor.validate_columns (parsed_data, required_columns)

            valid_rows = AppImportProcessor.filter_valid_rows (parsed_data, required_columns)

            importedCount = 0
            skippedCount = 0

            for row in valid_rows:
                try:
                    email = row.get ("email")

                    existingUser = asyncio.run (UserAuthRepository.findOneByEmail (email))
                    if existingUser:
                        skippedCount += 1
                        continue

                    hashedPassword = AppAuth.hashPassword (row.get ("password"))
                    user = User (
                        name=row.get ("name"),
                        email=email,
                        password=hashedPassword
                    )
                    asyncio.run (UserAuthRepository.create (user))
                    importedCount += 1

                except Exception as e:
                    skippedCount += 1
                    continue

            eventEmitter = getEventEmitter ()
            event = UserAdminImportedEvent (
                userId=userId,
                filename=filename,
                totalImported=importedCount,
                totalSkipped=skippedCount
            )
            asyncio.run (eventEmitter.emit ("v1.user.admin.imported", event))

        except Exception as e:
            eventEmitter = getEventEmitter ()
            event = UserAdminImportedFailedEvent (
                userId=userId if 'userId' in locals () else None,
                filename=filename if 'filename' in locals () else None,
                error=str (e)
            )
            asyncio.run (eventEmitter.emit ("v1.user.admin.imported-failed", event))
            raise
