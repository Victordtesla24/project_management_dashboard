"""Database update and delete operations."""

from typing import Any, Dict, List, Optional

from .dialect import Dialect


class Update:
    """SQL update statement builder."""

    def __init__(self, table_name: str, dialect: Optional[Dialect] = None) -> None:
        """Initialize update builder."""
        self.table_name = table_name
        self.dialect = dialect or Dialect("default")
        self.set_values: Dict[str, Any] = {}
        self.where_clauses: List[str] = []
        self.where_params: List[Any] = []

    def set(self, values: Dict[str, Any]) -> "Update":
        """Set values to update."""
        self.set_values.update(values)
        return self

    def where(self, condition: str, *params: Any) -> "Update":
        """Add where clause."""
        self.where_clauses.append(condition)
        self.where_params.extend(params)
        return self

    def build(self) -> str:
        """Build SQL update statement."""
        if not self.set_values:
            msg = "No values to update"
            raise ValueError(msg)

        table = self.dialect.format_table_name(self.table_name)
        if not self.dialect.schema:
            table = self.dialect.quote_identifier(table)

        # Build SET clause
        set_items = []
        for col in self.set_values:
            set_items.append(f"{self.dialect.quote_identifier(col)} = %s")

        sql = f"UPDATE {table} SET {', '.join(set_items)}"

        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameters for prepared statement."""
        params = list(self.set_values.values())
        params.extend(self.where_params)
        return params


class Delete:
    """SQL delete statement builder."""

    def __init__(self, table_name: str, dialect: Optional[Dialect] = None) -> None:
        """Initialize delete builder."""
        self.table_name = table_name
        self.dialect = dialect or Dialect("default")
        self.where_clauses: List[str] = []
        self.where_params: List[Any] = []

    def where(self, condition: str, *params: Any) -> "Delete":
        """Add where clause."""
        self.where_clauses.append(condition)
        self.where_params.extend(params)
        return self

    def build(self) -> str:
        """Build SQL delete statement."""
        table = self.dialect.format_table_name(self.table_name)
        if not self.dialect.schema:
            table = self.dialect.quote_identifier(table)

        sql = f"DELETE FROM {table}"

        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)

        return sql

    def get_parameters(self) -> List[Any]:
        """Get parameters for prepared statement."""
        return self.where_params
