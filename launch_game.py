#!/usr/bin/env python3
"""
Quick Launcher for AR Sandbox Game
Starts the webcam server and opens the game in browser
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

def check_dependencies():
    """Check if required packages are available"""
    required = ['cv2', 'websockets', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing packages:")
        for pkg in missing:
            print(f"   • {pkg}")
        print("\n📦 Install with:")
        print("   pip install opencv-python websockets numpy")
        return False
    
    return True

def test_camera():
    """Quick camera test"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera working")
                return True
        print("⚠️ Camera not accessible (game will work without it)")
        return False
    except:
        print("⚠️ Camera test failed (game will work without it)")
        return False

def open_game_in_browser():
    """Open the game HTML file in browser"""
    game_file = Path("working_sandbox_game.html")
    
    if game_file.exists():
        try:
            time.sleep(2)  # Wait for server to start
            game_url = game_file.resolve().as_uri()
            webbrowser.open(game_url)
            print(f"🌐 Game opened: {game_url}")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print(f"📂 Manually open: {game_file.absolute()}")
    else:
        print("❌ Game file not found: working_sandbox_game.html")

def start_server():
    """Start the webcam server"""
    try:
        print("🚀 Starting webcam server...")
        result = subprocess.run([
            sys.executable, "simple_webcam_server.py"
        ], check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def main():
    """Main launcher"""
    print("🎮 AR SANDBOX GAME LAUNCHER")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to continue anyway...")
    
    # Test camera
    test_camera()
    
    print("\n🚀 LAUNCHING GAME...")
    print("1. Starting webcam server...")
    print("2. Opening game in browser...")
    print("3. Ready to play!")
    print("\n🎮 GAME CONTROLS:")
    print("• Mouse: Click and drag to build")
    print("• 1-4: Switch build modes")
    print("• F: Flood mission")
    print("• H: Highway mission")
    print("• R: Reset game")
    print("• Click vehicles to activate them")
    print("\nPress Ctrl+C to stop")
    print("-" * 40)
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_game_in_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server (this blocks)
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Game stopped")
    
    print("👋 Thanks for playing!")

if __name__ == "__main__":
    main()
