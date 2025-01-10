"""Module with examples from the tutorial section of the docs."""
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestExamples:
    """Test examples from documentation."""

    @pytest.fixture()
    def mock_objects(self):
        """Create mock objects for testing."""
        # Mock data
        test_sha = b"1234567890" * 2  # 20 bytes
        test_data = b"my test data"
        test_tuple = ("blob", len(test_data), BytesIO(test_data))

        # Create mock objects
        mock_db = Mock()
        mock_stream = MagicMock()
        mock_info = MagicMock()

        # Configure mock objects
        mock_db.sha_iter.return_value = [test_sha]
        mock_db.has_object.return_value = True
        mock_db.stream.return_value = mock_stream
        mock_db.info.return_value = mock_info

        # Configure stream properties
        mock_stream.size = len(test_data)
        mock_stream.read.return_value = test_data
        mock_stream.__getitem__.return_value = test_tuple
        mock_stream.binsha = test_sha

        # Configure info properties
        mock_info.__getitem__.return_value = test_tuple
        mock_info.binsha = test_sha

        return {
            "db": mock_db,
            "stream": mock_stream,
            "info": mock_info,
            "sha": test_sha,
            "data": test_data,
            "tuple": test_tuple,
        }

    def test_object_iteration(self, mock_objects):
        """Test iterating over git objects."""
        mock_db = mock_objects["db"]

        # Test iteration and object access
        for sha1 in mock_db.sha_iter():
            oinfo = mock_db.info(sha1)
            ostream = mock_db.stream(sha1)
            assert oinfo[:3] == ostream[:3]
            assert len(ostream.read()) == ostream.size
            assert mock_db.has_object(oinfo.binsha)

    def test_object_storage(self, mock_objects):
        """Test storing git objects."""
        mock_db = mock_objects["db"]
        mock_stream = mock_objects["stream"]
        test_sha = mock_objects["sha"]

        # Test object storage
        mock_stream.binsha = None
        mock_db.store(mock_stream)
        mock_stream.binsha = test_sha
        assert len(mock_stream.binsha) == 20
        assert mock_db.has_object(mock_stream.binsha)

    def test_object_properties(self, mock_objects):
        """Test git object properties."""
        mock_stream = mock_objects["stream"]
        test_data = mock_objects["data"]
        test_tuple = mock_objects["tuple"]

        # Test stream properties
        assert mock_stream.size == len(test_data)
        assert mock_stream.read() == test_data
        assert mock_stream[:3] == test_tuple

    @patch("os.path.exists")
    def test_object_persistence(self, mock_exists, mock_objects):
        """Test git object persistence."""
        mock_db = mock_objects["db"]
        mock_stream = mock_objects["stream"]
        test_sha = mock_objects["sha"]

        # Configure mock
        mock_exists.return_value = True

        # Test persistence
        mock_stream.binsha = test_sha
        assert mock_db.has_object(mock_stream.binsha)
        assert len(mock_stream.binsha) == 20
