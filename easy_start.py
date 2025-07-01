#!/usr/bin/env python3
"""
RC Sandbox - Easy Start Launcher
Simple, user-friendly launcher for beginners
"""

import os
import sys
import webbrowser
from pathlib import Path

def main():
    print("🏗️ RC SANDBOX - EASY START LAUNCHER")
    print("=" * 50)
    print()
    print("Welcome! Let's get you started with RC Sandbox.")
    print()
    
    # Check if we're in the right directory
    if not Path("rc_sandbox_clean/index.html").exists():
        print("❌ Error: Can't find RC Sandbox files.")
        print("   Make sure you're running this from the RC Sandbox folder.")
        input("Press Enter to exit...")
        return
    
    print("Choose your experience:")
    print()
    print("1. 🌐 HTML Demo (No installation, works immediately)")
    print("2. 🚀 Professional Demo (Requires Python setup)")
    print("3. 📚 Help & Troubleshooting")
    print("4. ❌ Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🌐 Opening HTML Demo...")
            html_path = Path("rc_sandbox_clean/index.html").absolute()
            webbrowser.open(html_path.as_uri())
            print("✅ Demo opened in your browser!")
            print("💡 Tip: Allow camera access for the full experience")
            break
            
        elif choice == "2":
            print("\n🚀 Checking Python setup...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, "professional_demo_suite.py", "--list"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Python setup looks good!")
                    print("\nAvailable demos:")
                    print(result.stdout)
                    demo_choice = input("\nEnter demo name (or press Enter for 'investor_pitch'): ").strip()
                    if not demo_choice:
                        demo_choice = "investor_pitch"
                    
                    print(f"\n🚀 Starting {demo_choice} demo...")
                    subprocess.run([sys.executable, "professional_demo_suite.py", "--demo", demo_choice])
                else:
                    print("❌ Python setup needs work.")
                    print("Try running: pip install -r requirements-minimal.txt")
                    print("Or check TROUBLESHOOTING.md for help")
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Check TROUBLESHOOTING.md for help")
            break
            
        elif choice == "3":
            print("\n📚 Opening troubleshooting guide...")
            if Path("TROUBLESHOOTING.md").exists():
                webbrowser.open(Path("TROUBLESHOOTING.md").absolute().as_uri())
                print("✅ Troubleshooting guide opened!")
            else:
                print("❌ Troubleshooting guide not found")
            break
            
        elif choice == "4":
            print("\n👋 Thanks for trying RC Sandbox!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
