/**
 * Physics Simulation Engine - Realistic sand physics, water flow, and particle effects
 * Enhanced with Matter.js for advanced 2D physics simulation and Lenia artificial life
 * Part of the RC Sandbox modular architecture
 */

class PhysicsEngine {
    constructor(terrainEngine) {
        this.terrainEngine = terrainEngine;
        this.gridWidth = terrainEngine.gridWidth;
        this.gridHeight = terrainEngine.gridHeight;

        // Matter.js physics world
        this.matterEngine = null;
        this.matterWorld = null;
        this.matterBodies = [];
        this.matterConstraints = [];

        // Initialize Matter.js if available
        this.initMatterJS();

        // Sandboxels-inspired cellular automata elements
        this.elements = this.initSandboxelsElements();
        this.cellularGrid = null;
        this.initCellularAutomata();
        
        // Physics simulation parameters
        this.gravity = 9.81; // m/s²
        this.sandDensity = 1600; // kg/m³
        this.waterDensity = 1000; // kg/m³
        this.airDensity = 1.225; // kg/m³
        
        // Sand physics
        this.angleOfRepose = 35; // degrees
        this.sandFriction = 0.6;
        this.sandCohesion = 0.1;
        this.erosionRate = 0.001;
        
        // Water simulation
        this.waterLevel = new Float32Array(this.gridWidth * this.gridHeight);
        this.waterVelocityX = new Float32Array(this.gridWidth * this.gridHeight);
        this.waterVelocityY = new Float32Array(this.gridWidth * this.gridHeight);
        this.waterFlow = new Float32Array(this.gridWidth * this.gridHeight);
        this.evaporationRate = 0.0001;
        this.infiltrationRate = 0.0005;

        // WebGL Fluid Simulation Integration
        this.webglFluidEnabled = false;
        this.webglFluidCanvas = null;
        this.webglFluidGL = null;
        this.webglFluidConfig = {
            SIM_RESOLUTION: 128,
            DYE_RESOLUTION: 512,
            DENSITY_DISSIPATION: 1,
            VELOCITY_DISSIPATION: 0.2,
            PRESSURE: 0.8,
            PRESSURE_ITERATIONS: 20,
            CURL: 30,
            SPLAT_RADIUS: 0.25,
            SPLAT_FORCE: 6000,
            TRANSPARENT: true,
            BLOOM: false // Disabled for AR overlay
        };
        this.webglFluidPrograms = {};
        this.webglFluidFramebuffers = {};
        this.initWebGLFluidSimulation();
        
        // Particle systems
        this.particles = [];
        this.maxParticles = 1000;
        this.particlePool = [];
        
        // Weather system
        this.weather = {
            windSpeed: 0,
            windDirection: 0,
            humidity: 50,
            temperature: 20,
            precipitation: 0,
            pressure: 1013.25
        };
        
        // Simulation state
        this.timeStep = 1/60; // 60 FPS
        this.simulationSpeed = 1.0;
        this.enablePhysics = true;

        // Lenia Artificial Life System (inspired by Lenia continuous cellular automata)
        this.leniaEnabled = true;
        this.leniaGrid = null;
        this.leniaKernel = null;
        this.leniaGrowthFunction = null;
        this.leniaSpecies = new Map();
        this.leniaAnimationSpeed = 1.0;
        this.leniaRadius = 13; // Default kernel radius
        this.leniaTimeStep = 0.1;
        this.leniaUpdateCounter = 0;

        // WebGL Fluid Simulation System
        this.fluidEnabled = true;
        this.fluidCanvas = null;
        this.fluidGL = null;
        this.fluidPrograms = {};
        this.fluidFramebuffers = {};
        this.fluidTextures = {};
        this.fluidConfig = {
            SIM_RESOLUTION: 128,
            DYE_RESOLUTION: 1024,
            CAPTURE_RESOLUTION: 512,
            DENSITY_DISSIPATION: 1,
            VELOCITY_DISSIPATION: 0.2,
            PRESSURE: 0.8,
            PRESSURE_ITERATIONS: 20,
            CURL: 30,
            SPLAT_RADIUS: 0.25,
            SPLAT_FORCE: 6000,
            SHADING: true,
            COLORFUL: true,
            COLOR_UPDATE_SPEED: 10,
            PAUSED: false,
            BACK_COLOR: { r: 0, g: 0, b: 0 },
            TRANSPARENT: false,
            BLOOM: true,
            BLOOM_ITERATIONS: 8,
            BLOOM_RESOLUTION: 256,
            BLOOM_INTENSITY: 0.8,
            BLOOM_THRESHOLD: 0.6,
            BLOOM_SOFT_KNEE: 0.7,
            SUNRAYS: true,
            SUNRAYS_RESOLUTION: 196,
            SUNRAYS_WEIGHT: 1.0
        };

        this.initializeParticlePool();
        this.initializeLeniaSystem();
        this.initializeWebGLFluid();
        
        console.log('⚛️ Physics Engine initialized');
    }

    // Initialize Matter.js physics engine
    initMatterJS() {
        try {
            if (typeof Matter !== 'undefined') {
                console.log('🔧 Initializing Matter.js physics...');

                // Create Matter.js engine
                this.matterEngine = Matter.Engine.create();
                this.matterWorld = this.matterEngine.world;

                // Configure physics properties
                this.matterEngine.world.gravity.y = 0.8; // Adjust for sandbox scale
                this.matterEngine.world.gravity.x = 0;

                // Create boundaries (invisible walls around sandbox)
                const boundaries = [
                    // Ground
                    Matter.Bodies.rectangle(this.gridWidth/2, this.gridHeight + 10, this.gridWidth, 20, { isStatic: true }),
                    // Left wall
                    Matter.Bodies.rectangle(-10, this.gridHeight/2, 20, this.gridHeight, { isStatic: true }),
                    // Right wall
                    Matter.Bodies.rectangle(this.gridWidth + 10, this.gridHeight/2, 20, this.gridHeight, { isStatic: true }),
                    // Top (optional ceiling)
                    Matter.Bodies.rectangle(this.gridWidth/2, -10, this.gridWidth, 20, { isStatic: true })
                ];

                Matter.World.add(this.matterWorld, boundaries);

                console.log('✅ Matter.js physics initialized');
                return true;
            } else {
                console.warn('⚠️ Matter.js not available, using fallback physics');
                return false;
            }
        } catch (error) {
            console.error('❌ Matter.js initialization failed:', error);
            return false;
        }
    }

    // Add physics body to Matter.js world
    addPhysicsBody(x, y, width, height, options = {}) {
        if (!this.matterEngine) return null;

        try {
            const body = Matter.Bodies.rectangle(x, y, width, height, {
                density: options.density || 0.001,
                friction: options.friction || 0.8,
                restitution: options.restitution || 0.3,
                frictionAir: options.frictionAir || 0.01,
                ...options
            });

            Matter.World.add(this.matterWorld, body);
            this.matterBodies.push(body);

            return body;
        } catch (error) {
            console.error('Error adding physics body:', error);
            return null;
        }
    }

