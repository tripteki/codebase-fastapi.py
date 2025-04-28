from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from src.app.bases.app_i18n import AppI18n

async def httpExceptionHandler (request: Request, exc: HTTPException) -> JSONResponse:
    """
    Args:
        request (Request)
        exc (HTTPException)
    Returns:
        JSONResponse
    """
    i18n = AppI18n.i18n ()

    detail = exc.detail
    if isinstance (detail, str) and detail.startswith ("_") and "." in detail:
        try:
            translated_detail = i18n.t (detail)
            if translated_detail != detail:
                detail = translated_detail
        except Exception:
            pass
    
    return JSONResponse (
        status_code=exc.status_code,
        content={"detail": detail}
    )
