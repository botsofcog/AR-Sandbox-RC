/**
 * Vehicle Fleet System - Complete K'NEX vehicle fleet with AI behaviors
 * Enhanced with Cannon.js physics for realistic RC construction equipment
 * Enhanced with Swarm Intelligence for coordinated multi-vehicle construction
 * Enhanced with Synaptic.js neural networks for advanced AI decision making
 * Part of the RC Sandbox modular architecture
 */

class Vehicle {
    constructor(id, type, x, y) {
        this.id = id;
        this.type = type;
        this.x = x;
        this.y = y;
        this.targetX = x;
        this.targetY = y;
        this.rotation = 0;
        this.speed = this.getTypeSpeed();
        this.power = this.getTypePower();
        this.cost = this.getTypeCost();
        this.batteryLevel = 100;
        this.attachmentState = 'idle';
        this.taskStatus = 'idle';
        this.currentTask = null;
        this.workProgress = 0;
        this.lastUpdate = Date.now();
        
        // AI behavior parameters
        this.aiEnabled = true;
        this.decisionCooldown = 0;
        this.workEfficiency = this.getTypeEfficiency();
        this.pathfinding = [];
        this.stuckCounter = 0;

        // Cannon.js physics properties
        this.physicsBody = null;
        this.physicsWorld = null;
        this.wheelBodies = [];
        this.wheelConstraints = [];
        this.engineForce = 0;
        this.brakeForce = 0;
        this.steeringValue = 0;
        this.maxSteerVal = 0.5;
        this.maxForce = 1000;
        this.maxBrakeForce = 1000000;

        // Swarm Intelligence properties
        this.swarmEnabled = true;
        this.velocity = { x: 0, y: 0 };
        this.direction = { x: 1, y: 0 };
        this.maxSpeed = this.getTypeMaxSpeed();
        this.acceleration = 0.1;
        this.neighborRadius = 50;
        this.separationRadius = 20;
        this.alignmentWeight = 1.0;
        this.cohesionWeight = 1.0;
        this.separationWeight = 2.0;
        this.seekWeight = 3.0;
        this.wanderAngle = Math.random() * Math.PI * 2;
        this.wanderWeight = 0.5;
        this.avoidanceWeight = 4.0;

        // Neural Network Decision Making (Synaptic.js)
        this.neuralNetwork = null;
        this.neuralNetworkEnabled = true;
        this.decisionInputs = [];
        this.lastDecision = null;
        this.learningRate = 0.1;
        this.trainingData = [];
        this.decisionHistory = [];

        // Three.js Projects Integration (Car Physics, Realistic Environments)
        this.threeJsPhysics = null;
        this.carPhysicsEnabled = true;
        this.environmentEffects = new Map();

        // IsoCity Building Integration
        this.isoCityEnabled = true;
        this.isometricView = null;
        this.cityBlocks = new Map();
        this.constructionSites = [];

        // Enhanced Voxel Engine Integration
        this.voxelEngineEnabled = true;
        this.voxelChunks = new Map();
        this.voxelMeshes = new Map();

        // Sand.js Advanced Physics
        this.sandPhysicsEnabled = true;
        this.sandParticles = [];
        this.sandSimulation = null;

        // Raycast Vehicle Engine
        this.raycastVehicle = null;
        this.vehiclePhysics = null;
        this.enhancedPhysicsEnabled = true;

        console.log(`🚛 ${this.id} (${this.type}) initialized`);
    }
    
    getTypeSpeed() {
        const speeds = {
            excavator: 2.0,
            bulldozer: 2.5,
            dump_truck: 3.5,
            crane: 1.5,
            compactor: 2.0
        };
        return speeds[this.type] || 2.0;
    }
    
    getTypePower() {
        const powers = {
            excavator: 90,
            bulldozer: 80,
            dump_truck: 60,
            crane: 95,
            compactor: 70
        };
        return powers[this.type] || 70;
    }
    
    getTypeCost() {
        const costs = {
            excavator: 250,
            bulldozer: 200,
            dump_truck: 150,
            crane: 350,
            compactor: 180
        };
        return costs[this.type] || 200;
    }
    
    getTypeEfficiency() {
        const efficiencies = {
            excavator: 0.9,  // Excellent at digging
            bulldozer: 0.8,  // Good at pushing/leveling
            dump_truck: 0.6, // Moderate at terrain work
            crane: 0.95,     // Excellent at precision work
            compactor: 0.75  // Good at smoothing
        };
        return efficiencies[this.type] || 0.7;
    }
    
    getSpecialty() {
        const specialties = {
            excavator: 'Deep excavation and terrain modification',
            bulldozer: 'Terrain shaping and material pushing',
            dump_truck: 'Material transport and delivery',
            crane: 'Precision placement and heavy lifting',
            compactor: 'Surface finishing and compaction'
        };
        return specialties[this.type] || 'General construction work';
    }

    // Initialize Cannon.js physics for realistic vehicle simulation
    initPhysics(world) {
        if (!world || typeof CANNON === 'undefined') {
            console.warn(`⚠️ ${this.id}: Cannon.js not available, using fallback physics`);
            return false;
        }

        try {
            console.log(`🔧 ${this.id}: Initializing Cannon.js physics...`);

            this.physicsWorld = world;

            // Create vehicle chassis body
            const chassisShape = new CANNON.Box(new CANNON.Vec3(2, 0.5, 4));
            this.physicsBody = new CANNON.Body({ mass: this.getTypeMass() });
            this.physicsBody.addShape(chassisShape);
            this.physicsBody.position.set(this.x, this.y + 1, 0);
            this.physicsBody.material = new CANNON.Material('chassis');

            // Add chassis to world
            world.addBody(this.physicsBody);

            // Create wheels
            this.createWheels(world);

            // Create vehicle constraints
            this.createVehicleConstraints(world);

            console.log(`✅ ${this.id}: Physics initialized successfully`);
            return true;

        } catch (error) {
            console.error(`❌ ${this.id}: Physics initialization failed:`, error);
            return false;
        }
    }

    // Get vehicle mass based on type
    getTypeMass() {
        const masses = {
            excavator: 15000,    // 15 tons
            bulldozer: 20000,    // 20 tons
            dump_truck: 12000,   // 12 tons
            crane: 25000,        // 25 tons
            compactor: 10000     // 10 tons
        };
        return masses[this.type] || 15000;
    }

    // Get vehicle max speed based on type
    getTypeMaxSpeed() {
        const speeds = {
            excavator: 3.0,      // Slow but powerful
            bulldozer: 4.0,      // Moderate speed
            dump_truck: 6.0,     // Fast for transport
            crane: 2.0,          // Very slow, precise
            compactor: 3.5       // Moderate speed
        };
        return speeds[this.type] || 4.0;
    }

