#!/usr/bin/env python3
"""
Simple Camera Viewer
Direct, simple display of all camera feeds without complications
"""

import cv2
import numpy as np
import time
import sys

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

def show_kinect_cameras():
    """Show Kinect cameras in simple windows"""
    print("📹 SHOWING KINECT CAMERAS...")
    print("Press ESC to close windows")
    
    if not KINECT_AVAILABLE:
        print("❌ Kinect not available")
        return
    
    try:
        while True:
            # Get Kinect frames
            try:
                depth_frame = freenect.sync_get_depth()[0]
                rgb_frame = freenect.sync_get_video()[0]
            except Exception as e:
                print(f"Frame capture error: {e}")
                break
            
            # Show depth if available
            if depth_frame is not None:
                # Convert depth to visible format
                depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
                depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)
                
                # Add simple text
                cv2.putText(depth_colored, "KINECT DEPTH", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                cv2.imshow("Kinect Depth", depth_colored)
            
            # Show RGB if available
            if rgb_frame is not None:
                # Convert RGB to BGR for OpenCV
                rgb_bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
                
                # Add simple text
                cv2.putText(rgb_bgr, "KINECT RGB", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("Kinect RGB", rgb_bgr)
            
            # Check for ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("ESC pressed - closing windows")
                break
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Display error: {e}")
    finally:
        cv2.destroyAllWindows()

def show_webcams():
    """Show webcam feeds in simple windows"""
    print("📹 SHOWING WEBCAMS...")
    print("Press ESC to close windows")
    
    webcam1 = None
    webcam2 = None
    
    try:
        # Try to open webcams
        webcam1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        webcam2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        
        while True:
            # Show webcam 1
            if webcam1 and webcam1.isOpened():
                ret1, frame1 = webcam1.read()
                if ret1:
                    cv2.putText(frame1, "WEBCAM 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow("Webcam 1", frame1)
            
            # Show webcam 2
            if webcam2 and webcam2.isOpened():
                ret2, frame2 = webcam2.read()
                if ret2:
                    cv2.putText(frame2, "WEBCAM 2", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    cv2.imshow("Webcam 2", frame2)
            
            # Check for ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("ESC pressed - closing windows")
                break
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Webcam display error: {e}")
    finally:
        if webcam1:
            webcam1.release()
        if webcam2:
            webcam2.release()
        cv2.destroyAllWindows()

def main():
    """Simple camera viewer menu"""
    print("="*50)
    print("📹 SIMPLE CAMERA VIEWER")
    print("="*50)
    
    while True:
        print("\nChoose what to view:")
        print("1. Kinect cameras (depth + RGB)")
        print("2. Webcams (1 + 2)")
        print("3. All cameras")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            show_kinect_cameras()
        elif choice == "2":
            show_webcams()
        elif choice == "3":
            print("Showing Kinect cameras first...")
            show_kinect_cameras()
            print("Now showing webcams...")
            show_webcams()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again")

if __name__ == "__main__":
    main()
