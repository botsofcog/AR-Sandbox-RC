/**
 * Real Construction Projects System
 * Actual construction scenarios with proper engineering requirements
 */

class RealConstructionProjects {
    constructor(core) {
        this.core = core;
        this.projects = new Map();
        this.templates = new Map();
        this.activeProject = null;
        this.standards = new Map();
        
        this.initializeProjectTemplates();
        this.initializeConstructionStandards();
    }
    
    initializeProjectTemplates() {
        // Highway Construction Project
        this.templates.set('highway_construction', {
            name: 'Highway Construction',
            description: 'Build a multi-lane highway with proper base layers and drainage',
            category: 'transportation',
            difficulty: 'advanced',
            estimatedDuration: 180, // minutes
            budget: 2500000, // dollars
            specifications: {
                lanes: 4,
                width: 24, // meters
                length: 500, // meters
                designSpeed: 100, // km/h
                trafficLoad: 'heavy'
            },
            phases: [
                {
                    name: 'Site Survey and Preparation',
                    duration: 20,
                    requirements: {
                        equipment: ['surveyor', 'bulldozer'],
                        materials: [],
                        weather: 'clear'
                    },
                    deliverables: ['site_survey', 'cleared_area'],
                    qualityChecks: ['elevation_accuracy', 'area_clearance']
                },
                {
                    name: 'Subgrade Preparation',
                    duration: 30,
                    requirements: {
                        equipment: ['excavator', 'compactor'],
                        materials: ['geotextile'],
                        previousPhase: 'Site Survey and Preparation'
                    },
                    deliverables: ['prepared_subgrade'],
                    qualityChecks: ['compaction_95_percent', 'grade_tolerance']
                },
                {
                    name: 'Base Course Installation',
                    duration: 40,
                    requirements: {
                        equipment: ['dump_truck', 'grader', 'compactor'],
                        materials: ['gravel', 'crushed_stone'],
                        thickness: 0.3 // meters
                    },
                    deliverables: ['base_course'],
                    qualityChecks: ['thickness_verification', 'compaction_98_percent']
                },
                {
                    name: 'Drainage System',
                    duration: 35,
                    requirements: {
                        equipment: ['trencher', 'pipe_layer'],
                        materials: ['drainage_pipe', 'gravel'],
                        slope: 0.02 // 2% minimum
                    },
                    deliverables: ['drainage_system'],
                    qualityChecks: ['flow_test', 'grade_verification']
                },
                {
                    name: 'Asphalt Paving',
                    duration: 45,
                    requirements: {
                        equipment: ['paver', 'roller'],
                        materials: ['asphalt'],
                        temperature: { min: 10, max: 35 }
                    },
                    deliverables: ['paved_surface'],
                    qualityChecks: ['smoothness_test', 'thickness_core_test']
                },
                {
                    name: 'Final Inspection',
                    duration: 10,
                    requirements: {
                        equipment: ['inspection_vehicle'],
                        materials: [],
                        tests: ['ride_quality', 'drainage_function']
                    },
                    deliverables: ['completion_certificate'],
                    qualityChecks: ['final_acceptance']
                }
            ],
            successCriteria: {
                budgetVariance: 0.1, // ±10%
                scheduleVariance: 0.15, // ±15%
                qualityScore: 0.85, // 85% minimum
                safetyIncidents: 0
            }
        });
        
        // Building Foundation Project
        this.templates.set('building_foundation', {
            name: 'Commercial Building Foundation',
            description: 'Construct foundation for 5-story commercial building',
            category: 'structural',
            difficulty: 'expert',
            estimatedDuration: 120,
            budget: 800000,
            specifications: {
                buildingHeight: 5, // stories
                footprint: { width: 40, length: 60 }, // meters
                foundationDepth: 3, // meters
                soilType: 'clay',
                loadCapacity: 500 // kN/m²
            },
            phases: [
                {
                    name: 'Geotechnical Investigation',
                    duration: 15,
                    requirements: {
                        equipment: ['drill_rig', 'testing_equipment'],
                        materials: [],
                        tests: ['soil_bearing_capacity', 'groundwater_level']
                    },
                    deliverables: ['geotechnical_report'],
                    qualityChecks: ['soil_classification', 'bearing_capacity_verification']
                },
                {
                    name: 'Excavation',
                    duration: 25,
                    requirements: {
                        equipment: ['excavator', 'dump_truck'],
                        materials: [],
                        depth: 3.5, // meters (including working space)
                        shoring: true
                    },
                    deliverables: ['excavated_foundation'],
                    qualityChecks: ['dimension_accuracy', 'slope_stability']
                },
                {
                    name: 'Dewatering System',
                    duration: 10,
                    requirements: {
                        equipment: ['pump', 'wellpoints'],
                        materials: ['drainage_pipe'],
                        waterLevel: 'below_foundation'
                    },
                    deliverables: ['dry_excavation'],
                    qualityChecks: ['water_level_control']
                },
                {
                    name: 'Footing Installation',
                    duration: 30,
                    requirements: {
                        equipment: ['concrete_truck', 'crane', 'vibrator'],
                        materials: ['concrete', 'rebar'],
                        strength: 'C30' // concrete grade
                    },
                    deliverables: ['concrete_footings'],
                    qualityChecks: ['concrete_strength_test', 'reinforcement_placement']
                },
                {
                    name: 'Foundation Walls',
                    duration: 35,
                    requirements: {
                        equipment: ['concrete_pump', 'formwork'],
                        materials: ['concrete', 'rebar', 'waterproofing'],
                        curing: 7 // days minimum
                    },
                    deliverables: ['foundation_walls'],
                    qualityChecks: ['wall_alignment', 'waterproofing_test']
                },
                {
                    name: 'Backfilling',
                    duration: 15,
                    requirements: {
                        equipment: ['compactor', 'dump_truck'],
                        materials: ['select_fill'],
                        compaction: 0.95 // 95% standard proctor
                    },
                    deliverables: ['completed_foundation'],
                    qualityChecks: ['compaction_test', 'final_survey']
                }
            ],
            successCriteria: {
                budgetVariance: 0.08,
                scheduleVariance: 0.12,
                qualityScore: 0.90,
                safetyIncidents: 0,
                structuralIntegrity: 1.0
            }
        });
        
        // Retaining Wall Project
        this.templates.set('retaining_wall', {
            name: 'Reinforced Retaining Wall',
            description: 'Build retaining wall for slope stabilization',
            category: 'geotechnical',
            difficulty: 'intermediate',
            estimatedDuration: 90,
            budget: 350000,
            specifications: {
                height: 6, // meters
                length: 100, // meters
                wallType: 'reinforced_concrete',
                soilPressure: 'active',
                drainageRequired: true
            },
            phases: [
                {
                    name: 'Slope Analysis',
                    duration: 10,
                    requirements: {
                        equipment: ['inclinometer', 'survey_equipment'],
                        materials: [],
                        analysis: ['stability', 'soil_pressure']
                    },
                    deliverables: ['stability_analysis'],
                    qualityChecks: ['factor_of_safety']
                },
                {
                    name: 'Foundation Excavation',
                    duration: 20,
                    requirements: {
                        equipment: ['excavator'],
                        materials: [],
                        depth: 1.5, // meters below grade
                        width: 2.0 // meters
                    },
                    deliverables: ['wall_foundation'],
                    qualityChecks: ['bearing_capacity', 'level_accuracy']
                },
                {
                    name: 'Drainage Installation',
                    duration: 15,
                    requirements: {
                        equipment: ['trencher'],
                        materials: ['perforated_pipe', 'gravel', 'geotextile'],
                        slope: 0.01 // 1% minimum
                    },
                    deliverables: ['drainage_system'],
                    qualityChecks: ['flow_capacity', 'outlet_function']
                },
                {
                    name: 'Wall Construction',
                    duration: 35,
                    requirements: {
                        equipment: ['concrete_pump', 'crane'],
                        materials: ['concrete', 'rebar', 'formwork'],
                        reinforcement: 'grade_60_steel'
                    },
                    deliverables: ['retaining_wall'],
                    qualityChecks: ['concrete_strength', 'reinforcement_cover']
                },
                {
                    name: 'Backfill and Compaction',
                    duration: 10,
                    requirements: {
                        equipment: ['compactor'],
                        materials: ['granular_fill'],
                        lifts: 0.3 // meter lifts
                    },
                    deliverables: ['completed_wall'],
                    qualityChecks: ['compaction_density', 'wall_deflection']
                }
            ],
            successCriteria: {
                budgetVariance: 0.12,
                scheduleVariance: 0.20,
                qualityScore: 0.88,
                safetyIncidents: 0,
                stabilityFactor: 1.5 // minimum factor of safety
            }
        });
    }
    
