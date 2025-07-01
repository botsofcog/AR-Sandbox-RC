/**
 * Interactive Tool System for AR Sandbox Pro
 * Handles construction tools, measurement tools, scenario modes, and educational features
 */

class InteractiveToolSystem {
    constructor(core) {
        this.core = core;
        this.activeTool = null;
        this.tools = new Map();
        this.measurements = [];
        this.constructions = [];
        this.scenarios = new Map();
        
        // Tool state
        this.isToolActive = false;
        this.toolData = {};
        
        // Measurement state
        this.measurementPoints = [];
        this.measurementMode = null;
        
        // Construction state
        this.constructionVehicles = [];
        this.constructionProjects = [];
    }
    
    async initialize() {
        console.log('🛠️ Initializing Interactive Tool System...');
        
        // Initialize measurement tools
        this.initializeMeasurementTools();
        
        // Initialize construction tools
        this.initializeConstructionTools();
        
        // Initialize scenarios
        this.initializeScenarios();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Interactive Tool System initialized');
    }
    
    initializeMeasurementTools() {
        // Ruler tool
        this.tools.set('ruler', {
            name: 'Ruler',
            icon: '📏',
            activate: () => this.activateRuler(),
            deactivate: () => this.deactivateRuler(),
            onMouseDown: (x, y) => this.rulerMouseDown(x, y),
            onMouseMove: (x, y) => this.rulerMouseMove(x, y),
            onMouseUp: (x, y) => this.rulerMouseUp(x, y)
        });
        
        // Area measurement tool
        this.tools.set('area', {
            name: 'Area Measurement',
            icon: '📐',
            activate: () => this.activateAreaMeasurement(),
            deactivate: () => this.deactivateAreaMeasurement(),
            onMouseDown: (x, y) => this.areaMouseDown(x, y),
            onMouseMove: (x, y) => this.areaMouseMove(x, y),
            onMouseUp: (x, y) => this.areaMouseUp(x, y)
        });
        
        // Volume measurement tool
        this.tools.set('volume', {
            name: 'Volume Measurement',
            icon: '📦',
            activate: () => this.activateVolumeMeasurement(),
            deactivate: () => this.deactivateVolumeMeasurement(),
            onMouseDown: (x, y) => this.volumeMouseDown(x, y),
            onMouseMove: (x, y) => this.volumeMouseMove(x, y),
            onMouseUp: (x, y) => this.volumeMouseUp(x, y)
        });
        
        // Slope measurement tool
        this.tools.set('slope', {
            name: 'Slope Measurement',
            icon: '📈',
            activate: () => this.activateSlopeMeasurement(),
            deactivate: () => this.deactivateSlopeMeasurement(),
            onMouseDown: (x, y) => this.slopeMouseDown(x, y),
            onMouseMove: (x, y) => this.slopeMouseMove(x, y),
            onMouseUp: (x, y) => this.slopeMouseUp(x, y)
        });
    }
    
    initializeConstructionTools() {
        // Excavator tool
        this.tools.set('excavator', {
            name: 'Excavator',
            icon: '🚜',
            activate: () => this.activateExcavator(),
            deactivate: () => this.deactivateExcavator(),
            onMouseDown: (x, y) => this.excavatorMouseDown(x, y),
            onMouseMove: (x, y) => this.excavatorMouseMove(x, y),
            onMouseUp: (x, y) => this.excavatorMouseUp(x, y)
        });
        
        // Bulldozer tool
        this.tools.set('bulldozer', {
            name: 'Bulldozer',
            icon: '🚛',
            activate: () => this.activateBulldozer(),
            deactivate: () => this.deactivateBulldozer(),
            onMouseDown: (x, y) => this.bulldozerMouseDown(x, y),
            onMouseMove: (x, y) => this.bulldozerMouseMove(x, y),
            onMouseUp: (x, y) => this.bulldozerMouseUp(x, y)
        });
        
        // Dump truck tool
        this.tools.set('dump-truck', {
            name: 'Dump Truck',
            icon: '🚚',
            activate: () => this.activateDumpTruck(),
            deactivate: () => this.deactivateDumpTruck(),
            onMouseDown: (x, y) => this.dumpTruckMouseDown(x, y),
            onMouseMove: (x, y) => this.dumpTruckMouseMove(x, y),
            onMouseUp: (x, y) => this.dumpTruckMouseUp(x, y)
        });
    }
    
