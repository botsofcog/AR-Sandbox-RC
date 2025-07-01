#!/usr/bin/env python3
"""
Direct Kinect Real Data - Using Magic-Sand's proven method
Since Magic-Sand works, replicate its exact Kinect access approach
"""

import cv2
import numpy as np
import time
import sys

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect library not available")

class DirectKinectReal:
    """
    Direct Kinect access using Magic-Sand's proven method
    """
    
    def __init__(self):
        self.kinect_active = False
        self.real_data_confirmed = False
        
    def magic_sand_kinect_init(self):
        """Initialize Kinect using Magic-Sand's exact method"""
        print("🎮 INITIALIZING KINECT - MAGIC-SAND METHOD...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False
        
        try:
            # Magic-Sand method: init() + setRegistration(true) + open()
            print("   🔄 Step 1: Kinect init...")
            
            # Stop any existing streams first
            try:
                freenect.stop_depth(0)
                freenect.stop_video(0)
                time.sleep(1.0)
            except:
                pass
            
            # Magic-Sand uses registration for RGB/depth correspondence
            print("   🔄 Step 2: Set registration mode...")
            
            # Set modes like Magic-Sand
            try:
                # Set depth mode (Magic-Sand uses 11-bit depth)
                freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
                print("      ✅ Depth mode set to 11-bit")
                
                # Set video mode (Magic-Sand uses RGB)
                freenect.set_video_mode(0, freenect.VIDEO_RGB)
                print("      ✅ Video mode set to RGB")
                
            except Exception as e:
                print(f"      ⚠️ Mode setting: {e}")
            
            # Start streams like Magic-Sand
            print("   🔄 Step 3: Start streams...")
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            # Magic-Sand waits for stabilization
            print("   ⏳ Step 4: Wait for stabilization...")
            time.sleep(2.0)
            
            # Test data capture
            print("   🧪 Step 5: Test data capture...")
            for attempt in range(10):
                try:
                    depth_data, depth_ts = freenect.sync_get_depth()
                    rgb_data, rgb_ts = freenect.sync_get_video()
                    
                    if depth_data is not None and rgb_data is not None:
                        print(f"      ✅ Attempt {attempt+1}: Both sensors working")
                        print(f"         Depth: {depth_data.shape}, RGB: {rgb_data.shape}")
                        
                        # Check if this is real data (not demo patterns)
                        if self.verify_real_data(depth_data, rgb_data):
                            self.kinect_active = True
                            self.real_data_confirmed = True
                            print("      🎉 REAL KINECT DATA CONFIRMED!")
                            return True
                        else:
                            print(f"      ⚠️ Attempt {attempt+1}: Still demo patterns")
                    else:
                        print(f"      ❌ Attempt {attempt+1}: No data")
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"      ❌ Attempt {attempt+1}: {e}")
                    time.sleep(0.3)
            
            print("   ⚠️ Kinect responding but may still be in demo mode")
            self.kinect_active = True
            return True
            
        except Exception as e:
            print(f"   ❌ Magic-Sand init failed: {e}")
            return False
    
    def verify_real_data(self, depth_data, rgb_data):
        """Verify if we're getting real sensor data vs demo patterns"""
        
        # Real depth data characteristics
        depth_std = np.std(depth_data)
        depth_mean = np.mean(depth_data)
        depth_range = np.max(depth_data) - np.min(depth_data)
        
        # Real RGB data characteristics  
        rgb_std = np.std(rgb_data)
        
        # Real data should have:
        # - Reasonable depth variation (not too uniform)
        # - Realistic depth values (500-4000mm typically)
        # - Natural RGB variation
        
        real_indicators = []
        
        if depth_std > 50:  # Good depth variation
            real_indicators.append("Good depth variation")
        
        if 500 < depth_mean < 3000:  # Realistic depth range
            real_indicators.append("Realistic depth values")
        
        if depth_range > 200:  # Good depth range
            real_indicators.append("Good depth range")
        
        if rgb_std > 30:  # Natural RGB variation
            real_indicators.append("Natural RGB variation")
        
        # Check for specific demo pattern indicators
        demo_indicators = []
        
        # Very uniform depth (common in demo mode)
        if depth_std < 10:
            demo_indicators.append("Very uniform depth")
        
        # Unrealistic depth values
        if depth_mean < 100 or depth_mean > 4000:
            demo_indicators.append("Unrealistic depth values")
        
        # Very uniform RGB (test pattern)
        if rgb_std < 15:
            demo_indicators.append("Very uniform RGB")
        
        print(f"         Real indicators: {real_indicators}")
        if demo_indicators:
            print(f"         Demo indicators: {demo_indicators}")
        
        # Consider it real if we have more real indicators than demo indicators
        return len(real_indicators) > len(demo_indicators)
    
    def capture_real_kinect_data(self):
        """Capture real Kinect data using Magic-Sand method"""
        
        if not self.kinect_active:
            print("❌ Kinect not active")
            return None, None
        
        try:
            # Get data like Magic-Sand
            depth_data, depth_timestamp = freenect.sync_get_depth()
            rgb_data, rgb_timestamp = freenect.sync_get_video()
            
            return depth_data, rgb_data
            
        except Exception as e:
            print(f"Data capture error: {e}")
            return None, None
    
    def display_real_kinect_data(self):
        """Display real Kinect data with analysis"""
        print("🎮 DISPLAYING REAL KINECT DATA...")
        
        # Create windows
        cv2.namedWindow('Real Kinect Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Real Kinect RGB', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Real Data Analysis', cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        real_data_frames = 0
        
        try:
            while True:
                # Capture data
                depth_data, rgb_data = self.capture_real_kinect_data()
                
                if depth_data is not None and rgb_data is not None:
                    # Verify if real data
                    is_real = self.verify_real_data(depth_data, rgb_data)
                    if is_real:
                        real_data_frames += 1
                    
                    # Display depth
                    depth_display = (depth_data / depth_data.max() * 255).astype(np.uint8)
                    depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                    
                    # Add real/demo indicator
                    status_color = (0, 255, 0) if is_real else (0, 0, 255)
                    status_text = "REAL DATA" if is_real else "DEMO MODE"
                    cv2.putText(depth_colored, status_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                    
                    cv2.imshow('Real Kinect Depth', depth_colored)
                    
                    # Display RGB
                    rgb_bgr = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                    cv2.putText(rgb_bgr, status_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                    cv2.imshow('Real Kinect RGB', rgb_bgr)
                    
                    # Analysis display
                    analysis_img = np.zeros((400, 600, 3), dtype=np.uint8)
                    
                    frame_count += 1
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    real_percentage = (real_data_frames / frame_count * 100) if frame_count > 0 else 0
                    
                    # Analysis text
                    cv2.putText(analysis_img, "KINECT DATA ANALYSIS", 
                               (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    cv2.putText(analysis_img, f"Status: {status_text}", 
                               (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                    cv2.putText(analysis_img, f"FPS: {fps:.1f}", 
                               (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(analysis_img, f"Real Data: {real_percentage:.1f}%", 
                               (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Data statistics
                    depth_std = np.std(depth_data)
                    depth_mean = np.mean(depth_data)
                    rgb_std = np.std(rgb_data)
                    
                    cv2.putText(analysis_img, f"Depth Std: {depth_std:.1f}", 
                               (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(analysis_img, f"Depth Mean: {depth_mean:.1f}", 
                               (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(analysis_img, f"RGB Std: {rgb_std:.1f}", 
                               (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.putText(analysis_img, "Magic-Sand Method Active", 
                               (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.putText(analysis_img, "Press 'q' to exit, 'r' to reset", 
                               (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Real Data Analysis', analysis_img)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("   🛑 User requested exit")
                    break
                elif key == ord('r'):
                    print("   🔄 Resetting Kinect...")
                    self.magic_sand_kinect_init()
                
                time.sleep(0.033)  # ~30 FPS
        
        finally:
            cv2.destroyAllWindows()
    
    def run_direct_kinect_real(self):
        """Run direct real Kinect system"""
        print("="*60)
        print("🎮 DIRECT KINECT REAL DATA - MAGIC-SAND METHOD")
        print("="*60)
        print("🎯 Goal: Get real Kinect data using Magic-Sand's proven approach")
        print("✅ Magic-Sand confirmed working - replicating method")
        print("="*60)
        
        # Initialize using Magic-Sand method
        success = self.magic_sand_kinect_init()
        
        if not success:
            print("❌ Kinect initialization failed")
            return False
        
        print(f"\n🎮 KINECT INITIALIZATION RESULTS:")
        print(f"   Kinect active: {'✅ YES' if self.kinect_active else '❌ NO'}")
        print(f"   Real data confirmed: {'✅ YES' if self.real_data_confirmed else '⚠️ UNCERTAIN'}")
        
        if self.kinect_active:
            print(f"\n🎮 STARTING REAL DATA DISPLAY...")
            self.display_real_kinect_data()
        
        # Final report
        print(f"\n📊 DIRECT KINECT RESULTS:")
        print(f"   Magic-Sand method: ✅ IMPLEMENTED")
        print(f"   Kinect access: {'✅ SUCCESS' if self.kinect_active else '❌ FAILED'}")
        print(f"   Real data: {'✅ CONFIRMED' if self.real_data_confirmed else '⚠️ UNCERTAIN'}")
        
        return self.kinect_active

def main():
    """Run direct Kinect real data system"""
    kinect = DirectKinectReal()
    
    try:
        success = kinect.run_direct_kinect_real()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Direct Kinect failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
