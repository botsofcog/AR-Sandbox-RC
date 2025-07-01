#!/usr/bin/env python3
"""
Smart Camera Detection System for AR Sandbox RC
Uses Kinect infrared to detect other cameras and intelligently selects best combination
Can use alternative webcam if Logitech C925e doesn't work optimally
"""

import cv2
import numpy as np
import time
import sys
import os
import threading
from typing import Dict, List, Optional, Tuple

try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect available for smart detection")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect not available")

class SmartCameraDetectionSystem:
    """
    Intelligent camera detection using Kinect infrared + smart camera selection
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.kinect_ir_active = False
        
        self.detected_cameras = []
        self.working_cameras = []
        self.optimal_camera_combo = None
        
    def initialize_kinect_sensors(self):
        """Initialize all Kinect sensors including infrared"""
        if not KINECT_AVAILABLE:
            print("[WARNING] Kinect not available for smart detection")
            return False, False, False
        
        print("[INIT] Initializing Kinect sensors for smart detection...")
        
        try:
            # Test depth sensor
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is not None:
                self.kinect_depth_active = True
                print("   [SUCCESS] Kinect depth sensor active")
            
            # Test RGB camera
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is not None:
                self.kinect_rgb_active = True
                print("   [SUCCESS] Kinect RGB camera active")
            
            # Test infrared sensor
            try:
                # Get infrared frame (if available)
                ir_frame = freenect.sync_get_video(0, freenect.VIDEO_IR_8BIT)[0]
                if ir_frame is not None:
                    self.kinect_ir_active = True
                    print("   [SUCCESS] Kinect infrared sensor active")
            except Exception as e:
                print(f"   [INFO] Kinect infrared not available: {e}")
            
            return self.kinect_depth_active, self.kinect_rgb_active, self.kinect_ir_active
            
        except Exception as e:
            print(f"   [ERROR] Kinect initialization failed: {e}")
            return False, False, False
    
    def detect_cameras_with_kinect_assistance(self):
        """Use Kinect to detect and locate other cameras in the environment"""
        print("\n[DETECT] Using Kinect to detect other cameras...")
        
        camera_detections = []
        
        if not self.kinect_rgb_active:
            print("   [SKIP] Kinect RGB not available for camera detection")
            return camera_detections
        
        try:
            # Capture multiple frames for analysis
            for frame_idx in range(5):
                rgb_frame = freenect.sync_get_video()[0]
                if rgb_frame is None:
                    continue
                
                # Detect camera-like objects
                detections = self.analyze_frame_for_cameras(rgb_frame, frame_idx)
                camera_detections.extend(detections)
                
                time.sleep(0.2)  # Small delay between captures
            
            # Consolidate detections
            unique_detections = self.consolidate_camera_detections(camera_detections)
            
            print(f"   [RESULT] Detected {len(unique_detections)} potential camera(s) in environment")
            for i, detection in enumerate(unique_detections):
                print(f"      Camera {i+1}: {detection['type']} at {detection['location']}")
            
            return unique_detections
            
        except Exception as e:
            print(f"   [ERROR] Kinect-assisted detection failed: {e}")
            return []
    
    def analyze_frame_for_cameras(self, rgb_frame, frame_idx):
        """Analyze RGB frame to detect camera-like objects"""
        detections = []
        
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            
            # Detect dark circular/rectangular objects (camera lenses)
            # Use HoughCircles to find circular camera lenses
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, 1, 50,
                param1=50, param2=30, minRadius=10, maxRadius=100
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    # Check if this circle is dark (camera lens)
                    roi = gray[max(0, y-r):min(gray.shape[0], y+r), 
                              max(0, x-r):min(gray.shape[1], x+r)]
                    if roi.size > 0 and np.mean(roi) < 80:  # Dark region
                        detections.append({
                            'type': 'circular_camera_lens',
                            'location': (x, y),
                            'size': r,
                            'confidence': 0.7,
                            'frame': frame_idx
                        })
            
            # Detect rectangular objects (camera bodies)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Check if contour is rectangular and appropriate size
                area = cv2.contourArea(contour)
                if 500 < area < 5000:  # Reasonable camera size
                    # Approximate contour to polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    if len(approx) == 4:  # Rectangular
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        
                        # Camera-like aspect ratio
                        if 0.5 < aspect_ratio < 2.0:
                            detections.append({
                                'type': 'rectangular_camera_body',
                                'location': (x + w//2, y + h//2),
                                'size': (w, h),
                                'confidence': 0.6,
                                'frame': frame_idx
                            })
            
            # Detect LED indicators (bright spots)
            bright_mask = gray > 240
            bright_contours, _ = cv2.findContours(bright_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in bright_contours:
                area = cv2.contourArea(contour)
                if 10 < area < 200:  # LED-like size
                    x, y, w, h = cv2.boundingRect(contour)
                    detections.append({
                        'type': 'led_indicator',
                        'location': (x + w//2, y + h//2),
                        'size': (w, h),
                        'confidence': 0.5,
                        'frame': frame_idx
                    })
            
        except Exception as e:
            print(f"   Frame analysis error: {e}")
        
        return detections
    
    def consolidate_camera_detections(self, detections):
        """Consolidate multiple detections into unique cameras"""
        if not detections:
            return []
        
        # Group detections by proximity
        unique_cameras = []
        proximity_threshold = 50  # pixels
        
        for detection in detections:
            location = detection['location']
            
            # Check if this detection is close to an existing camera
            merged = False
            for camera in unique_cameras:
                camera_location = camera['location']
                distance = np.sqrt((location[0] - camera_location[0])**2 + 
                                 (location[1] - camera_location[1])**2)
                
                if distance < proximity_threshold:
                    # Merge detections
                    camera['confidence'] = max(camera['confidence'], detection['confidence'])
                    camera['detections'].append(detection)
                    merged = True
                    break
            
            if not merged:
                # New unique camera
                unique_cameras.append({
                    'location': location,
                    'confidence': detection['confidence'],
                    'primary_type': detection['type'],
                    'detections': [detection]
                })
        
        return unique_cameras
    
    def smart_camera_enumeration(self):
        """Intelligently enumerate and test all available cameras"""
        print("\n[SMART] Intelligent camera enumeration...")
        
        working_cameras = []
        
        # Test different camera access methods
        test_configs = [
            # DirectShow with different indices
            {"method": "opencv", "backend": cv2.CAP_DSHOW, "indices": [0, 1, 2, 3, 4]},
            # MSMF with different indices  
            {"method": "opencv", "backend": cv2.CAP_MSMF, "indices": [0, 1, 2]},
            # Any backend
            {"method": "opencv", "backend": cv2.CAP_ANY, "indices": [0, 1, 2]},
        ]
        
        for config in test_configs:
            print(f"   Testing {config['method']} with backend...")
            
            for idx in config['indices']:
                try:
                    cap = cv2.VideoCapture(idx, config['backend'])
                    
                    if cap.isOpened():
                        # Test frame capture
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            height, width = frame.shape[:2]
                            
                            # Analyze camera capabilities
                            capabilities = self.analyze_camera_capabilities(cap, idx)
                            
                            camera_info = {
                                'index': idx,
                                'method': config['method'],
                                'backend': config['backend'],
                                'resolution': (width, height),
                                'capabilities': capabilities,
                                'capture_object': cap,
                                'quality_score': self.calculate_camera_quality_score(capabilities, width, height)
                            }
                            
                            working_cameras.append(camera_info)
                            print(f"      [SUCCESS] Camera {idx}: {width}x{height} (Quality: {camera_info['quality_score']:.1f})")
                            
                            # Don't release - keep for potential use
                            continue
                        else:
                            cap.release()
                    
                except Exception as e:
                    pass  # Continue testing
        
        # Sort by quality score
        working_cameras.sort(key=lambda x: x['quality_score'], reverse=True)
        
        print(f"   [RESULT] Found {len(working_cameras)} working camera(s)")
        self.working_cameras = working_cameras
        
        return working_cameras
    
    def analyze_camera_capabilities(self, cap, idx):
        """Analyze camera capabilities and features"""
        capabilities = {
            'max_resolution': (640, 480),
            'supports_high_res': False,
            'supports_autofocus': False,
            'frame_rate': 30,
            'likely_webcam_type': 'unknown'
        }
        
        try:
            # Test maximum resolution
            original_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            original_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            # Test high resolution (Logitech C925e supports 1920x1080)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                test_height, test_width = test_frame.shape[:2]
                if test_width >= 1280 and test_height >= 720:
                    capabilities['supports_high_res'] = True
                    capabilities['max_resolution'] = (test_width, test_height)
                    capabilities['likely_webcam_type'] = 'high_end_webcam'  # Likely Logitech C925e
            
            # Reset to standard resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Test autofocus capability
            try:
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                if cap.get(cv2.CAP_PROP_AUTOFOCUS) == 1:
                    capabilities['supports_autofocus'] = True
            except:
                pass
            
            # Get frame rate
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                capabilities['frame_rate'] = fps
            
        except Exception as e:
            print(f"      Capability analysis error for camera {idx}: {e}")
        
        return capabilities
    
    def calculate_camera_quality_score(self, capabilities, width, height):
        """Calculate quality score for camera selection"""
        score = 0
        
        # Resolution score
        pixel_count = width * height
        if pixel_count >= 1920 * 1080:
            score += 50  # Excellent resolution
        elif pixel_count >= 1280 * 720:
            score += 40  # Good resolution
        elif pixel_count >= 640 * 480:
            score += 30  # Standard resolution
        else:
            score += 10  # Low resolution
        
        # High resolution support
        if capabilities['supports_high_res']:
            score += 20
        
        # Autofocus support
        if capabilities['supports_autofocus']:
            score += 15
        
        # Frame rate
        if capabilities['frame_rate'] >= 30:
            score += 10
        elif capabilities['frame_rate'] >= 15:
            score += 5
        
        # Webcam type bonus
        if capabilities['likely_webcam_type'] == 'high_end_webcam':
            score += 15  # Likely Logitech C925e
        
        return score
    
    def select_optimal_camera_combination(self):
        """Intelligently select the best 3-camera combination"""
        print("\n[SMART] Selecting optimal camera combination...")
        
        if not self.working_cameras:
            print("   [ERROR] No working cameras found for selection")
            return None
        
        # Always include Kinect if available
        combination = {
            'kinect_depth': self.kinect_depth_active,
            'kinect_rgb': self.kinect_rgb_active,
            'webcam': None,
            'total_cameras': 0,
            'quality_score': 0
        }
        
        if self.kinect_depth_active:
            combination['total_cameras'] += 1
            combination['quality_score'] += 40  # Kinect depth is valuable
        
        if self.kinect_rgb_active:
            combination['total_cameras'] += 1
            combination['quality_score'] += 30  # Kinect RGB is good
        
        # Select best webcam
        if self.working_cameras:
            best_webcam = self.working_cameras[0]  # Already sorted by quality
            combination['webcam'] = best_webcam
            combination['total_cameras'] += 1
            combination['quality_score'] += best_webcam['quality_score']
            
            print(f"   [SELECTED] Best webcam: Camera {best_webcam['index']}")
            print(f"      Resolution: {best_webcam['resolution']}")
            print(f"      Type: {best_webcam['capabilities']['likely_webcam_type']}")
            print(f"      Quality score: {best_webcam['quality_score']:.1f}")
        
        print(f"   [COMBINATION] Total cameras: {combination['total_cameras']}/3")
        print(f"   [COMBINATION] Overall quality: {combination['quality_score']:.1f}")
        
        self.optimal_camera_combo = combination
        return combination
    
    def run_smart_detection(self):
        """Run complete smart camera detection and selection"""
        print("="*60)
        print("🧠 SMART CAMERA DETECTION SYSTEM - AR SANDBOX RC")
        print("="*60)
        
        # Initialize Kinect sensors
        kinect_depth, kinect_rgb, kinect_ir = self.initialize_kinect_sensors()
        
        # Use Kinect to detect other cameras
        camera_detections = self.detect_cameras_with_kinect_assistance()
        
        # Smart camera enumeration
        working_cameras = self.smart_camera_enumeration()
        
        # Select optimal combination
        optimal_combo = self.select_optimal_camera_combination()
        
        # Generate report
        print(f"\n🎯 SMART DETECTION RESULTS:")
        print(f"   Kinect sensors: {sum([kinect_depth, kinect_rgb, kinect_ir])}/3 active")
        print(f"   Camera detections: {len(camera_detections)} potential cameras seen")
        print(f"   Working cameras: {len(working_cameras)} accessible")
        
        if optimal_combo and optimal_combo['total_cameras'] >= 2:
            print(f"   🎉 OPTIMAL COMBINATION FOUND!")
            print(f"      Total cameras: {optimal_combo['total_cameras']}/3")
            print(f"      Quality score: {optimal_combo['quality_score']:.1f}")
            return True
        else:
            print(f"   ⚠️ Insufficient cameras for optimal setup")
            return False

def main():
    """Run smart camera detection system"""
    smart_system = SmartCameraDetectionSystem()
    success = smart_system.run_smart_detection()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