    // Create realistic wheels for the vehicle
    createWheels(world) {
        const wheelShape = new CANNON.Sphere(0.5);
        const wheelMaterial = new CANNON.Material('wheel');
        wheelMaterial.friction = 0.4;
        wheelMaterial.restitution = 0.3;

        // Wheel positions relative to chassis
        const wheelPositions = [
            new CANNON.Vec3(-1.5, -0.5, 1.8),  // Front left
            new CANNON.Vec3(1.5, -0.5, 1.8),   // Front right
            new CANNON.Vec3(-1.5, -0.5, -1.8), // Rear left
            new CANNON.Vec3(1.5, -0.5, -1.8)   // Rear right
        ];

        this.wheelBodies = [];

        for (let i = 0; i < wheelPositions.length; i++) {
            const wheelBody = new CANNON.Body({ mass: 100 });
            wheelBody.addShape(wheelShape);
            wheelBody.material = wheelMaterial;

            // Position wheel relative to chassis
            const worldPos = this.physicsBody.position.vadd(wheelPositions[i]);
            wheelBody.position.copy(worldPos);

            world.addBody(wheelBody);
            this.wheelBodies.push(wheelBody);
        }
    }

    // Create vehicle constraints (suspension, steering)
    createVehicleConstraints(world) {
        this.wheelConstraints = [];

        for (let i = 0; i < this.wheelBodies.length; i++) {
            const wheelBody = this.wheelBodies[i];

            // Create point-to-point constraint (simple suspension)
            const constraint = new CANNON.PointToPointConstraint(
                this.physicsBody,
                new CANNON.Vec3(-1.5 + (i % 2) * 3, -0.5, 1.8 - Math.floor(i / 2) * 3.6),
                wheelBody,
                new CANNON.Vec3(0, 0, 0)
            );

            world.addConstraint(constraint);
            this.wheelConstraints.push(constraint);
        }
    }

    // Apply physics forces for movement
    applyPhysicsForces() {
        if (!this.physicsBody || !this.wheelBodies.length) return;

        // Apply engine force to rear wheels
        const rearWheels = [this.wheelBodies[2], this.wheelBodies[3]]; // Rear left, rear right

        for (const wheel of rearWheels) {
            // Forward/backward force
            const forceDirection = new CANNON.Vec3(0, 0, this.engineForce);
            wheel.applyLocalForce(forceDirection, new CANNON.Vec3(0, 0, 0));

            // Brake force
            if (this.brakeForce > 0) {
                const velocity = wheel.velocity;
                const brakeDirection = velocity.clone().scale(-this.brakeForce);
                wheel.applyForce(brakeDirection, wheel.position);
            }
        }

        // Apply steering to front wheels
        const frontWheels = [this.wheelBodies[0], this.wheelBodies[1]]; // Front left, front right

        for (const wheel of frontWheels) {
            // Steering force
            const steerDirection = new CANNON.Vec3(this.steeringValue * 500, 0, 0);
            wheel.applyLocalForce(steerDirection, new CANNON.Vec3(0, 0, 0));
        }
    }

    // Update physics-based movement
    updatePhysicsMovement(deltaTime) {
        if (!this.physicsBody) return;

        // Sync position from physics body
        this.x = this.physicsBody.position.x;
        this.y = this.physicsBody.position.z; // Note: Cannon.js uses Y-up, we use Z-up

        // Update rotation from physics
        this.rotation = this.physicsBody.quaternion.toAxisAngle()[1];

        // Apply AI movement forces
        if (this.taskStatus === 'moving') {
            this.calculatePhysicsMovement();
        } else {
            // Idle - apply brakes
            this.engineForce = 0;
            this.brakeForce = this.maxBrakeForce * 0.1;
            this.steeringValue = 0;
        }

        // Apply forces to physics bodies
        this.applyPhysicsForces();
    }

    // Calculate movement forces based on AI target
    calculatePhysicsMovement() {
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 5) {
            // Close to target - stop
            this.engineForce = 0;
            this.brakeForce = this.maxBrakeForce * 0.5;
            this.steeringValue = 0;
            this.taskStatus = 'idle';
            return;
        }

        // Calculate desired direction
        const targetAngle = Math.atan2(dy, dx);
        const angleDiff = targetAngle - this.rotation;

        // Normalize angle difference
        let normalizedAngle = angleDiff;
        while (normalizedAngle > Math.PI) normalizedAngle -= 2 * Math.PI;
        while (normalizedAngle < -Math.PI) normalizedAngle += 2 * Math.PI;

        // Apply steering
        this.steeringValue = Math.max(-this.maxSteerVal, Math.min(this.maxSteerVal, normalizedAngle * 2));

