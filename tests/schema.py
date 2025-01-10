"""Test schema module."""

from typing import Any, Optional

from sqlalchemy import Column as SAColumn
from sqlalchemy import MetaData, Table


class Column:
    """Column class for testing."""

    def __init__(
        self,
        name: str,
        type_: Any,
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize column."""
        self.name = name
        self.type_ = type_
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.kwargs = kwargs

    def create_column(self) -> SAColumn:
        """Create SQLAlchemy column."""
        return SAColumn(
            self.name,
            self.type_,
            primary_key=self.primary_key,
            nullable=self.nullable,
            unique=self.unique,
            **self.kwargs,
        )


def create_table(name: str, *columns: Column, metadata: Optional[MetaData] = None) -> Table:
    """Create a table with the given columns."""
    if metadata is None:
        metadata = MetaData()

    return Table(
        name,
        metadata,
        *[col.create_column() for col in columns],
    )
