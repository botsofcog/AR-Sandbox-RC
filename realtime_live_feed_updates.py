#!/usr/bin/env python3
"""
Real-time Live Feed Updates - Active topography with extreme precision
"""

import cv2
import numpy as np
import time
import sys
import threading
from scipy.interpolate import griddata
from collections import deque

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

try:
    sys.path.append('external_libs/python-examples-cv')
    import camera_stream
    CAMERA_STREAM_AVAILABLE = True
except ImportError:
    CAMERA_STREAM_AVAILABLE = False

class RealTimeLiveFeedUpdates:
    """
    Real-time live feed updates with extreme precision topography
    """
    
    def __init__(self):
        # Precision settings
        self.grid_resolution = 0.005  # 5mm precision
        self.update_rate = 30  # 30 FPS updates
        
        # Multi-camera data
        self.kinect_depth = None
        self.kinect_rgb = None
        self.webcam1 = None
        self.webcam2 = None
        self.stereo_depth = None
        self.fused_depth = None
        
        # Real-time processing
        self.topography_grid = None
        self.previous_grid = None
        self.change_detection = None
        self.temporal_buffer = deque(maxlen=10)
        
        # Camera streams
        self.webcam1_stream = None
        self.webcam2_stream = None
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.processing_times = deque(maxlen=30)
        
    def initialize_cameras(self):
        """Initialize all cameras for real-time updates"""
        print("🎮 INITIALIZING CAMERAS FOR REAL-TIME UPDATES...")
        
        # Initialize Kinect
        kinect_ok = self.initialize_kinect()
        
        # Initialize webcams for stereo
        webcam_ok = self.initialize_webcams()
        
        total_cameras = sum([
            self.kinect_depth is not None,
            self.kinect_rgb is not None,
            self.webcam1_stream is not None,
            self.webcam2_stream is not None
        ])
        
        print(f"   📊 Active cameras: {total_cameras}/4")
        return total_cameras >= 2
    
    def initialize_kinect(self):
        """Initialize Kinect with proven real data method"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Reset and initialize like working system
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(1.0)
            
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            # Test for real data
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            if depth_data is not None:
                depth_std = np.std(depth_data)
                if depth_std > 50:  # Real variation
                    print("   ✅ Kinect depth: REAL DATA")
                    return True
            
            print("   ⚠️ Kinect depth: May be test patterns")
            return True
            
        except Exception as e:
            print(f"   ❌ Kinect failed: {e}")
            return False
    
    def initialize_webcams(self):
        """Initialize webcams for stereo depth"""
        if not CAMERA_STREAM_AVAILABLE:
            return False
        
        try:
            # Webcam 1
            self.webcam1_stream = camera_stream.CameraVideoStream()
            self.webcam1_stream.open(src=0, backend=cv2.CAP_DSHOW)
            time.sleep(0.3)
            
            # Webcam 2  
            self.webcam2_stream = camera_stream.CameraVideoStream()
            self.webcam2_stream.open(src=1, backend=cv2.CAP_DSHOW)
            time.sleep(0.3)
            
            print("   ✅ Stereo webcams initialized")
            return True
            
        except Exception as e:
            print(f"   ❌ Webcams failed: {e}")
            return False
    
    def capture_all_data(self):
        """Capture synchronized data from all cameras"""
        capture_start = time.time()
        
        # Capture Kinect
        if KINECT_AVAILABLE:
            try:
                self.kinect_depth, _ = freenect.sync_get_depth()
                self.kinect_rgb, _ = freenect.sync_get_video()
            except:
                pass
        
        # Capture webcams
        if self.webcam1_stream and self.webcam2_stream:
            try:
                grabbed1, self.webcam1 = self.webcam1_stream.read()
                grabbed2, self.webcam2 = self.webcam2_stream.read()
                
                if not grabbed1:
                    self.webcam1 = None
                if not grabbed2:
                    self.webcam2 = None
            except:
                pass
        
        capture_time = time.time() - capture_start
        return capture_time
    
    def compute_stereo_depth(self):
        """Compute stereo depth from webcams"""
        if self.webcam1 is None or self.webcam2 is None:
            return None
        
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(self.webcam1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(self.webcam2, cv2.COLOR_BGR2GRAY)
            
            # Enhanced stereo matching
            stereo = cv2.StereoBM_create(numDisparities=96, blockSize=15)
            stereo.setMinDisparity(0)
            stereo.setSpeckleWindowSize(100)
            stereo.setSpeckleRange(32)
            
            # Compute disparity
            disparity = stereo.compute(gray1, gray2)
            
            # Convert to depth
            focal_length = 800.0
            baseline = 0.12
            
            disparity_safe = np.where(disparity > 0, disparity, 1)
            depth = (focal_length * baseline) / (disparity_safe / 16.0)
            
            # Filter realistic depths
            depth_filtered = np.where((depth > 0.1) & (depth < 3.0), depth, 0)
            
            return depth_filtered.astype(np.float32)
            
        except Exception as e:
            return None
    
    def fuse_depth_sources(self):
        """Fuse Kinect and stereo depth for extreme precision"""
        if self.kinect_depth is None and self.stereo_depth is None:
            return None
        
        if self.kinect_depth is None:
            return self.stereo_depth
        
        if self.stereo_depth is None:
            return self.kinect_depth.astype(np.float32) / 1000.0
        
        # Resize to match
        h, w = self.stereo_depth.shape
        kinect_resized = cv2.resize(self.kinect_depth.astype(np.float32) / 1000.0, (w, h))
        
        # Weighted fusion for extreme precision
        kinect_mask = kinect_resized > 0
        stereo_mask = self.stereo_depth > 0
        
        fused = np.zeros_like(self.stereo_depth)
        
        # Use Kinect where available (more accurate)
        fused[kinect_mask] = kinect_resized[kinect_mask]
        
        # Fill gaps with stereo
        gap_mask = (~kinect_mask) & stereo_mask
        fused[gap_mask] = self.stereo_depth[gap_mask]
        
        # Precision blend in overlapping regions
        overlap_mask = kinect_mask & stereo_mask
        fused[overlap_mask] = (0.8 * kinect_resized[overlap_mask] + 
                              0.2 * self.stereo_depth[overlap_mask])
        
        return fused
    
    def create_precision_topography(self, depth_data):
        """Create extreme precision topography grid"""
        if depth_data is None:
            return None
        
        h, w = depth_data.shape
        
        # Camera intrinsics
        fx, fy = 525.0, 525.0
        cx, cy = w/2, h/2
        
        # Create coordinate grids
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert to 3D points
        z = depth_data
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        
        # Filter valid points
        valid_mask = z > 0
        
        if np.sum(valid_mask) < 100:
            return None
        
        points = np.stack([x[valid_mask], y[valid_mask], z[valid_mask]], axis=1)
        
        # Extract coordinates
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        z_coords = points[:, 2]
        
        # Create bounds
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        
        if x_max - x_min < 0.1 or y_max - y_min < 0.1:
            return None
        
        # Create extreme precision grid
        grid_x = np.arange(x_min, x_max, self.grid_resolution)
        grid_y = np.arange(y_min, y_max, self.grid_resolution)
        
        # Limit for real-time performance
        if len(grid_x) > 800:
            grid_x = np.linspace(x_min, x_max, 800)
        if len(grid_y) > 600:
            grid_y = np.linspace(y_min, y_max, 600)
        
        grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
        
        try:
            # High-precision interpolation
            grid_Z = griddata(
                (x_coords, y_coords), z_coords,
                (grid_X, grid_Y), method='cubic', fill_value=0
            )
            
            return {
                'X': grid_X,
                'Y': grid_Y,
                'Z': grid_Z,
                'resolution_mm': self.grid_resolution * 1000,
                'points_count': len(points),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return None
    
    def detect_changes(self, current_grid):
        """Detect real-time changes in topography"""
        if current_grid is None or self.previous_grid is None:
            self.previous_grid = current_grid
            return None
        
        try:
            # Calculate difference
            current_Z = current_grid['Z']
            previous_Z = self.previous_grid['Z']
            
            if current_Z.shape != previous_Z.shape:
                self.previous_grid = current_grid
                return None
            
            # Compute change map
            change_map = np.abs(current_Z - previous_Z)
            
            # Threshold for significant changes (1mm)
            significant_changes = change_map > 0.001
            
            # Update previous
            self.previous_grid = current_grid
            
            return {
                'change_map': change_map,
                'significant_changes': significant_changes,
                'max_change': np.max(change_map),
                'change_pixels': np.sum(significant_changes)
            }
            
        except Exception as e:
            return None
    
    def process_real_time_updates(self):
        """Process real-time topography updates"""
        processing_start = time.time()
        
        # Compute stereo depth
        self.stereo_depth = self.compute_stereo_depth()
        
        # Fuse depth sources
        self.fused_depth = self.fuse_depth_sources()
        
        # Create precision topography
        if self.fused_depth is not None:
            self.topography_grid = self.create_precision_topography(self.fused_depth)
            
            # Detect changes
            if self.topography_grid is not None:
                self.change_detection = self.detect_changes(self.topography_grid)
        
        processing_time = time.time() - processing_start
        self.processing_times.append(processing_time)
        
        return processing_time
    
    def display_real_time_system(self):
        """Display real-time live feed update system"""
        print("🎮 REAL-TIME LIVE FEED UPDATES SYSTEM")
        print("="*50)
        
        # Create windows
        cv2.namedWindow('Fused Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Live Topography', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Change Detection', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('System Performance', cv2.WINDOW_AUTOSIZE)
        
        try:
            while True:
                frame_start = time.time()
                
                # Capture all camera data
                capture_time = self.capture_all_data()
                
                # Process real-time updates
                processing_time = self.process_real_time_updates()
                
                # Display fused depth
                if self.fused_depth is not None:
                    depth_norm = cv2.normalize(self.fused_depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(depth_colored, "FUSED DEPTH (EXTREME PRECISION)", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.imshow('Fused Depth', depth_colored)
                
                # Display live topography
                if self.topography_grid is not None:
                    topo_Z = self.topography_grid['Z']
                    topo_norm = cv2.normalize(topo_Z, None, 0, 255, cv2.NORM_MINMAX)
                    topo_colored = cv2.applyColorMap(topo_norm.astype(np.uint8), cv2.COLORMAP_RAINBOW)
                    
                    resolution = self.topography_grid['resolution_mm']
                    points = self.topography_grid['points_count']
                    
                    cv2.putText(topo_colored, f"LIVE TOPOGRAPHY {resolution:.1f}mm", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(topo_colored, f"Points: {points}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Live Topography', topo_colored)
                
                # Display change detection
                if self.change_detection is not None:
                    change_map = self.change_detection['change_map']
                    change_norm = cv2.normalize(change_map, None, 0, 255, cv2.NORM_MINMAX)
                    change_colored = cv2.applyColorMap(change_norm.astype(np.uint8), cv2.COLORMAP_HOT)
                    
                    max_change = self.change_detection['max_change'] * 1000  # Convert to mm
                    change_pixels = self.change_detection['change_pixels']
                    
                    cv2.putText(change_colored, "REAL-TIME CHANGES", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(change_colored, f"Max change: {max_change:.1f}mm", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(change_colored, f"Changed pixels: {change_pixels}", (10, 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Change Detection', change_colored)
                
                # Performance display
                status_img = np.zeros((400, 600, 3), dtype=np.uint8)
                
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                
                avg_processing = np.mean(self.processing_times) if self.processing_times else 0
                
                cv2.putText(status_img, "REAL-TIME PERFORMANCE", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(status_img, f"Processing: {avg_processing*1000:.1f}ms", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(status_img, f"Capture: {capture_time*1000:.1f}ms", 
                           (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if self.topography_grid:
                    cv2.putText(status_img, f"Grid Resolution: {self.topography_grid['resolution_mm']:.1f}mm", 
                               (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.putText(status_img, "EXTREME PRECISION REAL-TIME UPDATES", 
                           (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(status_img, "Press 'q' to exit", 
                           (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('System Performance', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                # Maintain target frame rate
                frame_time = time.time() - frame_start
                target_time = 1.0 / self.update_rate
                if frame_time < target_time:
                    time.sleep(target_time - frame_time)
        
        finally:
            cv2.destroyAllWindows()
    
    def run_realtime_system(self):
        """Run real-time live feed updates system"""
        print("="*60)
        print("🎯 REAL-TIME LIVE FEED UPDATES")
        print("="*60)
        print(f"📊 Target: {self.update_rate} FPS")
        print(f"🔧 Precision: {self.grid_resolution*1000:.1f}mm")
        print("🎮 Extreme precision real-time topography")
        print("="*60)
        
        if not self.initialize_cameras():
            print("❌ Insufficient cameras")
            return False
        
        self.display_real_time_system()
        return True

def main():
    """Run real-time live feed updates system"""
    system = RealTimeLiveFeedUpdates()
    
    try:
        success = system.run_realtime_system()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Real-time system failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
