/**
 * UI Controller - Manages interface interactions and state
 * Part of the RC Sandbox modular architecture
 */

class UIController {
    constructor(terrainEngine) {
        this.terrainEngine = terrainEngine;
        this.activeVehicles = new Map();
        this.objectives = new Map();
        this.currentTool = 'excavator';
        
        this.setupEventListeners();
        this.initializeObjectives();
        
        console.log('🎮 UI Controller initialized');
    }
    
    setupEventListeners() {
        // Tool selection
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectTool(e.target.dataset.tool);
            });
        });
        
        // Mode selection
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectMode(e.target.dataset.mode);
            });
        });
        
        // Brush controls
        const brushSizeSlider = document.getElementById('brush-size');
        const brushSizeValue = document.getElementById('brush-size-value');
        brushSizeSlider.addEventListener('input', (e) => {
            const size = parseInt(e.target.value);
            brushSizeValue.textContent = size;
            this.terrainEngine.setBrushSize(size);
        });
        
        const intensitySlider = document.getElementById('intensity');
        const intensityValue = document.getElementById('intensity-value');
        intensitySlider.addEventListener('input', (e) => {
            const intensity = parseInt(e.target.value);
            intensityValue.textContent = intensity;
            this.terrainEngine.setIntensity(intensity / 100);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }
    
    initializeObjectives() {
        this.objectives.set('terrain', {
            name: 'Initialize terrain system',
            completed: true,
            description: 'Set up real-time terrain visualization'
        });
        
        this.objectives.set('vehicles', {
            name: 'Deploy RC vehicles',
            completed: false,
            description: 'Connect and calibrate RC vehicle fleet'
        });
        
        this.objectives.set('roads', {
            name: 'Build road network',
            completed: false,
            description: 'Create pathways for vehicle navigation'
        });
        
        this.objectives.set('flood', {
            name: 'Test flood defense',
            completed: false,
            description: 'Execute flood defense mission scenario'
        });
        
        this.updateObjectivesDisplay();
    }
    
    selectTool(tool) {
        // Update UI
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tool="${tool}"]`).classList.add('active');
        
        this.currentTool = tool;
        
        // Handle different tool types
        if (['raise', 'lower', 'smooth'].includes(tool)) {
            this.terrainEngine.setTool(tool);
        } else if (tool === 'brush') {
            this.terrainEngine.setTool('raise');
        } else {
            // Vehicle tools
            this.selectVehicle(tool);
        }
        
        console.log(`🔧 Tool selected: ${tool}`);
    }
    
    selectMode(mode) {
        // Update UI
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        this.terrainEngine.setTool(mode);
        console.log(`⚙️ Mode selected: ${mode}`);
    }
    
    selectVehicle(vehicleType) {
        // Vehicle selection logic
        const vehicleSpecs = {
            excavator: { id: 'EX001', speed: 2.0, power: 90 },
            bulldozer: { id: 'BD001', speed: 2.5, power: 80 },
            dump_truck: { id: 'DT001', speed: 3.5, power: 60 },
            crane: { id: 'CR001', speed: 1.5, power: 95 },
            compactor: { id: 'CP001', speed: 2.0, power: 70 }
        };
        
        const spec = vehicleSpecs[vehicleType];
        if (spec) {
            console.log(`🚛 Vehicle selected: ${spec.id} (${vehicleType})`);
            
            // Update status display
            this.updateVehicleStatus(spec);
            
            // Send vehicle selection to telemetry server
            if (window.websocketManager) {
                window.websocketManager.sendVehicleCommand({
                    vehicle_id: spec.id,
                    action: 'select'
                });
            }
        }
    }
    
    updateVehicleStatus(spec) {
        // Update vehicle count and active status
        const vehicleCountEl = document.getElementById('vehicle-count');
        const activeVehiclesEl = document.getElementById('active-vehicles');
        
        if (vehicleCountEl) vehicleCountEl.textContent = '5';
        if (activeVehiclesEl) activeVehiclesEl.textContent = '2';
    }
    
    updateObjectivesDisplay() {
        const objectiveItems = document.querySelectorAll('.objective-item');
        
        objectiveItems.forEach((item, index) => {
            const checkbox = item.querySelector('.objective-checkbox');
            const objectiveKeys = Array.from(this.objectives.keys());
            
            if (index < objectiveKeys.length) {
                const objective = this.objectives.get(objectiveKeys[index]);
                if (objective.completed) {
                    checkbox.classList.add('completed');
                } else {
                    checkbox.classList.remove('completed');
                }
            }
        });
    }
    
    completeObjective(objectiveKey) {
        if (this.objectives.has(objectiveKey)) {
            this.objectives.get(objectiveKey).completed = true;
            this.updateObjectivesDisplay();
            console.log(`✅ Objective completed: ${objectiveKey}`);
        }
    }
    
    handleKeyboard(event) {
        switch (event.key) {
            case '1':
                this.selectTool('excavator');
                break;
            case '2':
                this.selectTool('bulldozer');
                break;
            case '3':
                this.selectTool('dump_truck');
                break;
            case '4':
                this.selectTool('crane');
                break;
            case '5':
                this.selectTool('compactor');
                break;
            case 'b':
            case 'B':
                this.selectTool('brush');
                break;
            case 'r':
            case 'R':
                this.selectMode('raise');
                break;
            case 'l':
            case 'L':
                this.selectMode('lower');
                break;
            case 's':
            case 'S':
                this.selectMode('smooth');
                break;
            case 'Escape':
                // Reset to default tool
                this.selectTool('brush');
                break;
        }
    }
    
    updateFPS(fps) {
        const fpsEl = document.getElementById('fps');
        if (fpsEl) {
            fpsEl.textContent = Math.round(fps);
        }
    }
    
    updateVehicleData(vehicleData) {
        // Update vehicle positions and status from telemetry
        this.activeVehicles.clear();
        
        if (vehicleData && vehicleData.vehicles) {
            Object.values(vehicleData.vehicles).forEach(vehicle => {
                this.activeVehicles.set(vehicle.vehicle_id, vehicle);
            });
            
            // Update UI counters
            const totalVehicles = Object.keys(vehicleData.vehicles).length;
            const activeCount = Object.values(vehicleData.vehicles)
                .filter(v => v.task_status !== 'idle').length;
            
            const vehicleCountEl = document.getElementById('vehicle-count');
            const activeVehiclesEl = document.getElementById('active-vehicles');
            
            if (vehicleCountEl) vehicleCountEl.textContent = totalVehicles;
            if (activeVehiclesEl) activeVehiclesEl.textContent = activeCount;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'error' ? '#ff4444' : '#4CAF50',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '5px',
            zIndex: '1000',
            opacity: '0',
            transition: 'opacity 0.3s'
        });
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // Mission control methods
    startFloodDefenseMission() {
        this.showNotification('🌊 Flood Defense Mission Started!', 'info');
        this.completeObjective('vehicles');
        
        // Auto-select excavator for flood defense
        this.selectTool('excavator');
    }
    
    startConstructionMission() {
        this.showNotification('🏗️ Construction Mission Started!', 'info');
        this.completeObjective('roads');
    }
    
    resetTerrain() {
        if (this.terrainEngine) {
            this.terrainEngine.initializeTerrain();
            this.showNotification('🔄 Terrain Reset', 'info');
        }
    }

    update() {
        // Update UI elements with current state
        this.updateStatusPanel();
        this.updateObjectiveProgress();
        this.updateVehicleStatus();
    }

    updateStatusPanel() {
        // Update FPS counter
        const fpsElement = document.getElementById('fps');
        if (fpsElement) {
            const fps = Math.round(1000 / (performance.now() - (this.lastFrameTime || performance.now())));
            fpsElement.textContent = Math.min(fps, 60);
            this.lastFrameTime = performance.now();
        }

        // Update vehicle count
        const vehicleCountElement = document.getElementById('vehicle-count');
        if (vehicleCountElement) {
            vehicleCountElement.textContent = this.activeVehicles.size;
        }

        // Update active vehicles
        const activeVehiclesElement = document.getElementById('active-vehicles');
        if (activeVehiclesElement) {
            const activeCount = Array.from(this.activeVehicles.values()).filter(v => v.active).length;
            activeVehiclesElement.textContent = activeCount;
        }
    }

    updateObjectiveProgress() {
        // Update objective checkboxes based on current state
        this.objectives.forEach((objective, id) => {
            const element = document.querySelector(`[data-objective="${id}"] .objective-checkbox`);
            if (element) {
                if (objective.completed) {
                    element.classList.add('completed');
                } else {
                    element.classList.remove('completed');
                }
            }
        });
    }

    updateVehicleStatus() {
        // Update vehicle tool buttons based on availability
        this.activeVehicles.forEach((vehicle, id) => {
            const element = document.querySelector(`[data-tool="${id}"]`);
            if (element) {
                if (vehicle.active) {
                    element.classList.add('active');
                } else {
                    element.classList.remove('active');
                }
            }
        });
    }
}

// Export for use in other modules
window.UIController = UIController;
