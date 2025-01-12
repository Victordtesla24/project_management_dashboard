"""Authentication package initialization."""
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from flask import redirect, request, url_for

F = TypeVar("F", bound=Callable[..., Any])


def login_required(f: F) -> F:
    """Decorator to require login for a route."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not request.cookies.get("auth_token"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return cast(F, decorated_function)
