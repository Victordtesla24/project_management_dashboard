"""Autogenerated test fixtures."""

from typing import Dict, Optional

import pytest
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.orm import sessionmaker

from tests.mock import MockEngine, mock_engine


class AutogenFixtureTest:
    """Base class for autogen fixture tests."""

    def setup_method(self) -> None:
        """Set up test method."""
        self.engine = mock_engine()
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def teardown_method(self) -> None:
        """Tear down test method."""
        self.session.close()
        self.metadata.clear()

    def create_table(self, name: str, *columns: Column, schema: Optional[str] = None) -> Table:
        """Create a table for testing."""
        table = Table(name, self.metadata, *columns, schema=schema)
        self.tables[name] = table
        return table

    def create_tables(self) -> None:
        """Create all tables in metadata."""
        self.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """Drop all tables in metadata."""
        self.metadata.drop_all(self.engine)


@pytest.fixture()
def autogen_test() -> AutogenFixtureTest:
    """Fixture for autogen tests."""
    return AutogenFixtureTest()


@pytest.fixture()
def mock_db_engine() -> MockEngine:
    """Fixture for mock database engine."""
    return mock_engine()
