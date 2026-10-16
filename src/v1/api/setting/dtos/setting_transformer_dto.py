from datetime import datetime
from typing import Optional
from typing_extensions import Self
from pydantic import BaseModel, Field
from src.app.configs.app_config import AppConfig
from src.v1.api.setting.databases.models.setting_model import Setting

class SettingTransformerDto (BaseModel):
    """
    SettingTransformerDto (BaseModel)

    Attributes:
        id (str)
        key (str)
        value (Optional[str])
        value_kind (str)
        value_url (Optional[str])
        created_at (datetime)
        updated_at (datetime)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    key: str = Field (..., json_schema_extra={"example": "APP_NAME"})
    value: Optional[str] = Field (None, json_schema_extra={"example": "Codebase"})
    value_kind: str = Field (..., json_schema_extra={"example": "text"})
    value_url: Optional[str] = Field (None, json_schema_extra={"example": None})
    created_at: datetime = Field (..., json_schema_extra={"example": "string"})
    updated_at: datetime = Field (..., json_schema_extra={"example": "string"})

    @staticmethod
    def fromSetting (setting: Setting) -> Self:
        """
        Args:
            setting (Setting)
        Returns:
            SettingTransformerDto
        """
        valueUrl = None
        if setting.value_kind == "file" and setting.value:
            appUrl = AppConfig.config ().frontend_url or ""
            valueUrl = f"{appUrl.rstrip ('/')}/storage/{setting.value.lstrip ('/')}"

        return SettingTransformerDto (
            id=setting.id,
            key=setting.key,
            value=setting.value,
            value_kind=setting.value_kind if setting.value_kind in ("text", "file") else "text",
            value_url=valueUrl,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
        )
