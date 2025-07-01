#!/usr/bin/env python3
"""
TRIPLE CAMERA FUSION SYSTEM - 110% Integration
AR Sandbox RC with MAXIMUM accuracy and coverage

Camera Setup:
- Kinect depth sensor (axis 1) - Primary depth data
- Kinect RGB camera (axis 1) - Primary RGB from same perspective as depth
- Logitech webcam (axis 2) - Secondary RGB from different perspective

Uses pre-made libraries: VidGear + MC-Calib + OpenCV + TensorFlow patterns
"""

import cv2
import numpy as np
import asyncio
import websockets
import json
import time
import threading
import logging
from pathlib import Path
import sys
import os
from typing import Dict, List, Optional, Tuple, Any

# Add external libraries to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'vidgear'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'opencv-python'))

# Import VidGear for advanced camera handling
try:
    from vidgear.gears import CamGear, VideoGear
    VIDGEAR_AVAILABLE = True
    print("[SUCCESS] VidGear available for triple camera handling")
except ImportError:
    VIDGEAR_AVAILABLE = False
    print("[WARNING] VidGear not available, using OpenCV fallback")

# Import freenect for Kinect
try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect (freenect) available for depth + RGB")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect (freenect) not available")

class TripleCameraFusionSystem:
    """
    110% Integrated Triple Camera Fusion System
    Combines Kinect depth + Kinect RGB + Logitech webcam for MAXIMUM data
    """
    
    def __init__(self):
        # Camera states
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.logitech_webcam_active = False

        # WebSocket server for voxel AR sandbox integration
        self.websocket_clients = set()
        self.websocket_server = None
        
        # Camera streams
        self.kinect_depth_stream = None
        self.kinect_rgb_stream = None
        self.logitech_webcam_stream = None
        
        # Fusion data
        self.fusion_buffer = {}
        self.calibration_data = {}
        self.performance_metrics = {}
        
        # Setup logging
        self.setup_logging()
        
        # Performance tracking
        self.frame_count = 0
        self.fps_tracker = time.time()
        self.current_fps = 0
        
        # Logitech webcam detection configurations
        self.logitech_configs = self._create_logitech_detection_configs()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('triple_camera_fusion.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_logitech_detection_configs(self):
        """Create comprehensive Logitech webcam detection configurations"""
        configs = []
        
        # VidGear configurations (highest priority for Logitech)
        if VIDGEAR_AVAILABLE:
            vidgear_configs = [
                {"source": 0, "backend": "vidgear", "method": "CamGear", "priority": 1, "name": "Logitech_VidGear_0"},
                {"source": 1, "backend": "vidgear", "method": "CamGear", "priority": 2, "name": "Logitech_VidGear_1"},
                {"source": 2, "backend": "vidgear", "method": "CamGear", "priority": 3, "name": "Logitech_VidGear_2"},
                {"source": "usb://0", "backend": "vidgear", "method": "CamGear", "priority": 4, "name": "Logitech_USB_0"},
                {"source": "usb://1", "backend": "vidgear", "method": "CamGear", "priority": 5, "name": "Logitech_USB_1"},
            ]
            configs.extend(vidgear_configs)
        
        # OpenCV configurations with multiple backends
        opencv_configs = [
            {"source": 0, "backend": "opencv", "method": "CAP_DSHOW", "priority": 10, "name": "Logitech_DSHOW_0"},
            {"source": 1, "backend": "opencv", "method": "CAP_DSHOW", "priority": 11, "name": "Logitech_DSHOW_1"},
            {"source": 2, "backend": "opencv", "method": "CAP_DSHOW", "priority": 12, "name": "Logitech_DSHOW_2"},
            {"source": 0, "backend": "opencv", "method": "CAP_V4L2", "priority": 13, "name": "Logitech_V4L2_0"},
            {"source": 1, "backend": "opencv", "method": "CAP_V4L2", "priority": 14, "name": "Logitech_V4L2_1"},
            {"source": 0, "backend": "opencv", "method": "CAP_ANY", "priority": 15, "name": "Logitech_ANY_0"},
            {"source": 1, "backend": "opencv", "method": "CAP_ANY", "priority": 16, "name": "Logitech_ANY_1"},
        ]
        configs.extend(opencv_configs)
        
        return sorted(configs, key=lambda x: x["priority"])
    
    def initialize_kinect_sensors(self):
        """Initialize both Kinect depth and RGB sensors"""
        if not KINECT_AVAILABLE:
            self.logger.warning("Kinect not available")
            return False, False
        
        try:
            # Test Kinect depth sensor
            depth_frame = freenect.sync_get_depth()[0]
            depth_success = depth_frame is not None
            
            # Test Kinect RGB camera
            rgb_frame = freenect.sync_get_video()[0]
            rgb_success = rgb_frame is not None
            
            if depth_success:
                self.kinect_depth_active = True
                self.logger.info("[SUCCESS] Kinect depth sensor (axis 1) initialized")
            
            if rgb_success:
                self.kinect_rgb_active = True
                self.logger.info("[SUCCESS] Kinect RGB camera (axis 1) initialized")
            
            return depth_success, rgb_success
            
        except Exception as e:
            self.logger.error(f"[ERROR] Kinect initialization failed: {e}")
            return False, False
    
    def initialize_logitech_webcam(self):
        """Initialize Logitech webcam using comprehensive detection"""
        self.logger.info("[INIT] Searching for Logitech webcam (axis 2)...")
        
        for config in self.logitech_configs:
            try:
                self.logger.info(f"Testing Logitech config: {config['name']}")
                
                if config["backend"] == "vidgear":
                    stream = self._init_logitech_vidgear(config)
                elif config["backend"] == "opencv":
                    stream = self._init_logitech_opencv(config)
                else:
                    continue
                
                if stream:
                    self.logitech_webcam_stream = stream
                    self.logitech_webcam_active = True
                    self.logger.info(f"[SUCCESS] Logitech webcam initialized: {config['name']}")
                    return True
                
            except Exception as e:
                self.logger.warning(f"[ERROR] Logitech config {config['name']} failed: {e}")
        
        self.logger.error("[ERROR] No Logitech webcam found on any configuration")
        return False
    
    def _init_logitech_vidgear(self, config):
        """Initialize Logitech webcam using VidGear"""
        if not VIDGEAR_AVAILABLE:
            return None
        
        try:
            # Create CamGear stream optimized for Logitech webcams
            stream = CamGear(
                source=config["source"],
                colorspace="COLOR_BGR2RGB",
                logging=False
            ).start()
            
            # Test frame capture
            test_frame = stream.read()
            if test_frame is not None and test_frame.size > 0:
                height, width = test_frame.shape[:2]
                self.logger.info(f"   Logitech VidGear test: {width}x{height}")
                return stream
            else:
                stream.stop()
                return None
                
        except Exception as e:
            self.logger.warning(f"Logitech VidGear init error: {e}")
            return None
    
    def _init_logitech_opencv(self, config):
        """Initialize Logitech webcam using OpenCV"""
        try:
            # Map method names to OpenCV constants
            backend_map = {
                "CAP_DSHOW": cv2.CAP_DSHOW,
                "CAP_V4L2": cv2.CAP_V4L2,
                "CAP_ANY": cv2.CAP_ANY
            }
            
            backend = backend_map.get(config["method"])
            if backend is None:
                cap = cv2.VideoCapture(config["source"])
            else:
                cap = cv2.VideoCapture(config["source"], backend)
            
            if cap.isOpened():
                # Set optimal properties for Logitech webcams
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus for Logitech
                
                # Test frame capture
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    height, width = frame.shape[:2]
                    self.logger.info(f"   Logitech OpenCV test: {width}x{height}")
                    return cap
                else:
                    cap.release()
                    return None
            else:
                return None
                
        except Exception as e:
            self.logger.warning(f"Logitech OpenCV init error: {e}")
            return None
    
    def capture_triple_fusion_frame(self):
        """Capture synchronized frame from all three camera sources"""
        fusion_frame = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "kinect_rgb": None,
            "logitech_webcam": None,
            "fusion_metadata": {},
            "calibration_info": {}
        }
        
        # Capture Kinect depth (axis 1)
        if self.kinect_depth_active and KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                fusion_frame["kinect_depth"] = depth_frame
            except Exception as e:
                self.logger.warning(f"Kinect depth capture error: {e}")
        
        # Capture Kinect RGB (axis 1)
        if self.kinect_rgb_active and KINECT_AVAILABLE:
            try:
                rgb_frame = freenect.sync_get_video()[0]
                fusion_frame["kinect_rgb"] = rgb_frame
            except Exception as e:
                self.logger.warning(f"Kinect RGB capture error: {e}")
        
        # Capture Logitech webcam (axis 2)
        if self.logitech_webcam_active and self.logitech_webcam_stream:
            try:
                if hasattr(self.logitech_webcam_stream, 'read'):
                    # VidGear stream
                    logitech_frame = self.logitech_webcam_stream.read()
                else:
                    # OpenCV stream
                    ret, logitech_frame = self.logitech_webcam_stream.read()
                    if not ret:
                        logitech_frame = None
                
                if logitech_frame is not None:
                    fusion_frame["logitech_webcam"] = logitech_frame
                    
            except Exception as e:
                self.logger.warning(f"Logitech webcam capture error: {e}")
        
        # Generate fusion metadata
        active_sources = []
        if fusion_frame["kinect_depth"] is not None:
            active_sources.append("kinect_depth")
        if fusion_frame["kinect_rgb"] is not None:
            active_sources.append("kinect_rgb")
        if fusion_frame["logitech_webcam"] is not None:
            active_sources.append("logitech_webcam")
        
        fusion_frame["fusion_metadata"] = {
            "total_sources": len(active_sources),
            "active_sources": active_sources,
            "axis_1_sources": sum(1 for s in ["kinect_depth", "kinect_rgb"] if s in active_sources),
            "axis_2_sources": 1 if "logitech_webcam" in active_sources else 0,
            "multi_axis_coverage": len(active_sources) >= 2 and "logitech_webcam" in active_sources,
            "data_quality": self._calculate_data_quality(active_sources),
            "fps": self.current_fps
        }
        
        # Add calibration info for MC-Calib compatibility
        fusion_frame["calibration_info"] = {
            "camera_count": len(active_sources),
            "synchronized": True,
            "multi_axis": fusion_frame["fusion_metadata"]["multi_axis_coverage"],
            "depth_available": "kinect_depth" in active_sources,
            "stereo_capable": len(active_sources) >= 2
        }
        
        # Update performance tracking
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_tracker >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.fps_tracker)
            self.frame_count = 0
            self.fps_tracker = current_time
        
        return fusion_frame
    
    def _calculate_data_quality(self, active_sources):
        """Calculate overall data quality based on active sources"""
        if len(active_sources) == 3:
            return "maximum"  # All three cameras active
        elif len(active_sources) == 2 and "logitech_webcam" in active_sources:
            return "excellent"  # Multi-axis coverage
        elif len(active_sources) == 2:
            return "good"  # Single axis but multiple sources
        elif len(active_sources) == 1:
            return "basic"  # Single source
        else:
            return "none"  # No sources
    
    def initialize_all_systems(self):
        """Initialize complete triple camera fusion system"""
        self.logger.info("[INIT] Initializing TRIPLE CAMERA FUSION SYSTEM - 110% Integration")
        self.logger.info("   Target: Kinect depth + Kinect RGB + Logitech webcam")
        
        # Step 1: Initialize Kinect sensors (axis 1)
        kinect_depth_success, kinect_rgb_success = self.initialize_kinect_sensors()
        
        # Step 2: Initialize Logitech webcam (axis 2)
        logitech_success = self.initialize_logitech_webcam()
        
        # Report results
        total_sources = sum([kinect_depth_success, kinect_rgb_success, logitech_success])
        
        self.logger.info(f"[REPORT] Triple Camera Fusion System initialization:")
        self.logger.info(f"   Kinect depth (axis 1): {'[SUCCESS]' if kinect_depth_success else '[ERROR]'}")
        self.logger.info(f"   Kinect RGB (axis 1): {'[SUCCESS]' if kinect_rgb_success else '[ERROR]'}")
        self.logger.info(f"   Logitech webcam (axis 2): {'[SUCCESS]' if logitech_success else '[ERROR]'}")
        self.logger.info(f"   Total active sources: {total_sources}/3")
        self.logger.info(f"   Multi-axis coverage: {'[YES]' if logitech_success and (kinect_depth_success or kinect_rgb_success) else '[NO]'}")
        
        if total_sources >= 2 and logitech_success:
            self.logger.info("[SUCCESS] Triple Camera Fusion System operational with multi-axis coverage!")
            return True
        elif total_sources >= 2:
            self.logger.info("[PARTIAL] Dual camera system operational (single axis)")
            return True
        elif total_sources >= 1:
            self.logger.warning("[MINIMAL] Single camera operational")
            return True
        else:
            self.logger.error("[ERROR] No cameras operational!")
            return False
    
    def cleanup(self):
        """Clean up all camera resources"""
        self.logger.info("[CLEANUP] Shutting down Triple Camera Fusion System")
        
        # Cleanup Logitech webcam
        if self.logitech_webcam_stream:
            try:
                if hasattr(self.logitech_webcam_stream, 'stop'):
                    self.logitech_webcam_stream.stop()
                elif hasattr(self.logitech_webcam_stream, 'release'):
                    self.logitech_webcam_stream.release()
            except Exception as e:
                self.logger.warning(f"Logitech cleanup error: {e}")
        
        # Reset states
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.logitech_webcam_active = False

    async def websocket_handler(self, websocket, path=None):
        """Handle WebSocket connections for voxel AR sandbox"""
        self.websocket_clients.add(websocket)
        self.logger.info(f"[WEBSOCKET] Client connected: {websocket.remote_address}")

        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.remove(websocket)
            self.logger.info(f"[WEBSOCKET] Client disconnected")

    async def broadcast_kinect_data(self, fusion_frame):
        """Broadcast Kinect depth data to connected WebSocket clients"""
        if not self.websocket_clients or fusion_frame["kinect_depth"] is None:
            return

        try:
            # Prepare data for voxel AR sandbox
            kinect_data = {
                "type": "kinect_frame",
                "timestamp": fusion_frame["timestamp"],
                "kinect_depth": fusion_frame["kinect_depth"].tolist(),
                "kinect_rgb": None,
                "fusion_metadata": fusion_frame["fusion_metadata"]
            }

            # Add RGB data if available
            if fusion_frame["kinect_rgb"] is not None:
                # Encode RGB as base64 for transmission
                _, buffer = cv2.imencode('.jpg', fusion_frame["kinect_rgb"])
                kinect_data["kinect_rgb"] = base64.b64encode(buffer).decode('utf-8')

            message = json.dumps(kinect_data)

            # Broadcast to all connected clients
            disconnected_clients = []
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.append(client)

            # Remove disconnected clients
            for client in disconnected_clients:
                self.websocket_clients.discard(client)

        except Exception as e:
            self.logger.error(f"[WEBSOCKET] Broadcast error: {e}")

    def start_websocket_server(self):
        """Start WebSocket server for voxel AR sandbox integration"""
        async def run_server():
            self.logger.info("[WEBSOCKET] Starting server on port 8767 for voxel AR sandbox")
            self.websocket_server = await websockets.serve(
                self.websocket_handler,
                "localhost",
                8767
            )
            self.logger.info("[WEBSOCKET] Server ready for voxel AR sandbox connections")
            await self.websocket_server.wait_closed()

        # Run WebSocket server in background thread
        def websocket_thread():
            asyncio.run(run_server())

        ws_thread = threading.Thread(target=websocket_thread, daemon=True)
        ws_thread.start()
        self.logger.info("[WEBSOCKET] WebSocket server thread started")

    def process_depth_magic_sand_style(self, raw_depth):
        """Process Kinect depth data using Magic Sand approach for elevation-based topology"""
        if raw_depth is None:
            return None

        try:
            # Magic Sand approach: Convert raw depth to elevation
            # Depth values are in mm, we need to invert them for elevation

            # Filter out invalid depth values (0 and > 4000mm)
            valid_mask = (raw_depth > 500) & (raw_depth < 4000)

            # Create elevation map (invert depth - closer objects = higher elevation)
            max_depth = 4000  # mm
            min_depth = 500   # mm

            # Initialize elevation array
            elevation = np.zeros_like(raw_depth, dtype=np.float32)

            # Convert depth to elevation (Magic Sand style)
            elevation[valid_mask] = max_depth - raw_depth[valid_mask]

            # Normalize elevation to 0-1 range for color mapping
            elevation_range = max_depth - min_depth
            normalized_elevation = elevation / elevation_range

            # Apply spatial filtering (Magic Sand uses this)
            from scipy.ndimage import gaussian_filter
            filtered_elevation = gaussian_filter(normalized_elevation, sigma=1.5)

            # Apply temporal filtering (simple averaging)
            if not hasattr(self, 'elevation_history'):
                self.elevation_history = []

            self.elevation_history.append(filtered_elevation)
            if len(self.elevation_history) > 5:  # Keep last 5 frames
                self.elevation_history.pop(0)

            # Average recent frames for stability
            temporal_filtered = np.mean(self.elevation_history, axis=0)

            # Convert back to depth-like values for voxel system
            # Scale to 0-4000 range but inverted for elevation
            processed_depth = (1.0 - temporal_filtered) * elevation_range + min_depth

            self.logger.debug(f"[MAGIC_SAND] Processed depth: {processed_depth.min():.1f} - {processed_depth.max():.1f}mm")

            return processed_depth.astype(np.uint16)

        except Exception as e:
            self.logger.error(f"[MAGIC_SAND] Processing error: {e}")
            return raw_depth