    initializeConstructionStandards() {
        // AASHTO Standards for Highway Construction
        this.standards.set('AASHTO_M43', {
            name: 'Aggregate for Base Course',
            requirements: {
                gradation: {
                    '50mm': { passing: 100 },
                    '25mm': { passing: [95, 100] },
                    '12.5mm': { passing: [70, 92] },
                    '4.75mm': { passing: [40, 70] },
                    '0.425mm': { passing: [15, 40] },
                    '0.075mm': { passing: [5, 15] }
                },
                plasticityIndex: { max: 6 },
                liquidLimit: { max: 25 }
            }
        });
        
        // ACI Standards for Concrete
        this.standards.set('ACI_318', {
            name: 'Building Code Requirements for Structural Concrete',
            requirements: {
                compressiveStrength: {
                    'C20': 20, // MPa
                    'C25': 25,
                    'C30': 30,
                    'C35': 35
                },
                slump: { min: 25, max: 100 }, // mm
                airContent: { min: 4, max: 7 }, // %
                waterCementRatio: { max: 0.5 }
            }
        });
    }
    
    startProject(templateId, location, customParameters = {}) {
        const template = this.templates.get(templateId);
        if (!template) {
            console.error(`Unknown project template: ${templateId}`);
            return null;
        }
        
        const project = {
            id: Date.now(),
            template: template,
            location: location,
            parameters: { ...template.specifications, ...customParameters },
            currentPhase: 0,
            startTime: Date.now(),
            status: 'planning',
            progress: 0,
            budget: {
                allocated: template.budget,
                spent: 0,
                remaining: template.budget
            },
            schedule: {
                plannedDuration: template.estimatedDuration,
                actualDuration: 0,
                variance: 0
            },
            quality: {
                score: 0,
                checks: new Map(),
                issues: []
            },
            safety: {
                incidents: 0,
                inspections: 0,
                violations: []
            },
            resources: {
                equipment: new Map(),
                materials: new Map(),
                personnel: new Map()
            }
        };
        
        this.projects.set(project.id, project);
        this.activeProject = project.id;
        
        this.core.uiSystem?.showNotification(
            `Started project: ${template.name}`,
            'info'
        );
        
        return project.id;
    }
    
