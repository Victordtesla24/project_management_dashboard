"""WebSocket utilities package."""

import json
from typing import Any, Dict, Optional


def parse_message(message: str) -> Optional[dict[str, Any]]:
    """Parse incoming WebSocket message."""
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return None


def format_message(data: dict[str, Any]) -> str:
    """Format outgoing WebSocket message."""
    return json.dumps(data)
