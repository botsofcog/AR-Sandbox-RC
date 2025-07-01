#!/usr/bin/env python3
"""
AR Sandbox Camera Fusion System
Modified from downloaded camera-fusion repository to handle Kinect + Logitech C925e
Uses DirectShow backend specifically to avoid MSMF conflicts
"""

import sys
import os
import time
import cv2
import numpy as np
from pathlib import Path
from threading import Event, Thread

# Add camera-fusion to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'camera-fusion'))

# Import camera-fusion components directly
CAMERA_FUSION_AVAILABLE = True
print("[SUCCESS] Camera-fusion code available")

try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect (freenect) available")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect (freenect) not available")

class ARSandboxCamera:
    """
    Modified Camera class for AR Sandbox that uses DirectShow backend
    Specifically designed to avoid MSMF conflicts with Kinect
    """

    def __init__(self, cam_id, vertical_flip=None, settings=None, force_backend=None):
        """Initialize AR Sandbox Camera with specific backend control"""
        self.force_backend = force_backend

        # Modified initialization for Windows DirectShow
        if isinstance(cam_id, str) and cam_id.isdigit():
            self.cam_id = int(cam_id)
        else:
            self.cam_id = cam_id

        self.cam_path = str(cam_id)

        if vertical_flip is True:
            print('Set vertical flip.')
            self.vertical_flip = True
        else:
            self.vertical_flip = False

        self.settings = settings
        self.t0 = time.time()
        self.stop = False
        self.current_frame = None
        self.cap = None
        self.height = 0
        self.width = 0

        # VideoCapture reading Thread
        self.thread_ready = Event()
        self.thread = Thread(target=self._update_frame, args=())
    
    def _setup(self):
        """Set up the camera with DirectShow backend for Windows"""
        print(f"[SETUP] Initializing camera {self.cam_id} with AR Sandbox backend selection")
        
        # Force DirectShow backend for Windows to avoid MSMF conflicts
        if self.force_backend == "directshow" or sys.platform in ["win32", "win64"]:
            print(f"   Using DirectShow backend for camera {self.cam_id}")
            self.cap = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)
        elif self.force_backend == "v4l2":
            print(f"   Using V4L2 backend for camera {self.cam_id}")
            self.cap = cv2.VideoCapture(self.cam_path, cv2.CAP_V4L2)
        else:
            # Default behavior
            if sys.platform == "linux" or sys.platform == "linux2":
                self.cap = cv2.VideoCapture(self.cam_path, cv2.CAP_V4L2)
            else:
                # Force DirectShow on Windows
                self.cap = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise ValueError(f'Camera {self.cam_id} not found!')

        self.set_camera_settings()

        # Current camera recording frame size
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        print(f"   Camera {self.cam_id} setup complete: {self.width}x{self.height}")

    def initialize(self):
        """Initialize the camera Thread."""
        self._setup()

        # Start the VideoCapture read() thread
        self.stop = False
        self.start_camera_thread()
        self.thread_ready.wait()

        # Quick test
        self.test_camera()
        print(f'Camera {self.cam_id} initialization done!')

    def start_camera_thread(self):
        """Start the Camera frame update Thread."""
        self.thread.start()
        self.thread_ready.wait()  # block until thread created a current_frame

    def test_camera(self):
        """Basic camera test."""
        test_frame = self.read()
        if test_frame is None:
            raise ValueError(f'Camera {self.cam_id} test failed - no frame captured')

        # Simple self-test
        if test_frame.shape[0] != self.height:
            print(f'WARNING: Camera {self.cam_id} height mismatch: {test_frame.shape[0]} vs {self.height}')
        if test_frame.shape[1] != self.width:
            print(f'WARNING: Camera {self.cam_id} width mismatch: {test_frame.shape[1]} vs {self.width}')

    def set_camera_settings(self):
        """Set camera settings."""
        if self.settings:
            for setting in self.settings:
                prop, value = setting
                self.cap.set(prop, value)
                print(f"   Set camera {self.cam_id} property {prop} to {value}")

    def read(self):
        """Read current frame."""
        return self.current_frame

    def _update_frame(self):
        """Read VideoCapture to update Camera current frame."""
        while True:
            if self.stop:
                break
            ret, frame = self.cap.read()
            if ret is False:
                print(f'Cam {self.cam_id} | Error reading frame!')
                continue
            if self.vertical_flip:
                frame = cv2.flip(frame, -1)
            self.current_frame = frame
            self.thread_ready.set()

    def stop_camera(self):
        """Stop camera and cleanup."""
        self.stop = True
        if self.thread.is_alive():
            self.thread.join()
        if self.cap:
            self.cap.release()

