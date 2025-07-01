/**
 * Multi-Layer Construction System
 * Proper construction layering with material sequencing and structural integrity
 */

class MultiLayerConstruction {
    constructor(core) {
        this.core = core;
        this.layers = new Map(); // location -> layer stack
        this.constructionTypes = new Map();
        this.layerStandards = new Map();
        this.activeConstruction = null;
        
        this.initializeConstructionTypes();
        this.initializeLayerStandards();
    }
    
    initializeConstructionTypes() {
        // Road Construction Layers
        this.constructionTypes.set('highway', {
            name: 'Highway Construction',
            category: 'transportation',
            layers: [
                {
                    name: 'Subgrade',
                    material: 'compacted_soil',
                    thickness: { min: 0.3, max: 1.0, typical: 0.6 },
                    compaction: 0.95,
                    requirements: ['bearing_capacity', 'moisture_control'],
                    function: 'foundation_support'
                },
                {
                    name: 'Subbase',
                    material: 'granular_material',
                    thickness: { min: 0.15, max: 0.4, typical: 0.25 },
                    compaction: 0.98,
                    requirements: ['gradation', 'plasticity_index'],
                    function: 'load_distribution'
                },
                {
                    name: 'Base Course',
                    material: 'crushed_aggregate',
                    thickness: { min: 0.2, max: 0.5, typical: 0.3 },
                    compaction: 0.98,
                    requirements: ['CBR_value', 'gradation'],
                    function: 'primary_load_bearing'
                },
                {
                    name: 'Binder Course',
                    material: 'asphalt_binder',
                    thickness: { min: 0.05, max: 0.15, typical: 0.1 },
                    compaction: 0.96,
                    requirements: ['temperature', 'density'],
                    function: 'intermediate_layer'
                },
                {
                    name: 'Surface Course',
                    material: 'asphalt_surface',
                    thickness: { min: 0.04, max: 0.1, typical: 0.06 },
                    compaction: 0.96,
                    requirements: ['smoothness', 'texture'],
                    function: 'wearing_surface'
                }
            ],
            specifications: {
                totalThickness: { min: 0.74, max: 2.15 },
                designLife: 20, // years
                trafficLoad: 'heavy',
                drainageRequired: true
            }
        });
        
        // Building Foundation Layers
        this.constructionTypes.set('building_foundation', {
            name: 'Building Foundation',
            category: 'structural',
            layers: [
                {
                    name: 'Excavation',
                    material: 'void',
                    thickness: { min: 1.0, max: 5.0, typical: 2.0 },
                    compaction: 0,
                    requirements: ['soil_classification', 'groundwater_control'],
                    function: 'preparation'
                },
                {
                    name: 'Lean Concrete',
                    material: 'lean_concrete',
                    thickness: { min: 0.05, max: 0.15, typical: 0.1 },
                    compaction: 1.0,
                    requirements: ['level_surface', 'curing'],
                    function: 'working_platform'
                },
                {
                    name: 'Footing',
                    material: 'structural_concrete',
                    thickness: { min: 0.3, max: 1.5, typical: 0.6 },
                    compaction: 1.0,
                    requirements: ['reinforcement', 'concrete_strength'],
                    function: 'load_transfer'
                },
                {
                    name: 'Foundation Wall',
                    material: 'reinforced_concrete',
                    thickness: { min: 0.2, max: 0.5, typical: 0.3 },
                    compaction: 1.0,
                    requirements: ['waterproofing', 'reinforcement'],
                    function: 'vertical_support'
                },
                {
                    name: 'Backfill',
                    material: 'select_fill',
                    thickness: { min: 0.5, max: 3.0, typical: 1.5 },
                    compaction: 0.95,
                    requirements: ['drainage', 'compaction'],
                    function: 'lateral_support'
                }
            ],
            specifications: {
                bearingCapacity: { min: 200, typical: 300 }, // kPa
                designLife: 50, // years
                waterproofing: true,
                thermalProtection: true
            }
        });
        
        // Retaining Wall Layers
        this.constructionTypes.set('retaining_wall', {
            name: 'Retaining Wall',
            category: 'geotechnical',
            layers: [
                {
                    name: 'Foundation Excavation',
                    material: 'void',
                    thickness: { min: 0.8, max: 2.0, typical: 1.2 },
                    compaction: 0,
                    requirements: ['bearing_capacity', 'frost_depth'],
                    function: 'foundation_preparation'
                },
                {
                    name: 'Foundation Concrete',
                    material: 'mass_concrete',
                    thickness: { min: 0.4, max: 1.0, typical: 0.6 },
                    compaction: 1.0,
                    requirements: ['concrete_strength', 'reinforcement'],
                    function: 'foundation_base'
                },
                {
                    name: 'Wall Stem',
                    material: 'reinforced_concrete',
                    thickness: { min: 0.2, max: 0.8, typical: 0.4 },
                    compaction: 1.0,
                    requirements: ['reinforcement_design', 'concrete_cover'],
                    function: 'retaining_structure'
                },
                {
                    name: 'Drainage Layer',
                    material: 'granular_drainage',
                    thickness: { min: 0.3, max: 0.6, typical: 0.4 },
                    compaction: 0.85,
                    requirements: ['permeability', 'gradation'],
                    function: 'hydrostatic_relief'
                },
                {
                    name: 'Backfill',
                    material: 'engineered_fill',
                    thickness: { min: 1.0, max: 8.0, typical: 3.0 },
                    compaction: 0.95,
                    requirements: ['friction_angle', 'compaction'],
                    function: 'retained_material'
                }
            ],
            specifications: {
                stabilityFactor: { min: 1.5, typical: 2.0 },
                drainageCapacity: 'adequate',
                designLife: 75 // years
            }
        });
    }
    
