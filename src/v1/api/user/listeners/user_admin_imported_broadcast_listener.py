from src.app.bases.app_event import OnEvent
from src.app.routes.app_ws_router import getSocketIOServer
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
        socketioServer = getSocketIOServer ()
        await socketioServer.emit ("v1.user.admin.imported", {
            "userId": event.userId,
            "filename": event.filename,
            "totalImported": event.totalImported,
            "totalSkipped": event.totalSkipped
        })
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
        socketioServer = getSocketIOServer ()
        await socketioServer.emit ("v1.user.admin.imported-failed", {
            "userId": event.userId,
            "filename": event.filename,
            "error": event.error
        })
    except Exception:
        pass