        // Apply engine force
        this.engineForce = this.maxForce * 0.3; // 30% power for smooth movement
        this.brakeForce = 0;
    }

    // ===== SWARM INTELLIGENCE ALGORITHMS =====

    // Update swarm behavior with neighboring vehicles
    updateSwarmBehavior(neighbors, obstacles = []) {
        if (!this.swarmEnabled || this.taskStatus === 'working') return;

        try {
            // Calculate flocking forces
            const alignment = this.calculateAlignment(neighbors);
            const cohesion = this.calculateCohesion(neighbors);
            const separation = this.calculateSeparation(neighbors);
            const seek = this.calculateSeek();
            const wander = this.calculateWander();
            const avoidance = this.calculateObstacleAvoidance(obstacles);

            // Combine forces with weights
            const totalForce = {
                x: (alignment.x * this.alignmentWeight +
                    cohesion.x * this.cohesionWeight +
                    separation.x * this.separationWeight +
                    seek.x * this.seekWeight +
                    wander.x * this.wanderWeight +
                    avoidance.x * this.avoidanceWeight),
                y: (alignment.y * this.alignmentWeight +
                    cohesion.y * this.cohesionWeight +
                    separation.y * this.separationWeight +
                    seek.y * this.seekWeight +
                    wander.y * this.wanderWeight +
                    avoidance.y * this.avoidanceWeight)
            };

            // Apply force to velocity
            this.velocity.x += totalForce.x * this.acceleration;
            this.velocity.y += totalForce.y * this.acceleration;

            // Limit velocity
            const speed = Math.sqrt(this.velocity.x * this.velocity.x + this.velocity.y * this.velocity.y);
            if (speed > this.maxSpeed) {
                this.velocity.x = (this.velocity.x / speed) * this.maxSpeed;
                this.velocity.y = (this.velocity.y / speed) * this.maxSpeed;
            }

            // Update direction
            if (speed > 0.1) {
                this.direction.x = this.velocity.x / speed;
                this.direction.y = this.velocity.y / speed;
                this.rotation = Math.atan2(this.direction.y, this.direction.x);
            }

            // Update position
            this.x += this.velocity.x;
            this.y += this.velocity.y;

        } catch (error) {
            console.error(`Swarm behavior error for ${this.id}:`, error);
        }
    }

    // Calculate alignment force (steer towards average heading of neighbors)
    calculateAlignment(neighbors) {
        if (neighbors.length === 0) return { x: 0, y: 0 };

        let avgDirection = { x: 0, y: 0 };

        for (const neighbor of neighbors) {
            avgDirection.x += neighbor.direction.x;
            avgDirection.y += neighbor.direction.y;
        }

        avgDirection.x /= neighbors.length;
        avgDirection.y /= neighbors.length;

        // Normalize
        const magnitude = Math.sqrt(avgDirection.x * avgDirection.x + avgDirection.y * avgDirection.y);
        if (magnitude > 0) {
            avgDirection.x /= magnitude;
            avgDirection.y /= magnitude;
        }

        return avgDirection;
    }

    // Calculate cohesion force (steer towards average position of neighbors)
    calculateCohesion(neighbors) {
        if (neighbors.length === 0) return { x: 0, y: 0 };

        let centerOfMass = { x: 0, y: 0 };

        for (const neighbor of neighbors) {
            centerOfMass.x += neighbor.x;
            centerOfMass.y += neighbor.y;
        }

        centerOfMass.x /= neighbors.length;
        centerOfMass.y /= neighbors.length;

        // Calculate direction to center of mass
        const direction = {
            x: centerOfMass.x - this.x,
            y: centerOfMass.y - this.y
        };

        // Normalize
        const magnitude = Math.sqrt(direction.x * direction.x + direction.y * direction.y);
        if (magnitude > 0) {
            direction.x /= magnitude;
            direction.y /= magnitude;
        }

        return direction;
    }

    // Calculate separation force (steer away from neighbors)
    calculateSeparation(neighbors) {
        if (neighbors.length === 0) return { x: 0, y: 0 };

        let separationForce = { x: 0, y: 0 };
        let count = 0;

        for (const neighbor of neighbors) {
            const distance = Math.sqrt(
                (this.x - neighbor.x) * (this.x - neighbor.x) +
                (this.y - neighbor.y) * (this.y - neighbor.y)
            );

            if (distance < this.separationRadius && distance > 0) {
                // Calculate direction away from neighbor
                const direction = {
                    x: this.x - neighbor.x,
                    y: this.y - neighbor.y
                };

                // Weight by distance (closer = stronger force)
                const weight = this.separationRadius / distance;
                direction.x *= weight;
                direction.y *= weight;

                separationForce.x += direction.x;
                separationForce.y += direction.y;
                count++;
            }
        }

        if (count > 0) {
            separationForce.x /= count;
            separationForce.y /= count;

            // Normalize
            const magnitude = Math.sqrt(separationForce.x * separationForce.x + separationForce.y * separationForce.y);
            if (magnitude > 0) {
                separationForce.x /= magnitude;
                separationForce.y /= magnitude;
            }
        }

        return separationForce;
    }

    // Calculate seek force (steer towards target)
    calculateSeek() {
        if (!this.targetX || !this.targetY) return { x: 0, y: 0 };

        const direction = {
            x: this.targetX - this.x,
            y: this.targetY - this.y
        };

        const distance = Math.sqrt(direction.x * direction.x + direction.y * direction.y);

        if (distance < 5) {
            // Close to target, reduce force
            return { x: 0, y: 0 };
        }

        // Normalize
        if (distance > 0) {
            direction.x /= distance;
            direction.y /= distance;
        }

        return direction;
    }

    // Calculate wander force (random exploration)
    calculateWander() {
        // Update wander angle
        this.wanderAngle += (Math.random() - 0.5) * 0.3;

        // Calculate wander force
        const wanderForce = {
            x: Math.cos(this.wanderAngle),
            y: Math.sin(this.wanderAngle)
        };

        return wanderForce;
    }

    // Calculate obstacle avoidance force
    calculateObstacleAvoidance(obstacles) {
        let avoidanceForce = { x: 0, y: 0 };

        for (const obstacle of obstacles) {
            const distance = Math.sqrt(
                (this.x - obstacle.x) * (this.x - obstacle.x) +
                (this.y - obstacle.y) * (this.y - obstacle.y)
            );

            const avoidanceRadius = 30;
            if (distance < avoidanceRadius && distance > 0) {
                // Calculate direction away from obstacle
                const direction = {
                    x: this.x - obstacle.x,
                    y: this.y - obstacle.y
                };

                // Weight by distance
                const weight = avoidanceRadius / distance;
                direction.x *= weight;
                direction.y *= weight;

                avoidanceForce.x += direction.x;
                avoidanceForce.y += direction.y;
            }
        }

        // Normalize
        const magnitude = Math.sqrt(avoidanceForce.x * avoidanceForce.x + avoidanceForce.y * avoidanceForce.y);
        if (magnitude > 0) {
            avoidanceForce.x /= magnitude;
            avoidanceForce.y /= magnitude;
        }

        return avoidanceForce;
    }

    // Get neighbors within radius
    getNeighbors(allVehicles) {
        const neighbors = [];

        for (const vehicle of allVehicles.values()) {
            if (vehicle.id === this.id) continue;

            const distance = Math.sqrt(
                (this.x - vehicle.x) * (this.x - vehicle.x) +
                (this.y - vehicle.y) * (this.y - vehicle.y)
            );

            if (distance <= this.neighborRadius) {
                neighbors.push(vehicle);
            }
        }

        return neighbors;
    }
    
    update(deltaTime, terrainEngine, fleetManager = null) {
        this.lastUpdate = Date.now();

        // Update battery drain
        if (this.taskStatus !== 'idle') {
            this.batteryLevel = Math.max(0, this.batteryLevel - deltaTime * 0.01);
        }

        // Update swarm behavior if fleet manager is available
        if (fleetManager && this.swarmEnabled && this.batteryLevel > 10) {
            const neighbors = this.getNeighbors(fleetManager.vehicles);
            const obstacles = fleetManager.getObstacles ? fleetManager.getObstacles() : [];
            this.updateSwarmBehavior(neighbors, obstacles);
        }

        // Update AI behavior
        if (this.aiEnabled && this.batteryLevel > 10) {
            this.updateAI(deltaTime, terrainEngine);
        }
        
        // Update movement (physics-based if available, fallback otherwise)
        if (this.physicsBody) {
            this.updatePhysicsMovement(deltaTime);
        } else {
            this.updateMovement(deltaTime);
        }
        
        // Update work progress
        if (this.taskStatus === 'working') {
            this.updateWork(deltaTime, terrainEngine);
        }
        
        // Update decision cooldown
        this.decisionCooldown = Math.max(0, this.decisionCooldown - deltaTime);
    }
    
    updateAI(deltaTime, terrainEngine) {
        // AI decision making every 2 seconds
        if (this.decisionCooldown > 0) return;
        
        this.decisionCooldown = 2000; // 2 second cooldown
        
        switch (this.taskStatus) {
            case 'idle':
                this.findWork(terrainEngine);
                break;
            case 'moving':
                this.checkMovementProgress();
                break;
            case 'working':
                this.evaluateWorkProgress(terrainEngine);
                break;
        }
    }
    
    findWork(terrainEngine) {
        // AI logic to find appropriate work based on vehicle type
        const workAreas = this.scanForWork(terrainEngine);
        
        if (workAreas.length > 0) {
            const bestWork = this.selectBestWork(workAreas);
            this.assignTask(bestWork);
        } else {
            // No work found, patrol or return to base
            this.patrol();
        }
    }
    
    scanForWork(terrainEngine) {
        const workAreas = [];
        const scanRadius = 50;
        
        // Scan terrain for work opportunities
        for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 8) {
            const scanX = this.x + Math.cos(angle) * scanRadius;
            const scanY = this.y + Math.sin(angle) * scanRadius;
            
            if (terrainEngine) {
                const elevation = terrainEngine.getElevationAt(scanX, scanY);
                if (elevation) {
                    const workType = this.evaluateWorkType(elevation);
                    if (workType) {
                        workAreas.push({
                            x: scanX,
                            y: scanY,
                            type: workType,
                            priority: this.calculateWorkPriority(workType, elevation),
                            elevation: elevation
                        });
                    }
                }
            }
        }
        
        return workAreas;
    }
    
    evaluateWorkType(elevation) {
        // Determine what type of work is needed based on terrain
        const height = elevation.elevation;
        
        switch (this.type) {
            case 'excavator':
                if (height > 0.5) return 'excavate'; // High areas need digging
                break;
            case 'bulldozer':
                if (Math.abs(height) > 0.3) return 'level'; // Uneven areas need leveling
                break;
            case 'dump_truck':
                if (height < -0.3) return 'fill'; // Low areas need filling
                break;
            case 'crane':
                // Cranes work on precision tasks
                return 'precision_work';
            case 'compactor':
                if (Math.abs(height) < 0.2) return 'compact'; // Flat areas need compacting
                break;
        }
        
        return null;
    }
    
    calculateWorkPriority(workType, elevation) {
        // Calculate priority based on vehicle specialty and terrain needs
        let priority = 0.5;
        
        // Distance factor (closer = higher priority)
        const distance = Math.sqrt((elevation.coordinates.x - this.x) ** 2 + 
                                 (elevation.coordinates.y - this.y) ** 2);
        priority += Math.max(0, 1 - distance / 100);
        
        // Type-specific priority adjustments
        switch (this.type) {
            case 'excavator':
                if (workType === 'excavate') priority += 0.4;
                break;
            case 'bulldozer':
                if (workType === 'level') priority += 0.4;
                break;
            case 'dump_truck':
                if (workType === 'fill') priority += 0.4;
                break;
            case 'crane':
                if (workType === 'precision_work') priority += 0.4;
                break;
            case 'compactor':
                if (workType === 'compact') priority += 0.4;
                break;
        }
        
        return Math.min(1, priority);
    }
    
    selectBestWork(workAreas) {
        // Select the highest priority work
        return workAreas.reduce((best, current) => 
            current.priority > best.priority ? current : best
        );
    }
    
    assignTask(workArea) {
        this.currentTask = workArea;
        this.targetX = workArea.x;
        this.targetY = workArea.y;
        this.taskStatus = 'moving';
        this.workProgress = 0;
        
        console.log(`🎯 ${this.id} assigned ${workArea.type} task at (${workArea.x.toFixed(1)}, ${workArea.y.toFixed(1)})`);
    }
    
    patrol() {
        // Random patrol movement when no work is found
        const patrolRadius = 30;
        this.targetX = this.x + (Math.random() - 0.5) * patrolRadius;
        this.targetY = this.y + (Math.random() - 0.5) * patrolRadius;
        this.taskStatus = 'moving';
        
        console.log(`🚶 ${this.id} patrolling to (${this.targetX.toFixed(1)}, ${this.targetY.toFixed(1)})`);
    }
    
    updateMovement(deltaTime) {
        if (this.taskStatus !== 'moving') return;
        
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 2) {
            // Reached target
            this.x = this.targetX;
            this.y = this.targetY;
            
            if (this.currentTask) {
                this.taskStatus = 'working';
                this.attachmentState = 'active';
                console.log(`🔧 ${this.id} starting work`);
            } else {
                this.taskStatus = 'idle';
            }
            
            this.stuckCounter = 0;
        } else {
            // Move toward target
            const moveDistance = this.speed * deltaTime / 1000;
            this.x += (dx / distance) * moveDistance;
            this.y += (dy / distance) * moveDistance;
            this.rotation = Math.atan2(dy, dx);
            
            // Check if stuck
            this.stuckCounter++;
            if (this.stuckCounter > 100) {
                console.log(`⚠️ ${this.id} appears stuck, finding new path`);
                this.findAlternatePath();
                this.stuckCounter = 0;
            }
        }
    }
    
    findAlternatePath() {
        // Simple obstacle avoidance
        const avoidanceAngle = (Math.random() - 0.5) * Math.PI;
        const avoidanceDistance = 20;
        
        this.targetX += Math.cos(avoidanceAngle) * avoidanceDistance;
        this.targetY += Math.sin(avoidanceAngle) * avoidanceDistance;
    }
    
    updateWork(deltaTime, terrainEngine) {
        if (!this.currentTask) return;
        
        // Simulate work progress
        const workRate = this.workEfficiency * deltaTime / 1000;
        this.workProgress += workRate;
        
        // Apply terrain modifications based on vehicle type
        if (terrainEngine && this.workProgress > 0.1) {
            this.applyTerrainWork(terrainEngine);
        }
        
        // Check if work is complete
        if (this.workProgress >= 1.0) {
            this.completeWork();
        }
    }
    
    applyTerrainWork(terrainEngine) {
        // Apply actual terrain modifications based on vehicle type
        const gridX = Math.floor(this.x / terrainEngine.cellWidth);
        const gridY = Math.floor(this.y / terrainEngine.cellHeight);
        const workRadius = 3;
        
        for (let dy = -workRadius; dy <= workRadius; dy++) {
            for (let dx = -workRadius; dx <= workRadius; dx++) {
                const nx = gridX + dx;
                const ny = gridY + dy;
                
                if (nx >= 0 && nx < terrainEngine.gridWidth && 
                    ny >= 0 && ny < terrainEngine.gridHeight) {
                    
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= workRadius) {
                        const index = ny * terrainEngine.gridWidth + nx;
                        const falloff = 1 - (distance / workRadius);
                        const effect = 0.001 * falloff * this.workEfficiency;
                        
                        switch (this.currentTask.type) {
                            case 'excavate':
                                terrainEngine.heightmap[index] = Math.max(-1, 
                                    terrainEngine.heightmap[index] - effect);
                                break;
                            case 'fill':
                                terrainEngine.heightmap[index] = Math.min(1, 
                                    terrainEngine.heightmap[index] + effect);
                                break;
                            case 'level':
                                // Smooth toward average
                                const target = 0.5;
                                const current = terrainEngine.heightmap[index];
                                terrainEngine.heightmap[index] = current + (target - current) * effect;
                                break;
                            case 'compact':
                                // Slight smoothing effect
                                // Implementation would involve averaging with neighbors
                                break;
                        }
                    }
                }
            }
        }
    }
    
    completeWork() {
        console.log(`✅ ${this.id} completed ${this.currentTask.type} work`);
        this.currentTask = null;
        this.taskStatus = 'idle';
        this.attachmentState = 'idle';
        this.workProgress = 0;
    }
    
    checkMovementProgress() {
        // Check if vehicle is making progress toward target
        const dx = this.targetX - this.x;
        const dy = this.targetY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance > 50) {
            // Target too far, find closer work
            this.taskStatus = 'idle';
            this.currentTask = null;
        }
    }
    
    evaluateWorkProgress(terrainEngine) {
        // Evaluate if current work is still needed
        if (!this.currentTask) {
            this.taskStatus = 'idle';
            return;
        }
        
        // Check if work area still needs attention
        const elevation = terrainEngine.getElevationAt(this.x, this.y);
        if (elevation) {
            const stillNeedsWork = this.evaluateWorkType(elevation);
            if (!stillNeedsWork || stillNeedsWork !== this.currentTask.type) {
                console.log(`🔄 ${this.id} work no longer needed, finding new task`);
                this.completeWork();
            }
        }
    }
    
    // Manual control methods
    moveTo(x, y) {
        this.targetX = x;
        this.targetY = y;
        this.taskStatus = 'moving';
        this.currentTask = null;
        this.aiEnabled = false; // Disable AI when manually controlled
        
        console.log(`🎮 ${this.id} manually directed to (${x.toFixed(1)}, ${y.toFixed(1)})`);
    }
    
    startWork(workType) {
        this.currentTask = { type: workType, x: this.x, y: this.y };
        this.taskStatus = 'working';
        this.attachmentState = 'active';
        this.workProgress = 0;
        this.aiEnabled = false;
        
        console.log(`🔧 ${this.id} manually started ${workType} work`);
    }
    
    stop() {
        this.taskStatus = 'idle';
        this.attachmentState = 'idle';
        this.currentTask = null;
        this.aiEnabled = false;
        
        console.log(`🛑 ${this.id} stopped`);
    }
    
    enableAI() {
        this.aiEnabled = true;
        console.log(`🤖 ${this.id} AI enabled`);
    }
    
    disableAI() {
        this.aiEnabled = false;
        console.log(`🎮 ${this.id} AI disabled - manual control`);
    }
    
    getStatus() {
        return {
            id: this.id,
            type: this.type,
            position: { x: this.x, y: this.y },
            target: { x: this.targetX, y: this.targetY },
            rotation: this.rotation,
            speed: this.speed,
            power: this.power,
            batteryLevel: this.batteryLevel,
            taskStatus: this.taskStatus,
            attachmentState: this.attachmentState,
            workProgress: this.workProgress,
            aiEnabled: this.aiEnabled,
            specialty: this.getSpecialty(),
            neuralNetworkEnabled: this.neuralNetworkEnabled
        };
    }

    // ===== NEURAL NETWORK DECISION MAKING =====

    // Initialize neural network for decision making
    initializeNeuralNetwork() {
        try {
            if (typeof synaptic === 'undefined') {
                console.warn('⚠️ Synaptic.js not available for neural networks');
                this.neuralNetworkEnabled = false;
                return;
            }

            // Create a simple feedforward network
            // Input: terrain info, nearby vehicles, task status, fuel, health
            // Hidden: processing layer
            // Output: movement decisions, task priorities
            const inputSize = 8;   // terrain height, target distance, battery, task urgency, etc.
            const hiddenSize = 6;  // processing neurons
            const outputSize = 3;  // move_direction, task_priority, speed_modifier

            this.neuralNetwork = new synaptic.Architect.Perceptron(inputSize, hiddenSize, outputSize);

            console.log(`🧠 Neural network initialized for ${this.id}`);
            this.neuralNetworkEnabled = true;

        } catch (error) {
            console.error(`❌ Failed to initialize neural network for ${this.id}:`, error);
            this.neuralNetworkEnabled = false;
        }
    }

    // Prepare input data for neural network
    prepareNeuralInputs(terrainEngine, fleetManager) {
        if (!this.neuralNetworkEnabled || !this.neuralNetwork) return null;

        try {
            const inputs = [];

            // 1. Terrain height at current position (normalized 0-1)
            const terrainHeight = terrainEngine ? terrainEngine.getHeightAt(this.x, this.y) / 100 : 0.5;
            inputs.push(Math.max(0, Math.min(1, terrainHeight)));

            // 2. Distance to target (normalized 0-1)
            const targetDistance = this.targetX !== null ?
                Math.sqrt((this.targetX - this.x) ** 2 + (this.targetY - this.y) ** 2) / 200 : 0.5;
            inputs.push(Math.max(0, Math.min(1, targetDistance)));

            // 3. Battery level (normalized 0-1)
            inputs.push(this.batteryLevel / 100);

            // 4. Current speed (normalized 0-1)
            inputs.push(this.speed / this.maxSpeed);

            // 5. Number of nearby vehicles (normalized 0-1)
            const nearbyVehicles = fleetManager ? this.getNeighbors(fleetManager.vehicles).length / 5 : 0;
            inputs.push(Math.max(0, Math.min(1, nearbyVehicles)));

            // 6. Task urgency (0-1 based on task type)
            const taskUrgency = this.taskStatus === 'emergency' ? 1.0 :
                               this.taskStatus === 'working' ? 0.7 : 0.3;
            inputs.push(taskUrgency);

            // 7. Work progress (0-1)
            inputs.push(this.workProgress / 100);

            // 8. Time factor (for temporal decisions)
            inputs.push((Date.now() % 10000) / 10000);

            this.decisionInputs = inputs;
            return inputs;

        } catch (error) {
            console.error(`❌ Error preparing neural inputs for ${this.id}:`, error);
            return null;
        }
    }

    // Make decision using neural network
    makeNeuralDecision(terrainEngine, fleetManager) {
        if (!this.neuralNetworkEnabled || !this.neuralNetwork) return null;

        const inputs = this.prepareNeuralInputs(terrainEngine, fleetManager);
        if (!inputs) return null;

        try {
            // Get neural network output
            const outputs = this.neuralNetwork.activate(inputs);

            // Interpret outputs
            const decision = {
                moveDirection: (outputs[0] - 0.5) * Math.PI * 2,  // Direction in radians
                taskPriority: outputs[1],                         // 0 to 1
                speedModifier: outputs[2],                        // 0 to 1
                timestamp: Date.now(),
                confidence: Math.max(...outputs) - Math.min(...outputs) // Decision confidence
            };

            this.lastDecision = decision;
            this.decisionHistory.push(decision);

            // Keep only recent decisions
            if (this.decisionHistory.length > 50) {
                this.decisionHistory.shift();
            }

            return decision;

        } catch (error) {
            console.error(`❌ Error making neural decision for ${this.id}:`, error);
            return null;
        }
    }

    // Enable/disable neural network
    setNeuralNetworkEnabled(enabled) {
        this.neuralNetworkEnabled = enabled;
        if (enabled && !this.neuralNetwork) {
            this.initializeNeuralNetwork();
        }
        console.log(`🧠 Neural network ${enabled ? 'enabled' : 'disabled'} for ${this.id}`);
    }

    // Get neural network statistics
    getNeuralStats() {
        return {
            enabled: this.neuralNetworkEnabled,
            hasNetwork: !!this.neuralNetwork,
            decisionHistory: this.decisionHistory.length,
            trainingData: this.trainingData.length,
            lastDecision: this.lastDecision
        };
    }
}

