"""Database migration utilities."""
from typing import Any, Dict, Optional, Union

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Connection, Engine


class MigrationContext:
    """Context for managing database migrations."""

    def __init__(
        self,
        connection: Optional[Union[Connection, Engine]] = None,
        opts: Optional[Dict[str, Any]] = None,
        environment_context: Optional[Any] = None,
    ) -> None:
        self.connection = connection
        self.opts = opts or {}
        self.environment_context = environment_context
        self._migrations: Dict[str, Any] = {}

    @property
    def metadata(self) -> MetaData:
        """Get the metadata for this migration context."""
        return MetaData()

    def get_current_revision(self) -> Optional[str]:
        """Get the current revision of the database."""
        return None

    def run_migrations(self) -> None:
        """Run pending migrations."""

    def execute(self, sql: str, execution_options: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SQL statement."""
        if not self.connection:
            self.connection = create_engine("sqlite://").connect()
        return self.connection.execute(sql)

    def begin_transaction(self) -> Any:
        """Begin a new transaction."""
        if not self.connection:
            self.connection = create_engine("sqlite://").connect()
        return self.connection.begin()
