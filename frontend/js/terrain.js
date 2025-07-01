/**
 * Terrain Engine - Real-time terrain visualization and interaction
 * Enhanced with Professional Voxel Construction using Divine Voxel Engine concepts
 * Part of the RC Sandbox modular architecture
 */

class TerrainEngine {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width = window.innerWidth;
        this.height = canvas.height = window.innerHeight;

        // Terrain grid
        this.gridWidth = 100;
        this.gridHeight = 75;
        this.heightmap = new Float32Array(this.gridWidth * this.gridHeight);

        // Rendering parameters
        this.cellWidth = this.width / this.gridWidth;
        this.cellHeight = this.height / this.gridHeight;

        // Scale conversion (1:16 toy scale to real terrain)
        this.toyScale = 16; // 1:16 scale
        this.realWorldWidth = 10; // 10 feet sandbox
        this.realWorldHeight = 7.5; // 7.5 feet sandbox
        this.heightScale = 2.0; // 2 feet max height

        // Topographic parameters
        this.contourInterval = 0.1; // Height interval between contour lines
        this.showContours = true;
        this.showElevationLabels = true;
        this.contourColors = {
            major: 'rgba(255, 255, 255, 0.8)', // Every 5th line
            minor: 'rgba(255, 255, 255, 0.4)', // Regular lines
            index: 'rgba(255, 255, 0, 0.9)'    // Every 10th line
        };

        // Interaction state
        this.isMouseDown = false;
        this.currentTool = 'raise';
        this.brushSize = 20;
        this.intensity = 0.5;

        // Water simulation
        this.waterLevel = 0.0;
        this.waterParticles = [];

        // Color mapping (Magic Sand style)
        this.colorMap = this.createColorMap();

        // Voxel Construction System (inspired by Divine Voxel Engine + Minicraft)
        this.voxelEnabled = true;
        this.voxelSize = 1.0; // Size of each voxel in world units
        this.voxelChunkSize = 16; // Chunk size (like Minicraft)
        this.voxelWorld = new Map(); // Sparse voxel storage
        this.voxelChunks = new Map(); // Chunk management
        this.voxelMaterials = this.initializeVoxelMaterials();
        this.currentVoxelMaterial = 'stone';
        this.voxelConstructionMode = 'place'; // 'place', 'remove', 'paint'
        this.voxelBrushSize = 1;
        this.voxelHeight = 32; // Maximum voxel height
        this.voxelRenderDistance = 8; // Chunks to render around player

        // Leaflet + Topography Mapping System
        this.mappingEnabled = true;
        this.leafletMap = null;
        this.topographyLayer = null;
        this.geoData = null;
        this.realWorldCoords = { lat: 40.7128, lng: -74.0060 }; // Default: NYC
        this.mapScale = 1000; // Meters per grid unit
        this.elevationData = new Map();

        // OpenLayers Advanced Mapping
        this.openLayersMap = null;
        this.vectorLayers = new Map();
        this.rasterLayers = new Map();
        this.gisEnabled = true;

        // THREE.Terrain Enhanced Generation
        this.threeTerrain = null;
        this.terrainGeometry = null;
        this.proceduralEnabled = true;
        this.terrainOptions = {
            xSegments: 63,
            ySegments: 63,
            xSize: 1024,
            ySize: 1024,
            maxHeight: 100,
            minHeight: -100
        };

        // Advanced Noise Generation
        this.noiseGenerators = new Map();
        this.noiseEnabled = true;
        this.noiseTypes = ['perlin', 'simplex', 'ridged', 'fbm', 'turbulence'];
        this.currentNoiseType = 'perlin';

        // Physics engine integration
        this.physicsEngine = null;
        this.enablePhysics = true;

        this.setupEventListeners();
        this.initializeTerrain();
        this.initializePhysics();