    executePhase(projectId, phaseIndex) {
        const project = this.projects.get(projectId);
        if (!project) return false;
        
        const phase = project.template.phases[phaseIndex];
        if (!phase) return false;
        
        // Check prerequisites
        if (!this.checkPhaseRequirements(project, phase)) {
            this.core.uiSystem?.showNotification(
                `Phase requirements not met: ${phase.name}`,
                'warning'
            );
            return false;
        }
        
        // Execute phase activities
        this.performPhaseActivities(project, phase);
        
        // Perform quality checks
        this.performQualityChecks(project, phase);
        
        // Update project status
        project.currentPhase = phaseIndex;
        project.progress = (phaseIndex + 1) / project.template.phases.length;
        
        // Calculate costs
        this.updateProjectCosts(project, phase);
        
        this.core.uiSystem?.showNotification(
            `Completed phase: ${phase.name}`,
            'success'
        );
        
        return true;
    }
    
    checkPhaseRequirements(project, phase) {
        // Check equipment availability
        for (const equipment of phase.requirements.equipment || []) {
            if (!this.isEquipmentAvailable(equipment)) {
                project.quality.issues.push(`Equipment not available: ${equipment}`);
                return false;
            }
        }
        
        // Check material availability
        for (const material of phase.requirements.materials || []) {
            if (!this.isMaterialAvailable(material)) {
                project.quality.issues.push(`Material not available: ${material}`);
                return false;
            }
        }
        
        // Check weather conditions
        if (phase.requirements.weather) {
            if (!this.checkWeatherConditions(phase.requirements.weather)) {
                project.quality.issues.push('Weather conditions not suitable');
                return false;
            }
        }
        
        // Check previous phase completion
        if (phase.requirements.previousPhase) {
            const prevPhaseIndex = project.template.phases.findIndex(
                p => p.name === phase.requirements.previousPhase
            );
            if (prevPhaseIndex >= project.currentPhase) {
                project.quality.issues.push('Previous phase not completed');
                return false;
            }
        }
        
        return true;
    }
    
