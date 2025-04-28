from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

class AppEventBase (BaseModel):
    """
    AppEventBase
    """
    model_config = ConfigDict (arbitrary_types_allowed=True)
