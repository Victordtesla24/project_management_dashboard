"""Test assertion utilities."""

import contextlib
import re
from typing import Any, Callable, Optional, Tuple, Type, Union


def eq_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a == b with optional message."""
    assert a == b, msg or f"{a!r} != {b!r}"


def ne_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a != b with optional message."""
    assert a != b, msg or f"{a!r} == {b!r}"


def is_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is b with optional message."""
    assert a is b, msg or f"{a!r} is not {b!r}"


def is_not_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is not b with optional message."""
    assert a is not b, msg or f"{a!r} is {b!r}"


def in_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a in b with optional message."""
    assert a in b, msg or f"{a!r} not in {b!r}"


def is_true(a: Any, msg: Optional[str] = None) -> None:
    """Assert a is True with optional message."""
    assert a is True, msg or f"{a!r} is not True"


def is_false(a: Any, msg: Optional[str] = None) -> None:
    """Assert a is False with optional message."""
    assert a is False, msg or f"{a!r} is not False"


def assert_raises(
    exc_cls: Type[Exception],
    callable_: Callable[..., Any],
    *args: Any,
    **kw: Any,
) -> Any:
    """Assert that callable raises the expected exception."""
    try:
        callable_(*args, **kw)
    except exc_cls:
        return True
    else:
        msg = f"Expected {exc_cls.__name__} to be raised"
        raise AssertionError(msg)


@contextlib.contextmanager
def raises(
    exc: Union[Type[Exception], Tuple[Type[Exception], ...]],
    msg: Optional[str] = None,
) -> Any:
    """Context manager for asserting that code raises an exception."""
    try:
        yield
    except exc:
        pass
    else:
        raise AssertionError(msg or f"Expected {exc.__name__} to be raised")


def expect_raises(
    exc: Union[Type[Exception], Tuple[Type[Exception], ...]],
    callable_: Optional[Callable] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Assert that a callable raises an exception."""
    if callable_ is None:
        return raises(exc)
    return assert_raises(exc, callable_, *args, **kwargs)


def expect_raises_message(
    exc: Type[Exception],
    msg: str,
    callable_: Optional[Callable] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Assert that callable raises exception with message."""
    try:
        if callable_ is None:
            yield
        else:
            callable_(*args, **kwargs)
    except exc as e:
        assert re.search(msg, str(e)), f"Exception message '{e!s}' did not match '{msg}'"
        return e
    else:
        raise AssertionError(f"Expected {exc.__name__} to be raised")


@contextlib.contextmanager
def expect_warnings(messages: Union[str, list[str]], regex: bool = False) -> Any:
    """Context manager for asserting that code produces expected warnings.

    Args:
    ----
        messages: String or list of strings containing warning messages to match
        regex: If True, treat messages as regex patterns
    """
    import warnings

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        yield

    if isinstance(messages, str):
        messages = [messages]

    if len(caught_warnings) != len(messages):
        msg = f"Expected {len(messages)} warnings, got {len(caught_warnings)}"
        raise AssertionError(msg)

    for warning, message in zip(caught_warnings, messages):
        if regex:
            assert re.search(
                message,
                str(warning.message),
            ), f"Warning '{warning.message}' did not match pattern '{message}'"
        else:
            assert message in str(
                warning.message,
            ), f"Warning '{warning.message}' did not contain '{message}'"
