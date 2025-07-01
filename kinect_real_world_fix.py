#!/usr/bin/env python3
"""
Kinect Real-World Sensor Fix
Fixes Kinect to sense actual environment instead of showing test patterns
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect library not available")

class KinectRealWorldFix:
    """
    Fixes Kinect to capture real-world data instead of test patterns
    """
    
    def __init__(self):
        self.device = None
        self.depth_working = False
        self.rgb_working = False
        
    def diagnose_test_patterns(self):
        """Diagnose if Kinect is showing test patterns vs real data"""
        print("🔍 DIAGNOSING KINECT TEST PATTERNS...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False, False
        
        try:
            # Capture depth frame
            depth_frame = freenect.sync_get_depth()[0]
            rgb_frame = freenect.sync_get_video()[0]
            
            if depth_frame is None or rgb_frame is None:
                print("   ❌ Cannot capture frames for diagnosis")
                return False, False
            
            # Analyze depth for test pattern
            depth_is_real = self.analyze_depth_for_real_data(depth_frame)
            
            # Analyze RGB for test pattern
            rgb_is_real = self.analyze_rgb_for_real_data(rgb_frame)
            
            return depth_is_real, rgb_is_real
            
        except Exception as e:
            print(f"   ❌ Diagnosis failed: {e}")
            return False, False
    
    def analyze_depth_for_real_data(self, depth_frame):
        """Check if depth frame contains real world data or test pattern"""
        print("   🔍 Analyzing depth sensor...")
        
        try:
            # Check for test pattern characteristics
            valid_pixels = np.sum(depth_frame > 0)
            total_pixels = depth_frame.size
            coverage = (valid_pixels / total_pixels) * 100
            
            print(f"      Valid depth pixels: {coverage:.1f}%")
            
            if valid_pixels > 0:
                valid_depths = depth_frame[depth_frame > 0]
                depth_range = np.max(valid_depths) - np.min(valid_depths)
                depth_std = np.std(valid_depths)
                
                print(f"      Depth range: {depth_range}mm")
                print(f"      Depth variation: {depth_std:.1f}mm")
                
                # Test pattern detection
                if coverage < 5:
                    print("      ❌ Very low coverage - likely test pattern or no objects")
                    return False
                elif depth_range < 50:
                    print("      ❌ Very flat - likely test pattern")
                    return False
                elif depth_std < 10:
                    print("      ❌ No variation - likely test pattern")
                    return False
                else:
                    print("      ✅ Real depth data detected")
                    return True
            else:
                print("      ❌ No valid depth data")
                return False
                
        except Exception as e:
            print(f"      ❌ Depth analysis error: {e}")
            return False
    
    def analyze_rgb_for_real_data(self, rgb_frame):
        """Check if RGB frame contains real world data or test pattern"""
        print("   📷 Analyzing RGB camera...")
        
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            
            # Check for gradient patterns (test pattern characteristic)
            # Calculate horizontal and vertical gradients
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            avg_gradient = np.mean(gradient_magnitude)
            
            print(f"      Average gradient: {avg_gradient:.1f}")
            
            # Check for uniform patterns
            brightness_std = np.std(gray)
            print(f"      Brightness variation: {brightness_std:.1f}")
            
            # Detect edges (real scenes have more edges than test patterns)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            print(f"      Edge density: {edge_density:.1f}%")
            
            # Test pattern detection
            if avg_gradient > 50 and brightness_std < 30:
                print("      ❌ High gradient, low variation - likely test pattern")
                return False
            elif edge_density < 1:
                print("      ❌ Very few edges - likely test pattern")
                return False
            elif brightness_std < 20:
                print("      ❌ Very uniform - likely test pattern")
                return False
            else:
                print("      ✅ Real RGB data detected")
                return True
                
        except Exception as e:
            print(f"      ❌ RGB analysis error: {e}")
            return False
    
    def fix_kinect_initialization(self):
        """Fix Kinect initialization to capture real world data"""
        print("\n🔧 FIXING KINECT INITIALIZATION...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False
        
        try:
            # Step 1: Stop any existing streams
            print("   🛑 Stopping existing streams...")
            try:
                freenect.stop_depth(0)
                freenect.stop_video(0)
                time.sleep(0.5)
            except:
                pass
            
            # Step 2: Reset device
            print("   🔄 Resetting Kinect device...")
            try:
                device = freenect.open_device(0)
                freenect.close_device(device)
                time.sleep(1.0)
            except:
                pass
            
            # Step 3: Set proper modes for real-world sensing
            print("   ⚙️ Setting real-world sensing modes...")
            
            # Set depth mode for real sensing
            freenect.set_depth_mode(0, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
            
            # Set video mode for real sensing
            freenect.set_video_mode(0, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
            
            # Step 4: Start streams in proper order
            print("   🚀 Starting real-world sensing...")
            freenect.start_depth(0)
            time.sleep(0.3)
            freenect.start_video(0)
            time.sleep(0.3)
            
            # Step 5: Clear initial frames (may contain test patterns)
            print("   🧹 Clearing initial test frames...")
            for i in range(10):
                try:
                    freenect.sync_get_depth()
                    freenect.sync_get_video()
                    time.sleep(0.1)
                except:
                    pass
            
            print("   ✅ Kinect initialization fixed")
            return True
            
        except Exception as e:
            print(f"   ❌ Initialization fix failed: {e}")
            return False
    
    def verify_real_world_sensing(self):
        """Verify that Kinect is now sensing real world"""
        print("\n🧪 VERIFYING REAL-WORLD SENSING...")
        
        # Wait a moment for stabilization
        time.sleep(1.0)
        
        # Test multiple frames to ensure consistency
        real_depth_count = 0
        real_rgb_count = 0
        test_frames = 5
        
        for i in range(test_frames):
            try:
                print(f"   Testing frame {i+1}/{test_frames}...")
                
                depth_frame = freenect.sync_get_depth()[0]
                rgb_frame = freenect.sync_get_video()[0]
                
                if depth_frame is not None and rgb_frame is not None:
                    depth_real = self.analyze_depth_for_real_data(depth_frame)
                    rgb_real = self.analyze_rgb_for_real_data(rgb_frame)
                    
                    if depth_real:
                        real_depth_count += 1
                    if rgb_real:
                        real_rgb_count += 1
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   Frame {i+1} error: {e}")
        
        depth_success_rate = (real_depth_count / test_frames) * 100
        rgb_success_rate = (real_rgb_count / test_frames) * 100
        
        print(f"\n📊 VERIFICATION RESULTS:")
        print(f"   Depth real-world sensing: {real_depth_count}/{test_frames} ({depth_success_rate:.0f}%)")
        print(f"   RGB real-world sensing: {real_rgb_count}/{test_frames} ({rgb_success_rate:.0f}%)")
        
        self.depth_working = depth_success_rate >= 60
        self.rgb_working = rgb_success_rate >= 60
        
        return self.depth_working, self.rgb_working
    
    def run_real_world_fix(self):
        """Run complete real-world sensing fix"""
        print("="*60)
        print("🌍 KINECT REAL-WORLD SENSOR FIX")
        print("="*60)
        
        # Initial diagnosis
        initial_depth_real, initial_rgb_real = self.diagnose_test_patterns()
        
        print(f"\n📊 INITIAL STATUS:")
        print(f"   Depth sensor: {'✅ Real data' if initial_depth_real else '❌ Test pattern'}")
        print(f"   RGB camera: {'✅ Real data' if initial_rgb_real else '❌ Test pattern'}")
        
        if initial_depth_real and initial_rgb_real:
            print("\n🎉 Both sensors already sensing real world!")
            return True
        
        # Apply fix
        fix_applied = self.fix_kinect_initialization()
        
        if not fix_applied:
            print("\n❌ Failed to apply initialization fix")
            return False
        
        # Verify fix
        final_depth_real, final_rgb_real = self.verify_real_world_sensing()
        
        # Generate report
        print(f"\n🎯 FINAL STATUS:")
        print(f"   Depth sensor: {'✅ Real data' if final_depth_real else '❌ Still test pattern'}")
        print(f"   RGB camera: {'✅ Real data' if final_rgb_real else '❌ Still test pattern'}")
        
        if final_depth_real and final_rgb_real:
            print(f"\n🎉 SUCCESS: Both sensors now sensing real world!")
        elif final_depth_real or final_rgb_real:
            print(f"\n⚠️ PARTIAL SUCCESS: One sensor fixed")
        else:
            print(f"\n❌ FAILED: Both sensors still showing test patterns")
            print(f"\n💡 TROUBLESHOOTING:")
            print(f"   1. Check Kinect positioning - should face objects/room")
            print(f"   2. Ensure adequate lighting for RGB camera")
            print(f"   3. Place objects in front of Kinect for depth sensing")
            print(f"   4. Check if Kinect is too close/far from objects")
        
        return final_depth_real and final_rgb_real

def main():
    """Run Kinect real-world sensor fix"""
    fix_system = KinectRealWorldFix()
    
    try:
        success = fix_system.run_real_world_fix()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Real-world fix failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
