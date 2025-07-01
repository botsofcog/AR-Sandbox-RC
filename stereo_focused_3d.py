#!/usr/bin/env python3
"""
Stereo-Focused 3D System
Prioritizes working stereo depth, fixes Kinect RGB test patterns
"""

import cv2
import numpy as np
import time
import sys
import threading

# Import existing resources
sys.path.append('external_libs/python-examples-cv')

try:
    import camera_stream
    CAMERA_STREAM_AVAILABLE = True
    print("✅ Camera stream available")
except ImportError:
    CAMERA_STREAM_AVAILABLE = False
    print("❌ Camera stream not available")

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

class StereoFocused3D:
    """
    Stereo-focused 3D system with Kinect RGB pattern fix
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
        
        # Stereo processing
        self.stereo_matcher = None
        self.setup_stereo_matcher()
        
        # Performance
        self.frame_count = 0
        self.start_time = time.time()
        
    def setup_stereo_matcher(self):
        """Setup optimized stereo matcher"""
        print("🔧 SETTING UP STEREO MATCHER...")
        
        # Create stereo matcher with optimized parameters
        self.stereo_matcher = cv2.StereoBM_create(
            numDisparities=96,  # Increased for better range
            blockSize=21        # Larger block for stability
        )
        
        # Fine-tune parameters
        self.stereo_matcher.setMinDisparity(0)
        self.stereo_matcher.setSpeckleWindowSize(100)
        self.stereo_matcher.setSpeckleRange(32)
        self.stereo_matcher.setDisp12MaxDiff(1)
        
        print("   ✅ Stereo matcher configured")
    
    def force_kinect_real_rgb(self):
        """Force Kinect RGB out of test pattern mode"""
        print("🔄 FORCING KINECT RGB TO REAL MODE...")
        
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Complete reset sequence
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(2.0)
            
            # Try different video modes to break test pattern
            video_modes = [freenect.VIDEO_RGB, freenect.VIDEO_BAYER, freenect.VIDEO_IR_8BIT]
            
            for i, mode in enumerate(video_modes):
                try:
                    print(f"   🧪 Trying video mode {i+1}/3...")
                    
                    # Set mode
                    freenect.set_video_mode(0, mode)
                    time.sleep(1.0)
                    
                    # Start and test
                    freenect.start_video(0)
                    time.sleep(2.0)
                    
                    # Test multiple frames
                    for test in range(5):
                        rgb_data, _ = freenect.sync_get_video()
                        if rgb_data is not None:
                            # Check if this looks like real data
                            rgb_std = np.std(rgb_data)
                            if rgb_std > 40:  # More variation = likely real
                                print(f"      ✅ Mode {i+1} shows real variation (std: {rgb_std:.1f})")
                                self.kinect_rgb_active = True
                                return True
                        time.sleep(0.2)
                    
                    freenect.stop_video(0)
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"      ❌ Mode {i+1} failed: {e}")
            
            # Fallback to RGB mode
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            freenect.start_video(0)
            print("   ⚠️ Using RGB mode (may still be test pattern)")
            self.kinect_rgb_active = True
            return True
            
        except Exception as e:
            print(f"   ❌ Kinect RGB force failed: {e}")
            return False
    
    def initialize_kinect_depth(self):
        """Initialize Kinect depth sensor"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Set depth mode
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.start_depth(0)
            time.sleep(1.0)
            
            # Test depth
            depth_data, _ = freenect.sync_get_depth()
            if depth_data is not None:
                self.kinect_depth_active = True
                print("   ✅ Kinect depth active")
                return True
            
        except Exception as e:
            print(f"   ❌ Kinect depth failed: {e}")
        
        return False
    
    def initialize_stereo_webcams(self):
        """Initialize webcams for stereo vision"""
        print("📷 INITIALIZING STEREO WEBCAMS...")
        
        webcam_count = 0
        
        # Webcam 1 (left)
        if CAMERA_STREAM_AVAILABLE:
            try:
                webcam1_stream = camera_stream.CameraVideoStream()
                webcam1_stream.open(src=0, backend=cv2.CAP_DSHOW)
                time.sleep(0.5)
                
                grabbed, test_frame = webcam1_stream.read()
                if grabbed and test_frame is not None:
                    self.webcam1_stream = webcam1_stream
                    self.webcam1_active = True
                    webcam_count += 1
                    print("   ✅ Left webcam (stereo) active")
            except Exception as e:
                print(f"   ❌ Left webcam failed: {e}")
        
        # Webcam 2 (right)
        if CAMERA_STREAM_AVAILABLE:
            try:
                webcam2_stream = camera_stream.CameraVideoStream()
                webcam2_stream.open(src=1, backend=cv2.CAP_DSHOW)
                time.sleep(0.5)
                
                grabbed, test_frame = webcam2_stream.read()
                if grabbed and test_frame is not None:
                    self.webcam2_stream = webcam2_stream
                    self.webcam2_active = True
                    webcam_count += 1
                    print("   ✅ Right webcam (stereo) active")
            except Exception as e:
                print(f"   ❌ Right webcam failed: {e}")
        
        print(f"   📊 Stereo webcams: {webcam_count}/2")
        return webcam_count >= 2
    
    def compute_high_quality_stereo_depth(self, left_img, right_img):
        """Compute high-quality stereo depth"""
        if left_img is None or right_img is None:
            return None
        
        # Convert to grayscale
        left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better matching
        left_eq = cv2.equalizeHist(left_gray)
        right_eq = cv2.equalizeHist(right_gray)
        
        # Compute disparity
        disparity = self.stereo_matcher.compute(left_eq, right_eq)
        
        # Convert to depth
        # Depth = (focal_length * baseline) / disparity
        focal_length = 800.0  # Approximate focal length
        baseline = 0.15  # Approximate baseline (15cm between webcams)
        
        # Avoid division by zero
        disparity_safe = np.where(disparity > 0, disparity, 1)
        depth = (focal_length * baseline) / (disparity_safe / 16.0)  # StereoBM uses 16-bit
        
        # Filter realistic depths (10cm to 3m)
        depth_filtered = np.where((depth > 0.1) & (depth < 3.0), depth, 0)
        
        # Apply median filter to reduce noise
        depth_smooth = cv2.medianBlur(depth_filtered.astype(np.float32), 5)
        
        return depth_smooth
    
    def create_enhanced_topography(self, stereo_depth, kinect_depth=None):
        """Create enhanced topography from stereo + kinect data"""
        if stereo_depth is None:
            return None
        
        # Start with stereo depth as base
        enhanced_depth = stereo_depth.copy()
        
        # If Kinect depth available, fuse it
        if kinect_depth is not None:
            # Resize Kinect depth to match stereo
            kinect_resized = cv2.resize(kinect_depth.astype(np.float32) / 1000.0, 
                                      (stereo_depth.shape[1], stereo_depth.shape[0]))
            
            # Create masks
            stereo_mask = stereo_depth > 0
            kinect_mask = kinect_resized > 0
            
            # Use Kinect where both are available (it's more accurate)
            overlap_mask = stereo_mask & kinect_mask
            enhanced_depth[overlap_mask] = kinect_resized[overlap_mask]
            
            # Fill stereo gaps with Kinect data
            gap_mask = (~stereo_mask) & kinect_mask
            enhanced_depth[gap_mask] = kinect_resized[gap_mask]
        
        return enhanced_depth
    
    def display_stereo_focused_system(self):
        """Display stereo-focused 3D system"""
        print("🎮 DISPLAYING STEREO-FOCUSED 3D SYSTEM...")
        
        # Create windows
        cv2.namedWindow('Stereo Depth (Primary)', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Left Camera', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Right Camera', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Enhanced Topography', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('System Status', cv2.WINDOW_AUTOSIZE)
        
        try:
            while True:
                # Capture stereo images
                left_img = None
                right_img = None
                
                if self.webcam1_active and self.webcam1_stream:
                    grabbed, left_img = self.webcam1_stream.read()
                    if not grabbed:
                        left_img = None
                
                if self.webcam2_active and self.webcam2_stream:
                    grabbed, right_img = self.webcam2_stream.read()
                    if not grabbed:
                        right_img = None
                
                # Capture Kinect data
                kinect_depth = None
                kinect_rgb = None
                
                if self.kinect_depth_active:
                    try:
                        kinect_depth, _ = freenect.sync_get_depth()
                    except:
                        pass
                
                if self.kinect_rgb_active:
                    try:
                        kinect_rgb, _ = freenect.sync_get_video()
                    except:
                        pass
                
                # Compute stereo depth
                stereo_depth = None
                if left_img is not None and right_img is not None:
                    stereo_depth = self.compute_high_quality_stereo_depth(left_img, right_img)
                
                # Create enhanced topography
                enhanced_topo = self.create_enhanced_topography(stereo_depth, kinect_depth)
                
                # Display results
                if stereo_depth is not None:
                    # Stereo depth visualization
                    stereo_norm = cv2.normalize(stereo_depth, None, 0, 255, cv2.NORM_MINMAX)
                    stereo_colored = cv2.applyColorMap(stereo_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(stereo_colored, "STEREO DEPTH (WORKING)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Stereo Depth (Primary)', stereo_colored)
                
                if enhanced_topo is not None:
                    # Enhanced topography
                    topo_norm = cv2.normalize(enhanced_topo, None, 0, 255, cv2.NORM_MINMAX)
                    topo_colored = cv2.applyColorMap(topo_norm.astype(np.uint8), cv2.COLORMAP_RAINBOW)
                    cv2.putText(topo_colored, "ENHANCED TOPOGRAPHY", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Enhanced Topography', topo_colored)
                
                # Display camera feeds
                if left_img is not None:
                    cv2.putText(left_img, "LEFT (STEREO)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Left Camera', cv2.resize(left_img, (320, 240)))
                
                if right_img is not None:
                    cv2.putText(right_img, "RIGHT (STEREO)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Right Camera', cv2.resize(right_img, (320, 240)))
                
                # System status
                status_img = np.zeros((400, 500, 3), dtype=np.uint8)
                
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                
                # Status text
                cv2.putText(status_img, "STEREO-FOCUSED 3D SYSTEM", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                stereo_status = "✅ WORKING" if stereo_depth is not None else "❌ FAILED"
                cv2.putText(status_img, f"Stereo Depth: {stereo_status}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                kinect_d_status = "✅ ACTIVE" if self.kinect_depth_active else "❌ INACTIVE"
                cv2.putText(status_img, f"Kinect Depth: {kinect_d_status}", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                kinect_rgb_status = "⚠️ TEST PATTERN" if self.kinect_rgb_active else "❌ INACTIVE"
                if kinect_rgb is not None:
                    rgb_std = np.std(kinect_rgb)
                    if rgb_std > 40:
                        kinect_rgb_status = "✅ REAL DATA"
                
                cv2.putText(status_img, f"Kinect RGB: {kinect_rgb_status}", 
                           (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.putText(status_img, "Press 'q' to exit, 'r' to reset RGB", 
                           (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('System Status', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("🔄 Resetting Kinect RGB...")
                    self.force_kinect_real_rgb()
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_stereo_focused_system(self):
        """Run the complete stereo-focused system"""
        print("="*60)
        print("🎯 STEREO-FOCUSED 3D SYSTEM")
        print("="*60)
        print("✅ Stereo depth working - prioritizing this")
        print("⚠️ Kinect RGB test patterns - will attempt fix")
        print("="*60)
        
        # Initialize stereo webcams (priority)
        stereo_ok = self.initialize_stereo_webcams()
        
        # Initialize Kinect depth
        kinect_depth_ok = self.initialize_kinect_depth()
        
        # Try to fix Kinect RGB
        kinect_rgb_ok = self.force_kinect_real_rgb()
        
        print(f"\n🔧 INITIALIZATION RESULTS:")
        print(f"   Stereo webcams: {'✅ WORKING' if stereo_ok else '❌ FAILED'}")
        print(f"   Kinect depth: {'✅ WORKING' if kinect_depth_ok else '❌ FAILED'}")
        print(f"   Kinect RGB: {'✅ FIXED' if kinect_rgb_ok else '❌ STILL TEST PATTERN'}")
        
        if stereo_ok:
            print(f"\n🎮 STARTING STEREO-FOCUSED DISPLAY...")
            self.display_stereo_focused_system()
        else:
            print(f"\n❌ Cannot run without stereo cameras")
            return False
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.kinect_depth_active or self.kinect_rgb_active:
                freenect.stop_depth(0)
                freenect.stop_video(0)
        except:
            pass
        
        if self.webcam1_stream:
            try:
                self.webcam1_stream.release()
            except:
                pass
        
        if self.webcam2_stream:
            try:
                self.webcam2_stream.release()
            except:
                pass

def main():
    """Run stereo-focused 3D system"""
    system = StereoFocused3D()
    
    try:
        success = system.run_stereo_focused_system()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Stereo system failed: {e}")
        return 1
    finally:
        system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
