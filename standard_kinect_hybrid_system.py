#!/usr/bin/env python3
"""
🎯 Standard Kinect + Hybrid RGB AR Sandbox System
Uses standard Kinect libraries for real depth + RGB simulation for 3-4 camera fusion
"""

import cv2
import numpy as np
import time
import threading
import logging
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata

# Standard Kinect libraries that everyone uses
try:
    import freenect  # Standard Linux/cross-platform Kinect library
    FREENECT_AVAILABLE = True
except ImportError:
    FREENECT_AVAILABLE = False

try:
    from pykinect2 import PyKinectV2, PyKinectRuntime  # Standard Windows Kinect library
    PYKINECT_AVAILABLE = True
except ImportError:
    PYKINECT_AVAILABLE = False

try:
    import pyrealsense2 as rs  # Standard Intel RealSense (alternative depth sensor)
    REALSENSE_AVAILABLE = True
except ImportError:
    REALSENSE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandardKinectHybridSystem:
    """
    Standard Kinect + Hybrid RGB system for AR sandbox topology
    """
    
    def __init__(self):
        print("🎯 Standard Kinect + Hybrid RGB AR Sandbox")
        print("=" * 50)
        
        # Kinect depth system (REAL depth data)
        self.kinect_depth_method = None
        self.kinect_runtime = None
        self.kinect_device = None
        
        # RGB camera system (for hybrid enhancement)
        self.webcam1 = None  # Logitech high-res
        self.webcam2 = None  # Secondary webcam
        self.kinect_rgb = None  # Kinect RGB camera
        
        # Topology and mapping
        self.real_depth_frame = None
        self.hybrid_depth_map = None
        self.topology_grid = None
        self.height_map = None
        
        # System parameters
        self.depth_width = 640
        self.depth_height = 480
        self.depth_range = (500, 4000)  # mm
        self.running = False
        
        # Initialize systems
        self.init_standard_kinect()
        self.init_rgb_cameras()
        
    def init_standard_kinect(self):
        """Initialize standard Kinect libraries for REAL depth data"""
        print("📡 Initializing Standard Kinect Libraries...")
        
        # Method 1: Try freenect (most common cross-platform)
        if FREENECT_AVAILABLE:
            try:
                print("  🔄 Testing freenect (libfreenect)...")
                # Test if Kinect is connected
                ctx = freenect.init()
                if freenect.num_devices(ctx) > 0:
                    print("  ✅ Kinect v1 detected via freenect")
                    self.kinect_depth_method = "freenect"
                    freenect.shutdown(ctx)
                    return
                else:
                    print("  ⚠️ No Kinect devices found via freenect")
                    freenect.shutdown(ctx)
            except Exception as e:
                print(f"  ❌ Freenect error: {e}")
        
        # Method 2: Try PyKinect2 (Windows standard)
        if PYKINECT_AVAILABLE:
            try:
                print("  🔄 Testing PyKinect2 (Windows)...")
                self.kinect_runtime = PyKinectRuntime.PyKinectRuntime(
                    PyKinectV2.FrameSourceTypes_Depth | PyKinectV2.FrameSourceTypes_Color
                )
                if self.kinect_runtime._kinect:
                    print("  ✅ Kinect v2 detected via PyKinect2")
                    self.kinect_depth_method = "pykinect2"
                    return
                else:
                    print("  ⚠️ No Kinect v2 found via PyKinect2")
            except Exception as e:
                print(f"  ❌ PyKinect2 error: {e}")
        
        # Method 3: Try RealSense (alternative depth sensor)
        if REALSENSE_AVAILABLE:
            try:
                print("  🔄 Testing RealSense...")
                pipeline = rs.pipeline()
                config = rs.config()
                config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
                
                profile = pipeline.start(config)
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                
                if depth_frame:
                    print("  ✅ RealSense depth sensor detected")
                    self.kinect_depth_method = "realsense"
                    self.realsense_pipeline = pipeline
                    return
                    
                pipeline.stop()
            except Exception as e:
                print(f"  ❌ RealSense error: {e}")
        
        print("  ❌ No standard depth sensors found")
        self.kinect_depth_method = None
        
    def init_rgb_cameras(self):
        """Initialize RGB cameras for hybrid enhancement"""
        print("📹 Initializing RGB Cameras for Hybrid Enhancement...")
        
        camera_count = 0
        
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"  📷 Camera {i}: {width}x{height}")
                        
                        # Assign cameras by resolution and capability
                        if width >= 1920 and self.webcam1 is None:
                            # High-res camera (likely Logitech)
                            self.webcam1 = cap
                            print(f"    ✅ Webcam 1 (High-res): Camera {i}")
                            camera_count += 1
                        elif width >= 1280 and self.webcam1 is None:
                            # Medium-res camera (backup Logitech)
                            self.webcam1 = cap
                            print(f"    ✅ Webcam 1 (Med-res): Camera {i}")
                            camera_count += 1
                        elif width == 640 and height == 480:
                            if self.kinect_rgb is None:
                                # Likely Kinect RGB
                                self.kinect_rgb = cap
                                print(f"    ✅ Kinect RGB: Camera {i}")
                                camera_count += 1
                            elif self.webcam2 is None:
                                # Secondary 640x480 camera
                                self.webcam2 = cap
                                print(f"    ✅ Webcam 2: Camera {i}")
                                camera_count += 1
                            else:
                                cap.release()
                        else:
                            cap.release()
                    else:
                        cap.release()
            except Exception as e:
                print(f"  ❌ Camera {i} error: {e}")
        
        print(f"  📊 RGB cameras initialized: {camera_count}")
        
    def get_real_kinect_depth(self):
        """Get REAL depth data from standard Kinect libraries"""
        if self.kinect_depth_method == "freenect":
            try:
                # Standard freenect approach
                depth_array, timestamp = freenect.sync_get_depth()
                # Flip horizontally to match camera orientation
                depth_array = np.fliplr(depth_array)
                print(f"📡 Freenect depth: {depth_array.shape}, range: {depth_array.min()}-{depth_array.max()}")
                return depth_array
            except Exception as e:
                logger.error(f"Freenect depth error: {e}")
                return None
                
        elif self.kinect_depth_method == "pykinect2":
            try:
                # Standard PyKinect2 approach
                if self.kinect_runtime.has_new_depth_frame():
                    depth_frame = self.kinect_runtime.get_last_depth_frame()
                    # Reshape to proper dimensions
                    depth_array = depth_frame.reshape((424, 512)).astype(np.uint16)
                    # Resize to standard 640x480
                    depth_resized = cv2.resize(depth_array, (640, 480))
                    print(f"📡 PyKinect2 depth: {depth_resized.shape}, range: {depth_resized.min()}-{depth_resized.max()}")
                    return depth_resized
                return None
            except Exception as e:
                logger.error(f"PyKinect2 depth error: {e}")
                return None
                
        elif self.kinect_depth_method == "realsense":
            try:
                # Standard RealSense approach
                frames = self.realsense_pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                if depth_frame:
                    depth_array = np.asanyarray(depth_frame.get_data())
                    print(f"📡 RealSense depth: {depth_array.shape}, range: {depth_array.min()}-{depth_array.max()}")
                    return depth_array
                return None
            except Exception as e:
                logger.error(f"RealSense depth error: {e}")
                return None
        
        return None
        
    def get_rgb_frames(self):
        """Get RGB frames from all cameras"""
        rgb_frames = {}
        
        # Kinect RGB
        if self.kinect_rgb:
            ret, frame = self.kinect_rgb.read()
            if ret:
                rgb_frames['kinect_rgb'] = frame
                
        # High-res webcam
        if self.webcam1:
            ret, frame = self.webcam1.read()
            if ret:
                # Resize to standard resolution for processing
                frame_resized = cv2.resize(frame, (640, 480))
                rgb_frames['webcam1_hires'] = frame_resized
                
        # Secondary webcam
        if self.webcam2:
            ret, frame = self.webcam2.read()
            if ret:
                rgb_frames['webcam2'] = frame
                
        return rgb_frames
        
    def create_hybrid_depth_enhancement(self, real_depth, rgb_frames):
        """Create hybrid depth map using real Kinect + RGB enhancement"""
        if real_depth is None:
            return None
            
        # Start with real depth as base
        hybrid_depth = real_depth.copy().astype(np.float32)
        
        # Enhance with RGB-based depth estimation
        for camera_name, rgb_frame in rgb_frames.items():
            try:
                # Create depth-like data from RGB
                rgb_depth = self.rgb_to_depth_estimation(rgb_frame)
                
                # Resize to match real depth
                if rgb_depth.shape != hybrid_depth.shape:
                    rgb_depth = cv2.resize(rgb_depth, (hybrid_depth.shape[1], hybrid_depth.shape[0]))
                
                # Blend with real depth (real depth has priority)
                weight = 0.1  # Low weight for RGB enhancement
                mask = (real_depth > 0) & (real_depth < 4000)  # Valid depth mask
                
                # Only enhance where we have valid real depth
                hybrid_depth[mask] = (
                    hybrid_depth[mask] * (1 - weight) + 
                    rgb_depth[mask] * weight
                )
                
                print(f"  🔄 Enhanced with {camera_name}")
                
            except Exception as e:
                logger.error(f"RGB enhancement error for {camera_name}: {e}")
                
        return hybrid_depth.astype(np.uint16)
        
    def rgb_to_depth_estimation(self, rgb_frame):
        """Convert RGB frame to depth-like estimation"""
        # Convert to grayscale
        gray = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection for depth cues
        edges = cv2.Canny(gray, 50, 150)
        
        # Create depth from brightness (darker = closer in many lighting conditions)
        depth_from_brightness = 255 - gray
        
        # Enhance edges (edges often indicate depth changes)
        depth_enhanced = depth_from_brightness.copy()
        depth_enhanced[edges > 0] = depth_enhanced[edges > 0] * 1.2
        
        # Apply Gaussian blur for smoothness
        depth_smooth = gaussian_filter(depth_enhanced, sigma=2)
        
        # Scale to depth range
        depth_scaled = (depth_smooth / 255.0) * (self.depth_range[1] - self.depth_range[0]) + self.depth_range[0]
        
        return depth_scaled.astype(np.float32)
        
    def create_topology_from_hybrid_depth(self, hybrid_depth):
        """Create topology map from hybrid depth data"""
        if hybrid_depth is None:
            return None
            
        # Apply filters
        filtered_depth = gaussian_filter(hybrid_depth, sigma=1.5)
        
        # Clip to valid range
        clipped_depth = np.clip(filtered_depth, self.depth_range[0], self.depth_range[1])
        
        # Convert depth to height (invert)
        height_map = self.depth_range[1] - clipped_depth
        
        # Normalize to 0-1 range
        height_normalized = (height_map - height_map.min()) / (height_map.max() - height_map.min())
        
        return height_normalized
        
    def run_hybrid_ar_sandbox(self):
        """Run the hybrid AR sandbox system"""
        print("\n🚀 Starting Standard Kinect + Hybrid RGB AR Sandbox...")
        print("Press 'q' to quit, 's' to save, 'r' to reset")
        
        if not self.kinect_depth_method:
            print("❌ No depth sensor available!")
            return
            
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                # Get REAL depth data from standard Kinect
                real_depth = self.get_real_kinect_depth()
                
                # Get RGB frames from all cameras
                rgb_frames = self.get_rgb_frames()
                
                # Create hybrid depth enhancement
                hybrid_depth = self.create_hybrid_depth_enhancement(real_depth, rgb_frames)
                
                # Create topology
                topology = self.create_topology_from_hybrid_depth(hybrid_depth)
                
                # Display results
                self.display_hybrid_sandbox(real_depth, hybrid_depth, topology, rgb_frames)
                
                # Update stats
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"📊 FPS: {fps:.1f} | Depth method: {self.kinect_depth_method} | RGB cameras: {len(rgb_frames)}")
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_data(real_depth, hybrid_depth, topology)
                elif key == ord('r'):
                    print("🔄 Resetting system...")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(0.1)
                
        self.cleanup()
        
    def display_hybrid_sandbox(self, real_depth, hybrid_depth, topology, rgb_frames):
        """Display the hybrid AR sandbox visualization"""
        # Display real depth
        if real_depth is not None:
            depth_vis = cv2.applyColorMap(
                (np.clip(real_depth, 0, 4000) / 4000 * 255).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            cv2.putText(depth_vis, f"REAL DEPTH ({self.kinect_depth_method})", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('Real Kinect Depth', depth_vis)
        
        # Display hybrid depth
        if hybrid_depth is not None:
            hybrid_vis = cv2.applyColorMap(
                (np.clip(hybrid_depth, 0, 4000) / 4000 * 255).astype(np.uint8),
                cv2.COLORMAP_VIRIDIS
            )
            cv2.putText(hybrid_vis, "HYBRID DEPTH (Real + RGB)", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('Hybrid Enhanced Depth', hybrid_vis)
        
        # Display topology
        if topology is not None:
            topo_vis = cv2.applyColorMap(
                (topology * 255).astype(np.uint8),
                cv2.COLORMAP_TERRAIN
            )
            cv2.putText(topo_vis, "AR SANDBOX TOPOLOGY", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('AR Sandbox Topology', topo_vis)
        
        # Display RGB frames
        for name, frame in rgb_frames.items():
            cv2.imshow(f'RGB: {name}', frame)
            
    def save_data(self, real_depth, hybrid_depth, topology):
        """Save current data"""
        timestamp = int(time.time())
        
        if real_depth is not None:
            cv2.imwrite(f'real_depth_{timestamp}.png', 
                       (np.clip(real_depth, 0, 4000) / 4000 * 65535).astype(np.uint16))
        
        if hybrid_depth is not None:
            cv2.imwrite(f'hybrid_depth_{timestamp}.png',
                       (np.clip(hybrid_depth, 0, 4000) / 4000 * 65535).astype(np.uint16))
        
        if topology is not None:
            cv2.imwrite(f'topology_{timestamp}.png',
                       (topology * 255).astype(np.uint8))
        
        print(f"💾 Data saved with timestamp: {timestamp}")
        
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        if self.kinect_rgb:
            self.kinect_rgb.release()
        if self.webcam1:
            self.webcam1.release()
        if self.webcam2:
            self.webcam2.release()
            
        if self.kinect_depth_method == "realsense" and hasattr(self, 'realsense_pipeline'):
            self.realsense_pipeline.stop()
            
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

def main():
    """Main function"""
    system = StandardKinectHybridSystem()
    
    print(f"\n📊 System Status:")
    print(f"  Depth sensor: {system.kinect_depth_method or 'None'}")
    print(f"  Kinect RGB: {'✅' if system.kinect_rgb else '❌'}")
    print(f"  Webcam 1: {'✅' if system.webcam1 else '❌'}")
    print(f"  Webcam 2: {'✅' if system.webcam2 else '❌'}")
    
    if not system.kinect_depth_method:
        print("\n❌ No depth sensor available!")
        print("💡 Install: pip install freenect pykinect2 pyrealsense2")
        return
        
    print(f"\n🎮 Controls:")
    print(f"  'q' - Quit")
    print(f"  's' - Save data")
    print(f"  'r' - Reset")
    print(f"\n🚀 Starting in 3 seconds...")
    
    time.sleep(3)
    system.run_hybrid_ar_sandbox()

if __name__ == "__main__":
    main()
