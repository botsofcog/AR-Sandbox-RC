/**
 * UI Manager - Professional user interface management for AR Sandbox Pro
 */

class UIManager {
    constructor(core, config = {}) {
        this.core = core;
        this.config = {
            theme: 'professional',
            animations: true,
            responsiveBreakpoints: {
                mobile: 768,
                tablet: 1024,
                desktop: 1440
            },
            ...config
        };
        
        this.panels = new Map();
        this.modals = new Map();
        this.notifications = [];
        
        this.version = '2.0.0';
        this.description = 'Professional UI management system';
    }
    
    async initialize() {
        console.log('🎨 Initializing UI Manager...');
        
        this.setupTheme();
        this.setupResponsiveHandling();
        this.setupNotificationSystem();
        this.bindUIEvents();
        
        console.log('✅ UI Manager initialized');
    }
    
    setupTheme() {
        document.body.setAttribute('data-theme', this.config.theme);
    }
    
    setupResponsiveHandling() {
        const handleResize = () => {
            const width = window.innerWidth;
            let breakpoint = 'desktop';
            
            if (width <= this.config.responsiveBreakpoints.mobile) {
                breakpoint = 'mobile';
            } else if (width <= this.config.responsiveBreakpoints.tablet) {
                breakpoint = 'tablet';
            }
            
            document.body.setAttribute('data-breakpoint', breakpoint);
            this.core.eventSystem.emit('ui:breakpointChanged', { breakpoint, width });
        };
        
        window.addEventListener('resize', handleResize);
        handleResize(); // Initial call
    }
    