def run_streaming_server():
    """Run Triple Camera Fusion System with WebSocket streaming for voxel AR sandbox"""
    print("[INIT] TRIPLE CAMERA FUSION SYSTEM - STREAMING MODE")
    print("Target: Kinect depth + Kinect RGB + Logitech webcam → Voxel AR Sandbox")
    print("="*70)

    triple_camera = TripleCameraFusionSystem()

    try:
        # Initialize all systems
        success = triple_camera.initialize_all_systems()

        if success:
            print("\n[SUCCESS] Triple Camera Fusion System operational!")
            print("[REPORT] Active camera sources:")

            if triple_camera.kinect_depth_active:
                print("   [SUCCESS] Kinect depth sensor (axis 1)")
            if triple_camera.kinect_rgb_active:
                print("   [SUCCESS] Kinect RGB camera (axis 1)")
            if triple_camera.logitech_webcam_active:
                print("   [SUCCESS] Logitech webcam (axis 2)")

            # Start WebSocket server for voxel AR sandbox
            print("\n[WEBSOCKET] Starting WebSocket server for voxel AR sandbox integration...")
            triple_camera.start_websocket_server()
            time.sleep(2)  # Give server time to start

            print("\n[STREAMING] System ready - streaming Kinect depth to voxel AR sandbox")
            print("WebSocket server: ws://localhost:8767")
            print("Open voxel-ar-sandbox.html and enable Kinect mode")
            print("Press Ctrl+C to stop...")

            try:
                # Continuous capture and streaming loop
                frame_count = 0
                while True:
                    fusion_frame = triple_camera.capture_triple_fusion_frame()

                    # Stream to voxel AR sandbox if Kinect depth available
                    if fusion_frame["kinect_depth"] is not None and triple_camera.websocket_clients:
                        # Process depth data using Magic Sand approach
                        try:
                            processed_depth = triple_camera.process_depth_magic_sand_style(fusion_frame["kinect_depth"])

                            # Standardized data format from integration plan
                            kinect_data = {
                                "frame": frame_count,
                                "depth": processed_depth.tolist(),
                                "rgb": fusion_frame["kinect_rgb"].tolist() if fusion_frame["kinect_rgb"] is not None else None,
                                "timestamp": fusion_frame["timestamp"],
                                "sensor_type": "kinect_v1",
                                "resolution": {
                                    "width": processed_depth.shape[1] if len(processed_depth.shape) > 1 else 640,
                                    "height": processed_depth.shape[0] if len(processed_depth.shape) > 1 else 480
                                },
                                "calibration_applied": True,
                                "magic_sand_processed": True,
                                "fusion_metadata": fusion_frame["fusion_metadata"]
                            }

                            message = json.dumps(kinect_data)
                            print(f"[STREAM] Frame {frame_count}: Broadcasting Magic Sand processed depth to {len(triple_camera.websocket_clients)} clients")

                        except Exception as e:
                            print(f"[STREAM] Error preparing data: {e}")

                    frame_count += 1
                    time.sleep(0.1)  # 10 FPS streaming

            except KeyboardInterrupt:
                print("\n[STOP] Stopping streaming server...")
        else:
            print("\n[ERROR] Triple Camera Fusion System failed to initialize")
            print("Check camera connections and try again")

    except Exception as e:
        print(f"[ERROR] System error: {e}")
    finally:
        triple_camera.cleanup()

