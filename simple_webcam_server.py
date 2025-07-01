#!/usr/bin/env python3
"""
Simple Webcam Server for AR Sandbox Game
Provides basic depth estimation from webcam to enhance the HTML game
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleWebcamServer:
    """
    Simple WebSocket server that provides webcam-based terrain detection
    """
    
    def __init__(self, port: int = 8765, camera_id: int = 0):
        self.port = port
        self.camera_id = camera_id
        self.clients = set()
        self.running = False
        self.cap = None
        
        # Simple depth detection parameters
        self.background_frame = None
        self.is_calibrated = False
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"📱 Client connected: {websocket.remote_address}")
        
        # Send initial status
        await self.send_to_client(websocket, {
            'type': 'server_status',
            'camera_available': self.cap is not None,
            'calibrated': self.is_calibrated,
            'message': 'Simple Webcam Server Connected'
        })
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"📱 Client disconnected")
    
    async def handle_client_message(self, websocket, message):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            command = data.get('command', '')
            
            if command == 'calibrate':
                await self.calibrate_background()
                await self.send_to_client(websocket, {
                    'type': 'calibration_result',
                    'success': self.is_calibrated
                })
            
            elif command == 'get_terrain_data':
                terrain_data = self.get_simple_terrain_data()
                if terrain_data:
                    await self.send_to_client(websocket, terrain_data)
            
            elif command == 'get_webcam_frame':
                frame_data = self.get_webcam_frame_data()
                if frame_data:
                    await self.send_to_client(websocket, frame_data)

            elif command == 'get_debug_view':
                debug_data = self.get_debug_topography_view()
                if debug_data:
                    await self.send_to_client(websocket, debug_data)
                    
        except json.JSONDecodeError:
            logger.warning("⚠️ Invalid JSON received")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
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
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.discard(client)
    
    def initialize_camera(self):
        """Initialize the webcam"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                logger.info("📹 Camera initialized successfully")
                return True
            else:
                logger.error("❌ Failed to open camera")
                return False
        except Exception as e:
            logger.error(f"❌ Camera initialization error: {e}")
            return False
    
    async def calibrate_background(self):
        """Calibrate by capturing background frame"""
        if not self.cap or not self.cap.isOpened():
            return False
        
        logger.info("🎯 Calibrating background...")
        
        # Capture several frames and average them
        frames = []
        for i in range(10):
            ret, frame = self.cap.read()
            if ret:
                frames.append(frame)
            await asyncio.sleep(0.1)
        
        if len(frames) >= 5:
            self.background_frame = np.mean(frames, axis=0).astype(np.uint8)
            self.is_calibrated = True
            logger.info("✅ Background calibration completed")
            return True
        else:
            logger.error("❌ Calibration failed - not enough frames")
            return False
    
    def get_simple_terrain_data(self):
        """Get enhanced terrain data from webcam with better topography detection"""
        if not self.cap or not self.cap.isOpened() or not self.is_calibrated:
            return None

        ret, current_frame = self.cap.read()
        if not ret:
            return None

        # ENHANCED TOPOGRAPHY DETECTION

        # 1. Background subtraction for object detection
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_background = cv2.cvtColor(self.background_frame, cv2.COLOR_BGR2GRAY)

        # Calculate difference (objects above background)
        diff = cv2.absdiff(gray_background, gray_current)

        # 2. Multi-threshold approach for better height estimation
        # Different thresholds represent different "height levels"
        height_map = np.zeros_like(gray_current, dtype=np.float32)

        # Layer 1: Close objects (high threshold)
        _, close_objects = cv2.threshold(diff, 60, 100, cv2.THRESH_BINARY)
        height_map += close_objects.astype(np.float32)

        # Layer 2: Medium distance objects
        _, medium_objects = cv2.threshold(diff, 40, 60, cv2.THRESH_BINARY)
        height_map += medium_objects.astype(np.float32) * 0.6

        # Layer 3: Far objects (low threshold)
        _, far_objects = cv2.threshold(diff, 20, 40, cv2.THRESH_BINARY)
        height_map += far_objects.astype(np.float32) * 0.3

        # 3. Morphological operations to clean up noise and create realistic terrain
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        height_map = cv2.morphologyEx(height_map, cv2.MORPH_CLOSE, kernel)
        height_map = cv2.morphologyEx(height_map, cv2.MORPH_OPEN, kernel)

        # 4. Distance transform for smooth height gradients
        # This makes objects have realistic "slopes" instead of flat tops
        binary_objects = (height_map > 10).astype(np.uint8)
        if np.any(binary_objects):
            distance_map = cv2.distanceTransform(binary_objects, cv2.DIST_L2, 5)
            # Normalize and scale distance transform
            if np.max(distance_map) > 0:
                distance_map = (distance_map / np.max(distance_map)) * 80
                height_map = np.maximum(height_map, distance_map)

        # 5. Gaussian smoothing for natural terrain appearance
        height_map = cv2.GaussianBlur(height_map, (7, 7), 0)

        # 6. Edge enhancement to maintain object boundaries
        edges = cv2.Canny(gray_current, 50, 150)
        edge_dilated = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
        height_map[edge_dilated > 0] *= 1.2  # Enhance edges

        # 7. Resize to game grid
        height_map_resized = cv2.resize(height_map, (50, 40))

        # 8. Apply realistic height scaling
        # Map to 0-100 range with better distribution
        height_values = np.clip(height_map_resized, 0, 255)
        height_values = (height_values / 255.0) * 100

        # 9. Add some noise reduction and final smoothing
        height_values = cv2.medianBlur(height_values.astype(np.uint8), 3).astype(np.float32)

        # 10. Ensure minimum height for detected objects
        height_values[height_values > 5] = np.maximum(height_values[height_values > 5], 15)

        return {
            'type': 'terrain_data',
            'timestamp': time.time(),
            'width': 50,
            'height': 40,
            'data': height_values.flatten().tolist(),
            'min_height': float(np.min(height_values)),
            'max_height': float(np.max(height_values)),
            'source': 'enhanced_webcam_topography',
            'fps': self.fps,
            'detection_method': 'multi_threshold_distance_transform'
        }
    
    def get_webcam_frame_data(self):
        """Get current webcam frame as base64"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Resize frame for web transmission
        frame_small = cv2.resize(frame, (320, 240))
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            'type': 'webcam_frame',
            'timestamp': time.time(),
            'image': frame_base64,
            'width': 320,
            'height': 240
        }

    def get_debug_topography_view(self):
        """Get debug view showing how topography is being detected"""
        if not self.cap or not self.cap.isOpened() or not self.is_calibrated:
            return None

        ret, current_frame = self.cap.read()
        if not ret:
            return None

        # Create debug visualization
        debug_frame = current_frame.copy()

        # Background subtraction
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_background = cv2.cvtColor(self.background_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_background, gray_current)

        # Show detected objects with color coding for height
        _, close_objects = cv2.threshold(diff, 60, 255, cv2.THRESH_BINARY)
        _, medium_objects = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
        _, far_objects = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

        # Color code the height levels
        debug_frame[close_objects > 0] = [0, 0, 255]  # Red for highest
        debug_frame[medium_objects > 0] = [0, 255, 255]  # Yellow for medium
        debug_frame[far_objects > 0] = [0, 255, 0]  # Green for lowest

        # Add text overlay
        cv2.putText(debug_frame, "TOPOGRAPHY DETECTION", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(debug_frame, "RED=High, YELLOW=Med, GREEN=Low", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(debug_frame, "Place objects to see detection", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Encode as base64
        _, buffer = cv2.imencode('.jpg', debug_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        debug_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            'type': 'debug_topography',
            'timestamp': time.time(),
            'image': debug_base64,
            'width': debug_frame.shape[1],
            'height': debug_frame.shape[0]
        }
    
    def update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    async def streaming_loop(self):
        """Main streaming loop"""
        logger.info("🌊 Starting streaming loop...")
        
        while self.running:
            try:
                # Get terrain data
                terrain_data = self.get_simple_terrain_data()
                if terrain_data:
                    await self.broadcast_to_all(terrain_data)
                    self.update_fps()
                
                # Limit to ~20 FPS
                await asyncio.sleep(1/20)
                
            except Exception as e:
                logger.error(f"❌ Error in streaming loop: {e}")
                await asyncio.sleep(0.1)
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting Simple Webcam Server on port {self.port}")
        
        # Initialize camera
        if not self.initialize_camera():
            logger.warning("⚠️ Camera not available, server will run in demo mode")
        
        self.running = True
        
        # Start WebSocket server
        server = await websockets.serve(
            lambda websocket, path: self.register_client(websocket, path),
            "localhost",
            self.port
        )
        
        logger.info(f"✅ Server started on ws://localhost:{self.port}")
        logger.info("🌐 Open working_sandbox_game.html in your browser")
        
        # Start streaming loop
        streaming_task = asyncio.create_task(self.streaming_loop())
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("🛑 Server interrupted")
        finally:
            self.running = False
            streaming_task.cancel()
            
            if self.cap:
                self.cap.release()
            
            logger.info("🧹 Server cleanup completed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Webcam AR Sandbox Server")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--camera", type=int, default=0, help="Camera ID")
    
    args = parser.parse_args()
    
    print("🤖 SIMPLE WEBCAM AR SANDBOX SERVER")
    print("=" * 50)
    print(f"Port: {args.port}")
    print(f"Camera: {args.camera}")
    print("\n🎮 Instructions:")
    print("1. Start this server")
    print("2. Open working_sandbox_game.html in your browser")
    print("3. The game will connect automatically")
    print("4. Click 'CALIBRATE' in the game to set up depth detection")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    server = SimpleWebcamServer(port=args.port, camera_id=args.camera)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
