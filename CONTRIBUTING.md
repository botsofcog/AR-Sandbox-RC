# 🤝 Contributing to AR Sandbox RC

Thank you for your interest in contributing to the AR Sandbox RC project! This document provides guidelines and information for contributors.

## 🎯 **Project Philosophy**

This project follows an **integration-focused approach**:

- 🔄 **Build upon existing code** rather than recreating from scratch
- 📦 **Mix and match features** from different versions  
- 🧪 **Rapid prototyping** with thorough testing
- 🛡️ **Zero changes policy** for deployment - preserve existing functionality
- 🎨 **Museum-quality interface** standards

## 🚀 **Getting Started**

### Prerequisites
- Python 3.8+
- Kinect v1 (Xbox 360) with libusbK drivers
- Multiple webcams (recommended)
- Basic knowledge of JavaScript/HTML5 Canvas
- Understanding of computer vision concepts

### Development Setup

#### 🔐 **SSH Setup (Recommended)**
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# 3. Add public key to GitHub (copy output and paste in GitHub settings)
cat ~/.ssh/id_ed25519.pub

# 4. Test connection
ssh -T git@github.com
```

#### 📥 **Clone and Setup**
```bash
# Clone with SSH (recommended)
git clone git@github.com:botsofcog/AR-Sandbox-RC.git
cd AR-Sandbox-RC

# Install Python dependencies
pip install -r requirements.txt

# Test the system
python triple_camera_fusion_system.py --test
```

📋 **For detailed SSH setup, see [SSH_SETUP.md](SSH_SETUP.md)**

## 📋 **How to Contribute**

### 🐛 **Bug Reports**
When reporting bugs, please include:
- **System specifications** (OS, Python version, hardware)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Console logs** and error messages
- **Screenshots/videos** if applicable

### ✨ **Feature Requests**
For new features:
- **Check existing issues** to avoid duplicates
- **Describe the use case** and benefits
- **Consider integration** with existing systems
- **Provide mockups** or examples if possible

### 🔧 **Code Contributions**

#### Pull Request Process
1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow coding standards** (see below)
4. **Test thoroughly** with multiple scenarios
5. **Update documentation** as needed
6. **Commit with clear messages**
7. **Submit pull request** with detailed description

#### Coding Standards

**Python Code:**
```python
# Use descriptive variable names
kinect_depth_data = capture_kinect_frame()

# Add comprehensive logging
logger.info(f"[SUCCESS] Kinect depth sensor initialized: {resolution}")

# Handle errors gracefully
try:
    process_depth_data(frame)
except Exception as e:
    logger.error(f"[ERROR] Depth processing failed: {e}")
```

**JavaScript Code:**
```javascript
// Use clear class and method names
class ARSandboxRenderer {
    updateFromKinectData(frameData) {
        console.log('📡 Processing Kinect depth data');
        // Implementation
    }
}

// Add status updates for user feedback
updateStatus('Kinect Connected');
```

**HTML Structure:**
```html
<!-- Use semantic HTML with clear IDs -->
<div id="terrain-canvas-container" class="sandbox-display">
    <canvas id="terrain-canvas"></canvas>
</div>

<!-- Include accessibility features -->
<button onclick="toggle3D()" aria-label="Toggle 3D isometric view">
    🎮 3D View
</button>
```

## 🎨 **Design Guidelines**

### Visual Standards
- **Museum-quality interface** with clean, professional appearance
- **Elevation-based color mapping** following the established scheme
- **Smooth animations** and transitions
- **Responsive design** for different screen sizes
- **Clear visual feedback** for all user interactions

### Color Scheme
```css
/* Elevation colors (maintain consistency) */
--water-deep: #000033;      /* Navy - deepest water */
--water-shallow: #0066ff;   /* Blue - sea level */
--terrain-sand: #ffcc66;    /* Sand - base level */
--terrain-grass: #00cc00;   /* Green - medium elevation */
--terrain-rock: #ff6600;    /* Orange/Red - high elevation */
--terrain-snow: #ffffff;    /* White - peaks */
```

## 🧪 **Testing Guidelines**

### Required Tests
- **Hardware compatibility** (different Kinect units, webcams)
- **Cross-browser testing** (Chrome, Firefox, Edge)
- **Performance testing** (frame rates, memory usage)
- **Error handling** (device disconnection, invalid data)
- **User interaction** (all controls and modes)

### Test Scenarios
```bash
# Test triple camera fusion
python triple_camera_fusion_system.py --test

# Test individual demos
# Open each HTML demo and verify:
# - Webcam initialization
# - Hand movement detection  
# - 3D mode toggle
# - Kinect data integration
```

## 📚 **Documentation**

### Required Documentation
- **Code comments** for complex algorithms
- **README updates** for new features
- **API documentation** for new methods
- **User guides** for new functionality
- **Integration notes** for system changes

### Documentation Style
```markdown
## 🎯 **Feature Name**

Brief description of what the feature does.

### Usage
```bash
# Command example
python script.py --option
```

### Parameters
- `--option`: Description of what this does
```

## 🏗️ **Architecture Guidelines**

### System Integration
- **Preserve existing functionality** when adding features
- **Use WebSocket communication** for real-time data
- **Implement proper error handling** and recovery
- **Follow modular design** patterns
- **Maintain backward compatibility**

### Performance Considerations
- **Optimize for real-time processing** (target 10+ FPS)
- **Minimize memory usage** for continuous operation
- **Use efficient algorithms** for computer vision tasks
- **Implement proper cleanup** for resources

## 🔍 **Code Review Process**

### Review Criteria
- ✅ **Functionality** - Does it work as intended?
- ✅ **Integration** - Does it work with existing systems?
- ✅ **Performance** - Does it maintain real-time operation?
- ✅ **Code Quality** - Is it readable and maintainable?
- ✅ **Documentation** - Is it properly documented?
- ✅ **Testing** - Has it been thoroughly tested?

### Review Timeline
- **Initial review** within 48 hours
- **Feedback incorporation** and re-review as needed
- **Final approval** and merge

## 🎖️ **Recognition**

Contributors will be recognized in:
- **README.md** acknowledgments section
- **Release notes** for significant contributions
- **Project documentation** for major features

## 📞 **Getting Help**

- **GitHub Issues** - For bugs and feature requests
- **Discussions** - For questions and general discussion
- **Documentation** - Check existing docs first
- **Code Examples** - Look at working demos for patterns

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make AR Sandbox RC even better! 🚀**
