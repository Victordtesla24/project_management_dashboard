"""Unit tests for database insert operations."""

import pytest

from src.db.dialect import Dialect
from src.db.insert import Insert


def test_insert_init():
    """Test insert builder initialization."""
    insert = Insert("users")
    assert insert.table_name == "users"
    assert isinstance(insert.dialect, Dialect)
    assert insert.values == []
    assert insert.columns == []


def test_insert_add_values():
    """Test adding values to insert."""
    insert = Insert("users")
    values = {"name": "John", "age": 30}
    insert.add_values(values)

    assert insert.columns == ["name", "age"]
    assert insert.values == [values]


def test_insert_build_single():
    """Test building single row insert statement."""
    insert = Insert("users")
    insert.add_values({"name": "John", "age": 30})

    sql = insert.build()
    params = insert.get_parameters()

    assert sql == 'INSERT INTO "users" ("name", "age") VALUES (%s, %s)'
    assert params == ["John", 30]


def test_insert_build_multiple():
    """Test building multi-row insert statement."""
    insert = Insert("users")
    insert.add_values({"name": "John", "age": 30})
    insert.add_values({"name": "Jane", "age": 25})

    sql = insert.build()
    params = insert.get_parameters()

    assert sql == 'INSERT INTO "users" ("name", "age") VALUES (%s, %s), (%s, %s)'
    assert params == ["John", 30, "Jane", 25]


def test_insert_empty():
    """Test error on empty insert."""
    insert = Insert("users")
    with pytest.raises(ValueError):
        insert.build()


def test_insert_custom_dialect():
    """Test insert with custom dialect."""
    dialect = Dialect("postgresql")
    insert = Insert("users", dialect)
    insert.add_values({"name": "John"})

    assert insert.dialect == dialect
    sql = insert.build()
    assert sql == 'INSERT INTO "users" ("name") VALUES (%s)'
