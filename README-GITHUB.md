# 🏗️ AR Sandbox RC - Professional Construction Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Kinect v1](https://img.shields.io/badge/Kinect-v1%20Xbox%20360-green.svg)](https://en.wikipedia.org/wiki/Kinect)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Status](https://img.shields.io/badge/status-WORKING-brightgreen.svg)](https://github.com/botsofcog/AR-Sandbox-RC)

> **Professional ecosystem with 30+ HTML demos, backend systems, JavaScript core systems, sample projects, and comprehensive documentation. Evolution from HTML sandbox demo into a real-world RC construction game with physical sand, depth sensors, AR overlays, and real RC vehicles.**

## 🎯 **Project Vision**

Transform a digital AR sandbox into a **real-world RC construction game** featuring:
- 🏗️ **Physical sand** with real-time terrain tracking
- 📡 **Depth sensors/LiDAR** for precise topology mapping  
- 🎮 **AR overlays** via projectors for immersive visualization
- 🚛 **Real RC vehicles** for authentic construction simulation
- 🏆 **Multiplayer scoring** and competitive gameplay
- 🎨 **Museum-quality interface** with professional controls

## ✨ **Key Features**

### 🔧 **Hardware Integration**
- **Kinect v1 (Xbox 360)** - Primary depth sensing
- **Multiple webcams** - RGB capture and backup depth estimation  
- **Triple camera fusion** - Comprehensive terrain analysis
- **RC construction vehicles** - Physical interaction capability
- **Projector system** - AR overlay projection

### 🎮 **Interactive Demos**
- **30+ HTML demonstrations** with various interaction modes
- **Color-changing pixels/squares** responding to hand movement
- **3D isometric view toggle** for enhanced visualization
- **Real-time height detection** from webcam and Kinect
- **Physics simulations** - Water, fire, steam, particle effects
- **Construction tools** - Excavators, bulldozers, dump trucks

### 🌊 **Advanced Physics**
- **Real-time water simulation** with flow dynamics
- **Particle effects** for realistic material behavior
- **Dynamic weather systems** affecting terrain
- **Elevation-based materials** (sand, dirt, grass, rock, snow)
- **Topographic visualization** with contour lines

## 🚀 **Quick Start**

### Prerequisites
```bash
# Python 3.8+ with required packages
pip install opencv-python numpy websockets freenect

# Kinect v1 drivers (Windows)
# Install libusbK drivers via Zadig for all 4 Kinect devices
```

### 🔐 **SSH Setup (Recommended)**
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key and add to GitHub
cat ~/.ssh/id_ed25519.pub

# 4. Test SSH connection
ssh -T git@github.com

# 5. Clone repository with SSH
git clone git@github.com:botsofcog/AR-Sandbox-RC.git
```

📋 **For detailed SSH setup instructions, see [SSH_SETUP.md](SSH_SETUP.md)**

### 🎯 **Launch the Working Demo**
```bash
# 1. Start the triple camera fusion system
python triple_camera_fusion_system.py --stream

# 2. Start HTTP server for demos
python -m http.server 8000

# 3. Open the working demo
# Navigate to: http://localhost:8000/working-ar-fixed.html
```

### 🎮 **Controls**
- **Hand Movement** → Height changes in real-time
- **V Key** → Toggle 3D isometric view
- **C Key** → Calibrate webcam baseline
- **Space** → Reset terrain
- **Mouse** → Manual terrain sculpting

## 📁 **Project Structure**

```
AR-Sandbox-RC/
├── 🎮 HTML Demos/
│   ├── working-ar-fixed.html          # ⭐ Main working demo
│   ├── robust-ar-sandbox.html         # Professional interface
│   ├── ultimate-ar-sandbox.html       # Advanced features
│   └── voxel-ar-sandbox.html         # Voxel rendering
├── 🐍 Backend Systems/
│   ├── triple_camera_fusion_system.py # Multi-camera integration
│   ├── ar_sandbox_data_bridge.py     # System connector
│   └── working_ar_sandbox/           # Professional AR sandbox
├── 🎨 Frontend Assets/
│   ├── js/                          # JavaScript modules
│   ├── css/                         # Styling and themes
│   └── assets/                      # SVG icons and graphics
├── 📊 Sample Projects/
│   ├── Magic-Sand-master/           # Reference implementation
│   └── open_AR_Sandbox-main/       # Community samples
└── 📚 Documentation/
    ├── AUGMENT_AI_INTEGRATION_PLAN.md # Development roadmap
    ├── FINAL_COMPLETION_REPORT.md    # Project status
    └── calibration_files/            # Sensor calibration
```

## 🎨 **Visual Features**

### Elevation-Based Color Mapping
- 🟦 **Navy/Purple/Black** → Deepest water/lowest points
- 🔵 **Blue** → Sea level water
- 🟫 **Sand+Blue** → Shorelines and beaches  
- 🟫 **Sand** → Base terrain level
- 🟠 **Orange** → Low elevation (dirt/sediment)
- 🟢 **Green** → Medium elevation (grass/vegetation)
- 🔴 **Red** → High elevation (stone/rock)
- 🟡 **Yellow** → Mountain rock
- ⚪ **White** → Snow peaks (highest elevation)

### Real-time Effects
- **Topographic contour lines** with black outlines
- **3D isometric projection** for depth visualization
- **Smooth color transitions** between elevation zones
- **Dynamic lighting effects** for enhanced realism

## 🔧 **Technical Implementation**

### Multi-Camera Fusion
```python
# Triple camera system integration
kinect_depth + kinect_rgb + logitech_webcam → unified_topology
```

### WebSocket Data Flow
```javascript
// Real-time streaming architecture
Triple_Camera_Fusion → WebSocket(8767) → HTML_Demo → Canvas_Rendering
```

### Magic Sand Processing
```python
# Depth-to-elevation conversion
raw_kinect_depth → magic_sand_processing → normalized_elevation → color_mapping
```

## 🏆 **Development Achievements**

- ✅ **72+ hours** of development across multiple sessions
- ✅ **Working physics** - Water, fire, vehicles, particle effects
- ✅ **Triple camera integration** - Kinect + dual webcams
- ✅ **Real-time streaming** at 10+ FPS
- ✅ **Professional UI/UX** with museum-quality interface
- ✅ **Comprehensive documentation** and testing
- ✅ **Modular architecture** for easy expansion

## 🎬 **Demo Screenshots**

### Working AR Sandbox Demo
![Working Demo](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=Color-Changing+Squares+%2B+3D+Isometric+View)

### Triple Camera Fusion System
![Camera System](https://via.placeholder.com/800x400/2d3748/ffffff?text=Kinect+Depth+%2B+RGB+%2B+Webcam+Fusion)

### Real-time Topology Mapping
![Topology](https://via.placeholder.com/800x400/4a5568/ffffff?text=Elevation-Based+Color+Mapping)

## 🤝 **Contributing**

This project follows an **integration-focused approach**:
- 🔄 **Build upon existing code** rather than recreating from scratch
- 📦 **Mix and match features** from different versions
- 🧪 **Rapid prototyping** with thorough testing
- 🛡️ **Zero changes policy** for deployment - preserve existing functionality

## 📄 **License**

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 **Acknowledgments**

- **Magic Sand Project** - Reference implementation for depth processing
- **OpenKinect Community** - Kinect v1 driver support  
- **AR Sandbox Community** - Inspiration and technical guidance
- **Bokeh/OpenCV Teams** - Essential libraries for visualization and computer vision

---

**🎯 Ready to build the future of interactive construction simulation!**
