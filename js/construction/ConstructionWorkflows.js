/**
 * Construction Workflows - Realistic Construction Processes
 * Implements proper construction sequences and vehicle behaviors
 */

class ConstructionWorkflows {
    constructor(core) {
        this.core = core;
        this.activeProjects = new Map();
        this.vehicles = new Map();
        this.workflows = new Map();
        this.materials = new Map();
        
        this.initializeWorkflows();
        this.initializeVehicles();
        this.initializeMaterials();
    }
    
    initializeWorkflows() {
        // Road Construction Workflow
        this.workflows.set('road_construction', {
            name: 'Road Construction',
            phases: [
                {
                    name: 'Site Preparation',
                    description: 'Clear and level the construction area',
                    vehicles: ['bulldozer'],
                    duration: 300, // seconds
                    requirements: [],
                    outputs: ['cleared_area']
                },
                {
                    name: 'Excavation',
                    description: 'Excavate to proper depth for road base',
                    vehicles: ['excavator'],
                    duration: 450,
                    requirements: ['cleared_area'],
                    outputs: ['excavated_roadway']
                },
                {
                    name: 'Base Layer',
                    description: 'Place and compact gravel base',
                    vehicles: ['dump_truck', 'compactor'],
                    duration: 600,
                    requirements: ['excavated_roadway'],
                    outputs: ['base_layer']
                },
                {
                    name: 'Surface Layer',
                    description: 'Apply asphalt surface',
                    vehicles: ['paver', 'roller'],
                    duration: 400,
                    requirements: ['base_layer'],
                    outputs: ['finished_road']
                }
            ]
        });
        
        // Building Foundation Workflow
        this.workflows.set('foundation_construction', {
            name: 'Building Foundation',
            phases: [
                {
                    name: 'Site Survey',
                    description: 'Survey and mark foundation area',
                    vehicles: ['surveyor'],
                    duration: 180,
                    requirements: [],
                    outputs: ['surveyed_site']
                },
                {
                    name: 'Excavation',
                    description: 'Excavate foundation to required depth',
                    vehicles: ['excavator'],
                    duration: 540,
                    requirements: ['surveyed_site'],
                    outputs: ['foundation_excavation']
                },
                {
                    name: 'Footing Installation',
                    description: 'Install concrete footings',
                    vehicles: ['concrete_truck', 'crane'],
                    duration: 720,
                    requirements: ['foundation_excavation'],
                    outputs: ['footings_installed']
                },
                {
                    name: 'Foundation Walls',
                    description: 'Pour foundation walls',
                    vehicles: ['concrete_truck', 'pump_truck'],
                    duration: 480,
                    requirements: ['footings_installed'],
                    outputs: ['foundation_complete']
                }
            ]
        });
        
        // Drainage System Workflow
        this.workflows.set('drainage_system', {
            name: 'Drainage System',
            phases: [
                {
                    name: 'Trenching',
                    description: 'Dig trenches for drainage pipes',
                    vehicles: ['trencher', 'excavator'],
                    duration: 360,
                    requirements: [],
                    outputs: ['drainage_trenches']
                },
                {
                    name: 'Pipe Installation',
                    description: 'Install drainage pipes and manholes',
                    vehicles: ['crane', 'pipe_layer'],
                    duration: 480,
                    requirements: ['drainage_trenches'],
                    outputs: ['pipes_installed']
                },
                {
                    name: 'Backfill',
                    description: 'Backfill trenches and compact',
                    vehicles: ['dump_truck', 'compactor'],
                    duration: 300,
                    requirements: ['pipes_installed'],
                    outputs: ['drainage_complete']
                }
            ]
        });
    }
    
