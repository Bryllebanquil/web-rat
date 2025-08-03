#!/usr/bin/env python3
"""
WebSocket Streaming Module
Ultra-low latency real-time video streaming via WebSockets
"""

import asyncio
import websockets
import json
import base64
import time
import threading
import logging
from typing import Set, Optional, Dict, Any
import queue

try:
    import uvloop
    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False

try:
    from high_performance_capture import HighPerformanceCapture
    HAS_HIGH_PERFORMANCE_CAPTURE = True
except ImportError:
    HAS_HIGH_PERFORMANCE_CAPTURE = False

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

class WebSocketStreamingServer:
    """High-performance WebSocket streaming server"""
    
    def __init__(self, host: str = "localhost", port: int = 8765, 
                 max_clients: int = 10, target_fps: int = 60):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.target_fps = target_fps
        
        # Client management
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_stats: Dict[str, Dict] = {}
        
        # Streaming components
        self.capture = None
        self.frame_queue = queue.Queue(maxsize=120)  # 2 seconds buffer at 60fps
        self.running = False
        
        # Performance tracking
        self.frames_sent = 0
        self.bytes_sent = 0
        self.start_time = time.time()
        
        logging.info(f"WebSocket streaming server initialized on {host}:{port}")
        logging.info(f"Target FPS: {target_fps}, Max clients: {max_clients}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        if HAS_UVLOOP and hasattr(asyncio, 'set_event_loop_policy'):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        self.running = True
        
        # Initialize capture system
        if HAS_HIGH_PERFORMANCE_CAPTURE:
            self.capture = HighPerformanceCapture(
                target_fps=self.target_fps, 
                quality=85, 
                enable_delta_compression=True
            )
            self.capture.start_capture_stream(self._frame_callback)
            logging.info("High-performance capture started")
        else:
            logging.warning("High-performance capture not available")
            return
        
        # Start frame distribution task
        asyncio.create_task(self._distribute_frames())
        
        # Start the WebSocket server
        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            max_size=1024*1024*10,  # 10MB max message size
            ping_interval=20,
            ping_timeout=10,
            compression=None  # Disable compression for speed
        ):
            logging.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def _handle_client(self, websocket, path):
        """Handle new client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        
        if len(self.clients) >= self.max_clients:
            await websocket.close(code=1013, reason="Server full")
            return
        
        self.clients.add(websocket)
        self.client_stats[client_id] = {
            'connected_at': time.time(),
            'frames_sent': 0,
            'bytes_sent': 0,
            'last_activity': time.time()
        }
        
        logging.info(f"Client connected: {client_id} (total: {len(self.clients)})")
        
        try:
            # Send initial connection message
            await self._send_to_client(websocket, {
                'type': 'connection',
                'message': 'Connected to high-performance stream',
                'fps': self.target_fps,
                'features': {
                    'high_performance_capture': HAS_HIGH_PERFORMANCE_CAPTURE,
                    'msgpack': HAS_MSGPACK,
                    'uvloop': HAS_UVLOOP
                }
            })
            
            # Handle client messages
            async for message in websocket:
                await self._handle_client_message(websocket, client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logging.error(f"Client error {client_id}: {e}")
        finally:
            self.clients.discard(websocket)
            self.client_stats.pop(client_id, None)
            logging.info(f"Client removed: {client_id} (remaining: {len(self.clients)})")
    
    async def _handle_client_message(self, websocket, client_id: str, message: str):
        """Handle incoming client messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'ping':
                await self._send_to_client(websocket, {'type': 'pong', 'timestamp': time.time()})
            elif msg_type == 'stats_request':
                stats = self._get_server_stats()
                await self._send_to_client(websocket, {'type': 'stats', 'data': stats})
            elif msg_type == 'quality_change':
                new_quality = data.get('quality', 85)
                if self.capture:
                    self.capture.set_quality(new_quality)
                await self._send_to_client(websocket, {
                    'type': 'quality_changed', 
                    'quality': new_quality
                })
            
            # Update client activity
            self.client_stats[client_id]['last_activity'] = time.time()
            
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON from client {client_id}")
        except Exception as e:
            logging.error(f"Error handling message from {client_id}: {e}")
    
    def _frame_callback(self, frame_data: bytes):
        """Callback for captured frames"""
        if frame_data and frame_data != b'DELTA_UNCHANGED':
            try:
                # Add frame to queue (non-blocking)
                if not self.frame_queue.full():
                    self.frame_queue.put_nowait({
                        'data': frame_data,
                        'timestamp': time.time()
                    })
                else:
                    # Drop oldest frame if queue is full
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait({
                            'data': frame_data,
                            'timestamp': time.time()
                        })
                    except queue.Empty:
                        pass
            except Exception as e:
                logging.error(f"Frame callback error: {e}")
    
    async def _distribute_frames(self):
        """Distribute frames to all connected clients"""
        while self.running:
            try:
                # Get frame from queue (non-blocking)
                try:
                    frame_data = self.frame_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.001)  # 1ms sleep
                    continue
                
                if not self.clients:
                    continue
                
                # Prepare frame message
                frame_message = {
                    'type': 'frame',
                    'timestamp': frame_data['timestamp'],
                    'data': base64.b64encode(frame_data['data']).decode('utf-8')
                }
                
                # Handle different frame types
                if frame_data['data'].startswith(b'LZ4_COMPRESSED'):
                    frame_message['encoding'] = 'lz4'
                    frame_message['data'] = base64.b64encode(frame_data['data'][14:]).decode('utf-8')
                
                # Send to all clients concurrently
                tasks = []
                for client in list(self.clients):  # Create a copy to avoid modification during iteration
                    tasks.append(self._send_frame_to_client(client, frame_message))
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                self.frames_sent += 1
                self.bytes_sent += len(frame_data['data'])
                
            except Exception as e:
                logging.error(f"Frame distribution error: {e}")
                await asyncio.sleep(0.01)
    
    async def _send_frame_to_client(self, websocket, frame_message: Dict):
        """Send frame to a specific client"""
        try:
            if websocket in self.clients:
                if HAS_MSGPACK:
                    # Use MessagePack for better performance
                    data = msgpack.packb(frame_message)
                    await websocket.send(data)
                else:
                    # Fallback to JSON
                    await websocket.send(json.dumps(frame_message))
                
                # Update client stats
                client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                if client_id in self.client_stats:
                    self.client_stats[client_id]['frames_sent'] += 1
                    self.client_stats[client_id]['bytes_sent'] += len(frame_message.get('data', ''))
                    
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            logging.error(f"Error sending frame to client: {e}")
    
    async def _send_to_client(self, websocket, message: Dict):
        """Send a message to a specific client"""
        try:
            if HAS_MSGPACK:
                data = msgpack.packb(message)
                await websocket.send(data)
            else:
                await websocket.send(json.dumps(message))
        except Exception as e:
            logging.error(f"Error sending message to client: {e}")
    
    def _get_server_stats(self) -> Dict[str, Any]:
        """Get server performance statistics"""
        uptime = time.time() - self.start_time
        avg_fps = self.frames_sent / uptime if uptime > 0 else 0
        avg_bandwidth = self.bytes_sent / uptime if uptime > 0 else 0
        
        capture_stats = {}
        if self.capture:
            capture_stats = self.capture.get_stats()
        
        return {
            'uptime': uptime,
            'connected_clients': len(self.clients),
            'frames_sent': self.frames_sent,
            'bytes_sent': self.bytes_sent,
            'avg_fps': avg_fps,
            'avg_bandwidth': avg_bandwidth,
            'frame_queue_size': self.frame_queue.qsize(),
            'capture_stats': capture_stats,
            'client_stats': self.client_stats
        }
    
    def stop_server(self):
        """Stop the streaming server"""
        self.running = False
        if self.capture:
            self.capture.stop_capture_stream()
        logging.info("WebSocket streaming server stopped")


class WebSocketStreamingClient:
    """High-performance WebSocket streaming client"""
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.running = False
        self.frame_callback = None
        
        # Performance tracking
        self.frames_received = 0
        self.bytes_received = 0
        self.start_time = time.time()
        
        logging.info(f"WebSocket streaming client initialized for {uri}")
    
    async def connect(self, frame_callback=None):
        """Connect to the streaming server"""
        self.frame_callback = frame_callback
        self.running = True
        
        try:
            async with websockets.connect(
                self.uri,
                max_size=1024*1024*10,  # 10MB max message size
                ping_interval=20,
                ping_timeout=10,
                compression=None
            ) as websocket:
                self.websocket = websocket
                logging.info(f"Connected to streaming server: {self.uri}")
                
                # Handle incoming messages
                async for message in websocket:
                    await self._handle_message(message)
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info("Disconnected from streaming server")
        except Exception as e:
            logging.error(f"Connection error: {e}")
        finally:
            self.running = False
    
    async def _handle_message(self, message):
        """Handle incoming messages from server"""
        try:
            # Try MessagePack first, then JSON
            if HAS_MSGPACK and isinstance(message, bytes):
                data = msgpack.unpackb(message, raw=False)
            else:
                data = json.loads(message)
            
            msg_type = data.get('type')
            
            if msg_type == 'frame' and self.frame_callback:
                # Decode frame data
                frame_data = base64.b64decode(data['data'])
                
                # Handle compressed frames
                if data.get('encoding') == 'lz4':
                    frame_data = b'LZ4_COMPRESSED' + frame_data
                
                # Call frame callback
                await self.frame_callback(frame_data, data.get('timestamp', time.time()))
                
                self.frames_received += 1
                self.bytes_received += len(frame_data)
                
            elif msg_type == 'connection':
                logging.info(f"Server connection: {data.get('message')}")
                logging.info(f"Server features: {data.get('features', {})}")
                
            elif msg_type == 'stats':
                logging.info(f"Server stats: {data.get('data', {})}")
            
        except Exception as e:
            logging.error(f"Error handling message: {e}")
    
    async def send_message(self, message: Dict):
        """Send a message to the server"""
        try:
            if self.websocket:
                if HAS_MSGPACK:
                    data = msgpack.packb(message)
                    await self.websocket.send(data)
                else:
                    await self.websocket.send(json.dumps(message))
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    async def request_stats(self):
        """Request server statistics"""
        await self.send_message({'type': 'stats_request'})
    
    async def change_quality(self, quality: int):
        """Request quality change"""
        await self.send_message({'type': 'quality_change', 'quality': quality})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        uptime = time.time() - self.start_time
        avg_fps = self.frames_received / uptime if uptime > 0 else 0
        avg_bandwidth = self.bytes_received / uptime if uptime > 0 else 0
        
        return {
            'uptime': uptime,
            'frames_received': self.frames_received,
            'bytes_received': self.bytes_received,
            'avg_fps': avg_fps,
            'avg_bandwidth': avg_bandwidth,
            'connected': self.running
        }


