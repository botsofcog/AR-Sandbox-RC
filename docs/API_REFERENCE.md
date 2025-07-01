# RC SANDBOX - API REFERENCE

## 📷 **4-Camera System API - 125% Integration**

### **PuzzlePiece4CameraSystem Class**

Main class for managing the 4-camera maximum coverage system.

```python
from puzzle_piece_3_camera_system import PuzzlePiece4CameraSystem

# Initialize 4-camera system
camera_system = PuzzlePiece4CameraSystem()
```

#### **Methods**

##### `initialize_all_puzzle_pieces() -> bool`
Initializes all 4 cameras using puzzle piece architecture.

**Returns**: `True` if 2+ cameras operational, `False` otherwise

**Example**:
```python
success = camera_system.initialize_all_puzzle_pieces()
if success:
    print("🎉 4-Camera system operational!")
```

##### `capture_4_camera_frame() -> dict`
Captures synchronized frame from all 4 camera sources.

**Returns**: Dictionary with frame data and metadata

**Response Format**:
```json
{
    "timestamp": 1672531200.123,
    "kinect_depth": "numpy_array",
    "kinect_rgb": "numpy_array",
    "webcam1_frame": "numpy_array",
    "webcam2_frame": "numpy_array",
    "puzzle_metadata": {
        "total_sources": 4,
        "active_sources": ["kinect_depth", "kinect_rgb", "webcam1_frame", "webcam2_frame"],
        "integration_level": "100%",
        "method": "PUZZLE_PIECES_4_CAMERA",
        "maximum_coverage": true
    }
}
```

##### `cleanup()`
Cleans up all camera resources and threads.

**Example**:
```python
camera_system.cleanup()
```

### **Integration Levels**

- **125% Integration** - All 4 cameras operational (Maximum Coverage)
- **110% Integration** - 3+ cameras operational (Excellent Coverage)
- **100% Integration** - 2+ cameras operational (Good Coverage)

## 🔌 WebSocket API

### Connection Endpoints

#### Depth Server

- **URL**: `ws://localhost:8765`

- **Purpose**: Real-time depth data streaming

- **Protocol**: WebSocket with JSON messages

#### Telemetry Server

- **URL**: `ws://localhost:8766`

- **Purpose**: Vehicle fleet management and control

- **Protocol**: WebSocket with JSON messages

#### Streaming Server

- **URL**: `ws://localhost:8767`

- **Purpose**: 24/7 streaming and viewer interaction

- **Protocol**: WebSocket with JSON messages

---

## 📊 Depth Server API

### Message Types

#### Depth Data Stream

```json

{
    "type": "depth_frame",
    "timestamp": 1640995200.123,
    "format": "uint16",
    "width": 640,
    "height": 480,
    "data": "base64_encoded_depth_data",
    "calibration": {
        "fx": 365.456,
        "fy": 365.456,
        "cx": 320.0,
        "cy": 240.0
    }
}

```

#### Calibration Command

```json

{
    "type": "calibration",
    "action": "set_points",
    "points": [
        {
            "real_world": {"x": 0.0, "y": 0.0, "z": 0.0},
            "pixel": {"x": 100, "y": 150},
            "depth": 1200
        }
    ]
}

```

#### Configuration Update

```json

{
    "type": "config",
    "depth_mode": "NFOV_UNBINNED",
    "fps": 30,
    "exposure": "auto",
    "gain": 128
}

```

### Response Messages

#### Status Response

```json

{
    "type": "status",
    "connected": true,
    "calibrated": true,
    "fps": 29.8,
    "frame_count": 1234,
    "errors": []
}

```

#### Error Response

```json

{
    "type": "error",
    "code": "E001",
    "message": "Kinect initialization failed",
    "details": "USB connection not found"
}

```

---

## 🚛 Telemetry Server API

### Vehicle Control Commands

#### Move Vehicle

```json

{
    "type": "vehicle_command",
    "vehicle_id": "EX001",
    "action": "move",
    "target_x": 150.5,
    "target_y": 200.3,
    "speed": 2.5
}

```

#### Start Work

```json

{
    "type": "vehicle_command",
    "vehicle_id": "BD001",
    "action": "work",
    "work_type": "level",
    "duration": 30.0,
    "intensity": 0.8
}

```

