/**
 * Physics Engine for AR Sandbox Pro
 * Handles water flow simulation, particle systems, gravity effects, and realistic material interactions
 */

class PhysicsEngine {
    constructor(core) {
        this.core = core;
        this.particles = [];
        this.waterParticles = [];
        this.maxParticles = 2000;
        this.gravity = 9.81;
        this.canvas = null;
        this.ctx = null;
        
        // Physics simulation parameters
        this.timeStep = 1/60;
        this.damping = 0.98;
        this.restitution = 0.3;
        
        // Water simulation
        this.waterGrid = null;
        this.waterVelocityX = null;
        this.waterVelocityY = null;
        this.waterPressure = null;
        
        // Particle systems
        this.particleSystems = {
            rain: { active: false, intensity: 0.5 },
            snow: { active: false, intensity: 0.3 },
            dust: { active: false, intensity: 0.2 },
            steam: { active: false, intensity: 0.4 }
        };
    }
    
    async initialize() {
        console.log('⚡ Initializing Physics Engine...');
        
        // Create physics canvas overlay
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'physics-canvas';
        this.canvas.width = 800;
        this.canvas.height = 600;
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.zIndex = '15';
        this.canvas.style.pointerEvents = 'none';
        document.body.appendChild(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        
        // Initialize water simulation grid
        this.initializeWaterSimulation();
        
        // Initialize particle systems
        this.initializeParticleSystems();
        
        console.log('✅ Physics Engine initialized');
    }
    
    initializeWaterSimulation() {
        const width = 200;
        const height = 150;
        
        this.waterGrid = new Float32Array(width * height);
        this.waterVelocityX = new Float32Array(width * height);
        this.waterVelocityY = new Float32Array(width * height);
        this.waterPressure = new Float32Array(width * height);
        
        this.waterSimulation = {
            width: width,
            height: height,
            cellSize: 4,
            viscosity: 0.001,
            density: 1000,
            surfaceTension: 0.0728
        };
    }
    
    initializeParticleSystems() {
        // Initialize particle pools for efficiency
        for (let i = 0; i < this.maxParticles; i++) {
            this.particles.push({
                x: 0, y: 0, z: 0,
                vx: 0, vy: 0, vz: 0,
                life: 0, maxLife: 1,
                size: 1, color: [255, 255, 255, 1],
                type: 'dust',
                active: false
            });
        }
    }
    
    update(deltaTime) {
        // Update water simulation
        this.updateWaterSimulation(deltaTime);
        
        // Update particle systems
        this.updateParticles(deltaTime);
        
        // Update environmental effects
        this.updateEnvironmentalEffects(deltaTime);
        
        // Handle collisions
        this.handleCollisions();
    }
    
    updateWaterSimulation(deltaTime) {
        if (!this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        const width = this.waterSimulation.width;
        const height = this.waterSimulation.height;
        
        // Apply external forces (gravity, terrain slope)
        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                const index = y * width + x;
                
                // Get terrain height at this position
                const terrainX = Math.floor(x * terrain.width / width);
                const terrainY = Math.floor(y * terrain.height / height);
                const terrainIndex = terrainY * terrain.width + terrainX;
                
                if (terrainIndex >= 0 && terrainIndex < terrain.heightMap.length) {
                    const terrainHeight = terrain.heightMap[terrainIndex];
                    const waterLevel = terrain.waterMap[terrainIndex];
                    
                    // Calculate pressure gradient
                    const leftHeight = terrain.heightMap[terrainIndex - 1] || terrainHeight;
                    const rightHeight = terrain.heightMap[terrainIndex + 1] || terrainHeight;
                    const topHeight = terrain.heightMap[terrainIndex - terrain.width] || terrainHeight;
                    const bottomHeight = terrain.heightMap[terrainIndex + terrain.width] || terrainHeight;
                    
                    const gradientX = (rightHeight - leftHeight) * 0.5;
                    const gradientY = (bottomHeight - topHeight) * 0.5;
                    
                    // Apply gravity and terrain forces
                    this.waterVelocityX[index] += -gradientX * this.gravity * deltaTime;
                    this.waterVelocityY[index] += -gradientY * this.gravity * deltaTime;
                    
                    // Apply damping
                    this.waterVelocityX[index] *= this.damping;
                    this.waterVelocityY[index] *= this.damping;
                    
                    // Update water position
                    this.waterGrid[index] = waterLevel;
                }
            }
        }
        
        // Create water particles for visualization
        this.createWaterParticles();
    }
    
