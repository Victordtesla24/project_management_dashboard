"""Authentication middleware module."""
import functools
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, TypeVar, Union, cast

import jwt
from flask import Response, current_app, redirect, request, session, url_for

F = TypeVar("F", bound=Callable[..., Any])


def create_token(payload: dict[str, Any]) -> str:
    """Create a JWT token with the given payload."""
    secret_key = current_app.config.get(
        "SECRET_KEY", os.environ.get("SECRET_KEY", "default-secret-key"),
    )
    if not payload.get("exp"):
        payload["exp"] = datetime.utcnow() + timedelta(hours=24)
    encoded = jwt.encode(payload, secret_key, algorithm="HS256")
    return encoded if isinstance(encoded, str) else str(encoded)


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        secret_key = current_app.config.get(
            "SECRET_KEY", os.environ.get("SECRET_KEY", "default-secret-key"),
        )
        return cast(dict[str, Any], jwt.decode(token, secret_key, algorithms=["HS256"]))
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_secure_hash(password: str) -> str:
    """Create a secure hash of the password."""
    salt = os.environ.get("AUTH_SALT", "default_salt")
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def init_auth(app: Any) -> None:
    """Initialize authentication for the application."""
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
    # Set default admin credentials if not in environment
    if "ADMIN_USER" not in os.environ:
        os.environ["ADMIN_USER"] = "admin"
    if "ADMIN_PASS" not in os.environ:
        os.environ["ADMIN_PASS"] = get_secure_hash("admin")


def login_required(f: F) -> F:
    """Decorator to require login for a route."""

    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if "user" not in session:
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return cast(F, decorated_function)


def authenticate(username: str, password: str) -> bool:
    """Authenticate a user with username and password."""
    admin_user = os.environ.get("ADMIN_USER")
    admin_pass = os.environ.get("ADMIN_PASS")
    if not admin_user or not admin_pass:
        return False
    hashed_password = get_secure_hash(password)
    return username == admin_user and hashed_password == admin_pass


def auth_required(f: F) -> F:
    """Alias for login_required decorator."""
    return login_required(f)


def ws_auth_required(f: F) -> F:
    """Decorator to require authentication for WebSocket connections."""

    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        auth_token = request.args.get("token")
        if not auth_token or auth_token != session.get("ws_token"):
            return Response("Unauthorized", 401)
        return f(*args, **kwargs)

    return cast(F, decorated_function)
