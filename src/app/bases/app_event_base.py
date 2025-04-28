from typing import Dict
from pydantic import BaseModel, ConfigDict

class AppEventBase (BaseModel):
    """
    AppEventBase (BaseModel)

    Attributes:
        model_config (ConfigDict)
    """
    model_config = ConfigDict (arbitrary_types_allowed=True)
