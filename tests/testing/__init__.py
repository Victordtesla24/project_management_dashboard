"""Testing utilities package."""
import itertools
import re
import warnings
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, TypeVar

from tests.assertions import eq_, raises

from .fixtures import AlterColRoundTripFixture

T = TypeVar("T")


def is_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is b with an optional message."""
    assert a is b, msg or f"{a!r} is not {b!r}"


def is_not_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is not b with an optional message."""
    assert a is not b, msg or f"{a!r} is {b!r}"


def is_not_none(a: Any, msg: Optional[str] = None) -> None:
    """Assert a is not None with an optional message."""
    assert a is not None, msg or f"{a!r} is None"


def combinations(*seqs: List[Dict[str, Any]], **kw: Any) -> List[Dict[str, Any]]:
    """Return a list of all possible combinations of dictionary elements."""
    result = []
    for combo in itertools.product(*seqs):
        merged = {}
        for d in combo:
            merged.update(d)
        result.append(merged)
    return result


def expect_warnings(*messages: str, **kw: Any) -> Any:
    """Context manager that expects certain warning messages."""

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


__all__ = [
    "AlterColRoundTripFixture",
    "eq_",
    "raises",
    "is_",
    "is_not_",
    "is_not_none",
    "combinations",
    "expect_warnings",
]
