import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.user.events.user.admin.exported.event import UserAdminExportedEvent
from src.v1.api.user.events.user.admin.exported_failed.event import UserAdminExportedFailedEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.admin.exported")
async def handleUserAdminExported (event: UserAdminExportedEvent) -> None:
    """
    Args:
        event (UserAdminExportedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.user.admin.exported", {
            "userId": event.userId,
            "filename": event.filename,
            "fileUrl": event.fileUrl
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)

@OnEvent ("v1.user.admin.exported-failed")
async def handleUserAdminExportedFailed (event: UserAdminExportedFailedEvent) -> None:
    """
    Args:
        event (UserAdminExportedFailedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.user.admin.exported-failed", {
            "userId": event.userId,
            "error": event.error
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
