#!/usr/bin/env python3
"""
🌉 AR Sandbox Data Bridge
Connects working triple_camera_fusion_system.py to working_ar_sandbox
Following the integration plan: use existing proven components
"""

import asyncio
import websockets
import json
import numpy as np
import time
import threading
import logging
from datetime import datetime

# Import working AR sandbox components
import sys
import os
sys.path.append('working_ar_sandbox')

try:
    from sandbox.sensor.sensor_api import Sensor
    from sandbox.projector import Projector
    from sandbox.sandbox_api import Sandbox
    WORKING_AR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Working AR Sandbox not available: {e}")
    WORKING_AR_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARSandboxDataBridge:
    """
    Bridge between triple camera fusion system and working AR sandbox
    """
    
    def __init__(self):
        print("🌉 AR Sandbox Data Bridge - Connecting Systems")
        print("=" * 60)
        
        # Data storage
        self.latest_depth_data = None
        self.latest_rgb_data = None
        self.latest_frame_count = 0
        self.data_lock = threading.Lock()
        
        # WebSocket client to triple camera fusion
        self.fusion_ws = None
        self.fusion_connected = False
        
        # Working AR sandbox components
        self.ar_sensor = None
        self.ar_projector = None
        self.ar_sandbox = None
        
        # Initialize systems
        self.init_ar_sandbox_connection()
        
    def init_ar_sandbox_connection(self):
        """Initialize connection to working AR sandbox"""
        if not WORKING_AR_AVAILABLE:
            print("❌ Working AR Sandbox not available")
            return
            
        try:
            print("🔄 Connecting to working AR sandbox components...")
            
            # Initialize sensor (this will connect to our data bridge)
            self.ar_sensor = Sensor(name='kinect_v1')
            print("✅ AR Sandbox sensor initialized")
            
            # Initialize projector
            calibprojector = "working_ar_sandbox/sandbox/_calibration_dir/my_projector_calibration.json"
            if os.path.exists(calibprojector):
                self.ar_projector = Projector(calibprojector=calibprojector)
                print("✅ AR Sandbox projector initialized")
            else:
                print("⚠️ Projector calibration file not found, using defaults")
                self.ar_projector = Projector()
            
            # Initialize main sandbox
            self.ar_sandbox = Sandbox(sensor=self.ar_sensor, projector=self.ar_projector)
            print("✅ AR Sandbox main system initialized")
            
        except Exception as e:
            print(f"❌ AR Sandbox initialization error: {e}")
            
    async def connect_to_fusion_system(self):
        """Connect to triple camera fusion WebSocket"""
        fusion_url = "ws://localhost:8767"
        
        while True:
            try:
                print(f"🔄 Connecting to triple camera fusion: {fusion_url}")
                
                async with websockets.connect(fusion_url) as websocket:
                    self.fusion_ws = websocket
                    self.fusion_connected = True
                    print("✅ Connected to triple camera fusion system")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            self.process_fusion_data(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"Data processing error: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                print("🔌 Connection to fusion system closed")
                self.fusion_connected = False
            except Exception as e:
                print(f"❌ Connection error: {e}")
                self.fusion_connected = False
                
            # Reconnect after delay
            print("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
            
    def process_fusion_data(self, data):
        """Process data from triple camera fusion system"""
        try:
            # Extract standardized data format
            if 'depth' in data and 'frame' in data:
                depth_array = np.array(data['depth'])
                rgb_array = np.array(data['rgb']) if data.get('rgb') else None
                frame_count = data['frame']
                
                # Store latest data thread-safely
                with self.data_lock:
                    self.latest_depth_data = depth_array
                    self.latest_rgb_data = rgb_array
                    self.latest_frame_count = frame_count
                    
                print(f"📡 Bridge received frame {frame_count}: depth {depth_array.shape}")
                
                # Update AR sandbox if available
                if self.ar_sandbox:
                    self.update_ar_sandbox(depth_array, rgb_array)
                    
        except Exception as e:
            logger.error(f"Fusion data processing error: {e}")
            
    def update_ar_sandbox(self, depth_data, rgb_data):
        """Update working AR sandbox with new data"""
        try:
            # Convert depth data to AR sandbox format
            if depth_data is not None:
                # Ensure proper shape and type
                if len(depth_data.shape) == 1:
                    # Reshape to 2D if needed
                    width = int(np.sqrt(len(depth_data)))
                    height = len(depth_data) // width
                    depth_2d = depth_data[:width*height].reshape(height, width)
                else:
                    depth_2d = depth_data
                    
                # Scale to AR sandbox expected range (mm)
                depth_mm = depth_2d.astype(np.uint16)
                
                # Update sensor data (this feeds into the AR sandbox)
                if hasattr(self.ar_sensor, 'depth'):
                    self.ar_sensor.depth = depth_mm
                    
                print(f"🎨 Updated AR sandbox with depth: {depth_mm.shape}")
                
        except Exception as e:
            logger.error(f"AR sandbox update error: {e}")
            
    def get_bridge_status(self):
        """Get current bridge status"""
        return {
            'fusion_connected': self.fusion_connected,
            'ar_sandbox_available': WORKING_AR_AVAILABLE,
            'latest_frame': self.latest_frame_count,
            'has_depth_data': self.latest_depth_data is not None,
            'has_rgb_data': self.latest_rgb_data is not None
        }
        
    def run_bridge(self):
        """Run the data bridge"""
        print("\n🚀 Starting AR Sandbox Data Bridge...")
        print("Connecting triple camera fusion → working AR sandbox")
        print("Press Ctrl+C to stop...")
        
        try:
            # Start WebSocket connection in background
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the connection
            loop.run_until_complete(self.connect_to_fusion_system())
            
        except KeyboardInterrupt:
            print("\n🛑 Bridge stopped by user")
        except Exception as e:
            print(f"❌ Bridge error: {e}")
        finally:
            print("🧹 Cleaning up bridge...")

def main():
    """Main function"""
    bridge = ARSandboxDataBridge()
    
    print(f"\n📊 Bridge Status:")
    status = bridge.get_bridge_status()
    for key, value in status.items():
        print(f"  {key}: {'✅' if value else '❌'}")
        
    if not WORKING_AR_AVAILABLE:
        print("\n❌ Cannot start bridge - working AR sandbox not available")
        print("💡 Make sure working_ar_sandbox is properly installed")
        return
        
    print(f"\n🎯 Bridge Configuration:")
    print(f"  Source: Triple Camera Fusion (ws://localhost:8767)")
    print(f"  Target: Working AR Sandbox (Bokeh server)")
    print(f"  Data Format: Standardized depth + RGB arrays")
    print(f"  Processing: Magic Sand elevation mapping")
    
    bridge.run_bridge()

if __name__ == "__main__":
    main()
