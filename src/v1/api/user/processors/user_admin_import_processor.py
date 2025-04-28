from typing import Dict
import asyncio
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.processors.app_import_processor import AppImportProcessor
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository

class UserAdminImportProcessor (AppImportProcessor):
    """
    UserAdminImportProcessor (AppImportProcessor)
    """

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

            parsed_data = AppImportProcessor.import_file (fileContent, filename)

            required_columns = ["name", "email", "password"]
            AppImportProcessor.validate_columns (parsed_data, required_columns)

            valid_rows = AppImportProcessor.filter_valid_rows (parsed_data, required_columns)

            importedCount = 0
            skippedCount = 0

            for row in valid_rows:
                try:
                    email = row.get ("email")

                    existingUser = await UserAuthRepository.findOneByEmail (email)
                    if existingUser:
                        skippedCount += 1
                        continue

                    hashedPassword = AppAuth.hashPassword (row.get ("password"))
                    user = User (
                        name=row.get ("name"),
                        email=email,
                        password=hashedPassword
                    )
                    await UserAuthRepository.create (user)
                    importedCount += 1

                except Exception:
                    skippedCount += 1
                    continue

            eventEmitter = getEventEmitter ()
            event = UserAdminImportedEvent (
                userId=userId,
                filename=filename,
                totalImported=importedCount,
                totalSkipped=skippedCount
            )
            await eventEmitter.emit ("v1.user.admin.imported", event)

        except Exception as e:
            eventEmitter = getEventEmitter ()
            event = UserAdminImportedFailedEvent (
                userId=userId,
                filename=filename,
                error=str (e)
            )
            await eventEmitter.emit ("v1.user.admin.imported-failed", event)