    createWaterParticles() {
        if (!this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        
        // Sample water areas and create particles
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * terrain.width;
            const y = Math.random() * terrain.height;
            const index = Math.floor(y) * terrain.width + Math.floor(x);
            
            if (index >= 0 && index < terrain.waterMap.length && terrain.waterMap[index] > 0.1) {
                this.spawnParticle({
                    x: x * 4,
                    y: y * 4,
                    z: terrain.heightMap[index] * 100,
                    vx: (Math.random() - 0.5) * 20,
                    vy: (Math.random() - 0.5) * 20,
                    vz: Math.random() * 10,
                    type: 'water',
                    life: 2.0,
                    size: 2 + Math.random() * 3,
                    color: [100, 150, 255, 0.8]
                });
            }
        }
    }
    
    updateParticles(deltaTime) {
        for (let particle of this.particles) {
            if (!particle.active) continue;
            
            // Update physics
            particle.vy += this.gravity * deltaTime * 10; // Scale gravity for visual effect
            
            particle.x += particle.vx * deltaTime;
            particle.y += particle.vy * deltaTime;
            particle.z += particle.vz * deltaTime;
            
            // Apply damping
            particle.vx *= this.damping;
            particle.vy *= this.damping;
            particle.vz *= this.damping;
            
            // Update life
            particle.life -= deltaTime;
            if (particle.life <= 0) {
                particle.active = false;
                continue;
            }
            
            // Terrain collision
            if (this.core.terrainEngine) {
                const terrainX = Math.floor(particle.x / 4);
                const terrainY = Math.floor(particle.y / 4);
                
                if (terrainX >= 0 && terrainX < this.core.terrainEngine.width &&
                    terrainY >= 0 && terrainY < this.core.terrainEngine.height) {
                    
                    const terrainIndex = terrainY * this.core.terrainEngine.width + terrainX;
                    const terrainHeight = this.core.terrainEngine.heightMap[terrainIndex] * 100;
                    
                    if (particle.z <= terrainHeight) {
                        particle.z = terrainHeight;
                        particle.vz = -particle.vz * this.restitution;
                        particle.vx *= 0.8;
                        particle.vy *= 0.8;
                        
                        // Create splash effect for water particles
                        if (particle.type === 'water') {
                            this.createSplashEffect(particle.x, particle.y, particle.z);
                        }
                    }
                }
            }
            
            // Boundary collision
            if (particle.x < 0 || particle.x > this.canvas.width ||
                particle.y < 0 || particle.y > this.canvas.height) {
                particle.active = false;
            }
            
            // Update visual properties
            const lifeRatio = particle.life / particle.maxLife;
            particle.color[3] = lifeRatio * 0.8;
            
            if (particle.type === 'steam') {
                particle.size += deltaTime * 5;
                particle.vz += deltaTime * 20; // Steam rises
            }
        }
    }
    
    createSplashEffect(x, y, z) {
        for (let i = 0; i < 5; i++) {
            this.spawnParticle({
                x: x + (Math.random() - 0.5) * 10,
                y: y + (Math.random() - 0.5) * 10,
                z: z + Math.random() * 20,
                vx: (Math.random() - 0.5) * 50,
                vy: (Math.random() - 0.5) * 50,
                vz: Math.random() * 30 + 10,
                type: 'splash',
                life: 0.5,
                size: 1 + Math.random() * 2,
                color: [150, 200, 255, 0.6]
            });
        }
    }
    
    updateEnvironmentalEffects(deltaTime) {
        // Rain effect
        if (this.particleSystems.rain.active) {
            for (let i = 0; i < this.particleSystems.rain.intensity * 10; i++) {
                this.spawnParticle({
                    x: Math.random() * this.canvas.width,
                    y: -10,
                    z: 200 + Math.random() * 100,
                    vx: (Math.random() - 0.5) * 20,
                    vy: 100 + Math.random() * 50,
                    vz: 0,
                    type: 'rain',
                    life: 3.0,
                    size: 1,
                    color: [100, 150, 255, 0.7]
                });
            }
        }
        
        // Snow effect
        if (this.particleSystems.snow.active) {
            for (let i = 0; i < this.particleSystems.snow.intensity * 5; i++) {
                this.spawnParticle({
                    x: Math.random() * this.canvas.width,
                    y: -10,
                    z: 200 + Math.random() * 100,
                    vx: (Math.random() - 0.5) * 10,
                    vy: 20 + Math.random() * 30,
                    vz: 0,
                    type: 'snow',
                    life: 5.0,
                    size: 2 + Math.random() * 3,
                    color: [255, 255, 255, 0.8]
                });
            }
        }
        
        // Dust effect
        if (this.particleSystems.dust.active) {
            for (let i = 0; i < this.particleSystems.dust.intensity * 3; i++) {
                this.spawnParticle({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    z: Math.random() * 50,
                    vx: (Math.random() - 0.5) * 5,
                    vy: (Math.random() - 0.5) * 5,
                    vz: Math.random() * 10,
                    type: 'dust',
                    life: 4.0,
                    size: 1 + Math.random(),
                    color: [139, 119, 101, 0.3]
                });
            }
        }
    }
    
