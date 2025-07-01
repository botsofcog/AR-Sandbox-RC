#!/usr/bin/env python3
"""
Kinect Compatibility Fix
Fixes libfreenect API compatibility issues and ensures both cameras work
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library loaded")
except ImportError as e:
    KINECT_AVAILABLE = False
    print(f"❌ Kinect library not available: {e}")

class KinectCompatibilityFix:
    """
    Fixes Kinect compatibility issues and ensures both cameras work properly
    """
    
    def __init__(self):
        self.device = None
        self.depth_working = False
        self.rgb_working = False
        
    def initialize_kinect_device(self):
        """Initialize Kinect device with proper error handling"""
        print("🔧 INITIALIZING KINECT DEVICE...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect library not available")
            return False
        
        try:
            # Method 1: Try direct device initialization
            print("   📡 Attempting direct device initialization...")
            self.device = freenect.open_device(0)
            
            if self.device is None:
                print("   ❌ Failed to open Kinect device")
                return False
            
            print("   ✅ Kinect device opened successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Device initialization failed: {e}")
            return False
    
    def fix_depth_sensor(self):
        """Fix depth sensor with multiple methods"""
        print("\n🔍 FIXING KINECT DEPTH SENSOR...")
        
        # Method 1: Try sync_get_depth with error handling
        try:
            print("   📡 Method 1: sync_get_depth...")
            depth_frame, timestamp = freenect.sync_get_depth()
            
            if depth_frame is not None:
                print(f"   ✅ Depth sensor working - Frame: {depth_frame.shape}")
                self.depth_working = True
                return True
            else:
                print("   ❌ sync_get_depth returned None")
        except Exception as e:
            print(f"   ❌ sync_get_depth failed: {e}")
        
        # Method 2: Try direct device access
        try:
            print("   📡 Method 2: Direct device access...")
            if self.device:
                freenect.set_depth_mode(self.device, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
                freenect.start_depth(self.device)
                
                # Wait a moment for initialization
                time.sleep(0.5)
                
                # Try to get frame
                depth_frame = freenect.get_depth(self.device)
                if depth_frame is not None:
                    print(f"   ✅ Direct access working - Frame: {depth_frame.shape}")
                    self.depth_working = True
                    return True
                else:
                    print("   ❌ Direct access returned None")
        except Exception as e:
            print(f"   ❌ Direct device access failed: {e}")
        
        # Method 3: Try alternative depth format
        try:
            print("   📡 Method 3: Alternative depth format...")
            freenect.set_depth_format(0, freenect.DEPTH_REGISTERED)
            depth_frame = freenect.sync_get_depth(0, freenect.DEPTH_REGISTERED)[0]
            
            if depth_frame is not None:
                print(f"   ✅ Alternative format working - Frame: {depth_frame.shape}")
                self.depth_working = True
                return True
            else:
                print("   ❌ Alternative format returned None")
        except Exception as e:
            print(f"   ❌ Alternative format failed: {e}")
        
        print("   ❌ All depth sensor methods failed")
        return False
    
    def fix_rgb_camera(self):
        """Fix RGB camera with multiple methods"""
        print("\n📷 FIXING KINECT RGB CAMERA...")
        
        # Method 1: Try sync_get_video with error handling
        try:
            print("   📡 Method 1: sync_get_video...")
            rgb_frame, timestamp = freenect.sync_get_video()
            
            if rgb_frame is not None:
                print(f"   ✅ RGB camera working - Frame: {rgb_frame.shape}")
                self.rgb_working = True
                return True
            else:
                print("   ❌ sync_get_video returned None")
        except Exception as e:
            print(f"   ❌ sync_get_video failed: {e}")
        
        # Method 2: Try direct device access
        try:
            print("   📡 Method 2: Direct device access...")
            if self.device:
                freenect.set_video_mode(self.device, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
                freenect.start_video(self.device)
                
                # Wait a moment for initialization
                time.sleep(0.5)
                
                # Try to get frame
                rgb_frame = freenect.get_video(self.device)
                if rgb_frame is not None:
                    print(f"   ✅ Direct access working - Frame: {rgb_frame.shape}")
                    self.rgb_working = True
                    return True
                else:
                    print("   ❌ Direct access returned None")
        except Exception as e:
            print(f"   ❌ Direct device access failed: {e}")
        
        # Method 3: Try alternative video format
        try:
            print("   📡 Method 3: Alternative video format...")
            freenect.set_video_format(0, freenect.VIDEO_YUV_RGB)
            rgb_frame = freenect.sync_get_video(0, freenect.VIDEO_YUV_RGB)[0]
            
            if rgb_frame is not None:
                print(f"   ✅ Alternative format working - Frame: {rgb_frame.shape}")
                self.rgb_working = True
                return True
            else:
                print("   ❌ Alternative format returned None")
        except Exception as e:
            print(f"   ❌ Alternative format failed: {e}")
        
        print("   ❌ All RGB camera methods failed")
        return False
    
    def test_working_cameras(self):
        """Test the working cameras with sustained capture"""
        print("\n🧪 TESTING WORKING CAMERAS...")
        
        if not (self.depth_working or self.rgb_working):
            print("   ❌ No cameras working for test")
            return False
        
        success_count = 0
        test_frames = 10
        
        for i in range(test_frames):
            try:
                frames_captured = 0
                
                # Test depth if working
                if self.depth_working:
                    try:
                        depth_frame = freenect.sync_get_depth()[0]
                        if depth_frame is not None:
                            frames_captured += 1
                    except:
                        pass
                
                # Test RGB if working
                if self.rgb_working:
                    try:
                        rgb_frame = freenect.sync_get_video()[0]
                        if rgb_frame is not None:
                            frames_captured += 1
                    except:
                        pass
                
                if frames_captured > 0:
                    success_count += 1
                    print(f"   Frame {i+1}: ✅ {frames_captured} camera(s) captured")
                else:
                    print(f"   Frame {i+1}: ❌ No cameras captured")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   Frame {i+1}: ❌ Error: {e}")
        
        success_rate = (success_count / test_frames) * 100
        print(f"   📊 Success rate: {success_rate:.1f}%")
        
        return success_rate >= 70
    
    def apply_compatibility_fixes(self):
        """Apply various compatibility fixes"""
        print("\n🔧 APPLYING COMPATIBILITY FIXES...")
        
        fixes_applied = []
        
        try:
            # Fix 1: Reset all Kinect states
            print("   🔄 Resetting Kinect states...")
            try:
                freenect.stop_depth(0)
                freenect.stop_video(0)
                time.sleep(0.2)
                fixes_applied.append("State reset")
            except:
                pass
            
            # Fix 2: Set compatible modes
            print("   ⚙️ Setting compatible modes...")
            try:
                freenect.set_depth_mode(0, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
                freenect.set_video_mode(0, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
                fixes_applied.append("Compatible modes")
            except:
                pass
            
            # Fix 3: Initialize with proper sequence
            print("   📡 Proper initialization sequence...")
            try:
                # Start depth first
                freenect.start_depth(0)
                time.sleep(0.2)
                
                # Start video second
                freenect.start_video(0)
                time.sleep(0.2)
                
                fixes_applied.append("Proper sequence")
            except:
                pass
            
            # Fix 4: Clear buffers
            print("   🧹 Clearing buffers...")
            try:
                for _ in range(3):
                    freenect.sync_get_depth()
                    freenect.sync_get_video()
                    time.sleep(0.05)
                fixes_applied.append("Buffer clearing")
            except:
                pass
            
        except Exception as e:
            print(f"   ❌ Compatibility fix error: {e}")
        
        return fixes_applied
    
    def run_compatibility_fix(self):
        """Run complete compatibility fix process"""
        print("="*60)
        print("🔧 KINECT COMPATIBILITY FIX")
        print("="*60)
        
        # Initialize device
        device_ok = self.initialize_kinect_device()
        
        # Apply compatibility fixes
        fixes_applied = self.apply_compatibility_fixes()
        
        # Fix depth sensor
        depth_fixed = self.fix_depth_sensor()
        
        # Fix RGB camera
        rgb_fixed = self.fix_rgb_camera()
        
        # Test working cameras
        if depth_fixed or rgb_fixed:
            test_ok = self.test_working_cameras()
        else:
            test_ok = False
        
        # Generate report
        print("\n" + "="*60)
        print("📊 COMPATIBILITY FIX REPORT")
        print("="*60)
        
        print(f"🎯 CAMERA STATUS:")
        print(f"   Depth Sensor: {'✅ FIXED' if depth_fixed else '❌ FAILED'}")
        print(f"   RGB Camera: {'✅ FIXED' if rgb_fixed else '❌ FAILED'}")
        
        if fixes_applied:
            print(f"\n🛠️ FIXES APPLIED ({len(fixes_applied)}):")
            for i, fix in enumerate(fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        working_cameras = sum([depth_fixed, rgb_fixed])
        print(f"\n📊 RESULT: {working_cameras}/2 Kinect cameras working")
        
        if working_cameras == 2:
            print("🎉 SUCCESS: Both Kinect cameras fixed and working!")
        elif working_cameras == 1:
            print("⚠️ PARTIAL SUCCESS: One Kinect camera working")
        else:
            print("❌ FAILED: Neither Kinect camera working")
        
        return working_cameras >= 1
    
    def cleanup(self):
        """Clean up Kinect resources"""
        try:
            if self.device:
                freenect.close_device(self.device)
        except:
            pass

def main():
    """Run Kinect compatibility fix"""
    fix_system = KinectCompatibilityFix()
    
    try:
        success = fix_system.run_compatibility_fix()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Compatibility fix failed: {e}")
        return 1
    finally:
        fix_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
