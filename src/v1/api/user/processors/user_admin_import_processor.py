from typing import Dict
import asyncio
import logging
from datetime import datetime
from src.app.bases.app_auth import AppAuth
from src.app.bases.app_event import getEventEmitter
from src.app.bases.app_i18n import AppI18n
from src.app.processors.app_import_processor import AppImportProcessor
from src.v1.api.user.databases.models.user_model import User
from src.v1.api.user.dtos.user_role_enum import UserRoleEnum
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent
from src.v1.api.log.support.activity_recorder import ActivityRecorder
from src.v1.api.user.repositories.user_acl_repository import UserAclRepository
from src.v1.api.user.repositories.user_admin_repository import UserAdminRepository
from src.v1.api.user.repositories.user_auth_repository import UserAuthRepository
from src.v1.api.user.services.user_auth_service import UserAuthService
from src.v1.api.user.support.account_notifier import AccountNotifier

logger = logging.getLogger (__name__)

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

            AppImportProcessor.validate_columns (parsed_data, ["email", "password"])
            firstRow = parsed_data[0] if parsed_data else {}
            if "name" not in firstRow and "full_name" not in firstRow:
                raise ValueError (i18n.t ("_app.processor.import.missing_columns", args={"columns": "name"}))

            valid_rows = AppImportProcessor.filter_valid_rows (parsed_data, ["email", "password"])

            importedCount = 0
            skippedCount = len (parsed_data) - len (valid_rows)

            for row in valid_rows:
                try:
                    email = row.get ("email")

                    if await UserAuthRepository.emailTaken (email):
                        skippedCount += 1
                        continue

                    displayName = str (row.get ("name") or row.get ("full_name") or "").strip ()
                    fullName = str (row.get ("full_name") or displayName).strip ()
                    if not displayName:
                        skippedCount += 1
                        continue
                    hashedPassword = AppAuth.hashPassword (row.get ("password"))
                    statusValue = str (row.get ("status") or "unverified").strip ().lower ()
                    if statusValue not in ("active", "unverified", "deactivated"):
                        skippedCount += 1
                        continue
                    now = datetime.utcnow ()
                    user = User (
                        name=displayName,
                        email=email,
                        password=hashedPassword,
                        email_verified_at=None if statusValue == "unverified" else now,
                        deleted_at=now if statusValue == "deactivated" else None,
                    )
                    await UserAuthRepository.create (user)
                    await UserAdminRepository ().upsertProfile (user.id, fullName)
                    try:
                        UserAclRepository.assignSingleRole (user.id, UserRoleEnum.User.value)
                    except LookupError:
                        await UserAclRepository.syncUserRole (user.id, UserRoleEnum.User.value)
                    ActivityRecorder.userCreated (
                        causerId=userId,
                        userId=user.id,
                        attributes={"full_name": fullName, "email": user.email, "role": UserRoleEnum.User.value},
                    )
                    try:
                        if statusValue == "active":
                            await AccountNotifier.accountCreated (user, UserRoleEnum.User.value)
                        elif statusValue == "unverified":
                            await UserAuthService.sendVerificationEmail (user)
                    except Exception:
                        logger.warning ("import verification email skipped email=%s", user.email, exc_info=True)
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
