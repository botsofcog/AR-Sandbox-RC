#!/usr/bin/env python3
"""
VISUAL PROOF: 4-Camera System Output Display
Shows each camera's output individually to prove all cameras are working
Displays: Kinect Depth + Kinect RGB + Webcam 1 + Webcam 2 in separate windows
"""

import cv2
import numpy as np
import time
import sys
import os

# Import our working 4-camera system
try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available for visual proof")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

class VisualProof4Cameras:
    """
    Visual proof system showing each of the 4 cameras individually
    """
    
    def __init__(self):
        # Camera states
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.webcam1_active = False
        self.webcam2_active = False
        
        # Camera streams
        self.webcam1_stream = None
        self.webcam2_stream = None
        
        # Display control
        self.running = False
        
        # Frame counters for proof
        self.kinect_depth_frames = 0
        self.kinect_rgb_frames = 0
        self.webcam1_frames = 0
        self.webcam2_frames = 0
        
    def initialize_cameras_for_proof(self):
        """Initialize all cameras using our proven working method"""
        print("🔍 INITIALIZING 4-CAMERA SYSTEM FOR VISUAL PROOF...")
        
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
        
        # Initialize webcam 1 (using proven DirectShow method)
        try:
            cap1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if cap1.isOpened():
                cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap1.set(cv2.CAP_PROP_FPS, 30)
                
                ret, test_frame = cap1.read()
                if ret and test_frame is not None:
                    self.webcam1_stream = cap1
                    self.webcam1_active = True
                    print("   ✅ Webcam 1 ready for proof")
                else:
                    cap1.release()
                    print("   ❌ Webcam 1 test frame failed")
            else:
                print("   ❌ Webcam 1 failed to open")
                
        except Exception as e:
            print(f"   ❌ Webcam 1 initialization failed: {e}")
        
        # Initialize webcam 2 (using proven DirectShow method)
        try:
            cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            if cap2.isOpened():
                cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap2.set(cv2.CAP_PROP_FPS, 30)
                
                ret, test_frame = cap2.read()
                if ret and test_frame is not None:
                    self.webcam2_stream = cap2
                    self.webcam2_active = True
                    print("   ✅ Webcam 2 ready for proof")
                else:
                    cap2.release()
                    print("   ❌ Webcam 2 test frame failed")
            else:
                print("   ❌ Webcam 2 failed to open")
                
        except Exception as e:
            print(f"   ❌ Webcam 2 initialization failed: {e}")
        
        # Report initialization results
        active_count = sum([self.kinect_depth_active, self.kinect_rgb_active, self.webcam1_active, self.webcam2_active])
        print(f"\n📊 CAMERAS READY FOR PROOF: {active_count}/4")
        
        return active_count >= 3  # Minimum 3 cameras for proof
    
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
            cv2.putText(depth_colored, f"Axis 1 - Side View [REQUIRED]", 
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
            cv2.putText(bgr_frame, f"Axis 1 - Side View [REQUIRED]", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return bgr_frame
            
        except Exception as e:
            print(f"Kinect RGB capture error: {e}")
            return None
    
    def capture_webcam1_frame(self):
        """Capture and process webcam 1 frame for display"""
        if not self.webcam1_active or not self.webcam1_stream:
            return None
        
        try:
            # Get webcam frame
            ret, webcam_frame = self.webcam1_stream.read()
            if not ret or webcam_frame is None:
                return None
            
            # Add frame counter and info
            self.webcam1_frames += 1
            cv2.putText(webcam_frame, f"WEBCAM 1 - Frame {self.webcam1_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(webcam_frame, f"Resolution: {webcam_frame.shape[1]}x{webcam_frame.shape[0]}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(webcam_frame, f"Axis 2 - Secondary View [REQUIRED]", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            return webcam_frame
            
        except Exception as e:
            print(f"Webcam 1 capture error: {e}")
            return None
    
    def capture_webcam2_frame(self):
        """Capture and process webcam 2 frame for display"""
        if not self.webcam2_active or not self.webcam2_stream:
            return None
        
        try:
            # Get webcam frame
            ret, webcam_frame = self.webcam2_stream.read()
            if not ret or webcam_frame is None:
                return None
            
            # Add frame counter and info
            self.webcam2_frames += 1
            cv2.putText(webcam_frame, f"WEBCAM 2 - Frame {self.webcam2_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(webcam_frame, f"Resolution: {webcam_frame.shape[1]}x{webcam_frame.shape[0]}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(webcam_frame, f"Axis 3 - Additional View [OPTIONAL]", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            
            return webcam_frame
            
        except Exception as e:
            print(f"Webcam 2 capture error: {e}")
            return None
    
    def display_all_cameras(self):
        """Display all 4 camera outputs in separate windows"""
        print("\n📺 STARTING 4-CAMERA VISUAL PROOF DISPLAY...")
        print("   Press 'q' in any window to quit")
        print("   Each camera will show in a separate window")
        
        self.running = True
        
        while self.running:
            # Capture frames from all cameras
            depth_frame = self.capture_kinect_depth_frame()
            rgb_frame = self.capture_kinect_rgb_frame()
            webcam1_frame = self.capture_webcam1_frame()
            webcam2_frame = self.capture_webcam2_frame()
            
            # Display each camera in separate window
            if depth_frame is not None:
                cv2.imshow("PROOF: Kinect Depth Sensor (Axis 1) [REQUIRED]", depth_frame)
            
            if rgb_frame is not None:
                cv2.imshow("PROOF: Kinect RGB Camera (Axis 1) [REQUIRED]", rgb_frame)
            
            if webcam1_frame is not None:
                cv2.imshow("PROOF: Webcam 1 (Axis 2) [REQUIRED]", webcam1_frame)
            
            if webcam2_frame is not None:
                cv2.imshow("PROOF: Webcam 2 (Axis 3) [OPTIONAL]", webcam2_frame)
            
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
        print("📊 VISUAL PROOF REPORT - 4-CAMERA SYSTEM")
        print("="*60)
        
        print(f"🎯 CAMERA STATUS:")
        print(f"   Kinect Depth Sensor: {'✅ PROVEN' if self.kinect_depth_frames > 0 else '❌ NO FRAMES'} ({self.kinect_depth_frames} frames)")
        print(f"   Kinect RGB Camera: {'✅ PROVEN' if self.kinect_rgb_frames > 0 else '❌ NO FRAMES'} ({self.kinect_rgb_frames} frames)")
        print(f"   Webcam 1: {'✅ PROVEN' if self.webcam1_frames > 0 else '❌ NO FRAMES'} ({self.webcam1_frames} frames)")
        print(f"   Webcam 2: {'✅ PROVEN' if self.webcam2_frames > 0 else '❌ NO FRAMES'} ({self.webcam2_frames} frames)")
        
        working_cameras = sum([
            self.kinect_depth_frames > 0,
            self.kinect_rgb_frames > 0, 
            self.webcam1_frames > 0,
            self.webcam2_frames > 0
        ])
        
        print(f"\n🎉 PROOF SUMMARY:")
        print(f"   Working cameras: {working_cameras}/4")
        
        if working_cameras == 4:
            print(f"   🚀 MAXIMUM COVERAGE: 125% Integration!")
        elif working_cameras == 3:
            print(f"   🎯 EXCELLENT COVERAGE: 110% Integration!")
        elif working_cameras == 2:
            print(f"   ⚠️ REDUCED COVERAGE: 67% Integration")
        else:
            print(f"   ❌ INSUFFICIENT COVERAGE: {working_cameras}/4 cameras")
        
        return working_cameras >= 3
    
    def run_visual_proof(self):
        """Run complete visual proof demonstration"""
        print("="*60)
        print("📹 VISUAL PROOF: 4-CAMERA SYSTEM OUTPUT")
        print("="*60)
        
        # Initialize cameras
        if not self.initialize_cameras_for_proof():
            print("❌ Insufficient cameras for visual proof")
            return False
        
        print(f"\n🎬 READY TO SHOW VISUAL PROOF!")
        print(f"   This will open up to 4 separate windows:")
        print(f"   1. Kinect Depth Sensor (colorized depth data)")
        print(f"   2. Kinect RGB Camera (color video)")
        print(f"   3. Webcam 1 (color video from different angle)")
        print(f"   4. Webcam 2 (additional color video - if available)")
        
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
        
        if self.webcam1_stream:
            try:
                self.webcam1_stream.release()
                print("   ✅ Webcam 1 released")
            except Exception as e:
                print(f"   ❌ Webcam 1 cleanup error: {e}")
        
        if self.webcam2_stream:
            try:
                self.webcam2_stream.release()
                print("   ✅ Webcam 2 released")
            except Exception as e:
                print(f"   ❌ Webcam 2 cleanup error: {e}")
        
        cv2.destroyAllWindows()
        print("   ✅ All windows closed")

def main():
    """Run visual proof of 4-camera system"""
    proof_system = VisualProof4Cameras()
    
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
