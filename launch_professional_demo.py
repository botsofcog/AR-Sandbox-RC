#!/usr/bin/env python3
"""
RC Sandbox - Professional AR Demo Launcher
Implements the actual AR sandbox system per specifications
"""

import asyncio
import websockets
import json
import cv2
import numpy as np
import time
import threading
import logging
from pathlib import Path
import webbrowser
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DepthSensorSimulator:
    """Simulates Kinect depth sensor for demo purposes"""
    
    def __init__(self):
        self.cap = None
        self.running = False
        self.frame_count = 0
        
    def initialize(self):
        """Initialize webcam as depth sensor simulator"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Failed to open webcam")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            logger.info("Depth sensor simulator initialized")
            return True
        except Exception as e:
            logger.error(f"Depth sensor initialization failed: {e}")
            return False
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Get simulated depth frame from webcam"""
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Convert to grayscale and simulate depth
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply some processing to simulate depth data
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        depth_sim = cv2.subtract(255, blurred)  # Invert for depth-like appearance
        
        self.frame_count += 1
        return depth_sim
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()

class TerrainProcessor:
    """Processes depth data into terrain mesh"""
    
    def __init__(self, mesh_width=100, mesh_height=75):
        self.mesh_width = mesh_width
        self.mesh_height = mesh_height
        self.calibration_offset = 0
        
    def process_depth_to_terrain(self, depth_frame: np.ndarray) -> Dict[str, Any]:
        """Convert depth frame to terrain mesh data"""
        if depth_frame is None:
            return None
            
        # Resize to mesh resolution
        resized = cv2.resize(depth_frame, (self.mesh_width, self.mesh_height))
        
        # Apply calibration and filtering
        filtered = cv2.medianBlur(resized, 5)
        
        # Normalize to height values
        normalized = cv2.normalize(filtered, None, 0, 100, cv2.NORM_MINMAX)
        
        return {
            'type': 'terrain_mesh',
            'timestamp': time.time(),
            'width': self.mesh_width,
            'height': self.mesh_height,
            'data': normalized.flatten().tolist(),
            'min_height': float(np.min(normalized)),
            'max_height': float(np.max(normalized))
        }

class RCVehicleSimulator:
    """Simulates RC vehicle telemetry"""
    
    def __init__(self):
        self.vehicles = {
            'EX001': {'type': 'excavator', 'x': 50, 'y': 37, 'rotation': 0, 'speed': 0},
            'BD001': {'type': 'bulldozer', 'x': 30, 'y': 20, 'rotation': 45, 'speed': 2},
            'DT001': {'type': 'dump_truck', 'x': 70, 'y': 55, 'rotation': 180, 'speed': 1},
        }
        
    def get_telemetry(self) -> Dict[str, Any]:
        """Get simulated vehicle telemetry"""
        # Simulate some movement
        for vehicle_id, data in self.vehicles.items():
            data['x'] += np.random.uniform(-0.5, 0.5)
            data['y'] += np.random.uniform(-0.5, 0.5)
            data['rotation'] += np.random.uniform(-2, 2)
            
            # Keep in bounds
            data['x'] = np.clip(data['x'], 0, 100)
            data['y'] = np.clip(data['y'], 0, 75)
            data['rotation'] = data['rotation'] % 360
            
        return {
            'type': 'vehicle_telemetry',
            'timestamp': time.time(),
            'vehicles': self.vehicles
        }

class ARSandboxServer:
    """Main AR Sandbox WebSocket server"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.running = False
        
        # Initialize components
        self.depth_sensor = DepthSensorSimulator()
        self.terrain_processor = TerrainProcessor()
        self.vehicle_simulator = RCVehicleSimulator()
        
    async def register_client(self, websocket):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")

        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def broadcast_data(self, data):
        """Broadcast data to all connected clients"""
        if self.clients:
            message = json.dumps(data)
            disconnected = set()
            
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected
    
    async def data_loop(self):
        """Main data processing loop"""
        logger.info("Starting data processing loop")
        
        while self.running:
            try:
                # Get depth frame and process terrain
                depth_frame = self.depth_sensor.get_depth_frame()
                if depth_frame is not None:
                    terrain_data = self.terrain_processor.process_depth_to_terrain(depth_frame)
                    if terrain_data:
                        await self.broadcast_data(terrain_data)
                
                # Get vehicle telemetry
                vehicle_data = self.vehicle_simulator.get_telemetry()
                await self.broadcast_data(vehicle_data)
                
                # Control frame rate (30 FPS)
                await asyncio.sleep(1/30)
                
            except Exception as e:
                logger.error(f"Error in data loop: {e}")
                await asyncio.sleep(0.1)
    
    async def start_server(self):
        """Start the WebSocket server"""
        if not self.depth_sensor.initialize():
            logger.error("Failed to initialize depth sensor")
            return False
            
        self.running = True
        
        # Start WebSocket server
        server = await websockets.serve(self.register_client, self.host, self.port)
        logger.info(f"AR Sandbox server started on ws://{self.host}:{self.port}")
        
        # Start data processing loop
        data_task = asyncio.create_task(self.data_loop())
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        finally:
            self.running = False
            data_task.cancel()
            self.depth_sensor.cleanup()
    
    def run(self):
        """Run the server"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")

