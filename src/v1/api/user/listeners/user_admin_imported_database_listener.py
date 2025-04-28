from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent

@OnEvent ("v1.user.admin.imported")
async def handleUserAdminImported (event: UserAdminImportedEvent) -> None:
    """
    Args:
        event (UserAdminImportedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="user.import.completed",
                data={
                    "filename": event.filename,
                    "totalImported": event.totalImported,
                    "totalSkipped": event.totalSkipped,
                    "message": i18n.t ("_v1_user.import.completed.message", args={"totalImported": event.totalImported, "totalSkipped": event.totalSkipped})
                }
            )
        )
    except Exception:
        pass

@OnEvent ("v1.user.admin.imported-failed")
async def handleUserAdminImportedFailed (event: UserAdminImportedFailedEvent) -> None:
    """
    Args:
        event (UserAdminImportedFailedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="user.import.failed",
                data={
                    "filename": event.filename,
                    "message": i18n.t ("_v1_user.import.failed.message"),
                    "error": event.error
                }
            )
        )
    except Exception:
        pass
