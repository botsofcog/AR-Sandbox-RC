/**
 * Advanced Terrain Materials System
 * Realistic construction materials with proper physics and applications
 */

class AdvancedTerrainMaterials {
    constructor(core) {
        this.core = core;
        this.materials = new Map();
        this.materialLayers = new Map();
        this.materialProperties = new Map();
        this.weatherEffects = new Map();
        
        this.initializeMaterials();
        this.initializeWeatherEffects();
    }
    
    initializeMaterials() {
        // Concrete - Foundation and structural material
        this.materials.set('concrete', {
            id: 'concrete',
            name: 'Concrete',
            category: 'structural',
            color: [200, 200, 200],
            density: 2400, // kg/m³
            compressiveStrength: 30, // MPa
            cost: 120, // $/m³
            cureTime: 2880, // minutes (48 hours)
            permeability: 0.01, // very low
            thermalConductivity: 1.7,
            durability: 0.95,
            workability: 0.7,
            properties: {
                loadBearing: true,
                waterResistant: true,
                fireResistant: true,
                frostResistant: false,
                chemicalResistant: true
            },
            applications: ['foundations', 'structures', 'pavements', 'retaining_walls'],
            mixDesign: {
                cement: 0.15,
                sand: 0.25,
                gravel: 0.45,
                water: 0.15
            }
        });
        
        // Asphalt - Road surface material
        this.materials.set('asphalt', {
            id: 'asphalt',
            name: 'Asphalt',
            category: 'paving',
            color: [64, 64, 64],
            density: 2300,
            cost: 80,
            cureTime: 60, // minutes
            permeability: 0.05,
            thermalConductivity: 0.75,
            durability: 0.85,
            workability: 0.9,
            properties: {
                loadBearing: true,
                waterResistant: true,
                fireResistant: false,
                frostResistant: true,
                chemicalResistant: false,
                flexible: true
            },
            applications: ['roads', 'parking_lots', 'runways'],
            temperatureRange: {
                min: -40, // °C
                max: 60,
                optimal: 25
            }
        });
        
        // Gravel - Base course material
        this.materials.set('gravel', {
            id: 'gravel',
            name: 'Gravel',
            category: 'aggregate',
            color: [128, 128, 128],
            density: 1600,
            cost: 25,
            cureTime: 0,
            permeability: 0.8, // high drainage
            thermalConductivity: 2.0,
            durability: 0.9,
            workability: 0.8,
            properties: {
                loadBearing: true,
                waterResistant: true,
                fireResistant: true,
                frostResistant: true,
                chemicalResistant: true,
                drainage: true
            },
            applications: ['base_course', 'drainage', 'foundations'],
            gradation: {
                size_range: '19-38mm',
                uniformity: 0.7
            }
        });
        
        // Clay - Natural soil material
        this.materials.set('clay', {
            id: 'clay',
            name: 'Clay',
            category: 'soil',
            color: [139, 69, 19],
            density: 1800,
            cost: 10,
            cureTime: 0,
            permeability: 0.001, // very low
            thermalConductivity: 1.5,
            durability: 0.6,
            workability: 0.4,
            properties: {
                loadBearing: false,
                waterResistant: false,
                fireResistant: true,
                frostResistant: false,
                chemicalResistant: true,
                expansive: true
            },
            applications: ['subgrade', 'landscaping', 'barriers'],
            plasticity: {
                index: 25,
                limit: 45,
                shrinkage: 0.15
            }
        });
        
        // Bedrock - Natural foundation material
        this.materials.set('bedrock', {
            id: 'bedrock',
            name: 'Bedrock',
            category: 'natural',
            color: [105, 105, 105],
            density: 2700,
            cost: 0, // natural occurrence
            cureTime: 0,
            permeability: 0.001,
            thermalConductivity: 3.0,
            durability: 1.0,
            workability: 0.1, // very difficult to work with
            properties: {
                loadBearing: true,
                waterResistant: true,
                fireResistant: true,
                frostResistant: true,
                chemicalResistant: true,
                excavatable: false
            },
            applications: ['foundation', 'anchor_points'],
            hardness: 9 // Mohs scale
        });
        
        // Sand - Granular material
        this.materials.set('sand', {
            id: 'sand',
            name: 'Sand',
            category: 'aggregate',
            color: [194, 178, 128],
            density: 1500,
            cost: 15,
            cureTime: 0,
            permeability: 0.6,
            thermalConductivity: 0.8,
            durability: 0.8,
            workability: 0.9,
            properties: {
                loadBearing: false,
                waterResistant: false,
                fireResistant: true,
                frostResistant: true,
                chemicalResistant: true,
                drainage: true
            },
            applications: ['bedding', 'backfill', 'concrete_mix'],
            gradation: {
                size_range: '0.1-2mm',
                uniformity: 0.8
            }
        });
        
        // Topsoil - Organic growing medium
        this.materials.set('topsoil', {
            id: 'topsoil',
            name: 'Topsoil',
            category: 'organic',
            color: [101, 67, 33],
            density: 1200,
            cost: 30,
            cureTime: 0,
            permeability: 0.4,
            thermalConductivity: 0.5,
            durability: 0.7,
            workability: 0.8,
            properties: {
                loadBearing: false,
                waterResistant: false,
                fireResistant: false,
                frostResistant: false,
                chemicalResistant: false,
                organic: true,
                fertile: true
            },
            applications: ['landscaping', 'vegetation', 'erosion_control'],
            organicContent: 0.15
        });
        
        // Geotextile - Synthetic reinforcement
        this.materials.set('geotextile', {
            id: 'geotextile',
            name: 'Geotextile',
            category: 'synthetic',
            color: [255, 255, 255],
            density: 200, // very light
            cost: 5, // per m²
            cureTime: 0,
            permeability: 0.9, // allows drainage
            thermalConductivity: 0.1,
            durability: 0.95,
            workability: 1.0,
            properties: {
                loadBearing: false,
                waterResistant: true,
                fireResistant: false,
                frostResistant: true,
                chemicalResistant: true,
                reinforcement: true,
                separation: true
            },
            applications: ['reinforcement', 'separation', 'drainage'],
            tensileStrength: 50 // kN/m
        });
    }
    
