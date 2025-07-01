/**
 * Professional UI System for AR Sandbox Pro
 * Creates polished, intuitive interface with custom controls, real-time feedback, and professional styling
 */

class ProfessionalUISystem {
    constructor(core) {
        this.core = core;
        this.panels = new Map();
        this.controls = new Map();
        this.notifications = [];
        this.isInitialized = false;
        
        // UI State
        this.activePanel = 'terrain';
        this.isDragging = false;
        this.dragTarget = null;
        
        // Performance monitoring
        this.performanceDisplay = null;
        this.statsUpdateInterval = null;
    }
    
    async initialize() {
        console.log('🎨 Initializing Professional UI System...');
        
        // Create main UI container
        this.createMainUIContainer();
        
        // Create control panels
        this.createTerrainControlPanel();
        this.createPhysicsControlPanel();
        this.createCameraControlPanel();
        this.createToolsPanel();
        this.createPerformancePanel();
        this.createNotificationSystem();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize performance monitoring
        this.initializePerformanceMonitoring();
        
        // Apply professional styling
        this.applyProfessionalStyling();
        
        this.isInitialized = true;
        console.log('✅ Professional UI System initialized');
    }
    
    createMainUIContainer() {
        // Remove any existing UI
        const existingUI = document.getElementById('ar-sandbox-ui');
        if (existingUI) existingUI.remove();
        
        // Create main UI container
        const uiContainer = document.createElement('div');
        uiContainer.id = 'ar-sandbox-ui';
        uiContainer.innerHTML = `
            <div class="ui-header">
                <div class="logo">
                    <h1>AR Sandbox Pro</h1>
                    <span class="version">v${this.core.version}</span>
                </div>
                <div class="header-controls">
                    <button class="btn-icon" id="settings-btn" title="Settings">⚙️</button>
                    <button class="btn-icon" id="fullscreen-btn" title="Fullscreen">⛶</button>
                    <button class="btn-icon" id="help-btn" title="Help">❓</button>
                </div>
            </div>
            
            <div class="ui-sidebar">
                <div class="panel-tabs">
                    <button class="tab-btn active" data-panel="terrain">🏔️ Terrain</button>
                    <button class="tab-btn" data-panel="physics">⚡ Physics</button>
                    <button class="tab-btn" data-panel="camera">📷 Camera</button>
                    <button class="tab-btn" data-panel="tools">🛠️ Tools</button>
                </div>
                <div class="panel-content" id="panel-content">
                    <!-- Panel content will be inserted here -->
                </div>
            </div>
            
            <div class="ui-footer">
                <div class="status-bar">
                    <span id="status-text">Ready</span>
                    <div class="performance-indicators">
                        <span id="fps-display">FPS: --</span>
                        <span id="particles-display">Particles: --</span>
                        <span id="memory-display">Memory: --</span>
                    </div>
                </div>
            </div>
            
            <div class="notification-container" id="notifications">
                <!-- Notifications will appear here -->
            </div>
        `;
        
        document.body.appendChild(uiContainer);
    }
    
    createTerrainControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'control-panel';
        panel.id = 'terrain-panel';
        panel.innerHTML = `
            <div class="panel-section">
                <h3>Brush Settings</h3>
                <div class="control-group">
                    <label>Tool:</label>
                    <div class="button-group">
                        <button class="tool-btn active" data-tool="raise">Raise</button>
                        <button class="tool-btn" data-tool="lower">Lower</button>
                        <button class="tool-btn" data-tool="smooth">Smooth</button>
                        <button class="tool-btn" data-tool="water">Water</button>
                    </div>
                </div>
                <div class="control-group">
                    <label>Size: <span id="brush-size-value">${this.core.state.brushSize}</span></label>
                    <input type="range" id="brush-size" min="5" max="50" value="${this.core.state.brushSize}" class="slider">
                </div>
                <div class="control-group">
                    <label>Strength: <span id="brush-strength-value">${this.core.state.brushStrength}</span></label>
                    <input type="range" id="brush-strength" min="0.1" max="2.0" step="0.1" value="${this.core.state.brushStrength}" class="slider">
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Terrain Type</h3>
                <div class="terrain-types">
                    <button class="terrain-btn active" data-type="sand">🏖️ Sand</button>
                    <button class="terrain-btn" data-type="soil">🌱 Soil</button>
                    <button class="terrain-btn" data-type="rock">🗿 Rock</button>
                    <button class="terrain-btn" data-type="grass">🌿 Grass</button>
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Display Options</h3>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="show-contours" ${this.core.state.showContours ? 'checked' : ''}>
                        <span class="checkmark"></span>
                        Show Contour Lines
                    </label>
                </div>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="show-grid" ${this.core.state.showGrid ? 'checked' : ''}>
                        <span class="checkmark"></span>
                        Show Grid
                    </label>
                </div>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="show-measurements" ${this.core.state.showMeasurements ? 'checked' : ''}>
                        <span class="checkmark"></span>
                        Show Measurements
                    </label>
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Quick Actions</h3>
                <div class="action-buttons">
                    <button class="action-btn" id="reset-terrain">🔄 Reset Terrain</button>
                    <button class="action-btn" id="generate-terrain">🎲 Generate Random</button>
                    <button class="action-btn" id="save-terrain">💾 Save Terrain</button>
                    <button class="action-btn" id="load-terrain">📁 Load Terrain</button>
                </div>
            </div>
        `;
        
        this.panels.set('terrain', panel);
    }
    
    createPhysicsControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'control-panel';
        panel.id = 'physics-panel';
        panel.innerHTML = `
            <div class="panel-section">
                <h3>Water Simulation</h3>
                <div class="control-group">
                    <label>Water Level: <span id="water-level-value">${this.core.state.waterLevel}</span></label>
                    <input type="range" id="water-level" min="0" max="1" step="0.1" value="${this.core.state.waterLevel}" class="slider">
                </div>
                <div class="control-group">
                    <label>Flow Rate:</label>
                    <input type="range" id="flow-rate" min="0.1" max="2.0" step="0.1" value="1.0" class="slider">
                </div>
                <div class="control-group">
                    <label>Evaporation Rate:</label>
                    <input type="range" id="evaporation-rate" min="0" max="0.1" step="0.01" value="0.01" class="slider">
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Particle Effects</h3>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="enable-rain">
                        <span class="checkmark"></span>
                        Rain Effect
                    </label>
                </div>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="enable-snow">
                        <span class="checkmark"></span>
                        Snow Effect
                    </label>
                </div>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="enable-dust">
                        <span class="checkmark"></span>
                        Dust Effect
                    </label>
                </div>
                <div class="control-group">
                    <label>Particle Intensity:</label>
                    <input type="range" id="particle-intensity" min="0.1" max="2.0" step="0.1" value="0.5" class="slider">
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Erosion Settings</h3>
                <div class="control-group">
                    <label>Erosion Rate:</label>
                    <input type="range" id="erosion-rate" min="0" max="0.1" step="0.01" value="0.02" class="slider">
                </div>
                <div class="control-group">
                    <label>Sediment Capacity:</label>
                    <input type="range" id="sediment-capacity" min="1" max="10" step="0.5" value="4" class="slider">
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Physics Actions</h3>
                <div class="action-buttons">
                    <button class="action-btn" id="drain-water">🌊 Drain Water</button>
                    <button class="action-btn" id="add-water">💧 Add Water</button>
                    <button class="action-btn" id="create-explosion">💥 Explosion</button>
                    <button class="action-btn" id="reset-physics">🔄 Reset Physics</button>
                </div>
            </div>
        `;
        
        this.panels.set('physics', panel);
    }
    
    createCameraControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'control-panel';
        panel.id = 'camera-panel';
        panel.innerHTML = `
            <div class="panel-section">
                <h3>Camera Settings</h3>
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="enable-camera" checked>
                        <span class="checkmark"></span>
                        Enable Camera
                    </label>
                </div>
                <div class="control-group">
                    <label>Camera Source:</label>
                    <select id="camera-source" class="select-input">
                        <option value="webcam">Webcam</option>
                        <option value="kinect">Kinect</option>
                        <option value="realsense">RealSense</option>
                    </select>
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Depth Sensing</h3>
                <div class="control-group">
                    <label>Min Depth: <span id="min-depth-value">0.5m</span></label>
                    <input type="range" id="min-depth" min="0.1" max="2.0" step="0.1" value="0.5" class="slider">
                </div>
                <div class="control-group">
                    <label>Max Depth: <span id="max-depth-value">2.0m</span></label>
                    <input type="range" id="max-depth" min="1.0" max="5.0" step="0.1" value="2.0" class="slider">
                </div>
                <div class="control-group">
                    <label>Sensitivity:</label>
                    <input type="range" id="depth-sensitivity" min="0.1" max="2.0" step="0.1" value="1.0" class="slider">
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Calibration</h3>
                <div class="action-buttons">
                    <button class="action-btn" id="calibrate-camera">📐 Calibrate</button>
                    <button class="action-btn" id="save-calibration">💾 Save Calibration</button>
                    <button class="action-btn" id="load-calibration">📁 Load Calibration</button>
                    <button class="action-btn" id="reset-calibration">🔄 Reset</button>
                </div>
            </div>
        `;
        
        this.panels.set('camera', panel);
    }
    
    createToolsPanel() {
        const panel = document.createElement('div');
        panel.className = 'control-panel';
        panel.id = 'tools-panel';
        panel.innerHTML = `
            <div class="panel-section">
                <h3>Measurement Tools</h3>
                <div class="tool-grid">
                    <button class="tool-card" data-tool="ruler">
                        <div class="tool-icon">📏</div>
                        <div class="tool-name">Ruler</div>
                    </button>
                    <button class="tool-card" data-tool="area">
                        <div class="tool-icon">📐</div>
                        <div class="tool-name">Area</div>
                    </button>
                    <button class="tool-card" data-tool="volume">
                        <div class="tool-icon">📦</div>
                        <div class="tool-name">Volume</div>
                    </button>
                    <button class="tool-card" data-tool="slope">
                        <div class="tool-icon">📈</div>
                        <div class="tool-name">Slope</div>
                    </button>
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Construction Tools</h3>
                <div class="tool-grid">
                    <button class="tool-card" data-tool="excavator">
                        <div class="tool-icon">🚜</div>
                        <div class="tool-name">Excavator</div>
                    </button>
                    <button class="tool-card" data-tool="bulldozer">
                        <div class="tool-icon">🚛</div>
                        <div class="tool-name">Bulldozer</div>
                    </button>
                    <button class="tool-card" data-tool="crane">
                        <div class="tool-icon">🏗️</div>
                        <div class="tool-name">Crane</div>
                    </button>
                    <button class="tool-card" data-tool="dump-truck">
                        <div class="tool-icon">🚚</div>
                        <div class="tool-name">Dump Truck</div>
                    </button>
                </div>
            </div>
            
            <div class="panel-section">
                <h3>Scenario Tools</h3>
                <div class="action-buttons">
                    <button class="action-btn" id="load-scenario">📋 Load Scenario</button>
                    <button class="action-btn" id="save-scenario">💾 Save Scenario</button>
                    <button class="action-btn" id="create-scenario">➕ Create New</button>
                </div>
            </div>
        `;
        
        this.panels.set('tools', panel);
    }
    
    createPerformancePanel() {
        const performanceDiv = document.createElement('div');
        performanceDiv.id = 'performance-panel';
        performanceDiv.className = 'performance-overlay';
        performanceDiv.innerHTML = `
            <div class="performance-header">Performance Monitor</div>
            <div class="performance-stats">
                <div class="stat-item">
                    <span class="stat-label">FPS:</span>
                    <span class="stat-value" id="detailed-fps">--</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Frame Time:</span>
                    <span class="stat-value" id="frame-time">--</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Particles:</span>
                    <span class="stat-value" id="particle-count">--</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Memory:</span>
                    <span class="stat-value" id="memory-usage">--</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Terrain Res:</span>
                    <span class="stat-value" id="terrain-resolution">--</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(performanceDiv);
        this.performanceDisplay = performanceDiv;
    }
    
    createNotificationSystem() {
        // Notification system is already created in main UI container
        this.notificationContainer = document.getElementById('notifications');
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchPanel(e.target.dataset.panel);
            });
        });
        
        // Tool selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tool-btn')) {
                this.selectTool(e.target.dataset.tool);
            }
        });
        
        // Slider updates
        document.addEventListener('input', (e) => {
            if (e.target.type === 'range') {
                this.handleSliderChange(e.target);
            }
        });
        
        // Checkbox changes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.handleCheckboxChange(e.target);
            }
        });
        
        // Action buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('action-btn')) {
                this.handleActionButton(e.target);
            }
        });
    }
    
    switchPanel(panelName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.panel === panelName);
        });
        
        // Update panel content
        const panelContent = document.getElementById('panel-content');
        panelContent.innerHTML = '';
        
        if (this.panels.has(panelName)) {
            panelContent.appendChild(this.panels.get(panelName));
        }
        
        this.activePanel = panelName;
    }
    
    selectTool(toolName) {
        // Update tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tool === toolName);
        });
        
        // Update core state
        this.core.state.tool = toolName;
        
        // Show notification
        this.showNotification(`Tool changed to: ${toolName}`, 'info');
    }
    
    handleSliderChange(slider) {
        const value = parseFloat(slider.value);
        const id = slider.id;
        
        // Update display value
        const valueDisplay = document.getElementById(id + '-value');
        if (valueDisplay) {
            valueDisplay.textContent = value;
        }
        
        // Update core state
        switch (id) {
            case 'brush-size':
                this.core.state.brushSize = value;
                break;
            case 'brush-strength':
                this.core.state.brushStrength = value;
                break;
            case 'water-level':
                this.core.state.waterLevel = value;
                break;
            // Add more cases as needed
        }
    }
    
    handleCheckboxChange(checkbox) {
        const checked = checkbox.checked;
        const id = checkbox.id;
        
        switch (id) {
            case 'show-contours':
                this.core.state.showContours = checked;
                break;
            case 'show-grid':
                this.core.state.showGrid = checked;
                break;
            case 'show-measurements':
                this.core.state.showMeasurements = checked;
                break;
            case 'enable-rain':
                if (this.core.physicsEngine) {
                    if (checked) {
                        this.core.physicsEngine.startRain();
                    } else {
                        this.core.physicsEngine.stopRain();
                    }
                }
                break;
            case 'enable-snow':
                if (this.core.physicsEngine) {
                    if (checked) {
                        this.core.physicsEngine.startSnow();
                    } else {
                        this.core.physicsEngine.stopSnow();
                    }
                }
                break;
            // Add more cases as needed
        }
    }
    
    handleActionButton(button) {
        const id = button.id;
        
        switch (id) {
            case 'reset-terrain':
                if (this.core.terrainEngine) {
                    this.core.terrainEngine.generateInitialTerrain();
                    this.showNotification('Terrain reset', 'success');
                }
                break;
            case 'create-explosion':
                if (this.core.physicsEngine) {
                    this.core.physicsEngine.createExplosion(400, 300, 50, 2);
                    this.showNotification('Explosion created!', 'info');
                }
                break;
            // Add more cases as needed
        }
    }
    
    initializePerformanceMonitoring() {
        this.statsUpdateInterval = setInterval(() => {
            this.updatePerformanceStats();
        }, 1000);
    }
    
    updatePerformanceStats() {
        if (!this.core.performance) return;
        
        // Update footer stats
        document.getElementById('fps-display').textContent = `FPS: ${this.core.performance.fps}`;
        
        // Update detailed performance panel
        if (this.performanceDisplay) {
            document.getElementById('detailed-fps').textContent = this.core.performance.fps;
            document.getElementById('frame-time').textContent = `${this.core.performance.frameTime.toFixed(2)}ms`;
            
            if (this.core.physicsEngine) {
                const activeParticles = this.core.physicsEngine.particles.filter(p => p.active).length;
                document.getElementById('particle-count').textContent = activeParticles;
            }
            
            // Memory usage (approximate)
            if (performance.memory) {
                const memoryMB = (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(1);
                document.getElementById('memory-usage').textContent = `${memoryMB}MB`;
            }
            
            if (this.core.terrainEngine) {
                document.getElementById('terrain-resolution').textContent = 
                    `${this.core.terrainEngine.width}x${this.core.terrainEngine.height}`;
            }
        }
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">×</button>
            </div>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info':
            default: return 'ℹ️';
        }
    }
    
    applyProfessionalStyling() {
        // Professional CSS will be added via separate CSS file
        // This method can be used for dynamic styling adjustments
    }
    
    update(deltaTime) {
        // Update any animated UI elements
        this.updateNotifications(deltaTime);
    }
    
    updateNotifications(deltaTime) {
        // Handle notification animations
        const notifications = this.notificationContainer.querySelectorAll('.notification');
        notifications.forEach((notification, index) => {
            notification.style.transform = `translateY(${index * 60}px)`;
        });
    }
    
    render() {
        // UI rendering is handled by DOM
        // This method can be used for canvas-based UI elements
    }
}
