"""Unit tests for database dialect utilities."""

from src.db.dialect import Dialect


def test_dialect_creation():
    """Test dialect initialization."""
    dialect = Dialect("postgresql")
    assert dialect.name == "postgresql"
    assert dialect.schema is None


def test_schema_property():
    """Test schema getter/setter."""
    dialect = Dialect("mysql")
    dialect.schema = "public"
    assert dialect.schema == "public"


def test_format_table_name():
    """Test table name formatting."""
    dialect = Dialect("sqlite")
    # Without schema
    assert dialect.format_table_name("users") == "users"
    # With schema
    dialect.schema = "app"
    assert dialect.format_table_name("users") == '"app"."users"'


def test_quote_identifier():
    """Test identifier quoting."""
    dialect = Dialect("postgresql")
    # Basic identifier
    assert dialect.quote_identifier("table_name") == '"table_name"'
    # Identifier with special characters
    assert dialect.quote_identifier("user-data") == '"user-data"'
    # Identifier with dots
    assert dialect.quote_identifier("complex.name") == '"complex.name"'


def test_get_type_name():
    """Test type name mapping."""
    dialect = Dialect("mysql")
    # Test standard types
    assert dialect.get_type_name(str) == "VARCHAR"
    assert dialect.get_type_name(int) == "INTEGER"
    assert dialect.get_type_name(float) == "FLOAT"
    assert dialect.get_type_name(bool) == "BOOLEAN"

    # Test fallback behavior
    assert dialect.get_type_name(dict) == "VARCHAR"  # Complex types default to VARCHAR
    assert dialect.get_type_name(None) == "VARCHAR"  # None defaults to VARCHAR


def test_dialect_specific_formatting():
    """Test dialect-specific table name formatting."""
    # PostgreSQL uses quotes for case-sensitivity
    pg_dialect = Dialect("postgresql")
    pg_dialect.schema = "App"
    assert pg_dialect.format_table_name("Users") == '"App"."Users"'

    # MySQL uses same quoting
    mysql_dialect = Dialect("mysql")
    mysql_dialect.schema = "app"
    assert mysql_dialect.format_table_name("users") == '"app"."users"'

    # SQLite uses same quoting
    sqlite_dialect = Dialect("sqlite")
    sqlite_dialect.schema = "main"
    assert sqlite_dialect.format_table_name("users") == '"main"."users"'
