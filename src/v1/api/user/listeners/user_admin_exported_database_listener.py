from src.app.bases.app_event import OnEvent
from src.app.bases.app_i18n import AppI18n
from src.v1.api.notification.dtos.notification_validator_dto import NotificationCreateValidatorDto
from src.v1.api.notification.services.notification_user_service import NotificationUserService
from src.v1.api.user.events.user.admin.exported.event import UserAdminExportedEvent
from src.v1.api.user.events.user.admin.exported_failed.event import UserAdminExportedFailedEvent

@OnEvent ("v1.user.admin.exported")
async def handleUserAdminExported (event: UserAdminExportedEvent) -> None:
    """
    Args:
        event (UserAdminExportedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="user.export.completed",
                data={
                    "filename": event.filename,
                    "fileUrl": event.fileUrl,
                    "message": i18n.t ("_v1_user.export.completed.message")
                }
            )
        )
    except Exception:
        pass

@OnEvent ("v1.user.admin.exported-failed")
async def handleUserAdminExportedFailed (event: UserAdminExportedFailedEvent) -> None:
    """
    Args:
        event (UserAdminExportedFailedEvent)
    Returns:
        None
    """
    try:
        i18n = AppI18n.i18n ()
        await NotificationUserService.notify (
            event.userId,
            NotificationCreateValidatorDto (
                user_id=event.userId,
                type="user.export.failed",
                data={
                    "message": i18n.t ("_v1_user.export.failed.message"),
                    "error": event.error
                }
            )
        )
    except Exception:
        pass
