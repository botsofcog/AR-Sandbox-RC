/**
 * Projection Overlay System - AR overlays optimized for projector mapping
 * Part of the RC Sandbox modular architecture
 */

class ProjectionOverlay {
    constructor(canvas, terrainEngine) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.terrainEngine = terrainEngine;
        
        // Projection parameters
        this.projectorWidth = 1920;
        this.projectorHeight = 1080;
        this.sandboxBounds = {
            x: 0, y: 0,
            width: 1000, height: 750  // Sandbox dimensions in units
        };
        
        // Overlay layers
        this.layers = new Map();
        this.activeLayer = 'ui';
        
        // Projection mapping
        this.keystoneCorrection = {
            topLeft: { x: 0, y: 0 },
            topRight: { x: 1, y: 0 },
            bottomLeft: { x: 0, y: 1 },
            bottomRight: { x: 1, y: 1 }
        };
        
        // Visual settings optimized for projection
        this.projectionSettings = {
            brightness: 1.0,
            contrast: 1.2,
            whiteBalance: 1.0,
            colorTemperature: 6500,  // Kelvin
            gamma: 2.2
        };
        
        this.initializeLayers();
        
        console.log('📽️ Projection Overlay System initialized');
    }
    
    initializeLayers() {
        // UI Layer - Interface elements
        this.addLayer('ui', {
            name: 'User Interface',
            visible: true,
            opacity: 0.9,
            blendMode: 'normal',
            color: '#FFFFFF'
        });
        
        // Contour Layer - Topographic lines
        this.addLayer('contours', {
            name: 'Contour Lines',
            visible: true,
            opacity: 0.7,
            blendMode: 'overlay',
            color: '#FFFFFF'
        });
        
        // Vehicle Layer - RC vehicle indicators
        this.addLayer('vehicles', {
            name: 'Vehicle Tracking',
            visible: true,
            opacity: 0.8,
            blendMode: 'normal',
            color: '#00FF00'
        });
        
        // Mission Layer - Mission-specific overlays
        this.addLayer('mission', {
            name: 'Mission Objectives',
            visible: false,
            opacity: 0.6,
            blendMode: 'multiply',
            color: '#FFFF00'
        });
        
        // Grid Layer - Reference grid
        this.addLayer('grid', {
            name: 'Reference Grid',
            visible: false,
            opacity: 0.3,
            blendMode: 'overlay',
            color: '#FFFFFF'
        });
        
        // Calibration Layer - Projection calibration
        this.addLayer('calibration', {
            name: 'Calibration Markers',
            visible: false,
            opacity: 1.0,
            blendMode: 'normal',
            color: '#FF0000'
        });
    }
    
    addLayer(id, properties) {
        this.layers.set(id, {
            id,
            canvas: document.createElement('canvas'),
            ctx: null,
            ...properties
        });
        
        const layer = this.layers.get(id);
        layer.canvas.width = this.projectorWidth;
        layer.canvas.height = this.projectorHeight;
        layer.ctx = layer.canvas.getContext('2d');
        
        // Set projection-optimized rendering
        layer.ctx.imageSmoothingEnabled = false;
        layer.ctx.textRenderingOptimization = 'optimizeSpeed';
    }
    
    setActiveLayer(layerId) {
        if (this.layers.has(layerId)) {
            this.activeLayer = layerId;
            console.log(`📽️ Active layer: ${layerId}`);
        }
    }
    
    toggleLayer(layerId) {
        const layer = this.layers.get(layerId);
        if (layer) {
            layer.visible = !layer.visible;
            console.log(`👁️ Layer ${layerId}: ${layer.visible ? 'visible' : 'hidden'}`);
        }
    }
    
    setLayerOpacity(layerId, opacity) {
        const layer = this.layers.get(layerId);
        if (layer) {
            layer.opacity = Math.max(0, Math.min(1, opacity));
        }
    }
    
    // Coordinate transformation for projection mapping
    sandboxToProjector(sandboxX, sandboxY) {
        // Convert sandbox coordinates to projector coordinates
        const normalizedX = sandboxX / this.sandboxBounds.width;
        const normalizedY = sandboxY / this.sandboxBounds.height;
        
        // Apply keystone correction
        const correctedCoords = this.applyKeystoneCorrection(normalizedX, normalizedY);
        
        return {
            x: correctedCoords.x * this.projectorWidth,
            y: correctedCoords.y * this.projectorHeight
        };
    }
    
    projectorToSandbox(projectorX, projectorY) {
        // Convert projector coordinates to sandbox coordinates
        const normalizedX = projectorX / this.projectorWidth;
        const normalizedY = projectorY / this.projectorHeight;
        
        // Reverse keystone correction
        const originalCoords = this.reverseKeystoneCorrection(normalizedX, normalizedY);
        
        return {
            x: originalCoords.x * this.sandboxBounds.width,
            y: originalCoords.y * this.sandboxBounds.height
        };
    }
    
    applyKeystoneCorrection(x, y) {
        // Bilinear interpolation for keystone correction
        const tl = this.keystoneCorrection.topLeft;
        const tr = this.keystoneCorrection.topRight;
        const bl = this.keystoneCorrection.bottomLeft;
        const br = this.keystoneCorrection.bottomRight;
        
        // Interpolate top edge
        const top = {
            x: tl.x + (tr.x - tl.x) * x,
            y: tl.y + (tr.y - tl.y) * x
        };
        
        // Interpolate bottom edge
        const bottom = {
            x: bl.x + (br.x - bl.x) * x,
            y: bl.y + (br.y - bl.y) * x
        };
        
        // Final interpolation
        return {
            x: top.x + (bottom.x - top.x) * y,
            y: top.y + (bottom.y - top.y) * y
        };
    }
    
    reverseKeystoneCorrection(x, y) {
        // Simplified reverse transformation (would need more complex math for perfect accuracy)
        return { x, y };
    }
    
    // Rendering methods for each layer
    renderUILayer() {
        const layer = this.layers.get('ui');
        if (!layer.visible) return;
        
        const ctx = layer.ctx;
        ctx.clearRect(0, 0, this.projectorWidth, this.projectorHeight);
        
        // Set projection-optimized styles
        ctx.strokeStyle = layer.color;
        ctx.fillStyle = layer.color;
        ctx.lineWidth = 3;
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        
        // Render UI panels as white outlines
        this.renderInventoryPanel(ctx);
        this.renderObjectivesPanel(ctx);
        this.renderStatusPanel(ctx);
        this.renderControlsPanel(ctx);
    }
    
    renderInventoryPanel(ctx) {
        const panelBounds = this.sandboxToProjector(50, 50);
        const panelSize = { width: 200, height: 250 };
        
        // Panel outline
        ctx.strokeRect(panelBounds.x, panelBounds.y, panelSize.width, panelSize.height);
        
        // Title
        ctx.fillText('INVENTORY', panelBounds.x + panelSize.width/2, panelBounds.y + 30);
        
        // Tool slots
        const slotSize = 50;
        const slotsPerRow = 3;
        const slotSpacing = 10;
        
        for (let i = 0; i < 6; i++) {
            const row = Math.floor(i / slotsPerRow);
            const col = i % slotsPerRow;
            
            const slotX = panelBounds.x + 25 + col * (slotSize + slotSpacing);
            const slotY = panelBounds.y + 60 + row * (slotSize + slotSpacing);
            
            ctx.strokeRect(slotX, slotY, slotSize, slotSize);
            
            // Vehicle labels
            const labels = ['EX001', 'BD001', 'DT001', 'CR001', 'CP001', 'BRUSH'];
            ctx.font = 'bold 12px Arial';
            ctx.fillText(labels[i], slotX + slotSize/2, slotY + slotSize/2 + 4);
        }
    }
    
    renderObjectivesPanel(ctx) {
        const panelBounds = this.sandboxToProjector(700, 50);
        const panelSize = { width: 250, height: 200 };
        
        // Panel outline
        ctx.strokeRect(panelBounds.x, panelBounds.y, panelSize.width, panelSize.height);
        
        // Title
        ctx.font = 'bold 24px Arial';
        ctx.fillText('OBJECTIVES', panelBounds.x + panelSize.width/2, panelBounds.y + 30);
        
        // Objective items
        const objectives = [
            'Initialize terrain system',
            'Deploy RC vehicles',
            'Build road network',
            'Test flood defense'
        ];
        
        ctx.font = '16px Arial';
        objectives.forEach((objective, index) => {
            const y = panelBounds.y + 60 + index * 30;
            
            // Checkbox
            ctx.strokeRect(panelBounds.x + 20, y - 10, 15, 15);
            
            // Objective text
            ctx.textAlign = 'left';
            ctx.fillText(objective, panelBounds.x + 45, y + 2);
        });
    }
    
    renderStatusPanel(ctx) {
        const panelBounds = this.sandboxToProjector(750, 600);
        const panelSize = { width: 200, height: 120 };
        
        // Panel outline
        ctx.strokeRect(panelBounds.x, panelBounds.y, panelSize.width, panelSize.height);
        
        // Title
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('STATUS', panelBounds.x + panelSize.width/2, panelBounds.y + 25);
        
        // Status items
        const statusItems = [
            'Vehicles: 5',
            'Active: 2',
            'Terrain: LIVE',
            'FPS: 30'
        ];
        
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        statusItems.forEach((item, index) => {
            const y = panelBounds.y + 45 + index * 18;
            ctx.fillText(item, panelBounds.x + 15, y);
        });
    }
    
    renderControlsPanel(ctx) {
        const panelBounds = this.sandboxToProjector(50, 600);
        const panelSize = { width: 300, height: 120 };
        
        // Panel outline
        ctx.strokeRect(panelBounds.x, panelBounds.y, panelSize.width, panelSize.height);
        
        // Title
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('CONTROLS', panelBounds.x + panelSize.width/2, panelBounds.y + 25);
        
        // Control instructions
        const controls = [
            'Click = Edit Terrain',
            'Scroll = Brush Size',
            'U = Toggle Mode'
        ];
        
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        controls.forEach((control, index) => {
            const y = panelBounds.y + 45 + index * 18;
            ctx.fillText(control, panelBounds.x + 15, y);
        });
    }
    
    renderContourLayer() {
        const layer = this.layers.get('contours');
        if (!layer.visible || !this.terrainEngine) return;
        
        const ctx = layer.ctx;
        ctx.clearRect(0, 0, this.projectorWidth, this.projectorHeight);
        
        ctx.strokeStyle = layer.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = layer.opacity;
        
        // Render contour lines from terrain engine
        this.renderProjectedContours(ctx);
        
        ctx.globalAlpha = 1.0;
    }
    
    renderProjectedContours(ctx) {
        if (!this.terrainEngine.showContours) return;
        
        const contourInterval = this.terrainEngine.contourInterval;
        const minHeight = -1.0;
        const maxHeight = 1.0;
        
        for (let level = minHeight; level <= maxHeight; level += contourInterval) {
            const lineNumber = Math.round(level / contourInterval);
            
            // Different line styles for projection
            if (lineNumber % 10 === 0) {
                ctx.lineWidth = 4;  // Index contours
                ctx.setLineDash([]);
            } else if (lineNumber % 5 === 0) {
                ctx.lineWidth = 3;  // Major contours
                ctx.setLineDash([]);
            } else {
                ctx.lineWidth = 2;  // Minor contours
                ctx.setLineDash([5, 5]);
            }
            
            ctx.beginPath();
            
            // Convert terrain contours to projection coordinates
            for (let y = 0; y < this.terrainEngine.gridHeight - 1; y++) {
                for (let x = 0; x < this.terrainEngine.gridWidth - 1; x++) {
                    const h1 = this.terrainEngine.heightmap[y * this.terrainEngine.gridWidth + x];
                    const h2 = this.terrainEngine.heightmap[y * this.terrainEngine.gridWidth + (x + 1)];
                    const h3 = this.terrainEngine.heightmap[(y + 1) * this.terrainEngine.gridWidth + x];
                    
                    // Check for contour crossings and convert to projection coordinates
                    if ((h1 <= level && h2 >= level) || (h1 >= level && h2 <= level)) {
                        const t = (level - h1) / (h2 - h1);
                        const sandboxX = (x + t) * (this.sandboxBounds.width / this.terrainEngine.gridWidth);
                        const sandboxY = y * (this.sandboxBounds.height / this.terrainEngine.gridHeight);
                        
                        const projCoords = this.sandboxToProjector(sandboxX, sandboxY);
                        ctx.moveTo(projCoords.x, projCoords.y);
                        
                        const endY = sandboxY + (this.sandboxBounds.height / this.terrainEngine.gridHeight);
                        const endCoords = this.sandboxToProjector(sandboxX, endY);
                        ctx.lineTo(endCoords.x, endCoords.y);
                    }
                    
                    if ((h1 <= level && h3 >= level) || (h1 >= level && h3 <= level)) {
                        const t = (level - h1) / (h3 - h1);
                        const sandboxX = x * (this.sandboxBounds.width / this.terrainEngine.gridWidth);
                        const sandboxY = (y + t) * (this.sandboxBounds.height / this.terrainEngine.gridHeight);
                        
                        const projCoords = this.sandboxToProjector(sandboxX, sandboxY);
                        ctx.moveTo(projCoords.x, projCoords.y);
                        
                        const endX = sandboxX + (this.sandboxBounds.width / this.terrainEngine.gridWidth);
                        const endCoords = this.sandboxToProjector(endX, sandboxY);
                        ctx.lineTo(endCoords.x, endCoords.y);
                    }
                }
            }
            
            ctx.stroke();
            ctx.setLineDash([]);
        }
    }
    
    renderVehicleLayer() {
        const layer = this.layers.get('vehicles');
        if (!layer.visible) return;
        
        const ctx = layer.ctx;
        ctx.clearRect(0, 0, this.projectorWidth, this.projectorHeight);
        
        ctx.strokeStyle = layer.color;
        ctx.fillStyle = layer.color;
        ctx.lineWidth = 3;
        ctx.globalAlpha = layer.opacity;
        
        // Render vehicle indicators (would integrate with vehicle fleet)
        this.renderVehicleIndicators(ctx);
        
        ctx.globalAlpha = 1.0;
    }
    
    renderVehicleIndicators(ctx) {
        // Example vehicle positions (would come from vehicle fleet manager)
        const vehicles = [
            { id: 'EX001', x: 200, y: 300, type: 'excavator' },
            { id: 'BD001', x: 400, y: 200, type: 'bulldozer' },
            { id: 'DT001', x: 600, y: 400, type: 'dump_truck' }
        ];
        
        vehicles.forEach(vehicle => {
            const projCoords = this.sandboxToProjector(vehicle.x, vehicle.y);
            
            // Vehicle circle
            ctx.beginPath();
            ctx.arc(projCoords.x, projCoords.y, 15, 0, Math.PI * 2);
            ctx.stroke();
            
            // Vehicle ID
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(vehicle.id, projCoords.x, projCoords.y - 25);
        });
    }
    
    renderGridLayer() {
        const layer = this.layers.get('grid');
        if (!layer.visible) return;
        
        const ctx = layer.ctx;
        ctx.clearRect(0, 0, this.projectorWidth, this.projectorHeight);
        
        ctx.strokeStyle = layer.color;
        ctx.lineWidth = 1;
        ctx.globalAlpha = layer.opacity;
        ctx.setLineDash([10, 10]);
        
        // Render reference grid
        const gridSpacing = 50; // Sandbox units
        
        // Vertical lines
        for (let x = 0; x <= this.sandboxBounds.width; x += gridSpacing) {
            const startCoords = this.sandboxToProjector(x, 0);
            const endCoords = this.sandboxToProjector(x, this.sandboxBounds.height);
            
            ctx.beginPath();
            ctx.moveTo(startCoords.x, startCoords.y);
            ctx.lineTo(endCoords.x, endCoords.y);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.sandboxBounds.height; y += gridSpacing) {
            const startCoords = this.sandboxToProjector(0, y);
            const endCoords = this.sandboxToProjector(this.sandboxBounds.width, y);
            
            ctx.beginPath();
            ctx.moveTo(startCoords.x, startCoords.y);
            ctx.lineTo(endCoords.x, endCoords.y);
            ctx.stroke();
        }
        
        ctx.setLineDash([]);
        ctx.globalAlpha = 1.0;
    }
    
    renderCalibrationLayer() {
        const layer = this.layers.get('calibration');
        if (!layer.visible) return;
        
        const ctx = layer.ctx;
        ctx.clearRect(0, 0, this.projectorWidth, this.projectorHeight);
        
        ctx.strokeStyle = layer.color;
        ctx.fillStyle = layer.color;
        ctx.lineWidth = 2;
        
        // Render calibration markers at corners
        const markers = [
            { x: 0, y: 0, label: 'TL' },
            { x: this.sandboxBounds.width, y: 0, label: 'TR' },
            { x: 0, y: this.sandboxBounds.height, label: 'BL' },
            { x: this.sandboxBounds.width, y: this.sandboxBounds.height, label: 'BR' }
        ];
        
        markers.forEach(marker => {
            const projCoords = this.sandboxToProjector(marker.x, marker.y);
            
            // Crosshair
            ctx.beginPath();
            ctx.moveTo(projCoords.x - 20, projCoords.y);
            ctx.lineTo(projCoords.x + 20, projCoords.y);
            ctx.moveTo(projCoords.x, projCoords.y - 20);
            ctx.lineTo(projCoords.x, projCoords.y + 20);
            ctx.stroke();
            
            // Circle
            ctx.beginPath();
            ctx.arc(projCoords.x, projCoords.y, 10, 0, Math.PI * 2);
            ctx.stroke();
            
            // Label
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(marker.label, projCoords.x, projCoords.y + 35);
        });
    }
    
    render() {
        // Clear main canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply projection settings
        this.applyProjectionSettings();
        
        // Render each layer
        this.renderUILayer();
        this.renderContourLayer();
        this.renderVehicleLayer();
        this.renderGridLayer();
        this.renderCalibrationLayer();
        
        // Composite all layers
        this.compositeLayers();
    }
    
    applyProjectionSettings() {
        // Apply brightness, contrast, etc.
        this.ctx.filter = `brightness(${this.projectionSettings.brightness}) contrast(${this.projectionSettings.contrast})`;
    }
    
    compositeLayers() {
        // Composite all visible layers onto main canvas
        this.layers.forEach(layer => {
            if (layer.visible) {
                this.ctx.globalAlpha = layer.opacity;
                this.ctx.globalCompositeOperation = layer.blendMode;
                this.ctx.drawImage(layer.canvas, 0, 0);
            }
        });
        
        this.ctx.globalAlpha = 1.0;
        this.ctx.globalCompositeOperation = 'source-over';
    }
    
    // Calibration methods
    startCalibration() {
        this.setActiveLayer('calibration');
        this.toggleLayer('calibration');
        console.log('📽️ Projection calibration started');
    }
    
    setKeystonePoint(corner, x, y) {
        if (this.keystoneCorrection[corner]) {
            this.keystoneCorrection[corner] = { x, y };
            console.log(`📐 Keystone ${corner}: (${x.toFixed(3)}, ${y.toFixed(3)})`);
        }
    }
    
    saveCalibration() {
        const calibrationData = {
            keystoneCorrection: this.keystoneCorrection,
            projectionSettings: this.projectionSettings,
            sandboxBounds: this.sandboxBounds,
            timestamp: Date.now()
        };
        
        localStorage.setItem('projectionCalibration', JSON.stringify(calibrationData));
        console.log('💾 Projection calibration saved');
    }
    
    loadCalibration() {
        try {
            const calibrationData = JSON.parse(localStorage.getItem('projectionCalibration'));
            if (calibrationData) {
                this.keystoneCorrection = calibrationData.keystoneCorrection;
                this.projectionSettings = calibrationData.projectionSettings;
                this.sandboxBounds = calibrationData.sandboxBounds;
                console.log('📂 Projection calibration loaded');
                return true;
            }
        } catch (e) {
            console.warn('⚠️ Failed to load projection calibration');
        }
        return false;
    }
}

// Export for use in other modules
window.ProjectionOverlay = ProjectionOverlay;