class VehicleFleetManager {
    constructor(terrainEngine) {
        this.terrainEngine = terrainEngine;
        this.vehicles = new Map();
        this.selectedVehicle = null;
        this.lastUpdate = Date.now();

        // Fleet statistics
        this.totalWorkCompleted = 0;
        this.totalDistance = 0;
        this.operationTime = 0;

        // Cannon.js physics world
        this.physicsWorld = null;
        this.physicsEnabled = false;

        // Swarm Intelligence coordination
        this.swarmEnabled = true;
        this.coordinationMode = 'autonomous'; // 'autonomous', 'formation', 'task_based'
        this.formations = new Map();
        this.taskGroups = new Map();
        this.obstacles = [];

        this.initializeFleet();

        console.log('🚛 Vehicle Fleet Manager initialized');
    }

    // Initialize Cannon.js physics world for realistic vehicle simulation
    initPhysicsWorld() {
        try {
            if (typeof CANNON === 'undefined') {
                console.warn('⚠️ Cannon.js not available, using fallback vehicle physics');
                return false;
            }

            console.log('🔧 Initializing Cannon.js physics world for vehicles...');

            // Create physics world
            this.physicsWorld = new CANNON.World();
            this.physicsWorld.gravity.set(0, -9.82, 0); // Earth gravity
            this.physicsWorld.broadphase = new CANNON.NaiveBroadphase();

            // Create ground plane
            const groundShape = new CANNON.Plane();
            const groundBody = new CANNON.Body({ mass: 0 });
            groundBody.addShape(groundShape);
            groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
            this.physicsWorld.add(groundBody);

            // Create materials and contact materials
            this.setupPhysicsMaterials();

            this.physicsEnabled = true;

            // Initialize physics for existing vehicles
            this.vehicles.forEach(vehicle => {
                vehicle.initPhysics(this.physicsWorld);
            });

            console.log('✅ Vehicle physics world initialized successfully');
            return true;

        } catch (error) {
            console.error('❌ Vehicle physics world initialization failed:', error);
            return false;
        }
    }