    performPhaseActivities(project, phase) {
        const location = project.location;
        
        // Simulate construction activities based on phase type
        switch (phase.name) {
            case 'Site Survey and Preparation':
                this.performSiteSurvey(location);
                this.clearSite(location);
                break;
                
            case 'Excavation':
            case 'Foundation Excavation':
                this.performExcavation(location, phase.requirements.depth || 1.0);
                break;
                
            case 'Base Course Installation':
                this.installBaseCourse(location, phase.requirements.thickness || 0.3);
                break;
                
            case 'Asphalt Paving':
                this.performPaving(location);
                break;
                
            case 'Footing Installation':
            case 'Foundation Walls':
                this.pourConcrete(location, phase.requirements.strength || 'C25');
                break;
                
            case 'Drainage System':
            case 'Drainage Installation':
                this.installDrainage(location);
                break;
                
            case 'Wall Construction':
                this.constructWall(location, project.parameters.height || 3);
                break;
        }
    }
    
    performSiteSurvey(location) {
        // Create survey markers and establish benchmarks
        if (this.core.terrainEngine) {
            // Mark survey points
            for (let i = 0; i < 10; i++) {
                const x = location.x + (Math.random() - 0.5) * 50;
                const y = location.y + (Math.random() - 0.5) * 50;
                
                // Place survey marker (visual indicator)
                this.placeSurveyMarker(x, y);
            }
        }
    }
    
