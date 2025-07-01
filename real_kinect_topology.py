#!/usr/bin/env python3
"""
Real Kinect Visual to Topology - Using Magic-Sand's proven method
"""

import cv2
import numpy as np
import time
import sys

try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False

def force_real_kinect_data():
    """Force Kinect to provide real environmental data using Magic-Sand method"""
    if not KINECT_AVAILABLE:
        return False
    
    try:
        # Complete reset like Magic-Sand does
        freenect.stop_depth(0)
        freenect.stop_video(0)
        time.sleep(2.0)
        
        # Magic-Sand initialization sequence
        freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
        freenect.set_video_mode(0, freenect.VIDEO_RGB)
        
        # Start depth first
        freenect.start_depth(0)
        time.sleep(1.0)
        
        # Start video
        freenect.start_video(0)
        time.sleep(1.0)
        
        # Test for real data
        for attempt in range(10):
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            if depth_data is not None and rgb_data is not None:
                # Check for real variation
                depth_std = np.std(depth_data)
                rgb_std = np.std(rgb_data)
                
                print(f"Attempt {attempt+1}: Depth std={depth_std:.1f}, RGB std={rgb_std:.1f}")
                
                if depth_std > 100 and rgb_std > 30:
                    print("✅ Real Kinect data detected!")
                    return True
            
            time.sleep(0.5)
        
        print("⚠️ May still be test patterns")
        return True
        
    except Exception as e:
        print(f"❌ Kinect initialization failed: {e}")
        return False

def create_topology_map(depth_data):
    """Convert real depth data to topology map"""
    if depth_data is None:
        return None
    
    h, w = depth_data.shape
    
    # Create topology map
    topology = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Get depth range
    valid_depths = depth_data[depth_data > 0]
    if len(valid_depths) == 0:
        return topology
    
    min_depth = np.min(valid_depths)
    max_depth = np.max(valid_depths)
    depth_range = max_depth - min_depth
    
    if depth_range == 0:
        return topology
    
    # Create height-based topology coloring
    for i in range(h):
        for j in range(w):
            depth = depth_data[i, j]
            
            if depth == 0:
                topology[i, j] = [0, 0, 0]  # Black for no data
            else:
                # Normalize depth to 0-1
                normalized = (depth - min_depth) / depth_range
                
                # Create topology colors
                if normalized < 0.3:  # Water/low areas
                    topology[i, j] = [255, 100, 0]  # Blue
                elif normalized < 0.7:  # Land/medium areas  
                    topology[i, j] = [0, 200, 100]  # Green
                else:  # Mountains/high areas
                    topology[i, j] = [0, 100, 255]  # Red
    
    # Add contour lines
    depth_norm = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX)
    edges = cv2.Canny(depth_norm.astype(np.uint8), 30, 100)
    topology[edges > 0] = [255, 255, 255]  # White contours
    
    return topology

def run_kinect_topology():
    """Run Kinect visual to topology system"""
    print("🎯 REAL KINECT VISUAL → TOPOLOGY MAP")
    print("="*50)
    
    if not KINECT_AVAILABLE:
        print("❌ Kinect not available")
        return
    
    # Force real Kinect data
    if not force_real_kinect_data():
        print("❌ Failed to get real Kinect data")
        return
    
    # Create windows
    cv2.namedWindow('KINECT DEPTH', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('KINECT RGB', cv2.WINDOW_AUTOSIZE)  
    cv2.namedWindow('TOPOLOGY MAP', cv2.WINDOW_AUTOSIZE)
    
    print("🎮 Showing real Kinect data → topology")
    print("Press 'q' to exit")
    
    try:
        while True:
            # Get Kinect data
            depth_data, _ = freenect.sync_get_depth()
            rgb_data, _ = freenect.sync_get_video()
            
            # Display what Kinect sees
            if depth_data is not None:
                # Show depth view
                depth_visual = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX)
                depth_colored = cv2.applyColorMap(depth_visual.astype(np.uint8), cv2.COLORMAP_JET)
                
                # Add real-time info
                depth_std = np.std(depth_data)
                valid_pixels = np.sum(depth_data > 0)
                
                cv2.putText(depth_colored, "KINECT DEPTH", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(depth_colored, f"Variation: {depth_std:.1f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(depth_colored, f"Valid pixels: {valid_pixels}", (10, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('KINECT DEPTH', depth_colored)
                
                # Create and show topology map
                topology_map = create_topology_map(depth_data)
                if topology_map is not None:
                    cv2.putText(topology_map, "TOPOLOGY MAP", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(topology_map, "Blue=Water, Green=Land, Red=Mountain", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
                    cv2.imshow('TOPOLOGY MAP', topology_map)
            
            if rgb_data is not None:
                # Show RGB view
                rgb_visual = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                
                rgb_std = np.std(rgb_data)
                cv2.putText(rgb_visual, "KINECT RGB", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(rgb_visual, f"Variation: {rgb_std:.1f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('KINECT RGB', rgb_visual)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            time.sleep(0.033)  # 30 FPS
    
    finally:
        cv2.destroyAllWindows()
        try:
            freenect.stop_depth(0)
            freenect.stop_video(0)
        except:
            pass

if __name__ == "__main__":
    run_kinect_topology()
