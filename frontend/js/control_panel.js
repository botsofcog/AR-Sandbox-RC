/**
 * Control Panel Integration - Farming sim-style control interface
 * FPV camera feeds, head tracking, and immersive vehicle operation
 * Part of the RC Sandbox modular architecture
 */

class ControlPanelInterface {
    constructor(vehicleFleet, terrainEngine) {
        this.vehicleFleet = vehicleFleet;
        this.terrainEngine = terrainEngine;

        // Control panel state
        this.activeVehicle = null;
        this.fpvMode = false;
        this.headTrackingEnabled = false;
        this.controlMode = 'overview'; // overview, fpv, manual

        // Camera system
        this.cameras = new Map();
        this.activeCameraFeed = null;
        this.cameraStreams = new Map();

        // Head tracking
        this.headTracker = null;
        this.headPosition = { x: 0, y: 0, z: 0 };
        this.headRotation = { pitch: 0, yaw: 0, roll: 0 };

        // Control interfaces
        this.joystickController = null;
        this.keyboardControls = new Map();
        this.touchControls = new Map();

        // UI elements
        this.controlPanelElement = null;
        this.fpvDisplay = null;
        this.instrumentCluster = null;
        this.miniMap = null;

        // Performance monitoring
        this.frameRate = 60;
        this.latency = 0;
        this.connectionStatus = 'connected';

        this.initializeControlPanel();

        console.log('🎮 Control Panel Interface initialized');
    }

    initializeControlPanel() {
        this.createControlPanelUI();
        this.setupCameraSystem();
        this.initializeHeadTracking();
        this.setupControlInputs();
        this.startPerformanceMonitoring();
    }

    createControlPanelUI() {
        // Create main control panel container
        this.controlPanelElement = document.createElement('div');
        this.controlPanelElement.id = 'control-panel';
        this.controlPanelElement.className = 'control-panel-container';

        // Apply farming sim-style CSS
        this.controlPanelElement.innerHTML = `
            <div class="control-panel-header">
                <div class="panel-title">🚛 VEHICLE CONTROL CENTER</div>
                <div class="connection-status">
                    <span class="status-indicator ${this.connectionStatus}"></span>
                    <span class="status-text">${this.connectionStatus.toUpperCase()}</span>
                </div>
            </div>

            <div class="control-panel-main">
                <!-- FPV Camera Feed -->
                <div class="fpv-section">
                    <div class="fpv-header">
                        <span class="fpv-title">📹 FIRST PERSON VIEW</span>
                        <div class="camera-controls">
                            <button class="camera-btn" onclick="controlPanel.toggleFPV()">
                                <span id="fpv-toggle-text">ENABLE FPV</span>
                            </button>
                            <button class="camera-btn" onclick="controlPanel.switchCamera()">
                                📷 SWITCH CAM
                            </button>
                        </div>
                    </div>
                    <div class="fpv-display" id="fpv-display">
                        <div class="fpv-placeholder">
                            <div class="fpv-icon">📹</div>
                            <div class="fpv-text">Select vehicle to enable FPV</div>
                        </div>
                        <canvas id="fpv-canvas" width="640" height="480" style="display: none;"></canvas>
                    </div>
                    <div class="fpv-overlay">
                        <div class="crosshair"></div>
                        <div class="fpv-info">
                            <div class="vehicle-info">
                                <span id="active-vehicle-id">No Vehicle</span>
                                <span id="vehicle-status">Idle</span>
                            </div>
                            <div class="camera-info">
                                <span id="camera-angle">0°</span>
                                <span id="zoom-level">1.0x</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Vehicle Selection Panel -->
                <div class="vehicle-selection">
                    <div class="section-title">🚛 VEHICLE FLEET</div>
                    <div class="vehicle-grid" id="vehicle-grid">
                        <!-- Vehicle buttons will be populated dynamically -->
                    </div>
                </div>

                <!-- Control Interface -->
                <div class="control-interface">
                    <div class="section-title">🎮 CONTROLS</div>
                    <div class="control-modes">
                        <button class="mode-btn active" data-mode="overview" onclick="controlPanel.setControlMode('overview')">
                            🗺️ OVERVIEW
                        </button>
                        <button class="mode-btn" data-mode="fpv" onclick="controlPanel.setControlMode('fpv')">
                            👁️ FPV
                        </button>
                        <button class="mode-btn" data-mode="manual" onclick="controlPanel.setControlMode('manual')">
                            🎮 MANUAL
                        </button>
                    </div>

                    <div class="control-inputs" id="control-inputs">
                        <!-- Control inputs will be populated based on mode -->
                    </div>
                </div>

                <!-- Instrument Cluster -->
                <div class="instrument-cluster">
                    <div class="section-title">📊 INSTRUMENTS</div>
                    <div class="instruments-grid">
                        <div class="instrument">
                            <div class="instrument-label">Speed</div>
                            <div class="instrument-value" id="speed-display">0.0</div>
                            <div class="instrument-unit">m/s</div>
                        </div>
                        <div class="instrument">
                            <div class="instrument-label">Battery</div>
                            <div class="instrument-value" id="battery-display">100</div>
                            <div class="instrument-unit">%</div>
                        </div>
                        <div class="instrument">
                            <div class="instrument-label">Task</div>
                            <div class="instrument-value" id="task-display">Idle</div>
                            <div class="instrument-unit"></div>
                        </div>
                        <div class="instrument">
                            <div class="instrument-label">Position</div>
                            <div class="instrument-value" id="position-display">0,0</div>
                            <div class="instrument-unit">m</div>
                        </div>
                    </div>
                </div>

                <!-- Mini Map -->
                <div class="mini-map-section">
                    <div class="section-title">🗺️ TACTICAL MAP</div>
                    <div class="mini-map" id="mini-map">
                        <canvas id="mini-map-canvas" width="200" height="150"></canvas>
                        <div class="map-overlay">
                            <div class="map-scale">Scale: 1:16</div>
                            <div class="map-coordinates" id="map-coordinates">0.0, 0.0</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="control-panel-footer">
                <div class="performance-info">
                    <span>FPS: <span id="fps-counter">60</span></span>
                    <span>Latency: <span id="latency-counter">0</span>ms</span>
                    <span>Head Tracking: <span id="head-tracking-status">OFF</span></span>
                </div>
                <div class="emergency-controls">
                    <button class="emergency-btn" onclick="controlPanel.emergencyStop()">
                        🚨 EMERGENCY STOP
                    </button>
                </div>
            </div>
        `;

        // Add to document
        document.body.appendChild(this.controlPanelElement);

        // Apply CSS styles
        this.applyControlPanelStyles();

        // Initialize sub-components
        this.fpvDisplay = document.getElementById('fpv-display');
        this.instrumentCluster = document.querySelector('.instrument-cluster');
        this.miniMap = document.getElementById('mini-map-canvas');

        console.log('🎮 Control panel UI created');
    }

    applyControlPanelStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .control-panel-container {
                position: fixed;
                top: 0;
                right: 0;
                width: 400px;
                height: 100vh;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-left: 3px solid #4CAF50;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: -5px 0 15px rgba(0,0,0,0.3);
            }

            .control-panel-header {
                background: #333;
                padding: 15px;
                border-bottom: 2px solid #4CAF50;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .panel-title {
                font-weight: bold;
                font-size: 14px;
                color: #4CAF50;
            }

            .connection-status {
                display: flex;
                align-items: center;
                gap: 5px;
            }

            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #4CAF50;
                animation: pulse 2s infinite;
            }

            .status-indicator.disconnected {
                background: #F44336;
            }

            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }

            .control-panel-main {
                padding: 10px;
            }

            .fpv-section {
                margin-bottom: 20px;
                border: 1px solid #555;
                border-radius: 5px;
                overflow: hidden;
            }

            .fpv-header {
                background: #444;
                padding: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .fpv-title {
                font-weight: bold;
                color: #2196F3;
            }

            .camera-controls {
                display: flex;
                gap: 5px;
            }

            .camera-btn {
                background: #2196F3;
                border: none;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 10px;
                transition: background 0.3s;
            }

            .camera-btn:hover {
                background: #1976D2;
            }

            .fpv-display {
                position: relative;
                width: 100%;
                height: 200px;
                background: #000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .fpv-placeholder {
                text-align: center;
                color: #666;
            }

            .fpv-icon {
                font-size: 48px;
                margin-bottom: 10px;
            }

            .fpv-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
            }

            .crosshair {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 20px;
                height: 20px;
                border: 2px solid #4CAF50;
                border-radius: 50%;
            }

            .crosshair::before,
            .crosshair::after {
                content: '';
                position: absolute;
                background: #4CAF50;
            }

            .crosshair::before {
                top: -2px;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                height: 24px;
            }

            .crosshair::after {
                left: -2px;
                top: 50%;
                transform: translateY(-50%);
                width: 24px;
                height: 2px;
            }

            .fpv-info {
                position: absolute;
                top: 10px;
                left: 10px;
                right: 10px;
                display: flex;
                justify-content: space-between;
                color: #4CAF50;
                font-size: 11px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            }

            .section-title {
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid #555;
            }

            .vehicle-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
                margin-bottom: 15px;
            }

            .vehicle-btn {
                background: #444;
                border: 1px solid #666;
                color: white;
                padding: 10px;
                border-radius: 3px;
                cursor: pointer;
                text-align: center;
                transition: all 0.3s;
                font-size: 11px;
            }

            .vehicle-btn:hover {
                background: #555;
                border-color: #4CAF50;
            }

            .vehicle-btn.active {
                background: #4CAF50;
                border-color: #4CAF50;
            }

            .vehicle-btn.offline {
                background: #333;
                color: #666;
                cursor: not-allowed;
            }

            .control-modes {
                display: flex;
                gap: 5px;
                margin-bottom: 10px;
            }

            .mode-btn {
                flex: 1;
                background: #444;
                border: 1px solid #666;
                color: white;
                padding: 8px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 10px;
                transition: all 0.3s;
            }

            .mode-btn:hover {
                background: #555;
            }

            .mode-btn.active {
                background: #2196F3;
                border-color: #2196F3;
            }

            .instruments-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }

            .instrument {
                background: #333;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px;
                text-align: center;
            }

            .instrument-label {
                font-size: 10px;
                color: #999;
                margin-bottom: 3px;
            }

            .instrument-value {
                font-size: 16px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 2px;
            }

            .instrument-unit {
                font-size: 9px;
                color: #666;
            }

            .mini-map {
                position: relative;
                border: 1px solid #555;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .map-overlay {
                position: absolute;
                bottom: 5px;
                left: 5px;
                right: 5px;
                display: flex;
                justify-content: space-between;
                font-size: 9px;
                color: #4CAF50;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            }

            .control-panel-footer {
                background: #333;
                padding: 10px 15px;
                border-top: 2px solid #4CAF50;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .performance-info {
                display: flex;
                gap: 15px;
                font-size: 10px;
                color: #999;
            }

            .emergency-btn {
                background: #F44336;
                border: none;
                color: white;
                padding: 10px 15px;
                border-radius: 3px;
                cursor: pointer;
                font-weight: bold;
                font-size: 11px;
                animation: emergencyPulse 2s infinite;
            }

            @keyframes emergencyPulse {
                0% { background: #F44336; }
                50% { background: #D32F2F; }
                100% { background: #F44336; }
            }

            .emergency-btn:hover {
                background: #D32F2F;
            }
        `;

        document.head.appendChild(style);
    }

    setupCameraSystem() {
        // Initialize virtual cameras for each vehicle
        if (this.vehicleFleet) {
            this.vehicleFleet.getAllVehicles().forEach(vehicle => {
                this.cameras.set(vehicle.id, {
                    vehicleId: vehicle.id,
                    position: { x: 0, y: 0, z: 2 }, // Camera offset from vehicle
                    rotation: { pitch: -15, yaw: 0, roll: 0 },
                    fov: 75,
                    active: false,
                    stream: null
                });
            });
        }

        // Setup FPV canvas
        const fpvCanvas = document.getElementById('fpv-canvas');
        if (fpvCanvas) {
            this.fpvContext = fpvCanvas.getContext('2d');
            this.fpvContext.fillStyle = '#000';
            this.fpvContext.fillRect(0, 0, fpvCanvas.width, fpvCanvas.height);
        }

        // Populate vehicle grid
        this.populateVehicleGrid();

        console.log('📹 Camera system initialized');
    }

    populateVehicleGrid() {
        const vehicleGrid = document.getElementById('vehicle-grid');
        if (!vehicleGrid || !this.vehicleFleet) return;

        vehicleGrid.innerHTML = '';

        this.vehicleFleet.getAllVehicles().forEach(vehicle => {
            const vehicleBtn = document.createElement('button');
            vehicleBtn.className = 'vehicle-btn';
            vehicleBtn.dataset.vehicleId = vehicle.id;
            vehicleBtn.innerHTML = `
                <div class="vehicle-icon">${this.getVehicleIcon(vehicle.type)}</div>
                <div class="vehicle-id">${vehicle.id}</div>
                <div class="vehicle-status">${vehicle.taskStatus}</div>
            `;

            vehicleBtn.addEventListener('click', () => {
                this.selectVehicle(vehicle.id);
            });

            vehicleGrid.appendChild(vehicleBtn);
        });
    }

    getVehicleIcon(vehicleType) {
        const icons = {
            excavator: '🚜',
            bulldozer: '🚛',
            dump_truck: '🚚',
            crane: '🏗️',
            compactor: '🚧'
        };
        return icons[vehicleType] || '🚛';
    }

    initializeHeadTracking() {
        // Initialize head tracking using MediaPipe or WebRTC
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            this.setupWebcamHeadTracking();
        } else {
            console.warn('⚠️ Head tracking not available - webcam access required');
        }
    }

    async setupWebcamHeadTracking() {
        try {
            // Request webcam access for head tracking
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });

            // Create hidden video element for head tracking
            const video = document.createElement('video');
            video.style.display = 'none';
            video.srcObject = stream;
            video.play();

            document.body.appendChild(video);

            // Initialize face detection (simplified implementation)
            this.headTracker = {
                video: video,
                enabled: false,
                lastPosition: { x: 0, y: 0 },
                calibrationCenter: { x: 320, y: 240 }
            };

            console.log('👁️ Head tracking initialized');

        } catch (error) {
            console.warn('⚠️ Head tracking setup failed:', error);
        }
    }

    setupControlInputs() {
        // Keyboard controls
        this.setupKeyboardControls();

        // Gamepad/joystick support
        this.setupGamepadControls();

        // Touch controls for mobile
        this.setupTouchControls();

        // Update control interface based on mode
        this.updateControlInterface();
    }

    setupKeyboardControls() {
        const keyMap = {
            'KeyW': 'forward',
            'KeyS': 'backward',
            'KeyA': 'left',
            'KeyD': 'right',
            'KeyQ': 'rotate_left',
            'KeyE': 'rotate_right',
            'Space': 'action',
            'ShiftLeft': 'boost',
            'KeyF': 'toggle_fpv',
            'KeyC': 'switch_camera',
            'KeyH': 'toggle_head_tracking'
        };

        document.addEventListener('keydown', (event) => {
            if (!this.activeVehicle) return;

            const action = keyMap[event.code];
            if (action) {
                event.preventDefault();
                this.handleControlInput(action, true);
            }
        });

        document.addEventListener('keyup', (event) => {
            if (!this.activeVehicle) return;

            const action = keyMap[event.code];
            if (action) {
                event.preventDefault();
                this.handleControlInput(action, false);
            }
        });

        console.log('⌨️ Keyboard controls initialized');
    }

    setupGamepadControls() {
        // Check for gamepad support
        if (navigator.getGamepads) {
            this.gamepadSupported = true;
            this.startGamepadPolling();
        }
    }

    startGamepadPolling() {
        const pollGamepads = () => {
            const gamepads = navigator.getGamepads();

            for (let i = 0; i < gamepads.length; i++) {
                const gamepad = gamepads[i];
                if (gamepad && this.activeVehicle) {
                    this.processGamepadInput(gamepad);
                }
            }

            requestAnimationFrame(pollGamepads);
        };

        pollGamepads();
        console.log('🎮 Gamepad polling started');
    }

    processGamepadInput(gamepad) {
        // Left stick for movement
        const leftStickX = gamepad.axes[0];
        const leftStickY = gamepad.axes[1];

        // Right stick for camera/rotation
        const rightStickX = gamepad.axes[2];
        const rightStickY = gamepad.axes[3];

        // Buttons
        const buttons = gamepad.buttons;

        // Apply deadzone
        const deadzone = 0.1;

        if (Math.abs(leftStickX) > deadzone || Math.abs(leftStickY) > deadzone) {
            this.sendVehicleMovement(leftStickX, -leftStickY);
        }

        if (Math.abs(rightStickX) > deadzone) {
            this.sendVehicleRotation(rightStickX);
        }

        // Action buttons
        if (buttons[0] && buttons[0].pressed) { // A button
            this.handleControlInput('action', true);
        }
    }

    setupTouchControls() {
        // Virtual joystick for mobile devices
        if ('ontouchstart' in window) {
            this.createVirtualJoystick();
        }
    }

    createVirtualJoystick() {
        const joystickContainer = document.createElement('div');
        joystickContainer.className = 'virtual-joystick';
        joystickContainer.innerHTML = `
            <div class="joystick-base">
                <div class="joystick-stick"></div>
            </div>
        `;

        // Add touch event handlers
        let isDragging = false;
        let startPos = { x: 0, y: 0 };

        joystickContainer.addEventListener('touchstart', (e) => {
            isDragging = true;
            const touch = e.touches[0];
            startPos = { x: touch.clientX, y: touch.clientY };
        });

        joystickContainer.addEventListener('touchmove', (e) => {
            if (!isDragging) return;

            const touch = e.touches[0];
            const deltaX = touch.clientX - startPos.x;
            const deltaY = touch.clientY - startPos.y;

            // Normalize to -1 to 1 range
            const normalizedX = Math.max(-1, Math.min(1, deltaX / 50));
            const normalizedY = Math.max(-1, Math.min(1, deltaY / 50));

            this.sendVehicleMovement(normalizedX, -normalizedY);
        });

        joystickContainer.addEventListener('touchend', () => {
            isDragging = false;
            this.sendVehicleMovement(0, 0);
        });

        document.body.appendChild(joystickContainer);
        console.log('📱 Touch controls initialized');
    }

    startPerformanceMonitoring() {
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
    }

    updatePerformanceMetrics() {
        // Update FPS counter
        const fpsCounter = document.getElementById('fps-counter');
        if (fpsCounter) {
            fpsCounter.textContent = this.frameRate.toFixed(0);
        }

        // Update latency counter
        const latencyCounter = document.getElementById('latency-counter');
        if (latencyCounter) {
            latencyCounter.textContent = this.latency.toFixed(0);
        }

        // Update head tracking status
        const headTrackingStatus = document.getElementById('head-tracking-status');
        if (headTrackingStatus) {
            headTrackingStatus.textContent = this.headTrackingEnabled ? 'ON' : 'OFF';
        }
    }

    // Core control methods
    selectVehicle(vehicleId) {
        // Deselect previous vehicle
        if (this.activeVehicle) {
            const prevBtn = document.querySelector(`[data-vehicle-id="${this.activeVehicle}"]`);
            if (prevBtn) prevBtn.classList.remove('active');
        }

        // Select new vehicle
        this.activeVehicle = vehicleId;
        const vehicleBtn = document.querySelector(`[data-vehicle-id="${vehicleId}"]`);
        if (vehicleBtn) vehicleBtn.classList.add('active');

        // Update vehicle info display
        const activeVehicleId = document.getElementById('active-vehicle-id');
        if (activeVehicleId) activeVehicleId.textContent = vehicleId;

        // Enable camera for selected vehicle
        this.activateVehicleCamera(vehicleId);

        // Update instrument cluster
        this.updateInstrumentCluster();

        console.log(`🎯 Vehicle selected: ${vehicleId}`);
    }

    activateVehicleCamera(vehicleId) {
        // Deactivate all cameras
        this.cameras.forEach(camera => camera.active = false);

        // Activate selected vehicle camera
        const camera = this.cameras.get(vehicleId);
        if (camera) {
            camera.active = true;
            this.activeCameraFeed = vehicleId;

            if (this.fpvMode) {
                this.startFPVStream(vehicleId);
            }
        }
    }

    toggleFPV() {
        this.fpvMode = !this.fpvMode;

        const fpvToggleText = document.getElementById('fpv-toggle-text');
        const fpvCanvas = document.getElementById('fpv-canvas');
        const fpvPlaceholder = document.querySelector('.fpv-placeholder');

        if (this.fpvMode && this.activeVehicle) {
            // Enable FPV mode
            fpvToggleText.textContent = 'DISABLE FPV';
            fpvCanvas.style.display = 'block';
            fpvPlaceholder.style.display = 'none';

            this.startFPVStream(this.activeVehicle);

        } else {
            // Disable FPV mode
            fpvToggleText.textContent = 'ENABLE FPV';
            fpvCanvas.style.display = 'none';
            fpvPlaceholder.style.display = 'flex';

            this.stopFPVStream();
        }

        console.log(`📹 FPV mode: ${this.fpvMode ? 'ON' : 'OFF'}`);
    }

    startFPVStream(vehicleId) {
        if (!this.fpvContext) return;

        // Start rendering FPV view
        this.fpvRenderLoop = setInterval(() => {
            this.renderFPVView(vehicleId);
        }, 1000 / 30); // 30 FPS

        console.log(`📹 FPV stream started for ${vehicleId}`);
    }

    stopFPVStream() {
        if (this.fpvRenderLoop) {
            clearInterval(this.fpvRenderLoop);
            this.fpvRenderLoop = null;
        }

        console.log('📹 FPV stream stopped');
    }

    renderFPVView(vehicleId) {
        if (!this.fpvContext || !this.vehicleFleet) return;

        const vehicle = this.vehicleFleet.getVehicleById(vehicleId);
        if (!vehicle) return;

        const camera = this.cameras.get(vehicleId);
        if (!camera) return;

        // Clear canvas
        this.fpvContext.fillStyle = '#001122';
        this.fpvContext.fillRect(0, 0, 640, 480);

        // Simulate FPV view based on vehicle position and camera angle
        this.renderVehiclePerspective(vehicle, camera);

        // Add HUD overlay
        this.renderFPVHUD(vehicle);
    }

    renderVehiclePerspective(vehicle, camera) {
        // Calculate camera position relative to vehicle
        const cameraWorldX = vehicle.x + camera.position.x;
        const cameraWorldY = vehicle.y + camera.position.y;
        const cameraHeight = camera.position.z;

        // Render simplified 3D perspective view
        this.render3DView(cameraWorldX, cameraWorldY, cameraHeight, camera.rotation);
    }

    render3DView(cameraX, cameraY, cameraZ, cameraRotation) {
        // Simplified 3D rendering for FPV view
        const ctx = this.fpvContext;

        // Draw horizon line
        const horizonY = 240 + (cameraRotation.pitch * 2);

        // Sky
        const skyGradient = ctx.createLinearGradient(0, 0, 0, horizonY);
        skyGradient.addColorStop(0, '#87CEEB');
        skyGradient.addColorStop(1, '#E0F6FF');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 640, horizonY);

        // Ground
        const groundGradient = ctx.createLinearGradient(0, horizonY, 0, 480);
        groundGradient.addColorStop(0, '#8B7355');
        groundGradient.addColorStop(1, '#654321');
        ctx.fillStyle = groundGradient;
        ctx.fillRect(0, horizonY, 640, 480 - horizonY);

        // Draw terrain features if available
        if (this.terrainEngine) {
            this.renderTerrainFeatures(cameraX, cameraY, cameraZ, cameraRotation);
        }

        // Draw other vehicles
        this.renderOtherVehicles(cameraX, cameraY, cameraRotation);
    }

    renderTerrainFeatures(cameraX, cameraY, cameraZ, cameraRotation) {
        // Render visible terrain features in FPV view
        const ctx = this.fpvContext;
        const viewDistance = 100;
        const fov = 75 * Math.PI / 180;

        // Sample terrain points in front of camera
        for (let distance = 10; distance < viewDistance; distance += 10) {
            for (let angle = -fov/2; angle < fov/2; angle += fov/20) {
                const worldX = cameraX + Math.cos(cameraRotation.yaw + angle) * distance;
                const worldY = cameraY + Math.sin(cameraRotation.yaw + angle) * distance;

                // Get terrain height at this point
                const terrainHeight = this.getTerrainHeightAt(worldX, worldY);

                // Project to screen coordinates
                const screenX = 320 + (angle / fov) * 640;
                const screenY = 240 - (terrainHeight - cameraZ) * (100 / distance);

                // Draw terrain point
                if (screenY > 0 && screenY < 480) {
                    ctx.fillStyle = this.getTerrainColorAt(worldX, worldY);
                    ctx.fillRect(screenX - 1, screenY - 1, 2, 2);
                }
            }
        }
    }

    renderOtherVehicles(cameraX, cameraY, cameraRotation) {
        if (!this.vehicleFleet) return;

        const ctx = this.fpvContext;
        const vehicles = this.vehicleFleet.getAllVehicles();

        vehicles.forEach(vehicle => {
            if (vehicle.id === this.activeVehicle) return;

            // Calculate relative position
            const relativeX = vehicle.x - cameraX;
            const relativeY = vehicle.y - cameraY;
            const distance = Math.sqrt(relativeX * relativeX + relativeY * relativeY);

            if (distance < 50) { // Only render nearby vehicles
                // Calculate angle relative to camera
                const angle = Math.atan2(relativeY, relativeX) - cameraRotation.yaw;

                // Project to screen
                const screenX = 320 + Math.sin(angle) * (200 / distance);
                const screenY = 240 - (10 / distance); // Assume vehicle height

                if (screenX > 0 && screenX < 640 && screenY > 0 && screenY < 480) {
                    // Draw vehicle as colored rectangle
                    const size = Math.max(2, 20 / distance);
                    ctx.fillStyle = this.getVehicleColor(vehicle.type);
                    ctx.fillRect(screenX - size/2, screenY - size/2, size, size);

                    // Draw vehicle ID
                    ctx.fillStyle = 'white';
                    ctx.font = '12px monospace';
                    ctx.fillText(vehicle.id, screenX + size/2 + 2, screenY);
                }
            }
        });
    }

    renderFPVHUD(vehicle) {
        const ctx = this.fpvContext;

        // HUD elements
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 2;
        ctx.font = '14px monospace';
        ctx.fillStyle = '#00FF00';

        // Speed indicator
        const speed = Math.sqrt(vehicle.vx * vehicle.vx + vehicle.vy * vehicle.vy) || 0;
        ctx.fillText(`SPD: ${speed.toFixed(1)} m/s`, 10, 30);

        // Battery level
        ctx.fillText(`BAT: ${vehicle.batteryLevel.toFixed(0)}%`, 10, 50);

        // Task status
        ctx.fillText(`TASK: ${vehicle.taskStatus.toUpperCase()}`, 10, 70);

        // Compass
        this.renderCompass(ctx, vehicle.rotation || 0);

        // Artificial horizon
        this.renderArtificialHorizon(ctx);
    }

    renderCompass(ctx, heading) {
        const centerX = 580;
        const centerY = 50;
        const radius = 30;

        // Compass circle
        ctx.strokeStyle = '#00FF00';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.stroke();

        // North indicator
        ctx.fillStyle = '#FF0000';
        ctx.fillText('N', centerX - 5, centerY - radius - 5);

        // Heading line
        ctx.strokeStyle = '#FFFF00';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(
            centerX + Math.sin(heading) * radius * 0.8,
            centerY - Math.cos(heading) * radius * 0.8
        );
        ctx.stroke();

        // Heading text
        ctx.fillStyle = '#00FF00';
        ctx.fillText(`${Math.round(heading * 180 / Math.PI)}°`, centerX - 15, centerY + radius + 15);
    }

    renderArtificialHorizon(ctx) {
        const centerX = 320;
        const centerY = 240;
        const size = 60;

        // Horizon line
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(centerX - size, centerY);
        ctx.lineTo(centerX + size, centerY);
        ctx.stroke();

        // Center dot
        ctx.fillStyle = '#FFFF00';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
        ctx.fill();
    }

    // Utility methods
    getTerrainHeightAt(x, y) {
        if (!this.terrainEngine) return 0;

        // Convert world coordinates to grid coordinates
        const gridX = Math.floor(x / this.terrainEngine.cellWidth);
        const gridY = Math.floor(y / this.terrainEngine.cellHeight);

        if (gridX >= 0 && gridX < this.terrainEngine.gridWidth &&
            gridY >= 0 && gridY < this.terrainEngine.gridHeight) {
            const index = gridY * this.terrainEngine.gridWidth + gridX;
            return this.terrainEngine.heightmap[index] || 0;
        }

        return 0;
    }

    getTerrainColorAt(x, y) {
        const height = this.getTerrainHeightAt(x, y);

        // Simple height-based coloring
        if (height < 0.1) return '#4169E1'; // Water
        if (height < 0.3) return '#F4A460'; // Sand
        if (height < 0.6) return '#228B22'; // Grass
        return '#FFFFFF'; // Snow/peaks
    }

    getVehicleColor(vehicleType) {
        const colors = {
            excavator: '#FFD700',
            bulldozer: '#FF6347',
            dump_truck: '#32CD32',
            crane: '#FF69B4',
            compactor: '#8A2BE2'
        };
        return colors[vehicleType] || '#FFFFFF';
    }

    // Control input handlers
    handleControlInput(action, pressed) {
        if (!this.activeVehicle) return;

        switch (action) {
            case 'forward':
                this.sendVehicleMovement(0, pressed ? 1 : 0);
                break;
            case 'backward':
                this.sendVehicleMovement(0, pressed ? -1 : 0);
                break;
            case 'left':
                this.sendVehicleMovement(pressed ? -1 : 0, 0);
                break;
            case 'right':
                this.sendVehicleMovement(pressed ? 1 : 0, 0);
                break;
            case 'rotate_left':
                this.sendVehicleRotation(pressed ? -1 : 0);
                break;
            case 'rotate_right':
                this.sendVehicleRotation(pressed ? 1 : 0);
                break;
            case 'action':
                if (pressed) this.sendVehicleAction();
                break;
            case 'toggle_fpv':
                if (pressed) this.toggleFPV();
                break;
            case 'switch_camera':
                if (pressed) this.switchCamera();
                break;
            case 'toggle_head_tracking':
                if (pressed) this.toggleHeadTracking();
                break;
        }
    }

    sendVehicleMovement(x, y) {
        if (!this.vehicleFleet || !this.activeVehicle) return;

        // Apply head tracking offset if enabled
        if (this.headTrackingEnabled) {
            x += this.headPosition.x * 0.1;
            y += this.headPosition.y * 0.1;
        }

        this.vehicleFleet.commandVehicle(this.activeVehicle, {
            action: 'move',
            x: x,
            y: y,
            source: 'control_panel'
        });
    }

    sendVehicleRotation(rotation) {
        if (!this.vehicleFleet || !this.activeVehicle) return;

        this.vehicleFleet.commandVehicle(this.activeVehicle, {
            action: 'rotate',
            rotation: rotation,
            source: 'control_panel'
        });
    }

    sendVehicleAction() {
        if (!this.vehicleFleet || !this.activeVehicle) return;

        this.vehicleFleet.commandVehicle(this.activeVehicle, {
            action: 'work',
            source: 'control_panel'
        });
    }

    switchCamera() {
        if (!this.activeVehicle) return;

        const camera = this.cameras.get(this.activeVehicle);
        if (camera) {
            // Cycle through camera angles
            camera.rotation.pitch = (camera.rotation.pitch + 15) % 60 - 30;

            // Update camera angle display
            const cameraAngle = document.getElementById('camera-angle');
            if (cameraAngle) {
                cameraAngle.textContent = `${camera.rotation.pitch}°`;
            }
        }
    }

    toggleHeadTracking() {
        this.headTrackingEnabled = !this.headTrackingEnabled;

        if (this.headTrackingEnabled && this.headTracker) {
            this.startHeadTracking();
        } else {
            this.stopHeadTracking();
        }

        console.log(`👁️ Head tracking: ${this.headTrackingEnabled ? 'ON' : 'OFF'}`);
    }

    startHeadTracking() {
        if (!this.headTracker) return;

        this.headTracker.enabled = true;

        // Start head position detection loop
        this.headTrackingLoop = setInterval(() => {
            this.updateHeadPosition();
        }, 1000 / 30); // 30 FPS

        console.log('👁️ Head tracking started');
    }

    stopHeadTracking() {
        if (this.headTrackingLoop) {
            clearInterval(this.headTrackingLoop);
            this.headTrackingLoop = null;
        }

        if (this.headTracker) {
            this.headTracker.enabled = false;
        }

        console.log('👁️ Head tracking stopped');
    }

    updateHeadPosition() {
        if (!this.headTracker || !this.headTracker.enabled) return;

        // Simplified head tracking using video analysis
        // In a real implementation, this would use MediaPipe or similar
        const video = this.headTracker.video;

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            // Create temporary canvas for face detection
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');

            ctx.drawImage(video, 0, 0);

            // Simplified face detection (placeholder)
            // Real implementation would use face detection library
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            // Calculate head position relative to center
            this.headPosition.x = (centerX - this.headTracker.calibrationCenter.x) / 100;
            this.headPosition.y = (centerY - this.headTracker.calibrationCenter.y) / 100;

            // Apply head tracking to camera if in FPV mode
            if (this.fpvMode && this.activeVehicle) {
                const camera = this.cameras.get(this.activeVehicle);
                if (camera) {
                    camera.rotation.yaw += this.headPosition.x * 0.1;
                    camera.rotation.pitch += this.headPosition.y * 0.1;
                }
            }
        }
    }

    setControlMode(mode) {
        this.controlMode = mode;

        // Update mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            }
        });

        // Update control interface
        this.updateControlInterface();

        console.log(`🎮 Control mode: ${mode}`);
    }

    updateControlInterface() {
        const controlInputs = document.getElementById('control-inputs');
        if (!controlInputs) return;

        let interfaceHTML = '';

        switch (this.controlMode) {
            case 'overview':
                interfaceHTML = `
                    <div class="control-info">
                        <p>🗺️ Overview mode - Click vehicles to select</p>
                        <p>Use mouse to navigate terrain view</p>
                    </div>
                `;
                break;

            case 'fpv':
                interfaceHTML = `
                    <div class="control-info">
                        <p>👁️ First Person View mode</p>
                        <p>WASD: Move | QE: Rotate | Space: Action</p>
                        <p>F: Toggle FPV | C: Switch Camera</p>
                        <p>H: Toggle Head Tracking</p>
                    </div>
                `;
                break;

            case 'manual':
                interfaceHTML = `
                    <div class="control-info">
                        <p>🎮 Manual Control mode</p>
                        <p>Use gamepad or keyboard for direct control</p>
                        <p>Left stick: Move | Right stick: Rotate</p>
                    </div>
                `;
                break;
        }

        controlInputs.innerHTML = interfaceHTML;
    }

    updateInstrumentCluster() {
        if (!this.activeVehicle || !this.vehicleFleet) return;

        const vehicle = this.vehicleFleet.getVehicleById(this.activeVehicle);
        if (!vehicle) return;

        // Update speed
        const speedDisplay = document.getElementById('speed-display');
        if (speedDisplay) {
            const speed = Math.sqrt(vehicle.vx * vehicle.vx + vehicle.vy * vehicle.vy) || 0;
            speedDisplay.textContent = speed.toFixed(1);
        }

        // Update battery
        const batteryDisplay = document.getElementById('battery-display');
        if (batteryDisplay) {
            batteryDisplay.textContent = vehicle.batteryLevel.toFixed(0);
        }

        // Update task
        const taskDisplay = document.getElementById('task-display');
        if (taskDisplay) {
            taskDisplay.textContent = vehicle.taskStatus;
        }

        // Update position
        const positionDisplay = document.getElementById('position-display');
        if (positionDisplay) {
            positionDisplay.textContent = `${vehicle.x.toFixed(1)},${vehicle.y.toFixed(1)}`;
        }

        // Update vehicle status in UI
        const vehicleStatus = document.getElementById('vehicle-status');
        if (vehicleStatus) {
            vehicleStatus.textContent = vehicle.taskStatus;
        }
    }

    emergencyStop() {
        if (!this.vehicleFleet) return;

        // Stop all vehicles immediately
        this.vehicleFleet.getAllVehicles().forEach(vehicle => {
            this.vehicleFleet.commandVehicle(vehicle.id, {
                action: 'emergency_stop',
                source: 'control_panel'
            });
        });

        // Disable FPV mode
        if (this.fpvMode) {
            this.toggleFPV();
        }

        console.log('🚨 EMERGENCY STOP ACTIVATED');

        // Show emergency notification
        this.showNotification('🚨 EMERGENCY STOP - All vehicles stopped', 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'error' ? '#F44336' : '#4CAF50'};
            color: white;
            padding: 15px 25px;
            border-radius: 5px;
            font-weight: bold;
            z-index: 10000;
            animation: slideDown 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Public API methods
    show() {
        if (this.controlPanelElement) {
            this.controlPanelElement.style.display = 'block';
        }
    }

    hide() {
        if (this.controlPanelElement) {
            this.controlPanelElement.style.display = 'none';
        }
    }

    destroy() {
        // Clean up resources
        if (this.fpvRenderLoop) {
            clearInterval(this.fpvRenderLoop);
        }

        if (this.headTrackingLoop) {
            clearInterval(this.headTrackingLoop);
        }

        if (this.controlPanelElement) {
            this.controlPanelElement.remove();
        }

        console.log('🎮 Control panel destroyed');
    }
}

// Export for use in other modules
window.ControlPanelInterface = ControlPanelInterface;