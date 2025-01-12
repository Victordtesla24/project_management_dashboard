"""Buffer utility functions."""


class Buffer:
    """Simple buffer implementation."""

    def __init__(self, size=1024) -> None:
        """Initialize buffer with given size."""
        self.size = size
        self.data = bytearray(size)
        self.position = 0

    def write(self, data):
        """Write data to buffer."""
        if self.position + len(data) > self.size:
            msg = "Buffer full"
            raise BufferOverflowError(msg)
        self.data[self.position : self.position + len(data)] = data
        self.position += len(data)

    def read(self, size=None):
        """Read data from buffer."""
        if size is None:
            size = self.position
        if size > self.position:
            size = self.position
        return bytes(self.data[:size])


class BufferOverflowError(Exception):
    """Raised when buffer is full."""
