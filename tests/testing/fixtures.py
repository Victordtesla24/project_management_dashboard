"""Test fixtures for database operations."""
from typing import Any, Optional

from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ClauseElement


class AlterColRoundTripFixture:
    """Base class for testing column alterations."""

    def __init__(self, dialect_name: str = "default") -> None:
        self.dialect_name = dialect_name
        self.metadata = MetaData()
        self._connection: Optional[Connection] = None

    def _get_connection(self) -> Connection:
        """Get a database connection."""
        if not self._connection:
            engine = create_engine("sqlite://")
            self._connection = engine.connect()
        return self._connection

    def _create_fixture_table(self, *cols: Column) -> Table:
        """Create a test table with the given columns."""
        return Table("test_table", self.metadata, *cols, sqlite_on_conflict="IGNORE")

    def _compile(self, clause: ClauseElement, **kw: Any) -> str:
        """Compile a SQL clause to a string."""
        if self.dialect_name != "default":
            kw["dialect"] = self._get_dialect()
        return str(clause.compile(**kw))

    def _get_dialect(self) -> Any:
        """Get the database dialect."""
        from sqlalchemy.dialects import registry

        return registry.load(self.dialect_name)()

    def setUp(self) -> None:
        """Set up the test fixture."""
        self.metadata = MetaData()

    def tearDown(self) -> None:
        """Clean up the test fixture."""
        if self._connection:
            self._connection.close()
            self._connection = None
