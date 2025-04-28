from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.app.bases.app_i18n import AppI18n

async def validationExceptionHandler (request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Args:
        request (Request)
        exc (RequestValidationError)
    Returns:
        JSONResponse
    """
    i18n = AppI18n.i18n ()
    errors = []
    for error in exc.errors ():
        errorDetail = {
            "type": error.get ("type", "value_error"),
            "loc": error.get ("loc", []),
            "msg": error.get ("msg", ""),
            "input": error.get ("input", {}),
            "ctx": {}
        }
        msg = errorDetail["msg"]
        ctx = error.get ("ctx", {})
        if isinstance (ctx, dict) and "error" in ctx:
            errorObj = ctx.get ("error")
            if isinstance (errorObj, ValueError):
                msg = str (errorObj)
            elif isinstance (errorObj, str):
                msg = errorObj
            if isinstance (errorObj, ValueError):
                errorMsg = str (errorObj)
                if errorMsg.startswith ("ValueError(") and errorMsg.endswith (")"):
                    errorMsg = errorMsg[11:-1]
                    if (errorMsg.startswith ("'") and errorMsg.endswith ("'")) or (errorMsg.startswith ('"') and errorMsg.endswith ('"')):
                        errorMsg = errorMsg[1:-1]
                errorDetail["ctx"] = {
                    "error": errorMsg
                }
            else:
                errorDetail["ctx"] = {
                    "error": str (errorObj) if errorObj else None
                }
        else:
            errorDetail["ctx"] = ctx if isinstance (ctx, dict) else {}
        if msg and msg.startswith ("_") and "." in msg:
            try:
                translatedMsg = i18n.t (msg)
                if translatedMsg != msg:
                    errorDetail["msg"] = translatedMsg
            except Exception:
                pass
        if isinstance (errorDetail.get ("ctx", {}), dict) and "error" in errorDetail["ctx"]:
            ctxError = errorDetail["ctx"]["error"]
            if ctxError and isinstance (ctxError, str) and ctxError.startswith ("_") and "." in ctxError:
                try:
                    translatedCtxError = i18n.t (ctxError)
                    if translatedCtxError != ctxError:
                        errorDetail["ctx"]["error"] = translatedCtxError
                except Exception:
                    pass
        errors.append (errorDetail)
    return JSONResponse (
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )
