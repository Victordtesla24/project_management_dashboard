"""\1"""


class WebSocketMiddleware:
    """\1"""
    async def process_request(self, websocket, next_handler):
        """\1"""
        return await next_handler(websocket)

    async def process_message(self, websocket, message, next_handler):
        """\1"""
        return await next_handler(websocket, message)
