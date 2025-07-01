# 🔧 RC SANDBOX TROUBLESHOOTING GUIDE

## 🚨 **COMMON ISSUES & QUICK FIXES**

### **Issue: "Can't open HTML file"**

## Solution:

1. Right-click on `rc_sandbox_clean/index.html`
2. Select "Open with" → "Web Browser"
3. If that doesn't work, try Chrome or Firefox specifically

### **Issue: "Camera not working"**

## Solution:

1. Make sure your browser has camera permission
2. Try refreshing the page (F5)
3. Check if other apps are using your camera
4. Try a different browser

### **Issue: "pip install fails"**

## Solution:

1. Try: `pip install -r requirements-minimal.txt` (smaller download)
2. Update pip: `python -m pip install --upgrade pip`
3. On Windows: Use `py -m pip install -r requirements.txt`
4. On Mac/Linux: Use `python3 -m pip install -r requirements.txt`

### **Issue: "Python not found"**

## Solution:

1. Download Python from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Restart your computer
4. Try again

### **Issue: "Demo won't start"**

## Solution:

1. Start with the HTML demo first: `rc_sandbox_clean/index.html`
2. For Python demos, try: `python --version` to check Python works
3. Make sure you're in the right folder
4. Try: `python professional_demo_suite.py --list` to see available demos

## 📞 **STILL NEED HELP?**

### **Quick Support Options:**

- 📧 **Email**: support@rc-sandbox.com

- 💬 **Discord**: Join our community chat

- 🎥 **Video Help**: Watch our setup tutorials

- 📱 **Phone**: +1-555-RC-SANDBOX (business hours)

### **Before Contacting Support:**

1. Try the HTML demo first (no installation needed)
2. Note your operating system (Windows/Mac/Linux)
3. Note your Python version: `python --version`
4. Copy any error messages exactly

## 🎯 **SYSTEM REQUIREMENTS**

### **Minimum (HTML Demo Only):**

- Any modern web browser

- Webcam (optional but recommended)

- Internet connection (for initial download)

### **Full System:**

- Python 3.8 or newer

- 4GB RAM

- 2GB free disk space

- Windows 10/Mac OS 10.15/Ubuntu 18.04 or newer

## 🔄 **RESET TO FRESH STATE**

If everything is broken:
1. Delete the entire RC Sandbox folder
2. Re-download from GitHub
3. Start with the HTML demo: `rc_sandbox_clean/index.html`
4. If that works, try the Python installation again
