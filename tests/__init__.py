"""Test package initialization."""

import contextlib
import re
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from sqlalchemy import MetaData, create_engine

from .assertions import eq_, raises


def assert_raises(
    exc: Type[Exception],
    callable_: Callable[..., Any],
    *args: Any,
    **kw: Any,
) -> Any:
    """Assert that callable_ raises exc."""
    try:
        callable_(*args, **kw)
    except exc:
        return True
    else:
        msg = f"Did not raise {exc}"
        raise AssertionError(msg)


def expect_warnings(*messages: str, **kw: Any) -> Any:
    """Context manager that expects certain warning messages."""
    import warnings

    @contextlib.contextmanager
    def expect() -> Generator[List[warnings.WarningMessage], None, None]:
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


def is_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is b with an optional message."""
    assert a is b, msg or f"{a!r} is not {b!r}"


def is_not_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a is not b with an optional message."""
    assert a is not b, msg or f"{a!r} is {b!r}"


def is_not_none(a: Any, msg: Optional[str] = None) -> None:
    """Assert a is not None with an optional message."""
    assert a is not None, msg or f"{a!r} is None"


def ne_(a: Any, b: Any, msg: Optional[str] = None) -> None:
    """Assert a != b with an optional message."""
    assert a != b, msg or f"{a!r} == {b!r}"


def is_true(a: Any, msg: Optional[str] = None) -> None:
    """Assert a is True with an optional message."""
    assert a is True, msg or f"{a!r} is not True"


T = TypeVar("T")


def assert_raises_message(
    exception: Type[Exception],
    msg: str,
    callable_: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Assert that callable_ raises exception with message msg."""
    try:
        callable_(*args, **kwargs)
        raise AssertionError(f"Callable did not raise {exception}")
    except exception as e:
        assert re.search(msg, str(e)), f"Exception message '{e!s}' did not match '{msg}'"
        return e


def expect_raises_message(
    exception: Type[Exception],
    msg: str,
    callable_: Optional[Callable[..., Any]] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Wrapper for assert_raises_message that returns a context manager if callable_ is None."""
    if callable_ is None:
        return _expect_raises_context(exception, msg)
    return assert_raises_message(exception, msg, callable_, *args, **kwargs)


class _expect_raises_context:
    """Context manager for expect_raises_message."""

    def __init__(self, exc: Type[Exception], msg: str) -> None:
        self.exc = exc
        self.msg = msg

    def __enter__(self) -> "_expect_raises_context":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        if exc_type is None:
            msg = f"Did not raise {self.exc}"
            raise AssertionError(msg)
        if not issubclass(exc_type, self.exc):
            return False
        if not re.search(self.msg, str(exc_val)):
            msg = f"Exception message '{exc_val!s}' did not match '{self.msg}'"
            raise AssertionError(msg)
        return True


from .config import TEST_DB_URL


def expect_raises(
    exc: Union[type, Tuple[type, ...]],
    callable_: Optional[Callable] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Assert that a callable raises an exception."""
    return raises(exc, callable_, *args, **kwargs)


def provide_metadata() -> MetaData:
    """Provide a fresh MetaData instance."""
    return MetaData()


class AssertsCompiledSQL:
    """Mixin class for SQL compilation assertion tests."""

    def assert_compile(
        self,
        clause: Any,
        result: str,
        params: Optional[Dict[str, Any]] = None,
        checkparams: Optional[Dict[str, Any]] = None,
        check_literal_execute: bool = True,
        check_post_param: bool = True,
        dialect: Optional[str] = None,
        checkpositional: Optional[List[Any]] = None,
        check_prefetch: Optional[List[Any]] = None,
        use_default_dialect: bool = False,
        allow_dialect_select: bool = False,
        literal_binds: bool = False,
        render_postcompile: bool = False,
    ) -> None:
        """Assert that a clause compiles to the expected SQL."""
        from sqlalchemy.sql import ClauseElement

        if use_default_dialect and dialect is not None:
            msg = "Can't specify dialect and use_default_dialect"
            raise ValueError(msg)

        if isinstance(clause, ClauseElement):
            if dialect is not None:
                dialect_obj = self._get_dialect(dialect)
            elif use_default_dialect:
                dialect_obj = self._get_default_dialect()
            else:
                dialect_obj = getattr(self, "__dialect__", None)

            kw: Dict[str, Any] = {}
            compile_kwargs: Dict[str, Any] = {}

            if params is not None:
                kw["column_keys"] = list(params)

            if literal_binds:
                compile_kwargs["literal_binds"] = True

            if render_postcompile:
                compile_kwargs["render_postcompile"] = True

            if dialect_obj:
                compiled = clause.compile(dialect=dialect_obj, **kw)
            else:
                compiled = clause.compile(**kw)

            if compile_kwargs:
                compiled = clause.compile(compile_kwargs=compile_kwargs)

            if checkparams is not None:
                eq_(compiled.construct_params(params), checkparams)
            if checkpositional is not None:
                eq_(compiled.construct_params(params), checkpositional)
            if check_prefetch is not None:
                eq_(compiled._prefetch, check_prefetch)

            sql_str = str(compiled)
            eq_(sql_str, result, f"Received SQL:\n{sql_str}\nExpected SQL:\n{result}")

            if check_literal_execute and isinstance(clause, ClauseElement):
                literal_sql = str(clause.compile(compile_kwargs={"literal_binds": True}))
                eq_(literal_sql, result, f"Received SQL:\n{literal_sql}\nExpected SQL:\n{result}")

            if check_post_param and isinstance(clause, ClauseElement):
                post_sql = str(clause.compile(compile_kwargs={"render_postcompile": True}))
                eq_(post_sql, result, f"Received SQL:\n{post_sql}\nExpected SQL:\n{result}")

    def _get_dialect(self, name: str) -> Any:
        """Get a dialect by name."""
        from sqlalchemy.dialects import registry

        return registry.load(name)()

    def _get_default_dialect(self) -> Any:
        """Get the default dialect."""
        return create_engine(TEST_DB_URL).dialect


class AssertsExecutionResults:
    """Mixin class for execution result assertion tests."""

    def assert_result(
        self,
        result: Any,
        expected: Any,
        params: Optional[Dict[str, Any]] = None,
        check_params: bool = True,
        check_type: bool = True,
    ) -> None:
        """Assert that a result matches the expected value."""
        if check_type:
            eq_(type(result), type(expected))
        if check_params and params is not None:
            eq_(result.parameters, params)
        eq_(result, expected)
