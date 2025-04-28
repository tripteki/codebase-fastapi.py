def userRoom (userId: str) -> str:
    """
    Args:
        userId (str)
    Returns:
        str
    """
    return f"user:{userId}"

async def emitToUser (userId: str, event: str, payload: dict) -> None:
    """
    Args:
        userId (str)
        event (str)
        payload (dict)
    Returns:
        None
    """
    if not userId:
        return

    from src.app.routes.app_ws_router import getSocketIOServer

    socketioServer = getSocketIOServer ()
    await socketioServer.emit (event, payload, room=userRoom (userId))
