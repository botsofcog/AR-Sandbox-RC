# RC SANDBOX - DEPLOYMENT GUIDE

## 🚀 QUICK START DEPLOYMENT

### One-Click Professional Demo

```bash

# Launch investor-ready demonstration

python professional_demo_suite.py --demo investor_pitch

# Launch technical deep dive

python professional_demo_suite.py --demo technical_deep_dive

# Launch quick showcase

python professional_demo_suite.py --demo quick_showcase

```text

### Basic HTML Demo

```bash

# Open the enhanced HTML demo

open rc_sandbox_clean/index.html

# or

python -m http.server 8000

# Then visit: http://localhost:8000/rc_sandbox_clean/

```text

---

## 📋 SYSTEM REQUIREMENTS

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+

- **CPU**: 4-core Intel i5 or AMD Ryzen 5

- **RAM**: 8GB DDR4

- **GPU**: DirectX 11 compatible (Intel HD 4000+)

- **Storage**: 10GB free space

- **Network**: Broadband internet for streaming features

### Recommended Requirements

- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+

- **CPU**: 8-core Intel i7 or AMD Ryzen 7

- **RAM**: 16GB DDR4

- **GPU**: NVIDIA RTX 3060 or AMD RX 6600 XT

- **Storage**: 20GB SSD space

- **Network**: Gigabit Ethernet

### Hardware Components

- **Depth Sensor**: Azure Kinect DK (recommended) or Xbox 360 Kinect

- **Projector**: 1080p+ HDMI/DisplayPort projector (3000+ lumens recommended)

- **Sandbox**: 4'×3' to 10'×8' sand table with fine sand

- **RC Vehicles**: K'NEX construction vehicles with wireless control

- **Computer**: Meeting minimum requirements above

---

## 🔧 INSTALLATION GUIDE

### 1. Clone Repository

```bash

git clone https://github.com/your-org/rc-sandbox.git
cd rc-sandbox

```text

### 2. Install Python Dependencies

```bash

# Create virtual environment

python -m venv venv

# Activate virtual environment

# Windows:

venv\Scripts\activate

# macOS/Linux:

source venv/bin/activate

# Install dependencies

pip install -r requirements.txt

```text

### 3. Install Hardware Drivers

#### Azure Kinect DK

```bash

# Download and install Azure Kinect SDK

# Windows: https://docs.microsoft.com/en-us/azure/kinect-dk/sensor-sdk-download

# Linux: sudo apt install libk4a1.4-dev

# Install Python bindings

pip install pykinect-azure

```text

#### Xbox 360 Kinect

```bash

# Install libfreenect

# Windows: Download from https://openkinect.org/wiki/Getting_Started

# macOS: brew install libfreenect

# Linux: sudo apt install libfreenect-dev

# Install Python bindings

pip install freenect

```text

### 4. Configure Hardware

#### Kinect Calibration

```bash

# Run interactive calibration

python backend/kinect_calibration.py --kinect azure

# Or load existing calibration

python backend/kinect_calibration.py --load calibration.json

```text

#### Projector Setup

1. Connect projector to computer via HDMI/DisplayPort
2. Position projector above sandbox at 45-60° angle
3. Run projection calibration:

```bash

python frontend/js/projection_overlay.js --calibrate

```text

---

## 🏗️ DEPLOYMENT SCENARIOS

### Scenario 1: Educational Institution

**Target**: Schools, universities, STEM programs

**Setup**:

- Single sandbox installation in classroom

- Teacher control interface

- Student interaction modes

- Curriculum integration

**Configuration**:

```bash

python professional_demo_suite.py --demo educational_stem --duration 45

```text

### Scenario 2: Museum Installation

**Target**: Science museums, visitor centers

**Setup**:

- Public-facing interactive display

- Autonomous operation with visitor interaction

- Safety systems and monitoring

- Remote management capabilities

**Configuration**:

