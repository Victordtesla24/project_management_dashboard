"""Test database engines module."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import TEST_DB_URL


def create_test_engine() -> Engine:
    """Create a test database engine."""
    return create_engine(TEST_DB_URL, echo=False)


@contextmanager
def create_test_session() -> Generator[Session, None, None]:
    """Create a test database session."""
    engine = create_test_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def setup_test_database() -> None:
    """Set up the test database."""
    return create_test_engine()
    # Add any database setup code here


def teardown_test_database() -> None:
    """Tear down the test database."""
    create_test_engine()
    # Add any database teardown code here
