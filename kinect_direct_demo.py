#!/usr/bin/env python3
"""
🎯 AR Sandbox RC - Direct Kinect Demo
Uses the working triple camera fusion system to display live feeds
"""

import cv2
import numpy as np
import time
import threading
from datetime import datetime

class DirectKinectDemo:
    def __init__(self):
        self.running = False
        self.kinect_depth = None
        self.kinect_rgb = None
        self.logitech_cam = None
        
        print("🎯 AR Sandbox RC - Direct Kinect Demo")
        print("=" * 50)
        
        # Initialize the triple camera system
        self.init_triple_camera_system()
        
    def init_triple_camera_system(self):
        """Initialize the triple camera system that we know works"""
        print("🔄 Initializing Triple Camera Fusion System...")
        
        try:
            # Try to load Kinect library
            import ctypes
            kinect_dll = ctypes.windll.LoadLibrary("C:\\Windows\\System32\\Kinect10.dll")
            print("✅ Kinect10.dll loaded successfully")
            self.kinect_available = True
        except Exception as e:
            print(f"⚠️ Kinect10.dll not available: {e}")
            self.kinect_available = False
            
        # Initialize cameras using OpenCV (the method that worked)
        self.init_cameras_opencv()
        
    def init_cameras_opencv(self):
        """Initialize cameras using OpenCV DirectShow"""
        print("📹 Initializing cameras with OpenCV DirectShow...")
        
        camera_count = 0
        
        # Test all camera indices
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"  📷 Camera {i}: {width}x{height}")
                        
                        # Assign cameras based on resolution
                        if width == 640 and height == 480:
                            # Likely Kinect RGB
                            self.kinect_rgb = cap
                            print(f"  ✅ Assigned as Kinect RGB: Camera {i}")
                            camera_count += 1
                        elif width >= 1280:
                            # Likely Logitech high-res
                            self.logitech_cam = cap
                            print(f"  ✅ Assigned as Logitech webcam: Camera {i}")
                            camera_count += 1
                        else:
                            cap.release()
                    else:
                        cap.release()
                else:
                    cap.release()
            except Exception as e:
                print(f"  ❌ Camera {i} error: {e}")
                
        print(f"📊 Total cameras initialized: {camera_count}")
        
        # For Kinect depth, we'll simulate from RGB
        if self.kinect_rgb:
            print("✅ Kinect depth will be simulated from RGB")
            
    def create_depth_from_rgb(self, rgb_frame):
        """Create depth-like visualization from RGB frame"""
        # Convert to grayscale
        gray = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur for depth effect
        depth_sim = cv2.GaussianBlur(gray, (15, 15), 0)
        
        # Invert for depth-like appearance (closer = brighter)
        depth_sim = 255 - depth_sim
        
        # Apply colormap for depth visualization
        depth_colored = cv2.applyColorMap(depth_sim, cv2.COLORMAP_JET)
        
        # Add edge detection for better depth perception
        edges = cv2.Canny(gray, 50, 150)
        depth_colored[edges > 0] = [0, 255, 0]  # Green edges
        
        return depth_colored
        
    def run_demo(self):
        """Run the live camera demo"""
        print("\n🚀 Starting live camera demo...")
        print("Press 'q' to quit, 's' to save frames")
        
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                # Create display windows
                frames = {}
                
                # Get Kinect RGB frame
                if self.kinect_rgb:
                    ret, kinect_frame = self.kinect_rgb.read()
                    if ret:
                        frames['Kinect RGB'] = kinect_frame
                        
                        # Create depth from RGB
                        depth_frame = self.create_depth_from_rgb(kinect_frame)
                        frames['Kinect Depth (Simulated)'] = depth_frame
                        
                # Get Logitech webcam frame
                if self.logitech_cam:
                    ret, logitech_frame = self.logitech_cam.read()
                    if ret:
                        # Resize for display
                        logitech_resized = cv2.resize(logitech_frame, (640, 480))
                        frames['Logitech Webcam'] = logitech_resized
                        
                # Create fusion visualization
                if len(frames) >= 2:
                    fusion_frame = self.create_fusion_display(frames)
                    frames['Triple Camera Fusion'] = fusion_frame
                    
                # Display all frames
                for window_name, frame in frames.items():
                    cv2.imshow(window_name, frame)
                    
                # Calculate and display FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"📊 FPS: {fps:.1f} | Frames: {frame_count} | Active cameras: {len(frames)}")
                    
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Quit requested")
                    break
                elif key == ord('s'):
                    self.save_frames(frames)
                    
            except KeyboardInterrupt:
                print("\n🛑 Demo stopped by user")
                break
            except Exception as e:
                print(f"❌ Demo error: {e}")
                time.sleep(0.1)
                
        self.cleanup()
        
    def create_fusion_display(self, frames):
        """Create a fusion display combining multiple camera feeds"""
        # Create a 2x2 grid for fusion display
        fusion_width, fusion_height = 640, 480
        fusion_frame = np.zeros((fusion_height, fusion_width, 3), dtype=np.uint8)
        
        # Add grid lines
        cv2.line(fusion_frame, (320, 0), (320, 480), (0, 255, 0), 2)
        cv2.line(fusion_frame, (0, 240), (640, 240), (0, 255, 0), 2)
        
        # Add camera feeds to quadrants
        frame_list = list(frames.values())
        positions = [(0, 0), (320, 0), (0, 240), (320, 240)]
        
        for i, (frame, (x, y)) in enumerate(zip(frame_list[:4], positions)):
            # Resize frame to fit quadrant
            resized = cv2.resize(frame, (320, 240))
            fusion_frame[y:y+240, x:x+320] = resized
            
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(fusion_frame, f"Fusion: {timestamp}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                   
        return fusion_frame
        
    def save_frames(self, frames):
        """Save current frames to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"💾 Saving frames with timestamp: {timestamp}")
        
        for name, frame in frames.items():
            filename = f"frame_{name.replace(' ', '_')}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"  ✅ Saved: {filename}")
            
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        if self.kinect_rgb:
            self.kinect_rgb.release()
            
        if self.logitech_cam:
            self.logitech_cam.release()
            
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

def main():
    """Main function"""
    demo = DirectKinectDemo()
    
    if not demo.kinect_rgb and not demo.logitech_cam:
        print("❌ No cameras available!")
        print("💡 Make sure cameras are connected and not in use by other applications")
        return
        
    print(f"\n📊 Camera Status:")
    print(f"  Kinect RGB: {'✅ Available' if demo.kinect_rgb else '❌ Not found'}")
    print(f"  Logitech Webcam: {'✅ Available' if demo.logitech_cam else '❌ Not found'}")
    print(f"  Kinect Depth: {'✅ Simulated' if demo.kinect_rgb else '❌ Not available'}")
    
    print(f"\n🎮 Controls:")
    print(f"  'q' - Quit demo")
    print(f"  's' - Save current frames")
    print(f"\n🚀 Starting in 3 seconds...")
    
    time.sleep(3)
    demo.run_demo()

if __name__ == "__main__":
    main()
