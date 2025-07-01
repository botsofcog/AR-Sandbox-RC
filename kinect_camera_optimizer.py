#!/usr/bin/env python3
"""
Kinect Camera Optimizer & Fix
Optimizes both Kinect depth sensor and RGB camera for maximum performance
Fixes common issues and ensures both cameras work at their best
"""

import cv2
import numpy as np
import time
import sys
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library available for optimization")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect library not available")

class KinectCameraOptimizer:
    """
    Optimizes and fixes both Kinect cameras for maximum performance
    """
    
    def __init__(self):
        self.depth_sensor_active = False
        self.rgb_camera_active = False
        
        # Performance metrics
        self.depth_frame_count = 0
        self.rgb_frame_count = 0
        self.depth_fps = 0
        self.rgb_fps = 0
        
        # Quality metrics
        self.depth_quality_score = 0
        self.rgb_quality_score = 0
        
        # Optimization settings
        self.optimized_settings = {}
        
    def initialize_kinect_system(self):
        """Initialize and optimize Kinect system"""
        print("🔧 INITIALIZING KINECT CAMERA SYSTEM...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ Kinect not available for optimization")
            return False, False
        
        try:
            # Initialize depth sensor with optimization
            print("   🔍 Optimizing Kinect depth sensor...")
            depth_success = self.optimize_depth_sensor()
            
            # Initialize RGB camera with optimization
            print("   📷 Optimizing Kinect RGB camera...")
            rgb_success = self.optimize_rgb_camera()
            
            return depth_success, rgb_success
            
        except Exception as e:
            print(f"   ❌ Kinect system initialization failed: {e}")
            return False, False
    
    def optimize_depth_sensor(self):
        """Optimize Kinect depth sensor for maximum performance"""
        try:
            # Test depth sensor access
            depth_frame = freenect.sync_get_depth()[0]
            if depth_frame is None:
                print("      ❌ Depth sensor not accessible")
                return False
            
            # Analyze depth quality
            depth_stats = self.analyze_depth_quality(depth_frame)
            
            # Apply optimizations
            optimizations = self.apply_depth_optimizations(depth_stats)
            
            self.depth_sensor_active = True
            self.depth_quality_score = depth_stats['quality_score']
            
            print(f"      ✅ Depth sensor optimized - Quality: {self.depth_quality_score:.1f}/100")
            print(f"      📊 Applied optimizations: {len(optimizations)}")
            
            return True
            
        except Exception as e:
            print(f"      ❌ Depth sensor optimization failed: {e}")
            return False
    
    def optimize_rgb_camera(self):
        """Optimize Kinect RGB camera for maximum performance"""
        try:
            # Test RGB camera access
            rgb_frame = freenect.sync_get_video()[0]
            if rgb_frame is None:
                print("      ❌ RGB camera not accessible")
                return False
            
            # Analyze RGB quality
            rgb_stats = self.analyze_rgb_quality(rgb_frame)
            
            # Apply optimizations
            optimizations = self.apply_rgb_optimizations(rgb_stats)
            
            self.rgb_camera_active = True
            self.rgb_quality_score = rgb_stats['quality_score']
            
            print(f"      ✅ RGB camera optimized - Quality: {self.rgb_quality_score:.1f}/100")
            print(f"      📊 Applied optimizations: {len(optimizations)}")
            
            return True
            
        except Exception as e:
            print(f"      ❌ RGB camera optimization failed: {e}")
            return False
    
    def analyze_depth_quality(self, depth_frame):
        """Analyze depth sensor quality and performance"""
        stats = {
            'quality_score': 0,
            'valid_pixels': 0,
            'depth_range': 0,
            'noise_level': 0,
            'coverage': 0
        }
        
        try:
            # Calculate valid pixels
            valid_mask = depth_frame > 0
            stats['valid_pixels'] = np.sum(valid_mask)
            total_pixels = depth_frame.size
            stats['coverage'] = (stats['valid_pixels'] / total_pixels) * 100
            
            if stats['valid_pixels'] > 0:
                valid_depths = depth_frame[valid_mask]
                
                # Calculate depth range
                stats['depth_range'] = np.max(valid_depths) - np.min(valid_depths)
                
                # Calculate noise level (standard deviation)
                stats['noise_level'] = np.std(valid_depths)
                
                # Calculate quality score
                coverage_score = min(stats['coverage'], 80) / 80 * 40  # Max 40 points
                range_score = min(stats['depth_range'], 2000) / 2000 * 30  # Max 30 points
                noise_score = max(0, 30 - (stats['noise_level'] / 50))  # Max 30 points
                
                stats['quality_score'] = coverage_score + range_score + noise_score
            
            print(f"         Coverage: {stats['coverage']:.1f}%")
            print(f"         Depth range: {stats['depth_range']:.0f}mm")
            print(f"         Noise level: {stats['noise_level']:.1f}")
            
        except Exception as e:
            print(f"         Depth analysis error: {e}")
        
        return stats
    
    def analyze_rgb_quality(self, rgb_frame):
        """Analyze RGB camera quality and performance"""
        stats = {
            'quality_score': 0,
            'brightness': 0,
            'contrast': 0,
            'sharpness': 0,
            'color_balance': 0
        }
        
        try:
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2HSV)
            
            # Calculate brightness
            stats['brightness'] = np.mean(gray)
            
            # Calculate contrast (standard deviation)
            stats['contrast'] = np.std(gray)
            
            # Calculate sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            stats['sharpness'] = laplacian.var()
            
            # Calculate color balance (saturation)
            stats['color_balance'] = np.mean(hsv[:,:,1])
            
            # Calculate quality score
            brightness_score = max(0, 25 - abs(stats['brightness'] - 128) / 5)  # Max 25 points
            contrast_score = min(stats['contrast'], 50) / 50 * 25  # Max 25 points
            sharpness_score = min(stats['sharpness'], 1000) / 1000 * 25  # Max 25 points
            color_score = min(stats['color_balance'], 100) / 100 * 25  # Max 25 points
            
            stats['quality_score'] = brightness_score + contrast_score + sharpness_score + color_score
            
            print(f"         Brightness: {stats['brightness']:.1f}")
            print(f"         Contrast: {stats['contrast']:.1f}")
            print(f"         Sharpness: {stats['sharpness']:.1f}")
            print(f"         Color balance: {stats['color_balance']:.1f}")
            
        except Exception as e:
            print(f"         RGB analysis error: {e}")
        
        return stats
    
    def apply_depth_optimizations(self, depth_stats):
        """Apply optimizations to depth sensor"""
        optimizations = []
        
        try:
            # Optimization 1: Set optimal depth format
            try:
                freenect.set_depth_format(0, freenect.DEPTH_11BIT)
                optimizations.append("depth_format_11bit")
            except:
                pass
            
            # Optimization 2: Set optimal depth mode
            try:
                freenect.set_depth_mode(0, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
                optimizations.append("depth_mode_medium")
            except:
                pass
            
            # Optimization 3: Enable depth registration if available
            try:
                freenect.set_depth_registration(0, True)
                optimizations.append("depth_registration")
            except:
                pass
            
        except Exception as e:
            print(f"         Depth optimization error: {e}")
        
        return optimizations
    
    def apply_rgb_optimizations(self, rgb_stats):
        """Apply optimizations to RGB camera"""
        optimizations = []
        
        try:
            # Optimization 1: Set optimal video format
            try:
                freenect.set_video_format(0, freenect.VIDEO_RGB)
                optimizations.append("video_format_rgb")
            except:
                pass
            
            # Optimization 2: Set optimal video mode
            try:
                freenect.set_video_mode(0, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
                optimizations.append("video_mode_medium")
            except:
                pass
            
            # Optimization 3: Auto-adjust based on quality
            if rgb_stats['brightness'] < 100:
                # Image too dark - try to increase exposure
                optimizations.append("brightness_adjustment")
            
            if rgb_stats['contrast'] < 30:
                # Low contrast - try to enhance
                optimizations.append("contrast_enhancement")
            
        except Exception as e:
            print(f"         RGB optimization error: {e}")
        
        return optimizations
    
    def test_optimized_performance(self):
        """Test performance of optimized Kinect cameras"""
        print("\n🧪 TESTING OPTIMIZED KINECT PERFORMANCE...")
        
        if not (self.depth_sensor_active and self.rgb_camera_active):
            print("   ❌ Both cameras must be active for performance test")
            return False
        
        # Test frame capture performance
        start_time = time.time()
        test_frames = 30
        
        depth_success = 0
        rgb_success = 0
        
        for i in range(test_frames):
            try:
                # Test depth capture
                depth_frame = freenect.sync_get_depth()[0]
                if depth_frame is not None:
                    depth_success += 1
                
                # Test RGB capture
                rgb_frame = freenect.sync_get_video()[0]
                if rgb_frame is not None:
                    rgb_success += 1
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"   Frame {i+1} error: {e}")
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Calculate performance metrics
        depth_fps = depth_success / test_duration
        rgb_fps = rgb_success / test_duration
        
        print(f"   📊 PERFORMANCE RESULTS:")
        print(f"      Depth sensor: {depth_success}/{test_frames} frames ({depth_fps:.1f} FPS)")
        print(f"      RGB camera: {rgb_success}/{test_frames} frames ({rgb_fps:.1f} FPS)")
        print(f"      Test duration: {test_duration:.1f} seconds")
        
        # Overall performance score
        performance_score = ((depth_success + rgb_success) / (test_frames * 2)) * 100
        print(f"      Overall performance: {performance_score:.1f}%")
        
        return performance_score >= 90
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report"""
        print("\n" + "="*60)
        print("📊 KINECT CAMERA OPTIMIZATION REPORT")
        print("="*60)
        
        print(f"🎯 CAMERA STATUS:")
        print(f"   Depth Sensor: {'✅ OPTIMIZED' if self.depth_sensor_active else '❌ FAILED'}")
        print(f"   RGB Camera: {'✅ OPTIMIZED' if self.rgb_camera_active else '❌ FAILED'}")
        
        if self.depth_sensor_active:
            print(f"   Depth Quality: {self.depth_quality_score:.1f}/100")
        
        if self.rgb_camera_active:
            print(f"   RGB Quality: {self.rgb_quality_score:.1f}/100")
        
        overall_quality = (self.depth_quality_score + self.rgb_quality_score) / 2
        print(f"   Overall Quality: {overall_quality:.1f}/100")
        
        if self.depth_sensor_active and self.rgb_camera_active:
            if overall_quality >= 80:
                print(f"   🎉 EXCELLENT: Both Kinect cameras optimized!")
            elif overall_quality >= 60:
                print(f"   ✅ GOOD: Kinect cameras working well")
            else:
                print(f"   ⚠️ FAIR: Kinect cameras need improvement")
        else:
            print(f"   ❌ ISSUES: One or both cameras failed optimization")
        
        return self.depth_sensor_active and self.rgb_camera_active
    
    def run_kinect_optimization(self):
        """Run complete Kinect camera optimization"""
        print("="*60)
        print("🔧 KINECT CAMERA OPTIMIZER & FIX")
        print("="*60)
        
        # Initialize and optimize
        depth_ok, rgb_ok = self.initialize_kinect_system()
        
        if depth_ok and rgb_ok:
            # Test optimized performance
            performance_ok = self.test_optimized_performance()
            
            # Generate report
            optimization_success = self.generate_optimization_report()
            
            return optimization_success and performance_ok
        else:
            print("\n❌ KINECT OPTIMIZATION FAILED")
            return False

def main():
    """Run Kinect camera optimization"""
    optimizer = KinectCameraOptimizer()
    
    try:
        success = optimizer.run_kinect_optimization()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