    // Add circular physics body (for particles, balls, etc.)
    addCircleBody(x, y, radius, options = {}) {
        if (!this.matterEngine) return null;

        try {
            const body = Matter.Bodies.circle(x, y, radius, {
                density: options.density || 0.001,
                friction: options.friction || 0.8,
                restitution: options.restitution || 0.6,
                frictionAir: options.frictionAir || 0.01,
                ...options
            });

            Matter.World.add(this.matterWorld, body);
            this.matterBodies.push(body);

            return body;
        } catch (error) {
            console.error('Error adding circle body:', error);
            return null;
        }
    }

    // Update Matter.js physics simulation
    updateMatterPhysics(deltaTime) {
        if (!this.matterEngine) return;

        try {
            // Step the physics simulation
            Matter.Engine.update(this.matterEngine, deltaTime * 1000 * this.simulationSpeed);

            // Clean up bodies that are out of bounds
            this.cleanupOutOfBoundsBodies();

        } catch (error) {
            console.error('Matter.js update error:', error);
        }
    }

    // Remove physics bodies that have fallen out of bounds
    cleanupOutOfBoundsBodies() {
        const bodiesToRemove = [];

        this.matterBodies.forEach((body, index) => {
            if (body.position.y > this.gridHeight + 100 ||
                body.position.x < -100 ||
                body.position.x > this.gridWidth + 100) {
                bodiesToRemove.push({ body, index });
            }
        });

        bodiesToRemove.forEach(({ body, index }) => {
            Matter.World.remove(this.matterWorld, body);
            this.matterBodies.splice(index, 1);
        });
    }

    // Initialize Sandboxels-inspired elements system
    initSandboxelsElements() {
        console.log('🧪 Initializing Sandboxels-inspired elements...');

        return {
            // Basic elements
            sand: {
                name: 'sand',
                color: '#c2b280',
                density: 1.5,
                state: 'powder',
                temp: 20,
                reactions: {
                    water: { result: 'wet_sand', chance: 0.1 }
                },
                behavior: 'fall'
            },

            water: {
                name: 'water',
                color: '#4169e1',
                density: 1.0,
                state: 'liquid',
                temp: 20,
                reactions: {
                    fire: { result: 'steam', chance: 0.3 },
                    lava: { result: 'steam', chance: 0.8 }
                },
                behavior: 'flow'
            },

            fire: {
                name: 'fire',
                color: '#ff4500',
                density: 0.1,
                state: 'energy',
                temp: 800,
                reactions: {
                    water: { result: 'steam', chance: 0.5 },
                    wood: { result: 'fire', chance: 0.2 }
                },
                behavior: 'rise'
            },

            steam: {
                name: 'steam',
                color: '#f0f8ff',
                density: 0.1,
                state: 'gas',
                temp: 100,
                reactions: {},
                behavior: 'rise'
            },

            lava: {
                name: 'lava',
                color: '#ff6347',
                density: 2.5,
                state: 'liquid',
                temp: 1200,
                reactions: {
                    water: { result: 'stone', chance: 0.9 }
                },
                behavior: 'flow'
            },

            stone: {
                name: 'stone',
                color: '#696969',
                density: 2.7,
                state: 'solid',
                temp: 20,
                reactions: {},
                behavior: 'static'
            },

            wood: {
                name: 'wood',
                color: '#8b4513',
                density: 0.8,
                state: 'solid',
                temp: 20,
                reactions: {
                    fire: { result: 'fire', chance: 0.1 }
                },
                behavior: 'static'
            },

            wet_sand: {
                name: 'wet_sand',
                color: '#8b7355',
                density: 1.8,
                state: 'powder',
                temp: 20,
                reactions: {},
                behavior: 'fall'
            },

            metal: {
                name: 'metal',
                color: '#c0c0c0',
                density: 7.8,
                state: 'solid',
                temp: 20,
                reactions: {
                    fire: { result: 'hot_metal', chance: 0.05 }
                },
                behavior: 'static'
            },

            hot_metal: {
                name: 'hot_metal',
                color: '#ff8c00',
                density: 7.8,
                state: 'solid',
                temp: 500,
                reactions: {
                    water: { result: 'steam', chance: 0.3 }
                },
                behavior: 'static'
            }
        };
    }

    // Initialize cellular automata grid
    initCellularAutomata() {
        try {
            console.log('🔬 Initializing cellular automata grid...');

            // Create grid for cellular automata
            this.cellularGrid = [];
            for (let y = 0; y < this.gridHeight; y++) {
                this.cellularGrid[y] = [];
                for (let x = 0; x < this.gridWidth; x++) {
                    this.cellularGrid[y][x] = {
                        element: null,
                        temp: 20,
                        updated: false
                    };
                }
            }

            console.log('✅ Cellular automata initialized');
            return true;

        } catch (error) {
            console.error('❌ Cellular automata initialization failed:', error);
            return false;
        }
    }

    // Add element to cellular automata grid
    addElement(x, y, elementName) {
        if (!this.cellularGrid || !this.elements[elementName]) return false;

        const gridX = Math.floor(x);
        const gridY = Math.floor(y);

        if (gridX < 0 || gridX >= this.gridWidth || gridY < 0 || gridY >= this.gridHeight) {
            return false;
        }

        this.cellularGrid[gridY][gridX] = {
            element: elementName,
            temp: this.elements[elementName].temp,
            updated: false
        };

        return true;
    }

    // Get element at position
    getElement(x, y) {
        if (!this.cellularGrid) return null;

        const gridX = Math.floor(x);
        const gridY = Math.floor(y);

        if (gridX < 0 || gridX >= this.gridWidth || gridY < 0 || gridY >= this.gridHeight) {
            return null;
        }

        return this.cellularGrid[gridY][gridX];
    }

    // Update cellular automata simulation
    updateCellularAutomata(deltaTime) {
        if (!this.cellularGrid || !this.enablePhysics) return;

        try {
            // Reset updated flags
            for (let y = 0; y < this.gridHeight; y++) {
                for (let x = 0; x < this.gridWidth; x++) {
                    this.cellularGrid[y][x].updated = false;
                }
            }

            // Process elements from bottom to top, left to right
            for (let y = this.gridHeight - 1; y >= 0; y--) {
                for (let x = 0; x < this.gridWidth; x++) {
                    const cell = this.cellularGrid[y][x];

                    if (cell.element && !cell.updated) {
                        this.updateElementBehavior(x, y, cell);
                        this.processElementReactions(x, y, cell);
                    }
                }
            }

        } catch (error) {
            console.error('Cellular automata update error:', error);
        }
    }

    // Update element behavior (falling, flowing, rising)
    updateElementBehavior(x, y, cell) {
        const element = this.elements[cell.element];
        if (!element) return;

        switch (element.behavior) {
            case 'fall':
                this.handleFallingBehavior(x, y, cell);
                break;
            case 'flow':
                this.handleFlowingBehavior(x, y, cell);
                break;
            case 'rise':
                this.handleRisingBehavior(x, y, cell);
                break;
            case 'static':
                // Static elements don't move
                break;
        }

        cell.updated = true;
    }

