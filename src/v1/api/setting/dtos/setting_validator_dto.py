from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class SettingRowValidatorDto (BaseModel):
    """
    SettingRowValidatorDto (BaseModel)

    Attributes:
        id (Optional[str])
        key (Optional[str])
        value (Optional[str])
        value_kind (Literal["text", "file"])
    """
    model_config = ConfigDict (extra="forbid")

    id: Optional[str] = Field (default=None)
    key: Optional[str] = Field (default=None, max_length=255)
    value: Optional[str] = Field (default=None)
    value_kind: Literal["text", "file"] = Field (default="text")

class SettingBatchValidatorDto (BaseModel):
    """
    SettingBatchValidatorDto (BaseModel)

    Attributes:
        rows (List[SettingRowValidatorDto])
    """
    model_config = ConfigDict (extra="forbid")

    rows: List[SettingRowValidatorDto] = Field (default_factory=list)
