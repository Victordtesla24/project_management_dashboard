"""Authentication routes module."""
from typing import Union

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.wrappers import Response as WerkzeugResponse

from dashboard.auth.middleware import authenticate, create_token

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, WerkzeugResponse]:
    """Handle login requests."""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if authenticate(username, password):
            # Create JWT token and set in cookie
            token = create_token({"username": username})
            session["user"] = username
            next_url = request.args.get("next", url_for("dashboard.index"))
            response = redirect(next_url)
            response.set_cookie("auth_token", token)
            return response
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


@bp.route("/logout")
def logout() -> WerkzeugResponse:
    """Handle logout requests."""
    session.clear()
    response = redirect(url_for("auth.login"))
    response.delete_cookie("auth_token")
    return response