        console.log('🗺️ Advanced Terrain Engine initialized');
        console.log(`📏 Scale: 1:${this.toyScale} | Real size: ${this.realWorldWidth}' × ${this.realWorldHeight}'`);
    }
    
    createColorMap() {
        // Magic Sand HeightColorMap.xml data
        return [
            { height: -2.2, color: [0, 0, 0] },      // Deep black
            { height: -2.0, color: [0, 0, 80] },     // Deep blue
            { height: -1.7, color: [0, 30, 100] },   // Blue
            { height: -1.5, color: [0, 50, 102] },   // Blue
            { height: -1.25, color: [19, 108, 160] }, // Light blue
            { height: -0.075, color: [24, 140, 205] }, // Cyan
            { height: -0.025, color: [135, 206, 250] }, // Light cyan
            { height: -0.005, color: [176, 226, 255] }, // Very light blue
            { height: 0, color: [0, 97, 71] },       // Dark green (sea level)
            { height: 0.025, color: [16, 122, 47] }, // Green
            { height: 0.25, color: [232, 215, 125] }, // Sand/tan
            { height: 0.6, color: [161, 67, 0] },    // Brown
            { height: 0.9, color: [130, 30, 30] },   // Dark brown
            { height: 1.4, color: [161, 161, 161] }, // Gray
            { height: 2.0, color: [206, 206, 206] }, // Light gray
            { height: 2.2, color: [255, 255, 255] }  // White peaks
        ];
    }
    
    getColorForHeight(height) {
        // Find the two closest height keys for interpolation
        for (let i = 0; i < this.colorMap.length - 1; i++) {
            const current = this.colorMap[i];
            const next = this.colorMap[i + 1];
            
            if (height >= current.height && height <= next.height) {
                // Linear interpolation between colors
                const t = (height - current.height) / (next.height - current.height);
                return [
                    Math.round(current.color[0] + (next.color[0] - current.color[0]) * t),
                    Math.round(current.color[1] + (next.color[1] - current.color[1]) * t),
                    Math.round(current.color[2] + (next.color[2] - current.color[2]) * t)
                ];
            }
        }
        
        // Default to first or last color
        if (height < this.colorMap[0].height) return this.colorMap[0].color;
        return this.colorMap[this.colorMap.length - 1].color;
    }
    
    initializeTerrain() {
        // Create initial terrain with some variation
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const index = y * this.gridWidth + x;
                
                // Create some initial hills and valleys
                const centerX = this.gridWidth / 2;
                const centerY = this.gridHeight / 2;
                const distFromCenter = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                
                // Base terrain with noise
                let height = Math.sin(x * 0.1) * Math.cos(y * 0.1) * 0.3;
                height += (Math.random() - 0.5) * 0.1;
                
                // Add some hills
                if (distFromCenter < 15) {
                    height += 0.5 * Math.exp(-distFromCenter * 0.1);
                }
                
                this.heightmap[index] = height;
            }
        }
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => {
            this.isMouseDown = true;
            this.modifyTerrain(e);
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isMouseDown) {
                this.modifyTerrain(e);
            }
        });
        
        this.canvas.addEventListener('mouseup', () => {
            this.isMouseDown = false;
        });
        
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.brushSize = Math.max(5, Math.min(50, this.brushSize + (e.deltaY > 0 ? -2 : 2)));
            document.getElementById('brush-size').value = this.brushSize;
            document.getElementById('brush-size-value').textContent = this.brushSize;
        });
        
        window.addEventListener('resize', () => {
            this.width = this.canvas.width = window.innerWidth;
            this.height = this.canvas.height = window.innerHeight;
            this.cellWidth = this.width / this.gridWidth;
            this.cellHeight = this.height / this.gridHeight;
        });
    }
    
    modifyTerrain(event) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        
        // Convert to grid coordinates
        const gridX = Math.floor(mouseX / this.cellWidth);
        const gridY = Math.floor(mouseY / this.cellHeight);
        
        const brushRadius = this.brushSize / Math.max(this.cellWidth, this.cellHeight);
        
        for (let y = Math.max(0, gridY - brushRadius); y < Math.min(this.gridHeight, gridY + brushRadius); y++) {
            for (let x = Math.max(0, gridX - brushRadius); x < Math.min(this.gridWidth, gridX + brushRadius); x++) {
                const distance = Math.sqrt((x - gridX) ** 2 + (y - gridY) ** 2);
                
                if (distance <= brushRadius) {
                    const index = y * this.gridWidth + x;
                    const falloff = 1 - (distance / brushRadius);
                    const effect = this.intensity * falloff * 0.02;
                    
                    switch (this.currentTool) {
                        case 'raise':
                            this.heightmap[index] = Math.min(2.0, this.heightmap[index] + effect);
                            break;
                        case 'lower':
                            this.heightmap[index] = Math.max(-2.0, this.heightmap[index] - effect);
                            break;
                        case 'smooth':
                            // Average with neighbors
                            let sum = 0;
                            let count = 0;
                            for (let dy = -1; dy <= 1; dy++) {
                                for (let dx = -1; dx <= 1; dx++) {
                                    const nx = x + dx;
                                    const ny = y + dy;
                                    if (nx >= 0 && nx < this.gridWidth && ny >= 0 && ny < this.gridHeight) {
                                        sum += this.heightmap[ny * this.gridWidth + nx];
                                        count++;
                                    }
                                }
                            }
                            const average = sum / count;
                            this.heightmap[index] = this.heightmap[index] * (1 - effect) + average * effect;
                            break;
                    }
                }
            }
        }
    }
    
    updateWaterSimulation() {
        // Simple water flow simulation with diffusion
        const newHeightmap = new Float32Array(this.heightmap);
        
        for (let y = 1; y < this.gridHeight - 1; y++) {
            for (let x = 1; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                const currentHeight = this.heightmap[index];
                
                if (currentHeight < this.waterLevel) {
                    // Water erosion effect
                    let lowestNeighbor = currentHeight;
                    let lowestIndex = index;
                    
                    // Check neighbors
                    for (let dy = -1; dy <= 1; dy++) {
                        for (let dx = -1; dx <= 1; dx++) {
                            if (dx === 0 && dy === 0) continue;
                            
                            const nx = x + dx;
                            const ny = y + dy;
                            const nIndex = ny * this.gridWidth + nx;
                            
                            if (this.heightmap[nIndex] < lowestNeighbor) {
                                lowestNeighbor = this.heightmap[nIndex];
                                lowestIndex = nIndex;
                            }
                        }
                    }
                    
                    // Slight erosion toward lowest neighbor
                    if (lowestIndex !== index) {
                        const erosion = 0.001;
                        newHeightmap[index] -= erosion;
                        newHeightmap[lowestIndex] += erosion * 0.5;
                    }
                }
            }
        }
        
        this.heightmap = newHeightmap;
    }
    
    initializePhysics() {
        // Initialize physics engine if available
        if (window.PhysicsEngine && this.enablePhysics) {
            this.physicsEngine = new PhysicsEngine(this);
            console.log('⚛️ Physics engine integrated with terrain');
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Render terrain with elevation colors
        for (let y = 0; y < this.gridHeight - 1; y++) {
            for (let x = 0; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                const height = this.heightmap[index];

                const color = this.getColorForHeight(height);
                this.ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;

                const screenX = x * this.cellWidth;
                const screenY = y * this.cellHeight;

                this.ctx.fillRect(screenX, screenY, this.cellWidth + 1, this.cellHeight + 1);
            }
        }

        // Render physics effects (water, particles)
        if (this.physicsEngine) {
            this.physicsEngine.render(this.ctx);
        }

        // Render voxel constructions
        this.renderVoxels();

        // Render topographic contour lines
        this.renderContourLines();

        // Render scale indicator
        this.renderScaleIndicator();

        // Update physics simulation
        if (this.physicsEngine) {
            this.physicsEngine.update(16.67); // ~60 FPS
        } else {
            // Fallback to simple water simulation
            this.updateWaterSimulation();
        }
    }
    
    convertToRealWorldHeight(normalizedHeight) {
        // Convert normalized height (0-1) to real-world height in feet
        return (normalizedHeight - 0.5) * this.heightScale;
    }

    convertToRealWorldCoords(gridX, gridY) {
        // Convert grid coordinates to real-world coordinates in feet
        const realX = (gridX / this.gridWidth) * this.realWorldWidth;
        const realY = (gridY / this.gridHeight) * this.realWorldHeight;
        return { x: realX, y: realY };
    }

    renderContourLines() {
        if (!this.showContours) return;

        const minHeight = -1.0;
        const maxHeight = 1.0;

        // Render contour lines with different styles
        for (let level = minHeight; level <= maxHeight; level += this.contourInterval) {
            const lineNumber = Math.round(level / this.contourInterval);

            // Determine line style
            let strokeStyle, lineWidth;
            if (lineNumber % 10 === 0) {
                // Index contours (every 10th line)
                strokeStyle = this.contourColors.index;
                lineWidth = 2;
            } else if (lineNumber % 5 === 0) {
                // Major contours (every 5th line)
                strokeStyle = this.contourColors.major;
                lineWidth = 1.5;
            } else {
                // Minor contours
                strokeStyle = this.contourColors.minor;
                lineWidth = 1;
            }

            this.ctx.strokeStyle = strokeStyle;
            this.ctx.lineWidth = lineWidth;
            this.ctx.beginPath();

            // March through grid to find contour crossings
            for (let y = 0; y < this.gridHeight - 1; y++) {
                for (let x = 0; x < this.gridWidth - 1; x++) {
                    const h1 = this.heightmap[y * this.gridWidth + x];
                    const h2 = this.heightmap[y * this.gridWidth + (x + 1)];
                    const h3 = this.heightmap[(y + 1) * this.gridWidth + x];
                    const h4 = this.heightmap[(y + 1) * this.gridWidth + (x + 1)];

                    // Check horizontal edge crossing
                    if ((h1 <= level && h2 >= level) || (h1 >= level && h2 <= level)) {
                        const t = (level - h1) / (h2 - h1);
                        const screenX = (x + t) * this.cellWidth;
                        const screenY = y * this.cellHeight;

                        this.ctx.moveTo(screenX, screenY);
                        this.ctx.lineTo(screenX, screenY + this.cellHeight);
                    }

                    // Check vertical edge crossing
                    if ((h1 <= level && h3 >= level) || (h1 >= level && h3 <= level)) {
                        const t = (level - h1) / (h3 - h1);
                        const screenX = x * this.cellWidth;
                        const screenY = (y + t) * this.cellHeight;

                        this.ctx.moveTo(screenX, screenY);
                        this.ctx.lineTo(screenX + this.cellWidth, screenY);
                    }
                }
            }

            this.ctx.stroke();

            // Add elevation labels for major contours
            if (this.showElevationLabels && lineNumber % 5 === 0) {
                this.renderElevationLabels(level);
            }
        }
    }

    renderElevationLabels(level) {
        const realHeight = this.convertToRealWorldHeight(level);
        const heightInInches = Math.round(realHeight * 12); // Convert feet to inches

        if (Math.abs(heightInInches) < 1) return; // Skip labels near zero

        this.ctx.fillStyle = 'rgba(255, 255, 0, 0.9)';
        this.ctx.font = '10px monospace';
        this.ctx.textAlign = 'center';

        // Place labels at strategic points along contour lines
        const labelSpacing = 150; // pixels between labels

        for (let x = labelSpacing; x < this.width; x += labelSpacing) {
            for (let y = labelSpacing; y < this.height; y += labelSpacing) {
                const gridX = Math.floor(x / this.cellWidth);
                const gridY = Math.floor(y / this.cellHeight);

                if (gridX < this.gridWidth && gridY < this.gridHeight) {
                    const height = this.heightmap[gridY * this.gridWidth + gridX];

                    // Check if this point is close to the contour level
                    if (Math.abs(height - level) < this.contourInterval / 2) {
                        const label = heightInInches > 0 ? `+${heightInInches}"` : `${heightInInches}"`;

                        // Add background for readability
                        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                        this.ctx.fillRect(x - 15, y - 8, 30, 16);

                        this.ctx.fillStyle = 'rgba(255, 255, 0, 0.9)';
                        this.ctx.fillText(label, x, y + 4);
                    }
                }
            }
        }
    }

    renderScaleIndicator() {
        // Render scale indicator in bottom-left corner
        const scaleX = 20;
        const scaleY = this.height - 60;
        const scaleWidth = 100;

        // Background
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(scaleX - 10, scaleY - 25, scaleWidth + 20, 40);

        // Scale bar
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(scaleX, scaleY);
        this.ctx.lineTo(scaleX + scaleWidth, scaleY);
        this.ctx.stroke();

        // Scale ticks
        for (let i = 0; i <= 4; i++) {
            const tickX = scaleX + (i * scaleWidth / 4);
            this.ctx.beginPath();
            this.ctx.moveTo(tickX, scaleY - 5);
            this.ctx.lineTo(tickX, scaleY + 5);
            this.ctx.stroke();
        }

        // Scale labels
        this.ctx.fillStyle = 'white';
        this.ctx.font = '12px monospace';
        this.ctx.textAlign = 'center';

        const realDistance = (scaleWidth / this.width) * this.realWorldWidth;
        const scaleLabel = `${realDistance.toFixed(1)}'`;

        this.ctx.fillText('0', scaleX, scaleY + 20);
        this.ctx.fillText(scaleLabel, scaleX + scaleWidth, scaleY + 20);
        this.ctx.fillText(`Scale 1:${this.toyScale}`, scaleX + scaleWidth/2, scaleY - 15);
    }
    
    setTool(tool) {
        this.currentTool = tool;
    }
    
    setBrushSize(size) {
        this.brushSize = size;
    }
    
    setIntensity(intensity) {
        this.intensity = intensity;
    }
    
    setWaterLevel(level) {
        this.waterLevel = level;
    }

    // Topographic control methods
    setContourInterval(interval) {
        this.contourInterval = Math.max(0.05, Math.min(0.5, interval));
        console.log(`📏 Contour interval set to ${this.contourInterval}`);
    }

    toggleContours() {
        this.showContours = !this.showContours;
        console.log(`🗺️ Contour lines ${this.showContours ? 'enabled' : 'disabled'}`);
    }

    toggleElevationLabels() {
        this.showElevationLabels = !this.showElevationLabels;
        console.log(`🏷️ Elevation labels ${this.showElevationLabels ? 'enabled' : 'disabled'}`);
    }

    getElevationAt(screenX, screenY) {
        // Get real-world elevation at screen coordinates
        const gridX = Math.floor(screenX / this.cellWidth);
        const gridY = Math.floor(screenY / this.cellHeight);

        if (gridX >= 0 && gridX < this.gridWidth && gridY >= 0 && gridY < this.gridHeight) {
            const normalizedHeight = this.heightmap[gridY * this.gridWidth + gridX];
            const realHeight = this.convertToRealWorldHeight(normalizedHeight);
            const realCoords = this.convertToRealWorldCoords(gridX, gridY);

            return {
                elevation: realHeight,
                elevationInches: Math.round(realHeight * 12),
                coordinates: realCoords,
                gridPosition: { x: gridX, y: gridY }
            };
        }

        return null;
    }

    createTopographicProfile(startX, startY, endX, endY) {
        // Create elevation profile between two points
        const profile = [];
        const steps = 50;

        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x = startX + (endX - startX) * t;
            const y = startY + (endY - startY) * t;

            const elevation = this.getElevationAt(x, y);
            if (elevation) {
                profile.push({
                    distance: t * Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2),
                    elevation: elevation.elevation,
                    coordinates: elevation.coordinates
                });
            }
        }

        return profile;
    }

    // Enhanced terrain generation
    generateRealisticTerrain() {
        console.log('🏔️ Generating realistic terrain...');

        // Clear existing terrain
        this.heightmap.fill(0.5);

        // Add multiple layers of noise for realistic terrain
        this.addPerlinNoise(0.01, 0.3); // Large features
        this.addPerlinNoise(0.05, 0.15); // Medium features
        this.addPerlinNoise(0.1, 0.05); // Small details

        // Add some specific features
        this.addMountainPeak(this.gridWidth * 0.3, this.gridHeight * 0.3, 15, 0.4);
        this.addValley(this.gridWidth * 0.7, this.gridHeight * 0.6, 20, -0.3);
        this.addRidge(this.gridWidth * 0.1, this.gridHeight * 0.8, this.gridWidth * 0.9, this.gridHeight * 0.2, 0.2);

        console.log('✅ Realistic terrain generated');
    }

    addPerlinNoise(frequency, amplitude) {
        // Simple Perlin-like noise implementation
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const index = y * this.gridWidth + x;
                const noise = Math.sin(x * frequency) * Math.cos(y * frequency) * amplitude;
                this.heightmap[index] += noise;
            }
        }
    }

    addMountainPeak(centerX, centerY, radius, height) {
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const distance = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                if (distance < radius) {
                    const index = y * this.gridWidth + x;
                    const falloff = 1 - (distance / radius);
                    this.heightmap[index] += height * falloff * falloff;
                }
            }
        }
    }

    addValley(centerX, centerY, radius, depth) {
        this.addMountainPeak(centerX, centerY, radius, depth); // Negative height creates valley
    }

    addRidge(x1, y1, x2, y2, height) {
        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const steps = Math.ceil(length);

        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x = x1 + (x2 - x1) * t;
            const y = y1 + (y2 - y1) * t;

            // Add ridge with some width
            for (let dy = -3; dy <= 3; dy++) {
                for (let dx = -3; dx <= 3; dx++) {
                    const nx = Math.floor(x + dx);
                    const ny = Math.floor(y + dy);

                    if (nx >= 0 && nx < this.gridWidth && ny >= 0 && ny < this.gridHeight) {
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        if (distance <= 3) {
                            const index = ny * this.gridWidth + nx;
                            const falloff = 1 - (distance / 3);
                            this.heightmap[index] += height * falloff;
                        }
                    }
                }
            }
        }
    }

    // Physics control methods
    enablePhysicsSimulation() {
        this.enablePhysics = true;
        if (!this.physicsEngine && window.PhysicsEngine) {
            this.initializePhysics();
        }
        console.log('⚛️ Physics simulation enabled');
    }

    disablePhysicsSimulation() {
        this.enablePhysics = false;
        if (this.physicsEngine) {
            this.physicsEngine.enablePhysics = false;
        }
        console.log('🚫 Physics simulation disabled');
    }

    startRain(intensity = 0.5) {
        if (this.physicsEngine) {
            this.physicsEngine.startRain(intensity);
        }
    }

    stopRain() {
        if (this.physicsEngine) {
            this.physicsEngine.stopRain();
        }
    }

    setWind(speed, direction) {
        if (this.physicsEngine) {
            this.physicsEngine.setWind(speed, direction);
        }
    }

    addWaterAt(screenX, screenY, amount = 0.1) {
        const gridX = Math.floor(screenX / this.cellWidth);
        const gridY = Math.floor(screenY / this.cellHeight);

        if (this.physicsEngine) {
            this.physicsEngine.addWater(gridX, gridY, amount);
        }
    }

    getPhysicsData() {
        return this.physicsEngine ? this.physicsEngine.getPhysicsData() : null;
    }

    // ===== VOXEL CONSTRUCTION SYSTEM =====

    // Initialize voxel materials (inspired by Minicraft block system)
    initializeVoxelMaterials() {
        return {
            air: {
                id: 0,
                name: 'Air',
                color: 'transparent',
                solid: false,
                transparent: true,
                hardness: 0
            },
            stone: {
                id: 1,
                name: 'Stone',
                color: '#808080',
                solid: true,
                transparent: false,
                hardness: 3,
                texture: 'stone'
            },
            dirt: {
                id: 2,
                name: 'Dirt',
                color: '#FF8C00',
                solid: true,
                transparent: false,
                hardness: 1,
                texture: 'dirt'
            },
            grass: {
                id: 3,
                name: 'Grass',
                color: '#228B22',
                solid: true,
                transparent: false,
                hardness: 1,
                texture: 'grass'
            },
            sand: {
                id: 4,
                name: 'Sand',
                color: '#F4A460',
                solid: true,
                transparent: false,
                hardness: 1,
                texture: 'sand'
            },
            water: {
                id: 5,
                name: 'Water',
                color: '#4169E1',
                solid: false,
                transparent: true,
                hardness: 0,
                texture: 'water'
            },
            wood: {
                id: 6,
                name: 'Wood',
                color: '#8B4513',
                solid: true,
                transparent: false,
                hardness: 2,
                texture: 'wood'
            },
            concrete: {
                id: 7,
                name: 'Concrete',
                color: '#C0C0C0',
                solid: true,
                transparent: false,
                hardness: 4,
                texture: 'concrete'
            },
            metal: {
                id: 8,
                name: 'Metal',
                color: '#708090',
                solid: true,
                transparent: false,
                hardness: 5,
                texture: 'metal'
            },
            glass: {
                id: 9,
                name: 'Glass',
                color: '#E0FFFF',
                solid: true,
                transparent: true,
                hardness: 1,
                texture: 'glass'
            }
        };
    }

    // Get voxel at world coordinates
    getVoxel(x, y, z) {
        const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`;
        return this.voxelWorld.get(key) || this.voxelMaterials.air;
    }

    // Set voxel at world coordinates
    setVoxel(x, y, z, materialId) {
        const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`;
        const material = Object.values(this.voxelMaterials).find(m => m.id === materialId);

        if (material) {
            if (material.id === 0) { // Air - remove voxel
                this.voxelWorld.delete(key);
            } else {
                this.voxelWorld.set(key, material);
            }

            // Mark chunk for update
            this.markChunkForUpdate(x, z);
            return true;
        }
        return false;
    }

    // Place voxel at screen coordinates
    placeVoxelAt(screenX, screenY, materialName = null) {
        if (!this.voxelEnabled) return false;

        // Convert screen coordinates to world coordinates
        const worldX = (screenX / this.cellWidth) * (this.realWorldWidth / this.gridWidth);
        const worldZ = (screenY / this.cellHeight) * (this.realWorldHeight / this.gridHeight);

        // Get height from heightmap
        const gridX = Math.floor(screenX / this.cellWidth);
        const gridY = Math.floor(screenY / this.cellHeight);
        const heightmapIndex = gridY * this.gridWidth + gridX;
        const baseHeight = this.heightmap[heightmapIndex] * this.heightScale;

        const material = materialName || this.currentVoxelMaterial;
        const materialData = this.voxelMaterials[material];

        if (!materialData) return false;

        // Place voxel(s) based on brush size
        let placed = false;
        for (let dx = -this.voxelBrushSize; dx <= this.voxelBrushSize; dx++) {
            for (let dz = -this.voxelBrushSize; dz <= this.voxelBrushSize; dz++) {
                const distance = Math.sqrt(dx * dx + dz * dz);
                if (distance <= this.voxelBrushSize) {
                    const voxelX = worldX + dx * this.voxelSize;
                    const voxelZ = worldZ + dz * this.voxelSize;

                    // Find appropriate Y level
                    let voxelY = Math.floor(baseHeight / this.voxelSize);

                    if (this.voxelConstructionMode === 'place') {
                        // Find top solid voxel and place above it
                        while (voxelY < this.voxelHeight) {
                            const existingVoxel = this.getVoxel(voxelX, voxelY + 1, voxelZ);
                            if (existingVoxel.id === 0) { // Air
                                this.setVoxel(voxelX, voxelY + 1, voxelZ, materialData.id);
                                placed = true;
                                break;
                            }
                            voxelY++;
                        }
                    } else if (this.voxelConstructionMode === 'remove') {
                        // Remove top solid voxel
                        while (voxelY >= 0) {
                            const existingVoxel = this.getVoxel(voxelX, voxelY, voxelZ);
                            if (existingVoxel.id !== 0) { // Not air
                                this.setVoxel(voxelX, voxelY, voxelZ, 0); // Set to air
                                placed = true;
                                break;
                            }
                            voxelY--;
                        }
                    }
                }
            }
        }

        return placed;
    }

    // Remove voxel at screen coordinates
    removeVoxelAt(screenX, screenY) {
        const oldMode = this.voxelConstructionMode;
        this.voxelConstructionMode = 'remove';
        const result = this.placeVoxelAt(screenX, screenY);
        this.voxelConstructionMode = oldMode;
        return result;
    }

    // Get chunk coordinates from world coordinates
    getChunkCoords(worldX, worldZ) {
        return {
            x: Math.floor(worldX / (this.voxelChunkSize * this.voxelSize)),
            z: Math.floor(worldZ / (this.voxelChunkSize * this.voxelSize))
        };
    }

    // Mark chunk for update (for future mesh regeneration)
    markChunkForUpdate(worldX, worldZ) {
        const chunkCoords = this.getChunkCoords(worldX, worldZ);
        const chunkKey = `${chunkCoords.x},${chunkCoords.z}`;

        if (!this.voxelChunks.has(chunkKey)) {
            this.voxelChunks.set(chunkKey, {
                x: chunkCoords.x,
                z: chunkCoords.z,
                needsUpdate: true,
                lastUpdate: Date.now()
            });
        } else {
            this.voxelChunks.get(chunkKey).needsUpdate = true;
        }
    }

    // Render voxels on 2D canvas (simple top-down view)
    renderVoxels() {
        if (!this.voxelEnabled) return;

        this.ctx.save();

        // Render each voxel as a colored square
        this.voxelWorld.forEach((material, key) => {
            const [x, y, z] = key.split(',').map(Number);

            // Convert world coordinates to screen coordinates
            const screenX = (x / (this.realWorldWidth / this.gridWidth)) * this.cellWidth;
            const screenY = (z / (this.realWorldHeight / this.gridHeight)) * this.cellHeight;

            // Only render if visible on screen
            if (screenX >= -this.voxelSize && screenX <= this.width + this.voxelSize &&
                screenY >= -this.voxelSize && screenY <= this.height + this.voxelSize) {

                this.ctx.fillStyle = material.color;
                this.ctx.globalAlpha = material.transparent ? 0.7 : 1.0;

                // Add height-based shading
                const heightShade = Math.min(1.0, y / 10); // Lighter at higher elevations
                this.ctx.filter = `brightness(${0.5 + heightShade * 0.5})`;

                this.ctx.fillRect(
                    screenX,
                    screenY,
                    this.cellWidth,
                    this.cellHeight
                );

                // Add border for solid blocks
                if (material.solid) {
                    this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                    this.ctx.lineWidth = 1;
                    this.ctx.strokeRect(screenX, screenY, this.cellWidth, this.cellHeight);
                }
            }
        });

        this.ctx.restore();
    }

    // Set voxel construction mode
    setVoxelMode(mode) {
        if (['place', 'remove', 'paint'].includes(mode)) {
            this.voxelConstructionMode = mode;
            console.log(`🧱 Voxel mode set to: ${mode}`);
            return true;
        }
        return false;
    }

    // Set current voxel material
    setVoxelMaterial(materialName) {
        if (this.voxelMaterials[materialName]) {
            this.currentVoxelMaterial = materialName;
            console.log(`🎨 Voxel material set to: ${materialName}`);
            return true;
        }
        return false;
    }

    // Set voxel brush size
    setVoxelBrushSize(size) {
        this.voxelBrushSize = Math.max(1, Math.min(10, size));
        console.log(`🖌️ Voxel brush size set to: ${this.voxelBrushSize}`);
    }

    // Get voxel construction statistics
    getVoxelStats() {
        const stats = {
            totalVoxels: this.voxelWorld.size,
            chunks: this.voxelChunks.size,
            materials: {}
        };

        // Count materials
        this.voxelWorld.forEach(material => {
            stats.materials[material.name] = (stats.materials[material.name] || 0) + 1;
        });

        return stats;
    }

    // Clear all voxels
    clearVoxels() {
        this.voxelWorld.clear();
        this.voxelChunks.clear();
        console.log('🧹 All voxels cleared');
    }

    // Export voxel data
    exportVoxelData() {
        const data = {
            voxels: Array.from(this.voxelWorld.entries()),
            materials: this.voxelMaterials,
            settings: {
                voxelSize: this.voxelSize,
                chunkSize: this.voxelChunkSize,
                height: this.voxelHeight
            }
        };

        return JSON.stringify(data);
    }

    // Import voxel data
    importVoxelData(jsonData) {
        try {
            const data = JSON.parse(jsonData);

            this.voxelWorld.clear();
            data.voxels.forEach(([key, material]) => {
                this.voxelWorld.set(key, material);
            });

            console.log(`📥 Imported ${data.voxels.length} voxels`);
            return true;
        } catch (error) {
            console.error('❌ Failed to import voxel data:', error);
            return false;
        }
    }
}

// Export for use in other modules
window.TerrainEngine = TerrainEngine;
