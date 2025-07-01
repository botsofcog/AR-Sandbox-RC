#!/usr/bin/env python3
"""
Kinect Diagnostic Tool
Diagnoses and fixes issues with both Kinect depth sensor and RGB camera
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library loaded successfully")
except ImportError as e:
    KINECT_AVAILABLE = False
    print(f"❌ Kinect library not available: {e}")

def test_kinect_depth_sensor():
    """Test Kinect depth sensor specifically"""
    print("\n🔍 TESTING KINECT DEPTH SENSOR...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect library not available")
        return False
    
    try:
        # Test depth sensor access
        print("   📡 Attempting depth sensor access...")
        depth_frame = freenect.sync_get_depth()[0]
        
        if depth_frame is None:
            print("   ❌ Depth sensor returned None")
            return False
        
        # Analyze depth frame
        print(f"   ✅ Depth frame captured: {depth_frame.shape}")
        print(f"   📊 Depth range: {np.min(depth_frame)} to {np.max(depth_frame)}")
        
        # Check for valid data
        valid_pixels = np.sum(depth_frame > 0)
        total_pixels = depth_frame.size
        coverage = (valid_pixels / total_pixels) * 100
        
        print(f"   📈 Valid pixels: {valid_pixels}/{total_pixels} ({coverage:.1f}%)")
        
        if coverage < 10:
            print("   ⚠️ Very low depth coverage - check sensor positioning")
        elif coverage < 50:
            print("   ⚠️ Low depth coverage - may need adjustment")
        else:
            print("   ✅ Good depth coverage")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Depth sensor test failed: {e}")
        return False

def test_kinect_rgb_camera():
    """Test Kinect RGB camera specifically"""
    print("\n📷 TESTING KINECT RGB CAMERA...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect library not available")
        return False
    
    try:
        # Test RGB camera access
        print("   📡 Attempting RGB camera access...")
        rgb_frame = freenect.sync_get_video()[0]
        
        if rgb_frame is None:
            print("   ❌ RGB camera returned None")
            return False
        
        # Analyze RGB frame
        print(f"   ✅ RGB frame captured: {rgb_frame.shape}")
        
        # Check image quality
        gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        print(f"   📊 Brightness: {brightness:.1f} (optimal: 100-150)")
        print(f"   📊 Contrast: {contrast:.1f} (optimal: >30)")
        
        if brightness < 50:
            print("   ⚠️ Image too dark - check lighting or positioning")
        elif brightness > 200:
            print("   ⚠️ Image too bright - reduce lighting or adjust position")
        else:
            print("   ✅ Good brightness level")
        
        if contrast < 20:
            print("   ⚠️ Low contrast - check scene content")
        else:
            print("   ✅ Good contrast level")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RGB camera test failed: {e}")
        return False

def test_kinect_synchronization():
    """Test if both Kinect cameras work together"""
    print("\n🔄 TESTING KINECT CAMERA SYNCHRONIZATION...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect library not available")
        return False
    
    try:
        success_count = 0
        test_frames = 10
        
        print(f"   🧪 Testing {test_frames} synchronized captures...")
        
        for i in range(test_frames):
            try:
                # Capture both simultaneously
                depth_frame = freenect.sync_get_depth()[0]
                rgb_frame = freenect.sync_get_video()[0]
                
                if depth_frame is not None and rgb_frame is not None:
                    success_count += 1
                    print(f"      Frame {i+1}: ✅ Both cameras captured")
                else:
                    print(f"      Frame {i+1}: ❌ One or both cameras failed")
                
                time.sleep(0.1)  # Small delay between captures
                
            except Exception as e:
                print(f"      Frame {i+1}: ❌ Error: {e}")
        
        success_rate = (success_count / test_frames) * 100
        print(f"   📊 Synchronization success rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("   ✅ Excellent synchronization")
        elif success_rate >= 70:
            print("   ⚠️ Good synchronization with some issues")
        else:
            print("   ❌ Poor synchronization - needs fixing")
        
        return success_rate >= 70
        
    except Exception as e:
        print(f"   ❌ Synchronization test failed: {e}")
        return False

def diagnose_kinect_issues():
    """Diagnose specific Kinect issues"""
    print("\n🔧 DIAGNOSING KINECT ISSUES...")
    
    issues = []
    fixes = []
    
    # Check if Kinect is detected
    if not KINECT_AVAILABLE:
        issues.append("Kinect library not available")
        fixes.append("Install libfreenect: pip install freenect")
        return issues, fixes
    
    try:
        # Test basic Kinect access
        print("   🔍 Testing basic Kinect device access...")
        
        # Try to get device count
        device_count = freenect.num_devices()
        print(f"   📱 Kinect devices detected: {device_count}")
        
        if device_count == 0:
            issues.append("No Kinect devices detected")
            fixes.append("Check USB connection and power supply")
            fixes.append("Install Kinect drivers using Zadig")
            return issues, fixes
        
        # Test depth sensor specifically
        depth_ok = test_kinect_depth_sensor()
        if not depth_ok:
            issues.append("Depth sensor not working properly")
            fixes.append("Check Kinect positioning and distance to objects")
            fixes.append("Ensure adequate lighting for IR sensor")
        
        # Test RGB camera specifically
        rgb_ok = test_kinect_rgb_camera()
        if not rgb_ok:
            issues.append("RGB camera not working properly")
            fixes.append("Check Kinect positioning and lighting")
            fixes.append("Ensure no obstructions to camera lens")
        
        # Test synchronization
        sync_ok = test_kinect_synchronization()
        if not sync_ok:
            issues.append("Camera synchronization issues")
            fixes.append("Close other applications using Kinect")
            fixes.append("Restart Kinect service or reconnect device")
        
        if not issues:
            print("   ✅ No issues detected - Kinect cameras working properly")
        
    except Exception as e:
        issues.append(f"Kinect diagnostic error: {e}")
        fixes.append("Restart computer and reconnect Kinect")
        fixes.append("Reinstall Kinect drivers")
    
    return issues, fixes

def apply_kinect_fixes():
    """Apply automatic fixes for common Kinect issues"""
    print("\n🔧 APPLYING KINECT FIXES...")
    
    fixes_applied = []
    
    if not KINECT_AVAILABLE:
        print("   ❌ Cannot apply fixes - Kinect library not available")
        return fixes_applied
    
    try:
        # Fix 1: Reset Kinect device
        print("   🔄 Resetting Kinect device...")
        try:
            freenect.close_device(freenect.open_device(0))
            fixes_applied.append("Device reset")
        except:
            pass
        
        # Fix 2: Set optimal modes
        print("   ⚙️ Setting optimal camera modes...")
        try:
            # Set depth mode
            freenect.set_depth_mode(0, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
            fixes_applied.append("Depth mode optimization")
        except:
            pass
        
        try:
            # Set video mode
            freenect.set_video_mode(0, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
            fixes_applied.append("Video mode optimization")
        except:
            pass
        
        # Fix 3: Clear any stuck states
        print("   🧹 Clearing stuck states...")
        try:
            # Force a few captures to clear buffers
            for _ in range(3):
                freenect.sync_get_depth()
                freenect.sync_get_video()
                time.sleep(0.1)
            fixes_applied.append("Buffer clearing")
        except:
            pass
        
    except Exception as e:
        print(f"   ❌ Fix application error: {e}")
    
    return fixes_applied

def main():
    """Run complete Kinect diagnostic and fix"""
    print("="*60)
    print("🔧 KINECT DIAGNOSTIC & FIX TOOL")
    print("="*60)
    
    # Run diagnostics
    issues, fixes = diagnose_kinect_issues()
    
    # Apply automatic fixes
    applied_fixes = apply_kinect_fixes()
    
    # Generate report
    print("\n" + "="*60)
    print("📊 KINECT DIAGNOSTIC REPORT")
    print("="*60)
    
    if issues:
        print(f"⚠️ ISSUES FOUND ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 RECOMMENDED FIXES:")
        for i, fix in enumerate(fixes, 1):
            print(f"   {i}. {fix}")
    else:
        print("✅ NO ISSUES FOUND - Kinect cameras working properly")
    
    if applied_fixes:
        print(f"\n🛠️ FIXES APPLIED ({len(applied_fixes)}):")
        for i, fix in enumerate(applied_fixes, 1):
            print(f"   {i}. {fix}")
    
    # Final test
    print(f"\n🧪 FINAL VERIFICATION:")
    depth_final = test_kinect_depth_sensor()
    rgb_final = test_kinect_rgb_camera()
    
    if depth_final and rgb_final:
        print("🎉 SUCCESS: Both Kinect cameras working properly!")
        return 0
    else:
        print("❌ ISSUES REMAIN: Manual intervention required")
        return 1

if __name__ == "__main__":
    sys.exit(main())
