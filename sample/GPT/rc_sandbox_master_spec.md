# RC Sandbox Master Specification

This document consolidates both the integration and UI specifications for the RC sandbox project, providing a single source-of-truth for Augment AI to implement all required modules and designs.

---

## Integration Specification

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

---

## UI Design Specification

# RC Sandbox UI Design Specification

## 1. Purpose

Provide Augment AI with a detailed, production-grade UI style guide and boilerplate for the AR/RC sandbox project. Focus on clarity, real-world HUD aesthetics, and projection legibility.

---

## 2. Color Palette

- **Background Panels:** `rgba(30, 30, 30, 0.75)` (smoked charcoal, semi-transparent)

- **Primary Accent:** `#E0C32A` (muted gold/yellow)

- **Secondary Accent:** `#4CAF50` (muted green)

- **Text & Icons:** `#FFFFFF` (white)

- **Shadows:** `0 4px 12px rgba(0,0,0,0.6)`

## 3. Typography

- **Font Family:** `"Roboto", sans-serif`

- **Headers:** `font-size: 1.25rem; font-weight: 500;`

- **Body Text:** `font-size: 1rem; font-weight: 400;`

- **Monospace:** `"Roboto Mono", monospace` for readouts.

## 4. Component Descriptions

### 4.1 Speedometer Gauge

- **Type:** Circular gauge with tick marks at 10-unit intervals.

- **Needle:** Thin line `2px` long pivoting from center.

- **Value Display:** Numeric at gauge center in monospace.

- **CSS Variables:**

  ```css

  --gauge-size: 120px;
  --gauge-border: 4px solid rgba(255,255,255,0.8);
  --gauge-needle-color: #E0C32A;
  ```

### 4.2 XP / Progress Bar

- **Type:** Rounded rectangle with 8px corner radius.

- **Fill:** Horizontal gradient from `#4CAF50` to `#E0C32A`.

- **Animation:** Smooth fill transition `0.5s ease-in-out`.

- **CSS Variables:**

  ```css

  --progress-height: 16px;
  --progress-border: 2px solid rgba(255,255,255,0.5);
  ```

### 4.3 Inventory & Tools Panel

- **Type:** Grid of icon buttons (3×2).

- **Button Size:** `64px × 64px`.

- **Hover State:** `background: rgba(255,255,255,0.1); transform: scale(1.05); transition: 0.2s`.

- **Selected State:** `border: 2px solid #E0C32A`.

### 4.4 Objectives Card List

- **Type:** Vertical list of cards.

- **Card Style:** `background: rgba(50,50,50,0.8); border-radius: 8px; padding: 8px; margin-bottom: 6px`.

- **Completion:** Checkmark icon slides in, opacity transition `0.3s`.

## 5. Samples

### 5.1 CSS Variables

```css

:root {
  --panel-bg: rgba(30,30,30,0.75);
  --accent-primary: #E0C32A;
  --accent-secondary: #4CAF50;
  --text-color: #FFFFFF;
  --shadow: 0 4px 12px rgba(0,0,0,0.6);
}

```

### 5.2 HTML Boilerplate

```html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RC Sandbox HUD</title>
  <link rel="stylesheet" href="styles/ui.css">
  <style>
    :root { /* include CSS variables from above */ }
    .panel { background: var(--panel-bg); box-shadow: var(--shadow); border-radius: 10px; padding: 8px; }
    .gauge { width: var(--gauge-size); height: var(--gauge-size); border: var(--gauge-border); border-radius: 50%; position: relative; }
    .gauge .needle { width: 2px; height: 50%; background: var(--gauge-needle-color); position: absolute; top: 50%; left: 50%; transform-origin: bottom center; }
    .progress { width: 200px; height: var(--progress-height); border: var(--progress-border); border-radius: 8px; overflow: hidden; }
    .progress .fill { height: 100%; background: linear-gradient(90deg, var(--accent-secondary), var(--accent-primary)); transition: width 0.5s ease-in-out; }
  </style>
</head>
<body>
  <div id="hud-container">
    <div id="speed-panel" class="panel">
      <div class="gauge">
        <div class="needle" id="speed-needle"></div>
        <div class="value" id="speed-value">0</div>
      </div>
    </div>
    <div id="xp-panel" class="panel">
      <div class="progress">
        <div class="fill" id="xp-fill" style="width: 0%;"></div>
      </div>
      <div class="value" id="xp-value">0 XP</div>
    </div>
    <!-- Add inventory, objectives, tools panels similarly -->
  </div>
  <script>
    // Example dynamic update
    function setSpeed(v) {
      const needle = document.getElementById('speed-needle');
      needle.style.transform = \`rotate(\${v * 1.8}deg) translate(-50%, -100%)\`;
      document.getElementById('speed-value').textContent = v;
    }
    function setXP(pct) {
      document.getElementById('xp-fill').style.width = pct + '%';
      document.getElementById('xp-value').textContent = pct + ' XP';
    }
  </script>
</body>
</html>

```

---

## Instructions for Augment AI:

- Use these specs to generate refined SVG/PNG assets at multiple resolutions (1×, 2×).

- Output a `styles/ui.css` file containing the variables and component styles.

- Provide updated HTML boilerplate with links to assets and live JS snippets for dynamic updates.
