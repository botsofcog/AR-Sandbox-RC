#!/usr/bin/env python3
"""
Threaded Triple Camera System for AR Sandbox RC
Uses proven multi-camera threading solution from python-examples-cv
Handles: Kinect depth + Kinect RGB + Logitech C925e with proper threading
"""

import sys
import os
import time
import cv2
import numpy as np
from threading import Thread

# Add the proven camera streaming solution to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'python-examples-cv'))

try:
    import camera_stream
    CAMERA_STREAM_AVAILABLE = True
    print("[SUCCESS] Proven camera streaming solution available")
except ImportError:
    CAMERA_STREAM_AVAILABLE = False
    print("[WARNING] Camera streaming solution not available")

try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect (freenect) available")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect (freenect) not available")

class ThreadedTripleCameraSystem:
    """
    Triple Camera System using proven threading solution
    Handles simultaneous access to multiple cameras without conflicts
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.logitech_active = False
        
        self.kinect_depth_stream = None
        self.kinect_rgb_stream = None
        self.logitech_stream = None
        
        self.running = False
        
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
    
    def initialize_logitech_camera_threaded(self):
        """Initialize Logitech C925e using proven threading solution"""
        if not CAMERA_STREAM_AVAILABLE:
            print("[ERROR] Camera streaming solution not available")
            return False
        
        print("[INIT] Initializing Logitech C925e using proven threading solution...")
        
        # Try different camera indices with the proven solution
        camera_indices = [0, 1, 2, 3, 4]
        
        for cam_idx in camera_indices:
            try:
                print(f"   Testing camera index {cam_idx} with threaded capture...")
                
                # Create threaded camera stream using proven solution
                stream = camera_stream.CameraVideoStream(
                    src=cam_idx,
                    backend=cv2.CAP_DSHOW,  # Force DirectShow for Windows
                    name=f"LogitechC925e_{cam_idx}"
                )
                
                # Test if camera opened successfully
                if stream.grabbed > 0:
                    # Test frame capture
                    test_frame = stream.read()
                    if test_frame is not None and test_frame.size > 0:
                        height, width = test_frame.shape[:2]
                        print(f"   [SUCCESS] Logitech C925e initialized on index {cam_idx}: {width}x{height}")
                        
                        # Set camera properties for optimal performance
                        if hasattr(stream, 'camera'):
                            stream.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            stream.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            stream.camera.set(cv2.CAP_PROP_FPS, 30)
                            stream.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                            stream.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        self.logitech_stream = stream
                        self.logitech_active = True
                        return True
                    else:
                        stream.stop()
                else:
                    print(f"   Camera index {cam_idx} failed to open")
                    
            except Exception as e:
                print(f"   Camera index {cam_idx} failed: {e}")
        
        print("[ERROR] Logitech C925e initialization failed on all indices")
        return False
    
    def capture_triple_threaded_frame(self):
        """Capture synchronized frame from all three threaded sources"""
        triple_frame = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "kinect_rgb": None,
            "logitech_frame": None,
            "threading_metadata": {}
        }
        
        # Capture Kinect depth (non-threaded, direct access)
        if self.kinect_depth_active and KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                triple_frame["kinect_depth"] = depth_frame
            except Exception as e:
                print(f"Kinect depth capture error: {e}")
        
        # Capture Kinect RGB (non-threaded, direct access)
        if self.kinect_rgb_active and KINECT_AVAILABLE:
            try:
                rgb_frame = freenect.sync_get_video()[0]
                triple_frame["kinect_rgb"] = rgb_frame
            except Exception as e:
                print(f"Kinect RGB capture error: {e}")
        
        # Capture Logitech camera (threaded access)
        if self.logitech_active and self.logitech_stream:
            try:
                logitech_frame = self.logitech_stream.read()
                if logitech_frame is not None:
                    triple_frame["logitech_frame"] = logitech_frame
            except Exception as e:
                print(f"Logitech capture error: {e}")
        
        # Generate threading metadata
        active_sources = []
        if triple_frame["kinect_depth"] is not None:
            active_sources.append("kinect_depth")
        if triple_frame["kinect_rgb"] is not None:
            active_sources.append("kinect_rgb")
        if triple_frame["logitech_frame"] is not None:
            active_sources.append("logitech_frame")
        
        triple_frame["threading_metadata"] = {
            "total_sources": len(active_sources),
            "active_sources": active_sources,
            "multi_axis_coverage": "logitech_frame" in active_sources and len(active_sources) >= 2,
            "integration_level": f"{(len(active_sources)/3)*100:.0f}%",
            "threading_solution": "proven_multi_camera",
            "kinect_direct_access": self.kinect_depth_active or self.kinect_rgb_active,
            "logitech_threaded_access": self.logitech_active
        }
        
        return triple_frame
    
    def initialize_all_systems(self):
        """Initialize complete threaded triple camera system"""
        print("="*60)
        print("THREADED TRIPLE CAMERA SYSTEM - Proven Solution")
        print("="*60)
        
        # Initialize Kinect sensors (direct access)
        kinect_depth_ok, kinect_rgb_ok = self.initialize_kinect_sensors()
        
        # Initialize Logitech camera (threaded access)
        logitech_ok = self.initialize_logitech_camera_threaded()
        
        # Report results
        active_cameras = sum([kinect_depth_ok, kinect_rgb_ok, logitech_ok])
        
        print(f"\n[REPORT] Threaded Triple Camera System:")
        print(f"   Kinect depth sensor: {'[ACTIVE]' if kinect_depth_ok else '[INACTIVE]'}")
        print(f"   Kinect RGB camera: {'[ACTIVE]' if kinect_rgb_ok else '[INACTIVE]'}")
        print(f"   Logitech C925e (threaded): {'[ACTIVE]' if logitech_ok else '[INACTIVE]'}")
        print(f"   Total active cameras: {active_cameras}/3")
        print(f"   Multi-axis coverage: {'[YES]' if logitech_ok and (kinect_depth_ok or kinect_rgb_ok) else '[NO]'}")
        print(f"   Threading solution: {'[PROVEN]' if CAMERA_STREAM_AVAILABLE else '[BASIC]'}")
        
        if active_cameras == 3:
            print("[SUCCESS] 🎉 ALL 3 CAMERAS OPERATIONAL - 110% INTEGRATION ACHIEVED!")
            return True
        elif active_cameras >= 2:
            print("[PARTIAL] Dual camera system operational")
            return True
        else:
            print("[ERROR] Insufficient cameras")
            return False
    
    def cleanup(self):
        """Clean up all camera resources"""
        print("[CLEANUP] Threaded Triple Camera System")
        
        if self.logitech_stream:
            try:
                self.logitech_stream.stop()
                print("   Logitech threaded stream stopped")
            except Exception as e:
                print(f"   Logitech cleanup error: {e}")
        
        # Cleanup any remaining threads
        if CAMERA_STREAM_AVAILABLE:
            try:
                camera_stream.closeDownAllThreadsCleanly()
                print("   All camera threads cleaned up")
            except Exception as e:
                print(f"   Thread cleanup error: {e}")

def main():
    """Test Threaded Triple Camera System"""
    triple_system = ThreadedTripleCameraSystem()
    
    try:
        # Initialize all systems
        success = triple_system.initialize_all_systems()
        
        if success:
            print("\n[TEST] Testing threaded triple frame capture...")
            
            # Test multiple frame captures
            for i in range(5):
                test_frame = triple_system.capture_triple_threaded_frame()
                metadata = test_frame["threading_metadata"]
                
                print(f"   Frame {i+1}: {metadata['active_sources']} - {metadata['integration_level']}")
                
                if metadata["total_sources"] == 3:
                    print(f"   🎉 PERFECT! All 3 cameras captured successfully!")
                
                time.sleep(0.5)  # Test sustained capture
            
            metadata = test_frame["threading_metadata"]
            print(f"\n[FINAL REPORT]")
            print(f"   Active sources: {metadata['active_sources']}")
            print(f"   Multi-axis coverage: {'[YES]' if metadata['multi_axis_coverage'] else '[NO]'}")
            print(f"   Integration level: {metadata['integration_level']}")
            print(f"   Threading solution: {metadata['threading_solution']}")
            
            if metadata["total_sources"] == 3:
                print(f"\n🚀 SUCCESS: 3-CAMERA SYSTEM FULLY OPERATIONAL!")
                print(f"   ✅ Kinect depth sensor (axis 1)")
                print(f"   ✅ Kinect RGB camera (axis 1)")
                print(f"   ✅ Logitech C925e webcam (axis 2)")
                print(f"   🎯 110% INTEGRATION ACHIEVED!")
            
            return 0
        else:
            print("\n[ERROR] Threaded Triple Camera System initialization failed")
            return 1
            
    finally:
        triple_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
