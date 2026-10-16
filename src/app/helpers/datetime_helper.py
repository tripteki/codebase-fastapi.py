from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo
from src.app.configs.app_config import AppConfig

DATETIME_TOKENS = (
    ("YYYY", "%Y"),
    ("MM", "%m"),
    ("DD", "%d"),
    ("HH", "%H"),
    ("mm", "%M"),
    ("ss", "%S"),
)

def appTimezone () -> ZoneInfo:
    """
    Returns:
        ZoneInfo
    """
    return ZoneInfo (AppConfig.config ().timezone)

def appNow () -> datetime:
    """
    Returns:
        datetime
    """
    return datetime.now (appTimezone ())

def formatAppDatetime (value: Optional[datetime], pattern: Optional[str] = None) -> Optional[str]:
    """
    Naive values are stored as UTC.

    Args:
        value (Optional[datetime])
        pattern (Optional[str])
    Returns:
        Optional[str]
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace (tzinfo=timezone.utc)
    strftimePattern = pattern or AppConfig.config ().datetime_format
    for token, directive in DATETIME_TOKENS:
        strftimePattern = strftimePattern.replace (token, directive)
    return value.astimezone (appTimezone ()).strftime (strftimePattern)
