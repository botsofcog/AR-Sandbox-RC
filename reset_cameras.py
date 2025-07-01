#!/usr/bin/env python3
"""
🔄 AR Sandbox RC - Camera Reset Utility
Resets all camera processes and hardware connections
"""

import subprocess
import time
import sys
import os
import cv2
import psutil

def print_header():
    print("🔄 AR Sandbox RC - Camera Reset Utility")
    print("=" * 50)
    print()

def kill_camera_processes():
    """Kill all camera-related processes"""
    print("🛑 Killing camera processes...")
    
    camera_processes = [
        "Camera.exe",
        "WindowsCamera.exe", 
        "opencv_videoio_msmf.exe",
        "python.exe",  # Our own camera scripts
    ]
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name']
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            
            # Kill camera processes
            if proc_name in camera_processes:
                print(f"  🛑 Killing {proc_name} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
            
            # Kill our camera scripts specifically
            elif 'camera' in cmdline.lower() or 'kinect' in cmdline.lower():
                print(f"  🛑 Killing camera script: {proc_name} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"✅ Killed {killed_count} camera processes")
    time.sleep(2)

def reset_opencv_cameras():
    """Reset OpenCV camera connections"""
    print("📹 Resetting OpenCV camera connections...")
    
    # Try to open and immediately close all camera indices
    for i in range(10):  # Check first 10 camera indices
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  📹 Found camera at index {i}")
                cap.release()
            time.sleep(0.1)
        except Exception as e:
            pass
    
    # Force release all VideoCapture objects
    cv2.destroyAllWindows()
    print("✅ OpenCV cameras reset")

def reset_kinect_hardware():
    """Reset Kinect hardware connection"""
    print("🎯 Resetting Kinect v1 hardware...")
    
    try:
        # Try to restart Kinect-related services
        services = ["KinectManagement", "KinectService"]
        for service in services:
            try:
                subprocess.run(["net", "stop", service], 
                             capture_output=True, check=False)
                time.sleep(1)
                subprocess.run(["net", "start", service], 
                             capture_output=True, check=False)
                print(f"  🔄 Restarted service: {service}")
            except Exception:
                pass
        
        print("💡 Manual Kinect reset recommended:")
        print("  1. Unplug Kinect USB cable")
        print("  2. Wait 10 seconds")
        print("  3. Plug back in")
        print("  4. Wait for green light")
        
    except Exception as e:
        print(f"⚠️ Kinect reset warning: {e}")

def reset_windows_camera_service():
    """Reset Windows Camera Service"""
    print("🔧 Resetting Windows Camera Service...")
    
    try:
        # Stop Windows Camera Service
        subprocess.run(["net", "stop", "FrameServer"], 
                      capture_output=True, check=False)
        time.sleep(2)
        
        # Start Windows Camera Service
        subprocess.run(["net", "start", "FrameServer"], 
                      capture_output=True, check=False)
        time.sleep(2)
        
        print("✅ Windows Camera Service reset")
        
    except Exception as e:
        print(f"⚠️ Service reset warning: {e}")

def test_camera_availability():
    """Test which cameras are available after reset"""
    print("🧪 Testing camera availability...")
    
    available_cameras = []
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    available_cameras.append(i)
                    print(f"  ✅ Camera {i}: Available")
                else:
                    print(f"  ❌ Camera {i}: No signal")
                cap.release()
            else:
                print(f"  ❌ Camera {i}: Cannot open")
        except Exception as e:
            print(f"  ❌ Camera {i}: Error - {e}")
        
        time.sleep(0.1)
    
    print(f"📊 Total available cameras: {len(available_cameras)}")
    return available_cameras

def main():
    print_header()
    
    try:
        # Step 1: Kill camera processes
        kill_camera_processes()
        
        # Step 2: Reset OpenCV cameras
        reset_opencv_cameras()
        
        # Step 3: Reset Windows Camera Service
        reset_windows_camera_service()
        
        # Step 4: Reset Kinect hardware
        reset_kinect_hardware()
        
        # Step 5: Wait for hardware to stabilize
        print("⏳ Waiting for hardware to stabilize...")
        time.sleep(5)
        
        # Step 6: Test camera availability
        available_cameras = test_camera_availability()
        
        print()
        print("🎉 Camera reset complete!")
        print(f"📹 {len(available_cameras)} cameras available: {available_cameras}")
        print()
        print("💡 Next steps:")
        print("  1. Refresh your browser")
        print("  2. Run the debug demo again")
        print("  3. Test the 4-camera system")
        print()
        
        if len(available_cameras) < 3:
            print("⚠️ WARNING: Less than 3 cameras detected!")
            print("   Expected: Kinect RGB + Kinect Depth + 2 Webcams")
            print("   Check hardware connections and drivers")
        
    except KeyboardInterrupt:
        print("\n🛑 Reset cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Reset error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running as administrator
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        print("⚠️ WARNING: Not running as administrator")
        print("   Some reset operations may fail")
        print("   Consider running as admin for full reset")
        print()
    
    main()
