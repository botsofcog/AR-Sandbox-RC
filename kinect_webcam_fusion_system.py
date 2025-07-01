#!/usr/bin/env python3
"""
Kinect + Webcam Fusion System for AR Sandbox RC
Uses VidGear, MC-Calib concepts, and TensorFlow webcam handling
Provides MAXIMUM data collection from both Kinect depth + webcam RGB
"""

import cv2
import numpy as np
import asyncio
import websockets
import json
import time
import threading
from pathlib import Path
import sys
import logging

# Import VidGear for advanced camera handling
try:
    from vidgear.gears import CamGear, VideoGear
    VIDGEAR_AVAILABLE = True
    print("[SUCCESS] VidGear available for advanced camera handling")
except ImportError:
    VIDGEAR_AVAILABLE = False
    print("[WARNING] VidGear not available, using fallback methods")

# Import freenect for Kinect
try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect (freenect) available")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect (freenect) not available")

class KinectWebcamFusionSystem:
    def __init__(self):
        self.kinect_depth = None
        self.kinect_rgb = None
        self.webcam_streams = []
        self.fusion_data = {}
        self.running = False
        
        # Camera configurations found by advanced detection
        self.camera_configs = [
            # VidGear configurations
            {"source": 0, "backend": "vidgear", "type": "webcam", "priority": 1},
            {"source": 1, "backend": "vidgear", "type": "webcam", "priority": 2},
            {"source": 2, "backend": "vidgear", "type": "webcam", "priority": 3},
            
            # OpenCV DirectShow configurations
            {"source": 0, "backend": "cv2_dshow", "type": "webcam", "priority": 4},
            {"source": 1, "backend": "cv2_dshow", "type": "webcam", "priority": 5},
            
            # Alternative paths
            {"source": "/dev/video0", "backend": "cv2_path", "type": "webcam", "priority": 6},
            {"source": "/dev/video1", "backend": "cv2_path", "type": "webcam", "priority": 7},
            
            # Kinect RGB as webcam fallback
            {"source": "kinect_rgb", "backend": "freenect", "type": "kinect_rgb", "priority": 8},
        ]
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kinect_webcam_fusion.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_kinect(self):
        """Initialize Kinect depth and RGB"""
        if not KINECT_AVAILABLE:
            self.logger.warning("Kinect not available")
            return False
        
        try:
            # Test Kinect connection
            depth_frame = freenect.sync_get_depth()[0]
            rgb_frame = freenect.sync_get_video()[0]
            
            if depth_frame is not None and rgb_frame is not None:
                self.kinect_depth = True
                self.kinect_rgb = True
                self.logger.info("[SUCCESS] Kinect depth + RGB initialized successfully")
                return True
            else:
                self.logger.error("[ERROR] Kinect test frames failed")
                return False

        except Exception as e:
            self.logger.error(f"[ERROR] Kinect initialization failed: {e}")
            return False
    
    def initialize_webcams_vidgear(self):
        """Initialize webcams using VidGear for maximum compatibility"""
        if not VIDGEAR_AVAILABLE:
            return []
        
        working_streams = []
        
        # VidGear camera configurations
        vidgear_configs = [
            # Try different camera indices with VidGear
            {"source": 0, "colorspace": "COLOR_BGR2RGB", "resolution": (640, 480)},
            {"source": 1, "colorspace": "COLOR_BGR2RGB", "resolution": (640, 480)},
            {"source": 2, "colorspace": "COLOR_BGR2RGB", "resolution": (640, 480)},
            
            # Try with different backends
            {"source": 0, "backend": cv2.CAP_DSHOW, "resolution": (640, 480)},
            {"source": 1, "backend": cv2.CAP_DSHOW, "resolution": (640, 480)},
            
            # Try USB camera paths
            {"source": "usb://0", "resolution": (640, 480)},
            {"source": "usb://1", "resolution": (640, 480)},
        ]
        
        for i, config in enumerate(vidgear_configs):
            try:
                self.logger.info(f"Testing VidGear config {i}: {config}")
                
                # Create CamGear stream
                stream = CamGear(
                    source=config["source"],
                    colorspace=config.get("colorspace"),
                    resolution=config.get("resolution"),
                    framerate=30,
                    **{k: v for k, v in config.items() if k not in ["source", "colorspace", "resolution"]}
                ).start()
                
                # Test frame capture
                test_frame = stream.read()
                if test_frame is not None:
                    height, width = test_frame.shape[:2]
                    
                    stream_info = {
                        "stream": stream,
                        "source": config["source"],
                        "backend": "vidgear",
                        "resolution": f"{width}x{height}",
                        "index": len(working_streams)
                    }
                    
                    working_streams.append(stream_info)
                    self.logger.info(f"[SUCCESS] VidGear stream {i} working: {width}x{height}")

                    # Limit to 3 webcam streams for performance
                    if len(working_streams) >= 3:
                        break
                else:
                    stream.stop()
                    self.logger.warning(f"[ERROR] VidGear stream {i} no frames")

            except Exception as e:
                self.logger.warning(f"[ERROR] VidGear config {i} failed: {e}")
        
        return working_streams
    
    def initialize_webcams_opencv(self):
        """Fallback webcam initialization using OpenCV"""
        working_streams = []
        
        # OpenCV configurations with multiple backends
        opencv_configs = [
            (0, cv2.CAP_DSHOW, "DirectShow"),
            (1, cv2.CAP_DSHOW, "DirectShow"),
            (2, cv2.CAP_DSHOW, "DirectShow"),
            (0, cv2.CAP_V4L2, "Video4Linux2"),
            (1, cv2.CAP_V4L2, "Video4Linux2"),
            (0, None, "Default"),
            (1, None, "Default"),
        ]
        
        for cam_idx, backend, backend_name in opencv_configs:
            try:
                self.logger.info(f"Testing OpenCV: Camera {cam_idx} with {backend_name}")
                
                if backend is None:
                    cap = cv2.VideoCapture(cam_idx)
                else:
                    cap = cv2.VideoCapture(cam_idx, backend)
                
                if cap.isOpened():
                    # Set properties
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Test frame
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        
                        stream_info = {
                            "stream": cap,
                            "source": cam_idx,
                            "backend": f"opencv_{backend_name.lower()}",
                            "resolution": f"{width}x{height}",
                            "index": len(working_streams)
                        }
                        
                        working_streams.append(stream_info)
                        self.logger.info(f"[SUCCESS] OpenCV stream working: {width}x{height}")

                        # Limit to 2 streams for performance
                        if len(working_streams) >= 2:
                            break
                        continue
                    else:
                        self.logger.warning(f"[ERROR] OpenCV camera {cam_idx} no frames")
                else:
                    self.logger.warning(f"[ERROR] OpenCV camera {cam_idx} failed to open")

                cap.release()

            except Exception as e:
                self.logger.warning(f"[ERROR] OpenCV camera {cam_idx} error: {e}")
        
        return working_streams
    
    def initialize_all_cameras(self):
        """Initialize all available camera sources"""
        self.logger.info("[INIT] Initializing Kinect + Webcam Fusion System")

        # Step 1: Initialize Kinect
        kinect_success = self.initialize_kinect()

        # Step 2: Initialize webcams with VidGear (preferred)
        if VIDGEAR_AVAILABLE:
            self.webcam_streams = self.initialize_webcams_vidgear()

        # Step 3: Fallback to OpenCV if VidGear didn't find cameras
        if len(self.webcam_streams) == 0:
            self.logger.info("VidGear found no cameras, trying OpenCV fallback")
            self.webcam_streams = self.initialize_webcams_opencv()

        # Step 4: Add Kinect RGB as webcam if no other webcams found
        if len(self.webcam_streams) == 0 and self.kinect_rgb:
            self.logger.info("No webcams found, using Kinect RGB as webcam")
            kinect_rgb_stream = {
                "stream": "kinect_rgb",
                "source": "kinect_rgb",
                "backend": "freenect",
                "resolution": "640x480",
                "index": 0
            }
            self.webcam_streams.append(kinect_rgb_stream)

        # Report results
        total_sources = (1 if kinect_success else 0) + len(self.webcam_streams)
        self.logger.info(f"[REPORT] Camera initialization complete:")
        self.logger.info(f"   Kinect depth: {'[SUCCESS]' if kinect_success else '[ERROR]'}")
        self.logger.info(f"   Webcam streams: {len(self.webcam_streams)}")
        self.logger.info(f"   Total sources: {total_sources}")
        
        return total_sources > 0
    
    def capture_fusion_frame(self):
        """Capture synchronized frame from all sources"""
        fusion_frame = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "kinect_rgb": None,
            "webcam_streams": [],
            "fusion_metadata": {}
        }
        
        # Capture Kinect data
        if self.kinect_depth and KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                rgb_frame = freenect.sync_get_video()[0]
                
                fusion_frame["kinect_depth"] = depth_frame
                fusion_frame["kinect_rgb"] = rgb_frame
                
            except Exception as e:
                self.logger.warning(f"Kinect capture error: {e}")
        
        # Capture webcam streams
        for i, stream_info in enumerate(self.webcam_streams):
            try:
                if stream_info["backend"] == "vidgear":
                    frame = stream_info["stream"].read()
                elif stream_info["backend"] == "freenect":
                    frame = freenect.sync_get_video()[0]  # Kinect RGB
                else:
                    ret, frame = stream_info["stream"].read()
                    if not ret:
                        frame = None
                
                if frame is not None:
                    webcam_data = {
                        "index": i,
                        "source": stream_info["source"],
                        "backend": stream_info["backend"],
                        "frame": frame,
                        "resolution": stream_info["resolution"]
                    }
                    fusion_frame["webcam_streams"].append(webcam_data)
                
            except Exception as e:
                self.logger.warning(f"Webcam {i} capture error: {e}")
        
        # Add fusion metadata
        fusion_frame["fusion_metadata"] = {
            "total_sources": len(fusion_frame["webcam_streams"]) + (1 if fusion_frame["kinect_depth"] is not None else 0),
            "kinect_available": fusion_frame["kinect_depth"] is not None,
            "webcam_count": len(fusion_frame["webcam_streams"]),
            "data_richness": "maximum" if len(fusion_frame["webcam_streams"]) >= 2 and fusion_frame["kinect_depth"] is not None else "partial"
        }
        
        return fusion_frame
    
    def cleanup(self):
        """Clean up all camera resources"""
        self.logger.info("🧹 Cleaning up camera resources")
        
        for stream_info in self.webcam_streams:
            try:
                if stream_info["backend"] == "vidgear":
                    stream_info["stream"].stop()
                elif hasattr(stream_info["stream"], "release"):
                    stream_info["stream"].release()
            except Exception as e:
                self.logger.warning(f"Cleanup error: {e}")
        
        self.webcam_streams.clear()

