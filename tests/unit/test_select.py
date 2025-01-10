"""Unit tests for database select operations."""


from src.db.dialect import Dialect
from src.db.select import Select


def test_select_init():
    """Test select builder initialization."""
    select = Select("users")
    assert select.table_name == "users"
    assert isinstance(select.dialect, Dialect)
    assert select.columns == []
    assert select.where_clauses == []
    assert select.where_params == []
    assert select.order_by is None
    assert select.limit_value is None


def test_select_all():
    """Test basic select all query."""
    select = Select("users")
    sql = select.build()
    params = select.get_parameters()

    assert sql == 'SELECT * FROM "users"'
    assert params == []


def test_select_columns():
    """Test selecting specific columns."""
    select = Select("users").columns_list("id", "name", "email")
    sql = select.build()

    assert sql == 'SELECT "id", "name", "email" FROM "users"'


def test_select_where():
    """Test where clause."""
    select = Select("users").where("age > %s", 18)
    sql = select.build()
    params = select.get_parameters()

    assert sql == 'SELECT * FROM "users" WHERE age > %s'
    assert params == [18]


def test_select_multiple_where():
    """Test multiple where clauses."""
    select = Select("users")
    select.where("age > %s", 18).where("city = %s", "London")
    sql = select.build()
    params = select.get_parameters()

    assert sql == 'SELECT * FROM "users" WHERE age > %s AND city = %s'
    assert params == [18, "London"]


def test_select_order():
    """Test order by clause."""
    select = Select("users").order("age", desc=True)
    sql = select.build()

    assert sql == 'SELECT * FROM "users" ORDER BY age DESC'


def test_select_limit():
    """Test limit clause."""
    select = Select("users").limit(10)
    sql = select.build()

    assert sql == 'SELECT * FROM "users" LIMIT 10'


def test_select_complex():
    """Test complex query with all clauses."""
    select = Select("users")
    select.columns_list("id", "name")
    select.where("age > %s", 18)
    select.where("city = %s", "London")
    select.order("name")
    select.limit(5)

    sql = select.build()
    params = select.get_parameters()

    assert (
        sql
        == 'SELECT "id", "name" FROM "users" WHERE age > %s AND city = %s ORDER BY name ASC LIMIT 5'
    )
    assert params == [18, "London"]


def test_select_custom_dialect():
    """Test select with custom dialect."""
    dialect = Dialect("postgresql")
    dialect.schema = "public"
    select = Select("users", dialect)
    sql = select.build()

    assert sql == 'SELECT * FROM "public"."users"'