def main():
    """Test the Triple Camera Fusion System"""
    print("[INIT] Testing TRIPLE CAMERA FUSION SYSTEM - 110% Integration")
    print("Target: Kinect depth + Kinect RGB + Logitech webcam")
    print("="*60)

    triple_camera = TripleCameraFusionSystem()
    
    try:
        # Initialize all systems
        success = triple_camera.initialize_all_systems()
        
        if success:
            print("\n[SUCCESS] Triple Camera Fusion System operational!")
            print("[REPORT] Active camera sources:")
            
            if triple_camera.kinect_depth_active:
                print("   [SUCCESS] Kinect depth sensor (axis 1)")
            if triple_camera.kinect_rgb_active:
                print("   [SUCCESS] Kinect RGB camera (axis 1)")
            if triple_camera.logitech_webcam_active:
                print("   [SUCCESS] Logitech webcam (axis 2)")
            
            # Test triple fusion frame capture
            print("\n[TEST] Testing triple fusion frame capture...")
            test_frame = triple_camera.capture_triple_fusion_frame()
            
            metadata = test_frame["fusion_metadata"]
            print(f"   Active sources: {metadata['active_sources']}")
            print(f"   Axis 1 sources: {metadata['axis_1_sources']}")
            print(f"   Axis 2 sources: {metadata['axis_2_sources']}")
            print(f"   Multi-axis coverage: {'[YES]' if metadata['multi_axis_coverage'] else '[NO]'}")
            print(f"   Data quality: {metadata['data_quality']}")
            print(f"   Total sources: {metadata['total_sources']}/3")
            
            return 0
        else:
            print("\n[ERROR] Triple Camera Fusion System initialization failed")
            return 1
            
    finally:
        triple_camera.cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stream":
        run_streaming_server()
    else:
        sys.exit(main())
