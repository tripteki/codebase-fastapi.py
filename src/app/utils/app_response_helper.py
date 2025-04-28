from typing import Dict, Optional
from src.app.dtos.app_dto import Description

def getPaginationResponses (
    item_example: Optional[Dict[str, object]] = None,
    unauthorized: bool = False,
    forbidden: bool = False,
    not_found: bool = False
) -> Dict[int, Dict[str, object]]:
    """
    Args:
        item_example (Optional[Dict[str, object]])
        unauthorized (bool)
        forbidden (bool)
        not_found (bool)
    Returns:
        Dict[int, Dict[str, object]]
    """
    responses: Dict[int, Dict[str, object]] = {}

    pagination_example = {
        "totalPage": 0,
        "perPage": 0,
        "currentPage": 0,
        "nextPage": 0,
        "previousPage": 0,
        "firstPage": 0,
        "lastPage": 0,
        "data": [item_example] if item_example else []
    }

    responses[200] = {
        "description": Description.OK,
        "content": {
            "application/json": {
                "example": pagination_example
            }
        }
    }

    if unauthorized:
        responses[401] = {
            "description": Description.UNAUTHORIZED,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }
    if forbidden:
        responses[403] = {
            "description": Description.FORBIDDEN,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }
    if not_found:
        responses[404] = {
            "description": Description.NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }

    return responses

def getStandardResponses (
    success: bool = False,
    success_desc: str = Description.OK,
    success_example: object = None,
    unauthorized: bool = False,
    forbidden: bool = False,
    bad_request: bool = False,
    unvalidated: bool = False,
    not_found: bool = False,
    unauthorized_desc: str = Description.UNAUTHORIZED,
    forbidden_desc: str = Description.FORBIDDEN,
    bad_request_desc: str = Description.BAD_REQUEST,
    unvalidated_desc: str = Description.UNVALIDATED,
    not_found_desc: str = Description.NOT_FOUND
) -> Dict[int, Dict[str, object]]:
    """
    Args:
        success (bool)
        success_desc (str)
        success_example (object)
        unauthorized (bool)
        forbidden (bool)
        bad_request (bool)
        unvalidated (bool)
        not_found (bool)
        unauthorized_desc (str)
        forbidden_desc (str)
        bad_request_desc (str)
        unvalidated_desc (str)
        not_found_desc (str)
    Returns:
        Dict[int, Dict[str, object]]
    """
    responses: Dict[int, Dict[str, object]] = {}

    if success:
        responses[200] = {
            "description": success_desc,
            "content": {
                "application/json": {
                    "example": success_example if success_example is not None else {}
                }
            }
        }

    if unauthorized:
        responses[401] = {
            "description": unauthorized_desc,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }
    if forbidden:
        responses[403] = {
            "description": forbidden_desc,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }
    if bad_request:
        responses[400] = {
            "description": bad_request_desc,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }
    if unvalidated:
        responses[422] = {
            "description": unvalidated_desc,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body"],
                                "msg": "string",
                                "input": {},
                                "ctx": {"error": "string"}
                            }
                        ]
                    }
                }
            }
        }
    if not_found:
        responses[404] = {
            "description": not_found_desc,
            "content": {
                "application/json": {
                    "example": {"detail": "string"}
                }
            }
        }

    return responses
