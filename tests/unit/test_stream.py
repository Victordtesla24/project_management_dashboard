"""Test stream functionality."""
import os
import tempfile
import zlib
from io import BytesIO
from unittest import TestCase


class DummyStream:
    """A dummy stream for testing."""

    def __init__(self) -> None:
        self.closed = False

    def close(self):
        self.closed = True


class TestStream(TestCase):
    """Test stream operations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_sizes = (15, 1000, 10000)  # Different sizes to test

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_stream_reader(self):
        """Test basic stream reading."""
        for size in self.data_sizes:
            # Create test data
            data = b"x" * size

            # Create file-based stream
            temp_path = os.path.join(self.temp_dir, f"test_stream_{size}.dat")
            with open(temp_path, "wb") as f:
                f.write(data)

            # Test reading in chunks
            with open(temp_path, "rb") as stream:
                # Read in small steps
                chunk_size = size // 10
                read_data = b""
                while True:
                    chunk = stream.read(chunk_size)
                    if not chunk:
                        break
                    read_data += chunk

                # Verify data
                assert read_data == data

                # Test seek and read
                stream.seek(0)
                all_data = stream.read()
                assert all_data == data

    def test_compressed_stream(self):
        """Test compressed stream operations."""
        for size in self.data_sizes:
            # Create test data
            data = b"x" * size
            compressed_data = zlib.compress(data)

            # Write compressed data
            temp_path = os.path.join(self.temp_dir, f"test_compressed_{size}.dat")
            with open(temp_path, "wb") as f:
                f.write(compressed_data)

            # Read and decompress
            with open(temp_path, "rb") as f:
                compressed = f.read()
                decompressed = zlib.decompress(compressed)
                assert decompressed == data

    def test_memory_stream(self):
        """Test memory-based stream."""
        for size in self.data_sizes:
            # Create test data
            data = b"x" * size

            # Test BytesIO operations
            stream = BytesIO(data)

            # Read in chunks
            chunk_size = size // 10
            read_data = b""
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                read_data += chunk

            # Verify data
            assert read_data == data

            # Test seek and read
            stream.seek(0)
            all_data = stream.read()
            assert all_data == data

    def test_stream_closing(self):
        """Test stream closing behavior."""
        # Test with dummy stream
        stream = DummyStream()
        assert not stream.closed
        stream.close()
        assert stream.closed

        # Test with real file stream
        temp_path = os.path.join(self.temp_dir, "test_close.dat")
        with open(temp_path, "wb") as f:
            f.write(b"test")

        stream = open(temp_path, "rb")
        assert not stream.closed
        stream.close()
        assert stream.closed
