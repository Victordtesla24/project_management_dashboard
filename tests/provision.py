"""Database provisioning utilities for tests."""

from contextlib import contextmanager


def set_default_schema_on_connection(connection, schema_name):
    """Set the default schema for a database connection."""
    if not schema_name:
        return

    # Execute schema setting based on database type
    if hasattr(connection, "execute"):
        if "postgresql" in str(connection.engine.url).lower():
            connection.execute(f"SET search_path TO {schema_name}")
        elif "mysql" in str(connection.engine.url).lower():
            connection.execute(f"USE {schema_name}")
        elif "sqlite" in str(connection.engine.url).lower():
            connection.execute("PRAGMA database_list")  # No schema concept in SQLite


@contextmanager
def temp_table_connection(engine, table_name, schema=None):
    """Create a temporary connection with a specific table and schema."""
    connection = engine.connect()
    transaction = connection.begin()

    try:
        if schema:
            set_default_schema_on_connection(connection, schema)
        yield connection
    finally:
        transaction.rollback()
        connection.close()


def setup_test_schema(connection, schema_name):
    """Set up a test schema in the database."""
    if "postgresql" in str(connection.engine.url).lower():
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    elif "mysql" in str(connection.engine.url).lower():
        connection.execute(f"CREATE DATABASE IF NOT EXISTS {schema_name}")
    # SQLite doesn't support schemas


def teardown_test_schema(connection, schema_name):
    """Clean up a test schema from the database."""
    if "postgresql" in str(connection.engine.url).lower():
        connection.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
    elif "mysql" in str(connection.engine.url).lower():
        connection.execute(f"DROP DATABASE IF EXISTS {schema_name}")
    # SQLite doesn't support schemas


def get_temp_table_name():
    """Generate a unique temporary table name."""
    import uuid

    return f"temp_table_{str(uuid.uuid4()).replace('-', '_')}"


def normalize_sequence(sequence_name):
    """Normalize a sequence name for cross-database compatibility."""
    return sequence_name.lower().replace("-", "_")


def temp_table_keyword_args(connection):
    """Get database-specific temporary table arguments."""
    if "postgresql" in str(connection.engine.url).lower():
        return {"prefixes": ["TEMPORARY"]}
    elif "mysql" in str(connection.engine.url).lower():
        return {"prefixes": ["TEMPORARY"]}
    else:
        return {}  # SQLite creates temp tables by default in transactions
