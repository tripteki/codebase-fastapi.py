from typing import Any, Optional, Dict
from pathlib import Path
import toml

def packageHelper (metadata: str) -> Optional[str]:
    """
    Args:
        metadata (str)
    Returns:
        Optional[str]
    """
    try:
        with open (Path (__file__).
                   resolve ().
                   parents[3] / "pyproject.toml", "r", encoding="utf-8") as f:
            project: Dict[str, Any] = toml.load (f)
            return project["tool"]["poetry"].get (metadata)
    except Exception:
        return None
