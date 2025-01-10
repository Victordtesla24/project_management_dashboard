"""Unit tests for conversion utilities."""


from src.utils.conversion_utils import to_bool, to_float, to_int


def test_to_int():
    """Test integer conversion."""
    assert to_int("123") == 123
    assert to_int("abc") == 0  # default value
    assert to_int("abc", default=10) == 10
    assert to_int(None) == 0
    assert to_int(12.34) == 12


def test_to_float():
    """Test float conversion."""
    assert to_float("123.45") == 123.45
    assert to_float("abc") == 0.0  # default value
    assert to_float("abc", default=1.5) == 1.5
    assert to_float(None) == 0.0
    assert to_float(123) == 123.0


def test_to_bool():
    """Test boolean conversion."""
    # String tests
    assert to_bool("true") is True
    assert to_bool("True") is True
    assert to_bool("yes") is True
    assert to_bool("1") is True
    assert to_bool("false") is False
    assert to_bool("no") is False

    # Number tests
    assert to_bool(1) is True
    assert to_bool(0) is False

    # Boolean tests
    assert to_bool(True) is True
    assert to_bool(False) is False

    # Default value test
    assert to_bool(None) is False
    assert to_bool(None, default=True) is True