    setupNotificationSystem() {
        // Create notification container
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    bindUIEvents() {
        // Tool selection
        this.core.eventSystem.on('core:toolChanged', ({ tool }) => {
            this.updateToolProperties(tool);
        });
        
        // Mode changes
        this.core.eventSystem.on('core:modeChanged', ({ mode }) => {
            this.updateModeInterface(mode);
        });
        
        // Performance updates
        this.core.eventSystem.on('render:performance', (stats) => {
            this.updatePerformanceDisplay(stats);
        });
    }
    
    updateToolProperties(tool) {
        const propertiesPanel = document.getElementById('toolProperties');
        if (!propertiesPanel) return;
        
        // Clear existing properties
        propertiesPanel.innerHTML = '';
        
        // Add tool-specific properties
        switch (tool) {
            case 'terrain':
                this.addTerrainProperties(propertiesPanel);
                break;
            case 'water':
                this.addWaterProperties(propertiesPanel);
                break;
            case 'structures':
                this.addStructureProperties(propertiesPanel);
                break;
            case 'measure':
                this.addMeasurementProperties(propertiesPanel);
                break;
            case 'vehicles':
                this.addVehicleProperties(propertiesPanel);
                break;
            case 'analysis':
                this.addAnalysisProperties(propertiesPanel);
                break;
        }
    }
    
    addTerrainProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Brush Size</label>
                <input type="range" min="5" max="50" value="20" class="property-slider" id="brushSize">
                <span class="property-value">20px</span>
            </div>
            <div class="property-group">
                <label>Material</label>
                <select class="property-select" id="terrainMaterial">
                    <option value="sand">Sand</option>
                    <option value="clay">Clay</option>
                    <option value="gravel">Gravel</option>
                    <option value="rock">Rock</option>
                </select>
            </div>
            <div class="property-group">
                <label>Strength</label>
                <input type="range" min="0.1" max="2.0" step="0.1" value="1.0" class="property-slider" id="brushStrength">
                <span class="property-value">1.0</span>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    addWaterProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Flow Rate</label>
                <input type="range" min="0.1" max="5.0" step="0.1" value="1.0" class="property-slider" id="waterFlow">
                <span class="property-value">1.0</span>
            </div>
            <div class="property-group">
                <label>Volume</label>
                <input type="range" min="1" max="100" value="50" class="property-slider" id="waterVolume">
                <span class="property-value">50</span>
            </div>
            <div class="property-group">
                <label>Temperature</label>
                <input type="range" min="0" max="100" value="20" class="property-slider" id="waterTemp">
                <span class="property-value">20°C</span>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    addStructureProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Structure Type</label>
                <select class="property-select" id="structureType">
                    <option value="building">Building</option>
                    <option value="bridge">Bridge</option>
                    <option value="road">Road</option>
                    <option value="wall">Wall</option>
                </select>
            </div>
            <div class="property-group">
                <label>Material</label>
                <select class="property-select" id="structureMaterial">
                    <option value="concrete">Concrete</option>
                    <option value="steel">Steel</option>
                    <option value="wood">Wood</option>
                    <option value="stone">Stone</option>
                </select>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    addMeasurementProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Measurement Type</label>
                <select class="property-select" id="measurementType">
                    <option value="height">Height</option>
                    <option value="slope">Slope</option>
                    <option value="area">Area</option>
                    <option value="volume">Volume</option>
                </select>
            </div>
            <div class="property-group">
                <label>Units</label>
                <select class="property-select" id="measurementUnits">
                    <option value="metric">Metric</option>
                    <option value="imperial">Imperial</option>
                </select>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    addVehicleProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Vehicle Type</label>
                <select class="property-select" id="vehicleType">
                    <option value="excavator">Excavator</option>
                    <option value="bulldozer">Bulldozer</option>
                    <option value="dumptruck">Dump Truck</option>
                    <option value="crane">Crane</option>
                </select>
            </div>
            <div class="property-group">
                <label>Speed</label>
                <input type="range" min="0.5" max="3.0" step="0.1" value="1.0" class="property-slider" id="vehicleSpeed">
                <span class="property-value">1.0</span>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    addAnalysisProperties(container) {
        container.innerHTML = `
            <div class="property-group">
                <label>Analysis Type</label>
                <select class="property-select" id="analysisType">
                    <option value="drainage">Drainage</option>
                    <option value="stability">Stability</option>
                    <option value="erosion">Erosion</option>
                    <option value="flow">Flow</option>
                </select>
            </div>
            <div class="property-group">
                <label>Visualization</label>
                <select class="property-select" id="analysisViz">
                    <option value="heatmap">Heat Map</option>
                    <option value="contours">Contours</option>
                    <option value="vectors">Vectors</option>
                </select>
            </div>
        `;
        
        this.bindPropertyEvents(container);
    }
    
    bindPropertyEvents(container) {
        // Bind slider events
        container.querySelectorAll('.property-slider').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const valueSpan = e.target.nextElementSibling;
                if (valueSpan) {
                    let value = e.target.value;
                    if (e.target.id === 'waterTemp') value += '°C';
                    else if (e.target.id === 'brushSize') value += 'px';
                    valueSpan.textContent = value;
                }
                
                this.core.eventSystem.emit('ui:propertyChanged', {
                    property: e.target.id,
                    value: e.target.value
                });
            });
        });
        
        // Bind select events
        container.querySelectorAll('.property-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.core.eventSystem.emit('ui:propertyChanged', {
                    property: e.target.id,
                    value: e.target.value
                });
            });
        });
    }
    
    updateModeInterface(mode) {
        // Update interface based on mode
        document.body.setAttribute('data-mode', mode);
    }
    
    updatePerformanceDisplay(stats) {
        const fpsElement = document.getElementById('fpsCounter');
        if (fpsElement) {
            fpsElement.textContent = stats.fps;
            
            // Color code based on performance
            if (stats.fps >= 55) {
                fpsElement.style.color = '#059669'; // Green
            } else if (stats.fps >= 30) {
                fpsElement.style.color = '#d97706'; // Orange
            } else {
                fpsElement.style.color = '#dc2626'; // Red
            }
        }
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const container = document.getElementById('notificationContainer');
        container.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            notification.remove();
        }, duration);
        
        return notification;
    }
    
    async start() {
        console.log('🎨 UI Manager started');
    }
    
    update(deltaTime) {
        // UI updates
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIManager;
} else {
    window.UIManager = UIManager;
}