    initializeVehicles() {
        // Excavator - Foundation and trenching specialist
        this.vehicles.set('excavator', {
            name: 'Excavator',
            icon: '🚜',
            type: 'heavy_equipment',
            capabilities: ['excavate', 'lift', 'grade'],
            workRadius: 25,
            efficiency: 0.8,
            fuelConsumption: 15, // liters per hour
            operatingCost: 120, // dollars per hour
            behavior: {
                excavate: (x, y, depth) => this.excavatorExcavate(x, y, depth),
                grade: (area) => this.excavatorGrade(area),
                move: (from, to) => this.moveVehicle('excavator', from, to)
            }
        });
        
        // Bulldozer - Site preparation and grading
        this.vehicles.set('bulldozer', {
            name: 'Bulldozer',
            icon: '🚛',
            type: 'heavy_equipment',
            capabilities: ['push', 'grade', 'clear'],
            workRadius: 30,
            efficiency: 0.9,
            fuelConsumption: 18,
            operatingCost: 140,
            behavior: {
                clear: (area) => this.bulldozerClear(area),
                grade: (area, targetLevel) => this.bulldozerGrade(area, targetLevel),
                push: (from, to, material) => this.bulldozerPush(from, to, material)
            }
        });
        
        // Dump Truck - Material transport
        this.vehicles.set('dump_truck', {
            name: 'Dump Truck',
            icon: '🚚',
            type: 'transport',
            capabilities: ['haul', 'dump', 'load'],
            capacity: 15, // cubic meters
            efficiency: 0.85,
            fuelConsumption: 25,
            operatingCost: 80,
            behavior: {
                load: (material, location) => this.dumpTruckLoad(material, location),
                haul: (from, to) => this.dumpTruckHaul(from, to),
                dump: (location, material) => this.dumpTruckDump(location, material)
            }
        });
        
        // Crane - Heavy lifting and placement
        this.vehicles.set('crane', {
            name: 'Mobile Crane',
            icon: '🏗️',
            type: 'lifting',
            capabilities: ['lift', 'place', 'swing'],
            liftCapacity: 50, // tons
            reach: 40, // meters
            efficiency: 0.75,
            operatingCost: 200,
            behavior: {
                lift: (item, from) => this.craneLift(item, from),
                place: (item, to) => this.cranePlace(item, to),
                setup: (location) => this.craneSetup(location)
            }
        });
        
        // Compactor - Soil and material compaction
        this.vehicles.set('compactor', {
            name: 'Soil Compactor',
            icon: '🛞',
            type: 'finishing',
            capabilities: ['compact', 'smooth'],
            workWidth: 8, // meters
            efficiency: 0.9,
            operatingCost: 60,
            behavior: {
                compact: (area, passes) => this.compactorCompact(area, passes),
                smooth: (area) => this.compactorSmooth(area)
            }
        });
    }
    
    initializeMaterials() {
        this.materials.set('gravel', {
            name: 'Gravel',
            density: 1.6, // tons per cubic meter
            cost: 25, // dollars per cubic meter
            compactionFactor: 0.85,
            drainageRate: 0.8,
            color: [128, 128, 128]
        });
        
        this.materials.set('concrete', {
            name: 'Concrete',
            density: 2.4,
            cost: 120,
            compactionFactor: 1.0,
            drainageRate: 0.1,
            color: [200, 200, 200],
            cureTime: 2880 // 48 hours in minutes
        });
        
        this.materials.set('asphalt', {
            name: 'Asphalt',
            density: 2.3,
            cost: 80,
            compactionFactor: 0.95,
            drainageRate: 0.2,
            color: [64, 64, 64]
        });
        
        this.materials.set('soil', {
            name: 'Soil',
            density: 1.8,
            cost: 15,
            compactionFactor: 0.75,
            drainageRate: 0.6,
            color: [101, 67, 33]
        });
    }
    
