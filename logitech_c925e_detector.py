#!/usr/bin/env python3
"""
Logitech C925e Detector using Pre-made Libraries
Uses downloaded RobustCameraDetector + Windows WMI + VidGear + GitHub solutions
"""

import cv2
import numpy as np
import subprocess
import time
import sys
import os
from pathlib import Path

# Import pre-made solutions
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_libs', 'vidgear'))

try:
    from robust_camera_detector import RobustCameraDetector
    ROBUST_DETECTOR_AVAILABLE = True
    print("[SUCCESS] RobustCameraDetector available")
except ImportError:
    ROBUST_DETECTOR_AVAILABLE = False
    print("[WARNING] RobustCameraDetector not available")

try:
    from vidgear.gears import CamGear, VideoGear
    VIDGEAR_AVAILABLE = True
    print("[SUCCESS] VidGear available")
except ImportError:
    VIDGEAR_AVAILABLE = False
    print("[WARNING] VidGear not available")

class LogitechC925eDetector:
    """
    Comprehensive Logitech C925e detection using all available pre-made solutions
    """
    
    def __init__(self):
        self.detected_cameras = []
        self.logitech_cameras = []
        self.working_stream = None
        
    def detect_using_windows_wmi(self):
        """Use Windows WMI to detect Logitech cameras"""
        print("\n[DETECT] Using Windows WMI detection...")
        
        try:
            # PowerShell command to find Logitech cameras specifically
            ps_command = """
            Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                $_.Name -like '*Logitech*' -or 
                $_.Name -like '*C925e*' -or 
                $_.Name -like '*webcam*' -or 
                $_.Name -like '*camera*'
            } | Select-Object Name, DeviceID, Status | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    devices = json.loads(result.stdout)
                    if not isinstance(devices, list):
                        devices = [devices]
                    
                    print(f"   Found {len(devices)} camera device(s):")
                    for i, device in enumerate(devices):
                        name = device.get('Name', 'Unknown')
                        status = device.get('Status', 'Unknown')
                        device_id = device.get('DeviceID', 'Unknown')
                        
                        print(f"   {i}: {name} - {status}")
                        
                        # Check if it's a Logitech camera
                        if 'logitech' in name.lower() or 'c925' in name.lower():
                            self.logitech_cameras.append({
                                'name': name,
                                'device_id': device_id,
                                'status': status,
                                'method': 'windows_wmi'
                            })
                            print(f"      [LOGITECH DETECTED] {name}")
                    
                    return len(self.logitech_cameras) > 0
                    
                except json.JSONDecodeError as e:
                    print(f"   [ERROR] JSON decode error: {e}")
                    return False
            else:
                print("   [ERROR] PowerShell WMI query failed")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Windows WMI detection failed: {e}")
            return False
    
    def detect_using_robust_detector(self):
        """Use the downloaded RobustCameraDetector"""
        if not ROBUST_DETECTOR_AVAILABLE:
            return False
        
        print("\n[DETECT] Using RobustCameraDetector...")
        
        try:
            detector = RobustCameraDetector()
            cameras = detector.enumerate_all_cameras()
            
            print(f"   RobustCameraDetector found {len(cameras)} camera(s):")
            for camera in cameras:
                print(f"   Index {camera.get('index', '?')}: {camera.get('method', 'unknown')} - {camera.get('backend', 'unknown')}")
                
                # Test if this could be the Logitech
                if camera.get('working', False):
                    self.detected_cameras.append(camera)
            
            return len(self.detected_cameras) > 0
            
        except Exception as e:
            print(f"   [ERROR] RobustCameraDetector failed: {e}")
            return False
    
    def test_direct_camera_access(self):
        """Test direct camera access with multiple methods"""
        print("\n[DETECT] Testing direct camera access...")
        
        # Test configurations specifically for Logitech C925e
        test_configs = [
            # VidGear configurations
            {"source": 0, "method": "vidgear", "backend": "CamGear"},
            {"source": 1, "method": "vidgear", "backend": "CamGear"},
            {"source": 2, "method": "vidgear", "backend": "CamGear"},
            
            # OpenCV with specific backends
            {"source": 0, "method": "opencv", "backend": cv2.CAP_DSHOW},
            {"source": 1, "method": "opencv", "backend": cv2.CAP_DSHOW},
            {"source": 2, "method": "opencv", "backend": cv2.CAP_DSHOW},
            {"source": 0, "method": "opencv", "backend": cv2.CAP_MSMF},
            {"source": 1, "method": "opencv", "backend": cv2.CAP_MSMF},
            {"source": 0, "method": "opencv", "backend": cv2.CAP_ANY},
            {"source": 1, "method": "opencv", "backend": cv2.CAP_ANY},
            
            # Alternative sources
            {"source": "/dev/video0", "method": "opencv", "backend": None},
            {"source": "/dev/video1", "method": "opencv", "backend": None},
        ]
        
        for i, config in enumerate(test_configs):
            try:
                print(f"   Testing config {i+1}: {config['method']} source {config['source']}")
                
                if config["method"] == "vidgear" and VIDGEAR_AVAILABLE:
                    success = self._test_vidgear_config(config)
                elif config["method"] == "opencv":
                    success = self._test_opencv_config(config)
                else:
                    continue
                
                if success:
                    print(f"   [SUCCESS] Found working Logitech camera with config {i+1}")
                    return True
                    
            except Exception as e:
                print(f"   Config {i+1} failed: {e}")
        
        return False
    
    def _test_vidgear_config(self, config):
        """Test VidGear configuration"""
        if not VIDGEAR_AVAILABLE:
            return False
        
        try:
            stream = CamGear(
                source=config["source"],
                colorspace="COLOR_BGR2RGB",
                logging=False
            ).start()
            
            # Test frame capture
            test_frame = stream.read()
            if test_frame is not None and test_frame.size > 0:
                height, width = test_frame.shape[:2]
                print(f"      VidGear success: {width}x{height}")
                
                # Keep this stream if it's working
                if self.working_stream is None:
                    self.working_stream = stream
                    return True
                else:
                    stream.stop()
                    return True
            else:
                stream.stop()
                return False
                
        except Exception as e:
            print(f"      VidGear error: {e}")
            return False
    
    def _test_opencv_config(self, config):
        """Test OpenCV configuration"""
        try:
            if config["backend"] is None:
                cap = cv2.VideoCapture(config["source"])
            else:
                cap = cv2.VideoCapture(config["source"], config["backend"])
            
            if cap.isOpened():
                # Set properties for Logitech C925e
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # C925e supports 1080p
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                
                # Test frame capture
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    height, width = frame.shape[:2]
                    print(f"      OpenCV success: {width}x{height}")
                    
                    # Keep this stream if it's working
                    if self.working_stream is None:
                        self.working_stream = cap
                        return True
                    else:
                        cap.release()
                        return True
                else:
                    cap.release()
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"      OpenCV error: {e}")
            return False
    
    def detect_logitech_c925e(self):
        """Comprehensive Logitech C925e detection using all methods"""
        print("="*60)
        print("LOGITECH C925E DETECTION - Using Pre-made Libraries")
        print("="*60)
        
        detection_methods = [
            ("Windows WMI Detection", self.detect_using_windows_wmi),
            ("RobustCameraDetector", self.detect_using_robust_detector),
            ("Direct Camera Access", self.test_direct_camera_access),
        ]
        
        for method_name, method_func in detection_methods:
            print(f"\n[METHOD] {method_name}")
            try:
                success = method_func()
                if success:
                    print(f"[SUCCESS] {method_name} found Logitech camera!")
                else:
                    print(f"[FAILED] {method_name} did not find Logitech camera")
            except Exception as e:
                print(f"[ERROR] {method_name} failed with error: {e}")
        
        # Generate final report
        self.generate_detection_report()
        
        return self.working_stream is not None
    
    def generate_detection_report(self):
        """Generate comprehensive detection report"""
        print("\n" + "="*60)
        print("LOGITECH C925E DETECTION REPORT")
        print("="*60)
        
        print(f"Logitech cameras detected by WMI: {len(self.logitech_cameras)}")
        for cam in self.logitech_cameras:
            print(f"   - {cam['name']} ({cam['status']})")
        
        print(f"Working cameras detected: {len(self.detected_cameras)}")
        for cam in self.detected_cameras:
            print(f"   - Index {cam.get('index', '?')}: {cam.get('method', 'unknown')}")
        
        if self.working_stream:
            print(f"Working stream established: [SUCCESS]")
            print(f"   Stream type: {type(self.working_stream).__name__}")
        else:
            print(f"Working stream established: [FAILED]")
        
        print("\nRECOMMENDATIONS:")
        if len(self.logitech_cameras) > 0:
            print("   1. Logitech camera detected by Windows - driver is working")
            if not self.working_stream:
                print("   2. Camera detected but not accessible - try different USB port")
                print("   3. Close any other applications using the camera")
                print("   4. Try running as administrator")
        else:
            print("   1. Logitech C925e not detected by Windows")
            print("   2. Check USB connection and try different port")
            print("   3. Install/update Logitech camera drivers")
            print("   4. Check Device Manager for camera devices")
    
    def cleanup(self):
        """Clean up resources"""
        if self.working_stream:
            try:
                if hasattr(self.working_stream, 'stop'):
                    self.working_stream.stop()
                elif hasattr(self.working_stream, 'release'):
                    self.working_stream.release()
            except Exception as e:
                print(f"Cleanup error: {e}")

def main():
    """Run Logitech C925e detection"""
    detector = LogitechC925eDetector()
    
    try:
        success = detector.detect_logitech_c925e()
        return 0 if success else 1
    finally:
        detector.cleanup()

if __name__ == "__main__":
    sys.exit(main())
