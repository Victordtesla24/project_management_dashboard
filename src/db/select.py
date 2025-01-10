"""Database select operations."""

from typing import Any, List, Optional

from .dialect import Dialect


class Select:
    """SQL select statement builder."""

    def __init__(self, table_name: str, dialect: Optional[Dialect] = None) -> None:
        """Initialize select builder."""
        self.table_name = table_name
        self.dialect = dialect or Dialect("default")
        self.columns: List[str] = []
        self.where_clauses: List[str] = []
        self.where_params: List[Any] = []
        self.order_by: Optional[str] = None
        self.limit_value: Optional[int] = None

    def columns_list(self, *cols: str) -> "Select":
        """Set columns to select."""
        self.columns = list(cols)
        return self

    def where(self, condition: str, *params: Any) -> "Select":
        """Add where clause."""
        self.where_clauses.append(condition)
        self.where_params.extend(params)
        return self

    def order(self, column: str, desc: bool = False) -> "Select":
        """Add order by clause."""
        self.order_by = f"{column} {'DESC' if desc else 'ASC'}"
        return self

    def limit(self, count: int) -> "Select":
        """Add limit clause."""
        self.limit_value = count
        return self

    def build(self) -> str:
        """Build SQL select statement."""
        # Get formatted table name (with schema if present)
        table = self.dialect.format_table_name(self.table_name)
        if not self.dialect.schema:
            table = self.dialect.quote_identifier(table)

        # Format columns
        cols = (
            "*"
            if not self.columns
            else ", ".join(self.dialect.quote_identifier(col) for col in self.columns)
        )

        sql = f"SELECT {cols} FROM {table}"

        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)

        if self.order_by:
            sql += f" ORDER BY {self.order_by}"

        if self.limit_value is not None:
            sql += f" LIMIT {self.limit_value}"

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameters for prepared statement."""
        return self.where_params
