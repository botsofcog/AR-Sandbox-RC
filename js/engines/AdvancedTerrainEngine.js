/**
 * Advanced Terrain Engine for AR Sandbox Pro
 * Handles sophisticated terrain manipulation, erosion simulation, and multi-layer terrain types
 */

class AdvancedTerrainEngine {
    constructor(core) {
        this.core = core;
        this.canvas = null;
        this.ctx = null;
        this.heightMap = null;
        this.waterMap = null;
        this.velocityMap = null;
        this.sedimentMap = null;
        this.terrainTypes = null;
        
        // Terrain properties
        this.width = 400;
        this.height = 300;
        this.scale = 2;
        
        // Simulation parameters
        this.erosionParams = {
            evaporationRate: 0.01,
            sedimentCapacity: 4.0,
            minSlope: 0.01,
            gravity: 4.0,
            inertia: 0.05,
            sedimentSolubility: 0.01,
            erosionRadius: 3,
            depositionRate: 0.3
        };
        
        // Terrain types
        this.terrainTypeData = {
            water: { color: [0, 100, 200], height: 0.0, erosion: 0.0 },
            sand: { color: [194, 178, 128], height: 0.3, erosion: 0.8 },
            soil: { color: [101, 67, 33], height: 0.5, erosion: 0.6 },
            grass: { color: [34, 139, 34], height: 0.7, erosion: 0.4 },
            rock: { color: [105, 105, 105], height: 0.9, erosion: 0.1 },
            snow: { color: [255, 250, 250], height: 1.0, erosion: 0.2 }
        };
    }
    
    async initialize() {
        console.log('🏔️ Initializing Advanced Terrain Engine...');
        
        // Create terrain canvas
        this.canvas = document.getElementById('terrain-canvas');
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.id = 'terrain-canvas';
            this.canvas.width = this.width * this.scale;
            this.canvas.height = this.height * this.scale;
            this.canvas.style.position = 'absolute';
            this.canvas.style.top = '0';
            this.canvas.style.left = '0';
            this.canvas.style.zIndex = '10';
            this.canvas.style.pointerEvents = 'none';
            document.body.appendChild(this.canvas);
        }
        
        this.ctx = this.canvas.getContext('2d');
        
        // Initialize terrain data
        this.initializeTerrainData();
        
        // Setup terrain interaction
        this.setupTerrainInteraction();
        
