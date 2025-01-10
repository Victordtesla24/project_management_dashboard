"""Test utilities."""

import os
import tempfile
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .config import TEST_DB_URL
from .mock import MockConnection, MockEngine, MockResult


def create_test_engine() -> Engine:
    """Create a test database engine."""
    return create_engine(TEST_DB_URL)


def create_test_session() -> Session:
    """Create a test database session."""
    engine = create_test_engine()
    return Session(engine)


def create_test_table(
    name: str,
    *columns: Column,
    schema: Optional[str] = None,
    metadata: Optional[MetaData] = None,
) -> Table:
    """Create a test table."""
    if metadata is None:
        metadata = MetaData()
    return Table(name, metadata, *columns, schema=schema)


def create_test_data(rows: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Create test data."""
    return rows or []


def create_temp_dir() -> str:
    """Create temporary directory for tests."""
    return tempfile.mkdtemp()


def create_temp_file(content: str = "") -> str:
    """Create temporary file with content."""
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


@contextmanager
def temp_dir() -> Generator[str, None, None]:
    """Context manager for temporary directory."""
    path = create_temp_dir()
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.rmdir(path)


@contextmanager
def temp_file(content: str = "") -> Generator[str, None, None]:
    """Context manager for temporary file."""
    path = create_temp_file(content)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)


def create_mock_engine() -> MockEngine:
    """Create mock database engine."""
    return MockEngine()


def create_mock_connection() -> MockConnection:
    """Create mock database connection."""
    return MockConnection()


def create_mock_result(rows: Optional[List[Dict[str, Any]]] = None) -> MockResult:
    """Create mock query result."""
    return MockResult(rows)
