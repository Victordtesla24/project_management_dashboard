import asyncio
import websockets
import json
import jwt
from typing import Set, Dict, Any
from ..config import get_config
from ..metrics import collect_system_metrics, process_metrics
from ..auth.middleware import verify_token

class MetricsWebSocket:
    """WebSocket server for metrics."""
    
    def __init__(self, config_path: str = None):
        """Initialize WebSocket server."""
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.config = get_config()
        self.running = False
        self.server = None
        self.collection_task = None
    
    async def start_server(self):
        """Start WebSocket server."""
        config = self.config['websocket']
        ssl_context = None
        if config.get('ssl'):
            # SSL configuration would go here if needed
            pass
            
        self.server = await websockets.serve(
            self.handle_client,
            config['host'],
            config['port'],
            ssl=ssl_context
        )
        self.running = True
        self.collection_task = asyncio.create_task(self.collect_metrics_loop())
        return self.server
    
    async def stop_server(self):
        """Stop WebSocket server."""
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            await client.close()
        self.clients.clear()
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle client connection with authentication."""
        try:
            # Get token from query parameters
            query = websocket.path.split('?')[-1]
            params = dict(param.split('=') for param in query.split('&') if '=' in param)
            token = params.get('token')
            
            if not token:
                await websocket.close(1008, "Missing authentication token")
                return
                
            try:
                # Verify JWT token
                payload = verify_token(token)
                if not payload:
                    await websocket.close(1008, "Invalid authentication token")
                    return
            except jwt.InvalidTokenError:
                await websocket.close(1008, "Invalid authentication token")
                return
            except Exception as e:
                await websocket.close(1011, f"Authentication error: {str(e)}")
                return
            
            await self.register_client(websocket)
            await self.send_initial_data(websocket)
            
            try:
                async for message in websocket:
                    try:
                        # Parse and validate incoming messages
                        data = json.loads(message)
                        if 'type' in data:
                            await self.handle_message(websocket, data)
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({
                            'error': 'Invalid JSON format'
                        }))
                    except Exception as e:
                        await websocket.send(json.dumps({
                            'error': f'Message handling error: {str(e)}'
                        }))
            except websockets.ConnectionClosed:
                pass
            finally:
                await self.unregister_client(websocket)
        except Exception as e:
            print(f"Error handling client: {e}")
            if websocket in self.clients:
                await self.unregister_client(websocket)
                
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: Dict):
        """Handle incoming messages from clients."""
        message_type = message.get('type')
        
        if message_type == 'ping':
            await websocket.send(json.dumps({'type': 'pong'}))
        elif message_type == 'subscribe':
            # Handle metric subscription
            metrics = message.get('metrics', [])
            if not isinstance(metrics, list):
                await websocket.send(json.dumps({
                    'error': 'Invalid metrics format'
                }))
                return
            # Store client's metric preferences
            websocket.subscribed_metrics = set(metrics)
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client."""
        self.clients.add(websocket)
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client."""
        if websocket in self.clients:
            self.clients.remove(websocket)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all clients."""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except websockets.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
    
    async def collect_metrics_loop(self):
        """Collect and broadcast metrics periodically."""
        while self.running:
            try:
                metrics = collect_system_metrics()
                processed = process_metrics(metrics)
                await self.broadcast_message(processed)
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(self.config['metrics']['collection_interval'])
    
    async def send_initial_data(self, websocket: websockets.WebSocketServerProtocol):
        """Send initial data to new client."""
        try:
            metrics = collect_system_metrics()
            processed = process_metrics(metrics)
            await websocket.send(json.dumps(processed))
        except Exception as e:
            print(f"Error sending initial data: {e}")