    // Handle falling behavior (sand, powder)
    handleFallingBehavior(x, y, cell) {
        // Try to fall down
        if (this.canMoveTo(x, y + 1)) {
            this.moveElement(x, y, x, y + 1);
        }
        // Try to fall diagonally
        else if (this.canMoveTo(x - 1, y + 1) && Math.random() < 0.5) {
            this.moveElement(x, y, x - 1, y + 1);
        }
        else if (this.canMoveTo(x + 1, y + 1)) {
            this.moveElement(x, y, x + 1, y + 1);
        }
    }

    // Handle flowing behavior (water, lava)
    handleFlowingBehavior(x, y, cell) {
        // Try to fall down first
        if (this.canMoveTo(x, y + 1)) {
            this.moveElement(x, y, x, y + 1);
            return;
        }

        // Flow horizontally
        const direction = Math.random() < 0.5 ? -1 : 1;
        if (this.canMoveTo(x + direction, y)) {
            this.moveElement(x, y, x + direction, y);
        }
        else if (this.canMoveTo(x - direction, y)) {
            this.moveElement(x, y, x - direction, y);
        }
    }

    // Handle rising behavior (fire, steam, gas)
    handleRisingBehavior(x, y, cell) {
        // Try to rise up
        if (this.canMoveTo(x, y - 1)) {
            this.moveElement(x, y, x, y - 1);
        }
        // Try to rise diagonally
        else if (this.canMoveTo(x - 1, y - 1) && Math.random() < 0.5) {
            this.moveElement(x, y, x - 1, y - 1);
        }
        else if (this.canMoveTo(x + 1, y - 1)) {
            this.moveElement(x, y, x + 1, y - 1);
        }
        // Spread horizontally if can't rise
        else {
            const direction = Math.random() < 0.5 ? -1 : 1;
            if (this.canMoveTo(x + direction, y)) {
                this.moveElement(x, y, x + direction, y);
            }
        }
    }

    // Check if element can move to position
    canMoveTo(x, y) {
        if (x < 0 || x >= this.gridWidth || y < 0 || y >= this.gridHeight) {
            return false;
        }

        const targetCell = this.cellularGrid[y][x];
        return !targetCell.element || targetCell.element === null;
    }

    // Move element from one position to another
    moveElement(fromX, fromY, toX, toY) {
        if (!this.canMoveTo(toX, toY)) return false;

        const fromCell = this.cellularGrid[fromY][fromX];
        const toCell = this.cellularGrid[toY][toX];

        // Move element
        toCell.element = fromCell.element;
        toCell.temp = fromCell.temp;
        toCell.updated = true;

        // Clear source
        fromCell.element = null;
        fromCell.temp = 20;
        fromCell.updated = true;

        return true;
    }

    // Process chemical reactions between elements
    processElementReactions(x, y, cell) {
        const element = this.elements[cell.element];
        if (!element || !element.reactions) return;

        // Check neighboring cells for reactions
        const neighbors = [
            { x: x - 1, y: y },     // left
            { x: x + 1, y: y },     // right
            { x: x, y: y - 1 },     // up
            { x: x, y: y + 1 },     // down
        ];

        for (const neighbor of neighbors) {
            if (neighbor.x < 0 || neighbor.x >= this.gridWidth ||
                neighbor.y < 0 || neighbor.y >= this.gridHeight) {
                continue;
            }

            const neighborCell = this.cellularGrid[neighbor.y][neighbor.x];
            if (!neighborCell.element) continue;

            const reaction = element.reactions[neighborCell.element];
            if (reaction && Math.random() < reaction.chance) {
                // Perform reaction
                this.performReaction(x, y, neighbor.x, neighbor.y, reaction);
                break; // Only one reaction per update
            }
        }
    }

    // Perform chemical reaction
    performReaction(x1, y1, x2, y2, reaction) {
        const cell1 = this.cellularGrid[y1][x1];
        const cell2 = this.cellularGrid[y2][x2];

        // Transform elements based on reaction
        if (reaction.result) {
            cell1.element = reaction.result;
            cell1.temp = this.elements[reaction.result]?.temp || cell1.temp;

            // Sometimes transform both elements
            if (Math.random() < 0.5) {
                cell2.element = reaction.result;
                cell2.temp = this.elements[reaction.result]?.temp || cell2.temp;
            }
        }
    }

