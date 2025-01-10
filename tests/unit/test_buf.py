"""Unit tests for buffer utilities."""

import pytest

from src.utils.buf_utils import Buffer, BufferOverflowError


def test_buffer_creation():
    """Test buffer initialization."""
    buf = Buffer(size=10)
    assert buf.size == 10
    assert len(buf.data) == 10
    assert buf.position == 0


def test_buffer_write():
    """Test writing to buffer."""
    buf = Buffer(size=10)
    data = b"Hello"
    buf.write(data)
    assert buf.position == 5
    assert buf.read() == b"Hello"


def test_buffer_overflow():
    """Test buffer overflow handling."""
    buf = Buffer(size=5)
    with pytest.raises(BufferOverflowError):
        buf.write(b"Too long data")


def test_buffer_read():
    """Test reading from buffer."""
    buf = Buffer(size=10)
    buf.write(b"Hello")
    assert buf.read(3) == b"Hel"
    assert buf.read() == b"Hello"
