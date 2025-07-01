#!/usr/bin/env python3
"""
VISUAL PROOF: 3-Camera Output Display
Shows each camera's output individually to prove all 3 cameras are working
Displays: Kinect Depth + Kinect RGB + Webcam in separate windows
"""

import cv2
import numpy as np
import time
import sys
import os
from threading import Thread, Event

# Import our working puzzle piece system
try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available for visual proof")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

class VisualProof3Cameras:
    """
    Visual proof system showing each camera output individually
    """
    
    def __init__(self):
        # Camera states
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.webcam_active = False
        
        # Camera streams
        self.webcam_stream = None
        
        # Display control
        self.running = False
        self.display_thread = None
        
        # Frame counters for proof
        self.kinect_depth_frames = 0
        self.kinect_rgb_frames = 0
        self.webcam_frames = 0
        
    def initialize_cameras_for_proof(self):
        """Initialize all cameras using our proven working method"""
        print("🔍 INITIALIZING CAMERAS FOR VISUAL PROOF...")
        
        # Initialize Kinect (proven working)
        if KINECT_AVAILABLE:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                if depth_frame is not None:
                    self.kinect_depth_active = True
                    print("   ✅ Kinect depth sensor ready for proof")
                
                rgb_frame = freenect.sync_get_video()[0]
                if rgb_frame is not None:
                    self.kinect_rgb_active = True
                    print("   ✅ Kinect RGB camera ready for proof")
                    
            except Exception as e:
                print(f"   ❌ Kinect initialization failed: {e}")
        
        # Initialize webcam (using proven DirectShow method)
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                ret, test_frame = cap.read()
                if ret and test_frame is not None:
                    self.webcam_stream = cap
                    self.webcam_active = True
                    print("   ✅ Webcam ready for proof")
                else:
                    cap.release()
                    print("   ❌ Webcam test frame failed")
            else:
                print("   ❌ Webcam failed to open")
                
        except Exception as e:
            print(f"   ❌ Webcam initialization failed: {e}")
        
        # Report initialization results
        active_count = sum([self.kinect_depth_active, self.kinect_rgb_active, self.webcam_active])
        print(f"\n📊 CAMERAS READY FOR PROOF: {active_count}/3")
        
        return active_count == 3
    
    def capture_kinect_depth_frame(self):
        """Capture and process Kinect depth frame for display"""
        if not self.kinect_depth_active or not KINECT_AVAILABLE:
            return None
        
        try:
            # Get raw depth frame
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is None:
                return None
            
            # Convert depth to displayable format
            # Normalize depth values to 0-255 for visualization
            depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
            depth_display = depth_normalized.astype(np.uint8)
            
            # Apply colormap for better visualization
            depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
            
            # Add frame counter and info
            self.kinect_depth_frames += 1
            cv2.putText(depth_colored, f"KINECT DEPTH - Frame {self.kinect_depth_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(depth_colored, f"Resolution: {depth_frame.shape[1]}x{depth_frame.shape[0]}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(depth_colored, f"Axis 1 - Side View", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return depth_colored
            
        except Exception as e:
            print(f"Kinect depth capture error: {e}")
            return None
    
    def capture_kinect_rgb_frame(self):
        """Capture and process Kinect RGB frame for display"""
        if not self.kinect_rgb_active or not KINECT_AVAILABLE:
            return None
        
        try:
            # Get RGB frame
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is None:
                return None
            
            # Convert RGB to BGR for OpenCV display
            bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            # Add frame counter and info
            self.kinect_rgb_frames += 1
            cv2.putText(bgr_frame, f"KINECT RGB - Frame {self.kinect_rgb_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(bgr_frame, f"Resolution: {rgb_frame.shape[1]}x{rgb_frame.shape[0]}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(bgr_frame, f"Axis 1 - Side View", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return bgr_frame
            
        except Exception as e:
            print(f"Kinect RGB capture error: {e}")
            return None
    
    def capture_webcam_frame(self):
        """Capture and process webcam frame for display"""
        if not self.webcam_active or not self.webcam_stream:
            return None
        
        try:
            # Get webcam frame
            ret, webcam_frame = self.webcam_stream.read()
            if not ret or webcam_frame is None:
                return None
            
            # Add frame counter and info
            self.webcam_frames += 1
            cv2.putText(webcam_frame, f"WEBCAM - Frame {self.webcam_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(webcam_frame, f"Resolution: {webcam_frame.shape[1]}x{webcam_frame.shape[0]}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(webcam_frame, f"Axis 2 - Different View", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            return webcam_frame
            
        except Exception as e:
            print(f"Webcam capture error: {e}")
            return None
    
    def display_all_cameras(self):
        """Display all 3 camera outputs in separate windows"""
        print("\n📺 STARTING VISUAL PROOF DISPLAY...")
        print("   Press 'q' in any window to quit")
        print("   Each camera will show in a separate window")
        
        self.running = True
        
        while self.running:
            # Capture frames from all cameras
            depth_frame = self.capture_kinect_depth_frame()
            rgb_frame = self.capture_kinect_rgb_frame()
            webcam_frame = self.capture_webcam_frame()
            
            # Display each camera in separate window
            if depth_frame is not None:
                cv2.imshow("PROOF: Kinect Depth Sensor (Axis 1)", depth_frame)
            
            if rgb_frame is not None:
                cv2.imshow("PROOF: Kinect RGB Camera (Axis 1)", rgb_frame)
            
            if webcam_frame is not None:
                cv2.imshow("PROOF: Webcam (Axis 2)", webcam_frame)
            
            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n🛑 User requested quit")
                break
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.033)  # ~30 FPS
        
        # Close all windows
        cv2.destroyAllWindows()
        self.running = False
    
    def generate_proof_report(self):
        """Generate final proof report"""
        print("\n" + "="*60)
        print("📊 VISUAL PROOF REPORT - 3-CAMERA SYSTEM")
        print("="*60)
        
        print(f"🎯 CAMERA STATUS:")
        print(f"   Kinect Depth Sensor: {'✅ PROVEN' if self.kinect_depth_frames > 0 else '❌ NO FRAMES'}")
        print(f"   Kinect RGB Camera: {'✅ PROVEN' if self.kinect_rgb_frames > 0 else '❌ NO FRAMES'}")
        print(f"   Webcam: {'✅ PROVEN' if self.webcam_frames > 0 else '❌ NO FRAMES'}")
        
        print(f"\n📈 FRAME COUNTS (Proof of Activity):")
        print(f"   Kinect Depth: {self.kinect_depth_frames} frames captured")
        print(f"   Kinect RGB: {self.kinect_rgb_frames} frames captured")
        print(f"   Webcam: {self.webcam_frames} frames captured")
        
        total_frames = self.kinect_depth_frames + self.kinect_rgb_frames + self.webcam_frames
        working_cameras = sum([
            self.kinect_depth_frames > 0,
            self.kinect_rgb_frames > 0, 
            self.webcam_frames > 0
        ])
        
        print(f"\n🎉 PROOF SUMMARY:")
        print(f"   Total frames captured: {total_frames}")
        print(f"   Working cameras: {working_cameras}/3")
        print(f"   Integration level: {(working_cameras/3)*100:.0f}%")
        
        if working_cameras == 3:
            print(f"   🚀 VISUAL PROOF COMPLETE: ALL 3 CAMERAS WORKING!")
        else:
            print(f"   ⚠️ PARTIAL PROOF: {working_cameras}/3 cameras proven")
        
        return working_cameras == 3
    
    def run_visual_proof(self):
        """Run complete visual proof demonstration"""
        print("="*60)
        print("📹 VISUAL PROOF: 3-CAMERA SYSTEM OUTPUT")
        print("="*60)
        
        # Initialize cameras
        if not self.initialize_cameras_for_proof():
            print("❌ Camera initialization failed - cannot provide visual proof")
            return False
        
        print(f"\n🎬 READY TO SHOW VISUAL PROOF!")
        print(f"   This will open 3 separate windows showing each camera")
        print(f"   1. Kinect Depth Sensor (colorized depth data)")
        print(f"   2. Kinect RGB Camera (color video)")
        print(f"   3. Webcam (color video from different angle)")
        
        input("\nPress ENTER to start visual proof display...")
        
        try:
            # Display all cameras
            self.display_all_cameras()
            
            # Generate proof report
            proof_complete = self.generate_proof_report()
            
            return proof_complete
            
        except KeyboardInterrupt:
            print("\n🛑 Visual proof interrupted by user")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up camera resources"""
        print("\n🧹 CLEANING UP VISUAL PROOF...")
        
        self.running = False
        
        if self.webcam_stream:
            try:
                self.webcam_stream.release()
                print("   ✅ Webcam released")
            except Exception as e:
                print(f"   ❌ Webcam cleanup error: {e}")
        
        cv2.destroyAllWindows()
        print("   ✅ All windows closed")

def main():
    """Run visual proof of 3-camera system"""
    proof_system = VisualProof3Cameras()
    
    try:
        success = proof_system.run_visual_proof()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Visual proof failed: {e}")
        return 1
    finally:
        proof_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
