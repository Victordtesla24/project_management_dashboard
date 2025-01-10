"""Database insert operations."""

from typing import Any, Dict, List, Optional

from .dialect import Dialect


class Insert:
    """SQL insert statement builder."""

    def __init__(self, table_name: str, dialect: Optional[Dialect] = None) -> None:
        """Initialize insert builder."""
        self.table_name = table_name
        self.dialect = dialect or Dialect("default")
        self.values: List[Dict[str, Any]] = []
        self.columns: List[str] = []

    def add_values(self, values: Dict[str, Any]) -> "Insert":
        """Add values to insert."""
        if not self.columns:
            self.columns = list(values.keys())
        self.values.append(values)
        return self

    def build(self) -> str:
        """Build SQL insert statement."""
        if not self.values:
            msg = "No values to insert"
            raise ValueError(msg)

        table = self.dialect.quote_identifier(self.table_name)
        columns = ", ".join(self.dialect.quote_identifier(col) for col in self.columns)

        # Build values part
        value_placeholders = []
        for _ in self.values:
            placeholders = ", ".join("%s" for _ in self.columns)
            value_placeholders.append(f"({placeholders})")
        values_sql = ", ".join(value_placeholders)

        return f"INSERT INTO {table} ({columns}) VALUES {values_sql}"

    def get_parameters(self) -> List[Any]:
        """Get parameters for prepared statement."""
        params = []
        for value_dict in self.values:
            for col in self.columns:
                params.append(value_dict.get(col))
        return params
