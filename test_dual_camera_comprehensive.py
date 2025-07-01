#!/usr/bin/env python3
"""
Comprehensive Dual Camera System Testing
Tests REAL functionality, not just initialization
Verifies actual frame capture, data flow, and AR sandbox integration
"""

import cv2
import numpy as np
import time
import sys
import os
import json
import threading
from pathlib import Path

# Import the dual camera system
from dual_camera_system import DualCameraSystem

class ComprehensiveDualCameraTest:
    """
    Thorough testing of dual camera system functionality
    Tests real frame capture, data processing, and integration
    """
    
    def __init__(self):
        self.dual_camera = DualCameraSystem()
        self.test_results = {}
        self.frame_samples = []
        self.performance_data = []
        
    def test_initialization(self):
        """Test 1: System initialization"""
        print("\n" + "="*60)
        print("TEST 1: SYSTEM INITIALIZATION")
        print("="*60)
        
        try:
            success = self.dual_camera.initialize_all_systems()
            
            if success:
                print("[SUCCESS] Dual camera system initialized")
                
                # Verify components
                kinect_depth = self.dual_camera.kinect_depth_active
                kinect_rgb = self.dual_camera.kinect_rgb_active
                webcam_count = len(self.dual_camera.webcam_streams)
                
                print(f"   Kinect depth: {'[ACTIVE]' if kinect_depth else '[INACTIVE]'}")
                print(f"   Kinect RGB: {'[ACTIVE]' if kinect_rgb else '[INACTIVE]'}")
                print(f"   Webcam streams: {webcam_count}")
                
                self.test_results['initialization'] = {
                    'success': True,
                    'kinect_depth': kinect_depth,
                    'kinect_rgb': kinect_rgb,
                    'webcam_count': webcam_count,
                    'total_sources': webcam_count + (1 if kinect_depth else 0)
                }
                
                return True
            else:
                print("[FAILED] Dual camera system initialization failed")
                self.test_results['initialization'] = {'success': False}
                return False
                
        except Exception as e:
            print(f"[ERROR] Initialization test failed: {e}")
            self.test_results['initialization'] = {'success': False, 'error': str(e)}
            return False
    
    def test_frame_capture(self):
        """Test 2: Actual frame capture functionality"""
        print("\n" + "="*60)
        print("TEST 2: FRAME CAPTURE FUNCTIONALITY")
        print("="*60)
        
        try:
            # Capture multiple frames to test consistency
            successful_captures = 0
            failed_captures = 0
            frame_data_samples = []
            
            print("Capturing 10 test frames...")
            
            for i in range(10):
                print(f"   Frame {i+1}/10...", end=" ")
                
                frame_data = self.dual_camera.capture_synchronized_frame()
                
                if frame_data:
                    # Verify frame data structure
                    has_timestamp = 'timestamp' in frame_data
                    has_kinect_depth = frame_data.get('kinect_depth') is not None
                    has_webcam_streams = len(frame_data.get('webcam_streams', [])) > 0
                    has_metadata = 'sync_metadata' in frame_data
                    
                    if has_timestamp and (has_kinect_depth or has_webcam_streams) and has_metadata:
                        successful_captures += 1
                        print("[SUCCESS]")
                        
                        # Store sample for analysis
                        sample = {
                            'frame_index': i,
                            'timestamp': frame_data['timestamp'],
                            'kinect_depth_shape': frame_data['kinect_depth'].shape if has_kinect_depth else None,
                            'webcam_count': len(frame_data['webcam_streams']),
                            'metadata': frame_data['sync_metadata']
                        }
                        frame_data_samples.append(sample)
                    else:
                        failed_captures += 1
                        print("[FAILED] - Invalid frame data structure")
                else:
                    failed_captures += 1
                    print("[FAILED] - No frame data returned")
                
                time.sleep(0.1)  # Small delay between captures
            
            success_rate = (successful_captures / 10) * 100
            print(f"\nFrame capture results:")
            print(f"   Successful captures: {successful_captures}/10 ({success_rate}%)")
            print(f"   Failed captures: {failed_captures}/10")
            
            if successful_captures >= 8:  # 80% success rate minimum
                print("[SUCCESS] Frame capture test passed")
                self.test_results['frame_capture'] = {
                    'success': True,
                    'success_rate': success_rate,
                    'samples': frame_data_samples
                }
                return True
            else:
                print("[FAILED] Frame capture test failed - insufficient success rate")
                self.test_results['frame_capture'] = {
                    'success': False,
                    'success_rate': success_rate
                }
                return False
                
        except Exception as e:
            print(f"[ERROR] Frame capture test failed: {e}")
            self.test_results['frame_capture'] = {'success': False, 'error': str(e)}
            return False
    
    def test_data_quality(self):
        """Test 3: Data quality and consistency"""
        print("\n" + "="*60)
        print("TEST 3: DATA QUALITY AND CONSISTENCY")
        print("="*60)
        
        try:
            # Capture frames for quality analysis
            quality_samples = []
            
            print("Analyzing data quality over 5 frames...")
            
            for i in range(5):
                frame_data = self.dual_camera.capture_synchronized_frame()
                
                if frame_data:
                    quality_metrics = {
                        'frame_index': i,
                        'timestamp': frame_data['timestamp'],
                        'kinect_depth_valid': False,
                        'webcam_frames_valid': 0,
                        'sync_quality': 'unknown'
                    }
                    
                    # Test Kinect depth data quality
                    if frame_data.get('kinect_depth') is not None:
                        depth_frame = frame_data['kinect_depth']
                        if isinstance(depth_frame, np.ndarray) and depth_frame.size > 0:
                            # Check for valid depth values
                            valid_pixels = np.count_nonzero(depth_frame)
                            total_pixels = depth_frame.size
                            depth_coverage = (valid_pixels / total_pixels) * 100
                            
                            quality_metrics['kinect_depth_valid'] = depth_coverage > 10  # At least 10% coverage
                            quality_metrics['depth_coverage'] = depth_coverage
                            quality_metrics['depth_shape'] = depth_frame.shape
                            quality_metrics['depth_range'] = [int(depth_frame.min()), int(depth_frame.max())]
                    
                    # Test webcam frame quality
                    for j, webcam_data in enumerate(frame_data.get('webcam_streams', [])):
                        if webcam_data.get('frame') is not None:
                            webcam_frame = webcam_data['frame']
                            if isinstance(webcam_frame, np.ndarray) and webcam_frame.size > 0:
                                quality_metrics['webcam_frames_valid'] += 1
                                
                                # Store frame info
                                quality_metrics[f'webcam_{j}_shape'] = webcam_frame.shape
                                quality_metrics[f'webcam_{j}_backend'] = webcam_data.get('backend', 'unknown')
                    
                    # Overall sync quality
                    if quality_metrics['kinect_depth_valid'] and quality_metrics['webcam_frames_valid'] > 0:
                        quality_metrics['sync_quality'] = 'excellent'
                    elif quality_metrics['kinect_depth_valid'] or quality_metrics['webcam_frames_valid'] > 0:
                        quality_metrics['sync_quality'] = 'good'
                    else:
                        quality_metrics['sync_quality'] = 'poor'
                    
                    quality_samples.append(quality_metrics)
                    
                    print(f"   Frame {i+1}: {quality_metrics['sync_quality']} quality")
                    if quality_metrics['kinect_depth_valid']:
                        print(f"      Depth coverage: {quality_metrics.get('depth_coverage', 0):.1f}%")
                    print(f"      Valid webcam frames: {quality_metrics['webcam_frames_valid']}")
                
                time.sleep(0.2)
            
            # Analyze overall quality
            excellent_frames = sum(1 for s in quality_samples if s['sync_quality'] == 'excellent')
            good_frames = sum(1 for s in quality_samples if s['sync_quality'] == 'good')
            poor_frames = sum(1 for s in quality_samples if s['sync_quality'] == 'poor')
            
            print(f"\nData quality analysis:")
            print(f"   Excellent quality: {excellent_frames}/5 frames")
            print(f"   Good quality: {good_frames}/5 frames")
            print(f"   Poor quality: {poor_frames}/5 frames")
            
            if excellent_frames >= 3 or (excellent_frames + good_frames) >= 4:
                print("[SUCCESS] Data quality test passed")
                self.test_results['data_quality'] = {
                    'success': True,
                    'excellent_frames': excellent_frames,
                    'good_frames': good_frames,
                    'poor_frames': poor_frames,
                    'samples': quality_samples
                }
                return True
            else:
                print("[FAILED] Data quality test failed - insufficient quality")
                self.test_results['data_quality'] = {
                    'success': False,
                    'excellent_frames': excellent_frames,
                    'good_frames': good_frames,
                    'poor_frames': poor_frames
                }
                return False
                
        except Exception as e:
            print(f"[ERROR] Data quality test failed: {e}")
            self.test_results['data_quality'] = {'success': False, 'error': str(e)}
            return False
    
    def test_performance(self):
        """Test 4: Performance and FPS"""
        print("\n" + "="*60)
        print("TEST 4: PERFORMANCE AND FPS")
        print("="*60)
        
        try:
            print("Testing performance over 30 frames...")
            
            start_time = time.time()
            frame_times = []
            successful_frames = 0
            
            for i in range(30):
                frame_start = time.time()
                
                frame_data = self.dual_camera.capture_synchronized_frame()
                
                frame_end = time.time()
                frame_time = frame_end - frame_start
                
                if frame_data:
                    successful_frames += 1
                    frame_times.append(frame_time)
                
                if i % 10 == 9:  # Progress update every 10 frames
                    print(f"   Processed {i+1}/30 frames...")
            
            total_time = time.time() - start_time
            
            if frame_times:
                avg_frame_time = np.mean(frame_times)
                max_frame_time = np.max(frame_times)
                min_frame_time = np.min(frame_times)
                fps = successful_frames / total_time
                
                print(f"\nPerformance results:")
                print(f"   Successful frames: {successful_frames}/30")
                print(f"   Average FPS: {fps:.2f}")
                print(f"   Average frame time: {avg_frame_time*1000:.1f}ms")
                print(f"   Min frame time: {min_frame_time*1000:.1f}ms")
                print(f"   Max frame time: {max_frame_time*1000:.1f}ms")
                
                # Performance criteria: at least 10 FPS with 80% success rate
                if fps >= 10 and (successful_frames / 30) >= 0.8:
                    print("[SUCCESS] Performance test passed")
                    self.test_results['performance'] = {
                        'success': True,
                        'fps': fps,
                        'avg_frame_time': avg_frame_time,
                        'success_rate': successful_frames / 30
                    }
                    return True
                else:
                    print("[FAILED] Performance test failed - insufficient FPS or success rate")
                    self.test_results['performance'] = {
                        'success': False,
                        'fps': fps,
                        'success_rate': successful_frames / 30
                    }
                    return False
            else:
                print("[FAILED] Performance test failed - no successful frames")
                self.test_results['performance'] = {'success': False}
                return False
                
        except Exception as e:
            print(f"[ERROR] Performance test failed: {e}")
            self.test_results['performance'] = {'success': False, 'error': str(e)}
            return False
    
    def test_ar_sandbox_integration(self):
        """Test 5: AR Sandbox integration compatibility"""
        print("\n" + "="*60)
        print("TEST 5: AR SANDBOX INTEGRATION")
        print("="*60)
        
        try:
            print("Testing AR sandbox data format compatibility...")
            
            frame_data = self.dual_camera.capture_synchronized_frame()
            
            if not frame_data:
                print("[FAILED] No frame data for integration test")
                return False
            
            # Test data format compatibility with AR sandbox
            compatibility_checks = {
                'has_timestamp': 'timestamp' in frame_data,
                'has_depth_data': frame_data.get('kinect_depth') is not None,
                'has_rgb_data': len(frame_data.get('webcam_streams', [])) > 0,
                'has_metadata': 'sync_metadata' in frame_data,
                'depth_format_valid': False,
                'rgb_format_valid': False
            }
            
            # Check depth data format
            if frame_data.get('kinect_depth') is not None:
                depth = frame_data['kinect_depth']
                if isinstance(depth, np.ndarray) and len(depth.shape) == 2:
                    compatibility_checks['depth_format_valid'] = True
                    print(f"   Depth data: {depth.shape} shape, {depth.dtype} type")
            
            # Check RGB data format
            if frame_data.get('webcam_streams'):
                for i, stream in enumerate(frame_data['webcam_streams']):
                    if stream.get('frame') is not None:
                        rgb = stream['frame']
                        if isinstance(rgb, np.ndarray) and len(rgb.shape) == 3:
                            compatibility_checks['rgb_format_valid'] = True
                            print(f"   RGB stream {i}: {rgb.shape} shape, {rgb.dtype} type")
            
            # Test mesh generation compatibility (simulate AR sandbox mesh generation)
            try:
                if frame_data.get('kinect_depth') is not None:
                    depth = frame_data['kinect_depth']
                    # Simulate mesh point generation
                    height, width = depth.shape
                    mesh_points = []
                    
                    for y in range(0, height, 4):  # Sample every 4th pixel
                        for x in range(0, width, 4):
                            z = depth[y, x]
                            if z > 0:  # Valid depth
                                mesh_points.append([x, y, z])
                    
                    if len(mesh_points) > 100:  # Need reasonable number of points
                        compatibility_checks['mesh_generation'] = True
                        print(f"   Generated {len(mesh_points)} mesh points")
                    else:
                        compatibility_checks['mesh_generation'] = False
                        print(f"   Insufficient mesh points: {len(mesh_points)}")
                else:
                    compatibility_checks['mesh_generation'] = False
                    
            except Exception as e:
                compatibility_checks['mesh_generation'] = False
                print(f"   Mesh generation failed: {e}")
            
            # Overall compatibility score
            passed_checks = sum(1 for check in compatibility_checks.values() if check)
            total_checks = len(compatibility_checks)
            compatibility_score = (passed_checks / total_checks) * 100
            
            print(f"\nIntegration compatibility:")
            for check, result in compatibility_checks.items():
                print(f"   {check}: {'[PASS]' if result else '[FAIL]'}")
            print(f"   Overall score: {compatibility_score:.1f}%")
            
            if compatibility_score >= 80:
                print("[SUCCESS] AR sandbox integration test passed")
                self.test_results['ar_integration'] = {
                    'success': True,
                    'compatibility_score': compatibility_score,
                    'checks': compatibility_checks
                }
                return True
            else:
                print("[FAILED] AR sandbox integration test failed")
                self.test_results['ar_integration'] = {
                    'success': False,
                    'compatibility_score': compatibility_score,
                    'checks': compatibility_checks
                }
                return False
                
        except Exception as e:
            print(f"[ERROR] AR sandbox integration test failed: {e}")
            self.test_results['ar_integration'] = {'success': False, 'error': str(e)}
            return False
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        print(f"Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "[PASS]" if result.get('success', False) else "[FAIL]"
            print(f"   {test_name}: {status}")
            
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Final verdict
        if passed_tests == total_tests:
            print("\n[SUCCESS] ALL TESTS PASSED - Dual Camera System FULLY FUNCTIONAL")
            return True
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("\n[PARTIAL] Most tests passed - System mostly functional with minor issues")
            return True
        else:
            print("\n[FAILED] Multiple test failures - System needs significant fixes")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("COMPREHENSIVE DUAL CAMERA SYSTEM TESTING")
        print("Testing REAL functionality, not just initialization")
        print("="*60)
        
        try:
            # Run all tests in sequence
            test_sequence = [
                self.test_initialization,
                self.test_frame_capture,
                self.test_data_quality,
                self.test_performance,
                self.test_ar_sandbox_integration
            ]
            
            for test_func in test_sequence:
                success = test_func()
                if not success:
                    print(f"\n[WARNING] Test {test_func.__name__} failed, continuing with remaining tests...")
            
            # Generate final report
            overall_success = self.generate_comprehensive_report()
            
            return overall_success
            
        finally:
            # Always cleanup
            self.dual_camera.cleanup()

def main():
    """Run comprehensive dual camera system testing"""
    tester = ComprehensiveDualCameraTest()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
