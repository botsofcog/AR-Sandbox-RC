#!/usr/bin/env python3
"""
Robust Camera Detection and Multi-Camera Management
Combines existing AR Sandbox code with VidGear and MC-Calib libraries
"""

import cv2
import numpy as np
import time
import logging
from typing import List, Dict, Optional, Tuple, Any
import threading
import sys
import os

# Add external libraries to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external_libs', 'vidgear'))

logger = logging.getLogger(__name__)

class RobustCameraDetector:
    """Enhanced camera detection using multiple methods and libraries"""
    
    def __init__(self):
        self.detected_cameras = []
        self.active_cameras = {}
        self.camera_info = {}
        
    def enumerate_all_cameras(self) -> List[Dict[str, Any]]:
        """Enumerate all available cameras using multiple detection methods"""
        logger.info("Starting comprehensive camera enumeration...")
        
        cameras = []
        
        # Method 1: Basic OpenCV enumeration
        cameras.extend(self._opencv_basic_enumeration())
        
        # Method 2: Enhanced backend testing
        cameras.extend(self._opencv_enhanced_enumeration())
        
        # Method 3: VidGear detection (if available)
        cameras.extend(self._vidgear_enumeration())
        
        # Method 4: System-specific detection
        cameras.extend(self._system_specific_enumeration())
        
        # Remove duplicates and validate
        unique_cameras = self._deduplicate_cameras(cameras)
        validated_cameras = self._validate_cameras(unique_cameras)
        
        self.detected_cameras = validated_cameras
        logger.info(f"Found {len(validated_cameras)} working cameras")
        
        return validated_cameras
    
    def _opencv_basic_enumeration(self) -> List[Dict[str, Any]]:
        """Basic OpenCV camera enumeration"""
        cameras = []
        logger.info("Testing basic OpenCV camera enumeration...")
        
        for i in range(10):  # Test up to 10 camera indices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        
                        cameras.append({
                            'index': i,
                            'method': 'opencv_basic',
                            'backend': 'default',
                            'width': width,
                            'height': height,
                            'fps': fps,
                            'working': True
                        })
                        logger.info(f"Found camera {i}: {width}x{height} @ {fps}fps")
                cap.release()
            except Exception as e:
                logger.debug(f"Camera {i} failed basic test: {e}")
        
        return cameras
    
    def _opencv_enhanced_enumeration(self) -> List[Dict[str, Any]]:
        """Enhanced OpenCV enumeration with multiple backends"""
        cameras = []
        logger.info("Testing enhanced OpenCV camera enumeration...")
        
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_V4L2, "Video4Linux"),
            (cv2.CAP_ANY, "Any Available")
        ]
        
        for i in range(8):  # Test camera indices
            for backend_id, backend_name in backends:
                try:
                    cap = cv2.VideoCapture(i, backend_id)
                    if cap.isOpened():
                        # Give camera time to initialize
                        time.sleep(0.3)
                        
                        # Test multiple frame reads for stability
                        success_count = 0
                        for _ in range(3):
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                success_count += 1
                            time.sleep(0.1)
                        
                        if success_count >= 2:  # At least 2/3 successful reads
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            
                            cameras.append({
                                'index': i,
                                'method': 'opencv_enhanced',
                                'backend': backend_name,
                                'backend_id': backend_id,
                                'width': width,
                                'height': height,
                                'fps': fps,
                                'stability': success_count,
                                'working': True
                            })
                            logger.info(f"Enhanced: Camera {i} with {backend_name}: {width}x{height}")
                            break  # Found working backend for this camera
                    
                    cap.release()
                except Exception as e:
                    logger.debug(f"Camera {i} with {backend_name} failed: {e}")
        
        return cameras
    
    def _vidgear_enumeration(self) -> List[Dict[str, Any]]:
        """Use VidGear for camera detection if available"""
        cameras = []
        try:
            # Try to import VidGear
            from vidgear.gears import CamGear
            logger.info("Testing VidGear camera enumeration...")
            
            for i in range(5):
                try:
                    stream = CamGear(source=i, logging=False).start()
                    frame = stream.read()
                    if frame is not None:
                        height, width = frame.shape[:2]
                        cameras.append({
                            'index': i,
                            'method': 'vidgear',
                            'backend': 'VidGear',
                            'width': width,
                            'height': height,
                            'working': True
                        })
                        logger.info(f"VidGear: Found camera {i}: {width}x{height}")
                    stream.stop()
                except Exception as e:
                    logger.debug(f"VidGear camera {i} failed: {e}")
        except ImportError:
            logger.debug("VidGear not available for camera enumeration")
        
        return cameras
    
    def _system_specific_enumeration(self) -> List[Dict[str, Any]]:
        """System-specific camera detection"""
        cameras = []
        
        # Windows-specific detection
        if sys.platform == "win32":
            cameras.extend(self._windows_camera_detection())
        
        # Linux-specific detection
        elif sys.platform.startswith("linux"):
            cameras.extend(self._linux_camera_detection())
        
        return cameras
    
    def _windows_camera_detection(self) -> List[Dict[str, Any]]:
        """Windows-specific camera detection using WMI or registry"""
        cameras = []
        logger.info("Testing Windows-specific camera detection...")
        
        try:
            import subprocess
            # Use PowerShell to enumerate cameras
            result = subprocess.run([
                "powershell", "-Command",
                "Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like '*camera*' -or $_.Name -like '*webcam*'} | Select-Object Name, DeviceID"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines[2:]):  # Skip header lines
                    if line.strip():
                        cameras.append({
                            'index': i,
                            'method': 'windows_wmi',
                            'backend': 'WMI',
                            'device_info': line.strip(),
                            'working': False  # Need to validate
                        })
                        logger.info(f"Windows WMI: Found camera device: {line.strip()}")
        except Exception as e:
            logger.debug(f"Windows camera detection failed: {e}")
        
        return cameras
    
    def _linux_camera_detection(self) -> List[Dict[str, Any]]:
        """Linux-specific camera detection using /dev/video*"""
        cameras = []
        logger.info("Testing Linux-specific camera detection...")
        
        try:
            import glob
            video_devices = glob.glob('/dev/video*')
            for device in video_devices:
                try:
                    # Extract device number
                    device_num = int(device.replace('/dev/video', ''))
                    cameras.append({
                        'index': device_num,
                        'method': 'linux_dev',
                        'backend': 'V4L2',
                        'device_path': device,
                        'working': False  # Need to validate
                    })
                    logger.info(f"Linux: Found video device: {device}")
                except ValueError:
                    continue
        except Exception as e:
            logger.debug(f"Linux camera detection failed: {e}")
        
        return cameras
    
    def _deduplicate_cameras(self, cameras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate camera entries"""
        unique_cameras = []
        seen_indices = set()
        
        # Prioritize by method reliability
        method_priority = {
            'opencv_enhanced': 1,
            'vidgear': 2,
            'opencv_basic': 3,
            'windows_wmi': 4,
            'linux_dev': 5
        }
        
        # Sort by priority and index
        sorted_cameras = sorted(cameras, key=lambda x: (method_priority.get(x['method'], 99), x['index']))
        
        for camera in sorted_cameras:
            if camera['index'] not in seen_indices:
                unique_cameras.append(camera)
                seen_indices.add(camera['index'])
        
        return unique_cameras
    
    def _validate_cameras(self, cameras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that cameras actually work"""
        validated = []
        
        for camera in cameras:
            if camera.get('working', False):
                validated.append(camera)
            else:
                # Try to validate unconfirmed cameras
                if self._test_camera_functionality(camera['index']):
                    camera['working'] = True
                    validated.append(camera)
        
        return validated
    
    def _test_camera_functionality(self, camera_index: int) -> bool:
        """Test if a camera index actually works"""
        try:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret and frame is not None
        except Exception:
            pass
        return False
    
    def get_best_cameras_for_ar_sandbox(self) -> Dict[str, Any]:
        """Get the best camera configuration for AR Sandbox"""
        if not self.detected_cameras:
            self.enumerate_all_cameras()
        
        # Look for Kinect (depth) and webcam (RGB) combination
        kinect_camera = None
        webcam_camera = None
        
        for camera in self.detected_cameras:
            # Kinect typically has specific resolutions
            if camera['width'] == 640 and camera['height'] == 480:
                if not kinect_camera:
                    kinect_camera = camera
            # Regular webcam
            elif camera['width'] >= 640 and camera['height'] >= 480:
                if not webcam_camera:
                    webcam_camera = camera
        
        return {
            'kinect_camera': kinect_camera,
            'webcam_camera': webcam_camera,
            'all_cameras': self.detected_cameras,
            'recommended_config': self._get_recommended_config()
        }
    
    def _get_recommended_config(self) -> Dict[str, Any]:
        """Get recommended camera configuration"""
        if len(self.detected_cameras) >= 2:
            return {
                'mode': 'hybrid',
                'depth_camera': self.detected_cameras[0],
                'rgb_camera': self.detected_cameras[1],
                'description': 'Use first camera for depth, second for RGB'
            }
        elif len(self.detected_cameras) == 1:
            return {
                'mode': 'single',
                'camera': self.detected_cameras[0],
                'description': 'Use single camera for both depth simulation and RGB'
            }
        else:
            return {
                'mode': 'none',
                'description': 'No working cameras detected'
            }

if __name__ == "__main__":
    # Test the camera detector
    logging.basicConfig(level=logging.INFO)
    detector = RobustCameraDetector()
    
    print("Detecting cameras...")
    cameras = detector.enumerate_all_cameras()
    
    print(f"\nFound {len(cameras)} cameras:")
    for i, camera in enumerate(cameras):
        print(f"  {i+1}. Index {camera['index']}: {camera['method']} via {camera['backend']}")
        if 'width' in camera and 'height' in camera:
            print(f"     Resolution: {camera['width']}x{camera['height']}")
    
    print("\nAR Sandbox Configuration:")
    config = detector.get_best_cameras_for_ar_sandbox()
    print(f"  Mode: {config['recommended_config']['mode']}")
    print(f"  Description: {config['recommended_config']['description']}")
