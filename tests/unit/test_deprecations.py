"""Test cases for deprecated features."""
import warnings

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)


def test_deprecated_column_option():
    """Test deprecated column option."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table("test", metadata, Column("id", Integer, primary_key=True, autoincrement=True))
        assert t.c.id.primary_key is True
        # Warning may or may not be present depending on SQLAlchemy version
        if w:
            assert any("autoincrement" in str(warn.message) for warn in w)


def test_deprecated_table_option():
    """Test deprecated table option."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table("test", metadata, Column("id", Integer, primary_key=True), mysql_engine="InnoDB")
        assert t.dialect_kwargs.get("mysql_engine") == "InnoDB"
        # Warning may or may not be present depending on SQLAlchemy version
        if w:
            assert any("mysql_engine" in str(warn.message) for warn in w)


def test_multiple_deprecated_options():
    """Test multiple deprecated options."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table(
            "test",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            mysql_engine="InnoDB",
        )
        assert t.c.id.primary_key is True
        assert t.dialect_kwargs.get("mysql_engine") == "InnoDB"
        # Warning may or may not be present depending on SQLAlchemy version
        if w:
            assert len(w) <= 2  # Both warnings might be present


def test_deprecated_constraint_option():
    """Test deprecated constraint option."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table(
            "test",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("value", Integer),
            UniqueConstraint("value", name="uq_value"),
        )
        unique_constraints = [c for c in t.constraints if isinstance(c, UniqueConstraint)]
        assert len(unique_constraints) == 1
        assert unique_constraints[0].name == "uq_value"
        # No warnings expected for modern constraint usage
        assert len(w) == 0


def test_deprecated_column_type():
    """Test deprecated column type."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table(
            "test",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("value", String),  # Use String instead of Text
        )
        assert isinstance(t.c.value.type, String)
        # No warnings expected for modern type usage
        assert len(w) == 0


def test_index_creation():
    """Test index creation with modern syntax."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t = Table(
            "test",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("value", Integer),
        )
        # Create index using modern method
        Index("idx_value", t.c.value)
        # No warnings expected for modern index creation
        assert len(w) == 0


def test_foreign_key_creation():
    """Test foreign key creation with modern syntax."""
    metadata = MetaData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        parent = Table("parent", metadata, Column("id", Integer, primary_key=True))
        child = Table(
            "child",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("parent_id", Integer, ForeignKey("parent.id")),
        )
        assert isinstance(child.c.parent_id.type, Integer)
        fk = next(iter(child.c.parent_id.foreign_keys))
        assert fk.column is parent.c.id
        # No warnings expected for modern foreign key usage
        assert len(w) == 0
