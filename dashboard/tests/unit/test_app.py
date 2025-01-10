import pytest
from flask import url_for

from dashboard.app import create_app


def test_index_redirect_if_not_logged_in(test_client):
    """Test that index redirects to login if not logged in."""
    response = test_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_index_if_logged_in(test_client, auth_headers):
    """Test that index returns 200 if logged in."""
    response = test_client.get("/", headers=auth_headers)
    assert response.status_code == 200


def test_login_get(test_client):
    """Test login page."""
    response = test_client.get("/login")
    assert response.status_code == 200


def test_login_post_valid(test_client):
    """Test valid login credentials."""
    response = test_client.post(
        "/login", json={"username": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    assert "token" in response.json


def test_login_post_invalid(test_client):
    """Test invalid login credentials."""
    response = test_client.post(
        "/login", json={"username": "wrong_user", "password": "wrong_password"}
    )
    assert response.status_code == 401


def test_logout(test_client, auth_headers):
    """Test logout."""
    response = test_client.get("/logout", headers=auth_headers)
    assert response.status_code == 200


def test_get_metrics(test_client, auth_headers):
    """Test getting metrics."""
    response = test_client.get("/metrics", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_metrics_unauthorized(test_client):
    """Test getting metrics without auth."""
    response = test_client.get("/metrics")
    assert response.status_code == 401


def test_cors_headers(test_client):
    """Test CORS headers are set."""
    response = test_client.options("/metrics")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "GET" in response.headers["Access-Control-Allow-Methods"]
