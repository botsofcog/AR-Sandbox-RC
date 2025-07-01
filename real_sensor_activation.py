#!/usr/bin/env python3
"""
Real Sensor Activation - Force Kinect out of demo mode into real sensing
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

class RealSensorActivation:
    """
    Force Kinect out of demo/test pattern mode into real sensor mode
    """
    
    def __init__(self):
        self.real_sensor_active = False
        self.demo_mode_detected = False
        
    def detect_demo_mode(self, depth_frame, rgb_frame):
        """Detect if Kinect is showing demo patterns instead of real data"""
        demo_indicators = []
        
        if depth_frame is not None:
            # Check for uniform/pattern depth data (demo mode)
            depth_std = np.std(depth_frame)
            depth_mean = np.mean(depth_frame)
            
            # Demo mode often has very uniform or patterned data
            if depth_std < 10:  # Very uniform depth
                demo_indicators.append("Uniform depth pattern")
            
            if depth_mean < 100 or depth_mean > 2000:  # Unrealistic depth values
                demo_indicators.append("Unrealistic depth values")
            
            # Check for geometric patterns (common in test mode)
            center_region = depth_frame[100:140, 140:180]
            if center_region.size > 0:
                center_std = np.std(center_region)
                if center_std < 5:  # Very uniform center region
                    demo_indicators.append("Uniform center region")
        
        if rgb_frame is not None:
            # Check for test patterns in RGB
            rgb_gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            
            # Check for gradient patterns (common test pattern)
            grad_x = cv2.Sobel(rgb_gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(rgb_gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # High gradient variance indicates test patterns
            if np.std(grad_x) > 50 and np.std(grad_y) > 50:
                demo_indicators.append("High gradient test pattern")
            
            # Check for color uniformity (another test pattern indicator)
            color_std = np.std(rgb_frame, axis=(0,1))
            if np.all(color_std < 20):  # Very uniform colors
                demo_indicators.append("Uniform RGB colors")
        
        self.demo_mode_detected = len(demo_indicators) > 0
        
        if demo_indicators:
            print(f"   🔍 Demo mode indicators: {demo_indicators}")
        
        return self.demo_mode_detected
    
    def force_real_sensor_mode(self):
        """Force Kinect into real sensor mode"""
        print("🔄 FORCING KINECT INTO REAL SENSOR MODE...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False
        
        try:
            # Method 1: Complete reset cycle
            print("   🔄 Method 1: Complete reset cycle...")
            
            # Stop everything
            try:
                freenect.stop_depth(0)
                freenect.stop_video(0)
                time.sleep(2.0)
                print("      ✅ Streams stopped")
            except:
                pass
            
            # Set specific modes to force real sensing
            try:
                # Set depth mode explicitly
                freenect.set_depth_mode(0, freenect.DEPTH_11BIT)
                time.sleep(0.5)
                
                # Set video mode explicitly  
                freenect.set_video_mode(0, freenect.VIDEO_RGB)
                time.sleep(0.5)
                
                print("      ✅ Sensor modes set")
            except Exception as e:
                print(f"      ⚠️ Mode setting: {e}")
            
            # Start with longer delays
            freenect.start_depth(0)
            time.sleep(3.0)  # Longer delay for sensor stabilization
            
            freenect.start_video(0)
            time.sleep(3.0)  # Longer delay for sensor stabilization
            
            print("      ✅ Streams restarted with delays")
            
            # Method 2: Clear buffer extensively
            print("   🔄 Method 2: Extensive buffer clearing...")
            
            for i in range(20):  # More clearing cycles
                try:
                    depth_data, _ = freenect.sync_get_depth()
                    rgb_data, _ = freenect.sync_get_video()
                    
                    if i % 5 == 0:
                        print(f"      Clearing cycle {i+1}/20...")
                    
                    time.sleep(0.3)  # Longer delays between reads
                except:
                    pass
            
            print("      ✅ Buffer clearing complete")
            
            # Method 3: Test for real data
            print("   🧪 Method 3: Testing for real sensor data...")
            
            real_data_count = 0
            for test in range(10):
                try:
                    depth_data, _ = freenect.sync_get_depth()
                    rgb_data, _ = freenect.sync_get_video()
                    
                    if not self.detect_demo_mode(depth_data, rgb_data):
                        real_data_count += 1
                        print(f"      ✅ Real data detected in test {test+1}")
                    else:
                        print(f"      ⚠️ Demo mode detected in test {test+1}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"      ❌ Test {test+1} failed: {e}")
            
            success_rate = real_data_count / 10
            print(f"   📊 Real sensor success rate: {success_rate*100:.0f}%")
            
            if success_rate >= 0.7:  # 70% real data
                self.real_sensor_active = True
                print("   🎉 REAL SENSOR MODE ACTIVATED!")
                return True
            else:
                print("   ⚠️ Still detecting demo patterns")
                return False
                
        except Exception as e:
            print(f"   ❌ Real sensor activation failed: {e}")
            return False
    
    def test_real_vs_demo_detection(self):
        """Test and display real vs demo data detection"""
        print("\n🧪 TESTING REAL VS DEMO DATA DETECTION...")
        
        # Create display windows
        cv2.namedWindow('Depth Analysis', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('RGB Analysis', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Detection Status', cv2.WINDOW_AUTOSIZE)
        
        try:
            for frame_num in range(30):
                print(f"   Frame {frame_num + 1}/30...")
                
                try:
                    # Get sensor data
                    depth_data, _ = freenect.sync_get_depth()
                    rgb_data, _ = freenect.sync_get_video()
                    
                    # Analyze data
                    is_demo = self.detect_demo_mode(depth_data, rgb_data)
                    
                    # Create analysis displays
                    if depth_data is not None:
                        # Depth analysis
                        depth_display = (depth_data / depth_data.max() * 255).astype(np.uint8)
                        depth_colored = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                        
                        # Add analysis overlay
                        depth_std = np.std(depth_data)
                        depth_mean = np.mean(depth_data)
                        
                        cv2.putText(depth_colored, f"Std: {depth_std:.1f}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(depth_colored, f"Mean: {depth_mean:.1f}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        cv2.imshow('Depth Analysis', depth_colored)
                    
                    if rgb_data is not None:
                        # RGB analysis
                        rgb_bgr = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
                        
                        # Add analysis overlay
                        color_std = np.std(rgb_data, axis=(0,1))
                        
                        cv2.putText(rgb_bgr, f"R-Std: {color_std[0]:.1f}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.putText(rgb_bgr, f"G-Std: {color_std[1]:.1f}", 
                                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.putText(rgb_bgr, f"B-Std: {color_std[2]:.1f}", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        
                        cv2.imshow('RGB Analysis', rgb_bgr)
                    
                    # Status display
                    status_img = np.zeros((200, 400, 3), dtype=np.uint8)
                    
                    status_text = "DEMO MODE" if is_demo else "REAL SENSOR"
                    status_color = (0, 0, 255) if is_demo else (0, 255, 0)
                    
                    cv2.putText(status_img, f"Status: {status_text}", 
                               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
                    cv2.putText(status_img, f"Frame: {frame_num + 1}/30", 
                               (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    if is_demo:
                        cv2.putText(status_img, "Need real sensor activation!", 
                                   (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    else:
                        cv2.putText(status_img, "Real sensor data detected!", 
                                   (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    cv2.imshow('Detection Status', status_img)
                    
                    # Check for exit
                    key = cv2.waitKey(100) & 0xFF
                    if key == ord('q'):
                        print("   🛑 User requested exit")
                        break
                    
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"   ❌ Frame {frame_num + 1} error: {e}")
        
        finally:
            cv2.destroyAllWindows()
    
    def run_complete_real_sensor_test(self):
        """Run complete real sensor activation and testing"""
        print("="*60)
        print("🔄 REAL SENSOR ACTIVATION - DEMO MODE → REAL MODE")
        print("="*60)
        print("🎯 Goal: Force Kinect from demo/test patterns to real sensor data")
        print("Press 'q' in any window to exit early")
        print("="*60)
        
        # Step 1: Force real sensor mode
        activation_success = self.force_real_sensor_mode()
        
        # Step 2: Test detection
        self.test_real_vs_demo_detection()
        
        # Final report
        print(f"\n📊 REAL SENSOR ACTIVATION RESULTS:")
        print(f"   Activation attempt: {'✅ SUCCESS' if activation_success else '❌ FAILED'}")
        print(f"   Real sensor active: {'✅ YES' if self.real_sensor_active else '❌ NO'}")
        print(f"   Demo mode detected: {'⚠️ YES' if self.demo_mode_detected else '✅ NO'}")
        
        if self.real_sensor_active:
            print(f"\n🎉 SUCCESS: Kinect is providing real sensor data!")
            print(f"   🎯 Ready for AR sandbox integration")
            print(f"   📷 Depth and RGB sensors working properly")
        else:
            print(f"\n⚠️ ISSUE: Kinect may still be in demo mode")
            print(f"   💡 Try covering/uncovering the sensors")
            print(f"   🔄 Try moving objects in front of Kinect")
            print(f"   🔌 Try unplugging/replugging USB")
        
        return self.real_sensor_active

def main():
    """Run real sensor activation"""
    activator = RealSensorActivation()
    
    try:
        success = activator.run_complete_real_sensor_test()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Real sensor activation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
