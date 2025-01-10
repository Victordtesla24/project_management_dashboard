"""Common test utilities."""

from typing import Any, Dict, Optional, Union

from sqlalchemy import MetaData, Table, text

from ..assertions import eq_
from ..engines import create_test_engine
from ..schema import Column, create_table

class TestBase:
    """Base class for tests."""

    def setup_method(self) -> None:
        """Set up test method."""
        self.engine = create_test_engine()
        self.metadata = MetaData()
        self.tables: Dict[str, Table] = {}

    def teardown_method(self) -> None:
        """Tear down test method."""
        for table in reversed(self.metadata.sorted_tables):
            table.drop(self.engine, checkfirst=True)

    def create_table(self, name: str, *columns: Column) -> Table:
        """Create a test table."""
        table = create_table(name, *columns, metadata=self.metadata)
        self.tables[name] = table
        return table

    def get_table(self, name: str) -> Optional[Table]:
        """Get a test table by name."""
        return self.tables.get(name)

    def assert_table_exists(self, name: str) -> None:
        """Assert that a table exists."""
        assert name in self.tables, f"Table {name} does not exist"
        assert self.tables[name].exists(self.engine), f"Table {name} does not exist in database"

    def assert_table_not_exists(self, name: str) -> None:
        """Assert that a table does not exist."""
        if name in self.tables:
            assert not self.tables[name].exists(self.engine), f"Table {name} exists in database"

    def execute(self, sql: Union[str, text]) -> Any:
        """Execute SQL statement."""
        with self.engine.connect() as conn:
            return conn.execute(text(sql) if isinstance(sql, str) else sql)

    def assert_sql(self, expected: str, actual: str) -> None:
        """Assert that two SQL statements are equal."""
        eq_(expected.strip(), actual.strip()) 