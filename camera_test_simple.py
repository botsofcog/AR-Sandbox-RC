#!/usr/bin/env python3
"""
Simple Camera Test - Verify what's actually working
"""

import cv2
import numpy as np
import time

def test_opencv_display():
    """Test if OpenCV can display windows"""
    print("🧪 TESTING OPENCV DISPLAY...")
    
    try:
        # Create a simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = (0, 255, 0)  # Green
        
        cv2.putText(test_image, "OpenCV Test Window", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        cv2.imshow("OpenCV Test", test_image)
        print("   ✅ Test window created")
        print("   Press any key in the window to continue...")
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("   ✅ OpenCV display working")
        return True
        
    except Exception as e:
        print(f"   ❌ OpenCV display failed: {e}")
        return False

def test_webcams():
    """Test webcam access"""
    print("\n🧪 TESTING WEBCAMS...")
    
    webcams_found = []
    
    for i in range(3):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    webcams_found.append({
                        'index': i,
                        'resolution': f"{width}x{height}",
                        'working': True
                    })
                    print(f"   ✅ Webcam {i}: {width}x{height}")
                else:
                    print(f"   ❌ Webcam {i}: Cannot capture frame")
                cap.release()
            else:
                print(f"   ❌ Webcam {i}: Cannot open")
        except Exception as e:
            print(f"   ❌ Webcam {i}: Error {e}")
    
    print(f"   📊 Total working webcams: {len(webcams_found)}")
    return webcams_found

def test_kinect():
    """Test Kinect access"""
    print("\n🧪 TESTING KINECT...")
    
    try:
        import freenect
        print("   ✅ Kinect library imported")
        
        # Test depth
        try:
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is not None:
                print(f"   ✅ Kinect depth: {depth_frame.shape}")
                valid_pixels = np.sum(depth_frame > 0)
                print(f"   📊 Valid depth pixels: {valid_pixels}")
            else:
                print("   ❌ Kinect depth: No data")
        except Exception as e:
            print(f"   ❌ Kinect depth: {e}")
        
        # Test RGB
        try:
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is not None:
                print(f"   ✅ Kinect RGB: {rgb_frame.shape}")
            else:
                print("   ❌ Kinect RGB: No data")
        except Exception as e:
            print(f"   ❌ Kinect RGB: {e}")
            
    except ImportError:
        print("   ❌ Kinect library not available")

def show_single_camera():
    """Show one camera at a time for testing"""
    print("\n📹 SINGLE CAMERA DISPLAY TEST")
    print("This will show one camera at a time")
    
    # Test Kinect depth
    try:
        import freenect
        print("\nShowing Kinect depth for 5 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                if depth_frame is not None:
                    depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(depth_colored, "KINECT DEPTH - 5 SEC TEST", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow("Kinect Depth Test", depth_colored)
                    
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC
                        break
            except:
                break
        
        cv2.destroyAllWindows()
        print("Kinect depth test complete")
        
    except ImportError:
        print("Kinect not available")
    
    # Test webcam
    print("\nShowing Webcam 0 for 5 seconds...")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            start_time = time.time()
            while time.time() - start_time < 5:
                ret, frame = cap.read()
                if ret:
                    cv2.putText(frame, "WEBCAM 0 - 5 SEC TEST", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow("Webcam Test", frame)
                    
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC
                        break
            
            cap.release()
            cv2.destroyAllWindows()
            print("Webcam test complete")
        else:
            print("Cannot open webcam")
    except Exception as e:
        print(f"Webcam test failed: {e}")

def main():
    """Run simple camera tests"""
    print("="*50)
    print("🧪 SIMPLE CAMERA TEST")
    print("="*50)
    
    # Test 1: OpenCV display
    opencv_ok = test_opencv_display()
    
    if not opencv_ok:
        print("❌ OpenCV display not working - cannot show camera feeds")
        return
    
    # Test 2: Camera access
    webcams = test_webcams()
    test_kinect()
    
    # Test 3: Single camera display
    response = input("\nShow single camera displays? (y/n): ").lower().strip()
    if response == 'y':
        show_single_camera()
    
    print("\n📊 SUMMARY:")
    print(f"   OpenCV display: {'✅ Working' if opencv_ok else '❌ Failed'}")
    print(f"   Webcams found: {len(webcams)}")
    print("   Kinect: Check output above")

if __name__ == "__main__":
    main()
