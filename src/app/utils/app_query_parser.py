from typing import Optional, List, Dict

def parseOrders (orders: Optional[str]) -> Optional[List[Dict[str, str]]]:
    """
    Args:
        orders (Optional[str])
    Returns:
        Optional[List[Dict[str, str]]]
    """
    if not orders:
        return None

    parsedOrders: List[Dict[str, str]] = []
    for order in orders.split (","):
        parts = order.split (":")
        if len (parts) == 2:
            parsedOrders.append ({"field": parts[0].strip (), "direction": parts[1].strip ()})

    return parsedOrders if parsedOrders else None

def parseFilters (filters: Optional[str]) -> Optional[List[Dict[str, str]]]:
    """
    Args:
        filters (Optional[str])
    Returns:
        Optional[List[Dict[str, str]]]
    """
    if not filters:
        return None

    parsedFilters: List[Dict[str, str]] = []
    for filter_item in filters.split (","):
        parts = filter_item.split (":")
        if len (parts) == 2:
            parsedFilters.append ({"field": parts[0].strip (), "search": parts[1].strip ()})

    return parsedFilters if parsedFilters else None