    // Setup physics materials for realistic vehicle behavior
    setupPhysicsMaterials() {
        // Ground material
        const groundMaterial = new CANNON.Material('ground');

        // Vehicle materials
        const chassisMaterial = new CANNON.Material('chassis');
        const wheelMaterial = new CANNON.Material('wheel');

        // Contact materials (define interactions)
        const wheelGroundContact = new CANNON.ContactMaterial(
            wheelMaterial,
            groundMaterial,
            {
                friction: 0.4,
                restitution: 0.3,
                contactEquationStiffness: 1e8,
                contactEquationRelaxation: 3
            }
        );

        const chassisGroundContact = new CANNON.ContactMaterial(
            chassisMaterial,
            groundMaterial,
            {
                friction: 0.4,
                restitution: 0.3
            }
        );

        this.physicsWorld.addContactMaterial(wheelGroundContact);
        this.physicsWorld.addContactMaterial(chassisGroundContact);
    }

    // Update physics world
    updatePhysics(deltaTime) {
        if (!this.physicsWorld || !this.physicsEnabled) return;

        try {
            // Step the physics simulation
            this.physicsWorld.step(deltaTime / 1000); // Convert ms to seconds

        } catch (error) {
            console.error('Physics update error:', error);
        }
    }

    // ===== SWARM INTELLIGENCE COORDINATION =====

