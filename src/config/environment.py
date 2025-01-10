"""Environment configuration utilities."""

import os
from typing import Any, Dict, Optional


class Environment:
    """Environment configuration manager."""

    def __init__(self, env_file: Optional[str] = None) -> None:
        """Initialize environment with optional env file."""
        self._env_file = env_file
        self._values: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load environment variables."""
        # Load from env file if specified
        if self._env_file and os.path.exists(self._env_file):
            with open(self._env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        self._values[key.strip()] = value.strip()

        # Override with actual environment variables
        for key, value in os.environ.items():
            self._values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get environment variable value."""
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set environment variable value."""
        self._values[key] = value
        os.environ[key] = str(value)

    def clear(self, key: str) -> None:
        """Clear environment variable."""
        self._values.pop(key, None)
        os.environ.pop(key, None)
