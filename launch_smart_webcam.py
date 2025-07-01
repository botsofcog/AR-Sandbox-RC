#!/usr/bin/env python3
"""
Smart Webcam AR Sandbox Launcher
Easy launcher for the beautiful AI-powered AR sandbox demo
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import threading

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['cv2', 'numpy', 'websockets']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Install with: pip install opencv-python numpy websockets")
        return False
    
    return True

def test_camera():
    """Test if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera test successful")
                return True
        print("❌ Camera not accessible")
        return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def launch_server(port=8765, camera_id=0):
    """Launch the WebSocket server"""
    try:
        print(f"🚀 Starting server on port {port}...")
        
        # Run the server
        result = subprocess.run([
            sys.executable, "smart_webcam_server.py",
            "--port", str(port),
            "--camera", str(camera_id)
        ], check=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def open_demo_in_browser():
    """Open the demo HTML file in browser"""
    demo_file = Path("smart_webcam_demo.html")
    
    if demo_file.exists():
        try:
            # Wait a moment for server to start
            time.sleep(2)
            
            demo_url = demo_file.resolve().as_uri()
            webbrowser.open(demo_url)
            print(f"🌐 Demo opened in browser: {demo_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            return False
    else:
        print("❌ Demo file not found: smart_webcam_demo.html")
        return False

def show_instructions():
    """Show usage instructions"""
    print("""
🎮 SMART WEBCAM AR SANDBOX CONTROLS:

🖱️  Mouse Controls:
   • Click and drag to sculpt terrain
   • Left click: Add material
   • Right click: Remove material

⌨️  Keyboard Shortcuts:
   • Space: Reset terrain
   • C: Start calibration
   • W: Add water effect
   • D: Toggle debug view
   • F: Toggle fullscreen
   • H: Show help

🎯 Calibration:
   1. Ensure sandbox is empty and well-lit
   2. Click "CALIBRATE" button or press 'C'
   3. Wait for calibration to complete
   4. Start sculpting!

🤖 AI Features:
   • Shadow analysis for height detection
   • Color-based terrain mapping
   • Edge detection and contours
   • Temporal stereo vision
   • Real-time performance optimization

💡 Tips:
   • Good lighting improves accuracy
   • Calibrate when lighting changes
   • Use debug view to see AI analysis
   • Adjust technique weights for your setup
""")

def main():
    """Main launcher function"""
    print("🤖 SMART WEBCAM AR SANDBOX LAUNCHER")
    print("=" * 50)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return False
    
    # Test camera
    print("📹 Testing camera...")
    if not test_camera():
        print("\n⚠️  Camera issues detected, but continuing anyway...")
        print("   The demo will work with fallback mode")
    
    # Show instructions
    show_instructions()
    
    # Get user preferences
    print("\n🎛️  CONFIGURATION:")
    try:
        port = input("WebSocket port (default 8765): ").strip()
        port = int(port) if port else 8765
        
        camera_id = input("Camera ID (default 0): ").strip()
        camera_id = int(camera_id) if camera_id else 0
        
        auto_open = input("Auto-open browser? (Y/n): ").strip().lower()
        auto_open = auto_open != 'n'
        
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        return False
    except ValueError:
        print("❌ Invalid input, using defaults")
        port, camera_id, auto_open = 8765, 0, True
    
    print(f"\n🚀 LAUNCHING SMART WEBCAM AR SANDBOX")
    print(f"   Port: {port}")
    print(f"   Camera: {camera_id}")
    print(f"   Auto-open: {auto_open}")
    print("-" * 50)
    
    # Open browser in background if requested
    if auto_open:
        browser_thread = threading.Thread(target=open_demo_in_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Launch server (this will block)
    try:
        success = launch_server(port, camera_id)
        if not success:
            print("❌ Server failed to start properly")
            return False
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    print("\n👋 Smart Webcam AR Sandbox stopped")
    return True

def quick_demo():
    """Quick demo launcher with defaults"""
    print("🚀 QUICK DEMO LAUNCHER")
    print("=" * 30)
    
    if not check_dependencies():
        return False
    
    print("📹 Starting with default settings...")
    print("🌐 Browser will open automatically")
    print("⌨️  Press Ctrl+C to stop")
    print("-" * 30)
    
    # Open browser
    browser_thread = threading.Thread(target=open_demo_in_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Launch server
    try:
        launch_server()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Webcam AR Sandbox Launcher")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick demo with default settings")
    parser.add_argument("--port", type=int, default=8765,
                       help="WebSocket port (default: 8765)")
    parser.add_argument("--camera", type=int, default=0,
                       help="Camera ID (default: 0)")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't auto-open browser")
    
    args = parser.parse_args()
    
    if args.quick:
        success = quick_demo()
    else:
        if len(sys.argv) > 1:
            # Command line mode
            print("🤖 SMART WEBCAM AR SANDBOX")
            print("=" * 30)
            
            if not check_dependencies():
                sys.exit(1)
            
            if not args.no_browser:
                browser_thread = threading.Thread(target=open_demo_in_browser)
                browser_thread.daemon = True
                browser_thread.start()
            
            try:
                success = launch_server(args.port, args.camera)
            except KeyboardInterrupt:
                print("\n👋 Stopped")
                success = True
        else:
            # Interactive mode
            success = main()
    
    sys.exit(0 if success else 1)
