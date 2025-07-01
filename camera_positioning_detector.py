#!/usr/bin/env python3
"""
Camera Positioning Detector for AR Sandbox RC
Detects if cameras are interfering with each other or improperly positioned
Provides guidance for optimal 3-camera setup positioning
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect available for positioning check")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect not available")

class CameraPositioningDetector:
    """
    Detects camera positioning issues and provides setup guidance
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.positioning_issues = []
        
    def check_kinect_positioning(self):
        """Check if Kinect is properly positioned for sandbox viewing"""
        print("\n[CHECK] Analyzing Kinect positioning...")
        
        if not KINECT_AVAILABLE:
            print("   [SKIP] Kinect not available")
            return False
        
        try:
            # Get Kinect depth frame
            depth_frame = freenect.sync_get_depth()[0]
            rgb_frame = freenect.sync_get_video()[0]
            
            if depth_frame is None or rgb_frame is None:
                print("   [ERROR] Cannot capture Kinect frames")
                return False
            
            # Analyze depth data for sandbox detection
            depth_analysis = self.analyze_depth_for_sandbox(depth_frame)
            
            # Analyze RGB for proper sandbox view
            rgb_analysis = self.analyze_rgb_for_sandbox(rgb_frame)
            
            print(f"   Depth analysis: {depth_analysis['status']}")
            print(f"   RGB analysis: {rgb_analysis['status']}")
            
            # Check for optimal positioning
            if depth_analysis['sandbox_detected'] and rgb_analysis['sandbox_view']:
                print("   [SUCCESS] Kinect properly positioned for sandbox")
                return True
            else:
                print("   [WARNING] Kinect positioning needs adjustment")
                self.positioning_issues.extend(depth_analysis['issues'])
                self.positioning_issues.extend(rgb_analysis['issues'])
                return False
                
        except Exception as e:
            print(f"   [ERROR] Kinect positioning check failed: {e}")
            return False
    
    def analyze_depth_for_sandbox(self, depth_frame):
        """Analyze depth frame to detect sandbox and positioning"""
        analysis = {
            'status': 'unknown',
            'sandbox_detected': False,
            'issues': []
        }
        
        try:
            # Basic depth statistics
            valid_depth = depth_frame[depth_frame > 0]
            if len(valid_depth) == 0:
                analysis['status'] = 'no_depth_data'
                analysis['issues'].append("No valid depth data - check Kinect connection")
                return analysis
            
            min_depth = np.min(valid_depth)
            max_depth = np.max(valid_depth)
            mean_depth = np.mean(valid_depth)
            depth_range = max_depth - min_depth
            
            print(f"      Depth range: {min_depth}mm to {max_depth}mm (range: {depth_range}mm)")
            
            # Check for sandbox-like depth profile
            if depth_range < 50:  # Less than 5cm variation
                analysis['issues'].append("Very flat surface - may not be sandbox or too far away")
            elif depth_range > 500:  # More than 50cm variation
                analysis['issues'].append("Very large depth variation - may be looking at room instead of sandbox")
            else:
                analysis['sandbox_detected'] = True
            
            # Check distance - sandbox should be relatively close
            if mean_depth > 2000:  # More than 2 meters
                analysis['issues'].append("Sandbox appears very far - move Kinect closer")
            elif mean_depth < 300:  # Less than 30cm
                analysis['issues'].append("Sandbox appears very close - move Kinect further back")
            
            # Check for rectangular sandbox shape in depth
            height, width = depth_frame.shape
            center_region = depth_frame[height//4:3*height//4, width//4:3*width//4]
            center_valid = center_region[center_region > 0]
            
            if len(center_valid) > len(valid_depth) * 0.3:  # Good center coverage
                analysis['sandbox_detected'] = True
            else:
                analysis['issues'].append("Poor center coverage - adjust Kinect angle")
            
            if analysis['sandbox_detected'] and len(analysis['issues']) == 0:
                analysis['status'] = 'optimal'
            elif analysis['sandbox_detected']:
                analysis['status'] = 'good_with_issues'
            else:
                analysis['status'] = 'poor'
                
        except Exception as e:
            analysis['status'] = 'error'
            analysis['issues'].append(f"Depth analysis error: {e}")
        
        return analysis
    
    def analyze_rgb_for_sandbox(self, rgb_frame):
        """Analyze RGB frame for proper sandbox view"""
        analysis = {
            'status': 'unknown',
            'sandbox_view': False,
            'issues': []
        }
        
        try:
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2HSV)
            
            # Check brightness - should not be too dark or too bright
            mean_brightness = np.mean(gray)
            print(f"      Average brightness: {mean_brightness:.1f}")
            
            if mean_brightness < 50:
                analysis['issues'].append("Image too dark - improve lighting or adjust Kinect position")
            elif mean_brightness > 200:
                analysis['issues'].append("Image too bright - reduce lighting or adjust Kinect position")
            
            # Check for sand-like colors (browns, tans, beiges)
            # Sand typically has low saturation and medium value
            sand_mask = (hsv[:,:,1] < 100) & (hsv[:,:,2] > 80) & (hsv[:,:,2] < 180)
            sand_percentage = np.sum(sand_mask) / sand_mask.size * 100
            
            print(f"      Sand-like color coverage: {sand_percentage:.1f}%")
            
            if sand_percentage > 30:
                analysis['sandbox_view'] = True
            else:
                analysis['issues'].append("Low sand-like color coverage - may not be viewing sandbox")
            
            # Check for rectangular/defined edges (sandbox edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            print(f"      Edge density: {edge_density:.1f}%")
            
            if edge_density < 2:
                analysis['issues'].append("Very few edges detected - may be too far or unfocused")
            elif edge_density > 15:
                analysis['issues'].append("Too many edges - may be looking at complex scene instead of sandbox")
            
            # Overall assessment
            if analysis['sandbox_view'] and len(analysis['issues']) <= 1:
                analysis['status'] = 'optimal'
            elif analysis['sandbox_view']:
                analysis['status'] = 'good_with_issues'
            else:
                analysis['status'] = 'poor'
                
        except Exception as e:
            analysis['status'] = 'error'
            analysis['issues'].append(f"RGB analysis error: {e}")
        
        return analysis
    
    def check_camera_interference(self):
        """Check if cameras are interfering with each other"""
        print("\n[CHECK] Analyzing camera interference...")
        
        interference_detected = False
        
        # Check if Kinect RGB is seeing another camera
        if KINECT_AVAILABLE:
            try:
                rgb_frame = freenect.sync_get_video()[0]
                if rgb_frame is not None:
                    # Look for camera-like objects (dark rectangles, LED lights)
                    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
                    
                    # Detect very dark regions (camera lenses)
                    dark_mask = gray < 30
                    dark_percentage = np.sum(dark_mask) / dark_mask.size * 100
                    
                    # Detect very bright spots (LED indicators)
                    bright_mask = gray > 240
                    bright_percentage = np.sum(bright_mask) / bright_mask.size * 100
                    
                    print(f"   Dark regions (possible cameras): {dark_percentage:.1f}%")
                    print(f"   Bright spots (possible LEDs): {bright_percentage:.1f}%")
                    
                    if dark_percentage > 5:  # More than 5% very dark
                        interference_detected = True
                        self.positioning_issues.append("Kinect may be looking at another camera - reposition cameras")
                    
                    if bright_percentage > 1:  # More than 1% very bright
                        interference_detected = True
                        self.positioning_issues.append("Bright LED spots detected - may be camera indicators")
                        
            except Exception as e:
                print(f"   [ERROR] Interference check failed: {e}")
        
        if not interference_detected:
            print("   [SUCCESS] No obvious camera interference detected")
        
        return not interference_detected
    
    def generate_positioning_guidance(self):
        """Generate specific positioning guidance"""
        print("\n" + "="*60)
        print("CAMERA POSITIONING GUIDANCE")
        print("="*60)
        
        print("\n📐 OPTIMAL 3-CAMERA SETUP:")
        print("   1. KINECT (Side view - Axis 1):")
        print("      - Position to the SIDE of sandbox")
        print("      - Angle: 45° downward toward sandbox")
        print("      - Distance: 60-100cm from sandbox")
        print("      - Should see sandbox from the side")
        
        print("\n   2. LOGITECH C925e (Overhead - Axis 2):")
        print("      - Position ABOVE sandbox")
        print("      - Angle: 90° downward (straight down)")
        print("      - Distance: 80-120cm above sandbox")
        print("      - Should see sandbox from above")
        
        print("\n   3. AVOID:")
        print("      - Cameras pointing at each other")
        print("      - Cameras in each other's field of view")
        print("      - Cameras too close together")
        print("      - Cameras at same angle/axis")
        
        if self.positioning_issues:
            print(f"\n⚠️ DETECTED ISSUES ({len(self.positioning_issues)}):")
            for i, issue in enumerate(self.positioning_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ NO POSITIONING ISSUES DETECTED")
        
        print(f"\n🎯 NEXT STEPS:")
        if self.positioning_issues:
            print("   1. Reposition cameras according to guidance above")
            print("   2. Ensure cameras are NOT looking at each other")
            print("   3. Test camera access after repositioning")
            print("   4. Run this positioning check again")
        else:
            print("   1. Camera positioning appears optimal")
            print("   2. Try camera access again")
            print("   3. Check for software conflicts if still failing")
    
    def run_full_positioning_check(self):
        """Run complete camera positioning analysis"""
        print("="*60)
        print("🎯 CAMERA POSITIONING DETECTOR - AR SANDBOX RC")
        print("="*60)
        
        # Check Kinect positioning
        kinect_ok = self.check_kinect_positioning()
        
        # Check camera interference
        interference_ok = self.check_camera_interference()
        
        # Generate guidance
        self.generate_positioning_guidance()
        
        # Overall assessment
        if kinect_ok and interference_ok and len(self.positioning_issues) == 0:
            print(f"\n🎉 POSITIONING OPTIMAL - Ready for 3-camera setup!")
            return True
        else:
            print(f"\n⚠️ POSITIONING NEEDS ADJUSTMENT")
            return False

def main():
    """Run camera positioning detector"""
    detector = CameraPositioningDetector()
    success = detector.run_full_positioning_check()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
