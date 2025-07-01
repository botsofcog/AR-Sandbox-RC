# RC Sandbox Integration Spec

## 1. Overview

Provide clear, actionable instructions for Augment AI to implement an RC construction sandbox system. Focus on sensor fusion, real-time terrain visualization, RC input handling, and AR overlay integration.

## 2. Focus Areas

1. **Sensor Fusion**
   - Integrate Kinect depth + Logitech RGB feed.
   - Calibrate depth-to-world mapping using planar marker (playing card).
2. **Realtime Terrain Engine**
   - Generate and update a mesh or grid from depth data.
   - Support click or tool-driven deformation before RC integration.
3. **RC Vehicle Input & Telemetry**
   - Stream speed, orientation, and control commands from Arduino/ESP32 over WebSocket/MQTT.
   - Map physical vehicle position to virtual coordinate system.
4. **UI / Game Logic**
   - Load provided SVG panels (inventory, HUD, objectives, tools).
   - Implement tool selection, objectives tracking, and scoring overlays.
5. **Deployment & Testing**
   - Provide Docker-compose or equivalent to run services.
   - Include unit tests and calibration scripts.

## 3. Functional Requirements

- **Depth Capture**: 30–60 FPS Kinect depth frames via `libfreenect` or WebUSB.

- **RGB Feed**: 30 FPS Logitech webcam, synchronized timestamp.

- **Mesh/Grid**: 100×75 or higher resolution, updated in <100 ms per frame.

- **Interaction**: Mouse/tool click to deform terrain; later replaced by vehicle attachments.

- **Telemetry**: JSON payloads with `{x, y, rotation, speed}` at 20 Hz.

## 4. Non-Functional Requirements

- **Latency**: End-to-end under 200 ms.

- **Modularity**: Sensor, engine, UI, and telemetry modules must be decoupled.

- **Extensibility**: Allow swapping depth cameras or vehicle types.

- **Stability**: Handle dropped frames gracefully; auto-reconnect sensors.

## 5. Implementation Phases

### Phase A: POC Refinement

- Merge RGB + depth into single demo.

- Validate mesh update pipeline.

- Load UI panels and basic admin controls.

### Phase B: RC Telemetry Integration

- Establish WebSocket/MQTT channel for vehicle data.

- Translate telemetry into interactive tool actions (e.g., plow).

### Phase C: Physical Sand Loop

- Use Kinect to detect real sand displacement.

- Project updated mesh onto sandbox via projector.

- Calibrate and align continuously with marker tracking.

## 6. AI Developer Guidelines

- Use Three.js for web-based mesh or Unity C# for game engine.

- Scaffold FastAPI/Node.js backend for depth and telemetry streams.

- Write calibration scripts in Python with OpenCV.

- Document endpoints, configs, and data formats in README.md.

## 7. File Structure

```

/project
  /assets
    inventory_panel.svg
    top_hud_bar.svg
    objectives_panel.svg
    tool_icons_grid.svg
  /backend
    depth_server.py
    telemetry_server.py
  /frontend
    index.html
    js/terrain.js
    js/ui.js
  capture_photos.py
  rc_sandbox_spec.md

```

## 8. Deliverables

- `depth_server.py`: streams depth frames over WebSocket.

- `telemetry_server.py`: streams RC telemetry.

- Frontend demo with integrated UI and terrain.

- Calibration scripts and unit tests.

- Deployment config (Docker-compose).

## 9. Quality Assurance

- Provide test cases for depth accuracy and mesh fidelity.

- Include sample data and expected outputs.

- Validate telemetry mapping with simulated RC inputs.

---

## Strictly adhere to this spec when generating code, modules, and configuration files.
