"""Mock utilities for testing."""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock


class MockEngine:
    """Mock database engine."""

    def __init__(self) -> None:
        """Initialize mock engine."""
        self.url = "mock://test"
        self.dialect = MagicMock()
        self.dialect.name = "mock"
        self.dialect.paramstyle = "qmark"

    def connect(self) -> "MockConnection":
        """Create mock connection."""
        return MockConnection()

    def execute(self, *args: Any, **kwargs: Any) -> "MockResult":
        """Execute mock query."""
        return MockResult()


class MockConnection:
    """Mock database connection."""

    def __init__(self) -> None:
        """Initialize mock connection."""
        self.closed = False
        self.committed = False
        self.rolled_back = False

    def close(self) -> None:
        """Close mock connection."""
        self.closed = True

    def commit(self) -> None:
        """Commit mock transaction."""
        self.committed = True

    def rollback(self) -> None:
        """Rollback mock transaction."""
        self.rolled_back = True

    def execute(self, *args: Any, **kwargs: Any) -> "MockResult":
        """Execute mock query."""
        return MockResult()


class MockResult:
    """Mock query result."""

    def __init__(self, rows: Optional[List[Dict[str, Any]]] = None) -> None:
        """Initialize mock result."""
        self.rows = rows or []
        self.closed = False
        self.returned_rows = False

    def close(self) -> None:
        """Close mock result."""
        self.closed = True

    def fetchall(self) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        self.returned_rows = True
        return self.rows

    def fetchone(self) -> Optional[Dict[str, Any]]:
        """Fetch one row."""
        self.returned_rows = True
        return self.rows[0] if self.rows else None


def mock_engine() -> MockEngine:
    """Create mock engine."""
    return MockEngine()


def mock_connection() -> MockConnection:
    """Create mock connection."""
    return MockConnection()


def mock_result(rows: Optional[List[Dict[str, Any]]] = None) -> MockResult:
    """Create mock result."""
    return MockResult(rows)
