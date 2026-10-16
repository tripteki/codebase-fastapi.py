from fastapi import Request, HTTPException, status
from src.app.dtos.app_dto import Message

async def urlGuard (request: Request) -> None:
    """
    Args:
        request (Request)
    Returns:
        None
    """
    signed = (request.query_params.get ("signed") or "").strip ()
    if not signed:
        raise HTTPException (
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Message.UNSIGNED,
        )
