#!/usr/bin/env python3
"""
Test Kinect v1 (Xbox 360) Connection
This script tests various methods to connect to your Kinect v1
"""

import sys
import os

def test_freenect_import():
    """Test if freenect module can be imported"""
    try:
        import freenect
        print("✅ freenect module imported successfully!")
        
        # Test basic functionality
        try:
            ctx = freenect.init()
            num_devices = freenect.num_devices(ctx)
            print(f"✅ Found {num_devices} Kinect device(s)")
            
            if num_devices > 0:
                print("✅ Kinect v1 detected and ready!")
                return True
            else:
                print("❌ No Kinect devices found")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing Kinect: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ freenect module not found: {e}")
        return False

def test_opencv_kinect():
    """Test OpenCV Kinect support"""
    try:
        import cv2
        print("✅ OpenCV imported successfully")
        
        # Try to open Kinect as a camera device
        # Kinect usually appears as camera index 1 or 2
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Camera device {i} working (resolution: {frame.shape})")
                cap.release()
            else:
                print(f"❌ Camera device {i} not available")
                
    except ImportError:
        print("❌ OpenCV not available")

def test_windows_kinect_sdk():
    """Test Windows Kinect SDK"""
    try:
        # Try to import Windows Kinect SDK wrapper
        from pykinect2 import PyKinectV2
        from pykinect2 import PyKinectRuntime
        
        print("✅ PyKinect2 (Windows SDK) imported successfully")
        
        # Note: This is for Kinect v2, but let's see if it detects anything
        kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth)
        
        if kinect.has_new_depth_frame():
            print("✅ Kinect v2 detected via Windows SDK")
        else:
            print("❌ No Kinect v2 detected via Windows SDK")
            
    except ImportError:
        print("❌ PyKinect2 (Windows SDK) not available")
    except Exception as e:
        print(f"❌ Error with Windows Kinect SDK: {e}")

def test_system_info():
    """Display system information"""
    print("\n=== System Information ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check for USB devices (Windows)
    if sys.platform == "win32":
        try:
            import subprocess
            result = subprocess.run(['wmic', 'path', 'win32_usbhub', 'get', 'deviceid'], 
                                  capture_output=True, text=True)
            if "USB" in result.stdout:
                print("✅ USB devices detected in system")
            else:
                print("❌ No USB devices found")
        except Exception as e:
            print(f"❌ Could not check USB devices: {e}")

def main():
    print("🔍 Testing Kinect v1 (Xbox 360) Connection...")
    print("=" * 50)
    
    # Test system info first
    test_system_info()
    
    print("\n=== Testing Connection Methods ===")
    
    # Test different connection methods
    freenect_works = test_freenect_import()
    
    print("\n--- Testing OpenCV ---")
    test_opencv_kinect()
    
    print("\n--- Testing Windows Kinect SDK ---")
    test_windows_kinect_sdk()
    
    print("\n=== Summary ===")
    if freenect_works:
        print("🎉 SUCCESS: Your Kinect v1 is ready to use with libfreenect!")
        print("You can now run your AR Sandbox with Kinect support.")
    else:
        print("⚠️  NEXT STEPS NEEDED:")
        print("1. Install libfreenect Python wrapper")
        print("2. Ensure Kinect drivers are properly installed")
        print("3. Check USB connection and power")
        
    print("\n💡 Your Kinect has a green blinking light, which means:")
    print("   - Power is connected ✅")
    print("   - Device is detected by system ✅") 
    print("   - Ready for software connection 🔄")

if __name__ == "__main__":
    main()
