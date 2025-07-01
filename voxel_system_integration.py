#!/usr/bin/env python3
"""
Voxel System Integration - Connect 3D extrapolation to Divine Voxel Engine
"""

import cv2
import numpy as np
import time
import sys
import json
import os
from scipy.interpolate import griddata

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

class VoxelSystemIntegration:
    """
    Integration between 3D extrapolation and Divine Voxel Engine
    """
    
    def __init__(self):
        # Voxel settings
        self.voxel_size = 0.01  # 1cm voxels
        self.voxel_grid = None
        self.voxel_data = None
        
        # 3D data
        self.kinect_depth = None
        self.kinect_rgb = None
        self.topography_grid = None
        self.point_cloud = None
        
        # Divine Voxel Engine integration
        self.dve_path = "external_libs/divine-voxel-engine"
        self.voxel_materials = {
            'sand': {'id': 'dve_sand', 'color': [194, 178, 128]},
            'water': {'id': 'dve_water', 'color': [64, 164, 223]},
            'dirt': {'id': 'dve_dirt', 'color': [139, 69, 19]},
            'stone': {'id': 'dve_stone', 'color': [128, 128, 128]},
            'grass': {'id': 'dve_grass', 'color': [34, 139, 34]}
        }
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
    
    def initialize_kinect(self):
        """Initialize Kinect for voxel data capture"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            # Reset and initialize
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(1.0)
            
            freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
            freenect.set_video_mode(0, freenect.VIDEO_RGB)
            
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            print("✅ Kinect initialized for voxel capture")
            return True
            
        except Exception as e:
            print(f"❌ Kinect init failed: {e}")
            return False
    
    def capture_3d_data(self):
        """Capture 3D data for voxel conversion"""
        if not KINECT_AVAILABLE:
            return False
        
        try:
            self.kinect_depth, _ = freenect.sync_get_depth()
            self.kinect_rgb, _ = freenect.sync_get_video()
            
            return self.kinect_depth is not None
            
        except Exception as e:
            return False
    
    def depth_to_point_cloud(self, depth_data):
        """Convert depth data to 3D point cloud"""
        if depth_data is None:
            return None
        
        h, w = depth_data.shape
        
        # Camera intrinsics
        fx, fy = 525.0, 525.0
        cx, cy = w/2, h/2
        
        # Create coordinate grids
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert to 3D
        z = depth_data.astype(np.float32) / 1000.0  # Convert mm to m
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        
        # Filter valid points
        valid_mask = (z > 0.1) & (z < 5.0)
        
        if np.sum(valid_mask) == 0:
            return None
        
        points = np.stack([x[valid_mask], y[valid_mask], z[valid_mask]], axis=1)
        
        # Add colors if RGB available
        colors = None
        if self.kinect_rgb is not None:
            rgb_resized = cv2.resize(self.kinect_rgb, (w, h))
            colors = rgb_resized[valid_mask] / 255.0
        
        return {'points': points, 'colors': colors}
    
    def create_voxel_grid(self, point_cloud):
        """Create voxel grid from point cloud"""
        if point_cloud is None or point_cloud['points'] is None:
            return None
        
        points = point_cloud['points']
        colors = point_cloud['colors']
        
        # Calculate bounds
        min_bounds = np.min(points, axis=0)
        max_bounds = np.max(points, axis=0)
        
        # Create voxel grid dimensions
        grid_size = ((max_bounds - min_bounds) / self.voxel_size).astype(int) + 1
        
        # Limit grid size for performance
        max_size = 200
        if np.any(grid_size > max_size):
            scale_factor = max_size / np.max(grid_size)
            grid_size = (grid_size * scale_factor).astype(int)
            self.voxel_size = self.voxel_size / scale_factor
        
        # Initialize voxel grid
        voxel_grid = np.zeros(grid_size, dtype=np.uint8)
        voxel_colors = np.zeros((*grid_size, 3), dtype=np.uint8)
        
        # Fill voxel grid
        for i, point in enumerate(points):
            # Convert point to voxel coordinates
            voxel_coord = ((point - min_bounds) / self.voxel_size).astype(int)
            
            # Ensure within bounds
            if np.all(voxel_coord >= 0) and np.all(voxel_coord < grid_size):
                voxel_grid[tuple(voxel_coord)] = 1
                
                if colors is not None:
                    voxel_colors[tuple(voxel_coord)] = (colors[i] * 255).astype(np.uint8)
        
        return {
            'grid': voxel_grid,
            'colors': voxel_colors,
            'size': self.voxel_size,
            'bounds': [min_bounds, max_bounds],
            'dimensions': grid_size
        }
    
    def classify_voxel_materials(self, voxel_data):
        """Classify voxels into material types"""
        if voxel_data is None:
            return None
        
        grid = voxel_data['grid']
        colors = voxel_data['colors']
        
        # Material classification based on height and color
        material_grid = np.zeros_like(grid, dtype=np.uint8)
        
        # Get height information
        height_map = np.zeros(grid.shape[:2])
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                z_indices = np.where(grid[x, y, :] > 0)[0]
                if len(z_indices) > 0:
                    height_map[x, y] = np.max(z_indices)
        
        # Normalize height
        if np.max(height_map) > 0:
            height_norm = height_map / np.max(height_map)
        else:
            height_norm = height_map
        
        # Classify materials
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                for z in range(grid.shape[2]):
                    if grid[x, y, z] > 0:
                        height = height_norm[x, y]
                        color = colors[x, y, z]
                        
                        # Material classification logic
                        if height < 0.2:  # Low areas
                            if np.mean(color) < 100:  # Dark = water
                                material_grid[x, y, z] = 2  # Water
                            else:
                                material_grid[x, y, z] = 1  # Sand
                        elif height < 0.6:  # Medium areas
                            if color[1] > color[0] and color[1] > color[2]:  # Green
                                material_grid[x, y, z] = 5  # Grass
                            else:
                                material_grid[x, y, z] = 3  # Dirt
                        else:  # High areas
                            material_grid[x, y, z] = 4  # Stone
        
        return material_grid
    
    def export_to_divine_voxel_format(self, voxel_data, material_grid):
        """Export voxel data to Divine Voxel Engine format"""
        if voxel_data is None or material_grid is None:
            return None
        
        # Create DVE-compatible data structure
        dve_data = {
            'metadata': {
                'version': '1.0',
                'generator': 'AR Sandbox RC',
                'timestamp': time.time(),
                'voxel_size': voxel_data['size'],
                'dimensions': voxel_data['dimensions'].tolist(),
                'bounds': [bound.tolist() for bound in voxel_data['bounds']]
            },
            'voxels': [],
            'materials': self.voxel_materials
        }
        
        # Convert voxel grid to DVE format
        grid = voxel_data['grid']
        colors = voxel_data['colors']
        
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                for z in range(grid.shape[2]):
                    if grid[x, y, z] > 0:
                        material_id = material_grid[x, y, z]
                        color = colors[x, y, z].tolist()
                        
                        voxel = {
                            'position': [x, y, z],
                            'material': material_id,
                            'color': color,
                            'properties': {
                                'solid': True,
                                'transparent': material_id == 2,  # Water is transparent
                                'collision': True
                            }
                        }
                        
                        dve_data['voxels'].append(voxel)
        
        return dve_data
    
    def save_voxel_data(self, dve_data, filename="ar_sandbox_voxels.json"):
        """Save voxel data for Divine Voxel Engine"""
        if dve_data is None:
            return False
        
        try:
            # Save main data
            with open(filename, 'w') as f:
                json.dump(dve_data, f, indent=2)
            
            # Save binary grid data for faster loading
            binary_filename = filename.replace('.json', '.npz')
            if 'voxels' in dve_data and len(dve_data['voxels']) > 0:
                # Convert voxel list to arrays for faster processing
                positions = np.array([v['position'] for v in dve_data['voxels']])
                materials = np.array([v['material'] for v in dve_data['voxels']])
                colors = np.array([v['color'] for v in dve_data['voxels']])
                
                np.savez(binary_filename,
                        positions=positions,
                        materials=materials,
                        colors=colors,
                        metadata=dve_data['metadata'])
            
            print(f"💾 Voxel data saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def display_voxel_system(self):
        """Display voxel system integration"""
        print("🎮 VOXEL SYSTEM INTEGRATION")
        print("="*50)
        
        cv2.namedWindow('Kinect Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Voxel Visualization', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Material Classification', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Voxel Status', cv2.WINDOW_AUTOSIZE)
        
        try:
            while True:
                # Capture 3D data
                if self.capture_3d_data():
                    # Convert to point cloud
                    self.point_cloud = self.depth_to_point_cloud(self.kinect_depth)
                    
                    # Create voxel grid
                    if self.point_cloud is not None:
                        self.voxel_data = self.create_voxel_grid(self.point_cloud)
                        
                        if self.voxel_data is not None:
                            # Classify materials
                            material_grid = self.classify_voxel_materials(self.voxel_data)
                            
                            # Export to DVE format
                            if material_grid is not None:
                                dve_data = self.export_to_divine_voxel_format(self.voxel_data, material_grid)
                
                # Display depth
                if self.kinect_depth is not None:
                    depth_norm = cv2.normalize(self.kinect_depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_norm.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(depth_colored, "KINECT DEPTH", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Kinect Depth', depth_colored)
                
                # Display voxel visualization
                if self.voxel_data is not None:
                    # Create 2D projection of voxel grid
                    grid = self.voxel_data['grid']
                    voxel_2d = np.max(grid, axis=2)  # Top-down view
                    
                    if np.max(voxel_2d) > 0:
                        voxel_vis = cv2.normalize(voxel_2d, None, 0, 255, cv2.NORM_MINMAX)
                        voxel_colored = cv2.applyColorMap(voxel_vis.astype(np.uint8), cv2.COLORMAP_RAINBOW)
                        voxel_resized = cv2.resize(voxel_colored, (480, 360))
                        
                        cv2.putText(voxel_resized, "VOXEL GRID (TOP VIEW)", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.putText(voxel_resized, f"Size: {self.voxel_data['size']*1000:.1f}mm", (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(voxel_resized, f"Dims: {self.voxel_data['dimensions']}", (10, 80), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                        
                        cv2.imshow('Voxel Visualization', voxel_resized)
                
                # Status display
                status_img = np.zeros((400, 600, 3), dtype=np.uint8)
                
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                
                cv2.putText(status_img, "VOXEL SYSTEM INTEGRATION", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                kinect_status = "✅ ACTIVE" if self.kinect_depth is not None else "❌ INACTIVE"
                cv2.putText(status_img, f"Kinect: {kinect_status}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                voxel_status = "✅ ACTIVE" if self.voxel_data is not None else "❌ INACTIVE"
                cv2.putText(status_img, f"Voxels: {voxel_status}", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if self.voxel_data:
                    voxel_count = np.sum(self.voxel_data['grid'] > 0)
                    cv2.putText(status_img, f"Voxel Count: {voxel_count}", 
                               (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.putText(status_img, "Divine Voxel Engine Integration", 
                           (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(status_img, "Press 'q' to exit, 's' to save", 
                           (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('Voxel Status', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if self.voxel_data is not None:
                        material_grid = self.classify_voxel_materials(self.voxel_data)
                        if material_grid is not None:
                            dve_data = self.export_to_divine_voxel_format(self.voxel_data, material_grid)
                            if self.save_voxel_data(dve_data):
                                print("💾 Voxel data exported for Divine Voxel Engine")
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_voxel_integration(self):
        """Run voxel system integration"""
        print("="*60)
        print("🎯 VOXEL SYSTEM INTEGRATION")
        print("="*60)
        print(f"🧊 Voxel Size: {self.voxel_size*1000:.1f}mm")
        print("🎮 Divine Voxel Engine integration")
        print("🎨 Material classification: Sand, Water, Dirt, Stone, Grass")
        print("="*60)
        
        if not self.initialize_kinect():
            print("❌ Kinect initialization failed")
            return False
        
        self.display_voxel_system()
        return True

def main():
    """Run voxel system integration"""
    system = VoxelSystemIntegration()
    
    try:
        success = system.run_voxel_integration()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Voxel integration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