    initializeWeatherEffects() {
        // Freeze-thaw cycles
        this.weatherEffects.set('freeze_thaw', {
            name: 'Freeze-Thaw Cycles',
            affectedMaterials: ['concrete', 'clay', 'topsoil'],
            effects: {
                concrete: { durability: -0.001, cracking: 0.002 },
                clay: { expansion: 0.05, strength: -0.01 },
                topsoil: { heaving: 0.03 }
            },
            conditions: { temperature: { min: -5, max: 5 } }
        });
        
        // Chemical weathering
        this.weatherEffects.set('chemical_weathering', {
            name: 'Chemical Weathering',
            affectedMaterials: ['concrete', 'asphalt'],
            effects: {
                concrete: { durability: -0.0005, ph_change: -0.01 },
                asphalt: { oxidation: 0.001, brittleness: 0.002 }
            },
            conditions: { humidity: { min: 0.7 }, temperature: { min: 20 } }
        });
        
        // Erosion
        this.weatherEffects.set('erosion', {
            name: 'Water Erosion',
            affectedMaterials: ['sand', 'topsoil', 'clay'],
            effects: {
                sand: { displacement: 0.01 },
                topsoil: { displacement: 0.005, nutrient_loss: 0.002 },
                clay: { displacement: 0.002 }
            },
            conditions: { water_flow: { min: 0.1 } }
        });
    }
    
    placeMaterial(materialId, x, y, thickness, compaction = 1.0) {
        const material = this.materials.get(materialId);
        if (!material || !this.core.terrainEngine) return false;
        
        const terrain = this.core.terrainEngine;
        const radius = Math.sqrt(thickness * 10); // Convert thickness to radius
        
        for (let dy = -radius; dy <= radius; dy++) {
            for (let dx = -radius; dx <= radius; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (nx >= 0 && nx < terrain.width && ny >= 0 && ny < terrain.height) {
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= radius) {
                        const falloff = 1 - (distance / radius);
                        const effectiveThickness = thickness * falloff * compaction;
                        const index = ny * terrain.width + nx;
                        
                        // Update height
                        terrain.heightMap[index] += effectiveThickness * 0.01;
                        
                        // Set material layer
                        this.setMaterialLayer(index, materialId, effectiveThickness);
                        
                        // Update terrain type for visualization
                        this.updateTerrainVisualization(index, materialId);
                    }
                }
            }
        }
        
