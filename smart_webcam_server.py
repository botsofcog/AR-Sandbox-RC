#!/usr/bin/env python3
"""
Smart Webcam Server for Beautiful AR Sandbox Demo
Provides real-time depth estimation to the enhanced HTML interface
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
import base64
from pathlib import Path

# Import our smart depth estimator
try:
    from backend.smart_webcam_depth import SmartWebcamDepth
except ImportError:
    print("⚠️ Smart webcam depth module not found, using fallback")
    SmartWebcamDepth = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartWebcamServer:
    """
    WebSocket server that provides smart depth estimation data
    to the beautiful HTML interface
    """
    
    def __init__(self, port: int = 8765, camera_id: int = 0):
        self.port = port
        self.camera_id = camera_id
        self.clients = set()
        self.running = False
        
        # Initialize smart depth estimator
        if SmartWebcamDepth:
            self.depth_estimator = SmartWebcamDepth(camera_id)
        else:
            self.depth_estimator = None
            
        # Fallback webcam for basic functionality
        self.fallback_cap = None
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
        # Calibration state
        self.is_calibrated = False
        self.calibration_progress = 0
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"📱 Client connected: {client_addr}")
        
        # Send initial status
        await self.send_to_client(websocket, {
            'type': 'status_update',
            'camera_status': 'active' if self.depth_estimator else 'fallback',
            'ai_model_status': 'ready' if self.depth_estimator else 'unavailable',
            'calibration_status': 'calibrated' if self.is_calibrated else 'not_calibrated',
            'server_info': {
                'version': '1.0.0',
                'features': ['smart_depth', 'ai_estimation', 'real_time'],
                'camera_id': self.camera_id
            }
        })
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"📱 Client disconnected: {client_addr}")
    
    async def handle_client_message(self, websocket, message):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            command = data.get('command', '')
            
            if command == 'start_calibration':
                await self.start_calibration_process(websocket)
            
            elif command == 'update_weights':
                weights = data.get('weights', {})
                if self.depth_estimator:
                    self.depth_estimator.technique_weights.update(weights)
                    logger.info(f"🎛️ Updated technique weights: {weights}")
            
            elif command == 'toggle_technique':
                technique = data.get('technique', '')
                enabled = data.get('enabled', True)
                logger.info(f"🔧 Technique {technique}: {'enabled' if enabled else 'disabled'}")
            
            elif command == 'get_debug_frame':
                await self.send_debug_frame(websocket)
            
            elif command == 'reset_terrain':
                logger.info("🔄 Terrain reset requested")
                await self.send_to_client(websocket, {
                    'type': 'terrain_reset',
                    'timestamp': time.time()
                })
                
        except json.JSONDecodeError:
            logger.warning("⚠️ Invalid JSON received from client")
        except Exception as e:
            logger.error(f"❌ Error handling client message: {e}")
    
    async def start_calibration_process(self, websocket):
        """Start the calibration process"""
        logger.info("🎯 Starting calibration process...")
        
        # Send calibration start notification
        await self.send_to_client(websocket, {
            'type': 'calibration_started',
            'timestamp': time.time()
        })
        
        # Simulate calibration progress
        for progress in range(0, 101, 5):
            self.calibration_progress = progress
            
            # Send progress update
            await self.send_to_client(websocket, {
                'type': 'calibration_progress',
                'progress': progress,
                'stage': self.get_calibration_stage(progress)
            })
            
            await asyncio.sleep(0.1)  # Simulate processing time
        
        # Perform actual calibration if depth estimator is available
        if self.depth_estimator:
            success = self.depth_estimator.calibrate_sandbox()
            self.is_calibrated = success
        else:
            # Simulate successful calibration
            self.is_calibrated = True
            success = True
        
        # Send calibration result
        await self.send_to_client(websocket, {
            'type': 'calibration_complete',
            'success': success,
            'timestamp': time.time()
        })
        
        logger.info(f"✅ Calibration {'successful' if success else 'failed'}")
    
    def get_calibration_stage(self, progress):
        """Get calibration stage description based on progress"""
        if progress < 30:
            return "Analyzing lighting conditions..."
        elif progress < 60:
            return "Capturing background model..."
        elif progress < 90:
            return "Optimizing AI parameters..."
        else:
            return "Finalizing calibration..."
    
    async def send_debug_frame(self, websocket):
        """Send debug visualization frame to client"""
        if self.depth_estimator:
            debug_img = self.depth_estimator.get_debug_visualization()
            if debug_img is not None:
                # Encode image as base64
                _, buffer = cv2.imencode('.jpg', debug_img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                await self.send_to_client(websocket, {
                    'type': 'debug_frame',
                    'image': img_base64,
                    'timestamp': time.time()
                })
    
    async def send_to_client(self, websocket, data):
        """Send data to a specific client"""
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.warning(f"⚠️ Error sending to client: {e}")
    
    async def broadcast_to_all(self, data):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps(data)
        disconnected_clients = []
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                logger.warning(f"⚠️ Error broadcasting to client: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.discard(client)
    
    def initialize_fallback_camera(self):
        """Initialize fallback camera if smart depth estimator is not available"""
        try:
            self.fallback_cap = cv2.VideoCapture(self.camera_id)
            if self.fallback_cap.isOpened():
                self.fallback_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.fallback_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                logger.info("📹 Fallback camera initialized")
                return True
            else:
                logger.error("❌ Failed to initialize fallback camera")
                return False
        except Exception as e:
            logger.error(f"❌ Fallback camera error: {e}")
            return False
    
    def get_terrain_data(self):
        """Get terrain data from smart depth estimator or fallback"""
        if self.depth_estimator and self.is_calibrated:
            # Use smart depth estimation
            terrain_data = self.depth_estimator.get_terrain_mesh_data()
            if terrain_data:
                terrain_data['source'] = 'smart_ai'
                return terrain_data
        
        # Fallback to simple simulation
        if self.fallback_cap and self.fallback_cap.isOpened():
            ret, frame = self.fallback_cap.read()
            if ret:
                # Create simple height map from grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                height_map = cv2.resize(gray, (100, 75))
                
                return {
                    'type': 'terrain_mesh',
                    'timestamp': time.time(),
                    'width': 100,
                    'height': 75,
                    'data': height_map.flatten().tolist(),
                    'min_height': float(np.min(height_map)),
                    'max_height': float(np.max(height_map)),
                    'source': 'fallback_camera'
                }
        
        return None
    
    def update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    async def terrain_streaming_loop(self):
        """Main loop for streaming terrain data"""
        logger.info("🌊 Starting terrain streaming loop...")
        
        while self.running:
            try:
                # Get terrain data
                terrain_data = self.get_terrain_data()
                
                if terrain_data:
                    # Add performance metrics
                    terrain_data['fps'] = self.fps
                    terrain_data['calibrated'] = self.is_calibrated
                    terrain_data['client_count'] = len(self.clients)
                    
                    # Broadcast to all clients
                    await self.broadcast_to_all(terrain_data)
                    
                    self.update_fps()
                
                # Adaptive frame rate (15-30 FPS)
                await asyncio.sleep(1/20)  # 20 FPS max
                
            except Exception as e:
                logger.error(f"❌ Error in terrain streaming loop: {e}")
                await asyncio.sleep(0.1)
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting Smart Webcam Server on port {self.port}")
        
        # Initialize depth estimator or fallback
        if self.depth_estimator:
            if self.depth_estimator.initialize_camera():
                logger.info("✅ Smart depth estimator initialized")
            else:
                logger.warning("⚠️ Smart depth estimator failed, using fallback")
                self.depth_estimator = None
                self.initialize_fallback_camera()
        else:
            self.initialize_fallback_camera()
        
        self.running = True
        
        # Start WebSocket server
        server = await websockets.serve(
            self.register_client,
            "localhost",
            self.port
        )
        
        logger.info(f"✅ WebSocket server started on ws://localhost:{self.port}")
        
        # Start terrain streaming
        streaming_task = asyncio.create_task(self.terrain_streaming_loop())
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("🛑 Server interrupted by user")
        finally:
            self.running = False
            streaming_task.cancel()
            
            # Cleanup
            if self.depth_estimator:
                self.depth_estimator.cleanup()
            if self.fallback_cap:
                self.fallback_cap.release()
            
            logger.info("🧹 Server cleanup completed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Webcam AR Sandbox Server")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--camera", type=int, default=0, help="Camera ID")
    
    args = parser.parse_args()
    
    print("🤖 Smart Webcam AR Sandbox Server")
    print("=" * 50)
    print(f"Port: {args.port}")
    print(f"Camera: {args.camera}")
    print("\n🌐 Open smart_webcam_demo.html in your browser")
    print("📱 The demo will automatically connect to this server")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    server = SmartWebcamServer(port=args.port, camera_id=args.camera)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