#### Stop Vehicle

```json

{
    "type": "vehicle_command",
    "vehicle_id": "DT001",
    "action": "stop",
    "emergency": false
}

```

#### Fleet Command

```json

{
    "type": "fleet_command",
    "action": "start_mission",
    "mission_type": "flood_defense",
    "vehicles": ["EX001", "BD001", "DT001"],
    "parameters": {
        "urgency": "high",
        "coordination": true
    }
}

```

### Vehicle Status Updates

#### Individual Vehicle Status

```json

{
    "type": "vehicle_status",
    "vehicle_id": "EX001",
    "position": {"x": 150.5, "y": 200.3, "rotation": 45.0},
    "status": "working",
    "battery": 85.2,
    "task": {
        "type": "excavate",
        "progress": 0.65,
        "estimated_completion": 45.0
    },
    "health": {
        "operational": true,
        "warnings": [],
        "errors": []
    }
}

```

#### Fleet Status

```json

{
    "type": "fleet_status",
    "total_vehicles": 5,
    "active_vehicles": 3,
    "mission_status": "in_progress",
    "overall_progress": 0.42,
    "vehicles": {
        "EX001": {"status": "working", "battery": 85.2},
        "BD001": {"status": "moving", "battery": 92.1},
        "DT001": {"status": "idle", "battery": 78.5}
    }
}

```

---

## 📺 Streaming Server API

### Viewer Interaction

#### Chat Command

```json

{
    "type": "chat_command",
    "username": "viewer123",
    "command": "!excavate",
    "parameters": ["north", "deep"],
    "timestamp": 1640995200.123,
    "user_level": "subscriber"
}

```

#### Viewer Vote

```json

{
    "type": "viewer_vote",
    "poll_id": "mission_choice",
    "option": "flood_defense",
    "username": "viewer456",
    "weight": 1.0
}

```

### Stream Control

#### Start Stream

```json

{
    "type": "stream_control",
    "action": "start",
    "quality": "1080p",
    "bitrate": 3000,
    "audio": true
}

```

#### Update Stream Settings

```json

{
    "type": "stream_control",
    "action": "update_settings",
    "settings": {
        "title": "RC Sandbox Live Demo",
        "category": "Science & Technology",
        "tags": ["sandbox", "construction", "interactive"]
    }
}

```

---

## 🎮 Frontend JavaScript API

### Terrain Engine

#### Initialize Terrain

```javascript

const terrain = new TerrainEngine(canvas);
terrain.initializeTerrain();

```

#### Modify Terrain

```javascript

// Raise terrain at position
terrain.modifyTerrain(x, y, 0.1, 'raise');

// Lower terrain at position
terrain.modifyTerrain(x, y, -0.1, 'lower');

// Smooth terrain area
terrain.smoothTerrain(x, y, radius);

```

#### Physics Control

```javascript

// Enable physics simulation
terrain.enablePhysicsSimulation();

// Start rain
terrain.startRain(0.5); // intensity 0-1

// Set wind
terrain.setWind(5.0, 180); // speed, direction

// Add water
terrain.addWaterAt(x, y, 0.2); // position, amount

```

### Vehicle Fleet Manager

#### Initialize Fleet

```javascript

const fleet = new VehicleFleetManager(terrainEngine);

```

#### Control Vehicles

```javascript

// Select vehicle
fleet.selectVehicle('EX001');

// Move vehicle
fleet.commandVehicle('EX001', {
    action: 'move',
    x: 150,
    y: 200
});

// Start mission
fleet.startFloodDefenseMission();

```

#### Get Fleet Status

```javascript

const status = fleet.getFleetStatus();
console.log(`Active vehicles: ${status.activeVehicles}`);

```

### Mission System

#### Start Mission

```javascript

const missions = new MissionSystem(terrainEngine, fleet, ui);
missions.startMission('flood_defense');

```

#### Track Progress

```javascript

const progress = missions.getMissionProgress();
console.log(`Progress: ${progress.percentage}%`);

```

### Physics Engine

#### Configure Physics

