"""Tests for utils module."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from dashboard.utils import format_metric, get_data_dir, load_config


class TestUtils(unittest.TestCase):
    """Test cases for utils module."""

    def test_load_config(self):
        """Test loading configuration from file."""
        config = {"key": "value"}

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump(config, f)
            config_path = f.name

        loaded_config = load_config(config_path)
        self.assertEqual(loaded_config, config)

        os.unlink(config_path)

    def test_get_data_dir(self):
        """Test getting data directory path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["DATA_DIR"] = tmp_dir
            data_dir = get_data_dir()

            self.assertIsInstance(data_dir, Path)
            self.assertTrue(data_dir.exists())
            self.assertTrue(data_dir.is_dir())

    def test_format_metric(self):
        """Test metric value formatting."""
        self.assertEqual(format_metric(75.5), "75.50%")
        self.assertEqual(format_metric(75.5, precision=1), "75.5%")
        self.assertEqual(format_metric(75.5, precision=0), "76%")


if __name__ == "__main__":
    unittest.main()
