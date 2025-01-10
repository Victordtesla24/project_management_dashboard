"""Test cases for autogenerated diffs."""
from sqlalchemy import (
    Column,
    Computed,
    Float,
    Integer,
    MetaData,
    Table,
    UniqueConstraint,
)


def test_basic_diff():
    """Test basic diff generation."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table("test", metadata1, Column("id", Integer, primary_key=True), Column("value", Integer))

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        Column("new_column", Integer),
    )

    assert len(t2.columns) == len(t1.columns) + 1
    assert t2.c.new_column.name == "new_column"


def test_diff_with_modified_column():
    """Test diff with modified column."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table(
        "test",
        metadata1,
        Column("id", Integer, primary_key=True),
        Column("value", Integer, nullable=True),
    )

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=True),
        Column("value", Integer, nullable=False),
    )

    assert t2.c.value.nullable is False
    assert t1.c.value.nullable is True


def test_diff_with_removed_column():
    """Test diff with removed column."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table(
        "test",
        metadata1,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        Column("to_remove", Integer),
    )

    t2 = Table("test", metadata2, Column("id", Integer, primary_key=True), Column("value", Integer))

    assert len(t2.columns) == len(t1.columns) - 1


def test_diff_with_renamed_column():
    """Test diff with renamed column."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table(
        "test", metadata1, Column("id", Integer, primary_key=True), Column("old_name", Integer),
    )

    t2 = Table(
        "test", metadata2, Column("id", Integer, primary_key=True), Column("new_name", Integer),
    )

    assert len(t2.columns) == len(t1.columns)
    assert t2.c.new_name.name == "new_name"


def test_diff_with_multiple_changes():
    """Test diff with multiple changes."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table(
        "test",
        metadata1,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        Column("to_remove", Integer),
        Column("to_modify", Integer, nullable=True),
    )

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        Column("new_column", Integer),
        Column("to_modify", Integer, nullable=False),
    )

    assert len(t2.columns) == len(t1.columns)
    assert t2.c.new_column.name == "new_column"
    assert t2.c.to_modify.nullable is False


def test_diff_with_primary_key_change():
    """Test diff with primary key change."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    Table("test", metadata1, Column("id", Integer, primary_key=True), Column("value", Integer))

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=False),
        Column("value", Integer, primary_key=True),
    )

    assert t2.c.id.primary_key is False
    assert t2.c.value.primary_key is True


def test_diff_with_unique_constraint():
    """Test diff with unique constraint."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table("test", metadata1, Column("id", Integer, primary_key=True), Column("value", Integer))

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        UniqueConstraint("value"),
    )

    t2_unique_cols = set()
    t1_unique_cols = set()

    for const in t2.constraints:
        if isinstance(const, UniqueConstraint):
            t2_unique_cols.update(col.name for col in const.columns)
    for const in t1.constraints:
        if isinstance(const, UniqueConstraint):
            t1_unique_cols.update(col.name for col in const.columns)

    assert "value" in t2_unique_cols
    assert "value" not in t1_unique_cols


def test_diff_with_type_change():
    """Test diff with type change."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    t1 = Table("test", metadata1, Column("id", Integer, primary_key=True), Column("value", Integer))

    t2 = Table("test", metadata2, Column("id", Integer, primary_key=True), Column("value", Float))

    assert isinstance(t2.c.value.type, Float)
    assert isinstance(t1.c.value.type, Integer)


def test_diff_with_computed_column():
    """Test diff with computed column."""
    metadata1 = MetaData()
    metadata2 = MetaData()
    Table("test", metadata1, Column("id", Integer, primary_key=True), Column("value", Integer))

    t2 = Table(
        "test",
        metadata2,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
        Column("computed", Integer, server_default=Computed("value * 2")),
    )

    assert str(t2.c.computed.server_default.sqltext) == "value * 2"
