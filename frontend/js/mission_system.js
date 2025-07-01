/**
 * Advanced Mission System - Multiple game modes for RC Sandbox
 * Part of the RC Sandbox modular architecture
 */

class Mission {
    constructor(id, name, type, description, objectives, timeLimit = null) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.description = description;
        this.objectives = objectives;
        this.timeLimit = timeLimit;
        this.startTime = null;
        this.endTime = null;
        this.status = 'not_started'; // not_started, active, completed, failed
        this.score = 0;
        this.completedObjectives = new Set();
        this.events = [];
    }
    
    start() {
        this.status = 'active';
        this.startTime = Date.now();
        this.events.push({ type: 'mission_started', timestamp: this.startTime });
        console.log(`🎯 Mission started: ${this.name}`);
    }
    
    complete() {
        this.status = 'completed';
        this.endTime = Date.now();
        this.events.push({ type: 'mission_completed', timestamp: this.endTime });
        console.log(`✅ Mission completed: ${this.name} (Score: ${this.score})`);
    }
    
    fail(reason = 'Unknown') {
        this.status = 'failed';
        this.endTime = Date.now();
        this.events.push({ type: 'mission_failed', timestamp: this.endTime, reason });
        console.log(`❌ Mission failed: ${this.name} - ${reason}`);
    }
    
    completeObjective(objectiveId) {
        if (this.objectives[objectiveId] && !this.completedObjectives.has(objectiveId)) {
            this.completedObjectives.add(objectiveId);
            this.score += this.objectives[objectiveId].points || 100;
            this.events.push({ 
                type: 'objective_completed', 
                timestamp: Date.now(), 
                objectiveId 
            });
            console.log(`🎯 Objective completed: ${this.objectives[objectiveId].name}`);
            
            // Check if all objectives are complete
            if (this.completedObjectives.size === Object.keys(this.objectives).length) {
                this.complete();
            }
        }
    }
    
    getProgress() {
        const totalObjectives = Object.keys(this.objectives).length;
        const completedCount = this.completedObjectives.size;
        return {
            completed: completedCount,
            total: totalObjectives,
            percentage: (completedCount / totalObjectives) * 100
        };
    }
    
    getRemainingTime() {
        if (!this.timeLimit || !this.startTime) return null;
        const elapsed = Date.now() - this.startTime;
        return Math.max(0, this.timeLimit - elapsed);
    }
    
    isExpired() {
        const remaining = this.getRemainingTime();
        return remaining !== null && remaining <= 0;
    }
}

class MissionSystem {
    constructor(terrainEngine, vehicleFleet, uiController) {
        this.terrainEngine = terrainEngine;
        this.vehicleFleet = vehicleFleet;
        this.uiController = uiController;
        
        this.currentMission = null;
        this.availableMissions = new Map();
        this.completedMissions = [];
        this.missionHistory = [];
        
        // Mission state
        this.checkpoints = [];
        this.raceTimer = null;
        this.constructionProgress = {};
        
        this.initializeMissions();
        
        console.log('🎮 Advanced Mission System initialized');
    }
    
