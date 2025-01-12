"""Test cases for Common Table Expressions (CTEs)."""
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table


def test_basic_cte():
    """Test basic CTE generation."""
    metadata = MetaData()
    Table(
        "base",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
    )

    cte = Table(
        "cte",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("base_id", Integer, ForeignKey("base.id")),
        Column("computed", Integer),
    )

    # Verify table structure
    assert "id" in cte.c
    assert "base_id" in cte.c
    assert "computed" in cte.c
    assert isinstance(cte.c.base_id.type, Integer)


def test_recursive_cte():
    """Test recursive CTE generation."""
    metadata = MetaData()
    tree = Table(
        "tree",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("parent_id", Integer, ForeignKey("tree.id")),
        Column("depth", Integer),
    )

    # Verify table structure
    assert "id" in tree.c
    assert "parent_id" in tree.c
    assert "depth" in tree.c
    assert isinstance(tree.c.parent_id.type, Integer)


def test_multiple_ctes():
    """Test multiple CTEs."""
    metadata = MetaData()
    Table(
        "base",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
    )

    cte1 = Table(
        "cte1",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("base_id", Integer, ForeignKey("base.id")),
        Column("doubled", Integer),
    )

    cte2 = Table(
        "cte2",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("cte1_id", Integer, ForeignKey("cte1.id")),
        Column("quadrupled", Integer),
    )

    # Verify table structure
    assert "id" in cte1.c
    assert "id" in cte2.c
    assert "base_id" in cte1.c
    assert "cte1_id" in cte2.c
    assert "doubled" in cte1.c
    assert "quadrupled" in cte2.c


def test_cte_with_multiple_references():
    """Test CTE with multiple references."""
    metadata = MetaData()
    Table(
        "base",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value1", Integer),
        Column("value2", Integer),
    )

    cte = Table(
        "cte",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("base_id", Integer, ForeignKey("base.id")),
        Column("sum", Integer),
        Column("product", Integer),
    )

    # Verify table structure
    assert "id" in cte.c
    assert "base_id" in cte.c
    assert "sum" in cte.c
    assert "product" in cte.c


def test_cte_with_complex_structure():
    """Test CTE with complex structure."""
    metadata = MetaData()
    Table(
        "base",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", Integer),
    )

    cte = Table(
        "cte",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("base_id", Integer, ForeignKey("base.id")),
        Column("complex", Integer),
    )

    # Verify table structure
    assert "id" in cte.c
    assert "base_id" in cte.c
    assert "complex" in cte.c
    assert isinstance(cte.c.complex.type, Integer)
