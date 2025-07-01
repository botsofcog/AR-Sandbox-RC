#!/usr/bin/env python3
"""
Simple Kinect detection test
"""

import sys
import time

def test_kinect_v1():
    """Test Kinect v1 detection"""
    try:
        import freenect
        print("✅ Kinect v1 library (freenect) found!")
        
        # Try to get device count
        ctx = freenect.init()
        num_devices = freenect.num_devices(ctx)
        print(f"📱 Kinect v1 devices detected: {num_devices}")
        
        if num_devices > 0:
            print("🎉 Kinect v1 is connected and ready!")
            return True
        else:
            print("❌ No Kinect v1 devices found")
            return False
            
    except ImportError:
        print("❌ Kinect v1 library (freenect) not available")
        return False
    except Exception as e:
        print(f"❌ Kinect v1 error: {e}")
        return False

def test_kinect_v2():
    """Test Kinect v2 detection"""
    try:
        from pylibfreenect2 import Freenect2, SyncMultiFrameListener
        print("✅ Kinect v2 library (pylibfreenect2) found!")
        
        fn = Freenect2()
        num_devices = fn.enumerateDevices()
        print(f"📱 Kinect v2 devices detected: {num_devices}")
        
        if num_devices > 0:
            print("🎉 Kinect v2 is connected and ready!")
            return True
        else:
            print("❌ No Kinect v2 devices found")
            return False
            
    except ImportError:
        print("❌ Kinect v2 library (pylibfreenect2) not available")
        return False
    except Exception as e:
        print(f"❌ Kinect v2 error: {e}")
        return False

def test_opencv_camera():
    """Test if any camera/depth sensor is available via OpenCV"""
    try:
        import cv2
        print("✅ OpenCV found!")

        # Try multiple camera indices for Kinect
        for i in range(5):
            print(f"  Testing camera index {i}...")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"📹 Camera device {i} found: {frame.shape}")
                    cap.release()
                    return True
                cap.release()

        print("❌ No working cameras found via OpenCV")
        return False

    except ImportError:
        print("❌ OpenCV not available")
        return False
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
        return False

def test_kinect_libusb():
    """Test if Kinect is accessible via libusb driver"""
    try:
        import usb.core
        import usb.util
        print("✅ PyUSB found!")

        # Xbox 360 Kinect USB IDs
        KINECT_VID = 0x045e  # Microsoft
        KINECT_PID = 0x02ae  # Kinect for Xbox 360

        # Find Kinect device
        dev = usb.core.find(idVendor=KINECT_VID, idProduct=KINECT_PID)
        if dev is not None:
            print(f"🎮 Xbox 360 Kinect found!")
            print(f"   Vendor ID: 0x{dev.idVendor:04x}")
            print(f"   Product ID: 0x{dev.idProduct:04x}")
            print(f"   Device: {dev}")
            return True
        else:
            print("❌ Xbox 360 Kinect not found via USB")

            # List all USB devices to see what's connected
            print("\n📋 All USB devices:")
            devices = usb.core.find(find_all=True)
            for device in devices:
                if device.idVendor == KINECT_VID:  # Microsoft devices
                    print(f"   Microsoft device: VID=0x{device.idVendor:04x}, PID=0x{device.idProduct:04x}")

            return False

    except ImportError:
        print("❌ PyUSB not available (pip install pyusb)")
        return False
    except Exception as e:
        print(f"❌ USB error: {e}")
        return False

def test_kinect_working():
    """Test if Kinect is actually working with current drivers"""
    try:
        import cv2
        print("✅ Testing Kinect with OpenCV...")

        # Try to access Kinect camera
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"📹 Camera {i}: {width}x{height} - {frame.dtype}")

                    # Check if this looks like Kinect resolution
                    if width == 640 and height == 480:
                        print(f"🎮 Possible Kinect camera at index {i}")
                    cap.release()
                    return True
                cap.release()

        print("❌ No working cameras found")
        return False

    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def test_magic_sand_connection():
    """Test if Magic Sand can connect to Kinect"""
    print("🎮 Testing Magic Sand Kinect connection...")

    # Check if Magic Sand is running and detecting Kinect
    try:
        import psutil
        magic_sand_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            if 'Magic-Sand' in proc.info['name']:
                magic_sand_running = True
                print(f"✅ Magic Sand is running (PID: {proc.info['pid']})")
                break

        if not magic_sand_running:
            print("⚠️ Magic Sand not currently running")

        return magic_sand_running

    except ImportError:
        print("⚠️ psutil not available, cannot check Magic Sand status")
        return False
    except Exception as e:
        print(f"❌ Error checking Magic Sand: {e}")
        return False

def main():
    print("🎮 KINECT WORKING - COMPREHENSIVE TESTING")
    print("=" * 60)

    # Test different Kinect versions
    kinect_v1_found = test_kinect_v1()
    print()
    kinect_v2_found = test_kinect_v2()
    print()
    camera_found = test_opencv_camera()
    print()
    kinect_usb_found = test_kinect_libusb()
    print()
    kinect_working = test_kinect_working()
    print()
    magic_sand_status = test_magic_sand_connection()
    print()
    
    print("=" * 50)
    print("📊 RESULTS:")
    
    if kinect_v1_found:
        print("🎯 Kinect v1 detected - Use freenect library")
    elif kinect_v2_found:
        print("🎯 Kinect v2 detected - Use pylibfreenect2 library")
    elif camera_found:
        print("📹 Regular camera detected - Can use for basic testing")
    else:
        print("❌ No depth sensors detected")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check Kinect USB connection")
        print("2. Install Kinect SDK drivers")
        print("3. Try different USB port")
        print("4. Check Device Manager for Kinect")
    
    print("\n💡 Next steps:")
    if kinect_v1_found or kinect_v2_found:
        print("- Run the AR sandbox with Kinect support")
        print("- Calibrate the sensor")
        print("- Test depth detection")
    else:
        print("- Install missing drivers")
        print("- Check hardware connections")
        print("- Use webcam mode for testing")

if __name__ == "__main__":
    main()
