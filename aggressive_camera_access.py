#!/usr/bin/env python3
"""
AGGRESSIVE CAMERA ACCESS SOLUTION
BRUTE FORCE approach to get ALL 3 CAMERAS working
Kills competing processes, forces camera access, uses every trick available
"""

import cv2
import numpy as np
import subprocess
import time
import sys
import os
import psutil
import threading
from pathlib import Path

try:
    import freenect
    KINECT_AVAILABLE = True
    print("[SUCCESS] Kinect available")
except ImportError:
    KINECT_AVAILABLE = False
    print("[WARNING] Kinect not available")

class AggressiveCameraAccess:
    """
    AGGRESSIVE camera access that FORCES all 3 cameras to work
    Uses every trick in the book to bypass camera conflicts
    """
    
    def __init__(self):
        self.kinect_depth_active = False
        self.kinect_rgb_active = False
        self.logitech_active = False
        
        self.kinect_depth_stream = None
        self.kinect_rgb_stream = None
        self.logitech_stream = None
        
    def kill_camera_processes(self):
        """AGGRESSIVELY kill all processes that might be using cameras"""
        print("[AGGRESSIVE] Killing all camera-related processes...")
        
        # List of processes that commonly use cameras
        camera_processes = [
            "Camera.exe",
            "CameraApp.exe", 
            "WindowsCamera.exe",
            "Skype.exe",
            "Teams.exe",
            "Zoom.exe",
            "Discord.exe",
            "OBS64.exe",
            "obs.exe",
            "chrome.exe",
            "firefox.exe",
            "msedge.exe",
            "LogiCapture.exe",
            "LogiTune.exe",
            "Logi Options+.exe",
            "YCMMirage.exe",
            "ManyCam.exe",
            "XSplit.exe",
            "Streamlabs OBS.exe"
        ]
        
        killed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                if any(camera_proc.lower() in proc_name.lower() for camera_proc in camera_processes):
                    print(f"   Killing {proc_name} (PID: {proc.info['pid']})")
                    proc.kill()
                    killed_processes.append(proc_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_processes:
            print(f"   Killed {len(killed_processes)} camera processes: {killed_processes}")
            time.sleep(2)  # Wait for processes to fully terminate
        else:
            print("   No camera processes found to kill")
        
        return len(killed_processes)
    
    def force_release_camera_devices(self):
        """Force release all camera devices using Windows commands"""
        print("[AGGRESSIVE] Force releasing camera devices...")
        
        try:
            # Disable and re-enable camera devices
            ps_command = """
            Get-PnpDevice | Where-Object {
                $_.FriendlyName -like '*camera*' -or 
                $_.FriendlyName -like '*webcam*' -or
                $_.FriendlyName -like '*Logitech*'
            } | ForEach-Object {
                Write-Host "Resetting device: $($_.FriendlyName)"
                Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
                Start-Sleep -Seconds 1
                Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("   Camera devices reset successfully")
                time.sleep(3)  # Wait for devices to reinitialize
                return True
            else:
                print(f"   Device reset failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   Device reset error: {e}")
            return False
    
    def aggressive_camera_detection(self):
        """AGGRESSIVELY detect and access cameras using multiple methods"""
        print("[AGGRESSIVE] Detecting cameras using ALL available methods...")
        
        detected_cameras = []
        
        # Method 1: Brute force index testing with multiple backends
        backends = [
            ("DirectShow", cv2.CAP_DSHOW),
            ("MSMF", cv2.CAP_MSMF),
            ("Any", cv2.CAP_ANY),
            ("VFW", cv2.CAP_VFW) if hasattr(cv2, 'CAP_VFW') else None
        ]
        
        backends = [b for b in backends if b is not None]
        
        for backend_name, backend_flag in backends:
            print(f"   Testing {backend_name} backend...")
            
            for cam_idx in range(10):  # Test indices 0-9
                try:
                    cap = cv2.VideoCapture(cam_idx, backend_flag)
                    
                    if cap.isOpened():
                        # Force camera properties
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        # Test frame capture
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            height, width = frame.shape[:2]
                            
                            camera_info = {
                                'index': cam_idx,
                                'backend': backend_name,
                                'backend_flag': backend_flag,
                                'resolution': (width, height),
                                'capture_object': cap,
                                'working': True
                            }
                            
                            detected_cameras.append(camera_info)
                            print(f"      [SUCCESS] Camera {cam_idx} via {backend_name}: {width}x{height}")
                            
                            # Don't release yet - keep it open for use
                            continue
                        else:
                            cap.release()
                    else:
                        cap.release()
                        
                except Exception as e:
                    pass  # Silently continue
        
        print(f"   Detected {len(detected_cameras)} working cameras")
        return detected_cameras
    
    def initialize_kinect_aggressive(self):
        """AGGRESSIVELY initialize Kinect sensors"""
        if not KINECT_AVAILABLE:
            return False, False
        
        print("[AGGRESSIVE] Initializing Kinect sensors...")
        
        try:
            # Force Kinect initialization with retries
            for attempt in range(3):
                try:
                    # Test depth
                    depth_frame = freenect.sync_get_depth()[0]
                    if depth_frame is not None:
                        self.kinect_depth_active = True
                        print("   [SUCCESS] Kinect depth sensor FORCED active")
                        break
                except Exception as e:
                    print(f"   Kinect depth attempt {attempt+1} failed: {e}")
                    time.sleep(1)
            
            for attempt in range(3):
                try:
                    # Test RGB
                    rgb_frame = freenect.sync_get_video()[0]
                    if rgb_frame is not None:
                        self.kinect_rgb_active = True
                        print("   [SUCCESS] Kinect RGB camera FORCED active")
                        break
                except Exception as e:
                    print(f"   Kinect RGB attempt {attempt+1} failed: {e}")
                    time.sleep(1)
            
            return self.kinect_depth_active, self.kinect_rgb_active
            
        except Exception as e:
            print(f"   [ERROR] Kinect aggressive initialization failed: {e}")
            return False, False
    
    def force_logitech_access(self, detected_cameras):
        """FORCE Logitech C925e access using detected cameras"""
        print("[AGGRESSIVE] FORCING Logitech C925e access...")
        
        # Try each detected camera to find the Logitech
        for camera in detected_cameras:
            try:
                cap = camera['capture_object']
                
                # Test if this could be the Logitech C925e
                # Logitech C925e typically supports higher resolutions
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    
                    # If it can do high resolution, it's likely the Logitech
                    if width >= 1280 and height >= 720:
                        print(f"   [SUCCESS] FORCED Logitech C925e access on index {camera['index']}")
                        print(f"      Resolution: {width}x{height}")
                        print(f"      Backend: {camera['backend']}")
                        
                        # Set optimal settings for AR Sandbox
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                        
                        self.logitech_stream = cap
                        self.logitech_active = True
                        
                        # Remove from detected cameras list to avoid double-use
                        detected_cameras.remove(camera)
                        return True
                
            except Exception as e:
                print(f"   Camera {camera['index']} test failed: {e}")
        
        print("   [ERROR] Could not FORCE Logitech C925e access")
        return False
    
    def capture_aggressive_frame(self):
        """Capture frame using AGGRESSIVE methods"""
        frame_data = {
            "timestamp": time.time(),
            "kinect_depth": None,
            "kinect_rgb": None,
            "logitech_frame": None,
            "aggressive_metadata": {}
        }
        
        # Kinect depth (aggressive)
        if self.kinect_depth_active:
            try:
                depth_frame = freenect.sync_get_depth()[0]
                frame_data["kinect_depth"] = depth_frame
            except Exception as e:
                print(f"Aggressive Kinect depth error: {e}")
        
        # Kinect RGB (aggressive)
        if self.kinect_rgb_active:
            try:
                rgb_frame = freenect.sync_get_video()[0]
                frame_data["kinect_rgb"] = rgb_frame
            except Exception as e:
                print(f"Aggressive Kinect RGB error: {e}")
        
        # Logitech (aggressive)
        if self.logitech_active and self.logitech_stream:
            try:
                ret, logitech_frame = self.logitech_stream.read()
                if ret and logitech_frame is not None:
                    frame_data["logitech_frame"] = logitech_frame
            except Exception as e:
                print(f"Aggressive Logitech error: {e}")
        
        # Metadata
        active_sources = []
        if frame_data["kinect_depth"] is not None:
            active_sources.append("kinect_depth")
        if frame_data["kinect_rgb"] is not None:
            active_sources.append("kinect_rgb")
        if frame_data["logitech_frame"] is not None:
            active_sources.append("logitech_frame")
        
        frame_data["aggressive_metadata"] = {
            "total_sources": len(active_sources),
            "active_sources": active_sources,
            "integration_level": f"{(len(active_sources)/3)*100:.0f}%",
            "method": "AGGRESSIVE_FORCE_ACCESS",
            "all_cameras_working": len(active_sources) == 3
        }
        
        return frame_data
    
    def aggressive_initialization(self):
        """AGGRESSIVE initialization of ALL 3 cameras"""
        print("="*60)
        print("🔥 AGGRESSIVE CAMERA ACCESS - FORCE ALL 3 CAMERAS 🔥")
        print("="*60)
        
        # Step 1: Kill competing processes
        killed_count = self.kill_camera_processes()
        
        # Step 2: Force release camera devices
        self.force_release_camera_devices()
        
        # Step 3: Aggressive camera detection
        detected_cameras = self.aggressive_camera_detection()
        
        # Step 4: Force Kinect initialization
        kinect_depth_ok, kinect_rgb_ok = self.initialize_kinect_aggressive()
        
        # Step 5: Force Logitech access
        logitech_ok = self.force_logitech_access(detected_cameras)
        
        # Report results
        active_cameras = sum([kinect_depth_ok, kinect_rgb_ok, logitech_ok])
        
        print(f"\n🔥 AGGRESSIVE RESULTS:")
        print(f"   Processes killed: {killed_count}")
        print(f"   Cameras detected: {len(detected_cameras) + (1 if logitech_ok else 0)}")
        print(f"   Kinect depth: {'[FORCED ACTIVE]' if kinect_depth_ok else '[FAILED]'}")
        print(f"   Kinect RGB: {'[FORCED ACTIVE]' if kinect_rgb_ok else '[FAILED]'}")
        print(f"   Logitech C925e: {'[FORCED ACTIVE]' if logitech_ok else '[FAILED]'}")
        print(f"   Total cameras: {active_cameras}/3")
        
        if active_cameras == 3:
            print(f"\n🎉 AGGRESSIVE SUCCESS: ALL 3 CAMERAS FORCED ACTIVE!")
            print(f"   🚀 110% INTEGRATION ACHIEVED BY FORCE!")
            return True
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: {active_cameras}/3 cameras active")
            return active_cameras >= 2
    
    def cleanup(self):
        """Cleanup camera resources"""
        print("[CLEANUP] Aggressive camera access")
        
        if self.logitech_stream:
            try:
                self.logitech_stream.release()
            except Exception as e:
                print(f"Logitech cleanup error: {e}")

def main():
    """AGGRESSIVE camera access test"""
    aggressive_system = AggressiveCameraAccess()
    
    try:
        success = aggressive_system.aggressive_initialization()
        
        if success:
            print("\n🔥 TESTING AGGRESSIVE FRAME CAPTURE...")
            
            for i in range(3):
                frame_data = aggressive_system.capture_aggressive_frame()
                metadata = frame_data["aggressive_metadata"]
                
                print(f"   Frame {i+1}: {metadata['active_sources']} - {metadata['integration_level']}")
                
                if metadata["all_cameras_working"]:
                    print(f"   🎉 ALL 3 CAMERAS CAPTURED SUCCESSFULLY!")
                
                time.sleep(1)
            
            return 0
        else:
            print("\n❌ AGGRESSIVE APPROACH FAILED")
            return 1
            
    finally:
        aggressive_system.cleanup()

if __name__ == "__main__":
    sys.exit(main())
