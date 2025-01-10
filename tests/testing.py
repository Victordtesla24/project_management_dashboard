"""Common test utilities."""
import itertools
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Connection

T = TypeVar("T")


def eq_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a == b with an optional message."""
    assert a == b, msg or f"{a!r} != {b!r}"


def ne_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a != b with an optional message."""
    assert a != b, msg or f"{a!r} == {b!r}"


def is_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is b with an optional message."""
    assert a is b, msg or f"{a!r} is not {b!r}"


def is_not_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is not b with an optional message."""
    assert a is not b, msg or f"{a!r} is {b!r}"


def combinations(*seqs: List[Any], **kw: Any) -> List[Tuple[Any, ...]]:
    """Return a list of all possible combinations of elements from the sequences."""
    return list(itertools.product(*seqs))


def fixture_session(**kw: Any) -> Connection:
    """Create a test database session."""
    return create_engine("sqlite://").connect()


def mock_engine(name: str = "default") -> Any:
    """Create a mock database engine."""
    return create_engine("sqlite://")


def resolve_lambda(func: Union[Callable[[], T], T], *arg: Any, **kw: Any) -> T:
    """Resolve a lambda or value to its final form."""
    return func() if callable(func) else func


def flag_combinations(*flags: str) -> List[Dict[str, bool]]:
    """Return all possible combinations of boolean flags."""
    return [dict(zip(flags, vals)) for vals in itertools.product([False, True], repeat=len(flags))]


def expect_warnings(*messages: str, **kw: Any) -> Any:
    """Context manager that expects certain warning messages."""
    import warnings
    from contextlib import contextmanager

    @contextmanager
    def expect():
        with warnings.catch_warnings(record=True) as log:
            warnings.simplefilter("always")
            yield log

        remaining = [str(m.message) for m in log]
        for msg in messages:
            for i, rem in enumerate(remaining):
                if re.search(msg, rem, re.I):
                    remaining.pop(i)
                    break
            else:
                raise AssertionError(f"Warning {msg!r} not found. Remaining warnings: {remaining}")

        if not kw.get("regex"):
            for rem in remaining:
                raise AssertionError(f"Additional unexpected warning: {rem!r}")

    return expect()


def provide_metadata(schema: Optional[str] = None) -> MetaData:
    """Create a new MetaData instance."""
    return MetaData(schema=schema)


def requires_python_3() -> None:
    """Skip test if not running on Python 3."""
