"""Test cases for DDL (Data Definition Language) operations."""
from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)


def test_basic_table_creation():
    """Test basic table creation."""
    metadata = MetaData()
    t = Table("test", metadata, Column("id", Integer, primary_key=True), Column("value", Integer))

    assert len(t.columns) == 2
    assert t.c.id.primary_key is True
    assert t.c.value.primary_key is False


def test_table_with_check_constraint():
    """Test table with check constraint."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        CheckConstraint("value > 0"),
    )

    assert len(t.columns) == 2
    check_constraints = [c for c in t.constraints if isinstance(c, CheckConstraint)]
    assert len(check_constraints) == 1
    assert str(check_constraints[0].sqltext) == "value > 0"


def test_table_with_multiple_constraints():
    """Test table with multiple constraints."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        CheckConstraint("value > 0"),
        CheckConstraint("value < 100"),
    )

    assert len(t.columns) == 2
    check_constraints = [c for c in t.constraints if isinstance(c, CheckConstraint)]
    assert len(check_constraints) == 2
    constraint_texts = sorted(str(c.sqltext) for c in check_constraints)
    assert constraint_texts == ["value < 100", "value > 0"]


def test_table_with_column_constraints():
    """Test table with column constraints."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer, nullable=False, unique=True),
    )

    assert t.c.value.nullable is False
    assert t.c.value.unique is True


def test_table_with_mixed_constraints():
    """Test table with mixed constraints."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer, nullable=False),
        UniqueConstraint("value"),
        CheckConstraint("value > 0"),
    )

    assert t.c.value.nullable is False
    unique_constraints = [c for c in t.constraints if isinstance(c, UniqueConstraint)]
    assert len(unique_constraints) == 1
    assert next(iter(unique_constraints[0].columns)).name == "value"

    check_constraints = [c for c in t.constraints if isinstance(c, CheckConstraint)]
    assert len(check_constraints) == 1
    assert str(check_constraints[0].sqltext) == "value > 0"


def test_table_without_primary_key():
    """Test table without primary key."""
    metadata = MetaData()
    t = Table("test", metadata, Column("value", Integer))

    assert len(t.columns) == 1
    assert t.c.value.primary_key is False


def test_table_with_multiple_primary_keys():
    """Test table with multiple primary keys."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id1", Integer, primary_key=True),
        Column("id2", Integer, primary_key=True),
    )

    assert t.c.id1.primary_key is True
    assert t.c.id2.primary_key is True


def test_table_with_all_column_types():
    """Test table with different column types."""
    metadata = MetaData()
    t = Table(
        "test",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(50), nullable=False),
        Column("description", String, nullable=True),
        Column("count", Integer, server_default=text("0")),
        UniqueConstraint("name"),
    )

    assert t.c.name.nullable is False
    assert t.c.description.nullable is True
    assert t.c.count.server_default.arg.text == "0"

    unique_constraints = [c for c in t.constraints if isinstance(c, UniqueConstraint)]
    assert len(unique_constraints) == 1
    assert next(iter(unique_constraints[0].columns)).name == "name"