        // Calculate and track costs
        const volume = Math.PI * radius * radius * thickness;
        const cost = volume * material.cost;
        
        this.core.uiSystem?.showNotification(
            `Placed ${material.name}: ${volume.toFixed(2)}m³ ($${cost.toFixed(2)})`,
            'info'
        );
        
        return true;
    }
    
    setMaterialLayer(index, materialId, thickness) {
        if (!this.materialLayers.has(index)) {
            this.materialLayers.set(index, []);
        }
        
        const layers = this.materialLayers.get(index);
        layers.push({
            material: materialId,
            thickness: thickness,
            placedTime: Date.now(),
            compaction: 1.0,
            weathering: 0
        });
        
        // Sort layers by placement time (bottom to top)
        layers.sort((a, b) => a.placedTime - b.placedTime);
    }
    
    updateTerrainVisualization(index, materialId) {
        const material = this.materials.get(materialId);
        if (!material || !this.core.terrainEngine) return;
        
        const terrain = this.core.terrainEngine;
        
        // Map material to terrain type for visualization
        switch (materialId) {
            case 'concrete':
            case 'bedrock':
                terrain.terrainTypes[index] = 4; // rock
                break;
            case 'asphalt':
                terrain.terrainTypes[index] = 4; // rock (dark)
                break;
            case 'gravel':
                terrain.terrainTypes[index] = 4; // rock
                break;
            case 'clay':
                terrain.terrainTypes[index] = 2; // soil
                break;
            case 'sand':
                terrain.terrainTypes[index] = 1; // sand
                break;
            case 'topsoil':
                terrain.terrainTypes[index] = 3; // grass
                break;
            default:
                terrain.terrainTypes[index] = 2; // soil
        }
    }
    
    getMaterialProperties(materialId) {
        return this.materials.get(materialId);
    }
    
    getLayersAtPosition(x, y) {
        if (!this.core.terrainEngine) return [];
        
        const terrain = this.core.terrainEngine;
        const index = y * terrain.width + x;
        
        return this.materialLayers.get(index) || [];
    }
    
    calculateBearingCapacity(x, y) {
        const layers = this.getLayersAtPosition(x, y);
        let totalCapacity = 0;
        
        for (const layer of layers) {
            const material = this.materials.get(layer.material);
            if (material && material.properties.loadBearing) {
                const layerCapacity = material.compressiveStrength * layer.thickness * layer.compaction;
                totalCapacity += layerCapacity;
            }
        }
        
        return totalCapacity;
    }
    
    calculateDrainageRate(x, y) {
        const layers = this.getLayersAtPosition(x, y);
        let effectivePermeability = 0;
        let totalThickness = 0;
        
        for (const layer of layers) {
            const material = this.materials.get(layer.material);
            if (material) {
                effectivePermeability += material.permeability * layer.thickness;
                totalThickness += layer.thickness;
            }
        }
        
        return totalThickness > 0 ? effectivePermeability / totalThickness : 0;
    }
    
    simulateWeatherEffects(deltaTime) {
        const currentWeather = this.getCurrentWeatherConditions();
        
        for (const [effectId, effect] of this.weatherEffects) {
            if (this.checkWeatherConditions(effect.conditions, currentWeather)) {
                this.applyWeatherEffect(effect, deltaTime);
            }
        }
    }
    
    getCurrentWeatherConditions() {
        // In a real implementation, this would get actual weather data
        return {
            temperature: 20, // °C
            humidity: 0.6,
            precipitation: 0.0, // mm/hour
            wind_speed: 5 // m/s
        };
    }
    
    checkWeatherConditions(conditions, current) {
        for (const [param, range] of Object.entries(conditions)) {
            const value = current[param];
            if (range.min !== undefined && value < range.min) return false;
            if (range.max !== undefined && value > range.max) return false;
        }
        return true;
    }
    
    applyWeatherEffect(effect, deltaTime) {
        for (const [index, layers] of this.materialLayers) {
            for (const layer of layers) {
                if (effect.affectedMaterials.includes(layer.material)) {
                    const materialEffect = effect.effects[layer.material];
                    if (materialEffect) {
                        // Apply weathering effects
                        for (const [property, change] of Object.entries(materialEffect)) {
                            layer.weathering += Math.abs(change) * deltaTime;
                        }
                    }
                }
            }
        }
    }
    
    testMaterialCompatibility(material1Id, material2Id) {
        const mat1 = this.materials.get(material1Id);
        const mat2 = this.materials.get(material2Id);
        
        if (!mat1 || !mat2) return { compatible: false, reason: 'Material not found' };
        
        // Check thermal compatibility
        const thermalDiff = Math.abs(mat1.thermalConductivity - mat2.thermalConductivity);
        if (thermalDiff > 2.0) {
            return { 
                compatible: false, 
                reason: 'Thermal expansion mismatch',
                recommendation: 'Use expansion joints'
            };
        }
        
        // Check chemical compatibility
        if (mat1.properties.chemicalResistant !== mat2.properties.chemicalResistant) {
            return {
                compatible: false,
                reason: 'Chemical compatibility issues',
                recommendation: 'Use barrier layer'
            };
        }
        
        // Check permeability compatibility
        const permDiff = Math.abs(mat1.permeability - mat2.permeability);
        if (permDiff > 0.5) {
            return {
                compatible: true,
                warning: 'Drainage considerations needed',
                recommendation: 'Install drainage system'
            };
        }
        
        return { compatible: true };
    }
    
    generateMaterialReport(x, y, radius) {
        const report = {
            location: { x, y, radius },
            materials: new Map(),
            totalVolume: 0,
            totalCost: 0,
            bearingCapacity: 0,
            drainageRate: 0,
            recommendations: []
        };
        
        // Sample area
        for (let dy = -radius; dy <= radius; dy++) {
            for (let dx = -radius; dx <= radius; dx++) {
                const nx = x + dx;
                const ny = y + dy;
                
                if (Math.sqrt(dx * dx + dy * dy) <= radius) {
                    const layers = this.getLayersAtPosition(nx, ny);
                    
                    for (const layer of layers) {
                        const material = this.materials.get(layer.material);
                        if (material) {
                            if (!report.materials.has(layer.material)) {
                                report.materials.set(layer.material, {
                                    name: material.name,
                                    volume: 0,
                                    cost: 0,
                                    avgThickness: 0,
                                    count: 0
                                });
                            }
                            
                            const matData = report.materials.get(layer.material);
                            matData.volume += layer.thickness;
                            matData.cost += layer.thickness * material.cost;
                            matData.avgThickness += layer.thickness;
                            matData.count++;
                        }
                    }
                    
                    report.bearingCapacity += this.calculateBearingCapacity(nx, ny);
                    report.drainageRate += this.calculateDrainageRate(nx, ny);
                }
            }
        }
        
        // Calculate averages
        const sampleCount = Math.PI * radius * radius;
        report.bearingCapacity /= sampleCount;
        report.drainageRate /= sampleCount;
        
        // Finalize material data
        for (const [materialId, data] of report.materials) {
            data.avgThickness /= data.count;
            report.totalVolume += data.volume;
            report.totalCost += data.cost;
        }
        
        // Generate recommendations
        if (report.drainageRate < 0.1) {
            report.recommendations.push('Consider adding drainage layer');
        }
        if (report.bearingCapacity < 100) {
            report.recommendations.push('Insufficient bearing capacity for heavy loads');
        }
        
        return report;
    }
    
    update(deltaTime) {
        // Simulate material aging and weather effects
        this.simulateWeatherEffects(deltaTime);
        
        // Update material curing
        this.updateMaterialCuring(deltaTime);
    }
    
    updateMaterialCuring(deltaTime) {
        for (const [index, layers] of this.materialLayers) {
            for (const layer of layers) {
                const material = this.materials.get(layer.material);
                if (material && material.cureTime > 0) {
                    const elapsed = (Date.now() - layer.placedTime) / 60000; // minutes
                    const cureProgress = Math.min(1, elapsed / material.cureTime);
                    
                    // Update layer properties based on curing
                    layer.compaction = 0.7 + (0.3 * cureProgress);
                }
            }
        }
    }
}