    clearSite(location) {
        if (this.core.terrainEngine) {
            const terrain = this.core.terrainEngine;
            const radius = 30;
            const targetHeight = 0.4;
            
            for (let dy = -radius; dy <= radius; dy++) {
                for (let dx = -radius; dx <= radius; dx++) {
                    const nx = location.x + dx;
                    const ny = location.y + dy;
                    
                    if (nx >= 0 && nx < terrain.width && ny >= 0 && ny < terrain.height) {
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        if (distance <= radius) {
                            const index = ny * terrain.width + nx;
                            const falloff = 1 - (distance / radius);
                            const effect = 0.02 * falloff;
                            
                            // Gradually level to target height
                            const currentHeight = terrain.heightMap[index];
                            const diff = targetHeight - currentHeight;
                            terrain.heightMap[index] += diff * effect;
                            terrain.updateTerrainType(index);
                        }
                    }
                }
            }
        }
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
            
            // Create excavation particles
            if (this.core.physicsEngine) {
                for (let i = 0; i < 20; i++) {
                    this.core.physicsEngine.spawnParticle({
                        x: location.x * 4 + (Math.random() - 0.5) * 40,
                        y: location.y * 4 + (Math.random() - 0.5) * 40,
                        z: 30 + Math.random() * 50,
                        vx: (Math.random() - 0.5) * 50,
                        vy: (Math.random() - 0.5) * 50,
                        vz: Math.random() * 40 + 20,
                        type: 'dust',
                        life: 4.0,
                        size: 3 + Math.random() * 5,
                        color: [139, 119, 101, 0.8]
                    });
                }
            }
        }
    }
    
    installBaseCourse(location, thickness) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('gravel', location.x, location.y, thickness, 0.95);
        }
    }
    
    performPaving(location) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('asphalt', location.x, location.y, 0.1, 0.98);
        }
    }
    
    pourConcrete(location, strength) {
        if (this.core.materialsSystem) {
            this.core.materialsSystem.placeMaterial('concrete', location.x, location.y, 0.3, 1.0);
        }
    }
    
    installDrainage(location) {
        // Create drainage trenches and install pipes
        if (this.core.terrainEngine) {
            const terrain = this.core.terrainEngine;
            
            // Create drainage channel
            for (let i = -25; i <= 25; i++) {
                const x = location.x + i;
                const y = location.y;
                
                if (x >= 0 && x < terrain.width && y >= 0 && y < terrain.height) {
                    const index = y * terrain.width + x;
                    terrain.heightMap[index] -= 0.05; // Create channel
                    terrain.updateTerrainType(index);
                }
            }
        }
    }
    
    performQualityChecks(project, phase) {
        const checks = phase.qualityChecks || [];
        let passedChecks = 0;
        
        for (const check of checks) {
            const result = this.executeQualityCheck(check, project, phase);
            project.quality.checks.set(check, result);
            
            if (result.passed) {
                passedChecks++;
            } else {
                project.quality.issues.push(`Quality check failed: ${check} - ${result.reason}`);
            }
        }
        
        const phaseQualityScore = passedChecks / checks.length;
        project.quality.score = (project.quality.score + phaseQualityScore) / 2;
    }
    
    executeQualityCheck(checkType, project, phase) {
        switch (checkType) {
            case 'compaction_95_percent':
                return { passed: Math.random() > 0.1, value: 94 + Math.random() * 4, target: 95 };
                
            case 'thickness_verification':
                const thickness = phase.requirements.thickness || 0.3;
                const measured = thickness * (0.95 + Math.random() * 0.1);
                return { 
                    passed: Math.abs(measured - thickness) < thickness * 0.05,
                    value: measured,
                    target: thickness,
                    tolerance: thickness * 0.05
                };
                
            case 'concrete_strength_test':
                const targetStrength = 25; // MPa
                const actualStrength = targetStrength * (0.9 + Math.random() * 0.2);
                return {
                    passed: actualStrength >= targetStrength,
                    value: actualStrength,
                    target: targetStrength
                };
                
            default:
                return { passed: Math.random() > 0.15, value: 'N/A', target: 'Pass' };
        }
    }
    
    updateProjectCosts(project, phase) {
        // Calculate phase costs
        const equipmentCost = (phase.requirements.equipment?.length || 0) * 1000 * (phase.duration / 60);
        const materialCost = (phase.requirements.materials?.length || 0) * 5000;
        const laborCost = phase.duration * 200; // $200 per minute
        
        const totalPhaseCost = equipmentCost + materialCost + laborCost;
        
        project.budget.spent += totalPhaseCost;
        project.budget.remaining = project.budget.allocated - project.budget.spent;
        
        // Add cost variance
        const variance = (Math.random() - 0.5) * 0.2; // ±10% variance
        project.budget.spent *= (1 + variance);
    }
    
    getProjectStatus(projectId) {
        const project = this.projects.get(projectId);
        if (!project) return null;
        
        const currentPhase = project.template.phases[project.currentPhase];
        
        return {
            id: project.id,
            name: project.template.name,
            status: project.status,
            progress: project.progress,
            currentPhase: currentPhase?.name || 'Complete',
            budget: project.budget,
            schedule: project.schedule,
            quality: {
                score: project.quality.score,
                issues: project.quality.issues.length
            },
            safety: project.safety
        };
    }
    
    generateProjectReport(projectId) {
        const project = this.projects.get(projectId);
        if (!project) return null;
        
        const report = {
            project: this.getProjectStatus(projectId),
            phases: [],
            qualityChecks: Array.from(project.quality.checks.entries()),
            recommendations: [],
            summary: {
                budgetVariance: (project.budget.spent - project.budget.allocated) / project.budget.allocated,
                scheduleVariance: project.schedule.variance,
                qualityScore: project.quality.score,
                safetyRecord: project.safety.incidents === 0 ? 'Excellent' : 'Needs Improvement'
            }
        };
        
        // Add phase details
        for (let i = 0; i <= project.currentPhase; i++) {
            const phase = project.template.phases[i];
            if (phase) {
                report.phases.push({
                    name: phase.name,
                    status: i < project.currentPhase ? 'Complete' : 'In Progress',
                    duration: phase.duration,
                    deliverables: phase.deliverables
                });
            }
        }
        
        // Generate recommendations
        if (report.summary.budgetVariance > 0.1) {
            report.recommendations.push('Consider cost control measures for future phases');
        }
        if (project.quality.score < 0.85) {
            report.recommendations.push('Implement additional quality control procedures');
        }
        if (project.quality.issues.length > 0) {
            report.recommendations.push('Address quality issues before proceeding');
        }
        
        return report;
    }
    
    // Helper methods
    isEquipmentAvailable(equipment) {
        return Math.random() > 0.1; // 90% availability
    }
    
    isMaterialAvailable(material) {
        return Math.random() > 0.05; // 95% availability
    }
    
    checkWeatherConditions(requirement) {
        return Math.random() > 0.2; // 80% suitable weather
    }
    
    placeSurveyMarker(x, y) {
        // Visual marker for survey points
        console.log(`Survey marker placed at (${x}, ${y})`);
    }
    
    constructWall(location, height) {
        if (this.core.materialsSystem) {
            // Build wall in layers
            for (let layer = 0; layer < height; layer++) {
                this.core.materialsSystem.placeMaterial(
                    'concrete', 
                    location.x, 
                    location.y + layer * 2, 
                    0.2, 
                    1.0
                );
            }
        }
    }
}