    startProject(workflowType, location, parameters = {}) {
        const workflow = this.workflows.get(workflowType);
        if (!workflow) {
            console.error(`Unknown workflow type: ${workflowType}`);
            return null;
        }
        
        const project = {
            id: Date.now(),
            type: workflowType,
            workflow: workflow,
            location: location,
            parameters: parameters,
            currentPhase: 0,
            startTime: Date.now(),
            status: 'active',
            progress: 0,
            assignedVehicles: new Map(),
            materials: new Map(),
            costs: {
                labor: 0,
                materials: 0,
                equipment: 0
            }
        };
        
        this.activeProjects.set(project.id, project);
        this.assignVehiclesToPhase(project);
        
        this.core.uiSystem?.showNotification(
            `Started ${workflow.name} project`, 
            'info'
        );
        
        return project.id;
    }
    
    assignVehiclesToPhase(project) {
        const currentPhase = project.workflow.phases[project.currentPhase];
        if (!currentPhase) return;
        
        // Clear previous assignments
        project.assignedVehicles.clear();
        
        // Assign required vehicles
        for (const vehicleType of currentPhase.vehicles) {
            const vehicle = this.vehicles.get(vehicleType);
            if (vehicle) {
                project.assignedVehicles.set(vehicleType, {
                    ...vehicle,
                    status: 'assigned',
                    location: project.location,
                    workStartTime: Date.now()
                });
            }
        }
        
        console.log(`Phase: ${currentPhase.name} - Assigned vehicles:`, 
                   Array.from(project.assignedVehicles.keys()));
    }
    
    updateProjects(deltaTime) {
        for (const [projectId, project] of this.activeProjects) {
            if (project.status !== 'active') continue;
            
            const currentPhase = project.workflow.phases[project.currentPhase];
            if (!currentPhase) continue;
            
            // Update phase progress
            const elapsed = (Date.now() - project.startTime) / 1000;
            const phaseProgress = Math.min(1, elapsed / currentPhase.duration);
            project.progress = (project.currentPhase + phaseProgress) / project.workflow.phases.length;
            
            // Execute vehicle behaviors
            this.executeVehicleBehaviors(project, currentPhase, deltaTime);
            
            // Check if phase is complete
            if (phaseProgress >= 1) {
                this.completePhase(project);
            }
            
            // Update costs
            this.updateProjectCosts(project, deltaTime);
        }
    }
    
    executeVehicleBehaviors(project, phase, deltaTime) {
        for (const [vehicleType, vehicle] of project.assignedVehicles) {
            const behavior = vehicle.behavior;
            const location = project.location;
            
            switch (phase.name) {
                case 'Site Preparation':
                    if (vehicleType === 'bulldozer') {
                        behavior.clear(location);
                    }
                    break;
                    
                case 'Excavation':
                    if (vehicleType === 'excavator') {
                        behavior.excavate(location.x, location.y, 2.0);
                    }
                    break;
                    
                case 'Base Layer':
                    if (vehicleType === 'dump_truck') {
                        behavior.dump(location, 'gravel');
                    } else if (vehicleType === 'compactor') {
                        behavior.compact(location, 3);
                    }
                    break;
                    
                case 'Surface Layer':
                    if (vehicleType === 'paver') {
                        this.applyAsphalt(location);
                    } else if (vehicleType === 'roller') {
                        behavior.compact(location, 2);
                    }
                    break;
            }
        }
    }
    
    completePhase(project) {
        const currentPhase = project.workflow.phases[project.currentPhase];
        
        this.core.uiSystem?.showNotification(
            `Completed: ${currentPhase.name}`, 
            'success'
        );
        
        // Move to next phase
        project.currentPhase++;
        
        if (project.currentPhase >= project.workflow.phases.length) {
            // Project complete
            project.status = 'completed';
            this.core.uiSystem?.showNotification(
                `Project completed: ${project.workflow.name}`, 
                'success'
            );
        } else {
            // Assign vehicles for next phase
            this.assignVehiclesToPhase(project);
        }
    }
    
    updateProjectCosts(project, deltaTime) {
        for (const [vehicleType, vehicle] of project.assignedVehicles) {
            const hourlyRate = vehicle.operatingCost;
            const cost = (hourlyRate / 3600) * deltaTime; // Cost per second
            project.costs.equipment += cost;
        }
    }
    
