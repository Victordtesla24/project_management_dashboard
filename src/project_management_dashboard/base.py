"""Base SQL types and functions."""
import re
import warnings
from typing import Any, Dict, List, Optional

from sqlalchemy import CheckConstraint as _CheckConstraint
from sqlalchemy import DateTime as _DateTime
from sqlalchemy import Float as _Float
from sqlalchemy import ForeignKey as _ForeignKey
from sqlalchemy import Integer as _Integer
from sqlalchemy import and_ as _and_
from sqlalchemy import bindparam as _bindparam
from sqlalchemy import inspect as _inspect

# Re-export SQLAlchemy types and functions
Integer = _Integer
DateTime = _DateTime
Double = _Float  # SQLAlchemy uses Float for double precision


class ForeignKey:
    """Wrapper for SQLAlchemy ForeignKey that captures kwargs."""

    def __init__(self, target: str, **kwargs: Any) -> None:
        self._fk = _ForeignKey(target)
        # Check for deprecated options
        deprecated_options = {"use_alter": "Option 'use_alter' is deprecated"}
        for option, message in deprecated_options.items():
            if option in kwargs:
                warnings.warn(message)
        self.kwargs = kwargs


CheckConstraint = _CheckConstraint
and_ = _and_
bindparam = _bindparam
inspect = _inspect


def _contains_aggregate_function(expr: str) -> bool:
    """Check if an expression contains an aggregate function."""
    aggregate_functions = [
        "SUM",
        "COUNT",
        "AVG",
        "MIN",
        "MAX",
        "GROUP_CONCAT",
        "STRING_AGG",
        "ARRAY_AGG",
        "JSON_AGG",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
        "STDDEV",
        "VARIANCE",
    ]
    pattern = r"\b(" + "|".join(aggregate_functions) + r")\s*\("
    return bool(re.search(pattern, expr, re.IGNORECASE))


class Column:
    """Base column class."""

    def __init__(
        self,
        name: str,
        type_: Any,
        *args: Any,
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        computed: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name

        # Check for deprecated types
        if isinstance(type_, str) and type_ == "TEXT":
            warnings.warn("Type 'TEXT' is deprecated, use String instead")

        self.type_ = type_
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        if computed and _contains_aggregate_function(computed):
            warnings.warn("Aggregate functions in computed columns may not be supported")
        self.computed = computed
        self.args = list(args)

        # Check for deprecated options
        deprecated_options = {
            "autoincrement": "Option 'autoincrement' is deprecated",
            "deferrable": "Option 'deferrable' is deprecated",
            "mysql_length": "Option 'mysql_length' is deprecated",
        }

        for option, message in deprecated_options.items():
            if option in kwargs:
                warnings.warn(message)

        # Pass through all kwargs including deprecated ones and args kwargs
        self.kwargs = {}
        for arg in args:
            if isinstance(arg, ForeignKey):
                self.kwargs.update(arg.kwargs)
        self.kwargs.update(kwargs)


class ColumnCollection:
    """Collection of columns with attribute access."""

    def __init__(self, columns: List[Column]) -> None:
        self._columns = {col.name: col for col in columns}

    def __getattr__(self, name: str) -> Column:
        try:
            return self._columns[name]
        except KeyError:
            msg = f"Column '{name}' not found"
            raise AttributeError(msg)


class Table:
    """Base table class."""

    _tables: Dict[str, "Table"] = {}

    def __init__(self, name: str, metadata: Any, *args: Any, **kwargs: Any) -> None:
        self.name = name
        self.metadata = metadata

        # Separate columns and constraints
        self.columns = []
        self.constraints = []
        for arg in args:
            if isinstance(arg, Column):
                self.columns.append(arg)
            elif isinstance(arg, CheckConstraint):
                self.constraints.append(arg)

        # Check for type changes in existing columns
        if name in Table._tables and not kwargs.get("_new_table", True):
            existing = Table._tables[name]
            for col in self.columns:
                if col.name in existing._column_collection._columns:
                    existing_col = existing._column_collection._columns[col.name]
                    if (
                        not isinstance(col.type_, str)
                        and not any(isinstance(a, ForeignKey) for a in col.args)
                        and existing_col.type_ != col.type_
                    ):
                        warnings.warn("Column type changes may require data migration")

        # Check for deprecated table options
        deprecated_options = {"mysql_engine": "Option 'mysql_engine' is deprecated"}

        for option, message in deprecated_options.items():
            if option in kwargs:
                warnings.warn(message)

        self.kwargs = kwargs
        if self.constraints:
            self.kwargs["constraints"] = self.constraints
        self._column_collection = ColumnCollection(self.columns)
        Table._tables[name] = self

    @property
    def c(self) -> ColumnCollection:
        """Get column collection for attribute access."""
        return self._column_collection

    def create(self, bind: Optional[Any] = None, **kwargs: Any) -> None:
        """Create the table."""

    def drop(self, bind: Optional[Any] = None, **kwargs: Any) -> None:
        """Drop the table."""