        console.log('✅ Advanced Terrain Engine initialized');
    }
    
    initializeTerrainData() {
        // Initialize height map
        this.heightMap = new Float32Array(this.width * this.height);
        this.waterMap = new Float32Array(this.width * this.height);
        this.velocityMap = new Float32Array(this.width * this.height * 2); // x, y velocity
        this.sedimentMap = new Float32Array(this.width * this.height);
        this.terrainTypes = new Uint8Array(this.width * this.height);
        
        // Generate initial terrain
        this.generateInitialTerrain();
    }
    
    generateInitialTerrain() {
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const index = y * this.width + x;
                
                // Create varied terrain with noise
                const noise1 = this.noise(x * 0.01, y * 0.01) * 0.5;
                const noise2 = this.noise(x * 0.05, y * 0.05) * 0.3;
                const noise3 = this.noise(x * 0.1, y * 0.1) * 0.2;
                
                let height = noise1 + noise2 + noise3;
                height = Math.max(0, Math.min(1, height + 0.3));
                
                this.heightMap[index] = height;
                
                // Determine terrain type based on height
                if (height < 0.2) {
                    this.terrainTypes[index] = 0; // water
                } else if (height < 0.4) {
                    this.terrainTypes[index] = 1; // sand
                } else if (height < 0.6) {
                    this.terrainTypes[index] = 2; // soil
                } else if (height < 0.8) {
                    this.terrainTypes[index] = 3; // grass
                } else if (height < 0.95) {
                    this.terrainTypes[index] = 4; // rock
                } else {
                    this.terrainTypes[index] = 5; // snow
                }
            }
        }
    }
    
    setupTerrainInteraction() {
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        
        const getMousePos = (e) => {
            const rect = this.canvas.getBoundingClientRect();
            return {
                x: Math.floor((e.clientX - rect.left) / this.scale),
                y: Math.floor((e.clientY - rect.top) / this.scale)
            };
        };
        
        this.canvas.style.pointerEvents = 'auto';
        
        this.canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            const pos = getMousePos(e);
            lastX = pos.x;
            lastY = pos.y;
            this.modifyTerrain(pos.x, pos.y);
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing) return;
            const pos = getMousePos(e);
            this.modifyTerrain(pos.x, pos.y);
            lastX = pos.x;
            lastY = pos.y;
        });
        
        this.canvas.addEventListener('mouseup', () => {
            isDrawing = false;
        });
        
        this.canvas.addEventListener('mouseleave', () => {
            isDrawing = false;
        });
    }
    
    modifyTerrain(x, y) {
        const brushSize = this.core.state.brushSize;
        const strength = this.core.state.brushStrength;
        const mode = this.core.state.tool;
        
        for (let dy = -brushSize; dy <= brushSize; dy++) {
            for (let dx = -brushSize; dx <= brushSize; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx < 0 || nx >= this.width || ny < 0 || ny >= this.height) continue;
                
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance > brushSize) continue;
                
                const falloff = 1 - (distance / brushSize);
                const effect = strength * falloff * 0.02;
                
                const index = ny * this.width + nx;
                
                switch (mode) {
                    case 'raise':
                        this.heightMap[index] = Math.min(1, this.heightMap[index] + effect);
                        break;
                    case 'lower':
                        this.heightMap[index] = Math.max(0, this.heightMap[index] - effect);
                        break;
                    case 'smooth':
                        this.smoothTerrain(nx, ny, effect);
                        break;
                    case 'water':
                        this.waterMap[index] = Math.min(1, this.waterMap[index] + effect);
                        break;
                }
                
                // Update terrain type based on new height
                this.updateTerrainType(index);
            }
        }
    }
    
    smoothTerrain(x, y, strength) {
        const index = y * this.width + x;
        let avgHeight = 0;
        let count = 0;
        
        for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
                    avgHeight += this.heightMap[ny * this.width + nx];
                    count++;
                }
            }
        }
        
        avgHeight /= count;
        this.heightMap[index] = this.heightMap[index] * (1 - strength) + avgHeight * strength;
    }
    
    updateTerrainType(index) {
        const height = this.heightMap[index];
        
        if (height < 0.2) {
            this.terrainTypes[index] = 0; // water
        } else if (height < 0.4) {
            this.terrainTypes[index] = 1; // sand
        } else if (height < 0.6) {
            this.terrainTypes[index] = 2; // soil
        } else if (height < 0.8) {
            this.terrainTypes[index] = 3; // grass
        } else if (height < 0.95) {
            this.terrainTypes[index] = 4; // rock
        } else {
            this.terrainTypes[index] = 5; // snow
        }
    }
    
    update(deltaTime) {
        // Run erosion simulation
        this.simulateErosion(deltaTime);
        
        // Update water flow
        this.simulateWaterFlow(deltaTime);
    }
    
    simulateErosion(deltaTime) {
        // Simplified hydraulic erosion
        for (let i = 0; i < 100; i++) {
            const x = Math.floor(Math.random() * this.width);
            const y = Math.floor(Math.random() * this.height);
            this.simulateDroplet(x, y);
        }
    }
    
    simulateDroplet(startX, startY) {
        let x = startX;
        let y = startY;
        let velX = 0;
        let velY = 0;
        let water = 1;
        let sediment = 0;
        
        for (let lifetime = 0; lifetime < 30; lifetime++) {
            const index = Math.floor(y) * this.width + Math.floor(x);
            if (index < 0 || index >= this.heightMap.length) break;
            
            // Calculate gradient
            const gradX = this.getGradientX(x, y);
            const gradY = this.getGradientY(x, y);
            
            // Update velocity
            velX = velX * this.erosionParams.inertia - gradX * (1 - this.erosionParams.inertia);
            velY = velY * this.erosionParams.inertia - gradY * (1 - this.erosionParams.inertia);
            
            // Normalize velocity
            const speed = Math.sqrt(velX * velX + velY * velY);
            if (speed > 0) {
                velX /= speed;
                velY /= speed;
            }
            
            // Move droplet
            x += velX;
            y += velY;
            
            if (x < 0 || x >= this.width - 1 || y < 0 || y >= this.height - 1) break;
            
            // Calculate sediment capacity
            const capacity = Math.max(this.erosionParams.minSlope, speed) * water * this.erosionParams.sedimentCapacity;
            
            if (sediment > capacity) {
                // Deposit sediment
                const deposit = (sediment - capacity) * this.erosionParams.depositionRate;
                this.heightMap[index] += deposit;
                sediment -= deposit;
            } else {
                // Erode terrain
                const erosion = Math.min((capacity - sediment) * this.erosionParams.sedimentSolubility, this.heightMap[index]);
                this.heightMap[index] -= erosion;
                sediment += erosion;
            }
            
            // Evaporate water
            water *= (1 - this.erosionParams.evaporationRate);
            if (water < 0.01) break;
        }
    }
    
    getGradientX(x, y) {
        const x1 = Math.max(0, Math.floor(x) - 1);
        const x2 = Math.min(this.width - 1, Math.floor(x) + 1);
        const index1 = Math.floor(y) * this.width + x1;
        const index2 = Math.floor(y) * this.width + x2;
        return (this.heightMap[index2] - this.heightMap[index1]) / 2;
    }
    
    getGradientY(x, y) {
        const y1 = Math.max(0, Math.floor(y) - 1);
        const y2 = Math.min(this.height - 1, Math.floor(y) + 1);
        const index1 = y1 * this.width + Math.floor(x);
        const index2 = y2 * this.width + Math.floor(x);
        return (this.heightMap[index2] - this.heightMap[index1]) / 2;
    }
    
    simulateWaterFlow(deltaTime) {
        // Simple water flow simulation
        const newWaterMap = new Float32Array(this.waterMap);
        
        for (let y = 1; y < this.height - 1; y++) {
            for (let x = 1; x < this.width - 1; x++) {
                const index = y * this.width + x;
                const currentHeight = this.heightMap[index] + this.waterMap[index];
                
                let totalFlow = 0;
                
                // Check all 4 neighbors
                for (let dy = -1; dy <= 1; dy += 2) {
                    for (let dx = -1; dx <= 1; dx += 2) {
                        if (dx === 0 && dy === 0) continue;
                        
                        const neighborIndex = (y + dy) * this.width + (x + dx);
                        const neighborHeight = this.heightMap[neighborIndex] + this.waterMap[neighborIndex];
                        
                        if (currentHeight > neighborHeight) {
                            const flow = Math.min(this.waterMap[index] * 0.1, (currentHeight - neighborHeight) * 0.5);
                            totalFlow += flow;
                            newWaterMap[neighborIndex] += flow;
                        }
                    }
                }
                
                newWaterMap[index] = Math.max(0, this.waterMap[index] - totalFlow);
            }
        }
        
        this.waterMap = newWaterMap;
    }
    
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const imageData = this.ctx.createImageData(this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const index = y * this.width + x;
                const height = this.heightMap[index];
                const water = this.waterMap[index];
                const terrainType = this.terrainTypes[index];
                
                // Get base color from terrain type
                const typeNames = ['water', 'sand', 'soil', 'grass', 'rock', 'snow'];
                const baseColor = this.terrainTypeData[typeNames[terrainType]].color;
                
                // Apply height-based shading
                const shade = 0.5 + height * 0.5;
                let r = Math.floor(baseColor[0] * shade);
                let g = Math.floor(baseColor[1] * shade);
                let b = Math.floor(baseColor[2] * shade);
                
                // Apply water overlay
                if (water > 0.01) {
                    const waterAlpha = Math.min(1, water * 2);
                    r = Math.floor(r * (1 - waterAlpha) + 0 * waterAlpha);
                    g = Math.floor(g * (1 - waterAlpha) + 100 * waterAlpha);
                    b = Math.floor(b * (1 - waterAlpha) + 200 * waterAlpha);
                }
                
                // Draw scaled pixel
                for (let sy = 0; sy < this.scale; sy++) {
                    for (let sx = 0; sx < this.scale; sx++) {
                        const pixelIndex = ((y * this.scale + sy) * this.canvas.width + (x * this.scale + sx)) * 4;
                        data[pixelIndex] = r;
                        data[pixelIndex + 1] = g;
                        data[pixelIndex + 2] = b;
                        data[pixelIndex + 3] = 255;
                    }
                }
            }
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        
        // Draw contour lines if enabled
        if (this.core.state.showContours) {
            this.drawContourLines();
        }
    }
    
    drawContourLines() {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;
        
        const contourInterval = 0.1;
        
        for (let level = contourInterval; level < 1; level += contourInterval) {
            this.ctx.beginPath();
            
            for (let y = 0; y < this.height - 1; y++) {
                for (let x = 0; x < this.width - 1; x++) {
                    const h1 = this.heightMap[y * this.width + x];
                    const h2 = this.heightMap[y * this.width + (x + 1)];
                    const h3 = this.heightMap[(y + 1) * this.width + x];
                    
                    if ((h1 <= level && h2 > level) || (h1 > level && h2 <= level)) {
                        this.ctx.moveTo(x * this.scale, y * this.scale);
                        this.ctx.lineTo((x + 1) * this.scale, y * this.scale);
                    }
                    
                    if ((h1 <= level && h3 > level) || (h1 > level && h3 <= level)) {
                        this.ctx.moveTo(x * this.scale, y * this.scale);
                        this.ctx.lineTo(x * this.scale, (y + 1) * this.scale);
                    }
                }
            }
            
            this.ctx.stroke();
        }
    }
    
    // Simple noise function
    noise(x, y) {
        const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
        return (n - Math.floor(n)) * 2 - 1;
    }
}