# HTML client template for testing
HTML_CLIENT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>High-Performance WebSocket Stream</title>
    <style>
        body { margin: 0; background: #000; font-family: Arial, sans-serif; }
        #stream { width: 100%; height: auto; max-width: 100vw; }
        #stats { position: fixed; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.7); padding: 10px; }
        #controls { position: fixed; top: 10px; right: 10px; color: white; }
        button { margin: 5px; padding: 5px 10px; }
    </style>
</head>
<body>
    <img id="stream" alt="Video Stream">
    <div id="stats">
        <div>FPS: <span id="fps">0</span></div>
        <div>Latency: <span id="latency">0</span>ms</div>
        <div>Quality: <span id="quality">85</span></div>
    </div>
    <div id="controls">
        <button onclick="changeQuality(-10)">Quality -</button>
        <button onclick="changeQuality(10)">Quality +</button>
        <button onclick="requestStats()">Stats</button>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:8765');
        const streamImg = document.getElementById('stream');
        const fpsSpan = document.getElementById('fps');
        const latencySpan = document.getElementById('latency');
        const qualitySpan = document.getElementById('quality');
        
        let frameCount = 0;
        let startTime = Date.now();
        let currentQuality = 85;
        
        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'frame') {
                    // Update stream
                    streamImg.src = 'data:image/jpeg;base64,' + data.data;
                    
                    // Calculate FPS and latency
                    frameCount++;
                    const now = Date.now();
                    const elapsed = (now - startTime) / 1000;
                    const fps = Math.round(frameCount / elapsed);
                    const latency = Math.round(now - (data.timestamp * 1000));
                    
                    fpsSpan.textContent = fps;
                    latencySpan.textContent = latency;
                    
                } else if (data.type === 'quality_changed') {
                    currentQuality = data.quality;
                    qualitySpan.textContent = currentQuality;
                } else if (data.type === 'connection') {
                    console.log('Connected:', data.message);
                }
            } catch (e) {
                console.error('Message handling error:', e);
            }
        };
        
        function changeQuality(delta) {
            currentQuality = Math.max(10, Math.min(100, currentQuality + delta));
            ws.send(JSON.stringify({type: 'quality_change', quality: currentQuality}));
        }
        
        function requestStats() {
            ws.send(JSON.stringify({type: 'stats_request'}));
        }
        
        // Periodic ping
        setInterval(() => {
            ws.send(JSON.stringify({type: 'ping'}));
        }, 5000);
    </script>
</body>
</html>
"""

def create_html_client(filename: str = "stream_client.html"):
    """Create an HTML client file for testing"""
    with open(filename, 'w') as f:
        f.write(HTML_CLIENT_TEMPLATE)
    logging.info(f"HTML client created: {filename}")


if __name__ == "__main__":
    # Test the WebSocket streaming
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    async def main():
        # Create HTML client for testing
        create_html_client()
        
        # Start server
        server = WebSocketStreamingServer(host="localhost", port=8765, target_fps=60)
        
        print("Starting WebSocket streaming server...")
        print("Open stream_client.html in your browser to view the stream")
        print("Press Ctrl+C to stop")
        
        try:
            await server.start_server()
        except KeyboardInterrupt:
            print("\nStopping server...")
            server.stop_server()
    
    asyncio.run(main())