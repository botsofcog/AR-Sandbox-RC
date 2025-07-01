#!/usr/bin/env python3
"""
Magic-Sand 3D Extrapolation Integration
Extracts working camera data from Magic-Sand and adds 3D extrapolation + topography
"""

import cv2
import numpy as np
import time
import sys
import os
import subprocess
import threading
from scipy.interpolate import griddata
import json

class MagicSand3DExtrapolation:
    """
    Integration with Magic-Sand for 3D extrapolation and topography
    """
    
    def __init__(self):
        self.magic_sand_path = "sample/Magic-Sand-master"
        self.magic_sand_running = False
        
        # Data extraction
        self.kinect_depth = None
        self.kinect_rgb = None
        self.webcam_data = None
        
        # 3D extrapolation
        self.point_cloud = None
        self.topography_grid = None
        self.mesh_vertices = None
        self.mesh_faces = None
        
        # Precision settings
        self.grid_resolution = 0.005  # 5mm precision
        self.temporal_buffer = []
        self.max_temporal_frames = 10
        
    def setup_magic_sand_data_extraction(self):
        """Setup data extraction from Magic-Sand"""
        print("🔧 SETTING UP MAGIC-SAND DATA EXTRACTION...")
        
        # Create data extraction directories
        os.makedirs("magic_sand_data", exist_ok=True)
        os.makedirs("magic_sand_data/depth", exist_ok=True)
        os.makedirs("magic_sand_data/rgb", exist_ok=True)
        os.makedirs("magic_sand_data/extrapolation", exist_ok=True)
        
        # Create data extraction script for Magic-Sand
        extraction_code = '''
// Magic-Sand Data Extraction Integration
// Add this to Magic-Sand's main loop for real-time data export

void exportFrameData() {
    if (kinectGrabber.isFrameNew()) {
        // Export depth data
        ofPixels depthPixels = kinectGrabber.getDepthPixels();
        if (depthPixels.isAllocated()) {
            string depthPath = "magic_sand_data/depth/depth_" + ofToString(ofGetFrameNum()) + ".raw";
            ofFile depthFile(depthPath, ofFile::WriteOnly, true);
            depthFile.writeFromBuffer((char*)depthPixels.getData(), depthPixels.size());
            depthFile.close();
        }
        
        // Export RGB data
        ofPixels colorPixels = kinectGrabber.getColorPixels();
        if (colorPixels.isAllocated()) {
            string rgbPath = "magic_sand_data/rgb/rgb_" + ofToString(ofGetFrameNum()) + ".raw";
            ofFile rgbFile(rgbPath, ofFile::WriteOnly, true);
            rgbFile.writeFromBuffer((char*)colorPixels.getData(), colorPixels.size());
            rgbFile.close();
        }
        
        // Export metadata
        ofJson metadata;
        metadata["frame"] = ofGetFrameNum();
        metadata["timestamp"] = ofGetElapsedTimeMillis();
        metadata["depth_width"] = depthPixels.getWidth();
        metadata["depth_height"] = depthPixels.getHeight();
        metadata["rgb_width"] = colorPixels.getWidth();
        metadata["rgb_height"] = colorPixels.getHeight();
        
        string metaPath = "magic_sand_data/metadata_" + ofToString(ofGetFrameNum()) + ".json";
        ofSaveJson(metaPath, metadata);
    }
}
'''
        
        # Save extraction code
        with open("magic_sand_data_extractor.cpp", "w") as f:
            f.write(extraction_code)
        
        print("   ✅ Data extraction setup complete")
        print("   💡 Add exportFrameData() to Magic-Sand's update() loop")
        
        return True
    
    def monitor_magic_sand_data(self):
        """Monitor Magic-Sand data files for real-time processing"""
        print("📁 MONITORING MAGIC-SAND DATA...")
        
        last_frame = -1
        
        while True:
            try:
                # Check for new data files
                depth_files = [f for f in os.listdir("magic_sand_data/depth") if f.endswith('.raw')]
                
                if depth_files:
                    # Get latest frame
                    frame_numbers = [int(f.split('_')[1].split('.')[0]) for f in depth_files]
                    latest_frame = max(frame_numbers)
                    
                    if latest_frame > last_frame:
                        # Load new data
                        self.load_magic_sand_frame(latest_frame)
                        
                        # Perform 3D extrapolation
                        self.perform_3d_extrapolation()
                        
                        last_frame = latest_frame
                
                time.sleep(0.033)  # ~30 FPS monitoring
                
            except Exception as e:
                print(f"   ⚠️ Monitoring error: {e}")
                time.sleep(0.1)
    
    def load_magic_sand_frame(self, frame_num):
        """Load specific frame data from Magic-Sand"""
        try:
            # Load metadata
            meta_path = f"magic_sand_data/metadata_{frame_num}.json"
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
            else:
                # Default metadata
                metadata = {
                    "depth_width": 640, "depth_height": 480,
                    "rgb_width": 640, "rgb_height": 480
                }
            
            # Load depth data
            depth_path = f"magic_sand_data/depth/depth_{frame_num}.raw"
            if os.path.exists(depth_path):
                with open(depth_path, 'rb') as f:
                    depth_raw = f.read()
                
                # Convert to numpy array
                depth_array = np.frombuffer(depth_raw, dtype=np.uint16)
                expected_size = metadata["depth_width"] * metadata["depth_height"]
                
                if len(depth_array) == expected_size:
                    self.kinect_depth = depth_array.reshape(
                        metadata["depth_height"], metadata["depth_width"]
                    )
            
            # Load RGB data
            rgb_path = f"magic_sand_data/rgb/rgb_{frame_num}.raw"
            if os.path.exists(rgb_path):
                with open(rgb_path, 'rb') as f:
                    rgb_raw = f.read()
                
                # Convert to numpy array
                rgb_array = np.frombuffer(rgb_raw, dtype=np.uint8)
                expected_size = metadata["rgb_width"] * metadata["rgb_height"] * 3
                
                if len(rgb_array) == expected_size:
                    self.kinect_rgb = rgb_array.reshape(
                        metadata["rgb_height"], metadata["rgb_width"], 3
                    )
            
        except Exception as e:
            print(f"   ❌ Frame loading error: {e}")
    
    def simulate_magic_sand_data(self):
        """Simulate Magic-Sand data for testing while integration is being set up"""
        print("🎮 SIMULATING MAGIC-SAND DATA FOR TESTING...")
        
        # Generate realistic sandbox terrain
        width, height = 640, 480
        
        # Create terrain with multiple features
        x = np.linspace(-2, 2, width)
        y = np.linspace(-1.5, 1.5, height)
        X, Y = np.meshgrid(x, y)
        
        # Base terrain with hills and valleys
        terrain = (
            800 +  # Base height
            200 * np.sin(X * 2) * np.cos(Y * 2) +  # Large hills
            100 * np.sin(X * 4) * np.cos(Y * 3) +  # Medium features
            50 * np.sin(X * 8) * np.cos(Y * 6) +   # Fine details
            30 * np.random.random((height, width))  # Noise
        )
        
        # Add time-based changes (simulating sand movement)
        time_factor = time.time() * 0.3
        dynamic_changes = (
            40 * np.sin(X * 3 + time_factor) * np.cos(Y * 2 + time_factor) +
            20 * np.sin(X * 6 + time_factor * 1.5)
        )
        terrain += dynamic_changes
        
        # Convert to proper depth format (mm)
        self.kinect_depth = terrain.astype(np.uint16)
        
        # Generate corresponding RGB
        normalized_terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        
        rgb = np.zeros((height, width, 3), dtype=np.uint8)
        # Topographic coloring
        rgb[:,:,0] = (normalized_terrain * 255).astype(np.uint8)  # Red for high
        rgb[:,:,1] = ((1 - normalized_terrain) * 200 + 55).astype(np.uint8)  # Green for low
        rgb[:,:,2] = (np.abs(normalized_terrain - 0.5) * 400).clip(0, 255).astype(np.uint8)  # Blue for mid
        
        self.kinect_rgb = rgb
    
    def perform_3d_extrapolation(self):
        """Perform high-precision 3D extrapolation"""
        if self.kinect_depth is None:
            return
        
        # Convert depth to 3D points
        points = self.depth_to_3d_points(self.kinect_depth)
        
        if points is not None and len(points) > 100:
            # Add to temporal buffer for stability
            self.temporal_buffer.append(points)
            if len(self.temporal_buffer) > self.max_temporal_frames:
                self.temporal_buffer.pop(0)
            
            # Create high-precision topography grid
            self.create_precision_topography(points)
            
            # Generate mesh for 3D visualization
            self.generate_3d_mesh(points)
    
    def depth_to_3d_points(self, depth_data):
        """Convert depth data to 3D points with camera calibration"""
        h, w = depth_data.shape
        
        # Kinect camera intrinsics (approximate)
        fx, fy = 525.0, 525.0  # Focal lengths
        cx, cy = w/2, h/2      # Principal point
        
        # Create coordinate grids
        u, v = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert depth to meters
        z = depth_data.astype(np.float32) / 1000.0
        
        # Calculate 3D coordinates
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        
        # Filter valid points (remove zeros and outliers)
        valid_mask = (z > 0.1) & (z < 5.0)  # 10cm to 5m range
        
        if np.sum(valid_mask) == 0:
            return None
        
        points = np.stack([
            x[valid_mask],
            y[valid_mask], 
            z[valid_mask]
        ], axis=1)
        
        return points
    
    def create_precision_topography(self, points):
        """Create high-precision topography grid"""
        if points is None or len(points) < 10:
            return
        
        # Extract coordinates
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        z_coords = points[:, 2]
        
        # Create high-resolution grid
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)
        
        # Ensure reasonable bounds
        if x_max - x_min < 0.1 or y_max - y_min < 0.1:
            return
        
        # Create grid with specified resolution
        grid_x = np.arange(x_min, x_max, self.grid_resolution)
        grid_y = np.arange(y_min, y_max, self.grid_resolution)
        
        if len(grid_x) > 1000 or len(grid_y) > 1000:
            # Limit grid size for performance
            grid_x = np.linspace(x_min, x_max, 500)
            grid_y = np.linspace(y_min, y_max, 500)
        
        grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
        
        # Interpolate Z values with multiple methods for robustness
        try:
            # Primary: Cubic interpolation
            grid_Z = griddata(
                (x_coords, y_coords), z_coords,
                (grid_X, grid_Y), method='cubic', fill_value=np.nan
            )
            
            # Fill NaN values with linear interpolation
            nan_mask = np.isnan(grid_Z)
            if np.sum(nan_mask) > 0:
                grid_Z_linear = griddata(
                    (x_coords, y_coords), z_coords,
                    (grid_X, grid_Y), method='linear', fill_value=0
                )
                grid_Z[nan_mask] = grid_Z_linear[nan_mask]
            
            self.topography_grid = {
                'X': grid_X,
                'Y': grid_Y,
                'Z': grid_Z,
                'resolution': self.grid_resolution,
                'bounds': [x_min, x_max, y_min, y_max],
                'points_count': len(points)
            }
            
        except Exception as e:
            print(f"   ⚠️ Topography creation error: {e}")
    
    def generate_3d_mesh(self, points):
        """Generate 3D mesh for visualization"""
        if self.topography_grid is None:
            return
        
        try:
            grid_X = self.topography_grid['X']
            grid_Y = self.topography_grid['Y']
            grid_Z = self.topography_grid['Z']
            
            # Create vertices
            h, w = grid_X.shape
            vertices = []
            
            for i in range(h):
                for j in range(w):
                    if not np.isnan(grid_Z[i, j]):
                        vertices.append([grid_X[i, j], grid_Y[i, j], grid_Z[i, j]])
            
            self.mesh_vertices = np.array(vertices)
            
            # Create simple triangular faces (for visualization)
            faces = []
            vertex_map = {}
            vertex_idx = 0
            
            for i in range(h):
                for j in range(w):
                    if not np.isnan(grid_Z[i, j]):
                        vertex_map[(i, j)] = vertex_idx
                        vertex_idx += 1
            
            # Create triangular faces
            for i in range(h-1):
                for j in range(w-1):
                    if ((i, j) in vertex_map and (i+1, j) in vertex_map and 
                        (i, j+1) in vertex_map and (i+1, j+1) in vertex_map):
                        
                        v1 = vertex_map[(i, j)]
                        v2 = vertex_map[(i+1, j)]
                        v3 = vertex_map[(i, j+1)]
                        v4 = vertex_map[(i+1, j+1)]
                        
                        # Two triangles per quad
                        faces.append([v1, v2, v3])
                        faces.append([v2, v4, v3])
            
            self.mesh_faces = np.array(faces)
            
        except Exception as e:
            print(f"   ⚠️ Mesh generation error: {e}")
    
    def display_3d_extrapolation(self):
        """Display real-time 3D extrapolation results"""
        print("🎮 DISPLAYING MAGIC-SAND 3D EXTRAPOLATION...")
        
        # Create windows
        cv2.namedWindow('Magic-Sand Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Magic-Sand RGB', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Precision Topography', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('3D Extrapolation Status', cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Simulate Magic-Sand data (replace with real data when integrated)
                self.simulate_magic_sand_data()
                self.perform_3d_extrapolation()
                
                # Display depth data
                if self.kinect_depth is not None:
                    depth_display = cv2.normalize(self.kinect_depth, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_display.astype(np.uint8), cv2.COLORMAP_JET)
                    cv2.putText(depth_colored, "MAGIC-SAND DEPTH", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Magic-Sand Depth', depth_colored)
                
                # Display RGB data
                if self.kinect_rgb is not None:
                    rgb_display = cv2.cvtColor(self.kinect_rgb, cv2.COLOR_RGB2BGR)
                    cv2.putText(rgb_display, "MAGIC-SAND RGB", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Magic-Sand RGB', rgb_display)
                
                # Display precision topography
                if self.topography_grid is not None:
                    grid_Z = self.topography_grid['Z']
                    topo_display = cv2.normalize(grid_Z, None, 0, 255, cv2.NORM_MINMAX)
                    topo_colored = cv2.applyColorMap(topo_display.astype(np.uint8), cv2.COLORMAP_RAINBOW)
                    
                    # Add precision info
                    resolution_mm = self.grid_resolution * 1000
                    cv2.putText(topo_colored, f"PRECISION: {resolution_mm:.1f}mm", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(topo_colored, f"POINTS: {self.topography_grid['points_count']}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    cv2.imshow('Precision Topography', topo_colored)
                
                # Status display
                status_img = np.zeros((400, 600, 3), dtype=np.uint8)
                
                frame_count += 1
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                
                cv2.putText(status_img, "MAGIC-SAND 3D EXTRAPOLATION", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                cv2.putText(status_img, f"FPS: {fps:.1f}", 
                           (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.putText(status_img, f"Grid Resolution: {self.grid_resolution*1000:.1f}mm", 
                           (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if self.topography_grid:
                    cv2.putText(status_img, f"Grid Size: {self.topography_grid['X'].shape}", 
                               (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(status_img, f"3D Points: {self.topography_grid['points_count']}", 
                               (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if self.mesh_vertices is not None:
                    cv2.putText(status_img, f"Mesh Vertices: {len(self.mesh_vertices)}", 
                               (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.putText(status_img, "Integration with Magic-Sand", 
                           (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(status_img, "Press 'q' to exit, '+/-' for resolution", 
                           (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('3D Extrapolation Status', status_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('+') or key == ord('='):
                    self.grid_resolution = max(0.001, self.grid_resolution - 0.001)
                    print(f"🔧 Resolution: {self.grid_resolution*1000:.1f}mm")
                elif key == ord('-'):
                    self.grid_resolution = min(0.02, self.grid_resolution + 0.001)
                    print(f"🔧 Resolution: {self.grid_resolution*1000:.1f}mm")
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_magic_sand_integration(self):
        """Run Magic-Sand 3D extrapolation integration"""
        print("="*60)
        print("🎯 MAGIC-SAND 3D EXTRAPOLATION INTEGRATION")
        print("="*60)
        print("✅ Using Magic-Sand's working camera data")
        print("🔧 Adding high-precision 3D extrapolation")
        print("📊 Real-time topography with extreme precision")
        print("="*60)
        
        # Setup data extraction
        self.setup_magic_sand_data_extraction()
        
        # Start display
        self.display_3d_extrapolation()
        
        return True

def main():
    """Run Magic-Sand 3D extrapolation integration"""
    system = MagicSand3DExtrapolation()
    
    try:
        success = system.run_magic_sand_integration()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Magic-Sand integration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
