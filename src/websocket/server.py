import asyncio
import json
import logging
from pathlib import Path

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket_server")


async def send_metrics(websocket):
    metrics_dir = Path("metrics")
    while True:
        try:
            system_metrics = json.loads((metrics_dir / "system_metrics.json").read_text())
            process_metrics = json.loads((metrics_dir / "process_metrics.json").read_text())

            await websocket.send(
                json.dumps({"system": system_metrics, "processes": process_metrics})
            )

            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")
            await asyncio.sleep(5)


async def main():
    logger.info("Starting WebSocket server")
    async with websockets.serve(send_metrics, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