    initializeMissions() {
        // Flood Defense Mission
        this.addMission(new Mission(
            'flood_defense',
            'Flood Defense Emergency',
            'emergency',
            'Build defensive barriers before the flood arrives! Use excavators to dig moats and bulldozers to build walls.',
            {
                dig_moats: { name: 'Dig defensive moats', points: 200, required: true },
                build_walls: { name: 'Build protective walls', points: 150, required: true },
                evacuate_area: { name: 'Clear evacuation routes', points: 100, required: false }
            },
            180000 // 3 minutes
        ));
        
        // Highway Construction Mission
        this.addMission(new Mission(
            'highway_construction',
            'Highway Construction Contract',
            'construction',
            'Build a highway system according to specifications. Follow the blueprint exactly for maximum points.',
            {
                level_ground: { name: 'Level construction area', points: 150, required: true },
                build_foundation: { name: 'Build road foundation', points: 200, required: true },
                create_lanes: { name: 'Create traffic lanes', points: 100, required: true },
                add_shoulders: { name: 'Add road shoulders', points: 75, required: false },
                install_drainage: { name: 'Install drainage system', points: 125, required: false }
            },
            300000 // 5 minutes
        ));
        
        // Waste Sorting Challenge Mission
        this.addMission(new Mission(
            'waste_sorting',
            'Waste Sorting & Recycling',
            'logistics',
            'Sort and transport different materials to their proper recycling centers. Efficiency is key!',
            {
                collect_metal: { name: 'Collect metal scraps', points: 100, required: true },
                collect_plastic: { name: 'Collect plastic waste', points: 100, required: true },
                collect_organic: { name: 'Collect organic matter', points: 100, required: true },
                sort_materials: { name: 'Sort materials correctly', points: 150, required: true },
                transport_efficiently: { name: 'Minimize transport trips', points: 200, required: false }
            },
            240000 // 4 minutes
        ));
        
        // Vehicle Racing Mission
        this.addMission(new Mission(
            'vehicle_racing',
            'Construction Vehicle Grand Prix',
            'racing',
            'Navigate the obstacle course as fast as possible! Each vehicle class has different challenges.',
            {
                complete_course: { name: 'Complete the racing circuit', points: 300, required: true },
                hit_checkpoints: { name: 'Hit all checkpoints in order', points: 150, required: true },
                avoid_obstacles: { name: 'Avoid penalty obstacles', points: 100, required: false },
                speed_bonus: { name: 'Finish under time limit', points: 200, required: false }
            },
            120000 // 2 minutes
        ));
        
        // Creative Sandbox Mission
        this.addMission(new Mission(
            'creative_sandbox',
            'Creative Sandbox Mode',
            'creative',
            'Build whatever you can imagine! No time limits, no restrictions. Let your creativity flow.',
            {
                explore_tools: { name: 'Try different vehicle types', points: 50, required: false },
                create_landscape: { name: 'Modify the terrain', points: 100, required: false },
                build_structures: { name: 'Create interesting structures', points: 150, required: false },
                experiment: { name: 'Experiment with features', points: 100, required: false }
            }
        ));
        
        console.log(`📋 Initialized ${this.availableMissions.size} mission types`);
    }
    
    addMission(mission) {
        this.availableMissions.set(mission.id, mission);
    }
    
    startMission(missionId) {
        const missionTemplate = this.availableMissions.get(missionId);
        if (!missionTemplate) {
            console.error(`Mission not found: ${missionId}`);
            return false;
        }
        
        // Create a new instance of the mission
        this.currentMission = new Mission(
            missionTemplate.id,
            missionTemplate.name,
            missionTemplate.type,
            missionTemplate.description,
            { ...missionTemplate.objectives },
            missionTemplate.timeLimit
        );
        
        this.currentMission.start();
        this.setupMissionEnvironment(missionId);
        
        // Notify UI
        if (this.uiController) {
            this.uiController.showNotification(`🎯 Mission Started: ${this.currentMission.name}`, 'info');
        }
        
        return true;
    }
    
    setupMissionEnvironment(missionId) {
        switch (missionId) {
            case 'flood_defense':
                this.setupFloodDefense();
                break;
            case 'construction_contract':
                this.setupConstructionContract();
                break;
            case 'recycling_challenge':
                this.setupRecyclingChallenge();
                break;
            case 'racing_circuit':
                this.setupRacingCircuit();
                break;
            case 'free_play':
                this.setupFreePlay();
                break;
        }
    }
    
    setupFloodDefense() {
        console.log('🌊 Setting up Flood Defense scenario...');
        
        // Create flood-prone areas
        if (this.terrainEngine) {
            // Create low-lying areas that need protection
            this.createFloodZones();
            
            // Pre-dig some moat locations
            this.createMoatTemplates();
            
            // Set water level higher
            this.terrainEngine.setWaterLevel(0.3);
        }
        
        // Configure vehicles for flood defense
        if (this.vehicleFleet) {
            this.vehicleFleet.startFloodDefenseMission();
        }
    }
    
