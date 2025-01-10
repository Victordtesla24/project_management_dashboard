"""Test module for properties decorators."""
import logging
from unittest.mock import Mock, patch

import pytest

from dashboard.core.properties import (
    accepts_baseline,
    checks,
    set_test_id,
    takes_config,
)


@pytest.fixture()
def mock_utils():
    """Mock utils module."""
    with patch("dashboard.core.properties.utils") as mock:
        mock.check_ast_node = Mock(return_value="AST_NODE")
        yield mock


def test_checks_decorator(mock_utils):
    """Test checks decorator."""

    # Define a test function with the checks decorator
    @checks("File", "Call")
    def test_func():
        pass

    # Verify checks were added
    assert hasattr(test_func, "_checks")
    assert "File" in test_func._checks
    assert "AST_NODE" in test_func._checks


def test_takes_config_decorator_with_name():
    """Test takes_config decorator with explicit name."""

    # Define a test function with the takes_config decorator
    @takes_config("test_name")
    def test_func():
        pass

    # Verify config name was set
    assert hasattr(test_func, "_takes_config")
    assert test_func._takes_config == "test_name"


def test_takes_config_decorator_without_name():
    """Test takes_config decorator without name."""

    # Define a test function with the takes_config decorator
    @takes_config
    def test_func():
        pass

    # Verify config name defaults to function name
    assert hasattr(test_func, "_takes_config")
    assert test_func._takes_config == "test_func"


def test_set_test_id_decorator():
    """Test set_test_id decorator."""

    # Define a test function with the set_test_id decorator
    @set_test_id("B101")
    def test_func():
        pass

    # Verify test ID was set
    assert hasattr(test_func, "_test_id")
    assert test_func._test_id == "B101"


def test_accepts_baseline_decorator():
    """Test accepts_baseline decorator."""

    # Define a test function with the accepts_baseline decorator
    @accepts_baseline
    def test_func():
        pass

    # Verify accepts_baseline flag was set
    assert hasattr(test_func, "_accepts_baseline")
    assert test_func._accepts_baseline is True


def test_multiple_decorators(mock_utils):
    """Test using multiple decorators together."""

    # Define a test function with multiple decorators
    @checks("File")
    @set_test_id("B102")
    @takes_config("test_config")
    def test_func():
        pass

    # Verify all attributes were set
    assert hasattr(test_func, "_checks")
    assert "File" in test_func._checks
    assert hasattr(test_func, "_test_id")
    assert test_func._test_id == "B102"
    assert hasattr(test_func, "_takes_config")
    assert test_func._takes_config == "test_config"


def test_decorator_logging(caplog):
    """Test decorator logging."""
    caplog.set_level(logging.DEBUG)

    # Define a test function with the accepts_baseline decorator
    @accepts_baseline
    def test_func():
        pass

    # Verify log messages
    assert "accepts_baseline() decorator executed on test_func" in caplog.text
