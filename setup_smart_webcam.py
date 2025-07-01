#!/usr/bin/env python3
"""
Setup script for Smart Webcam AR Sandbox
Installs required dependencies and tests the system
"""

import subprocess
import sys
import os
import cv2
import numpy as np

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_camera():
    """Test if camera is working"""
    print("📹 Testing camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera not found or not accessible")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Could not read from camera")
        cap.release()
        return False
    
    print(f"✅ Camera working! Resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True

def main():
    print("🚀 Setting up Smart Webcam AR Sandbox")
    print("=" * 50)
    
    # Required packages
    required_packages = [
        "opencv-python",
        "numpy",
        "scipy",
        "websockets",
        "scikit-learn"
    ]
    
    # Optional AI packages
    optional_packages = [
        "torch",
        "torchvision"
    ]
    
    print("📦 Installing required packages...")
    for package in required_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            return False
    
    print("\n🤖 Installing optional AI packages...")
    for package in optional_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"⚠️ {package} installation failed (optional)")
    
    print("\n📹 Testing camera...")
    if not check_camera():
        print("❌ Camera test failed!")
        return False
    
    print("\n🧪 Running system test...")
    try:
        from backend.smart_webcam_depth import SmartWebcamDepth
        
        # Quick test
        depth_estimator = SmartWebcamDepth(0)
        if depth_estimator.initialize_camera():
            print("✅ Smart webcam depth estimation initialized")
            depth_estimator.cleanup()
        else:
            print("❌ Failed to initialize depth estimation")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the interactive demo:")
    print("   python smart_webcam_sandbox.py --mode demo")
    print("\n2. Or start the WebSocket server:")
    print("   python smart_webcam_sandbox.py --mode server")
    print("\n3. For integration with RC Sandbox:")
    print("   python professional_demo_suite.py --demo smart_webcam")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
