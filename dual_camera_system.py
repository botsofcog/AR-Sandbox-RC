#!/usr/bin/env python3
"""
Dual Camera System for AR Sandbox RC
Combines pre-made solutions: VidGear + TensorFlow patterns + MC-Calib concepts + OpenCV
Provides MAXIMUM data collection from Kinect depth + multiple webcam RGB sources
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

# Add external libraries to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'vidgear'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'opencv-python'))

# Import VidGear for advanced camera handling
try:
    from vidgear.gears import CamGear, VideoGear
    VIDGEAR_AVAILABLE = True
    print("[SUCCESS] VidGear available for advanced multi-camera handling")
except ImportError:
    VIDGEAR_AVAILABLE = False
    print("[WARNING] VidGear not available, using OpenCV fallback")

# Import freenect for Kinect
try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect (freenect) available for depth sensing")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect (freenect) not available")

class DualCameraSystem:
    """
    Comprehensive dual camera system using pre-made libraries
    Combines Kinect depth + multiple webcam RGB sources
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.webcam_streams = []
        self.active_cameras = {}
        self.frame_sync_buffer = {}
        self.running = False
        
        # Camera configurations from TensorFlow webcam patterns
        self.camera_configs = self._load_camera_configs()
        
        # Setup logging
        self.setup_logging()
        
        # Performance tracking
        self.frame_count = 0
        self.fps_tracker = time.time()
        self.current_fps = 0
    
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('dual_camera_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_camera_configs(self):
        """Load camera configurations using multiple detection methods"""
        configs = []
        
        # VidGear configurations (highest priority)
        if VIDGEAR_AVAILABLE:
            vidgear_configs = [
                {"source": 0, "backend": "vidgear", "method": "CamGear", "priority": 1},
                {"source": 1, "backend": "vidgear", "method": "CamGear", "priority": 2},
                {"source": 2, "backend": "vidgear", "method": "CamGear", "priority": 3},
                {"source": "usb://0", "backend": "vidgear", "method": "CamGear", "priority": 4},
                {"source": "usb://1", "backend": "vidgear", "method": "CamGear", "priority": 5},
            ]
            configs.extend(vidgear_configs)
        
        # OpenCV configurations (fallback)
        opencv_configs = [
            {"source": 0, "backend": "opencv", "method": "CAP_DSHOW", "priority": 10},
            {"source": 1, "backend": "opencv", "method": "CAP_DSHOW", "priority": 11},
            {"source": 2, "backend": "opencv", "method": "CAP_DSHOW", "priority": 12},
            {"source": 0, "backend": "opencv", "method": "CAP_V4L2", "priority": 13},
            {"source": 1, "backend": "opencv", "method": "CAP_V4L2", "priority": 14},
            {"source": 0, "backend": "opencv", "method": "CAP_ANY", "priority": 15},
            {"source": 1, "backend": "opencv", "method": "CAP_ANY", "priority": 16},
        ]
        configs.extend(opencv_configs)
        
        # Kinect RGB as webcam fallback
        if KINECT_AVAILABLE:
            kinect_config = {"source": "kinect_rgb", "backend": "freenect", "method": "sync_get_video", "priority": 20}
            configs.append(kinect_config)
        
        return sorted(configs, key=lambda x: x["priority"])
    
    def initialize_kinect_depth(self):
        """Initialize Kinect depth sensor using freenect"""
        if not KINECT_AVAILABLE:
            self.logger.warning("Kinect not available for depth sensing")
            return False
        
        try:
            # Test Kinect depth capture
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is not None:
                self.kinect_depth_active = True
                self.logger.info("[SUCCESS] Kinect depth sensor initialized")
                return True
            else:
                self.logger.error("[ERROR] Kinect depth test failed")
                return False
        except Exception as e:
            self.logger.error(f"[ERROR] Kinect depth initialization failed: {e}")
            return False
    
    def initialize_webcam_streams(self):
        """Initialize webcam streams using VidGear and OpenCV"""
        working_streams = []
        
        for config in self.camera_configs:
            try:
                self.logger.info(f"Testing camera config: {config}")
                
                if config["backend"] == "vidgear":
                    stream = self._init_vidgear_stream(config)
                elif config["backend"] == "opencv":
                    stream = self._init_opencv_stream(config)
                elif config["backend"] == "freenect":
                    stream = self._init_kinect_rgb_stream(config)
                else:
                    continue
                
                if stream:
                    stream_info = {
                        "stream": stream,
                        "config": config,
                        "index": len(working_streams),
                        "active": True
                    }
                    working_streams.append(stream_info)
                    self.logger.info(f"[SUCCESS] Camera stream {len(working_streams)} initialized")
                    
                    # Limit to 3 webcam streams for performance
                    if len(working_streams) >= 3:
                        break
                
            except Exception as e:
                self.logger.warning(f"[ERROR] Camera config failed: {e}")
        
        self.webcam_streams = working_streams
        return len(working_streams) > 0
    
    def _init_vidgear_stream(self, config):
        """Initialize VidGear CamGear stream"""
        if not VIDGEAR_AVAILABLE:
            return None
        
        try:
            # Create CamGear stream with TensorFlow-inspired parameters
            stream = CamGear(
                source=config["source"],
                colorspace="COLOR_BGR2RGB",
                resolution=(640, 480),
                framerate=30,
                logging=False
            ).start()
            
            # Test frame capture
            test_frame = stream.read()
            if test_frame is not None:
                return stream
            else:
                stream.stop()
                return None
                
        except Exception as e:
            self.logger.warning(f"VidGear stream init error: {e}")
            return None
    
    def _init_opencv_stream(self, config):
        """Initialize OpenCV stream with multiple backend support"""
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
                # Set properties following TensorFlow webcam patterns
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Test frame capture
                ret, frame = cap.read()
                if ret and frame is not None:
                    return cap
                else:
                    cap.release()
                    return None
            else:
                return None
                
        except Exception as e:
            self.logger.warning(f"OpenCV stream init error: {e}")
            return None
    
    def _init_kinect_rgb_stream(self, config):
        """Initialize Kinect RGB as webcam stream"""
        if not KINECT_AVAILABLE:
            return None
        
        try:
            # Test Kinect RGB capture
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is not None:
                self.kinect_rgb_active = True
                return "kinect_rgb"  # Special marker for Kinect RGB
            else:
                return None
        except Exception as e:
            self.logger.warning(f"Kinect RGB init error: {e}")
            return None
    
    def capture_synchronized_frame(self):
        """Capture synchronized frame from all active sources"""
        frame_data = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "webcam_streams": [],
            "sync_metadata": {}
        }
        
        # Capture Kinect depth
        if self.kinect_depth_active and KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                frame_data["kinect_depth"] = depth_frame
            except Exception as e:
                self.logger.warning(f"Kinect depth capture error: {e}")
        
        # Capture webcam streams
        for i, stream_info in enumerate(self.webcam_streams):
            try:
                config = stream_info["config"]
                
                if config["backend"] == "vidgear":
                    frame = stream_info["stream"].read()
                elif config["backend"] == "freenect":
                    frame = freenect.sync_get_video()[0]  # Kinect RGB
                else:  # OpenCV
                    ret, frame = stream_info["stream"].read()
                    if not ret:
                        frame = None
                
                if frame is not None:
                    webcam_data = {
                        "index": i,
                        "source": config["source"],
                        "backend": config["backend"],
                        "frame": frame,
                        "timestamp": time.time()
                    }
                    frame_data["webcam_streams"].append(webcam_data)
                
            except Exception as e:
                self.logger.warning(f"Webcam {i} capture error: {e}")
        
        # Add synchronization metadata
        frame_data["sync_metadata"] = {
            "total_sources": len(frame_data["webcam_streams"]) + (1 if frame_data["kinect_depth"] is not None else 0),
            "kinect_depth_active": frame_data["kinect_depth"] is not None,
            "webcam_count": len(frame_data["webcam_streams"]),
            "data_quality": "excellent" if len(frame_data["webcam_streams"]) >= 2 and frame_data["kinect_depth"] is not None else "good"
        }
        
        # Update performance tracking
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_tracker >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.fps_tracker)
            self.frame_count = 0
            self.fps_tracker = current_time
        
        frame_data["sync_metadata"]["fps"] = self.current_fps
        
        return frame_data
    
    def initialize_all_systems(self):
        """Initialize all camera systems"""
        self.logger.info("[INIT] Initializing Dual Camera System with pre-made libraries")
        
        # Step 1: Initialize Kinect depth
        kinect_success = self.initialize_kinect_depth()
        
        # Step 2: Initialize webcam streams
        webcam_success = self.initialize_webcam_streams()
        
        # Report results
        total_sources = (1 if kinect_success else 0) + len(self.webcam_streams)
        self.logger.info(f"[REPORT] Dual Camera System initialization complete:")
        self.logger.info(f"   Kinect depth: {'[SUCCESS]' if kinect_success else '[ERROR]'}")
        self.logger.info(f"   Webcam streams: {len(self.webcam_streams)}")
        self.logger.info(f"   Total sources: {total_sources}")
        
        if total_sources > 0:
            self.logger.info("[SUCCESS] Dual Camera System operational!")
            return True
        else:
            self.logger.error("[ERROR] No camera sources available!")
            return False
    
    def cleanup(self):
        """Clean up all camera resources"""
        self.logger.info("[CLEANUP] Shutting down Dual Camera System")
        
        for stream_info in self.webcam_streams:
            try:
                config = stream_info["config"]
                if config["backend"] == "vidgear":
                    stream_info["stream"].stop()
                elif hasattr(stream_info["stream"], "release"):
                    stream_info["stream"].release()
            except Exception as e:
                self.logger.warning(f"Cleanup error: {e}")
        
        self.webcam_streams.clear()
        self.kinect_depth_active = False
        self.kinect_rgb_active = False

