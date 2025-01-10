"""WebSocket middleware package."""


class WebSocketMiddleware:
    """Base WebSocket middleware."""

    async def process_request(self, websocket, next_handler):
        """Process incoming request."""
        return await next_handler(websocket)

    async def process_message(self, websocket, message, next_handler):
        """Process incoming message."""
        return await next_handler(websocket, message)
