#!/usr/bin/env python3
"""
Test webcam detection to ensure simultaneous Kinect + Webcam operation
"""

import cv2
import sys

def test_webcam_detection():
    """Test all possible webcam configurations"""
    print("🔍 Testing webcam detection for simultaneous Kinect + Webcam operation")
    print("=" * 60)
    
    working_cameras = []
    
    # Test DirectShow backend specifically
    print("\n📹 Testing DirectShow backend (Windows native):")
    for i in range(6):  # Test cameras 0-5
        try:
            print(f"  Testing camera {i} with DirectShow...")
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"  ✅ Camera {i}: {width}x{height} - WORKING")
                    working_cameras.append({
                        'index': i,
                        'backend': 'DirectShow',
                        'backend_id': cv2.CAP_DSHOW,
                        'resolution': f"{width}x{height}"
                    })
                else:
                    print(f"  ❌ Camera {i}: Opens but no frames")
                cap.release()
            else:
                print(f"  ❌ Camera {i}: Failed to open")
                
        except Exception as e:
            print(f"  ❌ Camera {i}: Error - {e}")
    
    # Test default backend
    print("\n📹 Testing default backend:")
    for i in range(3):  # Test cameras 0-2
        try:
            print(f"  Testing camera {i} with default backend...")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"  ✅ Camera {i}: {width}x{height} - WORKING")
                    # Only add if not already found with DirectShow
                    if not any(cam['index'] == i for cam in working_cameras):
                        working_cameras.append({
                            'index': i,
                            'backend': 'Default',
                            'backend_id': None,
                            'resolution': f"{width}x{height}"
                        })
                else:
                    print(f"  ❌ Camera {i}: Opens but no frames")
                cap.release()
            else:
                print(f"  ❌ Camera {i}: Failed to open")
                
        except Exception as e:
            print(f"  ❌ Camera {i}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("📊 WEBCAM DETECTION RESULTS:")
    
    if working_cameras:
        print(f"✅ Found {len(working_cameras)} working camera(s):")
        for cam in working_cameras:
            print(f"   Camera {cam['index']}: {cam['backend']} backend, {cam['resolution']}")
        
        print(f"\n🎯 RECOMMENDED CONFIG for simultaneous operation:")
        best_cam = working_cameras[0]
        print(f"   Use Camera {best_cam['index']} with {best_cam['backend']} backend")
        print(f"   cv2.VideoCapture({best_cam['index']}, cv2.CAP_DSHOW)")
        
        return working_cameras
    else:
        print("❌ No working webcams detected!")
        print("🔧 Possible solutions:")
        print("   1. Check if webcam is connected and not in use by another app")
        print("   2. Try different USB ports")
        print("   3. Update webcam drivers")
        print("   4. Check Windows Camera app works")
        
        return []

if __name__ == "__main__":
    working_cameras = test_webcam_detection()
    
    if working_cameras:
        print(f"\n🎉 SUCCESS: {len(working_cameras)} webcam(s) available for simultaneous Kinect + Webcam operation!")
        sys.exit(0)
    else:
        print(f"\n💥 FAILURE: No webcams available - will use Kinect-only mode")
        sys.exit(1)