    initializeLayerStandards() {
        // AASHTO Standards
        this.layerStandards.set('subgrade_compaction', {
            standard: 'AASHTO T99',
            requirement: 'minimum_95_percent',
            testMethod: 'standard_proctor',
            frequency: 'every_150_cubic_meters'
        });
        
        this.layerStandards.set('base_course_CBR', {
            standard: 'AASHTO T193',
            requirement: 'minimum_80_CBR',
            testMethod: 'california_bearing_ratio',
            frequency: 'every_source_change'
        });
        
        this.layerStandards.set('concrete_strength', {
            standard: 'ASTM C39',
            requirement: 'design_strength_28_days',
            testMethod: 'compression_test',
            frequency: 'every_100_cubic_meters'
        });
    }
    
    startLayeredConstruction(type, location, parameters = {}) {
        const constructionType = this.constructionTypes.get(type);
        if (!constructionType) {
            console.error(`Unknown construction type: ${type}`);
            return null;
        }
        
        const construction = {
            id: Date.now(),
            type: type,
            definition: constructionType,
            location: location,
            parameters: { ...constructionType.specifications, ...parameters },
            currentLayer: 0,
            completedLayers: [],
            status: 'planning',
            qualityControl: new Map(),
            costs: {
                materials: 0,
                labor: 0,
                equipment: 0,
                testing: 0
            },
            schedule: {
                startDate: new Date(),
                estimatedCompletion: null,
                actualCompletion: null
            }
        };
        
        this.activeConstruction = construction;
        
        this.core.uiSystem?.showNotification(
            `Started ${constructionType.name} construction`,
            'info'
        );
        
        return construction.id;
    }
    
