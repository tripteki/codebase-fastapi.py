from typing import List, Optional
from pydantic import BaseModel, Field

class SearchItemTransformerDto (BaseModel):
    """
    SearchItemTransformerDto (BaseModel)

    Attributes:
        id (str)
        title (str)
        subtitle (Optional[str])
        url (str)
    """
    id: str = Field (..., json_schema_extra={"example": "string"})
    title: str = Field (..., json_schema_extra={"example": "Admin Name"})
    subtitle: Optional[str] = Field (None, json_schema_extra={"example": "admin@mail.com"})
    url: str = Field (..., json_schema_extra={"example": "/admin/users/string"})

class SearchGroupTransformerDto (BaseModel):
    """
    SearchGroupTransformerDto (BaseModel)

    Attributes:
        category (str)
        items (List[SearchItemTransformerDto])
    """
    category: str = Field (..., json_schema_extra={"example": "users"})
    items: List[SearchItemTransformerDto] = Field (default_factory=list)

class SearchTransformerDto (BaseModel):
    """
    SearchTransformerDto (BaseModel)

    Attributes:
        results (List[SearchGroupTransformerDto])
    """
    results: List[SearchGroupTransformerDto] = Field (default_factory=list)
