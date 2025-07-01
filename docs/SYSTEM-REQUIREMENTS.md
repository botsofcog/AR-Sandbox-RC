# 📋 System Requirements - AR Sandbox RC

## 🎯 **Camera System Requirements**

### **MINIMUM SYSTEM (110% Integration)**

**Required for Full Operation:**

#### **Hardware - REQUIRED**
- ✅ **Kinect v1 (Xbox 360)** with USB adapter and power supply
- ✅ **1x USB Webcam** (any compatible webcam)
- ✅ **Windows 10/11** computer
- ✅ **2x Available USB ports** (USB 3.0 recommended)

#### **Software - REQUIRED**
- ✅ **Python 3.8+** installed
- ✅ **OpenCV** (`pip install opencv-python`)
- ✅ **NumPy** (`pip install numpy`)
- ✅ **libfreenect** for Kinect support

#### **Camera Configuration - MINIMUM**
```
AXIS 1 (Side View - Kinect) - REQUIRED
├── Kinect Depth Sensor [REQUIRED]
└── Kinect RGB Camera [REQUIRED]

AXIS 2 (Secondary Perspective) - REQUIRED
└── Webcam 1 [REQUIRED]
```

**Result: 110% Integration - Full AR Sandbox Operation**

---

### **MAXIMUM SYSTEM (125% Integration)**

**Optional Enhancement:**

#### **Additional Hardware - OPTIONAL**
- 🔄 **Additional USB Webcam** for maximum coverage
- 🔄 **Extra USB port** for 4th camera

#### **Camera Configuration - MAXIMUM**
```
AXIS 1 (Side View - Kinect) - REQUIRED
├── Kinect Depth Sensor [REQUIRED]
└── Kinect RGB Camera [REQUIRED]

AXIS 2 (Secondary Perspective) - REQUIRED
└── Webcam 1 [REQUIRED]

AXIS 3 (Tertiary Perspective) - OPTIONAL
└── Webcam 2 [OPTIONAL]
```

**Result: 125% Integration - Maximum Coverage**

---

## 📊 **Integration Level Breakdown**

### **110% Integration (3 Cameras) - TARGET MINIMUM**
- **Status**: ✅ **FULL OPERATION**
- **Cameras**: Kinect Depth + Kinect RGB + Webcam 1
- **Functionality**: Complete AR sandbox with multi-axis coverage
- **Performance**: Excellent accuracy and reliability
- **Recommendation**: **This is the target configuration**

### **125% Integration (4 Cameras) - OPTIONAL MAXIMUM**
- **Status**: 🚀 **ENHANCED OPERATION**
- **Cameras**: Kinect Depth + Kinect RGB + Webcam 1 + Webcam 2
- **Functionality**: Maximum coverage with redundancy
- **Performance**: Ultimate accuracy and reliability
- **Recommendation**: **Nice to have, but not required**

### **67% Integration (2 Cameras) - REDUCED**
- **Status**: ⚠️ **REDUCED FUNCTIONALITY**
- **Cameras**: Kinect Depth + Kinect RGB (or + Webcam 1)
- **Functionality**: Basic AR sandbox operation
- **Performance**: Limited accuracy, missing multi-axis coverage
- **Recommendation**: **Add 3rd camera to reach 110%**

### **33% Integration (1 Camera) - MINIMAL**
- **Status**: ❌ **MINIMAL FUNCTIONALITY**
- **Cameras**: Single camera only
- **Functionality**: Very limited operation
- **Performance**: Poor accuracy, no multi-axis coverage
- **Recommendation**: **Add cameras to reach minimum 110%**

---

## 🔧 **Hardware Specifications**

### **Kinect v1 (Xbox 360) - REQUIRED**
- **Model**: Xbox 360 Kinect (white horizontal design)
- **Connection**: USB adapter + power supply required
- **Drivers**: libfreenect (install via Zadig)
- **Capabilities**: 
  - Depth sensing: 640x480 @ 30fps
  - RGB camera: 640x480 @ 30fps
  - IR projection for depth mapping

### **USB Webcam - REQUIRED (1x) + OPTIONAL (1x)**
- **Minimum**: Any USB webcam with 640x480 resolution
- **Recommended**: Logitech C925e or similar HD webcam
- **Connection**: USB 2.0 or 3.0
- **Capabilities**:
  - RGB video: 640x480 @ 30fps minimum
  - Autofocus support preferred
  - DirectShow compatibility

### **Computer Requirements**
- **OS**: Windows 10/11 (64-bit recommended)
- **CPU**: Intel i5 or AMD equivalent (multi-core recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **USB**: Multiple USB ports (USB 3.0 recommended for bandwidth)
- **Graphics**: DirectX 11 compatible (for web rendering)

---

## 🚀 **Quick Setup Validation**

### **Step 1: Check Hardware**
```bash
# Verify cameras in Device Manager
# Should see:
# - Xbox NUI Camera (Kinect)
# - USB Video Device (Webcam 1)
# - USB Video Device (Webcam 2) [OPTIONAL]
```

### **Step 2: Test System**
```bash
cd "AR Sandbox RC"
python puzzle_piece_3_camera_system.py
```

### **Step 3: Validate Integration Level**
**Target Output for 110% (Minimum):**
```
🧩 PUZZLE PIECE RESULTS:
   Kinect depth sensor: ✅ WORKING
   Kinect RGB camera: ✅ WORKING
   Webcam 1: ✅ WORKING
   Webcam 2: ❌ FAILED (or not connected)
   Total active cameras: 3/4

🎉 EXCELLENT! 3/4 cameras working - 110%+ integration!
```

**Bonus Output for 125% (Maximum):**
```
🧩 PUZZLE PIECE RESULTS:
   Kinect depth sensor: ✅ WORKING
   Kinect RGB camera: ✅ WORKING
   Webcam 1: ✅ WORKING
   Webcam 2: ✅ WORKING
   Total active cameras: 4/4

🎉 MAXIMUM COVERAGE! ALL 4 CAMERAS WORKING!
   🚀 125% INTEGRATION ACHIEVED!
```

---

## ⚠️ **Important Notes**

### **3 Cameras is the Minimum**
- **110% Integration** requires exactly 3 cameras minimum
- **4th camera is optional** for enhanced coverage
- **System will operate fully** with 3 cameras
- **4th camera provides redundancy** and additional perspective

### **Camera Positioning**
```
     WEBCAM 2 (OVERHEAD) [OPTIONAL]
            ↓
    ┌─────────────────────────┐
    │                         │
    │    SANDBOX WITH SAND    │ ← KINECT (Side view) [REQUIRED]
    │                         │
    └─────────────────────────┘
            ↑
     WEBCAM 1 (ANGLE VIEW) [REQUIRED]
```

### **USB Bandwidth Considerations**
- **3 cameras**: Usually works on any modern computer
- **4 cameras**: May require USB 3.0 or powered hub
- **Recommendation**: Test with 3 cameras first, add 4th if desired

---

## 📞 **Support**

### **If You Can't Reach 110% (3 Cameras)**
1. Check USB connections and try different ports
2. Verify all cameras are recognized in Device Manager
3. Install Kinect drivers using Zadig
4. Close other applications using cameras
5. Run diagnostic: `python smart_camera_detection_system.py`

### **If You Have 110% but Want 125%**
1. Connect additional USB webcam
2. Run test again: `python puzzle_piece_3_camera_system.py`
3. System should automatically detect and use 4th camera

**Remember: 110% (3 cameras) is the target for full operation. 125% (4 cameras) is a bonus!**
