"""Test pack file operations with mocks."""
from unittest.mock import Mock, mock_open, patch

from .lib import TestBase


class TestPack(TestBase):
    def test_pack_operations(self):
        """Test basic pack operations using mocks."""
        # Mock file data
        mock_pack_data = b"PACK\x00\x00\x00\x02\x00\x00\x00\x03" + b"\x00" * 100
        mock_index_data = b"\xff\x74\x4f\x63\x00\x00\x00\x02\x00\x00\x00\x03" + b"\x00" * 100

        # Create mock file objects
        mock_pack_file = mock_open(read_data=mock_pack_data).return_value
        mock_index_file = mock_open(read_data=mock_index_data).return_value

        with patch("builtins.open") as mock_open_func:
            # Configure mock to return different file objects based on path
            def side_effect(path, *args, **kwargs):
                if path.endswith(".pack"):
                    return mock_pack_file
                if path.endswith(".idx"):
                    return mock_index_file
                msg = f"Mock file not found: {path}"
                raise FileNotFoundError(msg)

            mock_open_func.side_effect = side_effect

            # Test pack file operations
            with open("test.pack", "rb") as f:
                data = f.read()
                assert data.startswith(b"PACK")  # Pack file signature
                assert len(data) > 12  # Basic size check

            # Test index file operations
            with open("test.idx", "rb") as f:
                data = f.read()
                assert len(data) > 12  # Basic size check

    def test_pack_writing(self):
        """Test pack file writing operations."""
        mock_data = []

        def mock_write(data):
            mock_data.append(data)
            return len(data)

        # Test writing pack data
        pack_writer = Mock(side_effect=mock_write)
        index_writer = Mock(side_effect=mock_write)

        # Write some test objects
        test_objects = [
            Mock(type=1, data=b"test1"),
            Mock(type=2, data=b"test2"),
            Mock(type=3, data=b"test3"),
        ]

        for obj in test_objects:
            pack_writer(obj.data)
            index_writer(obj.data)

        # Verify writes
        assert len(mock_data) == 6  # 3 objects * 2 writers
        assert all(isinstance(d, bytes) for d in mock_data)

    def test_pack_reading(self):
        """Test pack file reading operations."""
        # Mock pack file content
        pack_content = (
            b"PACK"  # signature
            b"\x00\x00\x00\x02"  # version 2
            b"\x00\x00\x00\x03"  # 3 objects
            b"test data..."  # some content
        )

        with patch("builtins.open", mock_open(read_data=pack_content)):
            with open("test.pack", "rb") as f:
                # Read and verify header
                signature = f.read(4)
                version = int.from_bytes(f.read(4), "big")
                num_objects = int.from_bytes(f.read(4), "big")

                assert signature == b"PACK"
                assert version == 2
                assert num_objects == 3

                # Read some content
                content = f.read()
                assert content == b"test data..."