    // Enable/disable swarm behavior for all vehicles
    enableSwarmBehavior(enabled = true) {
        this.swarmEnabled = enabled;
        this.vehicles.forEach(vehicle => {
            vehicle.swarmEnabled = enabled;
        });

        console.log(`🐝 Swarm behavior ${enabled ? 'enabled' : 'disabled'} for fleet`);
    }

    // Set coordination mode for the fleet
    setCoordinationMode(mode) {
        this.coordinationMode = mode;
        console.log(`🎯 Fleet coordination mode set to: ${mode}`);

        switch (mode) {
            case 'formation':
                this.initializeFormations();
                break;
            case 'task_based':
                this.initializeTaskGroups();
                break;
            case 'autonomous':
                // Individual vehicle autonomy
                break;
        }
    }

    // Initialize formation patterns
    initializeFormations() {
        // V-formation for efficient movement
        this.formations.set('v_formation', {
            name: 'V Formation',
            positions: [
                { x: 0, y: 0 },      // Leader
                { x: -20, y: 15 },   // Left wing
                { x: 20, y: 15 },    // Right wing
                { x: -40, y: 30 },   // Left rear
                { x: 40, y: 30 }     // Right rear
            ]
        });

        // Line formation for construction work
        this.formations.set('line_formation', {
            name: 'Line Formation',
            positions: [
                { x: 0, y: 0 },
                { x: 30, y: 0 },
                { x: 60, y: 0 },
                { x: 90, y: 0 },
                { x: 120, y: 0 }
            ]
        });

        // Circle formation for area coverage
        this.formations.set('circle_formation', {
            name: 'Circle Formation',
            positions: this.generateCirclePositions(5, 40)
        });

        console.log('✅ Formation patterns initialized');
    }

    // Generate circle formation positions
    generateCirclePositions(count, radius) {
        const positions = [];
        for (let i = 0; i < count; i++) {
            const angle = (i / count) * Math.PI * 2;
            positions.push({
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius
            });
        }
        return positions;
    }