    spawnParticle(config) {
        // Find inactive particle
        for (let particle of this.particles) {
            if (!particle.active) {
                particle.x = config.x;
                particle.y = config.y;
                particle.z = config.z || 0;
                particle.vx = config.vx || 0;
                particle.vy = config.vy || 0;
                particle.vz = config.vz || 0;
                particle.life = config.life || 1;
                particle.maxLife = particle.life;
                particle.size = config.size || 1;
                particle.color = [...config.color];
                particle.type = config.type || 'dust';
                particle.active = true;
                break;
            }
        }
    }
    
    handleCollisions() {
        // Handle particle-particle collisions for clustering effects
        for (let i = 0; i < this.particles.length; i++) {
            if (!this.particles[i].active) continue;
            
            for (let j = i + 1; j < this.particles.length; j++) {
                if (!this.particles[j].active) continue;
                
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const dz = this.particles[i].z - this.particles[j].z;
                const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
                
                const minDistance = this.particles[i].size + this.particles[j].size;
                
                if (distance < minDistance && distance > 0) {
                    // Simple elastic collision
                    const overlap = minDistance - distance;
                    const separationX = (dx / distance) * overlap * 0.5;
                    const separationY = (dy / distance) * overlap * 0.5;
                    const separationZ = (dz / distance) * overlap * 0.5;
                    
                    this.particles[i].x += separationX;
                    this.particles[i].y += separationY;
                    this.particles[i].z += separationZ;
                    
                    this.particles[j].x -= separationX;
                    this.particles[j].y -= separationY;
                    this.particles[j].z -= separationZ;
                    
                    // Exchange velocities (simplified)
                    const tempVx = this.particles[i].vx;
                    const tempVy = this.particles[i].vy;
                    const tempVz = this.particles[i].vz;
                    
                    this.particles[i].vx = this.particles[j].vx * this.restitution;
                    this.particles[i].vy = this.particles[j].vy * this.restitution;
                    this.particles[i].vz = this.particles[j].vz * this.restitution;
                    
                    this.particles[j].vx = tempVx * this.restitution;
                    this.particles[j].vy = tempVy * this.restitution;
                    this.particles[j].vz = tempVz * this.restitution;
                }
            }
        }
    }
    
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Sort particles by z-depth for proper rendering
        const activeParticles = this.particles.filter(p => p.active);
        activeParticles.sort((a, b) => b.z - a.z);
        
        // Render particles
        for (let particle of activeParticles) {
            this.ctx.save();
            
            // Set particle color and alpha
            const [r, g, b, a] = particle.color;
            this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a})`;
            this.ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${a * 0.5})`;
            
            // Apply 3D perspective (simple)
            const perspective = 1 - (particle.z / 300);
            const size = particle.size * Math.max(0.1, perspective);
            
            // Draw particle based on type
            switch (particle.type) {
                case 'water':
                case 'splash':
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, size, 0, Math.PI * 2);
                    this.ctx.fill();
                    break;
                    
                case 'rain':
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(particle.x + particle.vx * 0.1, particle.y + particle.vy * 0.1);
                    this.ctx.lineWidth = size;
                    this.ctx.stroke();
                    break;
                    
                case 'snow':
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, size, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${a * 0.3})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                    break;
                    
                case 'dust':
                case 'steam':
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, size, 0, Math.PI * 2);
                    this.ctx.fill();
                    break;
            }
            
            this.ctx.restore();
        }
    }
    
    // Public methods for controlling particle systems
    startRain(intensity = 0.5) {
        this.particleSystems.rain.active = true;
        this.particleSystems.rain.intensity = intensity;
    }
    
    stopRain() {
        this.particleSystems.rain.active = false;
    }
    
    startSnow(intensity = 0.3) {
        this.particleSystems.snow.active = true;
        this.particleSystems.snow.intensity = intensity;
    }
    
    stopSnow() {
        this.particleSystems.snow.active = false;
    }
    
    startDust(intensity = 0.2) {
        this.particleSystems.dust.active = true;
        this.particleSystems.dust.intensity = intensity;
    }
    
    stopDust() {
        this.particleSystems.dust.active = false;
    }
    
    createExplosion(x, y, z, intensity = 1) {
        for (let i = 0; i < intensity * 20; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 50 + Math.random() * 100;
            
            this.spawnParticle({
                x: x,
                y: y,
                z: z,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                vz: Math.random() * 50 + 25,
                type: 'dust',
                life: 1.0 + Math.random(),
                size: 2 + Math.random() * 4,
                color: [255, 100 + Math.random() * 100, 0, 0.8]
            });
        }
    }
}
