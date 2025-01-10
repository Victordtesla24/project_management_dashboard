"""Unit tests for string lowering utilities."""

import pytest

from src.utils.lowering import (
    to_lower,
    to_lower_dict_keys,
    to_lower_list,
    to_lower_safe,
)


def test_to_lower():
    """Test basic string lowering."""
    assert to_lower("Hello") == "hello"
    assert to_lower("WORLD") == "world"
    assert to_lower("MiXeD") == "mixed"
    assert to_lower("already_lower") == "already_lower"


def test_to_lower_error():
    """Test error handling in to_lower."""
    with pytest.raises(TypeError):
        to_lower(None)
    with pytest.raises(TypeError):
        to_lower(123)
    with pytest.raises(TypeError):
        to_lower(["not", "a", "string"])


def test_to_lower_safe():
    """Test safe string lowering."""
    assert to_lower_safe("Hello") == "hello"
    assert to_lower_safe(None) == ""
    assert to_lower_safe(123) == ""
    assert to_lower_safe(None, default="N/A") == "N/A"


def test_to_lower_list():
    """Test list lowering."""
    input_list = ["Hello", "WORLD", "MiXeD", "already_lower"]
    expected = ["hello", "world", "mixed", "already_lower"]
    assert to_lower_list(input_list) == expected


def test_to_lower_list_with_non_strings():
    """Test list lowering with non-string elements."""
    input_list = ["Hello", 123, None, "WORLD"]
    expected = ["hello", "", "", "world"]
    assert to_lower_list(input_list) == expected


def test_to_lower_list_error():
    """Test error handling in list lowering."""
    with pytest.raises(TypeError):
        to_lower_list("not_a_list")
    with pytest.raises(TypeError):
        to_lower_list(123)
    with pytest.raises(TypeError):
        to_lower_list(None)


def test_to_lower_dict_keys():
    """Test dictionary key lowering."""
    input_dict = {"Hello": 1, "WORLD": 2, "MiXeD": 3, "already_lower": 4}
    expected = {"hello": 1, "world": 2, "mixed": 3, "already_lower": 4}
    assert to_lower_dict_keys(input_dict) == expected


def test_to_lower_dict_keys_with_non_string_keys():
    """Test dictionary key lowering with non-string keys."""
    input_dict = {"Hello": 1, 123: 2, None: 3, "WORLD": 4}
    expected = {"hello": 1, "": 2, "": 3, "world": 4}
    assert to_lower_dict_keys(input_dict) == expected


def test_to_lower_dict_keys_error():
    """Test error handling in dictionary key lowering."""
    with pytest.raises(TypeError):
        to_lower_dict_keys("not_a_dict")
    with pytest.raises(TypeError):
        to_lower_dict_keys(123)
    with pytest.raises(TypeError):
        to_lower_dict_keys(None)
