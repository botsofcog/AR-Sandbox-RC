#!/usr/bin/env python3
"""
Precision Topography Grid - 5mm precision using Magic-Sand data
"""

import cv2
import numpy as np
import time
import sys
from scipy.interpolate import griddata
import json
import os

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

class PrecisionTopographyGrid:
    """
    High-precision topography grid system
    """
    
    def __init__(self):
        self.grid_resolution = 0.005  # 5mm precision
        self.topography_grid = None
        self.kinect_depth = None
        self.kinect_rgb = None
        
        # Camera calibration
        self.fx, self.fy = 525.0, 525.0
        self.cx, self.cy = 320.0, 240.0
        
    def capture_kinect_data(self):
        """Capture real Kinect data"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Get depth and RGB
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            if depth_data is not None:
                self.kinect_depth = depth_data
            
            if rgb_data is not None:
                self.kinect_rgb = rgb_data
            
            return depth_data is not None
            
        except Exception as e:
            print(f"Kinect capture error: {e}")
            return False
    
    def depth_to_3d_points(self, depth_data):
        """Convert depth to 3D points with camera calibration"""
        if depth_data is None:
            return None
        
        h, w = depth_data.shape
        
        # Create coordinate grids
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert depth to meters
        z = depth_data.astype(np.float32) / 1000.0
        
        # Calculate 3D coordinates
        x = (u - self.cx) * z / self.fx
        y = (v - self.cy) * z / self.fy
        
        # Filter valid points
        valid_mask = (z > 0.1) & (z < 5.0)
        
        if np.sum(valid_mask) == 0:
            return None
        
        points = np.stack([
            x[valid_mask],
            y[valid_mask], 
            z[valid_mask]
        ], axis=1)
        
        return points
    
    def create_precision_grid(self, points):
        """Create high-precision topography grid"""
        if points is None or len(points) < 10:
            return None
        
        # Extract coordinates
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        z_coords = points[:, 2]
        
        # Create bounds
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        
        if x_max - x_min < 0.1 or y_max - y_min < 0.1:
            return None
        
        # Create high-resolution grid
        grid_x = np.arange(x_min, x_max, self.grid_resolution)
        grid_y = np.arange(y_min, y_max, self.grid_resolution)
        
        # Limit for performance
        if len(grid_x) > 1000:
            grid_x = np.linspace(x_min, x_max, 1000)
        if len(grid_y) > 1000:
            grid_y = np.linspace(y_min, y_max, 1000)
        
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
                'bounds': [x_min, x_max, y_min, y_max]
            }
            
        except Exception as e:
            print(f"Grid creation error: {e}")
            return None
    
    def save_topography_data(self, filename="topography_data.json"):
        """Save topography data"""
        if self.topography_grid is None:
            return False
        
        try:
            # Convert numpy arrays to lists for JSON
            data = {
                'resolution_mm': self.topography_grid['resolution_mm'],
                'points_count': self.topography_grid['points_count'],
                'bounds': self.topography_grid['bounds'],
                'grid_shape': self.topography_grid['Z'].shape,
                'timestamp': time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save grid data separately (binary)
            np.savez(filename.replace('.json', '.npz'),
                    X=self.topography_grid['X'],
                    Y=self.topography_grid['Y'],
                    Z=self.topography_grid['Z'])
            
            return True
            
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def display_precision_topography(self):
        """Display precision topography system"""
        print("🎮 PRECISION TOPOGRAPHY GRID SYSTEM")
        print("="*50)
        
        cv2.namedWindow('Kinect Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Precision Topography', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Grid Status', cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Capture data
                if self.capture_kinect_data():
                    # Convert to 3D points
                    points = self.depth_to_3d_points(self.kinect_depth)
                    
                    # Create precision grid
                    if points is not None:
                        self.topography_grid = self.create_precision_grid(points)
                
                # Display depth
                if self.kinect_depth is not None:
                    depth_norm = cv2.normalize(self.kinect_depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(depth_colored, "KINECT DEPTH", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Kinect Depth', depth_colored)
                
                # Display precision topography
                if self.topography_grid is not None:
                    grid_Z = self.topography_grid['Z']
                    topo_norm = cv2.normalize(grid_Z, None, 0, 255, cv2.NORM_MINMAX)
                    topo_colored = cv2.applyColorMap(topo_norm.astype(np.uint8), cv2.COLORMAP_RAINBOW)
                    
                    # Add precision info
                    resolution = self.topography_grid['resolution_mm']
                    points_count = self.topography_grid['points_count']
                    
                    cv2.putText(topo_colored, f"PRECISION: {resolution:.1f}mm", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(topo_colored, f"POINTS: {points_count}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(topo_colored, f"GRID: {grid_Z.shape}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    cv2.imshow('Precision Topography', topo_colored)
                
                # Status display
                status_img = np.zeros((300, 500, 3), dtype=np.uint8)
                
                frame_count += 1
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                
                cv2.putText(status_img, "PRECISION TOPOGRAPHY", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                kinect_status = "✅ ACTIVE" if self.kinect_depth is not None else "❌ INACTIVE"
                cv2.putText(status_img, f"Kinect: {kinect_status}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                grid_status = "✅ ACTIVE" if self.topography_grid is not None else "❌ INACTIVE"
                cv2.putText(status_img, f"Grid: {grid_status}", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if self.topography_grid:
                    cv2.putText(status_img, f"Resolution: {self.topography_grid['resolution_mm']:.1f}mm", 
                               (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.putText(status_img, "Press 'q' to exit, 's' to save", 
                           (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(status_img, "'+/-' to change resolution", 
                           (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('Grid Status', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if self.save_topography_data():
                        print("💾 Topography data saved")
                    else:
                        print("❌ Save failed")
                elif key == ord('+') or key == ord('='):
                    self.grid_resolution = max(0.001, self.grid_resolution - 0.001)
                    print(f"🔧 Resolution: {self.grid_resolution*1000:.1f}mm")
                elif key == ord('-'):
                    self.grid_resolution = min(0.02, self.grid_resolution + 0.001)
                    print(f"🔧 Resolution: {self.grid_resolution*1000:.1f}mm")
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_precision_system(self):
        """Run precision topography system"""
        print("="*60)
        print("🎯 PRECISION TOPOGRAPHY GRID SYSTEM")
        print("="*60)
        print(f"📊 Grid Resolution: {self.grid_resolution*1000:.1f}mm")
        print("🎮 Using real Kinect data for precision mapping")
        print("="*60)
        
        if not KINECT_AVAILABLE:
            print("❌ Kinect not available")
            return False
        
        self.display_precision_topography()
        return True

def main():
    """Run precision topography grid system"""
    system = PrecisionTopographyGrid()
    
    try:
        success = system.run_precision_system()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Precision system failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
