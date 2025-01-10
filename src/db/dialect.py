"""Database dialect utilities."""


class Dialect:
    """Base dialect class."""

    def __init__(self, name) -> None:
        """Initialize dialect with name."""
        self.name = name
        self._schema = None

    @property
    def schema(self):
        """Get current schema."""
        return self._schema

    @schema.setter
    def schema(self, value):
        """Set current schema."""
        self._schema = value

    def format_table_name(self, table_name):
        """Format table name with schema if present."""
        if self._schema:
            return f"{self.quote_identifier(self._schema)}.{self.quote_identifier(table_name)}"
        return table_name

    def quote_identifier(self, identifier):
        """Quote an identifier (table name, column name, etc)."""
        return f'"{identifier}"'

    def get_type_name(self, type_):
        """Get database type name for given Python type."""
        type_map = {str: "VARCHAR", int: "INTEGER", float: "FLOAT", bool: "BOOLEAN"}
        return type_map.get(type_, "VARCHAR")
