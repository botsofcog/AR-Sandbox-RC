#!/usr/bin/env python3
"""
Smart Webcam AR Sandbox Integration
Replaces broken Kinect with intelligent webcam-based depth detection
Integrates with existing RC Sandbox system
"""

import asyncio
import websockets
import json
import cv2
import numpy as np
import time
import logging
from typing import Dict, Any, Optional
import threading
from queue import Queue

# Import our smart webcam depth estimator
from backend.smart_webcam_depth import SmartWebcamDepth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartWebcamSandbox:
    """
    Main integration class that connects smart webcam depth estimation
    to the RC Sandbox system
    """
    
    def __init__(self, camera_id: int = 0, websocket_port: int = 8765):
        self.camera_id = camera_id
        self.websocket_port = websocket_port
        self.depth_estimator = SmartWebcamDepth(camera_id)
        self.clients = set()
        self.running = False
        self.frame_count = 0
        
        # Performance monitoring
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        # Calibration state
        self.is_calibrated = False
        self.auto_calibration_frames = 0
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"📱 Client connected: {websocket.remote_address}")
        
        # Send initial status
        await websocket.send(json.dumps({
            'type': 'status',
            'message': 'Smart Webcam Sandbox Connected',
            'calibrated': self.is_calibrated,
            'camera_id': self.camera_id
        }))
        
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            logger.info(f"📱 Client disconnected: {websocket.remote_address}")
    
    async def broadcast_terrain_data(self, terrain_data: Dict[str, Any]):
        """Broadcast terrain data to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps(terrain_data)
        disconnected_clients = []
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                logger.warning(f"⚠️ Error sending to client: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.discard(client)
    
    async def handle_client_message(self, websocket, message):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            command = data.get('command', '')
            
            if command == 'calibrate':
                await self.perform_calibration()
                await websocket.send(json.dumps({
                    'type': 'calibration_result',
                    'success': self.is_calibrated
                }))
            
            elif command == 'get_debug_view':
                debug_img = self.depth_estimator.get_debug_visualization()
                if debug_img is not None:
                    # Encode debug image as base64 for web transmission
                    _, buffer = cv2.imencode('.jpg', debug_img)
                    import base64
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    await websocket.send(json.dumps({
                        'type': 'debug_image',
                        'image': img_base64
                    }))
            
            elif command == 'adjust_weights':
                weights = data.get('weights', {})
                self.depth_estimator.technique_weights.update(weights)
                logger.info(f"🎛️ Updated technique weights: {weights}")
        
        except json.JSONDecodeError:
            logger.warning("⚠️ Invalid JSON received from client")
        except Exception as e:
            logger.error(f"❌ Error handling client message: {e}")
    
    async def perform_calibration(self):
        """Perform sandbox calibration"""
        logger.info("🎯 Starting automatic calibration...")
        
        if self.depth_estimator.calibrate_sandbox():
            self.is_calibrated = True
            logger.info("✅ Calibration successful!")
            
            # Broadcast calibration success to all clients
            await self.broadcast_terrain_data({
                'type': 'calibration_complete',
                'timestamp': time.time(),
                'success': True
            })
        else:
            logger.error("❌ Calibration failed!")
            await self.broadcast_terrain_data({
                'type': 'calibration_complete',
                'timestamp': time.time(),
                'success': False
            })
    
    def update_fps_counter(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    async def terrain_streaming_loop(self):
        """Main loop for streaming terrain data"""
        logger.info("🌊 Starting terrain streaming loop...")
        
        while self.running:
            try:
                # Get terrain data from smart webcam
                terrain_data = self.depth_estimator.get_terrain_mesh_data()
                
                if terrain_data:
                    # Add performance metrics
                    terrain_data['fps'] = self.current_fps
                    terrain_data['frame_count'] = self.frame_count
                    terrain_data['calibrated'] = self.is_calibrated
                    
                    # Broadcast to all clients
                    await self.broadcast_terrain_data(terrain_data)
                    
                    self.frame_count += 1
                    self.update_fps_counter()
                    
                    # Auto-calibration if not calibrated
                    if not self.is_calibrated:
                        self.auto_calibration_frames += 1
                        if self.auto_calibration_frames >= 100:  # Auto-calibrate after 100 frames
                            await self.perform_calibration()
                            self.auto_calibration_frames = 0
                
                # Adaptive frame rate (target 15-30 FPS)
                await asyncio.sleep(1/20)  # 20 FPS max
                
            except Exception as e:
                logger.error(f"❌ Error in terrain streaming loop: {e}")
                await asyncio.sleep(0.1)
    
    async def start_server(self):
        """Start the WebSocket server and terrain streaming"""
        logger.info(f"🚀 Starting Smart Webcam Sandbox Server on port {self.websocket_port}")
        
        # Initialize camera
        if not self.depth_estimator.initialize_camera():
            logger.error("❌ Failed to initialize camera")
            return False
        
        self.running = True
        
        # Start WebSocket server
        server = await websockets.serve(
            self.register_client,
            "localhost",
            self.websocket_port
        )
        
        logger.info(f"✅ WebSocket server started on ws://localhost:{self.websocket_port}")
        
        # Start terrain streaming in background
        streaming_task = asyncio.create_task(self.terrain_streaming_loop())
        
        try:
            # Wait for server to run
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("🛑 Server interrupted by user")
        finally:
            self.running = False
            streaming_task.cancel()
            self.depth_estimator.cleanup()
            logger.info("🧹 Server cleanup completed")
        
        return True
    
    def run_interactive_demo(self):
        """Run an interactive demo with OpenCV windows"""
        logger.info("🎮 Starting interactive demo mode")
        
        if not self.depth_estimator.initialize_camera():
            logger.error("❌ Failed to initialize camera")
            return
        
        print("\n🎮 SMART WEBCAM SANDBOX DEMO")
        print("Controls:")
        print("  'c' - Calibrate sandbox")
        print("  'd' - Toggle debug view")
        print("  's' - Save current terrain")
        print("  'r' - Reset calibration")
        print("  'q' - Quit")
        print("\nMove objects in the sandbox to see real-time topography!")
        
        show_debug = False
        
        try:
            while True:
                # Get terrain data
                terrain_data = self.depth_estimator.get_terrain_mesh_data()
                
                if terrain_data:
                    # Create visualization
                    terrain_array = np.array(terrain_data['data']).reshape(
                        terrain_data['height'], terrain_data['width']
                    )
                    
                    # Convert to color map for visualization
                    terrain_colored = cv2.applyColorMap(
                        cv2.normalize(terrain_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
                        cv2.COLORMAP_TERRAIN
                    )
                    
                    # Resize for better viewing
                    terrain_display = cv2.resize(terrain_colored, (800, 600))
                    
                    # Add info overlay
                    info_text = [
                        f"FPS: {self.current_fps}",
                        f"Calibrated: {'Yes' if self.is_calibrated else 'No'}",
                        f"Height Range: {terrain_data['min_height']:.1f}-{terrain_data['max_height']:.1f}",
                        f"Techniques: {', '.join(terrain_data['techniques_used'])}"
                    ]
                    
                    for i, text in enumerate(info_text):
                        cv2.putText(terrain_display, text, (10, 30 + i * 25), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    cv2.imshow("Smart Webcam Sandbox - Terrain", terrain_display)
                    
                    self.update_fps_counter()
                
                # Show debug view if requested
                if show_debug:
                    debug_img = self.depth_estimator.get_debug_visualization()
                    if debug_img is not None:
                        cv2.imshow("Debug View", debug_img)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('c'):
                    print("🎯 Calibrating...")
                    if self.depth_estimator.calibrate_sandbox():
                        self.is_calibrated = True
                        print("✅ Calibration successful!")
                    else:
                        print("❌ Calibration failed!")
                
                elif key == ord('d'):
                    show_debug = not show_debug
                    if not show_debug:
                        cv2.destroyWindow("Debug View")
                    print(f"🔍 Debug view: {'ON' if show_debug else 'OFF'}")
                
                elif key == ord('s'):
                    if terrain_data:
                        filename = f"terrain_capture_{int(time.time())}.json"
                        with open(filename, 'w') as f:
                            json.dump(terrain_data, f, indent=2)
                        print(f"💾 Terrain saved to {filename}")
                
                elif key == ord('r'):
                    self.is_calibrated = False
                    self.depth_estimator.background_model = None
                    print("🔄 Calibration reset")
                
                elif key == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        
        finally:
            self.depth_estimator.cleanup()
            print("🧹 Demo cleanup completed")


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Webcam AR Sandbox")
    parser.add_argument("--mode", choices=["server", "demo"], default="demo",
                       help="Run mode: server (WebSocket) or demo (interactive)")
    parser.add_argument("--camera", type=int, default=0,
                       help="Camera ID (default: 0)")
    parser.add_argument("--port", type=int, default=8765,
                       help="WebSocket port (default: 8765)")
    
    args = parser.parse_args()
    
    sandbox = SmartWebcamSandbox(camera_id=args.camera, websocket_port=args.port)
    
    if args.mode == "server":
        print("🌐 Starting WebSocket server mode...")
        asyncio.run(sandbox.start_server())
    else:
        print("🎮 Starting interactive demo mode...")
        sandbox.run_interactive_demo()