```javascript

const physics = new PhysicsEngine(terrainEngine);

// Set weather
physics.setWeather({
    windSpeed: 5.0,
    windDirection: 180,
    precipitation: 0.3,
    temperature: 25
});

// Get physics data
const data = physics.getPhysicsData();

```

---

## 🔧 Configuration API

### System Configuration

#### Load Configuration

```javascript

const config = await fetch('/api/config').then(r => r.json());

```

#### Update Configuration

```javascript

await fetch('/api/config', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        physics: {
            enabled: true,
            quality: 'high'
        },
        rendering: {
            fps_target: 60,
            particles: 1000
        }
    })
});

```

### Calibration API

#### Save Calibration

```javascript

const calibration = {
    kinect: {
        transformation_matrix: [[1,0,0,0],[0,1,0,0],[0,0,1,0]],
        error: 0.05
    },
    projector: {
        keystone: {
            topLeft: {x: 0, y: 0},
            topRight: {x: 1, y: 0},
            bottomLeft: {x: 0, y: 1},
            bottomRight: {x: 1, y: 1}
        }
    }
};

await fetch('/api/calibration', {
    method: 'POST',
    body: JSON.stringify(calibration)
});

```

---

## 📈 Analytics API

### Performance Metrics

#### Get System Metrics

```javascript

const metrics = await fetch('/api/metrics').then(r => r.json());
/*
{
    "fps": 59.8,
    "latency_ms": 25.3,
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "active_connections": 3
}
*/

```

#### Get Usage Statistics

```javascript

const stats = await fetch('/api/stats').then(r => r.json());
/*
{
    "session_duration": 1800,
    "terrain_modifications": 156,
    "vehicles_controlled": 8,
    "missions_completed": 2
}
*/

```

---

## 🚨 Error Handling

### Error Codes

| Code | Category | Description |
|------|----------|-------------|
| E001 | Hardware | Kinect initialization failed |
| E002 | Calibration | Calibration data invalid |
| E003 | Network | WebSocket connection timeout |
| E004 | Performance | Insufficient system resources |
| E005 | Projection | Projector alignment failed |
| E006 | Vehicle | Vehicle communication error |
| E007 | Mission | Mission execution failed |
| E008 | Physics | Physics simulation error |
| E009 | Streaming | Stream connection failed |
| E010 | Storage | File system error |

### Error Response Format

```json

{
    "error": {
        "code": "E003",
        "message": "WebSocket connection timeout",
        "details": "Failed to connect to telemetry server",
        "timestamp": 1640995200.123,
        "context": {
            "service": "telemetry_server",
            "endpoint": "ws://localhost:8766",
            "retry_count": 3
        },
        "suggestions": [
            "Check if telemetry server is running",
            "Verify network connectivity",
            "Check firewall settings"
        ]
    }
}

```

---

## 🔐 Authentication API

### Login

```javascript

const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'secure_password'
    })
});

const {token} = await response.json();

```

### Authenticated Requests

```javascript

const response = await fetch('/api/protected_endpoint', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

```

---

## 📝 Event System

### Event Types

#### System Events

- `system.startup` - System initialization complete

- `system.shutdown` - System shutdown initiated

- `system.error` - System error occurred

#### Hardware Events

- `kinect.connected` - Kinect sensor connected

- `kinect.disconnected` - Kinect sensor disconnected

- `kinect.calibrated` - Calibration completed

#### Vehicle Events

- `vehicle.moved` - Vehicle position changed

- `vehicle.task_started` - Vehicle started new task

- `vehicle.task_completed` - Vehicle completed task

- `vehicle.battery_low` - Vehicle battery below threshold

#### Mission Events

- `mission.started` - Mission began

- `mission.completed` - Mission finished successfully

- `mission.failed` - Mission failed

- `mission.objective_completed` - Objective achieved

### Event Subscription

```javascript

// Subscribe to events
websocket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'event') {
        switch (data.event_type) {
            case 'vehicle.moved':
                updateVehiclePosition(data.vehicle_id, data.position);
                break;
            case 'mission.completed':
                showMissionComplete(data.mission_id, data.score);
                break;
        }
    }
});

```

---

## 📚 API Version: 2.0
## 🔄 Last Updated: 2024-01-01
## 📞 Support: api-support@rc-sandbox.com