def main():
    """Test the Dual Camera System"""
    print("[INIT] Testing Dual Camera System with pre-made libraries")
    print("="*60)
    
    dual_camera = DualCameraSystem()
    
    try:
        # Initialize all systems
        success = dual_camera.initialize_all_systems()
        
        if success:
            print("\n[SUCCESS] Dual Camera System operational!")
            print("[REPORT] Available data sources:")
            
            if dual_camera.kinect_depth_active:
                print("   [SUCCESS] Kinect depth sensor")
            if dual_camera.kinect_rgb_active:
                print("   [SUCCESS] Kinect RGB camera")
            
            for i, stream in enumerate(dual_camera.webcam_streams):
                config = stream["config"]
                print(f"   [SUCCESS] Webcam {i}: {config['backend']} ({config['source']})")
            
            # Test synchronized frame capture
            print("\n[TEST] Testing synchronized frame capture...")
            test_frame = dual_camera.capture_synchronized_frame()
            
            print(f"   Kinect depth: {'[SUCCESS]' if test_frame['kinect_depth'] is not None else '[ERROR]'}")
            print(f"   Webcam streams: {len(test_frame['webcam_streams'])}")
            print(f"   Data quality: {test_frame['sync_metadata']['data_quality']}")
            print(f"   Total sources: {test_frame['sync_metadata']['total_sources']}")
            
            return 0
        else:
            print("\n[ERROR] Dual Camera System initialization failed")
            return 1
            
    finally:
        dual_camera.cleanup()

if __name__ == "__main__":
    sys.exit(main())
