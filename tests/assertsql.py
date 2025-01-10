"""SQL assertion utilities for tests."""
from typing import Any, Dict, Optional, Tuple


class CursorSQL:
    """Mock cursor for testing SQL compilation."""

    def __init__(
        self,
        statement: str,
        params: Optional[Dict[str, Any]] = None,
        positiontup: Optional[Tuple[Any, ...]] = None,
    ) -> None:
        self.statement = statement
        self.params = params or {}
        self.positiontup = positiontup or ()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CursorSQL):
            return NotImplemented
        return (
            self.statement == other.statement
            and self.params == other.params
            and self.positiontup == other.positiontup
        )

    def __str__(self) -> str:
        return f"CursorSQL({self.statement!r}, {self.params!r}, {self.positiontup!r})"