    setupConstructionContract() {
        console.log('🏗️ Setting up Construction Contract...');
        
        // Create construction blueprint overlay
        this.createConstructionBlueprint();
        
        // Level some areas for construction
        if (this.terrainEngine) {
            this.prepareConstructionSite();
        }
    }
    
    setupRecyclingChallenge() {
        console.log('♻️ Setting up Recycling Challenge...');
        
        // Place recycling materials around the map
        this.placeMaterials();
        
        // Create recycling centers
        this.createRecyclingCenters();
    }
    
    setupRacingCircuit() {
        console.log('🏁 Setting up Racing Circuit...');
        
        // Create race track
        this.createRaceTrack();
        
        // Place checkpoints
        this.createCheckpoints();
        
        // Add obstacles
        this.createRaceObstacles();
    }
    
    setupFreePlay() {
        console.log('🎨 Setting up Free Play mode...');
        
        // Enable all tools and features
        if (this.uiController) {
            this.uiController.showNotification('🎨 Free Play Mode: All tools unlocked!', 'info');
        }
        
        // Generate interesting starting terrain
        if (this.terrainEngine) {
            this.terrainEngine.generateRealisticTerrain();
        }
    }
    
    createFloodZones() {
        // Create vulnerable low areas
        const zones = [
            { x: 30, y: 20, radius: 15, depth: -0.4 },
            { x: 70, y: 50, radius: 20, depth: -0.3 },
            { x: 20, y: 60, radius: 12, depth: -0.5 }
        ];
        
        zones.forEach(zone => {
            for (let dy = -zone.radius; dy <= zone.radius; dy++) {
                for (let dx = -zone.radius; dx <= zone.radius; dx++) {
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= zone.radius) {
                        const gridX = zone.x + dx;
                        const gridY = zone.y + dy;
                        
                        if (gridX >= 0 && gridX < this.terrainEngine.gridWidth && 
                            gridY >= 0 && gridY < this.terrainEngine.gridHeight) {
                            
                            const index = gridY * this.terrainEngine.gridWidth + gridX;
                            const falloff = 1 - (distance / zone.radius);
                            this.terrainEngine.heightmap[index] += zone.depth * falloff;
                        }
                    }
                }
            }
        });
    }
    
    createMoatTemplates() {
        // Create suggested moat locations
        this.moatTemplates = [
            { x: 25, y: 15, width: 20, height: 5 },
            { x: 60, y: 40, width: 25, height: 8 },
            { x: 15, y: 55, width: 15, height: 6 }
        ];
    }
    
    createConstructionBlueprint() {
        // Define highway blueprint
        this.constructionBlueprint = {
            mainRoad: { startX: 10, startY: 30, endX: 90, endY: 30, width: 8 },
            onRamp: { startX: 30, startY: 10, endX: 30, endY: 30, width: 6 },
            offRamp: { startX: 60, startY: 30, endX: 60, endY: 50, width: 6 }
        };
    }
    
    prepareConstructionSite() {
        // Level the construction area
        const blueprint = this.constructionBlueprint;
        
        // Level main road area
        this.levelArea(blueprint.mainRoad.startX, blueprint.mainRoad.startY - 4,
                     blueprint.mainRoad.endX, blueprint.mainRoad.endY + 4, 0.5);
    }
    
    levelArea(x1, y1, x2, y2, targetHeight) {
        for (let y = Math.floor(y1); y <= Math.ceil(y2); y++) {
            for (let x = Math.floor(x1); x <= Math.ceil(x2); x++) {
                if (x >= 0 && x < this.terrainEngine.gridWidth && 
                    y >= 0 && y < this.terrainEngine.gridHeight) {
                    
                    const index = y * this.terrainEngine.gridWidth + x;
                    this.terrainEngine.heightmap[index] = targetHeight;
                }
            }
        }
    }
    
    placeMaterials() {
        // Place different types of recyclable materials
        this.materials = [
            { type: 'metal', x: 20, y: 20, collected: false },
            { type: 'plastic', x: 40, y: 30, collected: false },
            { type: 'organic', x: 60, y: 40, collected: false },
            { type: 'metal', x: 80, y: 20, collected: false },
            { type: 'plastic', x: 30, y: 60, collected: false },
            { type: 'organic', x: 70, y: 60, collected: false }
        ];
    }
    
    createRecyclingCenters() {
        // Create recycling center locations
        this.recyclingCenters = [
            { type: 'metal', x: 10, y: 10, name: 'Metal Recycling' },
            { type: 'plastic', x: 90, y: 10, name: 'Plastic Processing' },
            { type: 'organic', x: 50, y: 70, name: 'Composting Center' }
        ];
    }
    
    createRaceTrack() {
        // Create a racing circuit with elevation changes
        this.raceTrack = {
            startLine: { x: 20, y: 30 },
            track: [
                { x: 20, y: 30 }, { x: 40, y: 20 }, { x: 60, y: 25 },
                { x: 80, y: 35 }, { x: 75, y: 55 }, { x: 50, y: 60 },
                { x: 25, y: 50 }, { x: 20, y: 30 }
            ]
        };
    }
    
    createCheckpoints() {
        // Place checkpoints along the race track
        this.checkpoints = [
            { id: 1, x: 40, y: 20, passed: false },
            { id: 2, x: 80, y: 35, passed: false },
            { id: 3, x: 50, y: 60, passed: false },
            { id: 4, x: 25, y: 50, passed: false }
        ];
    }
    
    createRaceObstacles() {
        // Add obstacles to make racing more challenging
        this.raceObstacles = [
            { x: 35, y: 25, type: 'barrier' },
            { x: 65, y: 40, type: 'cone' },
            { x: 45, y: 55, type: 'barrier' }
        ];
    }
    
    update() {
        if (!this.currentMission || this.currentMission.status !== 'active') return;
        
        // Check for mission timeout
        if (this.currentMission.isExpired()) {
            this.currentMission.fail('Time limit exceeded');
            this.endMission();
            return;
        }
        
        // Update mission-specific logic
        switch (this.currentMission.type) {
            case 'emergency':
                this.updateFloodDefense();
                break;
            case 'construction':
                this.updateConstructionContract();
                break;
            case 'logistics':
                this.updateRecyclingChallenge();
                break;
            case 'racing':
                this.updateRacingCircuit();
                break;
            case 'creative':
                this.updateFreePlay();
                break;
        }
    }
    
    updateFloodDefense() {
        // Check if moats are being dug
        // Check if walls are being built
        // Monitor flood timer
    }
    
    updateConstructionContract() {
        // Check construction progress against blueprint
        // Verify road specifications
    }
    
    updateRecyclingChallenge() {
        // Check material collection
        // Verify sorting accuracy
    }
    
    updateRacingCircuit() {
        // Check checkpoint progress
        // Monitor lap times
    }
    
    updateFreePlay() {
        // Track creative achievements
        // No failure conditions
    }
    
    endMission() {
        if (this.currentMission) {
            this.missionHistory.push(this.currentMission);
            
            if (this.currentMission.status === 'completed') {
                this.completedMissions.push(this.currentMission);
            }
            
            // Notify UI
            if (this.uiController) {
                const message = this.currentMission.status === 'completed' 
                    ? `✅ Mission Complete! Score: ${this.currentMission.score}`
                    : `❌ Mission Failed`;
                this.uiController.showNotification(message, 
                    this.currentMission.status === 'completed' ? 'info' : 'error');
            }
            
            this.currentMission = null;
        }
    }
    
    getCurrentMission() {
        return this.currentMission;
    }
    
    getAvailableMissions() {
        return Array.from(this.availableMissions.values());
    }
    
    getMissionProgress() {
        return this.currentMission ? this.currentMission.getProgress() : null;
    }
    
    completeObjective(objectiveId) {
        if (this.currentMission) {
            this.currentMission.completeObjective(objectiveId);
        }
    }
}

// Export for use in other modules
window.Mission = Mission;
window.MissionSystem = MissionSystem;
