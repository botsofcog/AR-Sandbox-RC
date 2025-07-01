#!/usr/bin/env python3
"""
Robust Depth Enhancement System
Improves weak stereo depth and combines multiple depth sources
"""

import cv2
import numpy as np
import time
import sys

# Import existing resources
sys.path.append('external_libs/python-examples-cv')

try:
    import camera_stream
    CAMERA_STREAM_AVAILABLE = True
except ImportError:
    CAMERA_STREAM_AVAILABLE = False

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

class RobustDepthEnhancement:
    """
    Robust depth enhancement using multiple techniques
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
        
        # Multiple stereo matchers for robust depth
        self.stereo_bm = None
        self.stereo_sgbm = None
        self.wls_filter = None
        
        self.setup_enhanced_stereo()
        
        # Depth enhancement parameters
        self.depth_history = []
        self.max_history = 5
        
    def setup_enhanced_stereo(self):
        """Setup enhanced stereo matching with multiple algorithms"""
        print("🔧 SETTING UP ENHANCED STEREO MATCHING...")
        
        # Block Matching (fast)
        self.stereo_bm = cv2.StereoBM_create(
            numDisparities=128,  # Increased range
            blockSize=15
        )
        self.stereo_bm.setMinDisparity(0)
        self.stereo_bm.setSpeckleWindowSize(200)
        self.stereo_bm.setSpeckleRange(32)
        self.stereo_bm.setDisp12MaxDiff(1)
        
        # Semi-Global Block Matching (higher quality)
        self.stereo_sgbm = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=128,
            blockSize=11,
            P1=8 * 3 * 11**2,
            P2=32 * 3 * 11**2,
            disp12MaxDiff=1,
            uniquenessRatio=10,
            speckleWindowSize=200,
            speckleRange=32
        )
        
        # WLS Filter for post-processing
        try:
            self.wls_filter = cv2.ximgproc.createDisparityWLSFilter(self.stereo_bm)
            self.wls_filter.setLambda(8000)
            self.wls_filter.setSigmaColor(1.2)
            print("   ✅ WLS filter available")
        except:
            print("   ⚠️ WLS filter not available")
        
        print("   ✅ Enhanced stereo matchers configured")
    
    def initialize_all_cameras(self):
        """Initialize all cameras"""
        print("🎮 INITIALIZING ALL CAMERAS...")
        
        # Initialize Kinect
        kinect_ok = self.initialize_kinect()
        
        # Initialize webcams
        webcam_ok = self.initialize_webcams()
        
        total_active = sum([self.kinect_depth_active, self.kinect_rgb_active, 
                           self.webcam1_active, self.webcam2_active])
        
        print(f"   📊 Total cameras: {total_active}/4")
        return total_active >= 2
    
    def initialize_kinect(self):
        """Initialize Kinect with enhanced settings"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Reset
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(1.0)
            
            # Set modes
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            
            # Start
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            # Test
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            if depth_data is not None:
                self.kinect_depth_active = True
                print("   ✅ Kinect depth active")
            
            if rgb_data is not None:
                self.kinect_rgb_active = True
                print("   ✅ Kinect RGB active")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Kinect failed: {e}")
            return False
    
    def initialize_webcams(self):
        """Initialize webcams with enhanced settings"""
        webcam_count = 0
        
        # Webcam 1
        if CAMERA_STREAM_AVAILABLE:
            try:
                webcam1_stream = camera_stream.CameraVideoStream()
                webcam1_stream.open(src=0, backend=cv2.CAP_DSHOW)
                time.sleep(0.3)
                
                grabbed, test_frame = webcam1_stream.read()
                if grabbed and test_frame is not None:
                    self.webcam1_stream = webcam1_stream
                    self.webcam1_active = True
                    webcam_count += 1
                    print("   ✅ Webcam 1 active")
            except Exception as e:
                print(f"   ❌ Webcam 1 failed: {e}")
        
        # Webcam 2
        if CAMERA_STREAM_AVAILABLE:
            try:
                webcam2_stream = camera_stream.CameraVideoStream()
                webcam2_stream.open(src=1, backend=cv2.CAP_DSHOW)
                time.sleep(0.3)
                
                grabbed, test_frame = webcam2_stream.read()
                if grabbed and test_frame is not None:
                    self.webcam2_stream = webcam2_stream
                    self.webcam2_active = True
                    webcam_count += 1
                    print("   ✅ Webcam 2 active")
            except Exception as e:
                print(f"   ❌ Webcam 2 failed: {e}")
        
        return webcam_count >= 2
    
    def preprocess_stereo_images(self, left_img, right_img):
        """Enhanced preprocessing for better stereo matching"""
        if left_img is None or right_img is None:
            return None, None
        
        # Convert to grayscale
        left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        left_enhanced = clahe.apply(left_gray)
        right_enhanced = clahe.apply(right_gray)
        
        # Apply Gaussian blur to reduce noise
        left_smooth = cv2.GaussianBlur(left_enhanced, (5, 5), 0)
        right_smooth = cv2.GaussianBlur(right_enhanced, (5, 5), 0)
        
        return left_smooth, right_smooth
    
    def compute_robust_stereo_depth(self, left_img, right_img):
        """Compute robust stereo depth using multiple algorithms"""
        if left_img is None or right_img is None:
            return None
        
        # Preprocess images
        left_proc, right_proc = self.preprocess_stereo_images(left_img, right_img)
        if left_proc is None:
            return None
        
        # Method 1: Block Matching (fast)
        try:
            disp_bm = self.stereo_bm.compute(left_proc, right_proc)
            depth_bm = self.disparity_to_depth(disp_bm)
        except:
            depth_bm = None
        
        # Method 2: SGBM (higher quality)
        try:
            disp_sgbm = self.stereo_sgbm.compute(left_proc, right_proc)
            depth_sgbm = self.disparity_to_depth(disp_sgbm)
        except:
            depth_sgbm = None
        
        # Method 3: WLS filtered (if available)
        depth_wls = None
        if self.wls_filter is not None and depth_bm is not None:
            try:
                # Create right matcher for WLS
                right_matcher = cv2.ximgproc.createRightMatcher(self.stereo_bm)
                disp_right = right_matcher.compute(right_proc, left_proc)
                
                # Apply WLS filter
                disp_filtered = self.wls_filter.filter(disp_bm, left_proc, None, disp_right)
                depth_wls = self.disparity_to_depth(disp_filtered)
            except:
                pass
        
        # Combine results (prioritize WLS > SGBM > BM)
        if depth_wls is not None:
            return self.post_process_depth(depth_wls)
        elif depth_sgbm is not None:
            return self.post_process_depth(depth_sgbm)
        elif depth_bm is not None:
            return self.post_process_depth(depth_bm)
        else:
            return None
    
    def disparity_to_depth(self, disparity):
        """Convert disparity to depth with enhanced parameters"""
        # Enhanced parameters
        focal_length = 1000.0  # Increased focal length estimate
        baseline = 0.12  # 12cm baseline estimate
        
        # Handle different disparity formats
        if disparity.dtype == np.int16:
            disparity = disparity.astype(np.float32) / 16.0
        
        # Avoid division by zero
        disparity_safe = np.where(disparity > 1.0, disparity, np.inf)
        
        # Calculate depth
        depth = (focal_length * baseline) / disparity_safe
        
        # Filter realistic depths (5cm to 5m)
        depth_filtered = np.where((depth > 0.05) & (depth < 5.0), depth, 0)
        
        return depth_filtered.astype(np.float32)
    
    def post_process_depth(self, depth):
        """Post-process depth for better quality"""
        if depth is None:
            return None
        
        # Remove small isolated regions
        depth_clean = cv2.medianBlur(depth, 5)
        
        # Fill small holes
        kernel = np.ones((3,3), np.uint8)
        depth_filled = cv2.morphologyEx(depth_clean, cv2.MORPH_CLOSE, kernel)
        
        # Apply bilateral filter to preserve edges while smoothing
        depth_smooth = cv2.bilateralFilter(depth_filled, 9, 75, 75)
        
        return depth_smooth
    
    def temporal_depth_filtering(self, current_depth):
        """Apply temporal filtering to reduce noise"""
        if current_depth is None:
            return None
        
        # Add to history
        self.depth_history.append(current_depth.copy())
        
        # Keep only recent frames
        if len(self.depth_history) > self.max_history:
            self.depth_history.pop(0)
        
        # If we have enough history, apply temporal median filter
        if len(self.depth_history) >= 3:
            depth_stack = np.stack(self.depth_history, axis=2)
            temporal_median = np.median(depth_stack, axis=2)
            return temporal_median
        else:
            return current_depth
    
    def fuse_all_depth_sources(self, stereo_depth, kinect_depth):
        """Fuse all available depth sources"""
        if stereo_depth is None and kinect_depth is None:
            return None
        
        if stereo_depth is None:
            return kinect_depth.astype(np.float32) / 1000.0  # Convert mm to m
        
        if kinect_depth is None:
            return stereo_depth
        
        # Resize to match
        h, w = stereo_depth.shape
        kinect_resized = cv2.resize(kinect_depth.astype(np.float32) / 1000.0, (w, h))
        
        # Create confidence masks
        stereo_conf = (stereo_depth > 0).astype(np.float32)
        kinect_conf = (kinect_resized > 0).astype(np.float32)
        
        # Weighted fusion (Kinect is generally more accurate)
        total_conf = stereo_conf + kinect_conf * 2.0  # Weight Kinect higher
        
        fused_depth = np.zeros_like(stereo_depth)
        valid_mask = total_conf > 0
        
        fused_depth[valid_mask] = (
            (stereo_depth[valid_mask] * stereo_conf[valid_mask] + 
             kinect_resized[valid_mask] * kinect_conf[valid_mask] * 2.0) / 
            total_conf[valid_mask]
        )
        
        return fused_depth
    
    def display_robust_depth_system(self):
        """Display robust depth enhancement system"""
        print("🎮 DISPLAYING ROBUST DEPTH ENHANCEMENT...")
        
        # Create windows
        cv2.namedWindow('Enhanced Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Stereo Left', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Stereo Right', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Depth Comparison', cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Capture all data
                left_img = None
                right_img = None
                kinect_depth = None
                kinect_rgb = None
                
                if self.webcam1_active and self.webcam1_stream:
                    grabbed, left_img = self.webcam1_stream.read()
                    if not grabbed:
                        left_img = None
                
                if self.webcam2_active and self.webcam2_stream:
                    grabbed, right_img = self.webcam2_stream.read()
                    if not grabbed:
                        right_img = None
                
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
                
                # Compute enhanced stereo depth
                stereo_depth = self.compute_robust_stereo_depth(left_img, right_img)
                
                # Apply temporal filtering
                if stereo_depth is not None:
                    stereo_depth = self.temporal_depth_filtering(stereo_depth)
                
                # Fuse all depth sources
                final_depth = self.fuse_all_depth_sources(stereo_depth, kinect_depth)
                
                # Display results
                if final_depth is not None:
                    # Enhanced depth visualization
                    depth_norm = cv2.normalize(final_depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    
                    # Add quality metrics
                    valid_pixels = np.sum(final_depth > 0)
                    total_pixels = final_depth.size
                    coverage = (valid_pixels / total_pixels) * 100
                    
                    cv2.putText(depth_colored, f"ENHANCED DEPTH - Coverage: {coverage:.1f}%", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    cv2.imshow('Enhanced Depth', depth_colored)
                
                # Display stereo cameras
                if left_img is not None:
                    cv2.putText(left_img, "LEFT STEREO", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Stereo Left', cv2.resize(left_img, (320, 240)))
                
                if right_img is not None:
                    cv2.putText(right_img, "RIGHT STEREO", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Stereo Right', cv2.resize(right_img, (320, 240)))
                
                # Depth comparison
                if stereo_depth is not None or kinect_depth is not None:
                    comparison = np.zeros((240, 640, 3), dtype=np.uint8)
                    
                    # Left side: Stereo depth
                    if stereo_depth is not None:
                        stereo_norm = cv2.normalize(stereo_depth, None, 0, 255, cv2.NORM_MINMAX)
                        stereo_colored = cv2.applyColorMap(stereo_norm.astype(np.uint8), cv2.COLORMAP_PLASMA)
                        stereo_resized = cv2.resize(stereo_colored, (320, 240))
                        comparison[:, :320] = stereo_resized
                        cv2.putText(comparison, "STEREO", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Right side: Kinect depth
                    if kinect_depth is not None:
                        kinect_norm = cv2.normalize(kinect_depth, None, 0, 255, cv2.NORM_MINMAX)
                        kinect_colored = cv2.applyColorMap(kinect_norm.astype(np.uint8), cv2.COLORMAP_VIRIDIS)
                        kinect_resized = cv2.resize(kinect_colored, (320, 240))
                        comparison[:, 320:] = kinect_resized
                        cv2.putText(comparison, "KINECT", (330, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Depth Comparison', comparison)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    # Clear depth history
                    self.depth_history.clear()
                    print("🧹 Depth history cleared")
                
                frame_count += 1
                
                # Performance info
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"📊 Enhanced Depth: {fps:.1f} FPS")
        
        finally:
            cv2.destroyAllWindows()
    
    def run_robust_depth_system(self):
        """Run the complete robust depth enhancement system"""
        print("="*60)
        print("🎯 ROBUST DEPTH ENHANCEMENT SYSTEM")
        print("="*60)
        print("🔧 Multiple stereo algorithms + temporal filtering + fusion")
        print("="*60)
        
        # Initialize cameras
        if not self.initialize_all_cameras():
            print("❌ Insufficient cameras")
            return False
        
        print("\n🎮 STARTING ROBUST DEPTH ENHANCEMENT...")
        self.display_robust_depth_system()
        
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
    """Run robust depth enhancement system"""
    system = RobustDepthEnhancement()
    
    try:
        success = system.run_robust_depth_system()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Robust depth system failed: {e}")
        return 1
    finally:
        system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