    // Initialize task-based groups
    initializeTaskGroups() {
        // Excavation team
        this.taskGroups.set('excavation', {
            name: 'Excavation Team',
            vehicles: [],
            leader: null,
            task: 'excavation',
            coordination: 'sequential'
        });

        // Transport team
        this.taskGroups.set('transport', {
            name: 'Transport Team',
            vehicles: [],
            leader: null,
            task: 'transport',
            coordination: 'parallel'
        });

        // Construction team
        this.taskGroups.set('construction', {
            name: 'Construction Team',
            vehicles: [],
            leader: null,
            task: 'construction',
            coordination: 'coordinated'
        });

        console.log('✅ Task groups initialized');
    }

    // Assign vehicle to formation
    assignToFormation(vehicleId, formationName, position) {
        const vehicle = this.vehicles.get(vehicleId);
        const formation = this.formations.get(formationName);

        if (vehicle && formation && formation.positions[position]) {
            vehicle.formationRole = {
                formation: formationName,
                position: position,
                targetOffset: formation.positions[position]
            };

            console.log(`🎯 ${vehicleId} assigned to ${formationName} position ${position}`);
            return true;
        }

        return false;
    }

    // Assign vehicle to task group
    assignToTaskGroup(vehicleId, groupName) {
        const vehicle = this.vehicles.get(vehicleId);
        const group = this.taskGroups.get(groupName);

        if (vehicle && group) {
            // Remove from previous group
            this.taskGroups.forEach(g => {
                g.vehicles = g.vehicles.filter(v => v !== vehicleId);
            });

            // Add to new group
            group.vehicles.push(vehicleId);

            // Set leader if first vehicle
            if (!group.leader) {
                group.leader = vehicleId;
            }

            vehicle.taskGroup = groupName;

            console.log(`👥 ${vehicleId} assigned to ${groupName} task group`);
            return true;
        }

        return false;
    }

    // Get obstacles for avoidance
    getObstacles() {
        // Return static obstacles and terrain features
        return this.obstacles;
    }

    // Add obstacle for fleet to avoid
    addObstacle(x, y, radius = 20) {
        this.obstacles.push({ x, y, radius });
    }

    // Remove obstacles
    clearObstacles() {
        this.obstacles = [];
    }

    // Coordinate fleet movement based on mode
    coordinateFleetMovement() {
        switch (this.coordinationMode) {
            case 'formation':
                this.updateFormationMovement();
                break;
            case 'task_based':
                this.updateTaskGroupMovement();
                break;
            case 'autonomous':
                // Vehicles coordinate individually through swarm behavior
                break;
        }
    }

    // Update formation-based movement
    updateFormationMovement() {
        this.formations.forEach((formation, formationName) => {
            const vehiclesInFormation = [];

            this.vehicles.forEach(vehicle => {
                if (vehicle.formationRole && vehicle.formationRole.formation === formationName) {
                    vehiclesInFormation.push(vehicle);
                }
            });

            if (vehiclesInFormation.length > 0) {
                // Find leader (position 0)
                const leader = vehiclesInFormation.find(v => v.formationRole.position === 0);

                if (leader) {
                    // Update formation positions relative to leader
                    vehiclesInFormation.forEach(vehicle => {
                        if (vehicle !== leader) {
                            const offset = vehicle.formationRole.targetOffset;
                            vehicle.targetX = leader.x + offset.x;
                            vehicle.targetY = leader.y + offset.y;
                            vehicle.taskStatus = 'moving';
                        }
                    });
                }
            }
        });
    }

    // Update task group movement
    updateTaskGroupMovement() {
        this.taskGroups.forEach(group => {
            if (group.vehicles.length === 0) return;

            const leader = this.vehicles.get(group.leader);
            if (!leader) return;

            switch (group.coordination) {
                case 'sequential':
                    // Vehicles follow in sequence
                    this.updateSequentialMovement(group);
                    break;
                case 'parallel':
                    // Vehicles work in parallel
                    this.updateParallelMovement(group);
                    break;
                case 'coordinated':
                    // Vehicles coordinate their actions
                    this.updateCoordinatedMovement(group);
                    break;
            }
        });
    }

    // Update sequential movement (follow the leader)
    updateSequentialMovement(group) {
        for (let i = 1; i < group.vehicles.length; i++) {
            const vehicle = this.vehicles.get(group.vehicles[i]);
            const previousVehicle = this.vehicles.get(group.vehicles[i - 1]);

            if (vehicle && previousVehicle) {
                // Follow previous vehicle with offset
                const offset = 25; // Distance behind
                const angle = previousVehicle.rotation + Math.PI; // Opposite direction

                vehicle.targetX = previousVehicle.x + Math.cos(angle) * offset;
                vehicle.targetY = previousVehicle.y + Math.sin(angle) * offset;
                vehicle.taskStatus = 'moving';
            }
        }
    }

    // Update parallel movement
    updateParallelMovement(group) {
        // Vehicles spread out to cover more area
        const spacing = 40;
        const leader = this.vehicles.get(group.leader);

        if (leader) {
            group.vehicles.forEach((vehicleId, index) => {
                if (index === 0) return; // Skip leader

                const vehicle = this.vehicles.get(vehicleId);
                if (vehicle) {
                    const offset = (index - (group.vehicles.length - 1) / 2) * spacing;
                    vehicle.targetX = leader.x + offset;
                    vehicle.targetY = leader.y;
                    vehicle.taskStatus = 'moving';
                }
            });
        }
    }

    // Update coordinated movement
    updateCoordinatedMovement(group) {
        // Vehicles coordinate based on task requirements
        // This could be enhanced with specific construction coordination logic
        this.updateParallelMovement(group); // Default to parallel for now
    }

    initializeFleet() {
        // Initialize the complete K'NEX vehicle fleet
        const fleetConfig = [
            { id: 'EX001', type: 'excavator', x: 100, y: 150 },
            { id: 'BD001', type: 'bulldozer', x: 200, y: 200 },
            { id: 'DT001', type: 'dump_truck', x: 300, y: 100 },
            { id: 'CR001', type: 'crane', x: 150, y: 300 },
            { id: 'CP001', type: 'compactor', x: 250, y: 250 }
        ];

        fleetConfig.forEach(config => {
            const vehicle = new Vehicle(config.id, config.type, config.x, config.y);
            this.vehicles.set(config.id, vehicle);

            // Initialize physics if world is available
            if (this.physicsWorld) {
                vehicle.initPhysics(this.physicsWorld);
            }
        });

        console.log(`✅ Fleet initialized with ${this.vehicles.size} vehicles`);
    }

    update() {
        const now = Date.now();
        const deltaTime = now - this.lastUpdate;
        this.lastUpdate = now;

        this.operationTime += deltaTime;

        // Update physics world first
        this.updatePhysics(deltaTime);

        // Coordinate fleet movement
        if (this.swarmEnabled) {
            this.coordinateFleetMovement();
        }

        // Update all vehicles with fleet manager reference for swarm behavior
        this.vehicles.forEach(vehicle => {
            vehicle.update(deltaTime, this.terrainEngine, this);
        });
    }

