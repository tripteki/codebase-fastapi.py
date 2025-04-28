import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from src.app.bases.app_i18n import AppI18n

logger = logging.getLogger (__name__)

async def generalExceptionHandler (request: Request, exc: Exception) -> JSONResponse:
    """
    Args:
        request (Request)
        exc (Exception)
    Returns:
        JSONResponse
    """
    i18n = AppI18n.i18n ()

    logger.error (
        f"Unhandled exception: {type (exc).__name__}: {str (exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )

    try:
        detail = i18n.t ("_app.error.internal_server_error")
    except Exception:
        detail = "Internal server error"
    
    return JSONResponse (
        status_code=500,
        content={"detail": detail}
    )
