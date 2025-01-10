"""String lowering utilities."""


def to_lower(value: str) -> str:
    """Convert string to lowercase."""
    if not isinstance(value, str):
        msg = "Value must be a string"
        raise TypeError(msg)
    return value.lower()


def to_lower_safe(value: str, default: str = "") -> str:
    """Convert string to lowercase with fallback."""
    try:
        return to_lower(value)
    except (TypeError, AttributeError):
        return default


def to_lower_list(values: list) -> list:
    """Convert list of strings to lowercase."""
    if not isinstance(values, list):
        msg = "Values must be a list"
        raise TypeError(msg)
    return [to_lower_safe(v) for v in values]


def to_lower_dict_keys(data: dict) -> dict:
    """Convert dictionary keys to lowercase."""
    if not isinstance(data, dict):
        msg = "Data must be a dictionary"
        raise TypeError(msg)
    return {to_lower_safe(k): v for k, v in data.items()}
