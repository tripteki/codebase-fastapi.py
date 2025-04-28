from urllib.parse import unquote
from fastapi import Request, HTTPException, status
from src.app.configs.app_config import AppConfig
from src.app.dtos.app_dto import Message
import re

async def urlGuard (request: Request) -> None:
    """
    Args:
        request (Request)
    Returns:
        None
    """
    try:
        appConfig = AppConfig.config ()
        
        frontendUrl: str = appConfig.frontend_url
        originalUrl: str = request.url.path
        cleanedUrl: str = re.sub (r"^/api/v1|^/v1", "", originalUrl)

        queryString = str (request.url.query)
        fullUrl = f"{frontendUrl}{cleanedUrl}"
        if queryString:
            fullUrl = f"{fullUrl}?{queryString}"

    except Exception:
        raise HTTPException (
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Message.UNSIGNED
        )
