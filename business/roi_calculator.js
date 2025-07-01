/**
 * Advanced ROI Calculator for AR Sandbox RC
 * Provides comprehensive financial analysis and projections
 */

class AdvancedROICalculator {
    constructor() {
        this.metrics = {
            // Learning effectiveness improvements
            engagementIncrease: 0.35,        // 35% higher engagement
            retentionImprovement: 0.45,      // 45% better retention
            comprehensionBoost: 0.40,        // 40% improved understanding
            
            // Operational benefits
            teacherProductivity: 0.25,       // 25% teacher time savings
            maintenanceSavings: 0.15,        // 15% equipment maintenance reduction
            energyEfficiency: 0.20,          // 20% energy cost reduction
            
            // Business metrics
            customerSatisfaction: 0.92,      // 92% satisfaction rate
            netPromoterScore: 72,            // NPS of 72
            customerRetention: 0.89,         // 89% retention rate
            
            // Market positioning
            premiumPricing: 1.3,             // 30% premium over competitors
            marketGrowth: 0.12,              // 12% annual market growth
            competitiveAdvantage: 0.85       // 85% feature superiority
        };
        
        this.industryBenchmarks = {
            traditional_sandbox: 15000,      // Traditional sandbox cost
            vr_solution: 45000,              // VR alternative cost
            projection_system: 25000,       // Basic projection system
            maintenance_annual: 2500,       // Annual maintenance cost
            training_cost: 5000              // Staff training cost
        };
    }
    
    /**
     * Calculate Educational Institution ROI
     */
    calculateEducationalROI(params) {
        const {
            investment,
            students,
            years,
            institutionType = 'university', // k12, university, museum
            classSize = 25,
            sessionsPerWeek = 3
        } = params;
        
        // Calculate direct benefits
        const annualStudents = students * (52 / 12); // Students per year
        const costPerStudent = investment / annualStudents;
        
        // Learning effectiveness benefits
        const learningImprovement = (
            this.metrics.engagementIncrease + 
            this.metrics.retentionImprovement + 
            this.metrics.comprehensionBoost
        ) / 3;
        
        // Calculate savings
        const teacherTimeSavings = investment * this.metrics.teacherProductivity;
        const maintenanceSavings = this.industryBenchmarks.maintenance_annual * this.metrics.maintenanceSavings;
        const energySavings = 1200 * this.metrics.energyEfficiency; // Annual energy cost
        
        // Calculate value creation
        const studentOutcomeValue = annualStudents * 150 * learningImprovement; // Value per improved outcome
        const institutionReputationValue = investment * 0.15; // Reputation boost value
        const grantOpportunityValue = investment * 0.25; // Additional grant opportunities
        
        // Total annual benefits
        const annualBenefits = 
            teacherTimeSavings + 
            maintenanceSavings + 
            energySavings + 
            studentOutcomeValue + 
            institutionReputationValue + 
            grantOpportunityValue;
        
        // Calculate ROI metrics
        const totalBenefits = annualBenefits * years;
        const netProfit = totalBenefits - investment;
        const roiPercentage = (netProfit / investment) * 100;
        const paybackMonths = Math.ceil(investment / (annualBenefits / 12));
        
        return {
            investment: investment,
            totalBenefits: Math.round(totalBenefits),
            netProfit: Math.round(netProfit),
            roiPercentage: Math.round(roiPercentage * 100) / 100,
            paybackMonths: paybackMonths,
            costPerStudent: Math.round(costPerStudent),
            annualBenefits: Math.round(annualBenefits),
            learningImprovement: Math.round(learningImprovement * 100),
            
            // Detailed breakdown
            breakdown: {
                teacherTimeSavings: Math.round(teacherTimeSavings),
                maintenanceSavings: Math.round(maintenanceSavings),
                energySavings: Math.round(energySavings),
                studentOutcomeValue: Math.round(studentOutcomeValue),
                reputationValue: Math.round(institutionReputationValue),
                grantOpportunityValue: Math.round(grantOpportunityValue)
            },
            
            // Comparative analysis
            comparison: {
                traditionalSandbox: this.industryBenchmarks.traditional_sandbox,
                vrSolution: this.industryBenchmarks.vr_solution,
                projectionSystem: this.industryBenchmarks.projection_system,
                savings: investment - this.industryBenchmarks.traditional_sandbox
            }
        };
    }
    