def create_frontend_html():
    """Create the AR sandbox frontend HTML"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RC Sandbox - Professional AR System</title>
    <style>
        body { margin: 0; background: #000; font-family: Arial, sans-serif; }
        #container { position: relative; width: 100vw; height: 100vh; }
        #terrain-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        .hud { position: absolute; background: rgba(30,30,30,0.8); color: white; padding: 10px; border-radius: 5px; }
        #status { top: 20px; left: 20px; }
        #vehicles { top: 20px; right: 20px; }
        .vehicle { margin: 5px 0; padding: 5px; background: rgba(0,100,0,0.3); border-radius: 3px; }
    </style>
</head>
<body>
    <div id="container">
        <canvas id="terrain-canvas"></canvas>
        <div id="status" class="hud">
            <h3>🏗️ RC Sandbox Status</h3>
            <div>Connection: <span id="connection-status">Connecting...</span></div>
            <div>Terrain Updates: <span id="terrain-updates">0</span></div>
            <div>FPS: <span id="fps">0</span></div>
        </div>
        <div id="vehicles" class="hud">
            <h3>🚛 RC Vehicles</h3>
            <div id="vehicle-list"></div>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('terrain-canvas');
        const ctx = canvas.getContext('2d');
        let terrainData = null;
        let vehicleData = null;
        let frameCount = 0;
        let lastTime = Date.now();
        
        // Resize canvas
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onopen = () => {
            document.getElementById('connection-status').textContent = 'Connected';
            console.log('Connected to AR Sandbox server');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'terrain_mesh') {
                terrainData = data;
                document.getElementById('terrain-updates').textContent = parseInt(document.getElementById('terrain-updates').textContent) + 1;
            } else if (data.type === 'vehicle_telemetry') {
                vehicleData = data;
                updateVehicleDisplay();
            }
        };
        
        ws.onclose = () => {
            document.getElementById('connection-status').textContent = 'Disconnected';
        };
        
        // Render terrain
        function renderTerrain() {
            if (!terrainData) return;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const cellW = canvas.width / terrainData.width;
            const cellH = canvas.height / terrainData.height;
            
            for (let y = 0; y < terrainData.height; y++) {
                for (let x = 0; x < terrainData.width; x++) {
                    const idx = y * terrainData.width + x;
                    const height = terrainData.data[idx];
                    
                    // Color based on height (topographic)
                    let color;
                    if (height < 20) {
                        color = `rgb(0, ${100 + height * 3}, 255)`; // Water/low
                    } else if (height < 40) {
                        color = `rgb(${194}, ${178}, 128)`; // Sand
                    } else if (height < 60) {
                        color = `rgb(34, ${139}, 34)`; // Grass
                    } else {
                        color = `rgb(${139}, 69, 19)`; // Rock
                    }
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
                }
            }
            
            // Render vehicles
            if (vehicleData) {
                for (const [id, vehicle] of Object.entries(vehicleData.vehicles)) {
                    const x = (vehicle.x / 100) * canvas.width;
                    const y = (vehicle.y / 75) * canvas.height;
                    
                    ctx.fillStyle = '#FF0000';
                    ctx.fillRect(x - 5, y - 5, 10, 10);
                    
                    ctx.fillStyle = '#FFFFFF';
                    ctx.font = '12px Arial';
                    ctx.fillText(id, x + 8, y + 4);
                }
            }
        }
        
        // Update vehicle display
        function updateVehicleDisplay() {
            if (!vehicleData) return;
            
            const list = document.getElementById('vehicle-list');
            list.innerHTML = '';
            
            for (const [id, vehicle] of Object.entries(vehicleData.vehicles)) {
                const div = document.createElement('div');
                div.className = 'vehicle';
                div.innerHTML = `
                    <strong>${id}</strong> (${vehicle.type})<br>
                    Position: ${vehicle.x.toFixed(1)}, ${vehicle.y.toFixed(1)}<br>
                    Speed: ${vehicle.speed} | Rotation: ${vehicle.rotation.toFixed(0)}°
                `;
                list.appendChild(div);
            }
        }
        
        // Animation loop
        function animate() {
            renderTerrain();
            
            frameCount++;
            const now = Date.now();
            if (now - lastTime >= 1000) {
                document.getElementById('fps').textContent = frameCount;
                frameCount = 0;
                lastTime = now;
            }
            
            requestAnimationFrame(animate);
        }
        
        animate();
        console.log('🏗️ RC Sandbox Professional AR System loaded');
    </script>
</body>
</html>'''
    
    with open('ar_sandbox_frontend.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return Path('ar_sandbox_frontend.html').absolute()

def main():
    """Main launcher function"""
    print("🏗️ RC SANDBOX - PROFESSIONAL AR DEMO")
    print("=" * 50)
    print()
    print("Starting AR Sandbox system with:")
    print("• Depth sensor simulation (webcam)")
    print("• Real-time terrain processing")
    print("• RC vehicle telemetry")
    print("• WebSocket architecture")
    print("• Professional visualization")
    print()
    
    # Create frontend
    frontend_path = create_frontend_html()
    
    # Start server in background
    server = ARSandboxServer()
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open frontend
    print(f"🌐 Opening AR Sandbox frontend...")
    webbrowser.open(frontend_path.as_uri())
    
    print("✅ AR Sandbox system is running!")
    print("📊 Check the browser for real-time terrain and vehicle data")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AR Sandbox system...")

if __name__ == "__main__":
    main()
