#!/usr/bin/env python3
"""
Kinect Depth Server - Serves depth data from Xbox 360 Kinect
Stolen and adapted from various AR sandbox implementations
"""

import cv2
import numpy as np
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socketserver
from urllib.parse import urlparse, parse_qs

class KinectDepthCapture:
    def __init__(self):
        self.depth_frame = None
        self.rgb_frame = None
        self.running = False
        self.cap = None
        
    def start_kinect(self):
        """Try different methods to connect to Kinect"""
        print("🔍 Attempting to connect to Xbox 360 Kinect...")

        # Method 1: Try our freenect module first
        try:
            import freenect
            print("✅ Using freenect module for Xbox 360 Kinect")

            # Test Kinect connection
            ctx = freenect.init()
            if freenect.num_devices(ctx) > 0:
                print("✅ Xbox 360 Kinect detected via freenect")
                self.kinect_module = freenect
                self.running = True
                return True
            else:
                print("❌ No Kinect devices found via freenect")
        except ImportError:
            print("❌ freenect module not available")
        except Exception as e:
            print(f"❌ freenect error: {e}")

        # Method 2: Try OpenCV with different backends as fallback
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

        for i, backend in enumerate(backends):
            try:
                print(f"Trying backend {i}: {backend}")
                self.cap = cv2.VideoCapture(0, backend)
                if self.cap.isOpened():
                    # Test if we can read a frame
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ Connected via OpenCV backend {backend}")
                        self.running = True
                        return True
                    else:
                        self.cap.release()
            except Exception as e:
                print(f"❌ Backend {backend} failed: {e}")

        # Method 3: Try to use Windows Kinect SDK via COM
        try:
            import win32com.client
            print("Trying Windows Kinect SDK...")
            # This would require pywin32 and proper Kinect SDK
            # For now, fall back to simulation
        except ImportError:
            pass
            
        # Method 3: Fallback to simulated depth data
        print("⚠️ Kinect not detected, using simulated depth data")
        self.running = True
        return True
        
    def get_depth_frame(self):
        """Get current depth frame as numpy array"""
        if not self.running:
            return None

        # Try freenect first
        if hasattr(self, 'kinect_module'):
            try:
                depth, timestamp = self.kinect_module.sync_get_depth(0, self.kinect_module.DEPTH_MM)
                if depth is not None:
                    # Convert from mm to 8-bit for visualization (scale 800-4000mm to 0-255)
                    depth_scaled = np.clip((depth - 800) * 255 / (4000 - 800), 0, 255).astype(np.uint8)
                    return depth_scaled
            except Exception as e:
                print(f"❌ Freenect depth error: {e}")

        # Fallback to OpenCV
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert RGB to simulated depth
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Simulate depth based on brightness
                depth = 255 - gray  # Invert so bright = close
                return depth

        # Generate simulated depth data for testing
        height, width = 480, 640
        depth = np.zeros((height, width), dtype=np.uint8)

        # Create some hills and valleys
        y, x = np.ogrid[:height, :width]
        center_y, center_x = height // 2, width // 2

        # Multiple terrain features
        for i in range(5):
            hill_x = np.random.randint(100, width - 100)
            hill_y = np.random.randint(100, height - 100)
            hill_size = np.random.randint(50, 150)
            hill_height = np.random.randint(30, 100)

            distance = np.sqrt((x - hill_x)**2 + (y - hill_y)**2)
            hill = np.maximum(0, hill_height - distance * hill_height / hill_size)
            depth = np.maximum(depth, hill.astype(np.uint8))

        return depth
        
    def get_rgb_frame(self):
        """Get current RGB frame"""
        # Try freenect first
        if hasattr(self, 'kinect_module'):
            try:
                rgb, timestamp = self.kinect_module.sync_get_video(0, self.kinect_module.VIDEO_RGB)
                if rgb is not None:
                    return rgb
            except Exception as e:
                print(f"❌ Freenect RGB error: {e}")

        # Fallback to OpenCV
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
        
    def stop(self):
        """Stop Kinect capture"""
        self.running = False
        if self.cap:
            self.cap.release()

class DepthServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/depth':
            # Serve depth data as JSON
            depth_frame = kinect.get_depth_frame()
            if depth_frame is not None:
                # Downsample for web transmission
                small_depth = cv2.resize(depth_frame, (128, 96))
                depth_list = small_depth.flatten().tolist()
                
                response = {
                    'width': 128,
                    'height': 96,
                    'data': depth_list,
                    'timestamp': time.time()
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(500, "No depth data available")
                
        elif parsed_path.path == '/rgb':
            # Serve RGB frame as JPEG
            rgb_frame = kinect.get_rgb_frame()
            if rgb_frame is not None:
                _, buffer = cv2.imencode('.jpg', rgb_frame)
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(buffer.tobytes())
            else:
                self.send_error(500, "No RGB data available")
                
        elif parsed_path.path == '/status':
            # Serve status information
            status = {
                'kinect_connected': kinect.running,
                'has_depth': kinect.get_depth_frame() is not None,
                'has_rgb': kinect.get_rgb_frame() is not None,
                'timestamp': time.time()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
            
        else:
            self.send_error(404, "Not found")
            
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    """Run the depth data server"""
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, DepthServerHandler)
    print(f"🌐 Kinect Depth Server running on http://localhost:8080")
    print("📡 Endpoints:")
    print("  /depth - Depth data as JSON")
    print("  /rgb   - RGB frame as JPEG") 
    print("  /status - Connection status")
    httpd.serve_forever()

# Global Kinect instance
kinect = KinectDepthCapture()

def main():
    print("🎮 Xbox 360 Kinect Depth Server")
    print("=" * 50)
    
    # Start Kinect
    if kinect.start_kinect():
        print("✅ Kinect system initialized")
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        print("\n🎯 Testing depth capture...")
        try:
            while True:
                depth = kinect.get_depth_frame()
                if depth is not None:
                    print(f"📊 Depth frame: {depth.shape}, min={depth.min()}, max={depth.max()}")
                else:
                    print("❌ No depth data")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            kinect.stop()
    else:
        print("❌ Failed to initialize Kinect")

if __name__ == "__main__":
    main()