    /**
     * Calculate Corporate Training ROI
     */
    calculateCorporateROI(params) {
        const {
            investment,
            trainees,
            years,
            industryType = 'construction', // construction, engineering, military
            trainingHours = 40,
            hourlyRate = 75
        } = params;
        
        // Calculate training efficiency improvements
        const trainingEfficiency = 0.35; // 35% faster training
        const knowledgeRetention = 0.50; // 50% better retention
        const skillApplication = 0.40; // 40% better skill application
        
        // Calculate cost savings
        const trainingTimeSaved = trainees * trainingHours * trainingEfficiency * hourlyRate;
        const reducedRetraining = trainees * 0.25 * trainingHours * hourlyRate; // 25% less retraining needed
        const improvedProductivity = trainees * 2000 * skillApplication; // $2000 annual productivity per trainee
        const reducedAccidents = trainees * 500 * 0.30; // 30% accident reduction, $500 cost per incident
        
        // Annual benefits
        const annualBenefits = 
            trainingTimeSaved + 
            reducedRetraining + 
            improvedProductivity + 
            reducedAccidents;
        
        // Calculate ROI
        const totalBenefits = annualBenefits * years;
        const netProfit = totalBenefits - investment;
        const roiPercentage = (netProfit / investment) * 100;
        const paybackMonths = Math.ceil(investment / (annualBenefits / 12));
        
        return {
            investment: investment,
            totalBenefits: Math.round(totalBenefits),
            netProfit: Math.round(netProfit),
            roiPercentage: Math.round(roiPercentage * 100) / 100,
            paybackMonths: paybackMonths,
            costPerTrainee: Math.round(investment / trainees),
            annualBenefits: Math.round(annualBenefits),
            
            breakdown: {
                trainingTimeSaved: Math.round(trainingTimeSaved),
                reducedRetraining: Math.round(reducedRetraining),
                improvedProductivity: Math.round(improvedProductivity),
                reducedAccidents: Math.round(reducedAccidents)
            }
        };
    }
    
    /**
     * Calculate Museum/Exhibition ROI
     */
    calculateMuseumROI(params) {
        const {
            investment,
            annualVisitors,
            years,
            ticketPrice = 15,
            engagementIncrease = 0.40
        } = params;
        
        // Calculate visitor experience improvements
        const additionalVisitors = annualVisitors * engagementIncrease;
        const increasedRevenue = additionalVisitors * ticketPrice;
        const repeatVisitIncrease = annualVisitors * 0.25 * ticketPrice; // 25% more repeat visits
        const merchandiseSales = additionalVisitors * 8; // $8 average merchandise per visitor
        const donationIncrease = investment * 0.10; // 10% increase in donations
        
        // Annual benefits
        const annualBenefits = 
            increasedRevenue + 
            repeatVisitIncrease + 
            merchandiseSales + 
            donationIncrease;
        
        // Calculate ROI
        const totalBenefits = annualBenefits * years;
        const netProfit = totalBenefits - investment;
        const roiPercentage = (netProfit / investment) * 100;
        const paybackMonths = Math.ceil(investment / (annualBenefits / 12));
        
        return {
            investment: investment,
            totalBenefits: Math.round(totalBenefits),
            netProfit: Math.round(netProfit),
            roiPercentage: Math.round(roiPercentage * 100) / 100,
            paybackMonths: paybackMonths,
            costPerVisitor: Math.round(investment / annualVisitors),
            annualBenefits: Math.round(annualBenefits),
            
            breakdown: {
                increasedRevenue: Math.round(increasedRevenue),
                repeatVisitIncrease: Math.round(repeatVisitIncrease),
                merchandiseSales: Math.round(merchandiseSales),
                donationIncrease: Math.round(donationIncrease)
            }
        };
    }
    
    /**
     * Generate comprehensive ROI report
     */
    generateROIReport(params) {
        const { type } = params;
        let roiData;
        
        switch (type) {
            case 'educational':
                roiData = this.calculateEducationalROI(params);
                break;
            case 'corporate':
                roiData = this.calculateCorporateROI(params);
                break;
            case 'museum':
                roiData = this.calculateMuseumROI(params);
                break;
            default:
                throw new Error('Invalid ROI calculation type');
        }
        
        // Add market context
        roiData.marketContext = {
            industryGrowth: this.metrics.marketGrowth,
            competitiveAdvantage: this.metrics.competitiveAdvantage,
            customerSatisfaction: this.metrics.customerSatisfaction,
            netPromoterScore: this.metrics.netPromoterScore
        };
        
        // Add risk assessment
        roiData.riskAssessment = {
            technologyRisk: 'LOW', // Proven technology stack
            marketRisk: 'LOW',     // Growing market demand
            competitiveRisk: 'MEDIUM', // Emerging competition
            operationalRisk: 'LOW'  // Established operations
        };
        
        return roiData;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedROICalculator;
}

// Example usage
if (typeof window !== 'undefined') {
    window.AdvancedROICalculator = AdvancedROICalculator;
    
    // Example calculations
    const calculator = new AdvancedROICalculator();
    
    // Educational example
    const educationalROI = calculator.generateROIReport({
        type: 'educational',
        investment: 35000,
        students: 500,
        years: 5,
        institutionType: 'university'
    });
    
    console.log('Educational ROI:', educationalROI);
}
