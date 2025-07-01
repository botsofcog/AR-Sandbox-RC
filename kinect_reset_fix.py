#!/usr/bin/env python3
"""
Kinect Reset & Stabilization Fix
Fixes flashing lights and unstable Kinect state
"""

import time
import sys

try:
    import freenect
    KINECT_AVAILABLE = True
    print("✅ Kinect library available")
except ImportError:
    KINECT_AVAILABLE = False
    print("❌ Kinect library not available")

def reset_kinect_completely():
    """Completely reset Kinect to stable state"""
    print("🔄 RESETTING KINECT COMPLETELY...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect not available")
        return False
    
    try:
        # Step 1: Stop everything
        print("   🛑 Stopping all Kinect streams...")
        try:
            freenect.stop_depth(0)
            freenect.stop_video(0)
            time.sleep(1.0)
            print("      ✅ Streams stopped")
        except Exception as e:
            print(f"      ⚠️ Stop streams: {e}")
        
        # Step 2: Close any open devices
        print("   🔒 Closing Kinect devices...")
        try:
            for device_id in range(3):  # Try multiple device IDs
                try:
                    device = freenect.open_device(device_id)
                    if device:
                        freenect.close_device(device)
                        print(f"      ✅ Closed device {device_id}")
                except:
                    pass
        except Exception as e:
            print(f"      ⚠️ Close devices: {e}")
        
        # Step 3: Wait for hardware reset
        print("   ⏳ Waiting for hardware reset...")
        time.sleep(3.0)
        
        # Step 4: Check device count
        try:
            device_count = freenect.num_devices()
            print(f"   📱 Kinect devices detected: {device_count}")
            
            if device_count == 0:
                print("   ❌ No Kinect devices detected after reset")
                return False
        except Exception as e:
            print(f"   ❌ Device count check failed: {e}")
            return False
        
        # Step 5: Test basic device access
        print("   🧪 Testing basic device access...")
        try:
            device = freenect.open_device(0)
            if device:
                print("      ✅ Device opened successfully")
                freenect.close_device(device)
                print("      ✅ Device closed successfully")
                time.sleep(1.0)
                return True
            else:
                print("      ❌ Failed to open device")
                return False
        except Exception as e:
            print(f"      ❌ Device access test failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Complete reset failed: {e}")
        return False

def stabilize_kinect_lights():
    """Stabilize Kinect lights and stop flashing"""
    print("💡 STABILIZING KINECT LIGHTS...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect not available")
        return False
    
    try:
        # Method 1: Gentle initialization
        print("   🔄 Method 1: Gentle initialization...")
        try:
            device = freenect.open_device(0)
            if device:
                # Set minimal modes first
                freenect.set_depth_mode(device, freenect.DEPTH_11BIT)
                time.sleep(0.5)
                freenect.set_video_mode(device, freenect.VIDEO_RGB)
                time.sleep(0.5)
                
                # Start depth only first
                freenect.start_depth(device)
                time.sleep(2.0)  # Wait longer for stabilization
                
                # Check if lights stabilized
                print("      ⏳ Checking light stabilization...")
                time.sleep(2.0)
                
                # Now start video
                freenect.start_video(device)
                time.sleep(2.0)
                
                freenect.close_device(device)
                print("      ✅ Gentle initialization complete")
                return True
        except Exception as e:
            print(f"      ❌ Gentle initialization failed: {e}")
        
        # Method 2: Reset cycle
        print("   🔄 Method 2: Reset cycle...")
        try:
            for cycle in range(3):
                print(f"      Cycle {cycle + 1}/3...")
                
                # Open device
                device = freenect.open_device(0)
                if device:
                    # Quick start/stop cycle
                    freenect.start_depth(device)
                    time.sleep(0.5)
                    freenect.stop_depth(device)
                    time.sleep(0.5)
                    
                    freenect.start_video(device)
                    time.sleep(0.5)
                    freenect.stop_video(device)
                    time.sleep(0.5)
                    
                    freenect.close_device(device)
                    time.sleep(1.0)
            
            print("      ✅ Reset cycle complete")
            return True
            
        except Exception as e:
            print(f"      ❌ Reset cycle failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Light stabilization failed: {e}")
        return False

def test_kinect_stability():
    """Test if Kinect is in stable state"""
    print("🧪 TESTING KINECT STABILITY...")
    
    if not KINECT_AVAILABLE:
        print("   ❌ Kinect not available")
        return False
    
    try:
        stable_tests = 0
        total_tests = 5
        
        for test in range(total_tests):
            print(f"   Test {test + 1}/{total_tests}...")
            
            try:
                # Test device open/close
                device = freenect.open_device(0)
                if device:
                    time.sleep(0.2)
                    freenect.close_device(device)
                    time.sleep(0.2)
                    stable_tests += 1
                    print(f"      ✅ Test {test + 1} passed")
                else:
                    print(f"      ❌ Test {test + 1} failed - cannot open device")
            except Exception as e:
                print(f"      ❌ Test {test + 1} failed: {e}")
            
            time.sleep(0.5)
        
        stability_percentage = (stable_tests / total_tests) * 100
        print(f"   📊 Stability: {stable_tests}/{total_tests} ({stability_percentage:.0f}%)")
        
        if stability_percentage >= 80:
            print("   ✅ Kinect is stable")
            return True
        else:
            print("   ❌ Kinect is unstable")
            return False
            
    except Exception as e:
        print(f"   ❌ Stability test failed: {e}")
        return False

def fix_kinect_flashing_lights():
    """Complete fix for Kinect flashing lights"""
    print("="*60)
    print("💡 KINECT FLASHING LIGHTS FIX")
    print("="*60)
    
    # Step 1: Complete reset
    reset_success = reset_kinect_completely()
    
    if not reset_success:
        print("\n❌ RESET FAILED - Manual intervention required")
        print("💡 MANUAL STEPS:")
        print("   1. Unplug Kinect power cable")
        print("   2. Wait 10 seconds")
        print("   3. Unplug Kinect USB cable")
        print("   4. Wait 10 seconds")
        print("   5. Plug in power cable first")
        print("   6. Wait for green light")
        print("   7. Plug in USB cable")
        print("   8. Run this script again")
        return False
    
    # Step 2: Stabilize lights
    stabilize_success = stabilize_kinect_lights()
    
    # Step 3: Test stability
    stability_success = test_kinect_stability()
    
    # Final report
    print(f"\n📊 KINECT FIX RESULTS:")
    print(f"   Reset: {'✅ SUCCESS' if reset_success else '❌ FAILED'}")
    print(f"   Stabilization: {'✅ SUCCESS' if stabilize_success else '❌ FAILED'}")
    print(f"   Stability: {'✅ STABLE' if stability_success else '❌ UNSTABLE'}")
    
    if reset_success and stabilize_success and stability_success:
        print(f"\n🎉 SUCCESS: Kinect lights should be stable now!")
        print(f"   💡 Light should be: SOLID GREEN (ready)")
        print(f"   🚫 Light should NOT be: Flashing or blinking")
        return True
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: Some issues remain")
        if not stability_success:
            print(f"   💡 Try unplugging/replugging Kinect power and USB")
        return False

def main():
    """Run Kinect flashing lights fix"""
    try:
        success = fix_kinect_flashing_lights()
        
        if success:
            print(f"\n✅ Kinect should now be ready for use")
            print(f"   You can now run the camera system again")
        else:
            print(f"\n❌ Manual intervention required")
            print(f"   Check Kinect power and USB connections")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
