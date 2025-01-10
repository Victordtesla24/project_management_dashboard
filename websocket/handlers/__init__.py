"""WebSocket handlers package."""


class WebSocketHandler:
    """Base WebSocket handler."""

    async def on_connect(self, websocket):
        """Handle client connection."""
        pass

    async def on_disconnect(self, websocket):
        """Handle client disconnection."""
        pass

    async def on_message(self, websocket, message):
        """Handle incoming message."""
        pass
