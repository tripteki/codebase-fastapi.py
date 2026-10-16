from pathlib import Path
from typing import Optional, Sequence, Union
from fastapi import HTTPException, UploadFile, status
from src.app.bases.app_i18n import AppI18n

IMAGE_MAX_SIZE_BYTES = 2 * 1024 * 1024
IMPORT_MAX_SIZE_BYTES = 5 * 1024 * 1024
IMPORT_ALLOWED_EXTENSIONS = {".csv", ".txt", ".xls", ".xlsx"}

def _uploadError (field: Union[str, Sequence[Union[str, int]]], key: str, args: Optional[dict] = None, value: Optional[str] = None) -> HTTPException:
    """
    Args:
        field (Union[str, Sequence[Union[str, int]]])
        key (str)
        args (Optional[dict])
        value (Optional[str])
    Returns:
        HTTPException
    """
    return HTTPException (
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[{
            "type": "value_error",
            "loc": ["body", field] if isinstance (field, str) else ["body", *field],
            "msg": AppI18n.i18n ().t (f"_app.upload.{key}", args=args or {}),
            "input": value,
            "ctx": {},
        }],
    )

async def _readLimited (file: UploadFile, maxBytes: int, field: Union[str, Sequence[Union[str, int]]]) -> bytes:
    """
    Args:
        file (UploadFile)
        maxBytes (int)
        field (Union[str, Sequence[Union[str, int]]])
    Returns:
        bytes
    """
    content = await file.read (maxBytes + 1)
    if len (content) > maxBytes:
        raise _uploadError (field, "too_large", {"size": maxBytes // (1024 * 1024)}, file.filename)
    return content

def detectImageExtension (content: bytes) -> Optional[str]:
    """
    Args:
        content (bytes)
    Returns:
        Optional[str]
    """
    if content.startswith (b"\xff\xd8\xff"):
        return ".jpg"
    if content.startswith (b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"
    if content.startswith (b"\x00\x00\x01\x00"):
        return ".ico"
    return None

async def readImageUpload (file: UploadFile, field: Union[str, Sequence[Union[str, int]]], allowIcon: bool = False) -> tuple[bytes, str]:
    """
    Args:
        file (UploadFile)
        field (Union[str, Sequence[Union[str, int]]])
        allowIcon (bool)
    Returns:
        tuple[bytes, str]
    """
    content = await _readLimited (file, IMAGE_MAX_SIZE_BYTES, field)
    extension = detectImageExtension (content)
    if extension is None or (extension == ".ico" and not allowIcon):
        raise _uploadError (field, "icon_type" if allowIcon else "image_type", value=file.filename)
    return content, extension

async def readImportUpload (file: UploadFile, field: str = "file") -> bytes:
    """
    Args:
        file (UploadFile)
        field (str)
    Returns:
        bytes
    """
    extension = Path (file.filename or "").suffix.lower ()
    if extension not in IMPORT_ALLOWED_EXTENSIONS:
        raise _uploadError (field, "import_type", value=file.filename)
    return await _readLimited (file, IMPORT_MAX_SIZE_BYTES, field)
