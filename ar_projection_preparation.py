#!/usr/bin/env python3
"""
AR Projection Preparation - Camera-projector calibration for real sand surface
"""

import cv2
import numpy as np
import time
import sys
import json
import os

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

class ARProjectionPreparation:
    """
    AR projection preparation system for real sand surface
    """
    
    def __init__(self):
        # Projection settings
        self.projector_resolution = (1920, 1080)  # Full HD projector
        self.projection_area = None
        self.camera_matrix = None
        self.projector_matrix = None
        self.homography_matrix = None
        
        # Calibration data
        self.calibration_points = []
        self.sand_surface_plane = None
        self.projection_bounds = None
        
        # Real-time data
        self.kinect_depth = None
        self.kinect_rgb = None
        self.sand_surface = None
        self.projection_overlay = None
        
        # AR overlay elements
        self.overlay_elements = {
            'contour_lines': True,
            'height_colors': True,
            'water_simulation': True,
            'vehicle_paths': True,
            'construction_zones': True
        }
        
    def initialize_kinect(self):
        """Initialize Kinect for projection preparation"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(1.0)
            
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            print("✅ Kinect initialized for AR projection")
            return True
            
        except Exception as e:
            print(f"❌ Kinect init failed: {e}")
            return False
    
    def capture_sand_surface(self):
        """Capture real sand surface data"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            self.kinect_depth, _ = freenect.sync_get_depth()
            self.kinect_rgb, _ = freenect.sync_get_video()
            
            if self.kinect_depth is not None:
                # Process sand surface
                self.sand_surface = self.process_sand_surface(self.kinect_depth)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def process_sand_surface(self, depth_data):
        """Process depth data to extract sand surface"""
        if depth_data is None:
            return None
        
        # Filter and smooth depth data
        depth_filtered = cv2.medianBlur(depth_data.astype(np.float32), 5)
        
        # Remove outliers
        valid_mask = (depth_filtered > 500) & (depth_filtered < 4000)  # 0.5m to 4m
        depth_clean = np.where(valid_mask, depth_filtered, 0)
        
        # Apply Gaussian smoothing
        depth_smooth = cv2.GaussianBlur(depth_clean, (7, 7), 0)
        
        return depth_smooth
    
    def detect_projection_area(self, sand_surface):
        """Detect the area suitable for projection"""
        if sand_surface is None:
            return None
        
        # Find valid sand area
        valid_mask = sand_surface > 0
        
        if np.sum(valid_mask) < 1000:  # Need minimum area
            return None
        
        # Find contours of valid area
        mask_uint8 = (valid_mask * 255).astype(np.uint8)
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None
        
        # Find largest contour (main sand area)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Ensure minimum size
        if w < 100 or h < 100:
            return None
        
        return {
            'contour': largest_contour,
            'bounds': (x, y, w, h),
            'area': cv2.contourArea(largest_contour),
            'center': (x + w//2, y + h//2)
        }
    
    def calculate_sand_plane(self, sand_surface, projection_area):
        """Calculate the sand surface plane for projection mapping"""
        if sand_surface is None or projection_area is None:
            return None
        
        x, y, w, h = projection_area['bounds']
        
        # Extract depth values in projection area
        roi_depth = sand_surface[y:y+h, x:x+w]
        valid_depths = roi_depth[roi_depth > 0]
        
        if len(valid_depths) < 100:
            return None
        
        # Calculate plane parameters
        mean_depth = np.mean(valid_depths)
        std_depth = np.std(valid_depths)
        
        # Create coordinate system
        h_coords, w_coords = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        
        # Flatten coordinates and depths
        coords = np.column_stack([
            w_coords.flatten(),
            h_coords.flatten(),
            roi_depth.flatten()
        ])
        
        # Filter valid points
        valid_coords = coords[coords[:, 2] > 0]
        
        if len(valid_coords) < 100:
            return None
        
        # Fit plane using least squares
        A = np.column_stack([valid_coords[:, 0], valid_coords[:, 1], np.ones(len(valid_coords))])
        b = valid_coords[:, 2]
        
        try:
            plane_params = np.linalg.lstsq(A, b, rcond=None)[0]
            
            return {
                'params': plane_params,
                'mean_depth': mean_depth,
                'std_depth': std_depth,
                'bounds': (x, y, w, h),
                'point_count': len(valid_coords)
            }
            
        except np.linalg.LinAlgError:
            return None
    
    def create_projection_mapping(self, sand_plane):
        """Create projection mapping from camera to projector coordinates"""
        if sand_plane is None:
            return None
        
        # Camera intrinsics (Kinect approximate)
        camera_matrix = np.array([
            [525.0, 0, 320.0],
            [0, 525.0, 240.0],
            [0, 0, 1]
        ])
        
        # Projector intrinsics (estimated)
        projector_matrix = np.array([
            [1000.0, 0, 960.0],
            [0, 1000.0, 540.0],
            [0, 0, 1]
        ])
        
        # Create homography for camera-to-projector mapping
        x, y, w, h = sand_plane['bounds']
        
        # Source points (camera coordinates)
        src_points = np.array([
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h]
        ], dtype=np.float32)
        
        # Destination points (projector coordinates)
        # Map to central area of projector
        proj_margin = 100
        dst_points = np.array([
            [proj_margin, proj_margin],
            [self.projector_resolution[0] - proj_margin, proj_margin],
            [self.projector_resolution[0] - proj_margin, self.projector_resolution[1] - proj_margin],
            [proj_margin, self.projector_resolution[1] - proj_margin]
        ], dtype=np.float32)
        
        # Calculate homography
        homography = cv2.getPerspectiveTransform(src_points, dst_points)
        
        return {
            'homography': homography,
            'camera_matrix': camera_matrix,
            'projector_matrix': projector_matrix,
            'src_points': src_points,
            'dst_points': dst_points
        }
    
    def create_ar_overlay(self, sand_surface, projection_mapping):
        """Create AR overlay for projection"""
        if sand_surface is None or projection_mapping is None:
            return None
        
        h, w = sand_surface.shape
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Height-based coloring
        if self.overlay_elements['height_colors']:
            depth_norm = cv2.normalize(sand_surface, None, 0, 255, cv2.NORM_MINMAX)
            height_colored = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_RAINBOW)
            overlay = cv2.addWeighted(overlay, 0.5, height_colored, 0.5, 0)
        
        # Contour lines
        if self.overlay_elements['contour_lines']:
            # Create contour lines at different heights
            for level in range(0, 255, 30):
                contour_mask = np.abs(depth_norm - level) < 5
                overlay[contour_mask] = [255, 255, 255]  # White contours
        
        # Water simulation areas
        if self.overlay_elements['water_simulation']:
            # Identify low areas for water
            low_areas = depth_norm < 50
            overlay[low_areas] = [255, 100, 0]  # Blue for water
        
        # Construction zones
        if self.overlay_elements['construction_zones']:
            # Add grid overlay for construction planning
            grid_spacing = 20
            for i in range(0, h, grid_spacing):
                overlay[i, :] = [100, 100, 100]  # Gray grid lines
            for j in range(0, w, grid_spacing):
                overlay[:, j] = [100, 100, 100]
        
        return overlay
    
    def project_overlay_to_projector_space(self, overlay, projection_mapping):
        """Transform overlay to projector coordinate space"""
        if overlay is None or projection_mapping is None:
            return None
        
        homography = projection_mapping['homography']
        
        # Transform overlay to projector space
        projector_overlay = cv2.warpPerspective(
            overlay, 
            homography, 
            self.projector_resolution
        )
        
        return projector_overlay
    
    def save_calibration_data(self, projection_mapping, filename="ar_projection_calibration.json"):
        """Save projection calibration data"""
        if projection_mapping is None:
            return False
        
        try:
            calibration_data = {
                'timestamp': time.time(),
                'projector_resolution': self.projector_resolution,
                'homography': projection_mapping['homography'].tolist(),
                'camera_matrix': projection_mapping['camera_matrix'].tolist(),
                'projector_matrix': projection_mapping['projector_matrix'].tolist(),
                'src_points': projection_mapping['src_points'].tolist(),
                'dst_points': projection_mapping['dst_points'].tolist(),
                'overlay_elements': self.overlay_elements
            }
            
            with open(filename, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            print(f"💾 Projection calibration saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def display_ar_projection_system(self):
        """Display AR projection preparation system"""
        print("🎮 AR PROJECTION PREPARATION SYSTEM")
        print("="*50)
        
        cv2.namedWindow('Sand Surface', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('AR Overlay', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Projector Output', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Projection Status', cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Capture sand surface
                if self.capture_sand_surface():
                    # Detect projection area
                    self.projection_area = self.detect_projection_area(self.sand_surface)
                    
                    if self.projection_area is not None:
                        # Calculate sand plane
                        self.sand_surface_plane = self.calculate_sand_plane(
                            self.sand_surface, self.projection_area
                        )
                        
                        if self.sand_surface_plane is not None:
                            # Create projection mapping
                            projection_mapping = self.create_projection_mapping(self.sand_surface_plane)
                            
                            if projection_mapping is not None:
                                # Create AR overlay
                                ar_overlay = self.create_ar_overlay(self.sand_surface, projection_mapping)
                                
                                if ar_overlay is not None:
                                    # Transform to projector space
                                    self.projection_overlay = self.project_overlay_to_projector_space(
                                        ar_overlay, projection_mapping
                                    )
                
                # Display sand surface
                if self.sand_surface is not None:
                    sand_norm = cv2.normalize(self.sand_surface, None, 0, 255, cv2.NORM_MINMAX)
                    sand_colored = cv2.applyColorMap(sand_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    
                    # Draw projection area
                    if self.projection_area is not None:
                        x, y, w, h = self.projection_area['bounds']
                        cv2.rectangle(sand_colored, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(sand_colored, "PROJECTION AREA", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    cv2.putText(sand_colored, "SAND SURFACE", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Sand Surface', sand_colored)
                
                # Display AR overlay
                if hasattr(self, 'ar_overlay') and self.ar_overlay is not None:
                    cv2.putText(self.ar_overlay, "AR OVERLAY", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('AR Overlay', self.ar_overlay)
                
                # Display projector output
                if self.projection_overlay is not None:
                    # Resize for display
                    display_size = (960, 540)  # Half resolution for display
                    projector_display = cv2.resize(self.projection_overlay, display_size)
                    cv2.putText(projector_display, "PROJECTOR OUTPUT", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Projector Output', projector_display)
                
                # Status display
                status_img = np.zeros((400, 600, 3), dtype=np.uint8)
                
                frame_count += 1
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                
                cv2.putText(status_img, "AR PROJECTION PREPARATION", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                sand_status = "✅ DETECTED" if self.sand_surface is not None else "❌ NO DATA"
                cv2.putText(status_img, f"Sand Surface: {sand_status}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                area_status = "✅ DETECTED" if self.projection_area is not None else "❌ NOT FOUND"
                cv2.putText(status_img, f"Projection Area: {area_status}", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                plane_status = "✅ CALCULATED" if self.sand_surface_plane is not None else "❌ NOT READY"
                cv2.putText(status_img, f"Surface Plane: {plane_status}", 
                           (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                overlay_status = "✅ READY" if self.projection_overlay is not None else "❌ NOT READY"
                cv2.putText(status_img, f"AR Overlay: {overlay_status}", 
                           (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.putText(status_img, f"Projector: {self.projector_resolution[0]}x{self.projector_resolution[1]}", 
                           (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.putText(status_img, "Press 'q' to exit, 's' to save calibration", 
                           (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('Projection Status', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if hasattr(self, 'projection_mapping') and self.projection_mapping is not None:
                        if self.save_calibration_data(self.projection_mapping):
                            print("💾 AR projection calibration saved")
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_ar_projection_preparation(self):
        """Run AR projection preparation system"""
        print("="*60)
        print("🎯 AR PROJECTION PREPARATION")
        print("="*60)
        print(f"📽️ Projector: {self.projector_resolution[0]}x{self.projector_resolution[1]}")
        print("🏖️ Real sand surface mapping")
        print("🎨 AR overlay generation")
        print("📐 Camera-projector calibration")
        print("="*60)
        
        if not self.initialize_kinect():
            print("❌ Kinect initialization failed")
            return False
        
        self.display_ar_projection_system()
        return True

def main():
    """Run AR projection preparation system"""
    system = ARProjectionPreparation()
    
    try:
        success = system.run_ar_projection_preparation()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ AR projection preparation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
