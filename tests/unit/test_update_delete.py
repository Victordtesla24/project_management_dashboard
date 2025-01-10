"""Unit tests for database update and delete operations."""

import pytest

from src.db.dialect import Dialect
from src.db.update_delete import Delete, Update


def test_update_init():
    """Test update builder initialization."""
    update = Update("users")
    assert update.table_name == "users"
    assert isinstance(update.dialect, Dialect)
    assert update.set_values == {}
    assert update.where_clauses == []
    assert update.where_params == []


def test_update_set():
    """Test setting update values."""
    update = Update("users")
    update.set({"name": "John", "age": 30})
    sql = update.build()
    params = update.get_parameters()

    assert sql == 'UPDATE "users" SET "name" = %s, "age" = %s'
    assert params == ["John", 30]


def test_update_where():
    """Test update with where clause."""
    update = Update("users")
    update.set({"name": "John"})
    update.where("id = %s", 1)
    sql = update.build()
    params = update.get_parameters()

    assert sql == 'UPDATE "users" SET "name" = %s WHERE id = %s'
    assert params == ["John", 1]


def test_update_multiple_where():
    """Test update with multiple where clauses."""
    update = Update("users")
    update.set({"status": "active"})
    update.where("age > %s", 18).where("city = %s", "London")
    sql = update.build()
    params = update.get_parameters()

    assert sql == 'UPDATE "users" SET "status" = %s WHERE age > %s AND city = %s'
    assert params == ["active", 18, "London"]


def test_update_empty():
    """Test error on empty update."""
    update = Update("users")
    with pytest.raises(ValueError):
        update.build()


def test_update_custom_dialect():
    """Test update with custom dialect."""
    dialect = Dialect("postgresql")
    dialect.schema = "public"
    update = Update("users", dialect)
    update.set({"name": "John"})
    sql = update.build()

    assert sql == 'UPDATE "public"."users" SET "name" = %s'


def test_delete_init():
    """Test delete builder initialization."""
    delete = Delete("users")
    assert delete.table_name == "users"
    assert isinstance(delete.dialect, Dialect)
    assert delete.where_clauses == []
    assert delete.where_params == []


def test_delete_all():
    """Test delete all records."""
    delete = Delete("users")
    sql = delete.build()
    params = delete.get_parameters()

    assert sql == 'DELETE FROM "users"'
    assert params == []


def test_delete_where():
    """Test delete with where clause."""
    delete = Delete("users")
    delete.where("id = %s", 1)
    sql = delete.build()
    params = delete.get_parameters()

    assert sql == 'DELETE FROM "users" WHERE id = %s'
    assert params == [1]


def test_delete_multiple_where():
    """Test delete with multiple where clauses."""
    delete = Delete("users")
    delete.where("age < %s", 18).where("status = %s", "inactive")
    sql = delete.build()
    params = delete.get_parameters()

    assert sql == 'DELETE FROM "users" WHERE age < %s AND status = %s'
    assert params == [18, "inactive"]


def test_delete_custom_dialect():
    """Test delete with custom dialect."""
    dialect = Dialect("postgresql")
    dialect.schema = "public"
    delete = Delete("users", dialect)
    sql = delete.build()

    assert sql == 'DELETE FROM "public"."users"'
