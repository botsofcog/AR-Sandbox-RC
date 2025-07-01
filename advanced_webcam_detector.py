#!/usr/bin/env python3
"""
Advanced Webcam Detection for AR Sandbox RC
Tries multiple methods to detect and connect webcams for Kinect + Webcam combo
"""

import cv2
import numpy as np
import sys
import time
import subprocess
import json
from pathlib import Path

class AdvancedWebcamDetector:
    def __init__(self):
        self.working_cameras = []
        self.tested_configs = []
        
    def list_windows_cameras(self):
        """Use Windows PowerShell to list available cameras"""
        try:
            print("🔍 Scanning Windows camera devices...")
            
            # PowerShell command to list camera devices
            ps_command = """
            Get-PnpDevice -Class Camera | Where-Object {$_.Status -eq "OK"} | 
            Select-Object FriendlyName, InstanceId, Status | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    devices = json.loads(result.stdout)
                    if not isinstance(devices, list):
                        devices = [devices]
                    
                    print(f"✅ Found {len(devices)} camera device(s):")
                    for i, device in enumerate(devices):
                        print(f"   {i}: {device.get('FriendlyName', 'Unknown')} - {device.get('Status', 'Unknown')}")
                    
                    return devices
                except json.JSONDecodeError:
                    print("⚠️ Could not parse PowerShell camera output")
            else:
                print("⚠️ PowerShell camera detection failed")
                
        except Exception as e:
            print(f"❌ Windows camera detection error: {e}")
        
        return []
    
    def try_opencv_backends(self):
        """Try different OpenCV backends systematically"""
        print("\n🎥 Testing OpenCV backends...")
        
        # Available backends to try
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_V4L2, "Video4Linux2"),
            (cv2.CAP_ANY, "Any Available"),
            (None, "Default")
        ]
        
        # Camera indices to try
        camera_indices = list(range(10))  # Try 0-9
        
        for backend_id, backend_name in backends:
            print(f"\n📹 Testing {backend_name} backend:")
            
            for cam_idx in camera_indices:
                try:
                    print(f"  Testing camera {cam_idx}...", end=" ")
                    
                    # Create capture object
                    if backend_id is None:
                        cap = cv2.VideoCapture(cam_idx)
                    else:
                        cap = cv2.VideoCapture(cam_idx, backend_id)
                    
                    # Set timeout for operations
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    if cap.isOpened():
                        # Try to read a frame with timeout
                        start_time = time.time()
                        ret, frame = cap.read()
                        read_time = time.time() - start_time
                        
                        if ret and frame is not None and read_time < 5.0:
                            height, width = frame.shape[:2]
                            
                            # Test if we can set properties
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            cap.set(cv2.CAP_PROP_FPS, 30)
                            
                            # Verify the camera works consistently
                            test_frames = 0
                            for _ in range(3):
                                ret2, frame2 = cap.read()
                                if ret2 and frame2 is not None:
                                    test_frames += 1
                                time.sleep(0.1)
                            
                            if test_frames >= 2:  # At least 2/3 frames successful
                                camera_info = {
                                    'index': cam_idx,
                                    'backend': backend_name,
                                    'backend_id': backend_id,
                                    'resolution': f"{width}x{height}",
                                    'working': True,
                                    'capture_object': cap  # Keep reference
                                }
                                
                                self.working_cameras.append(camera_info)
                                print(f"✅ WORKING - {width}x{height}")
                                
                                # Don't release this one yet - we'll use it
                                continue
                            else:
                                print("❌ Inconsistent frames")
                        else:
                            if read_time >= 5.0:
                                print("❌ Timeout")
                            else:
                                print("❌ No frames")
                    else:
                        print("❌ Failed to open")
                    
                    cap.release()
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    try:
                        cap.release()
                    except:
                        pass
        
        return len(self.working_cameras) > 0
    
    def try_alternative_methods(self):
        """Try alternative camera access methods"""
        print("\n🔧 Trying alternative camera access methods...")
        
        # Method 1: Try with specific camera names/paths
        camera_paths = [
            "/dev/video0", "/dev/video1", "/dev/video2",
            "0", "1", "2", "3", "4"
        ]
        
        for path in camera_paths:
            try:
                print(f"  Testing path '{path}'...", end=" ")
                cap = cv2.VideoCapture(path)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        
                        camera_info = {
                            'index': path,
                            'backend': 'Alternative Path',
                            'backend_id': None,
                            'resolution': f"{width}x{height}",
                            'working': True,
                            'capture_object': cap
                        }
                        
                        self.working_cameras.append(camera_info)
                        print(f"✅ WORKING - {width}x{height}")
                        continue
                    else:
                        print("❌ No frames")
                else:
                    print("❌ Failed to open")
                
                cap.release()
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def test_kinect_rgb_fallback(self):
        """Test if we can use Kinect RGB as webcam fallback"""
        print("\n📷 Testing Kinect RGB as webcam fallback...")
        
        try:
            # Try to import freenect
            import freenect
            
            # Test Kinect RGB capture
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is not None:
                print("✅ Kinect RGB available as webcam fallback")
                
                # Create a mock camera info for Kinect RGB
                camera_info = {
                    'index': 'kinect_rgb',
                    'backend': 'Kinect RGB',
                    'backend_id': 'freenect',
                    'resolution': '640x480',
                    'working': True,
                    'capture_object': 'kinect_rgb'  # Special marker
                }
                
                self.working_cameras.append(camera_info)
                return True
            else:
                print("❌ Kinect RGB not available")
                
        except ImportError:
            print("❌ Freenect not available")
        except Exception as e:
            print(f"❌ Kinect RGB error: {e}")
        
        return False
    
    def generate_report(self):
        """Generate comprehensive detection report"""
        print("\n" + "="*60)
        print("📊 ADVANCED WEBCAM DETECTION REPORT")
        print("="*60)
        
        if self.working_cameras:
            print(f"✅ Found {len(self.working_cameras)} working camera source(s):")
            
            for i, cam in enumerate(self.working_cameras):
                print(f"\n📹 Camera {i+1}:")
                print(f"   Index: {cam['index']}")
                print(f"   Backend: {cam['backend']}")
                print(f"   Resolution: {cam['resolution']}")
                print(f"   Status: {'✅ READY' if cam['working'] else '❌ FAILED'}")
            
            print(f"\n🎯 RECOMMENDED CONFIGURATION:")
            best_cam = self.working_cameras[0]
            print(f"   Primary Camera: {best_cam['backend']} (Index {best_cam['index']})")
            
            if len(self.working_cameras) > 1:
                second_cam = self.working_cameras[1]
                print(f"   Secondary Camera: {second_cam['backend']} (Index {second_cam['index']})")
            
            return True
        else:
            print("❌ NO WORKING CAMERAS DETECTED!")
            print("\n🔧 TROUBLESHOOTING STEPS:")
            print("   1. Check if any camera apps are running (close them)")
            print("   2. Unplug and replug USB webcam")
            print("   3. Try different USB ports (preferably USB 3.0)")
            print("   4. Update webcam drivers")
            print("   5. Test with Windows Camera app")
            print("   6. Check Device Manager for camera devices")
            
            return False
    
    def cleanup(self):
        """Clean up camera resources"""
        for cam in self.working_cameras:
            if hasattr(cam.get('capture_object'), 'release'):
                try:
                    cam['capture_object'].release()
                except:
                    pass

def main():
    """Run advanced webcam detection"""
    print("🚀 Advanced Webcam Detection for AR Sandbox RC")
    print("🎯 Goal: Enable Kinect + Webcam simultaneous operation")
    print("="*60)
    
    detector = AdvancedWebcamDetector()
    
    try:
        # Step 1: List Windows camera devices
        windows_cameras = detector.list_windows_cameras()
        
        # Step 2: Try OpenCV backends
        opencv_success = detector.try_opencv_backends()
        
        # Step 3: Try alternative methods if needed
        if not opencv_success:
            detector.try_alternative_methods()
        
        # Step 4: Test Kinect RGB fallback
        detector.test_kinect_rgb_fallback()
        
        # Step 5: Generate report
        success = detector.generate_report()
        
        return 0 if success else 1
        
    finally:
        detector.cleanup()

if __name__ == "__main__":
    sys.exit(main())