    initializeScenarios() {
        // Construction scenario
        this.scenarios.set('construction', {
            name: 'Construction Site',
            description: 'Build roads, foundations, and structures',
            objectives: [
                'Level the construction area',
                'Build access roads',
                'Create foundation excavation',
                'Manage water drainage'
            ],
            tools: ['excavator', 'bulldozer', 'dump-truck'],
            timeLimit: 600, // 10 minutes
            scoring: {
                efficiency: 0,
                accuracy: 0,
                timeBonus: 0
            }
        });
        
        // Landscape scenario
        this.scenarios.set('landscape', {
            name: 'Landscape Design',
            description: 'Create beautiful and functional landscapes',
            objectives: [
                'Design water features',
                'Create elevation changes',
                'Plan drainage systems',
                'Add vegetation zones'
            ],
            tools: ['ruler', 'area', 'volume'],
            timeLimit: 900, // 15 minutes
            scoring: {
                aesthetics: 0,
                functionality: 0,
                sustainability: 0
            }
        });
        
        // Flood management scenario
        this.scenarios.set('flood-management', {
            name: 'Flood Management',
            description: 'Design flood control and water management systems',
            objectives: [
                'Create retention basins',
                'Design drainage channels',
                'Build flood barriers',
                'Test water flow patterns'
            ],
            tools: ['excavator', 'volume', 'slope'],
            timeLimit: 720, // 12 minutes
            scoring: {
                effectiveness: 0,
                costEfficiency: 0,
                environmentalImpact: 0
            }
        });
    }
    
