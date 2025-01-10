"""Conversion utility functions."""


def to_int(value, default=0):
    """Convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value, default=0.0):
    """Convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_bool(value, default=False):
    """Convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "t", "yes", "y", "1")
    if isinstance(value, (int, float)):
        return bool(value)
    return default
