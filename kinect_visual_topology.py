#!/usr/bin/env python3
"""
Kinect Visual to Topology Map
Shows what Kinect sees and applies it to topology
"""

import cv2
import numpy as np
import time
import sys

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

def kinect_visual_topology():
    """Show Kinect visual data and apply to topology map"""
    
    if not KINECT_AVAILABLE:
        print("❌ Cannot run without Kinect")
        return
    
    print("🎮 KINECT VISUAL → TOPOLOGY MAP")
    print("="*50)
    
    # Initialize Kinect
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
        
        print("✅ Kinect initialized")
        
    except Exception as e:
        print(f"❌ Kinect init failed: {e}")
        return
    
    # Create windows
    cv2.namedWindow('KINECT DEPTH VIEW', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('KINECT RGB VIEW', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('TOPOLOGY MAP', cv2.WINDOW_AUTOSIZE)
    
    print("🎮 Press 'q' to exit")
    
    try:
        while True:
            # Get Kinect data
            try:
                depth_data, _ = freenect.sync_get_depth()
                rgb_data, _ = freenect.sync_get_video()
                
                if depth_data is not None:
                    # Show what Kinect depth sees
                    depth_visual = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX)
                    depth_colored = cv2.applyColorMap(depth_visual.astype(np.uint8), cv2.COLORMAP_JET)
                    
                    # Add info
                    cv2.putText(depth_colored, "KINECT DEPTH VIEW", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(depth_colored, f"Shape: {depth_data.shape}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(depth_colored, f"Range: {depth_data.min()}-{depth_data.max()}", (10, 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('KINECT DEPTH VIEW', depth_colored)
                    
                    # Create topology map from depth
                    topology_map = create_topology_from_depth(depth_data)
                    cv2.imshow('TOPOLOGY MAP', topology_map)
                
                if rgb_data is not None:
                    # Show what Kinect RGB sees
                    rgb_visual = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                    
                    # Add info
                    cv2.putText(rgb_visual, "KINECT RGB VIEW", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(rgb_visual, f"Shape: {rgb_data.shape}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('KINECT RGB VIEW', rgb_visual)
                
            except Exception as e:
                print(f"Capture error: {e}")
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            time.sleep(0.033)  # ~30 FPS
    
    finally:
        cv2.destroyAllWindows()
        try:
            freenect.stop_depth(0)
            freenect.stop_video(0)
        except:
            pass

def create_topology_from_depth(depth_data):
    """Create topology map from Kinect depth data"""
    
    # Convert depth to topology visualization
    h, w = depth_data.shape
    
    # Create topology map
    topology = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Normalize depth for topology
    depth_norm = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX)
    
    # Create height-based coloring
    # Blue = low/water, Green = medium, Red = high
    for i in range(h):
        for j in range(w):
            height = depth_norm[i, j]
            
            if height < 85:  # Low areas (water)
                topology[i, j] = [255, 100, 0]  # Blue
            elif height < 170:  # Medium areas (land)
                topology[i, j] = [0, 255, 100]  # Green
            else:  # High areas (mountains)
                topology[i, j] = [0, 100, 255]  # Red
    
    # Add contour lines
    contours = cv2.Canny(depth_norm.astype(np.uint8), 50, 150)
    topology[contours > 0] = [255, 255, 255]  # White contour lines
    
    # Add topology info
    cv2.putText(topology, "TOPOLOGY MAP", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(topology, "Blue=Low, Green=Mid, Red=High", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return topology

if __name__ == "__main__":
    kinect_visual_topology()
