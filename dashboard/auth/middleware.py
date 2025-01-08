"""Authentication middleware for the dashboard."""

import functools
from typing import Callable, Any, Dict, Optional
from flask import session, redirect, url_for, request, Response, current_app
import hashlib
import os
import jwt
from datetime import datetime, timedelta

def create_token(payload: Dict[str, Any]) -> str:
    """Create a new JWT token."""
    secret_key = current_app.config.get('SECRET_KEY', os.environ.get('SECRET_KEY', 'default-secret-key'))
    if not payload.get('exp'):
        payload['exp'] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload if valid."""
    try:
        secret_key = current_app.config.get('SECRET_KEY', os.environ.get('SECRET_KEY', 'default-secret-key'))
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_secure_hash(password: str) -> str:
    """Generate secure hash of password."""
    salt = os.environ.get('AUTH_SALT', 'default_salt')
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def init_auth(app: Any) -> None:
    """Initialize authentication settings."""
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # Set default admin credentials if not in environment
    if 'ADMIN_USER' not in os.environ:
        os.environ['ADMIN_USER'] = 'admin'
    if 'ADMIN_PASS' not in os.environ:
        os.environ['ADMIN_PASS'] = get_secure_hash('admin')

def login_required(f: Callable) -> Callable:
    """Decorator to require login for routes."""
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'user' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def authenticate(username: str, password: str) -> bool:
    """Authenticate user credentials."""
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASS')
    
    if not admin_user or not admin_pass:
        print("Missing admin credentials in environment")
        return False
    
    hashed_password = get_secure_hash(password)
    print(f"Input hash: {hashed_password}")
    print(f"Stored hash: {admin_pass}")
    
    return username == admin_user and hashed_password == admin_pass

def auth_required(f: Callable) -> Callable:
    """Decorator to require authentication for routes (alias for login_required)."""
    return login_required(f)

def ws_auth_required(f: Callable) -> Callable:
    """Decorator to require authentication for WebSocket connections."""
    @functools.wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        auth_token = request.args.get('token')
        if not auth_token or auth_token != session.get('ws_token'):
            return Response('Unauthorized', 401)
        return f(*args, **kwargs)
    return decorated_function