    placeLayer(constructionId, layerIndex, customThickness = null) {
        const construction = this.activeConstruction;
        if (!construction || construction.id !== constructionId) {
            console.error('Construction not found or not active');
            return false;
        }
        
        const layerDef = construction.definition.layers[layerIndex];
        if (!layerDef) {
            console.error('Layer definition not found');
            return false;
        }
        
        // Check prerequisites
        if (!this.checkLayerPrerequisites(construction, layerIndex)) {
            return false;
        }
        
        // Determine layer thickness
        const thickness = customThickness || layerDef.thickness.typical;
        
        // Validate thickness
        if (thickness < layerDef.thickness.min || thickness > layerDef.thickness.max) {
            this.core.uiSystem?.showNotification(
                `Layer thickness out of range: ${thickness}m (${layerDef.thickness.min}-${layerDef.thickness.max}m)`,
                'warning'
            );
            return false;
        }
        
        // Place the layer
        const layerResult = this.executeLayerPlacement(construction, layerDef, thickness);
        
        if (layerResult.success) {
            // Record completed layer
            construction.completedLayers.push({
                index: layerIndex,
                definition: layerDef,
                thickness: thickness,
                placementDate: new Date(),
                qualityResults: layerResult.qualityResults,
                cost: layerResult.cost
            });
            
            construction.currentLayer = layerIndex + 1;
            
            // Update costs
            construction.costs.materials += layerResult.cost.materials;
            construction.costs.labor += layerResult.cost.labor;
            construction.costs.equipment += layerResult.cost.equipment;
            
            // Check if construction is complete
            if (construction.currentLayer >= construction.definition.layers.length) {
                construction.status = 'completed';
                construction.schedule.actualCompletion = new Date();
                
                this.core.uiSystem?.showNotification(
                    `Construction completed: ${construction.definition.name}`,
                    'success'
                );
            } else {
                this.core.uiSystem?.showNotification(
                    `Layer completed: ${layerDef.name}`,
                    'success'
                );
            }
            
            return true;
        }
        
        return false;
    }
    
    checkLayerPrerequisites(construction, layerIndex) {
        // Check if previous layers are completed
        if (layerIndex > 0 && construction.currentLayer < layerIndex) {
            this.core.uiSystem?.showNotification(
                'Previous layers must be completed first',
                'warning'
            );
            return false;
        }
        
        // Check material availability
        const layerDef = construction.definition.layers[layerIndex];
        if (!this.isMaterialAvailable(layerDef.material)) {
            this.core.uiSystem?.showNotification(
                `Material not available: ${layerDef.material}`,
                'warning'
            );
            return false;
        }
        
        // Check environmental conditions
        if (!this.checkEnvironmentalConditions(layerDef)) {
            this.core.uiSystem?.showNotification(
                'Environmental conditions not suitable',
                'warning'
            );
            return false;
        }
        
        return true;
    }
    
    executeLayerPlacement(construction, layerDef, thickness) {
        const location = construction.location;
        const result = {
            success: false,
            qualityResults: {},
            cost: { materials: 0, labor: 0, equipment: 0 }
        };
        
        try {
            // Place material based on layer type
            switch (layerDef.function) {
                case 'preparation':
                    this.performExcavation(location, thickness);
                    break;
                    
                case 'foundation_support':
                case 'load_distribution':
                case 'primary_load_bearing':
                    this.placeGranularLayer(location, layerDef.material, thickness, layerDef.compaction);
                    break;
                    
                case 'wearing_surface':
                case 'intermediate_layer':
                    this.placeAsphaltLayer(location, layerDef.material, thickness, layerDef.compaction);
                    break;
                    
                case 'load_transfer':
                case 'vertical_support':
                case 'retaining_structure':
                    this.placeConcreteLayer(location, layerDef.material, thickness);
                    break;
                    
                case 'lateral_support':
                case 'retained_material':
                    this.placeBackfillLayer(location, layerDef.material, thickness, layerDef.compaction);
                    break;
                    
                case 'hydrostatic_relief':
                    this.placeDrainageLayer(location, layerDef.material, thickness);
                    break;
                    
                default:
                    this.placeGenericLayer(location, layerDef.material, thickness);
            }
            
            // Perform quality control tests
            result.qualityResults = this.performQualityControl(layerDef, thickness);
            
            // Calculate costs
            result.cost = this.calculateLayerCost(layerDef, thickness, location);
            
            // Update layer registry
            this.updateLayerRegistry(location, layerDef, thickness);
            
            result.success = true;
            
        } catch (error) {
            console.error('Layer placement failed:', error);
            result.success = false;
        }
        
        return result;
    }
    
