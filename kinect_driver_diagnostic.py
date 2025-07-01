#!/usr/bin/env python3
"""
Kinect Driver Diagnostic & Zadig Integration
Diagnoses driver issues and provides Zadig guidance for custom driver loading
"""

import subprocess
import sys
import time
import os

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect library not available")

class KinectDriverDiagnostic:
    """
    Diagnoses Kinect driver issues and provides Zadig guidance
    """
    
    def __init__(self):
        self.kinect_devices_found = []
        self.driver_issues = []
        self.zadig_recommendations = []
        
    def scan_windows_devices(self):
        """Scan Windows Device Manager for Kinect devices"""
        print("🔍 SCANNING WINDOWS DEVICES FOR KINECT...")
        
        try:
            # Use PowerShell to get device information
            powershell_cmd = '''
            Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                $_.Name -like "*Kinect*" -or 
                $_.Name -like "*Xbox*" -or 
                $_.DeviceID -like "*VID_045E*PID_02AE*" -or
                $_.DeviceID -like "*VID_045E*PID_02AD*" -or
                $_.DeviceID -like "*VID_045E*PID_02B0*"
            } | Select-Object Name, DeviceID, Status, PNPDeviceID | Format-Table -AutoSize
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print("   📱 KINECT DEVICES FOUND:")
                    print(output)
                    
                    # Parse devices
                    lines = output.split('\n')
                    for line in lines:
                        if 'Kinect' in line or 'Xbox' in line:
                            self.kinect_devices_found.append(line.strip())
                            
                    if self.kinect_devices_found:
                        print(f"   ✅ Found {len(self.kinect_devices_found)} Kinect-related device(s)")
                    else:
                        print("   ❌ No Kinect devices found in Device Manager")
                        self.driver_issues.append("No Kinect devices detected in Windows")
                else:
                    print("   ❌ No Kinect devices found")
                    self.driver_issues.append("No Kinect devices detected")
            else:
                print(f"   ❌ Device scan failed: {result.stderr}")
                self.driver_issues.append("Windows device scan failed")
                
        except Exception as e:
            print(f"   ❌ Device scan error: {e}")
            self.driver_issues.append(f"Device scan error: {e}")
    
    def check_kinect_driver_status(self):
        """Check specific Kinect driver status"""
        print("\n🔍 CHECKING KINECT DRIVER STATUS...")
        
        try:
            # Check for specific Kinect driver issues
            powershell_cmd = '''
            Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                $_.Name -like "*Kinect*" -or $_.Name -like "*Xbox*"
            } | ForEach-Object {
                $status = if ($_.Status -eq "OK") { "✅ OK" } else { "❌ " + $_.Status }
                Write-Output "$($_.Name): $status"
                if ($_.Status -ne "OK") {
                    Write-Output "  DeviceID: $($_.DeviceID)"
                    Write-Output "  PNPDeviceID: $($_.PNPDeviceID)"
                }
            }
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print("   📊 DRIVER STATUS:")
                    print(output)
                    
                    # Check for driver issues
                    if "❌" in output:
                        self.driver_issues.append("Kinect drivers have errors")
                        self.zadig_recommendations.append("Replace problematic drivers with WinUSB using Zadig")
                    
                    # Check for missing drivers
                    if "Unknown" in output or "Error" in output:
                        self.driver_issues.append("Kinect drivers missing or corrupted")
                        self.zadig_recommendations.append("Install WinUSB drivers using Zadig")
                else:
                    print("   ❌ No driver status information available")
                    
        except Exception as e:
            print(f"   ❌ Driver status check failed: {e}")
            self.driver_issues.append(f"Driver status check failed: {e}")
    
    def test_libfreenect_access(self):
        """Test libfreenect access to Kinect"""
        print("\n🧪 TESTING LIBFREENECT ACCESS...")
        
        if not KINECT_AVAILABLE:
            print("   ❌ libfreenect not available")
            self.driver_issues.append("libfreenect library not available")
            return False
        
        try:
            # Test device count
            print("   📱 Testing device detection...")
            try:
                # Try different ways to get device count
                device_count = 0
                
                # Method 1: Try to open device directly
                try:
                    device = freenect.open_device(0)
                    if device:
                        device_count = 1
                        freenect.close_device(device)
                        print("   ✅ Device 0 accessible")
                    else:
                        print("   ❌ Device 0 not accessible")
                except Exception as e:
                    print(f"   ❌ Device 0 access failed: {e}")
                
                if device_count == 0:
                    self.driver_issues.append("libfreenect cannot access Kinect device")
                    self.zadig_recommendations.append("Replace Xbox 360 Kinect drivers with WinUSB using Zadig")
                
            except Exception as e:
                print(f"   ❌ Device detection failed: {e}")
                self.driver_issues.append(f"Device detection failed: {e}")
            
            # Test data capture
            if device_count > 0:
                print("   📊 Testing data capture...")
                try:
                    depth_frame, timestamp = freenect.sync_get_depth()
                    if depth_frame is not None:
                        print(f"   ✅ Depth capture working: {depth_frame.shape}")
                    else:
                        print("   ❌ Depth capture returns None")
                        self.driver_issues.append("Depth sensor not providing data")
                        self.zadig_recommendations.append("Ensure Kinect Camera driver is replaced with WinUSB")
                        
                    rgb_frame, timestamp = freenect.sync_get_video()
                    if rgb_frame is not None:
                        print(f"   ✅ RGB capture working: {rgb_frame.shape}")
                    else:
                        print("   ❌ RGB capture returns None")
                        self.driver_issues.append("RGB camera not providing data")
                        self.zadig_recommendations.append("Ensure Kinect Camera driver is replaced with WinUSB")
                        
                except Exception as e:
                    print(f"   ❌ Data capture test failed: {e}")
                    self.driver_issues.append(f"Data capture failed: {e}")
                    self.zadig_recommendations.append("Replace all Kinect drivers with WinUSB using Zadig")
            
            return device_count > 0
            
        except Exception as e:
            print(f"   ❌ libfreenect test failed: {e}")
            self.driver_issues.append(f"libfreenect test failed: {e}")
            return False
    
    def generate_zadig_instructions(self):
        """Generate specific Zadig instructions based on detected issues"""
        print("\n" + "="*60)
        print("🔧 ZADIG DRIVER REPLACEMENT INSTRUCTIONS")
        print("="*60)
        
        if not self.driver_issues:
            print("✅ NO DRIVER ISSUES DETECTED - Zadig not needed")
            return
        
        print("⚠️ DRIVER ISSUES DETECTED - Zadig recommended")
        print("\n📋 DETECTED ISSUES:")
        for i, issue in enumerate(self.driver_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 ZADIG INSTRUCTIONS:")
        print("1. **DOWNLOAD ZADIG** (if not already available):")
        print("   - Go to: https://zadig.akeo.ie/")
        print("   - Download latest version")
        print("   - Run as Administrator")
        
        print("\n2. **KINECT DRIVER REPLACEMENT STEPS:**")
        print("   a) Open Zadig as Administrator")
        print("   b) Go to Options → List All Devices")
        print("   c) Look for these Kinect devices:")
        print("      • Xbox NUI Camera")
        print("      • Xbox NUI Audio") 
        print("      • Xbox NUI Motor")
        print("      • Kinect Camera")
        print("      • Kinect Audio")
        
        print("\n3. **REPLACE EACH DEVICE:**")
        print("   a) Select device from dropdown")
        print("   b) Ensure target driver is 'WinUSB'")
        print("   c) Click 'Replace Driver'")
        print("   d) Wait for completion")
        print("   e) Repeat for all Kinect devices")
        
        print("\n4. **SPECIFIC RECOMMENDATIONS:**")
        for i, recommendation in enumerate(self.zadig_recommendations, 1):
            print(f"   {i}. {recommendation}")
        
        print("\n5. **AFTER ZADIG:**")
        print("   a) Unplug Kinect USB cable")
        print("   b) Wait 5 seconds")
        print("   c) Plug back in USB cable")
        print("   d) Run this diagnostic again")
        print("   e) Test camera system")
        
        print("\n⚠️ **IMPORTANT NOTES:**")
        print("   • Run Zadig as Administrator")
        print("   • Replace ALL Kinect-related devices")
        print("   • Use WinUSB driver (not libusb)")
        print("   • Backup existing drivers if prompted")
        
    def run_complete_diagnostic(self):
        """Run complete Kinect driver diagnostic"""
        print("="*60)
        print("🔍 KINECT DRIVER DIAGNOSTIC & ZADIG INTEGRATION")
        print("="*60)
        
        # Scan Windows devices
        self.scan_windows_devices()
        
        # Check driver status
        self.check_kinect_driver_status()
        
        # Test libfreenect access
        libfreenect_ok = self.test_libfreenect_access()
        
        # Generate Zadig instructions
        self.generate_zadig_instructions()
        
        # Final summary
        print(f"\n📊 DIAGNOSTIC SUMMARY:")
        print(f"   Windows devices found: {len(self.kinect_devices_found)}")
        print(f"   Driver issues: {len(self.driver_issues)}")
        print(f"   libfreenect access: {'✅ WORKING' if libfreenect_ok else '❌ FAILED'}")
        print(f"   Zadig needed: {'✅ YES' if self.driver_issues else '❌ NO'}")
        
        if self.driver_issues:
            print(f"\n🎯 NEXT STEPS:")
            print(f"   1. Use Zadig to replace Kinect drivers with WinUSB")
            print(f"   2. Follow the detailed instructions above")
            print(f"   3. Run this diagnostic again after Zadig")
            print(f"   4. Test the camera system")
        else:
            print(f"\n🎉 DRIVERS APPEAR CORRECT - Try camera system")
        
        return len(self.driver_issues) == 0

def main():
    """Run Kinect driver diagnostic"""
    diagnostic = KinectDriverDiagnostic()
    
    try:
        success = diagnostic.run_complete_diagnostic()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
