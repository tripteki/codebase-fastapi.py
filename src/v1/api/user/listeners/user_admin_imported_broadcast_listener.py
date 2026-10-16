import logging
from src.app.bases.app_event import OnEvent
from src.app.bases.app_realtime import emitToUser
from src.v1.api.log.support.admin_refresh_broadcaster import AdminRefreshBroadcaster
from src.v1.api.user.events.user.admin.imported.event import UserAdminImportedEvent
from src.v1.api.user.events.user.admin.imported_failed.event import UserAdminImportedFailedEvent

logger = logging.getLogger (__name__)

@OnEvent ("v1.user.admin.imported")
async def handleUserAdminImported (event: UserAdminImportedEvent) -> None:
    """
    Args:
        event (UserAdminImportedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.user.admin.imported", {
            "userId": event.userId,
            "filename": event.filename,
            "totalImported": event.totalImported,
            "totalSkipped": event.totalSkipped
        })
        if event.totalImported > 0:
            await AdminRefreshBroadcaster.broadcast (["users"], event.userId)
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)

@OnEvent ("v1.user.admin.imported-failed")
async def handleUserAdminImportedFailed (event: UserAdminImportedFailedEvent) -> None:
    """
    Args:
        event (UserAdminImportedFailedEvent)
    Returns:
        None
    """
    try:
        await emitToUser (event.userId, "v1.user.admin.imported-failed", {
            "userId": event.userId,
            "filename": event.filename,
            "error": event.error
        })
    except Exception:
        logger.warning ("event listener failed module=%s", __name__, exc_info=True)
