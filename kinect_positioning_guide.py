#!/usr/bin/env python3
"""
Kinect Positioning Guide
Helps position Kinect properly to see sandbox instead of test patterns/screens
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect available for positioning")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect not available")

class KinectPositioningGuide:
    """
    Guides user to position Kinect properly for sandbox viewing
    """
    
    def __init__(self):
        self.running = False
        
    def analyze_current_view(self):
        """Analyze what Kinect is currently seeing"""
        print("🔍 ANALYZING CURRENT KINECT VIEW...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available")
            return False
        
        try:
            # Capture current frames
            depth_frame = freenect.sync_get_depth()[0]
            rgb_frame = freenect.sync_get_video()[0]
            
            if depth_frame is None or rgb_frame is None:
                print("   ❌ Cannot capture frames")
                return False
            
            # Analyze depth view
            self.analyze_depth_view(depth_frame)
            
            # Analyze RGB view
            self.analyze_rgb_view(rgb_frame)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return False
    
    def analyze_depth_view(self, depth_frame):
        """Analyze depth view for positioning issues"""
        print("\n   🔍 DEPTH SENSOR ANALYSIS:")
        
        try:
            valid_pixels = np.sum(depth_frame > 0)
            total_pixels = depth_frame.size
            coverage = (valid_pixels / total_pixels) * 100
            
            if valid_pixels > 0:
                valid_depths = depth_frame[depth_frame > 0]
                min_depth = np.min(valid_depths)
                max_depth = np.max(valid_depths)
                mean_depth = np.mean(valid_depths)
                depth_range = max_depth - min_depth
                
                print(f"      Coverage: {coverage:.1f}%")
                print(f"      Distance range: {min_depth}mm to {max_depth}mm")
                print(f"      Average distance: {mean_depth:.0f}mm")
                print(f"      Depth variation: {depth_range}mm")
                
                # Positioning guidance based on depth
                if mean_depth < 500:
                    print("      ⚠️ TOO CLOSE - Move Kinect further back")
                elif mean_depth > 3000:
                    print("      ⚠️ TOO FAR - Move Kinect closer")
                else:
                    print("      ✅ Good distance")
                
                if depth_range < 100:
                    print("      ⚠️ VERY FLAT SURFACE - May be looking at wall/screen")
                    print("         💡 Point Kinect at sandbox with varied terrain")
                elif depth_range > 1000:
                    print("      ⚠️ VERY LARGE VARIATION - May be looking at room")
                    print("         💡 Focus Kinect on sandbox area only")
                else:
                    print("      ✅ Good depth variation for sandbox")
                
                if coverage < 50:
                    print("      ⚠️ LOW COVERAGE - Check for obstructions")
                else:
                    print("      ✅ Good coverage")
            else:
                print("      ❌ NO DEPTH DATA - Check Kinect connection")
                
        except Exception as e:
            print(f"      ❌ Depth analysis error: {e}")
    
    def analyze_rgb_view(self, rgb_frame):
        """Analyze RGB view for positioning issues"""
        print("\n   📷 RGB CAMERA ANALYSIS:")
        
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2HSV)
            
            # Basic image statistics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            print(f"      Brightness: {brightness:.1f} (optimal: 80-150)")
            print(f"      Contrast: {contrast:.1f} (optimal: >30)")
            
            # Check for screen/monitor patterns
            # Screens often have regular patterns and high gradients
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            avg_gradient = np.mean(gradient_magnitude)
            
            print(f"      Gradient intensity: {avg_gradient:.1f}")
            
            # Check for sand-like colors (browns, tans, beiges)
            sand_mask = (hsv[:,:,1] < 100) & (hsv[:,:,2] > 60) & (hsv[:,:,2] < 200)
            sand_percentage = np.sum(sand_mask) / sand_mask.size * 100
            
            print(f"      Sand-like colors: {sand_percentage:.1f}%")
            
            # Detect edges and patterns
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size * 100
            
            print(f"      Edge density: {edge_density:.1f}%")
            
            # Positioning guidance based on RGB
            if brightness < 50:
                print("      ⚠️ TOO DARK - Improve lighting or move closer")
            elif brightness > 200:
                print("      ⚠️ TOO BRIGHT - Reduce lighting or move away")
            else:
                print("      ✅ Good brightness")
            
            if avg_gradient > 30 and edge_density > 10:
                print("      ⚠️ HIGH PATTERN ACTIVITY - May be looking at screen/monitor")
                print("         💡 Point Kinect away from screens toward sandbox")
            elif sand_percentage > 20:
                print("      ✅ Good sand-like surface detected")
            elif edge_density < 2:
                print("      ⚠️ VERY UNIFORM SURFACE - May be looking at wall")
                print("         💡 Point Kinect at textured sandbox surface")
            else:
                print("      ✅ Good surface variation")
                
        except Exception as e:
            print(f"      ❌ RGB analysis error: {e}")
    
    def provide_positioning_guidance(self):
        """Provide specific positioning guidance"""
        print("\n" + "="*60)
        print("📐 KINECT POSITIONING GUIDANCE")
        print("="*60)
        
        print("\n🎯 OPTIMAL KINECT SETUP FOR AR SANDBOX:")
        
        print("\n1. 📍 POSITION:")
        print("   • Place Kinect 60-100cm away from sandbox")
        print("   • Mount at 45° angle looking DOWN at sandbox")
        print("   • Ensure clear line of sight to sandbox")
        print("   • NO obstructions between Kinect and sandbox")
        
        print("\n2. 🚫 AVOID POINTING AT:")
        print("   • Computer screens or monitors")
        print("   • TV screens or displays")
        print("   • Bright lights or windows")
        print("   • Flat walls or uniform surfaces")
        print("   • Other cameras or reflective surfaces")
        
        print("\n3. 🎯 POINT KINECT AT:")
        print("   • Physical sandbox with sand")
        print("   • Varied terrain with hills and valleys")
        print("   • Textured surfaces with depth variation")
        print("   • Well-lit but not overly bright areas")
        
        print("\n4. 💡 LIGHTING:")
        print("   • Ensure adequate room lighting")
        print("   • Avoid direct sunlight on sandbox")
        print("   • No bright lights pointing at Kinect")
        print("   • Even lighting across sandbox surface")
        
        print("\n5. 🔧 TROUBLESHOOTING:")
        print("   • If seeing 'test patterns': Reposition away from screens")
        print("   • If depth too flat: Add terrain variation to sandbox")
        print("   • If too bright/dark: Adjust lighting or distance")
        print("   • If no depth data: Check for obstructions")
    
    def live_positioning_helper(self):
        """Live positioning helper with real-time feedback"""
        print("\n🔴 LIVE POSITIONING HELPER")
        print("Press 'q' to quit, 'r' to refresh analysis")
        
        self.running = True
        
        while self.running:
            try:
                # Get current frames
                depth_frame = freenect.sync_get_depth()[0]
                rgb_frame = freenect.sync_get_video()[0]
                
                if depth_frame is not None and rgb_frame is not None:
                    # Create visualization
                    self.create_positioning_visualization(depth_frame, rgb_frame)
                
                # Check for user input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n🛑 Positioning helper stopped")
                    break
                elif key == ord('r'):
                    print("\n🔄 Refreshing analysis...")
                    self.analyze_current_view()
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"Live helper error: {e}")
                break
        
        cv2.destroyAllWindows()
        self.running = False
    
    def create_positioning_visualization(self, depth_frame, rgb_frame):
        """Create visual feedback for positioning"""
        try:
            # Convert depth to displayable format
            depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
            depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)
            
            # Convert RGB to BGR for OpenCV
            rgb_bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            # Add positioning guidance text
            valid_pixels = np.sum(depth_frame > 0)
            coverage = (valid_pixels / depth_frame.size) * 100
            
            if valid_pixels > 0:
                mean_depth = np.mean(depth_frame[depth_frame > 0])
                
                # Add text overlay
                cv2.putText(depth_colored, f"Coverage: {coverage:.1f}%", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(depth_colored, f"Distance: {mean_depth:.0f}mm", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Positioning guidance
                if mean_depth < 500:
                    cv2.putText(depth_colored, "TOO CLOSE - Move back", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                elif mean_depth > 3000:
                    cv2.putText(depth_colored, "TOO FAR - Move closer", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(depth_colored, "GOOD DISTANCE", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show windows
            cv2.imshow("Kinect Depth - Positioning Helper", depth_colored)
            cv2.imshow("Kinect RGB - Positioning Helper", rgb_bgr)
            
        except Exception as e:
            print(f"Visualization error: {e}")
    
    def run_positioning_guide(self):
        """Run complete positioning guide"""
        print("="*60)
        print("📐 KINECT POSITIONING GUIDE")
        print("="*60)
        
        # Analyze current view
        analysis_ok = self.analyze_current_view()
        
        # Provide guidance
        self.provide_positioning_guidance()
        
        if analysis_ok:
            print(f"\n🔴 Would you like to use the LIVE POSITIONING HELPER?")
            print(f"   This shows real-time Kinect view with positioning guidance")
            response = input("Start live helper? (y/n): ").lower().strip()
            
            if response == 'y':
                self.live_positioning_helper()
        
        return analysis_ok

def main():
    """Run Kinect positioning guide"""
    guide = KinectPositioningGuide()
    
    try:
        success = guide.run_positioning_guide()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Positioning guide failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