    // Vehicle behavior implementations
    excavatorExcavate(x, y, depth) {
        if (!this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        const brushSize = 15;
        const strength = 0.05;
        
        for (let dy = -brushSize; dy <= brushSize; dy++) {
            for (let dx = -brushSize; dx <= brushSize; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx >= 0 && nx < terrain.width && ny >= 0 && ny < terrain.height) {
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= brushSize) {
                        const falloff = 1 - (distance / brushSize);
                        const effect = strength * falloff;
                        const index = ny * terrain.width + nx;
                        
                        terrain.heightMap[index] = Math.max(0, terrain.heightMap[index] - effect);
                        terrain.updateTerrainType(index);
                    }
                }
            }
        }
        
        // Create dust particles
        if (this.core.physicsEngine) {
            for (let i = 0; i < 15; i++) {
                this.core.physicsEngine.spawnParticle({
                    x: x * 4 + (Math.random() - 0.5) * 30,
                    y: y * 4 + (Math.random() - 0.5) * 30,
                    z: 20 + Math.random() * 40,
                    vx: (Math.random() - 0.5) * 40,
                    vy: (Math.random() - 0.5) * 40,
                    vz: Math.random() * 30 + 15,
                    type: 'dust',
                    life: 3.0,
                    size: 2 + Math.random() * 4,
                    color: [139, 119, 101, 0.7]
                });
            }
        }
    }
    
    bulldozerClear(area) {
        if (!this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        const targetHeight = 0.4; // Target level for cleared area
        const smoothingStrength = 0.03;
        
        const minX = Math.max(0, area.x - area.radius);
        const maxX = Math.min(terrain.width - 1, area.x + area.radius);
        const minY = Math.max(0, area.y - area.radius);
        const maxY = Math.min(terrain.height - 1, area.y + area.radius);
        
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                const index = y * terrain.width + x;
                const currentHeight = terrain.heightMap[index];
                
                // Gradually move towards target height
                const diff = targetHeight - currentHeight;
                terrain.heightMap[index] += diff * smoothingStrength;
                terrain.updateTerrainType(index);
            }
        }
    }
    
    dumpTruckDump(location, materialType) {
        if (!this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        const material = this.materials.get(materialType);
        const dumpRadius = 12;
        const heightIncrease = 0.08;
        
        for (let dy = -dumpRadius; dy <= dumpRadius; dy++) {
            for (let dx = -dumpRadius; dx <= dumpRadius; dx++) {
                const nx = location.x + dx;
                const ny = location.y + dy;
                
                if (nx >= 0 && nx < terrain.width && ny >= 0 && ny < terrain.height) {
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= dumpRadius) {
                        const falloff = 1 - (distance / dumpRadius);
                        const effect = heightIncrease * falloff;
                        const index = ny * terrain.width + nx;
                        
                        terrain.heightMap[index] += effect;
                        
                        // Set terrain type based on material
                        if (materialType === 'gravel') {
                            terrain.terrainTypes[index] = 4; // rock
                        } else if (materialType === 'concrete') {
                            terrain.terrainTypes[index] = 4; // rock
                        }
                    }
                }
            }
        }
    }
    
    getProjectStatus(projectId) {
        const project = this.activeProjects.get(projectId);
        if (!project) return null;
        
        const currentPhase = project.workflow.phases[project.currentPhase];
        
        return {
            id: project.id,
            type: project.type,
            status: project.status,
            progress: project.progress,
            currentPhase: currentPhase?.name || 'Complete',
            costs: project.costs,
            assignedVehicles: Array.from(project.assignedVehicles.keys())
        };
    }
    
    getAllProjectStatuses() {
        const statuses = [];
        for (const [projectId] of this.activeProjects) {
            statuses.push(this.getProjectStatus(projectId));
        }
        return statuses;
    }
}