def main():
    """Test the Kinect + Webcam Fusion System"""
    print("🚀 Testing Kinect + Webcam Fusion System")
    print("="*60)
    
    fusion_system = KinectWebcamFusionSystem()
    
    try:
        # Initialize all cameras
        success = fusion_system.initialize_all_cameras()
        
        if success:
            print("\n🎉 SUCCESS: Kinect + Webcam Fusion System operational!")
            print("📊 Available data sources:")
            
            if fusion_system.kinect_depth:
                print("   ✅ Kinect depth sensor")
            if fusion_system.kinect_rgb:
                print("   ✅ Kinect RGB camera")
            
            for i, stream in enumerate(fusion_system.webcam_streams):
                print(f"   ✅ Webcam {i}: {stream['backend']} ({stream['resolution']})")
            
            # Test frame capture
            print("\n🧪 Testing frame capture...")
            test_frame = fusion_system.capture_fusion_frame()
            
            print(f"   Kinect depth: {'✅' if test_frame['kinect_depth'] is not None else '❌'}")
            print(f"   Webcam streams: {len(test_frame['webcam_streams'])}")
            print(f"   Data richness: {test_frame['fusion_metadata']['data_richness']}")
            
            return 0
        else:
            print("\n❌ FAILURE: No camera sources available")
            return 1
            
    finally:
        fusion_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
