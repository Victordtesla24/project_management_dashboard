"""\1"""
import json
from typing import Any, Optional


def parse_message(message: str) -> Optional[dict[str, Any]]:
    """\1"""
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return None

def format_message(data: dict[str, Any]) -> str:
    """\1"""
    return json.dumps(data)
