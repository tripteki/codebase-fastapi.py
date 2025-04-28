from src.app.bases.app_context import AppContext
from src.app.bases.app_event import OnEvent
from src.v1.api.user.events.user.admin.activated.event import UserAdminActivatedEvent

@OnEvent ("user.admin.activated")
async def handleUserAdminActivatedBroadcast (event: UserAdminActivatedEvent) -> None:
    """
    Broadcast user activated event via WebSocket
    Args:
        event (UserAdminActivatedEvent)
    Returns:
        None
    """
    try:
        app = AppContext.getApp ()
        if hasattr (app.state, "ws") and app.state.ws:
            await app.state.ws.emit ("user.admin.activated", {
                "id": event.id,
                "name": event.name,
                "email": event.email,
                "email_verified_at": str (event.email_verified_at) if event.email_verified_at else None,
                "created_at": str (event.created_at) if event.created_at else None,
                "updated_at": str (event.updated_at) if event.updated_at else None,
                "deleted_at": str (event.deleted_at) if event.deleted_at else None
            })
    except Exception:
        pass
