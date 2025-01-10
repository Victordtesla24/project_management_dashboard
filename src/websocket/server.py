"""WebSocket server module."""
import asyncio
import json
import logging
from pathlib import Path

import websockets  # type: ignore

logger = logging.getLogger(__name__)

async def send_metrics(websocket):
    """Send metrics to connected clients."""
    metrics_dir = Path("metrics")
    while True:
        try:
            system_metrics = json.loads((metrics_dir / "system_metrics.json").read_text())
            process_metrics = json.loads((metrics_dir / "process_metrics.json").read_text())
            await websocket.send(
                json.dumps({
                    "system": system_metrics,
                    "processes": process_metrics,
                }),
            )
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")
            await asyncio.sleep(5)

async def main():
    """Main function to run WebSocket server."""
    logger.info("Starting WebSocket server")
    async with websockets.serve(send_metrics, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