```bash

python professional_demo_suite.py --demo museum_interactive --duration 60

```text

### Scenario 3: Corporate Training

**Target**: Engineering firms, construction companies

**Setup**:

- Professional meeting room installation

- Project visualization and collaboration

- Client presentation capabilities

- Data export and reporting

**Configuration**:

```bash

python professional_demo_suite.py --demo technical_deep_dive --duration 30

```text

### Scenario 4: Entertainment Venue

**Target**: Arcades, family entertainment centers

**Setup**:

- High-throughput public installation

- Game modes and scoring

- Social media integration

- Revenue tracking

**Configuration**:

```bash

python professional_demo_suite.py --demo streaming_showcase --duration 120

```text

---

## 🌐 NETWORK DEPLOYMENT

### Local Network Setup

```bash

# Start backend services

python backend/depth_server.py --port 8765
python backend/telemetry_server.py --port 8766

# Start web server

python -m http.server 8000 --directory frontend

# Access via: http://localhost:8000

```text

### Cloud Deployment (AWS/Azure)

```bash

# Deploy to cloud instance

# 1. Launch EC2/VM instance with GPU support

# 2. Install dependencies

# 3. Configure security groups for ports 8765-8767

# 4. Set up SSL certificates for HTTPS

# 5. Configure domain name and DNS

# Example Docker deployment

docker build -t rc-sandbox .
docker run -p 8000:8000 -p 8765:8765 -p 8766:8766 rc-sandbox

```text

### Streaming Setup (Twitch Integration)

```bash

# Configure streaming credentials

export TWITCH_STREAM_KEY="your_stream_key"
export TWITCH_OAUTH_TOKEN="oauth:your_token"

# Start streaming server

python backend/streaming_server.py --channel your_channel

```text

---

## 🔒 SECURITY CONFIGURATION

### Network Security

```bash

# Configure firewall rules

# Allow ports 8765-8767 for WebSocket connections

# Allow port 8000 for web interface

# Block all other incoming connections

# Windows Firewall

netsh advfirewall firewall add rule name="RC Sandbox" dir=in action=allow protocol=TCP localport=8000,8765-8767

# Linux iptables

sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8765:8767 -j ACCEPT

```text

### Access Control

```python

# Configure user authentication in config.json

{
    "authentication": {
        "enabled": true,
        "admin_password": "secure_admin_password",
        "user_accounts": {
            "teacher": "teacher_password",
            "student": "student_password"
        }
    }
}

```text

---

## 📊 MONITORING & MAINTENANCE

### Performance Monitoring

```bash

# View real-time performance metrics

python professional_demo_suite.py --demo technical_deep_dive --monitor

# Generate performance report

python -c "
from professional_demo_suite import ProfessionalDemoSuite
suite = ProfessionalDemoSuite()
report = suite.generate_professional_report()
print(json.dumps(report, indent=2))
"

```text

### Log Management

```bash

# View system logs

tail -f logs/rc_sandbox.log

# Rotate logs

logrotate /etc/logrotate.d/rc_sandbox

```text

### Backup & Recovery

```bash

# Backup configuration and calibration data

tar -czf backup_$(date +%Y%m%d).tar.gz \
    *.json \
    calibration/ \
    logs/ \
    user_data/

# Restore from backup

tar -xzf backup_20240101.tar.gz

```text

---

## 🚨 TROUBLESHOOTING

### Common Issues

#### Kinect Not Detected

```bash

# Check USB connection and drivers

lsusb | grep Microsoft  # Linux

# or

Device Manager > Cameras  # Windows

# Reinstall drivers

pip uninstall pykinect-azure
pip install pykinect-azure --force-reinstall

```text

#### Poor Performance

```bash

# Check system resources

htop  # Linux/macOS

# or

Task Manager  # Windows

# Reduce quality settings

python professional_demo_suite.py --demo quick_showcase --low-quality

```text