    placeGranularLayer(location, material, thickness, compaction) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial(material, location.x, location.y, thickness, compaction);
        }
        
        // Simulate compaction process
        this.simulateCompaction(location, compaction);
    }
    
    placeAsphaltLayer(location, material, thickness, compaction) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('asphalt', location.x, location.y, thickness, compaction);
        }
        
        // Create paving effects
        this.createPavingEffects(location, thickness);
    }
    
    placeConcreteLayer(location, material, thickness) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('concrete', location.x, location.y, thickness, 1.0);
        }
        
        // Simulate concrete pour
        this.simulateConcretePour(location, thickness);
    }
    
    placeBackfillLayer(location, material, thickness, compaction) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('soil', location.x, location.y, thickness, compaction);
        }
        
        // Simulate backfill placement in lifts
        this.simulateBackfillLifts(location, thickness, compaction);
    }
    
    placeDrainageLayer(location, material, thickness) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('gravel', location.x, location.y, thickness, 0.85);
        }
        
        // Install drainage pipes
        this.installDrainagePipes(location);
    }
    
    performExcavation(location, depth) {
        if (this.core.terrainEngine) {
            const terrain = this.core.terrainEngine;
            const radius = 20;
            const excavationDepth = depth * 0.1; // Scale for visualization
            
            for (let dy = -radius; dy <= radius; dy++) {
                for (let dx = -radius; dx <= radius; dx++) {
                    const nx = location.x + dx;
                    const ny = location.y + dy;
                    
                    if (nx >= 0 && nx < terrain.width && ny >= 0 && ny < terrain.height) {
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        if (distance <= radius) {
                            const index = ny * terrain.width + nx;
                            const falloff = 1 - (distance / radius);
                            const effect = excavationDepth * falloff;
                            
                            terrain.heightMap[index] = Math.max(0, terrain.heightMap[index] - effect);
                            terrain.updateTerrainType(index);
                        }
                    }
                }
            }
        }
    }
    
    simulateCompaction(location, targetCompaction) {
        // Create compaction effects
        if (this.core.physicsEngine) {
            for (let i = 0; i < 5; i++) {
                this.core.physicsEngine.spawnParticle({
                    x: location.x * 4 + (Math.random() - 0.5) * 20,
                    y: location.y * 4 + (Math.random() - 0.5) * 20,
                    z: 10 + Math.random() * 20,
                    vx: (Math.random() - 0.5) * 20,
                    vy: (Math.random() - 0.5) * 20,
                    vz: Math.random() * 15 + 5,
                    type: 'dust',
                    life: 2.0,
                    size: 1 + Math.random() * 2,
                    color: [139, 119, 101, 0.4]
                });
            }
        }
    }
    
    createPavingEffects(location, thickness) {
        // Create steam/heat effects for asphalt paving
        if (this.core.physicsEngine) {
            for (let i = 0; i < 8; i++) {
                this.core.physicsEngine.spawnParticle({
                    x: location.x * 4 + (Math.random() - 0.5) * 30,
                    y: location.y * 4 + (Math.random() - 0.5) * 30,
                    z: 5 + Math.random() * 15,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    vz: Math.random() * 20 + 10,
                    type: 'steam',
                    life: 3.0,
                    size: 2 + Math.random() * 4,
                    color: [255, 255, 255, 0.6]
                });
            }
        }
    }
    
    simulateConcretePour(location, thickness) {
        // Create concrete pour effects
        if (this.core.physicsEngine) {
            for (let i = 0; i < 12; i++) {
                this.core.physicsEngine.spawnParticle({
                    x: location.x * 4 + (Math.random() - 0.5) * 25,
                    y: location.y * 4 + (Math.random() - 0.5) * 25,
                    z: 20 + Math.random() * 30,
                    vx: (Math.random() - 0.5) * 15,
                    vy: (Math.random() - 0.5) * 15,
                    vz: Math.random() * 10,
                    type: 'splash',
                    life: 1.5,
                    size: 2 + Math.random() * 3,
                    color: [200, 200, 200, 0.8]
                });
            }
        }
    }
    
    performQualityControl(layerDef, thickness) {
        const results = {};
        
        // Thickness test
        const measuredThickness = thickness * (0.95 + Math.random() * 0.1);
        results.thickness = {
            measured: measuredThickness,
            target: thickness,
            tolerance: thickness * 0.05,
            passed: Math.abs(measuredThickness - thickness) <= thickness * 0.05
        };
        
        // Compaction test (if applicable)
        if (layerDef.compaction > 0) {
            const measuredCompaction = layerDef.compaction * (0.92 + Math.random() * 0.1);
            results.compaction = {
                measured: measuredCompaction,
                target: layerDef.compaction,
                passed: measuredCompaction >= layerDef.compaction * 0.95
            };
        }
        
        // Material quality test
        results.materialQuality = {
            grade: 'A',
            passed: Math.random() > 0.1 // 90% pass rate
        };
        
        return results;
    }
    
    calculateLayerCost(layerDef, thickness, location) {
        const area = Math.PI * 20 * 20; // Approximate area
        const volume = area * thickness;
        
        // Material costs ($/m³)
        const materialCosts = {
            'compacted_soil': 15,
            'granular_material': 25,
            'crushed_aggregate': 35,
            'asphalt_binder': 80,
            'asphalt_surface': 90,
            'lean_concrete': 100,
            'structural_concrete': 150,
            'reinforced_concrete': 200,
            'select_fill': 20,
            'engineered_fill': 30,
            'granular_drainage': 40
        };
        
        const materialCost = (materialCosts[layerDef.material] || 50) * volume;
        const laborCost = materialCost * 0.3; // 30% of material cost
        const equipmentCost = materialCost * 0.2; // 20% of material cost
        
        return {
            materials: materialCost,
            labor: laborCost,
            equipment: equipmentCost
        };
    }
    
    updateLayerRegistry(location, layerDef, thickness) {
        const key = `${location.x}_${location.y}`;
        
        if (!this.layers.has(key)) {
            this.layers.set(key, []);
        }
        
        const layerStack = this.layers.get(key);
        layerStack.push({
            material: layerDef.material,
            thickness: thickness,
            compaction: layerDef.compaction,
            function: layerDef.function,
            placementDate: new Date()
        });
    }
    
    getLayerStack(x, y) {
        const key = `${x}_${y}`;
        return this.layers.get(key) || [];
    }
    
    getConstructionProgress(constructionId) {
        const construction = this.activeConstruction;
        if (!construction || construction.id !== constructionId) return null;
        
        const totalLayers = construction.definition.layers.length;
        const completedLayers = construction.completedLayers.length;
        const progress = completedLayers / totalLayers;
        
        return {
            id: constructionId,
            type: construction.type,
            progress: progress,
            currentLayer: construction.currentLayer,
            totalLayers: totalLayers,
            status: construction.status,
            costs: construction.costs,
            nextLayer: construction.definition.layers[construction.currentLayer]?.name || 'Complete'
        };
    }
    
    // Helper methods
    isMaterialAvailable(material) {
        return Math.random() > 0.05; // 95% availability
    }
    
    checkEnvironmentalConditions(layerDef) {
        // Check weather, temperature, etc.
        return Math.random() > 0.1; // 90% suitable conditions
    }
    
    simulateBackfillLifts(location, totalThickness, compaction) {
        const liftThickness = 0.3; // 30cm lifts
        const numLifts = Math.ceil(totalThickness / liftThickness);
        
        console.log(`Placing backfill in ${numLifts} lifts of ${liftThickness}m each`);
    }
    
    installDrainagePipes(location) {
        console.log(`Installing drainage pipes at location (${location.x}, ${location.y})`);
    }
    
    placeGenericLayer(location, material, thickness) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial(material, location.x, location.y, thickness, 0.9);
        }
    }
}
