#!/usr/bin/env python3
"""
Visual Kinect Test - Activate Kinect with visual display
Based on your observation that Kinect shows solid green during demo visuals
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

class VisualKinectTest:
    """
    Visual Kinect test that displays data to activate the sensor
    """
    
    def __init__(self):
        self.kinect_active = False
        self.depth_frame = None
        self.rgb_frame = None
        
    def activate_kinect_with_display(self):
        """Activate Kinect by starting visual display"""
        print("🎮 ACTIVATING KINECT WITH VISUAL DISPLAY...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False
        
        try:
            # Create display windows
            cv2.namedWindow('Kinect Depth', cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow('Kinect RGB', cv2.WINDOW_AUTOSIZE)
            
            print("   🔄 Starting Kinect streams...")
            
            # Start streams
            freenect.start_depth(0)
            time.sleep(0.5)
            freenect.start_video(0)
            time.sleep(0.5)
            
            print("   ⏳ Waiting for Kinect to activate...")
            
            # Try to get data with visual feedback
            for attempt in range(20):  # Try for 20 seconds
                try:
                    print(f"      Attempt {attempt + 1}/20...")
                    
                    # Get depth data
                    depth_data, depth_timestamp = freenect.sync_get_depth()
                    
                    # Get RGB data
                    rgb_data, rgb_timestamp = freenect.sync_get_video()
                    
                    if depth_data is not None:
                        print(f"      ✅ Depth data: {depth_data.shape}")
                        
                        # Convert depth to displayable format
                        depth_display = (depth_data / depth_data.max() * 255).astype(np.uint8)
                        depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                        
                        # Display depth
                        cv2.imshow('Kinect Depth', depth_colored)
                        
                        self.depth_frame = depth_data
                        self.kinect_active = True
                    else:
                        print(f"      ❌ Depth data: None")
                    
                    if rgb_data is not None:
                        print(f"      ✅ RGB data: {rgb_data.shape}")
                        
                        # Convert RGB to BGR for OpenCV
                        rgb_bgr = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                        
                        # Display RGB
                        cv2.imshow('Kinect RGB', rgb_bgr)
                        
                        self.rgb_frame = rgb_data
                    else:
                        print(f"      ❌ RGB data: None")
                    
                    # Check if both are working
                    if depth_data is not None and rgb_data is not None:
                        print(f"      🎉 BOTH KINECT SENSORS WORKING!")
                        
                        # Show success for a few seconds
                        for i in range(10):
                            cv2.waitKey(100)
                            print(f"         Success display {i+1}/10...")
                        
                        return True
                    
                    # Wait and check for exit
                    key = cv2.waitKey(100) & 0xFF
                    if key == ord('q'):
                        print("      🛑 User requested exit")
                        break
                        
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"      ❌ Attempt {attempt + 1} failed: {e}")
                    time.sleep(0.5)
            
            print("   ⚠️ Kinect activation attempts completed")
            return self.kinect_active
            
        except Exception as e:
            print(f"   ❌ Visual activation failed: {e}")
            return False
        finally:
            # Clean up
            try:
                cv2.destroyAllWindows()
                freenect.stop_depth(0)
                freenect.stop_video(0)
            except:
                pass
    
    def test_kinect_with_webcam_comparison(self):
        """Test Kinect alongside webcam for comparison"""
        print("\n📷 TESTING KINECT WITH WEBCAM COMPARISON...")
        
        # Try to open webcam
        webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        webcam_working = webcam.isOpened()
        
        if webcam_working:
            print("   ✅ Webcam available for comparison")
        else:
            print("   ❌ Webcam not available")
        
        # Create comparison windows
        if webcam_working:
            cv2.namedWindow('Webcam', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Kinect Status', cv2.WINDOW_AUTOSIZE)
        
        try:
            for frame_num in range(50):  # Test for 50 frames
                print(f"   Frame {frame_num + 1}/50...")
                
                # Get webcam frame
                if webcam_working:
                    ret, webcam_frame = webcam.read()
                    if ret:
                        cv2.imshow('Webcam', webcam_frame)
                
                # Try Kinect
                try:
                    depth_data, _ = freenect.sync_get_depth()
                    rgb_data, _ = freenect.sync_get_video()
                    
                    # Create status display
                    status_img = np.zeros((400, 600, 3), dtype=np.uint8)
                    
                    # Status text
                    depth_status = "✅ WORKING" if depth_data is not None else "❌ FAILED"
                    rgb_status = "✅ WORKING" if rgb_data is not None else "❌ FAILED"
                    
                    cv2.putText(status_img, f"Kinect Depth: {depth_status}", 
                               (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if depth_data is not None else (0, 0, 255), 2)
                    cv2.putText(status_img, f"Kinect RGB: {rgb_status}", 
                               (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if rgb_data is not None else (0, 0, 255), 2)
                    cv2.putText(status_img, f"Frame: {frame_num + 1}/50", 
                               (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    if depth_data is not None:
                        cv2.putText(status_img, f"Depth Shape: {depth_data.shape}", 
                                   (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if rgb_data is not None:
                        cv2.putText(status_img, f"RGB Shape: {rgb_data.shape}", 
                                   (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Kinect Status', status_img)
                    
                    # If we get data, show it
                    if depth_data is not None:
                        depth_display = (depth_data / depth_data.max() * 255).astype(np.uint8)
                        depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                        cv2.imshow('Kinect Depth Live', depth_colored)
                    
                    if rgb_data is not None:
                        rgb_bgr = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                        cv2.imshow('Kinect RGB Live', rgb_bgr)
                    
                except Exception as e:
                    print(f"      Kinect error: {e}")
                
                # Check for exit
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q'):
                    print("   🛑 User requested exit")
                    break
                
                time.sleep(0.1)
        
        finally:
            if webcam_working:
                webcam.release()
            cv2.destroyAllWindows()
    
    def run_complete_visual_test(self):
        """Run complete visual Kinect test"""
        print("="*60)
        print("🎮 VISUAL KINECT TEST - ACTIVATION WITH DISPLAY")
        print("="*60)
        print("💡 Based on your observation: Kinect shows solid green during demo visuals")
        print("🎯 Goal: Activate Kinect by displaying visual data")
        print("\nPress 'q' in any window to exit early")
        print("="*60)
        
        # Test 1: Visual activation
        success = self.activate_kinect_with_display()
        
        if success:
            print("\n🎉 SUCCESS: Kinect activated with visual display!")
            
            # Test 2: Comparison with webcam
            self.test_kinect_with_webcam_comparison()
        else:
            print("\n⚠️ Kinect activation incomplete - trying comparison test anyway...")
            self.test_kinect_with_webcam_comparison()
        
        # Final report
        print(f"\n📊 VISUAL TEST RESULTS:")
        print(f"   Kinect activation: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"   Depth sensor: {'✅ WORKING' if self.depth_frame is not None else '❌ FAILED'}")
        print(f"   RGB camera: {'✅ WORKING' if self.rgb_frame is not None else '❌ FAILED'}")
        
        if success:
            print(f"\n🎯 NEXT STEPS:")
            print(f"   1. Kinect responds to visual display")
            print(f"   2. Integrate with AR sandbox")
            print(f"   3. Use visual feedback loop")
            print(f"   4. Test with voxel system")
        
        return success

def main():
    """Run visual Kinect test"""
    test = VisualKinectTest()
    
    try:
        success = test.run_complete_visual_test()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Visual test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
