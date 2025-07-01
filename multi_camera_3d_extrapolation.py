#!/usr/bin/env python3
"""
Multi-Camera 3D Extrapolation System
Combines Kinect depth + RGB + 2 webcams for precise topography reconstruction
"""

import cv2
import numpy as np
import time
import sys
import threading
from scipy.spatial.distance import cdist
from scipy.interpolate import griddata
# import open3d as o3d  # Optional - using built-in methods instead

# Import existing resources
sys.path.append('external_libs/python-examples-cv')
sys.path.append('external_libs/camera-fusion')

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

class MultiCamera3DExtrapolation:
    """
    Multi-camera 3D extrapolation and topography system
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
        
        # 3D reconstruction data
        self.point_cloud = None
        self.mesh = None
        self.topography_grid = None
        
        # Camera calibration matrices (will be computed)
        self.kinect_intrinsic = None
        self.webcam1_intrinsic = None
        self.webcam2_intrinsic = None
        
        # Stereo calibration
        self.stereo_params = {}
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        
    def initialize_all_cameras(self):
        """Initialize all cameras for 3D extrapolation"""
        print("🎮 INITIALIZING ALL CAMERAS FOR 3D EXTRAPOLATION...")
        
        # Initialize Kinect
        kinect_success = self.initialize_kinect()
        
        # Initialize webcams
        webcam_success = self.initialize_webcams()
        
        # Setup camera calibration
        self.setup_camera_calibration()
        
        total_cameras = sum([self.kinect_depth_active, self.kinect_rgb_active, 
                           self.webcam1_active, self.webcam2_active])
        
        print(f"   📊 Total cameras active: {total_cameras}/4")
        return total_cameras >= 2  # Need at least 2 cameras for 3D
    
    def initialize_kinect(self):
        """Initialize Kinect using proven method"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Stop existing streams
            try:
                freenect.stop_depth(0)
                freenect.stop_video(0)
                time.sleep(1.0)
            except:
                pass
            
            # Set modes
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            
            # Start streams
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            # Test capture
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            if depth_data is not None:
                self.kinect_depth_active = True
                print("   ✅ Kinect depth active")
            
            if rgb_data is not None:
                self.kinect_rgb_active = True
                print("   ✅ Kinect RGB active")
            
            return self.kinect_depth_active or self.kinect_rgb_active
            
        except Exception as e:
            print(f"   ❌ Kinect init failed: {e}")
            return False
    
    def initialize_webcams(self):
        """Initialize webcams for stereo vision"""
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
                    print("   ✅ Webcam 1 active for stereo")
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
                    print("   ✅ Webcam 2 active for stereo")
            except Exception as e:
                print(f"   ❌ Webcam 2 failed: {e}")
        
        return webcam_count > 0
    
    def setup_camera_calibration(self):
        """Setup camera calibration matrices"""
        print("🔧 SETTING UP CAMERA CALIBRATION...")
        
        # Default Kinect intrinsics (approximate)
        self.kinect_intrinsic = np.array([
            [525.0, 0, 319.5],
            [0, 525.0, 239.5],
            [0, 0, 1]
        ])
        
        # Default webcam intrinsics (will be refined)
        self.webcam1_intrinsic = np.array([
            [800.0, 0, 320.0],
            [0, 800.0, 240.0],
            [0, 0, 1]
        ])
        
        self.webcam2_intrinsic = np.array([
            [800.0, 0, 320.0],
            [0, 800.0, 240.0],
            [0, 0, 1]
        ])
        
        print("   ✅ Camera calibration matrices set")
    
    def capture_all_camera_data(self):
        """Capture synchronized data from all cameras"""
        frame_data = {
            "kinect_depth": None,
            "kinect_rgb": None,
            "webcam1": None,
            "webcam2": None,
            "timestamp": time.time()
        }
        
        # Capture Kinect data
        if self.kinect_depth_active or self.kinect_rgb_active:
            try:
                depth_data, _ = freenect.sync_get_depth()
                rgb_data, _ = freenect.sync_get_video()
                
                if depth_data is not None:
                    frame_data["kinect_depth"] = depth_data
                
                if rgb_data is not None:
                    frame_data["kinect_rgb"] = rgb_data
                    
            except Exception as e:
                print(f"Kinect capture error: {e}")
        
        # Capture webcam data
        if self.webcam1_active and self.webcam1_stream:
            try:
                grabbed, webcam1_frame = self.webcam1_stream.read()
                if grabbed and webcam1_frame is not None:
                    frame_data["webcam1"] = webcam1_frame
            except Exception as e:
                print(f"Webcam 1 error: {e}")
        
        if self.webcam2_active and self.webcam2_stream:
            try:
                grabbed, webcam2_frame = self.webcam2_stream.read()
                if grabbed and webcam2_frame is not None:
                    frame_data["webcam2"] = webcam2_frame
            except Exception as e:
                print(f"Webcam 2 error: {e}")
        
        return frame_data
    
    def extract_depth_from_stereo(self, img1, img2):
        """Extract depth using stereo vision from webcams"""
        if img1 is None or img2 is None:
            return None
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Create stereo matcher
        stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
        
        # Compute disparity
        disparity = stereo.compute(gray1, gray2)
        
        # Convert disparity to depth (approximate)
        # Depth = (focal_length * baseline) / disparity
        focal_length = 800.0  # Approximate
        baseline = 0.1  # Approximate 10cm between webcams
        
        # Avoid division by zero
        disparity_safe = np.where(disparity > 0, disparity, 1)
        depth = (focal_length * baseline) / (disparity_safe / 16.0)  # StereoBM uses 16-bit
        
        # Filter unrealistic depths
        depth = np.where((depth > 0.1) & (depth < 5.0), depth, 0)
        
        return depth.astype(np.float32)
    
    def fuse_depth_data(self, kinect_depth, stereo_depth):
        """Fuse Kinect depth with stereo depth for higher precision"""
        if kinect_depth is None and stereo_depth is None:
            return None
        
        if kinect_depth is None:
            return stereo_depth
        
        if stereo_depth is None:
            return kinect_depth.astype(np.float32) / 1000.0  # Convert mm to meters
        
        # Resize stereo depth to match Kinect resolution
        kinect_h, kinect_w = kinect_depth.shape
        stereo_resized = cv2.resize(stereo_depth, (kinect_w, kinect_h))
        
        # Convert Kinect depth to meters
        kinect_depth_m = kinect_depth.astype(np.float32) / 1000.0
        
        # Weighted fusion (prefer Kinect where available)
        kinect_mask = kinect_depth_m > 0
        stereo_mask = stereo_resized > 0
        
        fused_depth = np.zeros_like(kinect_depth_m)
        
        # Use Kinect where available
        fused_depth[kinect_mask] = kinect_depth_m[kinect_mask]
        
        # Fill gaps with stereo data
        gap_mask = (~kinect_mask) & stereo_mask
        fused_depth[gap_mask] = stereo_resized[gap_mask]
        
        # Blend overlapping regions
        overlap_mask = kinect_mask & stereo_mask
        fused_depth[overlap_mask] = (0.7 * kinect_depth_m[overlap_mask] + 
                                   0.3 * stereo_resized[overlap_mask])
        
        return fused_depth
    
    def create_3d_point_cloud(self, depth_data, rgb_data=None):
        """Create 3D point cloud from fused depth data"""
        if depth_data is None:
            return None
        
        h, w = depth_data.shape
        
        # Create coordinate grids
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert to 3D coordinates using camera intrinsics
        fx, fy = self.kinect_intrinsic[0, 0], self.kinect_intrinsic[1, 1]
        cx, cy = self.kinect_intrinsic[0, 2], self.kinect_intrinsic[1, 2]
        
        # Calculate 3D points
        z = depth_data
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        
        # Filter valid points
        valid_mask = z > 0
        
        points = np.stack([x[valid_mask], y[valid_mask], z[valid_mask]], axis=1)
        
        # Add colors if RGB data available
        colors = None
        if rgb_data is not None:
            rgb_resized = cv2.resize(rgb_data, (w, h))
            colors = rgb_resized[valid_mask] / 255.0
        
        return points, colors
    
    def create_topography_grid(self, points, grid_resolution=0.01):
        """Create high-precision topography grid"""
        if points is None or len(points) == 0:
            return None
        
        # Extract X, Y, Z coordinates
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        z_coords = points[:, 2]
        
        # Create regular grid
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        
        grid_x = np.arange(x_min, x_max, grid_resolution)
        grid_y = np.arange(y_min, y_max, grid_resolution)
        
        grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
        
        # Interpolate Z values onto regular grid
        try:
            grid_Z = griddata(
                (x_coords, y_coords), z_coords,
                (grid_X, grid_Y), method='cubic', fill_value=0
            )
            
            return {
                'X': grid_X,
                'Y': grid_Y,
                'Z': grid_Z,
                'resolution': grid_resolution
            }
        except Exception as e:
            print(f"Topography grid creation failed: {e}")
            return None
    
    def display_3d_reconstruction(self, frame_data):
        """Display real-time 3D reconstruction"""
        
        # Extract stereo depth from webcams
        stereo_depth = None
        if frame_data["webcam1"] is not None and frame_data["webcam2"] is not None:
            stereo_depth = self.extract_depth_from_stereo(
                frame_data["webcam1"], frame_data["webcam2"]
            )
        
        # Fuse depth data
        fused_depth = self.fuse_depth_data(frame_data["kinect_depth"], stereo_depth)
        
        if fused_depth is not None:
            # Create point cloud
            points, colors = self.create_3d_point_cloud(fused_depth, frame_data["kinect_rgb"])
            
            if points is not None:
                # Create topography grid
                self.topography_grid = self.create_topography_grid(points)
                
                # Display depth visualization
                depth_display = (fused_depth / np.max(fused_depth) * 255).astype(np.uint8)
                depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                
                # Add topography info
                if self.topography_grid is not None:
                    grid_info = f"Grid: {self.topography_grid['X'].shape}"
                    cv2.putText(depth_colored, grid_info, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('3D Fused Depth', depth_colored)
        
        # Display individual camera feeds
        if frame_data["kinect_rgb"] is not None:
            kinect_rgb_bgr = cv2.cvtColor(frame_data["kinect_rgb"], cv2.COLOR_RGB2BGR)
            cv2.imshow('Kinect RGB', cv2.resize(kinect_rgb_bgr, (320, 240)))
        
        if frame_data["webcam1"] is not None:
            cv2.imshow('Webcam 1', cv2.resize(frame_data["webcam1"], (320, 240)))
        
        if frame_data["webcam2"] is not None:
            cv2.imshow('Webcam 2', cv2.resize(frame_data["webcam2"], (320, 240)))
        
        # Display stereo depth if available
        if stereo_depth is not None:
            stereo_display = (stereo_depth / np.max(stereo_depth) * 255).astype(np.uint8)
            stereo_colored = cv2.applyColorMap(stereo_display, cv2.COLORMAP_PLASMA)
            cv2.imshow('Stereo Depth', cv2.resize(stereo_colored, (320, 240)))
    
    def run_3d_extrapolation_system(self):
        """Run the complete 3D extrapolation system"""
        print("="*60)
        print("🎯 MULTI-CAMERA 3D EXTRAPOLATION & TOPOGRAPHY")
        print("="*60)
        
        # Initialize cameras
        if not self.initialize_all_cameras():
            print("❌ Insufficient cameras for 3D reconstruction")
            return False
        
        print("\n🎮 STARTING 3D EXTRAPOLATION...")
        print("Press 'q' to exit, 's' to save point cloud")
        
        try:
            while True:
                # Capture from all cameras
                frame_data = self.capture_all_camera_data()
                
                # Perform 3D reconstruction and display
                self.display_3d_reconstruction(frame_data)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    print("💾 Saving point cloud...")
                    # Save functionality here
                
                self.frame_count += 1
                
                # Performance info
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / elapsed
                    print(f"📊 3D Reconstruction: {fps:.1f} FPS")
        
        finally:
            cv2.destroyAllWindows()
            self.cleanup()
        
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
    """Run multi-camera 3D extrapolation system"""
    system = MultiCamera3DExtrapolation()
    
    try:
        success = system.run_3d_extrapolation_system()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ 3D extrapolation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
