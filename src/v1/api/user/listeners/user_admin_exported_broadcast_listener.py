from src.app.bases.app_event import OnEvent
from src.app.routes.app_ws_router import getSocketIOServer
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
        socketioServer = getSocketIOServer ()
        await socketioServer.emit ("v1.user.admin.exported", {
            "userId": event.userId,
            "filename": event.filename,
            "fileUrl": event.fileUrl
        })
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
        socketioServer = getSocketIOServer ()
        await socketioServer.emit ("v1.user.admin.exported-failed", {
            "userId": event.userId,
            "error": event.error
        })
    except Exception:
        pass