    // Get cellular automata statistics
    getCellularStats() {
        if (!this.cellularGrid) return null;

        const stats = {};
        let totalElements = 0;

        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const cell = this.cellularGrid[y][x];
                if (cell.element) {
                    stats[cell.element] = (stats[cell.element] || 0) + 1;
                    totalElements++;
                }
            }
        }

        return {
            elements: stats,
            totalElements,
            availableElements: Object.keys(this.elements)
        };
    }

    initializeParticlePool() {
        // Pre-allocate particle objects for performance
        for (let i = 0; i < this.maxParticles; i++) {
            this.particlePool.push({
                x: 0, y: 0, z: 0,
                vx: 0, vy: 0, vz: 0,
                life: 0, maxLife: 1,
                size: 1, color: '#FFFFFF',
                type: 'sand', // sand, water, dust, debris
                active: false
            });
        }
    }
    
    update(deltaTime) {
        if (!this.enablePhysics) return;

        const dt = deltaTime * this.simulationSpeed;

        // Update Matter.js physics simulation
        this.updateMatterPhysics(dt);

        // Update Sandboxels-inspired cellular automata
        this.updateCellularAutomata(dt);

        // Update physics simulations
        this.updateSandPhysics(dt);
        this.updateWaterSimulation(dt);
        this.updateParticleSystem(dt);
        this.updateWeatherEffects(dt);
        this.updateErosion(dt);

        // Update Lenia artificial life system
        this.updateLeniaSystem(dt);
    }
    
    updateSandPhysics(deltaTime) {
        // Implement cellular automata for sand physics
        const heightmap = this.terrainEngine.heightmap;
        const newHeightmap = new Float32Array(heightmap);
        
        for (let y = 1; y < this.gridHeight - 1; y++) {
            for (let x = 1; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                const currentHeight = heightmap[index];
                
                // Check stability based on angle of repose
                const neighbors = this.getNeighborHeights(x, y, heightmap);
                const maxSlope = this.calculateMaxSlope(neighbors);
                
                if (maxSlope > Math.tan(this.angleOfRepose * Math.PI / 180)) {
                    // Sand is unstable, calculate avalanche
                    const avalanche = this.calculateAvalanche(x, y, heightmap, deltaTime);
                    
                    // Apply avalanche effects
                    newHeightmap[index] -= avalanche.removed;
                    
                    // Distribute sand to lower neighbors
                    for (const neighbor of avalanche.distribution) {
                        const nIndex = neighbor.y * this.gridWidth + neighbor.x;
                        newHeightmap[nIndex] += neighbor.amount;
                        
                        // Create sand particles for visual effect
                        this.createSandParticles(neighbor.x, neighbor.y, neighbor.amount);
                    }
                }
            }
        }
        
        // Apply changes with smoothing
        for (let i = 0; i < heightmap.length; i++) {
            heightmap[i] = heightmap[i] * 0.9 + newHeightmap[i] * 0.1;
        }
    }
    
    getNeighborHeights(x, y, heightmap) {
        const neighbors = [];
        
        for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
                if (dx === 0 && dy === 0) continue;
                
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx >= 0 && nx < this.gridWidth && ny >= 0 && ny < this.gridHeight) {
                    const nIndex = ny * this.gridWidth + nx;
                    neighbors.push({
                        x: nx, y: ny,
                        height: heightmap[nIndex],
                        distance: Math.sqrt(dx * dx + dy * dy)
                    });
                }
            }
        }
        
        return neighbors;
    }
    
    calculateMaxSlope(neighbors) {
        let maxSlope = 0;
        
        for (const neighbor of neighbors) {
            const slope = Math.abs(neighbor.height) / neighbor.distance;
            maxSlope = Math.max(maxSlope, slope);
        }
        
        return maxSlope;
    }
    
    calculateAvalanche(x, y, heightmap, deltaTime) {
        const index = y * this.gridWidth + x;
        const currentHeight = heightmap[index];
        const neighbors = this.getNeighborHeights(x, y, heightmap);
        
        // Find lowest neighbors
        const lowerNeighbors = neighbors.filter(n => n.height < currentHeight);
        lowerNeighbors.sort((a, b) => a.height - b.height);
        
        // Calculate sand to remove
        const excessHeight = currentHeight - (lowerNeighbors[0]?.height || currentHeight);
        const sandToMove = Math.min(excessHeight * 0.1 * deltaTime, 0.01);
        
        // Distribute sand to lower neighbors
        const distribution = [];
        let totalWeight = 0;
        
        for (const neighbor of lowerNeighbors.slice(0, 4)) { // Max 4 neighbors
            const weight = (currentHeight - neighbor.height) / neighbor.distance;
            totalWeight += weight;
            distribution.push({ ...neighbor, weight });
        }
        
        // Normalize distribution
        for (const dist of distribution) {
            dist.amount = (dist.weight / totalWeight) * sandToMove;
        }
        
        return {
            removed: sandToMove,
            distribution
        };
    }
    
    updateWaterSimulation(deltaTime) {
        // Shallow water equations simulation
        const heightmap = this.terrainEngine.heightmap;
        
        // Add precipitation
        if (this.weather.precipitation > 0) {
            this.addPrecipitation(deltaTime);
        }
        
        // Calculate water flow using height differences
        this.calculateWaterFlow(heightmap, deltaTime);
        
        // Update water positions
        this.advectWater(deltaTime);
        
        // Apply evaporation and infiltration
        this.applyWaterLoss(deltaTime);
        
        // Update water visual effects
        this.updateWaterParticles(deltaTime);
    }
    
    addPrecipitation(deltaTime) {
        const rainAmount = this.weather.precipitation * deltaTime * 0.001;
        
        for (let i = 0; i < this.waterLevel.length; i++) {
            this.waterLevel[i] += rainAmount;
            
            // Create rain particles
            if (Math.random() < 0.1) {
                const x = i % this.gridWidth;
                const y = Math.floor(i / this.gridWidth);
                this.createRainParticle(x, y);
            }
        }
    }
    
    calculateWaterFlow(heightmap, deltaTime) {
        const newVelX = new Float32Array(this.waterVelocityX);
        const newVelY = new Float32Array(this.waterVelocityY);
        
        for (let y = 1; y < this.gridHeight - 1; y++) {
            for (let x = 1; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                
                if (this.waterLevel[index] > 0.001) {
                    // Calculate pressure gradients
                    const totalHeight = heightmap[index] + this.waterLevel[index];
                    
                    const leftHeight = heightmap[index - 1] + this.waterLevel[index - 1];
                    const rightHeight = heightmap[index + 1] + this.waterLevel[index + 1];
                    const topHeight = heightmap[index - this.gridWidth] + this.waterLevel[index - this.gridWidth];
                    const bottomHeight = heightmap[index + this.gridWidth] + this.waterLevel[index + this.gridWidth];
                    
                    // Calculate acceleration due to gravity
                    const accelX = -this.gravity * (rightHeight - leftHeight) / 2;
                    const accelY = -this.gravity * (bottomHeight - topHeight) / 2;
                    
                    // Update velocities
                    newVelX[index] += accelX * deltaTime;
                    newVelY[index] += accelY * deltaTime;
                    
                    // Apply friction
                    const friction = 0.95;
                    newVelX[index] *= friction;
                    newVelY[index] *= friction;
                }
            }
        }
        
        this.waterVelocityX.set(newVelX);
        this.waterVelocityY.set(newVelY);
    }
    
    advectWater(deltaTime) {
        const newWaterLevel = new Float32Array(this.waterLevel);
        
        for (let y = 1; y < this.gridHeight - 1; y++) {
            for (let x = 1; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                
                if (this.waterLevel[index] > 0.001) {
                    const velX = this.waterVelocityX[index];
                    const velY = this.waterVelocityY[index];
                    
                    // Calculate water movement
                    const moveX = velX * deltaTime;
                    const moveY = velY * deltaTime;
                    
                    // Distribute water to neighboring cells
                    const waterToMove = this.waterLevel[index] * 0.1;
                    
                    if (Math.abs(moveX) > 0.1) {
                        const targetX = Math.round(x + Math.sign(moveX));
                        if (targetX >= 0 && targetX < this.gridWidth) {
                            const targetIndex = y * this.gridWidth + targetX;
                            newWaterLevel[targetIndex] += waterToMove * Math.abs(moveX);
                            newWaterLevel[index] -= waterToMove * Math.abs(moveX);
                        }
                    }
                    
                    if (Math.abs(moveY) > 0.1) {
                        const targetY = Math.round(y + Math.sign(moveY));
                        if (targetY >= 0 && targetY < this.gridHeight) {
                            const targetIndex = targetY * this.gridWidth + x;
                            newWaterLevel[targetIndex] += waterToMove * Math.abs(moveY);
                            newWaterLevel[index] -= waterToMove * Math.abs(moveY);
                        }
                    }
                }
            }
        }
        
        this.waterLevel.set(newWaterLevel);
    }
    
    applyWaterLoss(deltaTime) {
        for (let i = 0; i < this.waterLevel.length; i++) {
            if (this.waterLevel[i] > 0) {
                // Evaporation
                const evaporation = this.evaporationRate * deltaTime * 
                                  (this.weather.temperature / 20) * 
                                  (1 - this.weather.humidity / 100);
                
                // Infiltration into sand
                const infiltration = this.infiltrationRate * deltaTime;
                
                const totalLoss = evaporation + infiltration;
                this.waterLevel[i] = Math.max(0, this.waterLevel[i] - totalLoss);
            }
        }
    }
    
    updateParticleSystem(deltaTime) {
        for (const particle of this.particles) {
            if (!particle.active) continue;
            
            // Update position
            particle.x += particle.vx * deltaTime;
            particle.y += particle.vy * deltaTime;
            particle.z += particle.vz * deltaTime;
            
            // Apply gravity
            particle.vz -= this.gravity * deltaTime;
            
            // Apply air resistance
            const airResistance = 0.98;
            particle.vx *= airResistance;
            particle.vy *= airResistance;
            particle.vz *= airResistance;
            
            // Update life
            particle.life -= deltaTime;
            
            // Check for ground collision
            if (particle.z <= 0) {
                particle.z = 0;
                particle.vz = 0;
                particle.vx *= 0.5; // Bounce damping
                particle.vy *= 0.5;
            }
            
            // Deactivate dead particles
            if (particle.life <= 0) {
                particle.active = false;
            }
        }
        
        // Remove inactive particles
        this.particles = this.particles.filter(p => p.active);
    }
    
    updateWeatherEffects(deltaTime) {
        // Simulate weather changes
        this.weather.windSpeed += (Math.random() - 0.5) * 0.1;
        this.weather.windSpeed = Math.max(0, Math.min(20, this.weather.windSpeed));
        
        this.weather.windDirection += (Math.random() - 0.5) * 0.1;
        this.weather.windDirection = (this.weather.windDirection + 360) % 360;
        
        // Wind effects on particles
        const windForceX = Math.cos(this.weather.windDirection * Math.PI / 180) * this.weather.windSpeed * 0.1;
        const windForceY = Math.sin(this.weather.windDirection * Math.PI / 180) * this.weather.windSpeed * 0.1;
        
        for (const particle of this.particles) {
            if (particle.active && particle.type === 'dust') {
                particle.vx += windForceX * deltaTime;
                particle.vy += windForceY * deltaTime;
            }
        }
    }
    
    updateErosion(deltaTime) {
        // Water erosion simulation
        const heightmap = this.terrainEngine.heightmap;
        
        for (let y = 1; y < this.gridHeight - 1; y++) {
            for (let x = 1; x < this.gridWidth - 1; x++) {
                const index = y * this.gridWidth + x;
                
                if (this.waterLevel[index] > 0.01) {
                    const waterSpeed = Math.sqrt(
                        this.waterVelocityX[index] ** 2 + 
                        this.waterVelocityY[index] ** 2
                    );
                    
                    // Erosion proportional to water speed and volume
                    const erosionAmount = this.erosionRate * waterSpeed * 
                                        this.waterLevel[index] * deltaTime;
                    
                    heightmap[index] -= erosionAmount;
                    
                    // Create sediment particles
                    if (erosionAmount > 0.001) {
                        this.createSedimentParticles(x, y, erosionAmount);
                    }
                }
            }
        }
    }
    
    // Particle creation methods
    createSandParticles(x, y, amount) {
        const numParticles = Math.min(Math.floor(amount * 100), 10);
        
        for (let i = 0; i < numParticles; i++) {
            const particle = this.getParticleFromPool();
            if (!particle) break;
            
            particle.x = x + (Math.random() - 0.5) * 2;
            particle.y = y + (Math.random() - 0.5) * 2;
            particle.z = this.terrainEngine.heightmap[y * this.gridWidth + x] + 0.1;
            
            particle.vx = (Math.random() - 0.5) * 2;
            particle.vy = (Math.random() - 0.5) * 2;
            particle.vz = Math.random() * 2;
            
            particle.life = 2 + Math.random() * 3;
            particle.maxLife = particle.life;
            particle.size = 0.5 + Math.random() * 1;
            particle.color = '#D2B48C'; // Sandy brown
            particle.type = 'sand';
            particle.active = true;
        }
    }
    
    createWaterParticles(x, y) {
        const particle = this.getParticleFromPool();
        if (!particle) return;
        
        particle.x = x + (Math.random() - 0.5);
        particle.y = y + (Math.random() - 0.5);
        particle.z = this.terrainEngine.heightmap[y * this.gridWidth + x] + 0.05;
        
        particle.vx = this.waterVelocityX[y * this.gridWidth + x] + (Math.random() - 0.5) * 0.5;
        particle.vy = this.waterVelocityY[y * this.gridWidth + x] + (Math.random() - 0.5) * 0.5;
        particle.vz = 0;
        
        particle.life = 1 + Math.random() * 2;
        particle.maxLife = particle.life;
        particle.size = 0.3 + Math.random() * 0.5;
        particle.color = '#4169E1'; // Royal blue
        particle.type = 'water';
        particle.active = true;
    }
    
    createRainParticle(x, y) {
        const particle = this.getParticleFromPool();
        if (!particle) return;
        
        particle.x = x + (Math.random() - 0.5) * 5;
        particle.y = y + (Math.random() - 0.5) * 5;
        particle.z = 10 + Math.random() * 5;
        
        particle.vx = this.weather.windSpeed * Math.cos(this.weather.windDirection * Math.PI / 180) * 0.1;
        particle.vy = this.weather.windSpeed * Math.sin(this.weather.windDirection * Math.PI / 180) * 0.1;
        particle.vz = -5 - Math.random() * 3;
        
        particle.life = 3;
        particle.maxLife = particle.life;
        particle.size = 0.2;
        particle.color = '#87CEEB'; // Sky blue
        particle.type = 'rain';
        particle.active = true;
    }
    
    createSedimentParticles(x, y, amount) {
        const numParticles = Math.min(Math.floor(amount * 50), 5);
        
        for (let i = 0; i < numParticles; i++) {
            const particle = this.getParticleFromPool();
            if (!particle) break;
            
            particle.x = x + (Math.random() - 0.5);
            particle.y = y + (Math.random() - 0.5);
            particle.z = this.terrainEngine.heightmap[y * this.gridWidth + x] + 0.05;
            
            particle.vx = this.waterVelocityX[y * this.gridWidth + x] * 0.5;
            particle.vy = this.waterVelocityY[y * this.gridWidth + x] * 0.5;
            particle.vz = 0;
            
            particle.life = 5 + Math.random() * 5;
            particle.maxLife = particle.life;
            particle.size = 0.3 + Math.random() * 0.3;
            particle.color = '#8B4513'; // Saddle brown
            particle.type = 'sediment';
            particle.active = true;
        }
    }
    
    getParticleFromPool() {
        // Find inactive particle in pool
        for (const particle of this.particlePool) {
            if (!particle.active) {
                return particle;
            }
        }
        
        // If no inactive particles, reuse oldest active one
        if (this.particles.length > 0) {
            const oldest = this.particles.reduce((prev, current) => 
                prev.life < current.life ? prev : current
            );
            oldest.active = false;
            return oldest;
        }
        
        return null;
    }
    
    updateWaterParticles(deltaTime) {
        // Create water particles where water is flowing
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const index = y * this.gridWidth + x;
                
                if (this.waterLevel[index] > 0.01) {
                    const speed = Math.sqrt(
                        this.waterVelocityX[index] ** 2 + 
                        this.waterVelocityY[index] ** 2
                    );
                    
                    // Create particles based on water speed
                    if (speed > 0.1 && Math.random() < 0.05) {
                        this.createWaterParticles(x, y);
                    }
                }
            }
        }
    }
    
    // Public control methods
    setWeather(weatherData) {
        Object.assign(this.weather, weatherData);
        console.log('🌤️ Weather updated:', this.weather);
    }
    
    startRain(intensity = 0.5) {
        this.weather.precipitation = intensity;
        console.log(`🌧️ Rain started (intensity: ${intensity})`);
    }
    
    stopRain() {
        this.weather.precipitation = 0;
        console.log('☀️ Rain stopped');
    }
    
    setWind(speed, direction) {
        this.weather.windSpeed = speed;
        this.weather.windDirection = direction;
        console.log(`💨 Wind set: ${speed} m/s at ${direction}°`);
    }
    
    addWater(x, y, amount) {
        const index = y * this.gridWidth + x;
        if (index >= 0 && index < this.waterLevel.length) {
            this.waterLevel[index] += amount;
            this.createWaterParticles(x, y);
        }
    }
    
    drainWater(x, y, amount) {
        const index = y * this.gridWidth + x;
        if (index >= 0 && index < this.waterLevel.length) {
            this.waterLevel[index] = Math.max(0, this.waterLevel[index] - amount);
        }
    }
    
    getPhysicsData() {
        return {
            sandPhysics: {
                angleOfRepose: this.angleOfRepose,
                friction: this.sandFriction,
                cohesion: this.sandCohesion
            },
            waterSimulation: {
                totalWater: this.waterLevel.reduce((sum, level) => sum + level, 0),
                averageFlow: this.waterFlow.reduce((sum, flow) => sum + flow, 0) / this.waterFlow.length,
                evaporationRate: this.evaporationRate
            },
            particles: {
                active: this.particles.filter(p => p.active).length,
                total: this.particles.length,
                poolSize: this.particlePool.length
            },
            weather: { ...this.weather }
        };
    }
    
    render(ctx) {
        // Render water overlay
        this.renderWater(ctx);

        // Render particles
        this.renderParticles(ctx);

        // Render Lenia artificial life
        this.renderLeniaSystem(ctx);

        // Render weather effects
        this.renderWeatherEffects(ctx);
    }
    
    renderWater(ctx) {
        const cellWidth = ctx.canvas.width / this.gridWidth;
        const cellHeight = ctx.canvas.height / this.gridHeight;
        
        ctx.save();
        ctx.globalAlpha = 0.6;
        
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const index = y * this.gridWidth + x;
                const waterLevel = this.waterLevel[index];
                
                if (waterLevel > 0.001) {
                    const alpha = Math.min(1, waterLevel * 10);
                    ctx.fillStyle = `rgba(65, 105, 225, ${alpha})`;
                    ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
                }
            }
        }
        
        ctx.restore();
    }
    
    renderParticles(ctx) {
        const cellWidth = ctx.canvas.width / this.gridWidth;
        const cellHeight = ctx.canvas.height / this.gridHeight;
        
        ctx.save();
        
        for (const particle of this.particles) {
            if (!particle.active) continue;
            
            const screenX = particle.x * cellWidth;
            const screenY = particle.y * cellHeight;
            const alpha = particle.life / particle.maxLife;
            
            ctx.globalAlpha = alpha;
            ctx.fillStyle = particle.color;
            
            ctx.beginPath();
            ctx.arc(screenX, screenY, particle.size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        ctx.restore();
    }
    
    renderWeatherEffects(ctx) {
        // Render wind direction indicator
        if (this.weather.windSpeed > 1) {
            ctx.save();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 2;
            
            const centerX = ctx.canvas.width - 50;
            const centerY = 50;
            const length = this.weather.windSpeed * 2;
            
            const endX = centerX + Math.cos(this.weather.windDirection * Math.PI / 180) * length;
            const endY = centerY + Math.sin(this.weather.windDirection * Math.PI / 180) * length;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
            
            // Arrow head
            const arrowSize = 5;
            const angle = this.weather.windDirection * Math.PI / 180;
            ctx.beginPath();
            ctx.moveTo(endX, endY);
            ctx.lineTo(endX - arrowSize * Math.cos(angle - 0.5), endY - arrowSize * Math.sin(angle - 0.5));
            ctx.moveTo(endX, endY);
            ctx.lineTo(endX - arrowSize * Math.cos(angle + 0.5), endY - arrowSize * Math.sin(angle + 0.5));
            ctx.stroke();
            
            ctx.restore();
        }
    }

    // ===== LENIA ARTIFICIAL LIFE SYSTEM =====

    // Initialize Lenia artificial life system
    initializeLeniaSystem() {
        try {
            console.log('🧬 Initializing Lenia artificial life system...');

            // Create Lenia grid matching terrain dimensions
            const width = this.terrainEngine.gridWidth || 100;
            const height = this.terrainEngine.gridHeight || 75;

            this.leniaGrid = Array(height).fill().map(() => Array(width).fill(0));

            // Initialize kernel for convolution (Gaussian-like)
            this.initializeLeniaKernel();

            // Initialize growth function
            this.initializeLeniaGrowthFunction();

            // Initialize species
            this.initializeLeniaSpecies();

            // Spawn initial life forms
            this.spawnInitialLifeForms();

            console.log('✅ Lenia artificial life system initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Lenia system:', error);
            this.leniaEnabled = false;
        }
    }

    // Initialize convolution kernel (inspired by Lenia)
    initializeLeniaKernel() {
        const R = this.leniaRadius;
        const size = R * 2 + 1;
        this.leniaKernel = Array(size).fill().map(() => Array(size).fill(0));

        // Create Gaussian-like kernel
        const center = R;
        let sum = 0;

        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                const dx = x - center;
                const dy = y - center;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance <= R) {
                    // Gaussian-like function
                    const value = Math.exp(-0.5 * (distance / (R * 0.3)) ** 2);
                    this.leniaKernel[y][x] = value;
                    sum += value;
                }
            }
        }

        // Normalize kernel
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                this.leniaKernel[y][x] /= sum;
            }
        }
    }

    // Initialize growth function (inspired by Lenia)
    initializeLeniaGrowthFunction() {
        // Growth function parameters
        this.leniaGrowthFunction = {
            mu: 0.15,    // Growth center
            sigma: 0.017, // Growth width

            // Growth function: Gaussian bell curve
            calculate: function(x) {
                const diff = x - this.mu;
                return 2 * Math.exp(-0.5 * (diff / this.sigma) ** 2) - 1;
            }
        };
    }

    // Initialize Lenia species (inspired by actual Lenia organisms)
    initializeLeniaSpecies() {
        // Orbium - the classic Lenia organism
        this.leniaSpecies.set('orbium', {
            name: 'Orbium',
            color: '#4CAF50',
            growthRate: 0.1,
            mu: 0.15,
            sigma: 0.017,
            pattern: this.createOrbiumPattern()
        });

        // Scutium - shield-like organism
        this.leniaSpecies.set('scutium', {
            name: 'Scutium',
            color: '#2196F3',
            growthRate: 0.08,
            mu: 0.29,
            sigma: 0.043,
            pattern: this.createScutiumPattern()
        });

        // Gyrorbium - rotating organism
        this.leniaSpecies.set('gyrorbium', {
            name: 'Gyrorbium',
            color: '#FF9800',
            growthRate: 0.12,
            mu: 0.156,
            sigma: 0.0224,
            pattern: this.createGyrorbiumPattern()
        });
    }

    // Create Orbium pattern (simplified)
    createOrbiumPattern() {
        const pattern = Array(13).fill().map(() => Array(13).fill(0));
        const center = 6;

        // Create circular pattern with gradient
        for (let y = 0; y < 13; y++) {
            for (let x = 0; x < 13; x++) {
                const dx = x - center;
                const dy = y - center;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance <= 6) {
                    pattern[y][x] = Math.max(0, 1 - distance / 6) * 0.8;
                }
            }
        }

        return pattern;
    }

    // Create Scutium pattern (simplified)
    createScutiumPattern() {
        const pattern = Array(13).fill().map(() => Array(13).fill(0));

        // Create shield-like pattern
        for (let y = 0; y < 13; y++) {
            for (let x = 0; x < 13; x++) {
                if (y < 8 && x >= 2 && x <= 10) {
                    const intensity = (8 - y) / 8 * 0.9;
                    pattern[y][x] = intensity;
                }
            }
        }

        return pattern;
    }

    // Create Gyrorbium pattern (simplified)
    createGyrorbiumPattern() {
        const pattern = Array(13).fill().map(() => Array(13).fill(0));
        const center = 6;

        // Create spiral-like pattern
        for (let y = 0; y < 13; y++) {
            for (let x = 0; x < 13; x++) {
                const dx = x - center;
                const dy = y - center;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const angle = Math.atan2(dy, dx);

                if (distance <= 5) {
                    const spiral = Math.sin(angle * 3 + distance * 0.5);
                    pattern[y][x] = Math.max(0, spiral * (1 - distance / 5)) * 0.7;
                }
            }
        }

        return pattern;
    }

    // Spawn initial life forms
    spawnInitialLifeForms() {
        const width = this.leniaGrid[0].length;
        const height = this.leniaGrid.length;

        // Spawn a few random organisms
        for (let i = 0; i < 3; i++) {
            const x = Math.floor(Math.random() * (width - 20)) + 10;
            const y = Math.floor(Math.random() * (height - 20)) + 10;
            const species = ['orbium', 'scutium', 'gyrorbium'][i % 3];

            this.spawnOrganism(x, y, species);
        }
    }

    // Spawn organism at specific location
    spawnOrganism(x, y, speciesName) {
        const species = this.leniaSpecies.get(speciesName);
        if (!species) return;

        const pattern = species.pattern;
        const patternHeight = pattern.length;
        const patternWidth = pattern[0].length;

        // Place pattern on grid
        for (let py = 0; py < patternHeight; py++) {
            for (let px = 0; px < patternWidth; px++) {
                const gridX = x + px - Math.floor(patternWidth / 2);
                const gridY = y + py - Math.floor(patternHeight / 2);

                if (gridX >= 0 && gridX < this.leniaGrid[0].length &&
                    gridY >= 0 && gridY < this.leniaGrid.length) {
                    this.leniaGrid[gridY][gridX] = Math.max(
                        this.leniaGrid[gridY][gridX],
                        pattern[py][px]
                    );
                }
            }
        }

        console.log(`🧬 Spawned ${species.name} at (${x}, ${y})`);
    }

    // Update Lenia system (main simulation step)
    updateLeniaSystem(deltaTime) {
        if (!this.leniaEnabled || !this.leniaGrid) return;

        this.leniaUpdateCounter += deltaTime * this.leniaAnimationSpeed;

        // Update at specified time step
        if (this.leniaUpdateCounter >= this.leniaTimeStep) {
            this.leniaUpdateCounter = 0;

            const width = this.leniaGrid[0].length;
            const height = this.leniaGrid.length;
            const newGrid = Array(height).fill().map(() => Array(width).fill(0));

            // Apply Lenia update rule
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const neighborhood = this.calculateNeighborhood(x, y);
                    const growth = this.leniaGrowthFunction.calculate(neighborhood);

                    // Update cell value
                    const currentValue = this.leniaGrid[y][x];
                    const newValue = Math.max(0, Math.min(1, currentValue + growth * this.leniaTimeStep));

                    newGrid[y][x] = newValue;
                }
            }

            this.leniaGrid = newGrid;
        }
    }

    // Calculate neighborhood value using convolution
    calculateNeighborhood(centerX, centerY) {
        const R = this.leniaRadius;
        const width = this.leniaGrid[0].length;
        const height = this.leniaGrid.length;
        let sum = 0;

        for (let dy = -R; dy <= R; dy++) {
            for (let dx = -R; dx <= R; dx++) {
                const x = centerX + dx;
                const y = centerY + dy;

                // Handle boundaries with wrapping
                const wrappedX = ((x % width) + width) % width;
                const wrappedY = ((y % height) + height) % height;

                const kernelX = dx + R;
                const kernelY = dy + R;

                if (kernelX >= 0 && kernelX < this.leniaKernel[0].length &&
                    kernelY >= 0 && kernelY < this.leniaKernel.length) {
                    sum += this.leniaGrid[wrappedY][wrappedX] * this.leniaKernel[kernelY][kernelX];
                }
            }
        }

        return sum;
    }

    // Render Lenia organisms
    renderLeniaSystem(ctx) {
        if (!this.leniaEnabled || !this.leniaGrid) return;

        ctx.save();

        const width = this.leniaGrid[0].length;
        const height = this.leniaGrid.length;
        const cellWidth = this.terrainEngine.cellWidth || 8;
        const cellHeight = this.terrainEngine.cellHeight || 8;

        // Render each cell
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const value = this.leniaGrid[y][x];

                if (value > 0.01) { // Only render visible cells
                    const screenX = x * cellWidth;
                    const screenY = y * cellHeight;

                    // Color based on organism density
                    const alpha = Math.min(1, value);
                    const hue = (value * 360 + Date.now() * 0.001) % 360; // Slowly changing colors

                    ctx.fillStyle = `hsla(${hue}, 70%, 60%, ${alpha * 0.7})`;
                    ctx.fillRect(screenX, screenY, cellWidth, cellHeight);

                    // Add glow effect for high-density areas
                    if (value > 0.5) {
                        ctx.shadowColor = ctx.fillStyle;
                        ctx.shadowBlur = 5;
                        ctx.fillRect(screenX, screenY, cellWidth, cellHeight);
                        ctx.shadowBlur = 0;
                    }
                }
            }
        }

        ctx.restore();
    }

    // Enable/disable Lenia system
    setLeniaEnabled(enabled) {
        this.leniaEnabled = enabled;
        console.log(`🧬 Lenia artificial life ${enabled ? 'enabled' : 'disabled'}`);
    }

    // Set Lenia animation speed
    setLeniaSpeed(speed) {
        this.leniaAnimationSpeed = Math.max(0.1, Math.min(5.0, speed));
        console.log(`🧬 Lenia speed set to ${this.leniaAnimationSpeed}x`);
    }

    // Spawn organism at mouse position
    spawnOrganismAt(screenX, screenY, speciesName = 'orbium') {
        if (!this.leniaEnabled) return;

        const cellWidth = this.terrainEngine.cellWidth || 8;
        const cellHeight = this.terrainEngine.cellHeight || 8;

        const gridX = Math.floor(screenX / cellWidth);
        const gridY = Math.floor(screenY / cellHeight);

        this.spawnOrganism(gridX, gridY, speciesName);
    }

    // Clear all organisms
    clearLeniaOrganisms() {
        if (!this.leniaGrid) return;

        for (let y = 0; y < this.leniaGrid.length; y++) {
            for (let x = 0; x < this.leniaGrid[0].length; x++) {
                this.leniaGrid[y][x] = 0;
            }
        }

        console.log('🧹 All Lenia organisms cleared');
    }

    // Get Lenia statistics
    getLeniaStats() {
        if (!this.leniaGrid) return { totalMass: 0, organisms: 0 };

        let totalMass = 0;
        let organisms = 0;

        for (let y = 0; y < this.leniaGrid.length; y++) {
            for (let x = 0; x < this.leniaGrid[0].length; x++) {
                const value = this.leniaGrid[y][x];
                totalMass += value;
                if (value > 0.1) organisms++;
            }
        }

        return {
            totalMass: totalMass.toFixed(2),
            organisms: organisms,
            species: this.leniaSpecies.size
        };
    }

    // ===== WEBGL FLUID SIMULATION SYSTEM =====

    // Initialize WebGL fluid simulation
    initializeWebGLFluid() {
        try {
            console.log('🌊 Initializing WebGL fluid simulation...');

            // Create fluid canvas overlay
            this.fluidCanvas = document.createElement('canvas');
            this.fluidCanvas.style.position = 'absolute';
            this.fluidCanvas.style.top = '0';
            this.fluidCanvas.style.left = '0';
            this.fluidCanvas.style.width = '100%';
            this.fluidCanvas.style.height = '100%';
            this.fluidCanvas.style.pointerEvents = 'none';
            this.fluidCanvas.style.zIndex = '2';
            this.fluidCanvas.style.opacity = '0.7';

            // Get WebGL context
            this.fluidGL = this.fluidCanvas.getContext('webgl2') || this.fluidCanvas.getContext('webgl');

            if (!this.fluidGL) {
                console.warn('⚠️ WebGL not supported for fluid simulation');
                this.fluidEnabled = false;
                return;
            }

            // Initialize WebGL fluid simulation
            this.initFluidShaders();
            this.initFluidFramebuffers();
            this.resizeFluidCanvas();

            // Add to DOM
            if (this.terrainEngine && this.terrainEngine.canvas && this.terrainEngine.canvas.parentNode) {
                this.terrainEngine.canvas.parentNode.appendChild(this.fluidCanvas);
            }

            console.log('✅ WebGL fluid simulation initialized');

        } catch (error) {
            console.error('❌ Failed to initialize WebGL fluid simulation:', error);
            this.fluidEnabled = false;
        }
    }

    // Initialize fluid shaders
    initFluidShaders() {
        // Vertex shader for fluid simulation
        const vertexShader = `
            precision highp float;
            attribute vec2 aPosition;
            varying vec2 vUv;
            varying vec2 vL;
            varying vec2 vR;
            varying vec2 vT;
            varying vec2 vB;
            uniform vec2 texelSize;

            void main () {
                vUv = aPosition * 0.5 + 0.5;
                vL = vUv - vec2(texelSize.x, 0.0);
                vR = vUv + vec2(texelSize.x, 0.0);
                vT = vUv + vec2(0.0, texelSize.y);
                vB = vUv - vec2(0.0, texelSize.y);
                gl_Position = vec4(aPosition, 0.0, 1.0);
            }
        `;

        // Fragment shader for fluid advection
        const advectionShader = `
            precision mediump float;
            precision mediump sampler2D;
            varying highp vec2 vUv;
            uniform sampler2D uVelocity;
            uniform sampler2D uSource;
            uniform vec2 texelSize;
            uniform vec2 dyeTexelSize;
            uniform float dt;
            uniform float dissipation;

            vec4 bilerp (sampler2D sam, vec2 uv, vec2 tsize) {
                vec2 st = uv / tsize - 0.5;
                vec2 iuv = floor(st);
                vec2 fuv = fract(st);
                vec4 a = texture2D(sam, (iuv + vec2(0.5, 0.5)) * tsize);
                vec4 b = texture2D(sam, (iuv + vec2(1.5, 0.5)) * tsize);
                vec4 c = texture2D(sam, (iuv + vec2(0.5, 1.5)) * tsize);
                vec4 d = texture2D(sam, (iuv + vec2(1.5, 1.5)) * tsize);
                return mix(mix(a, b, fuv.x), mix(c, d, fuv.x), fuv.y);
            }

            void main () {
                vec2 coord = vUv - dt * bilerp(uVelocity, vUv, texelSize).xy * texelSize;
                gl_FragColor = dissipation * bilerp(uSource, coord, dyeTexelSize);
                gl_FragColor.a = 1.0;
            }
        `;

        // Fragment shader for divergence calculation
        const divergenceShader = `
            precision mediump float;
            precision mediump sampler2D;
            varying highp vec2 vUv;
            varying highp vec2 vL;
            varying highp vec2 vR;
            varying highp vec2 vT;
            varying highp vec2 vB;
            uniform sampler2D uVelocity;

            void main () {
                float L = texture2D(uVelocity, vL).x;
                float R = texture2D(uVelocity, vR).x;
                float T = texture2D(uVelocity, vT).y;
                float B = texture2D(uVelocity, vB).y;
                vec2 C = texture2D(uVelocity, vUv).xy;
                if (vL.x < 0.0) { L = -C.x; }
                if (vR.x > 1.0) { R = -C.x; }
                if (vT.y > 1.0) { T = -C.y; }
                if (vB.y < 0.0) { B = -C.y; }
                float div = 0.5 * (R - L + T - B);
                gl_FragColor = vec4(div, 0.0, 0.0, 1.0);
            }
        `;

        // Create shader programs
        this.fluidPrograms.advection = this.createFluidProgram(vertexShader, advectionShader);
        this.fluidPrograms.divergence = this.createFluidProgram(vertexShader, divergenceShader);

        console.log('✅ Fluid shaders initialized');
    }

    // Create WebGL program
    createFluidProgram(vertexSource, fragmentSource) {
        const gl = this.fluidGL;

        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertexShader, vertexSource);
        gl.compileShader(vertexShader);

        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragmentShader, fragmentSource);
        gl.compileShader(fragmentShader);

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        return program;
    }

    // Initialize fluid framebuffers
    initFluidFramebuffers() {
        const gl = this.fluidGL;

        // Create velocity framebuffer
        this.fluidFramebuffers.velocity = this.createFluidFramebuffer(this.fluidConfig.SIM_RESOLUTION);

        // Create density framebuffer
        this.fluidFramebuffers.density = this.createFluidFramebuffer(this.fluidConfig.DYE_RESOLUTION);

        console.log('✅ Fluid framebuffers initialized');
    }

    // Create framebuffer
    createFluidFramebuffer(resolution) {
        const gl = this.fluidGL;

        const texture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, resolution, resolution, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);

        const framebuffer = gl.createFramebuffer();
        gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);

        return { framebuffer, texture, resolution };
    }

    // Resize fluid canvas
    resizeFluidCanvas() {
        if (!this.fluidCanvas || !this.terrainEngine) return;

        const canvas = this.terrainEngine.canvas;
        this.fluidCanvas.width = canvas.width;
        this.fluidCanvas.height = canvas.height;

        if (this.fluidGL) {
            this.fluidGL.viewport(0, 0, this.fluidCanvas.width, this.fluidCanvas.height);
        }
    }
}

// Export for use in other modules
window.PhysicsEngine = PhysicsEngine;