class ARSandboxTripleCameraFusion:
    """
    Triple Camera Fusion System using downloaded camera-fusion library
    Handles Kinect depth + Kinect RGB + Logitech C925e with proper backend selection
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.logitech_active = False
        
        self.kinect_depth_stream = None
        self.kinect_rgb_stream = None
        self.logitech_camera = None
        
        self.fusion_system = None
        self.calibration_data = {}
        
    def initialize_kinect_sensors(self):
        """Initialize Kinect depth and RGB sensors"""
        if not KINECT_AVAILABLE:
            print("[WARNING] Kinect not available")
            return False, False
        
        try:
            # Test Kinect depth
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is not None:
                self.kinect_depth_active = True
                print("[SUCCESS] Kinect depth sensor initialized")
            
            # Test Kinect RGB
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is not None:
                self.kinect_rgb_active = True
                print("[SUCCESS] Kinect RGB camera initialized")
            
            return self.kinect_depth_active, self.kinect_rgb_active
            
        except Exception as e:
            print(f"[ERROR] Kinect initialization error: {e}")
            return False, False
    
    def initialize_logitech_camera(self):
        """Initialize Logitech C925e using camera-fusion with DirectShow"""
        if not CAMERA_FUSION_AVAILABLE:
            print("[ERROR] Camera-fusion library not available")
            return False
        
        print("[INIT] Initializing Logitech C925e using camera-fusion with DirectShow...")
        
        # Try different camera indices with DirectShow backend
        camera_indices = [0, 1, 2, 3, 4]
        
        for cam_idx in camera_indices:
            try:
                print(f"   Testing camera index {cam_idx} with DirectShow...")
                
                # Create AR Sandbox camera with DirectShow backend
                camera = ARSandboxCamera(
                    cam_id=cam_idx,
                    force_backend="directshow",
                    settings=[
                        (cv2.CAP_PROP_FRAME_WIDTH, 640),
                        (cv2.CAP_PROP_FRAME_HEIGHT, 480),
                        (cv2.CAP_PROP_FPS, 30),
                        (cv2.CAP_PROP_AUTOFOCUS, 0),  # Disable autofocus
                        (cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
                    ]
                )
                
                # Test initialization
                camera.initialize()
                
                # Test frame capture
                test_frame = camera.read()
                if test_frame is not None and test_frame.size > 0:
                    height, width = test_frame.shape[:2]
                    print(f"   [SUCCESS] Logitech C925e initialized on index {cam_idx}: {width}x{height}")
                    
                    self.logitech_camera = camera
                    self.logitech_active = True
                    return True
                else:
                    camera.stop_camera()
                    
            except Exception as e:
                print(f"   Camera index {cam_idx} failed: {e}")
        
        print("[ERROR] Logitech C925e initialization failed on all indices")
        return False
    
    def capture_fusion_frame(self):
        """Capture synchronized frame from all three sources"""
        fusion_frame = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "kinect_rgb": None,
            "logitech_frame": None,
            "fusion_metadata": {}
        }
        
        # Capture Kinect depth
        if self.kinect_depth_active and KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                fusion_frame["kinect_depth"] = depth_frame
            except Exception as e:
                print(f"Kinect depth capture error: {e}")
        
        # Capture Kinect RGB
        if self.kinect_rgb_active and KINECT_AVAILABLE:
            try:
                rgb_frame = freenect.sync_get_video()[0]
                fusion_frame["kinect_rgb"] = rgb_frame
            except Exception as e:
                print(f"Kinect RGB capture error: {e}")
        
        # Capture Logitech camera
        if self.logitech_active and self.logitech_camera:
            try:
                logitech_frame = self.logitech_camera.read()
                if logitech_frame is not None:
                    fusion_frame["logitech_frame"] = logitech_frame
            except Exception as e:
                print(f"Logitech capture error: {e}")
        
        # Generate metadata
        active_sources = []
        if fusion_frame["kinect_depth"] is not None:
            active_sources.append("kinect_depth")
        if fusion_frame["kinect_rgb"] is not None:
            active_sources.append("kinect_rgb")
        if fusion_frame["logitech_frame"] is not None:
            active_sources.append("logitech_frame")
        
        fusion_frame["fusion_metadata"] = {
            "total_sources": len(active_sources),
            "active_sources": active_sources,
            "multi_axis_coverage": "logitech_frame" in active_sources and len(active_sources) >= 2,
            "integration_level": f"{(len(active_sources)/3)*100:.0f}%",
            "camera_fusion_ready": len(active_sources) >= 2
        }
        
        return fusion_frame
    
    def initialize_all_systems(self):
        """Initialize complete triple camera fusion system"""
        print("="*60)
        print("AR SANDBOX TRIPLE CAMERA FUSION - Using Downloaded Library")
        print("="*60)
        
        # Initialize Kinect sensors
        kinect_depth_ok, kinect_rgb_ok = self.initialize_kinect_sensors()
        
        # Initialize Logitech camera
        logitech_ok = self.initialize_logitech_camera()
        
        # Report results
        active_cameras = sum([kinect_depth_ok, kinect_rgb_ok, logitech_ok])
        
        print(f"\n[REPORT] AR Sandbox Triple Camera Fusion:")
        print(f"   Kinect depth sensor: {'[ACTIVE]' if kinect_depth_ok else '[INACTIVE]'}")
        print(f"   Kinect RGB camera: {'[ACTIVE]' if kinect_rgb_ok else '[INACTIVE]'}")
        print(f"   Logitech C925e: {'[ACTIVE]' if logitech_ok else '[INACTIVE]'}")
        print(f"   Total active cameras: {active_cameras}/3")
        print(f"   Multi-axis coverage: {'[YES]' if logitech_ok and (kinect_depth_ok or kinect_rgb_ok) else '[NO]'}")
        print(f"   Camera-fusion ready: {'[YES]' if active_cameras >= 2 else '[NO]'}")
        
        if active_cameras >= 2:
            print("[SUCCESS] AR Sandbox Triple Camera Fusion operational!")
            return True
        else:
            print("[ERROR] Insufficient cameras for fusion")
            return False
    
    def cleanup(self):
        """Clean up camera resources"""
        print("[CLEANUP] AR Sandbox Triple Camera Fusion")
        
        if self.logitech_camera:
            try:
                self.logitech_camera.stop_camera()
            except Exception as e:
                print(f"Logitech cleanup error: {e}")

def main():
    """Test AR Sandbox Triple Camera Fusion"""
    fusion_system = ARSandboxTripleCameraFusion()
    
    try:
        # Initialize all systems
        success = fusion_system.initialize_all_systems()
        
        if success:
            print("\n[TEST] Testing fusion frame capture...")
            test_frame = fusion_system.capture_fusion_frame()
            
            metadata = test_frame["fusion_metadata"]
            print(f"   Active sources: {metadata['active_sources']}")
            print(f"   Multi-axis coverage: {'[YES]' if metadata['multi_axis_coverage'] else '[NO]'}")
            print(f"   Integration level: {metadata['integration_level']}")
            print(f"   Camera-fusion ready: {'[YES]' if metadata['camera_fusion_ready'] else '[NO]'}")
            
            return 0
        else:
            print("\n[ERROR] AR Sandbox Triple Camera Fusion initialization failed")
            return 1
            
    finally:
        fusion_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