    setupEventListeners() {
        // Tool selection events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tool-card')) {
                const toolName = e.target.dataset.tool;
                this.selectTool(toolName);
            }
        });
        
        // Canvas interaction events
        if (this.core.terrainEngine && this.core.terrainEngine.canvas) {
            const canvas = this.core.terrainEngine.canvas;
            
            canvas.addEventListener('mousedown', (e) => {
                if (this.activeTool) {
                    const rect = canvas.getBoundingClientRect();
                    const x = Math.floor((e.clientX - rect.left) / this.core.terrainEngine.scale);
                    const y = Math.floor((e.clientY - rect.top) / this.core.terrainEngine.scale);
                    this.activeTool.onMouseDown(x, y);
                }
            });
            
            canvas.addEventListener('mousemove', (e) => {
                if (this.activeTool) {
                    const rect = canvas.getBoundingClientRect();
                    const x = Math.floor((e.clientX - rect.left) / this.core.terrainEngine.scale);
                    const y = Math.floor((e.clientY - rect.top) / this.core.terrainEngine.scale);
                    this.activeTool.onMouseMove(x, y);
                }
            });
            
            canvas.addEventListener('mouseup', (e) => {
                if (this.activeTool) {
                    const rect = canvas.getBoundingClientRect();
                    const x = Math.floor((e.clientX - rect.left) / this.core.terrainEngine.scale);
                    const y = Math.floor((e.clientY - rect.top) / this.core.terrainEngine.scale);
                    this.activeTool.onMouseUp(x, y);
                }
            });
        }
    }
    
    selectTool(toolName) {
        // Deactivate current tool
        if (this.activeTool) {
            this.activeTool.deactivate();
        }
        
        // Activate new tool
        if (this.tools.has(toolName)) {
            this.activeTool = this.tools.get(toolName);
            this.activeTool.activate();
            this.isToolActive = true;
            
            this.core.uiSystem?.showNotification(`${this.activeTool.name} activated`, 'info');
        }
    }
    
    // Ruler tool implementation
    activateRuler() {
        this.measurementMode = 'ruler';
        this.measurementPoints = [];
        this.toolData.ruler = { startPoint: null, endPoint: null, distance: 0 };
    }
    
    deactivateRuler() {
        this.measurementMode = null;
        this.measurementPoints = [];
    }
    
    rulerMouseDown(x, y) {
        if (!this.toolData.ruler.startPoint) {
            this.toolData.ruler.startPoint = { x, y };
        } else {
            this.toolData.ruler.endPoint = { x, y };
            this.calculateRulerDistance();
        }
    }
    
    rulerMouseMove(x, y) {
        if (this.toolData.ruler.startPoint && !this.toolData.ruler.endPoint) {
            this.toolData.ruler.endPoint = { x, y };
            this.calculateRulerDistance();
        }
    }
    
    rulerMouseUp(x, y) {
        if (this.toolData.ruler.startPoint) {
            this.toolData.ruler.endPoint = { x, y };
            this.calculateRulerDistance();
            this.saveMeasurement('ruler', this.toolData.ruler);
        }
    }
    
    calculateRulerDistance() {
        const start = this.toolData.ruler.startPoint;
        const end = this.toolData.ruler.endPoint;
        
        if (start && end) {
            const dx = end.x - start.x;
            const dy = end.y - start.y;
            const pixelDistance = Math.sqrt(dx * dx + dy * dy);
            
            // Convert to real-world units (assuming 1 pixel = 1cm in toy scale)
            const realDistance = pixelDistance * 0.01; // Convert to meters
            this.toolData.ruler.distance = realDistance;
            
            // Update UI
            this.updateMeasurementDisplay('Distance', `${realDistance.toFixed(2)}m`);
        }
    }
    
    // Area measurement tool implementation
    activateAreaMeasurement() {
        this.measurementMode = 'area';
        this.measurementPoints = [];
        this.toolData.area = { points: [], area: 0 };
    }
    
    deactivateAreaMeasurement() {
        this.measurementMode = null;
        this.measurementPoints = [];
    }
    
    areaMouseDown(x, y) {
        this.toolData.area.points.push({ x, y });
        
        if (this.toolData.area.points.length >= 3) {
            this.calculatePolygonArea();
        }
    }
    
    areaMouseMove(x, y) {
        // Show preview of current polygon
    }
    
    areaMouseUp(x, y) {
        // Double-click to finish polygon
    }
    
    calculatePolygonArea() {
        const points = this.toolData.area.points;
        if (points.length < 3) return;
        
        // Shoelace formula for polygon area
        let area = 0;
        for (let i = 0; i < points.length; i++) {
            const j = (i + 1) % points.length;
            area += points[i].x * points[j].y;
            area -= points[j].x * points[i].y;
        }
        area = Math.abs(area) / 2;
        
        // Convert to real-world units
        const realArea = area * 0.0001; // Convert to square meters
        this.toolData.area.area = realArea;
        
        this.updateMeasurementDisplay('Area', `${realArea.toFixed(2)}m²`);
    }
    
    // Volume measurement tool implementation
    activateVolumeMeasurement() {
        this.measurementMode = 'volume';
        this.toolData.volume = { region: null, volume: 0, baseHeight: 0 };
    }
    
    deactivateVolumeMeasurement() {
        this.measurementMode = null;
    }
    
    volumeMouseDown(x, y) {
        // Start volume calculation region
        this.toolData.volume.region = { startX: x, startY: y, endX: x, endY: y };
    }
    
    volumeMouseMove(x, y) {
        if (this.toolData.volume.region) {
            this.toolData.volume.region.endX = x;
            this.toolData.volume.region.endY = y;
            this.calculateVolume();
        }
    }
    
    volumeMouseUp(x, y) {
        if (this.toolData.volume.region) {
            this.toolData.volume.region.endX = x;
            this.toolData.volume.region.endY = y;
            this.calculateVolume();
            this.saveMeasurement('volume', this.toolData.volume);
        }
    }
    
    calculateVolume() {
        const region = this.toolData.volume.region;
        if (!region || !this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        const minX = Math.min(region.startX, region.endX);
        const maxX = Math.max(region.startX, region.endX);
        const minY = Math.min(region.startY, region.endY);
        const maxY = Math.max(region.startY, region.endY);
        
        let totalVolume = 0;
        let baseHeight = this.toolData.volume.baseHeight;
        
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                if (x >= 0 && x < terrain.width && y >= 0 && y < terrain.height) {
                    const index = y * terrain.width + x;
                    const height = terrain.heightMap[index];
                    const heightDiff = Math.max(0, height - baseHeight);
                    totalVolume += heightDiff;
                }
            }
        }
        
        // Convert to real-world units
        const realVolume = totalVolume * 0.000001; // Convert to cubic meters
        this.toolData.volume.volume = realVolume;
        
        this.updateMeasurementDisplay('Volume', `${realVolume.toFixed(3)}m³`);
    }
    
    // Construction tool implementations
    activateExcavator() {
        this.createConstructionVehicle('excavator', '🚜');
    }
    
    deactivateExcavator() {
        this.removeConstructionVehicle('excavator');
    }
    
    excavatorMouseDown(x, y) {
        // Excavator digs terrain
        this.core.state.tool = 'lower';
        this.core.state.brushSize = 15;
        this.core.state.brushStrength = 1.0;
        
        if (this.core.terrainEngine) {
            this.core.terrainEngine.modifyTerrain(x, y);
            
            // Create dust particles
            if (this.core.physicsEngine) {
                for (let i = 0; i < 10; i++) {
                    this.core.physicsEngine.spawnParticle({
                        x: x * 4 + (Math.random() - 0.5) * 20,
                        y: y * 4 + (Math.random() - 0.5) * 20,
                        z: 20 + Math.random() * 30,
                        vx: (Math.random() - 0.5) * 30,
                        vy: (Math.random() - 0.5) * 30,
                        vz: Math.random() * 20 + 10,
                        type: 'dust',
                        life: 2.0,
                        size: 2 + Math.random() * 3,
                        color: [139, 119, 101, 0.6]
                    });
                }
            }
        }
    }
    
    excavatorMouseMove(x, y) {
        // Continue excavation while dragging
        this.excavatorMouseDown(x, y);
    }
    
    excavatorMouseUp(x, y) {
        // Stop excavation
    }
    
    activateBulldozer() {
        this.createConstructionVehicle('bulldozer', '🚛');
    }
    
    deactivateBulldozer() {
        this.removeConstructionVehicle('bulldozer');
    }
    
    bulldozerMouseDown(x, y) {
        // Bulldozer smooths and levels terrain
        this.core.state.tool = 'smooth';
        this.core.state.brushSize = 25;
        this.core.state.brushStrength = 0.8;
        
        if (this.core.terrainEngine) {
            this.core.terrainEngine.modifyTerrain(x, y);
        }
    }
    
    bulldozerMouseMove(x, y) {
        this.bulldozerMouseDown(x, y);
    }
    
    bulldozerMouseUp(x, y) {
        // Stop bulldozing
    }
    
    createConstructionVehicle(type, icon) {
        const vehicle = {
            type: type,
            icon: icon,
            x: 100,
            y: 100,
            active: true
        };
        
        this.constructionVehicles.push(vehicle);
        this.core.uiSystem?.showNotification(`${type} deployed`, 'success');
    }
    
    removeConstructionVehicle(type) {
        this.constructionVehicles = this.constructionVehicles.filter(v => v.type !== type);
    }
    
    saveMeasurement(type, data) {
        const measurement = {
            id: Date.now(),
            type: type,
            data: data,
            timestamp: new Date().toISOString()
        };
        
        this.measurements.push(measurement);
        this.core.uiSystem?.showNotification(`${type} measurement saved`, 'success');
    }
    
    updateMeasurementDisplay(label, value) {
        // Update measurement display in UI
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.textContent = `${label}: ${value}`;
        }
    }
    
    loadScenario(scenarioName) {
        if (!this.scenarios.has(scenarioName)) return;
        
        const scenario = this.scenarios.get(scenarioName);
        
        // Reset environment
        this.resetEnvironment();
        
        // Load scenario objectives
        this.displayScenarioObjectives(scenario);
        
        // Enable scenario tools
        this.enableScenarioTools(scenario.tools);
        
        // Start scenario timer
        this.startScenarioTimer(scenario.timeLimit);
        
        this.core.uiSystem?.showNotification(`Scenario loaded: ${scenario.name}`, 'info');
    }
    
    resetEnvironment() {
        // Reset terrain
        if (this.core.terrainEngine) {
            this.core.terrainEngine.generateInitialTerrain();
        }
        
        // Clear measurements
        this.measurements = [];
        
        // Remove construction vehicles
        this.constructionVehicles = [];
    }
    
    displayScenarioObjectives(scenario) {
        // Display objectives in UI
        console.log('Scenario Objectives:', scenario.objectives);
    }
    
    enableScenarioTools(tools) {
        // Enable only specified tools
        this.allowedTools = tools;
    }
    
    startScenarioTimer(timeLimit) {
        // Start countdown timer
        this.scenarioStartTime = Date.now();
        this.scenarioTimeLimit = timeLimit * 1000; // Convert to milliseconds
    }
    
    update(deltaTime) {
        // Update construction vehicles
        this.updateConstructionVehicles(deltaTime);
        
        // Update scenario timer
        this.updateScenarioTimer();
    }
    
    updateConstructionVehicles(deltaTime) {
        // Animate construction vehicles
        for (const vehicle of this.constructionVehicles) {
            // Simple animation or movement logic
        }
    }
    
    updateScenarioTimer() {
        if (this.scenarioStartTime && this.scenarioTimeLimit) {
            const elapsed = Date.now() - this.scenarioStartTime;
            const remaining = Math.max(0, this.scenarioTimeLimit - elapsed);
            
            if (remaining === 0) {
                this.endScenario();
            }
        }
    }
    
    endScenario() {
        // Calculate score and show results
        this.core.uiSystem?.showNotification('Scenario completed!', 'success');
        this.scenarioStartTime = null;
        this.scenarioTimeLimit = null;
    }
    
    // Slope measurement implementation
    activateSlopeMeasurement() {
        this.measurementMode = 'slope';
        this.toolData.slope = { startPoint: null, endPoint: null, slope: 0, angle: 0 };
    }
    
    deactivateSlopeMeasurement() {
        this.measurementMode = null;
    }
    
    slopeMouseDown(x, y) {
        if (!this.toolData.slope.startPoint) {
            this.toolData.slope.startPoint = { x, y };
        } else {
            this.toolData.slope.endPoint = { x, y };
            this.calculateSlope();
        }
    }
    
    slopeMouseMove(x, y) {
        if (this.toolData.slope.startPoint && !this.toolData.slope.endPoint) {
            this.toolData.slope.endPoint = { x, y };
            this.calculateSlope();
        }
    }
    
    slopeMouseUp(x, y) {
        if (this.toolData.slope.startPoint) {
            this.toolData.slope.endPoint = { x, y };
            this.calculateSlope();
            this.saveMeasurement('slope', this.toolData.slope);
        }
    }
    
    calculateSlope() {
        const start = this.toolData.slope.startPoint;
        const end = this.toolData.slope.endPoint;
        
        if (start && end && this.core.terrainEngine) {
            const terrain = this.core.terrainEngine;
            
            // Get heights at start and end points
            const startIndex = start.y * terrain.width + start.x;
            const endIndex = end.y * terrain.width + end.x;
            
            if (startIndex >= 0 && startIndex < terrain.heightMap.length &&
                endIndex >= 0 && endIndex < terrain.heightMap.length) {
                
                const startHeight = terrain.heightMap[startIndex];
                const endHeight = terrain.heightMap[endIndex];
                
                const dx = end.x - start.x;
                const dy = end.y - start.y;
                const horizontalDistance = Math.sqrt(dx * dx + dy * dy);
                const verticalDistance = Math.abs(endHeight - startHeight);
                
                const slope = verticalDistance / horizontalDistance;
                const angle = Math.atan(slope) * (180 / Math.PI);
                
                this.toolData.slope.slope = slope;
                this.toolData.slope.angle = angle;
                
                this.updateMeasurementDisplay('Slope', `${(slope * 100).toFixed(1)}% (${angle.toFixed(1)}°)`);
            }
        }
    }
}
