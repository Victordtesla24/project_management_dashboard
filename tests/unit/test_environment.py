"""Unit tests for environment configuration."""

import os

import pytest

from src.config.environment import Environment


@pytest.fixture()
def env_file(tmp_path):
    """Create a temporary env file for testing."""
    env_path = tmp_path / ".env.test"
    with open(env_path, "w") as f:
        f.write("TEST_VAR=test_value\n")
        f.write("# Comment line\n")
        f.write("ANOTHER_VAR=123\n")
    return str(env_path)


def test_environment_init():
    """Test environment initialization without file."""
    env = Environment()
    assert isinstance(env._values, dict)
    assert env._env_file is None


def test_environment_with_file(env_file):
    """Test environment initialization with file."""
    env = Environment(env_file)
    assert env.get("TEST_VAR") == "test_value"
    assert env.get("ANOTHER_VAR") == "123"


def test_environment_override():
    """Test environment variable override."""
    os.environ["TEST_OVERRIDE"] = "original"
    env = Environment()
    assert env.get("TEST_OVERRIDE") == "original"

    env.set("TEST_OVERRIDE", "new_value")
    assert env.get("TEST_OVERRIDE") == "new_value"
    assert os.environ["TEST_OVERRIDE"] == "new_value"


def test_environment_clear():
    """Test clearing environment variables."""
    env = Environment()
    env.set("TEST_CLEAR", "value")
    assert env.get("TEST_CLEAR") == "value"

    env.clear("TEST_CLEAR")
    assert env.get("TEST_CLEAR") is None
    assert "TEST_CLEAR" not in os.environ


def test_environment_default_value():
    """Test getting default value."""
    env = Environment()
    assert env.get("NON_EXISTENT", "default") == "default"