    selectVehicle(vehicleId) {
        if (this.vehicles.has(vehicleId)) {
            this.selectedVehicle = vehicleId;
            console.log(`🎯 Selected vehicle: ${vehicleId}`);
            return this.vehicles.get(vehicleId);
        }
        return null;
    }

    getSelectedVehicle() {
        return this.selectedVehicle ? this.vehicles.get(this.selectedVehicle) : null;
    }

    commandVehicle(vehicleId, command) {
        const vehicle = this.vehicles.get(vehicleId);
        if (!vehicle) return false;

        switch (command.action) {
            case 'move':
                vehicle.moveTo(command.x, command.y);
                break;
            case 'work':
                vehicle.startWork(command.workType || 'general');
                break;
            case 'stop':
                vehicle.stop();
                break;
            case 'enable_ai':
                vehicle.enableAI();
                break;
            case 'disable_ai':
                vehicle.disableAI();
                break;
            default:
                console.warn(`Unknown command: ${command.action}`);
                return false;
        }

        return true;
    }

    startFloodDefenseMission() {
        console.log('🌊 Starting Fleet Flood Defense Mission!');

        // Assign specific roles to each vehicle
        const missions = [
            { vehicleId: 'EX001', task: 'excavate', area: 'north_moat' },
            { vehicleId: 'BD001', task: 'level', area: 'defense_wall' },
            { vehicleId: 'DT001', task: 'fill', area: 'south_moat' },
            { vehicleId: 'CR001', task: 'precision_work', area: 'gate_construction' },
            { vehicleId: 'CP001', task: 'compact', area: 'road_network' }
        ];

        missions.forEach(mission => {
            const vehicle = this.vehicles.get(mission.vehicleId);
            if (vehicle) {
                vehicle.enableAI();
                // Set specific mission parameters
                vehicle.currentMission = mission;
                console.log(`📋 ${mission.vehicleId} assigned to ${mission.task} in ${mission.area}`);
            }
        });

        return missions;
    }

    getFleetStatus() {
        const status = {
            totalVehicles: this.vehicles.size,
            activeVehicles: 0,
            idleVehicles: 0,
            workingVehicles: 0,
            movingVehicles: 0,
            averageBattery: 0,
            totalWorkCompleted: this.totalWorkCompleted,
            operationTime: this.operationTime,
            vehicles: {}
        };

        let batterySum = 0;

        this.vehicles.forEach(vehicle => {
            const vehicleStatus = vehicle.getStatus();
            status.vehicles[vehicle.id] = vehicleStatus;

            batterySum += vehicleStatus.batteryLevel;

            switch (vehicleStatus.taskStatus) {
                case 'idle':
                    status.idleVehicles++;
                    break;
                case 'working':
                    status.workingVehicles++;
                    status.activeVehicles++;
                    break;
                case 'moving':
                    status.movingVehicles++;
                    status.activeVehicles++;
                    break;
            }
        });

        status.averageBattery = batterySum / this.vehicles.size;

        return status;
    }

    render(ctx) {
        // Render all vehicles on the terrain
        this.vehicles.forEach(vehicle => {
            this.renderVehicle(ctx, vehicle);
        });

        // Render selection indicator
        if (this.selectedVehicle) {
            const vehicle = this.vehicles.get(this.selectedVehicle);
            if (vehicle) {
                this.renderSelectionIndicator(ctx, vehicle);
            }
        }
    }

    renderVehicle(ctx, vehicle) {
        const x = vehicle.x;
        const y = vehicle.y;

        // Vehicle body
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(vehicle.rotation);

        // Vehicle color based on type
        const colors = {
            excavator: '#FF6B35',
            bulldozer: '#F7931E',
            dump_truck: '#4CAF50',
            crane: '#2196F3',
            compactor: '#9C27B0'
        };

        ctx.fillStyle = colors[vehicle.type] || '#666';
        ctx.fillRect(-8, -6, 16, 12);

        // Direction indicator
        ctx.fillStyle = '#FFF';
        ctx.fillRect(6, -2, 4, 4);

        ctx.restore();

        // Status indicators
        this.renderVehicleStatus(ctx, vehicle);
    }

    renderVehicleStatus(ctx, vehicle) {
        const x = vehicle.x;
        const y = vehicle.y - 20;

        // Vehicle ID
        ctx.fillStyle = 'white';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(vehicle.id, x, y);

        // Battery level
        const batteryWidth = 20;
        const batteryHeight = 4;
        const batteryX = x - batteryWidth / 2;
        const batteryY = y + 5;

        // Battery background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(batteryX, batteryY, batteryWidth, batteryHeight);

        // Battery level
        const batteryLevel = vehicle.batteryLevel / 100;
        const batteryColor = batteryLevel > 0.5 ? '#4CAF50' :
                           batteryLevel > 0.2 ? '#FF9800' : '#F44336';
        ctx.fillStyle = batteryColor;
        ctx.fillRect(batteryX, batteryY, batteryWidth * batteryLevel, batteryHeight);

        // Task status indicator
        if (vehicle.taskStatus !== 'idle') {
            ctx.fillStyle = vehicle.taskStatus === 'working' ? '#4CAF50' : '#2196F3';
            ctx.beginPath();
            ctx.arc(x + 12, y - 5, 3, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    renderSelectionIndicator(ctx, vehicle) {
        const x = vehicle.x;
        const y = vehicle.y;

        // Selection circle
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        // Target line
        if (vehicle.taskStatus === 'moving') {
            ctx.strokeStyle = 'rgba(255, 215, 0, 0.5)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(vehicle.targetX, vehicle.targetY);
            ctx.stroke();

            // Target indicator
            ctx.fillStyle = '#FFD700';
            ctx.beginPath();
            ctx.arc(vehicle.targetX, vehicle.targetY, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Utility methods
    getVehicleAt(x, y, radius = 20) {
        for (const vehicle of this.vehicles.values()) {
            const distance = Math.sqrt((vehicle.x - x) ** 2 + (vehicle.y - y) ** 2);
            if (distance <= radius) {
                return vehicle;
            }
        }
        return null;
    }

    getAllVehicles() {
        return Array.from(this.vehicles.values());
    }

    getVehicleById(id) {
        return this.vehicles.get(id);
    }

    emergencyStopAll() {
        console.log('🚨 EMERGENCY STOP - All vehicles stopping');
        this.vehicles.forEach(vehicle => {
            vehicle.stop();
        });
    }

    enableAllAI() {
        this.vehicles.forEach(vehicle => {
            vehicle.enableAI();
        });
        console.log('🤖 All vehicle AI enabled');
    }

    disableAllAI() {
        this.vehicles.forEach(vehicle => {
            vehicle.disableAI();
        });
        console.log('🎮 All vehicle AI disabled - manual control mode');
    }
}

// Export for use in other modules
window.Vehicle = Vehicle;
window.VehicleFleetManager = VehicleFleetManager;