#### WebSocket Connection Failed

```bash

# Check if ports are available

netstat -an | grep 8765
netstat -an | grep 8766

# Restart services

pkill -f depth_server
pkill -f telemetry_server
python backend/depth_server.py &
python backend/telemetry_server.py &

```text

#### Projection Misalignment

```bash

# Recalibrate projector

python frontend/js/projection_overlay.js --recalibrate

# Manual keystone adjustment

# Use projector's built-in keystone correction

# Then run software calibration

```text

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| E001 | Kinect initialization failed | Check USB connection and drivers |
| E002 | Calibration file not found | Run calibration process |
| E003 | WebSocket connection timeout | Check network and firewall settings |
| E004 | Insufficient system resources | Close other applications or upgrade hardware |
| E005 | Projection mapping failed | Recalibrate projector alignment |

---

## 📈 SCALING & OPTIMIZATION

### Multi-Sandbox Network

```bash

# Configure master-slave setup

python backend/network_manager.py --mode master --port 9000
python backend/network_manager.py --mode slave --master-ip 192.168.1.100

```text

### Performance Optimization

```python

# Optimize for different scenarios

config = {
    "education": {
        "fps_target": 30,
        "physics_quality": "medium",
        "particle_count": 500
    },
    "museum": {
        "fps_target": 60,
        "physics_quality": "high",
        "particle_count": 1000
    },
    "corporate": {
        "fps_target": 60,
        "physics_quality": "ultra",
        "particle_count": 2000
    }
}

```text

### Load Balancing

```bash

# Distribute processing across multiple machines

python backend/load_balancer.py --nodes node1,node2,node3

```text

---

## 📞 SUPPORT & MAINTENANCE

### Support Channels

- **Documentation**: https://rc-sandbox.readthedocs.io

- **Community Forum**: https://community.rc-sandbox.com

- **Technical Support**: support@rc-sandbox.com

- **Emergency Hotline**: +1-800-RC-SANDBOX

### Maintenance Schedule

- **Daily**: Check system logs and performance metrics

- **Weekly**: Update software and security patches

- **Monthly**: Full system backup and hardware inspection

- **Quarterly**: Recalibration and performance optimization

- **Annually**: Hardware refresh and major updates

### Service Level Agreements

- **Response Time**: 4 hours for critical issues

- **Resolution Time**: 24 hours for system-down issues

- **Uptime Guarantee**: 99.5% for production installations

- **Support Hours**: 24/7 for enterprise customers

---

## 🎯 SUCCESS METRICS

### Key Performance Indicators

- **System Uptime**: >99.5%

- **Frame Rate**: >30 FPS sustained

- **Latency**: <50ms WebSocket response

- **User Engagement**: >5 minutes average session

- **Error Rate**: <0.1% of operations

### Monitoring Dashboard

```bash

# Launch monitoring dashboard

python monitoring/dashboard.py --port 8080

# Access via: http://localhost:8080/dashboard

```text

---

---

## 📚 ADDITIONAL DOCUMENTATION

### Technical Documentation

- **API Reference**: `docs/API_REFERENCE.md`

- **Architecture Guide**: `docs/ARCHITECTURE.md`

- **Development Setup**: `docs/DEVELOPMENT.md`

- **Testing Guide**: `docs/TESTING.md`

### User Manuals

- **Operator Manual**: `docs/OPERATOR_MANUAL.md`

- **Maintenance Guide**: `docs/MAINTENANCE.md`

- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

- **Safety Guidelines**: `docs/SAFETY.md`

### Training Materials

- **Installation Training**: `training/installation/`

- **Operation Training**: `training/operation/`

- **Maintenance Training**: `training/maintenance/`

- **Video Tutorials**: `training/videos/`

---

## 🏆 Deployment Status: PRODUCTION READY

*This deployment guide ensures successful installation and operation of the RC Sandbox system across all target environments and use cases.*
