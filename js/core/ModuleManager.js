/**
 * Module Manager - Dynamic module loading and dependency management
 * Provides plugin architecture for AR Sandbox Pro
 */

class ModuleManager {
    constructor(core) {
        this.core = core;
        this.modules = new Map();
        this.dependencies = new Map();
        this.loadingPromises = new Map();
        this.moduleConfigs = new Map();
        this.hooks = new Map();
        
        // Module registry for different license tiers
        this.moduleRegistry = {
            // Core modules (always available)
            core: [
                'RenderEngine',
                'PhysicsEngine',
                'InputManager',
                'AudioEngine',
                'UIManager'
            ],
            
            // Basic modules (trial and above)
            basic: [
                'TerrainModule',
                'WaterModule',
                'DepthCamera',
                'TouchInterface'
            ],
            
            // Educational modules (educational license and above)
            educational: [
                'EducationModule',
                'AssessmentModule',
                'ProgressModule',
                'LessonPlanModule'
            ],
            
            // Commercial modules (commercial license and above)
            commercial: [
                'CollaborationModule',
                'AnalyticsModule',
                'ReportingModule',
                'CustomizationModule'
            ],
            
            // Enterprise modules (enterprise license only)
            enterprise: [
                'MultiSiteModule',
                'APIModule',
                'IntegrationModule',
                'AdvancedAnalyticsModule'
            ]
        };
    }
    
    /**
     * Load a module dynamically
     */
    async loadModule(moduleName, config = {}) {
        // Check if module is already loaded
        if (this.modules.has(moduleName)) {
            return this.modules.get(moduleName);
        }
        
        // Check if module is currently loading
        if (this.loadingPromises.has(moduleName)) {
            return this.loadingPromises.get(moduleName);
        }
        
        // Validate license for module
        if (!this.validateModuleLicense(moduleName)) {
            throw new Error(`Module ${moduleName} not available in current license tier`);
        }
        
        console.log(`📦 Loading module: ${moduleName}`);
        
        const loadingPromise = this.loadModuleInternal(moduleName, config);
        this.loadingPromises.set(moduleName, loadingPromise);
        
        try {
            const module = await loadingPromise;
            this.modules.set(moduleName, module);
            this.core.registerModule(moduleName, module);
            
            console.log(`✅ Module loaded: ${moduleName}`);
            this.core.eventSystem.emit('module:loaded', { name: moduleName, module });
            
            return module;
        } catch (error) {
            console.error(`❌ Failed to load module ${moduleName}:`, error);
            throw error;
        } finally {
            this.loadingPromises.delete(moduleName);
        }
    }
    
    async loadModuleInternal(moduleName, config) {
        // Load dependencies first
        const dependencies = this.dependencies.get(moduleName) || [];
        for (const dep of dependencies) {
            await this.loadModule(dep);
        }
        
        // Determine module path
        const modulePath = this.getModulePath(moduleName);
        
        // Load module script
        await this.loadScript(modulePath);
        
        // Get module class
        const ModuleClass = window[moduleName];
        if (!ModuleClass) {
            throw new Error(`Module class ${moduleName} not found after loading script`);
        }
        
        // Create module instance
        const moduleConfig = { ...this.moduleConfigs.get(moduleName), ...config };
        const module = new ModuleClass(this.core, moduleConfig);
        
        // Initialize module if it has an initialize method
        if (module.initialize && typeof module.initialize === 'function') {
            await module.initialize();
        }
        
        // Execute post-load hooks
        const hooks = this.hooks.get(moduleName) || [];
        for (const hook of hooks) {
            await hook(module);
        }
        
        return module;
    }
    
    /**
     * Unload a module
     */
    async unloadModule(moduleName) {
        const module = this.modules.get(moduleName);
        if (!module) {
            return;
        }
        
        console.log(`📦 Unloading module: ${moduleName}`);
        
        // Call cleanup if available
        if (module.cleanup && typeof module.cleanup === 'function') {
            await module.cleanup();
        }
        
        // Remove from core
        this.core.modules.delete(moduleName);
        this.modules.delete(moduleName);
        
        console.log(`✅ Module unloaded: ${moduleName}`);
        this.core.eventSystem.emit('module:unloaded', { name: moduleName });
    }
    
    /**
     * Reload a module
     */
    async reloadModule(moduleName, config = {}) {
        await this.unloadModule(moduleName);
        return this.loadModule(moduleName, config);
    }
    
    /**
     * Register module dependencies
     */
    registerDependencies(moduleName, dependencies) {
        this.dependencies.set(moduleName, dependencies);
    }
    
    /**
     * Register module configuration
     */
    registerConfig(moduleName, config) {
        this.moduleConfigs.set(moduleName, config);
    }
    
    /**
     * Register post-load hook
     */
    registerHook(moduleName, hook) {
        if (!this.hooks.has(moduleName)) {
            this.hooks.set(moduleName, []);
        }
        this.hooks.get(moduleName).push(hook);
    }
    
    /**
     * Get loaded modules
     */
    getLoadedModules() {
        return Array.from(this.modules.keys());
    }
    
    /**
     * Check if module is loaded
     */
    isModuleLoaded(moduleName) {
        return this.modules.has(moduleName);
    }
    
    /**
     * Get module instance
     */
    getModule(moduleName) {
        return this.modules.get(moduleName);
    }
    
    /**
     * Validate module license
     */
    validateModuleLicense(moduleName) {
        const license = this.core.config.license;
        const licenseType = license.type;
        
        // Check each tier
        for (const [tier, modules] of Object.entries(this.moduleRegistry)) {
            if (modules.includes(moduleName)) {
                return this.isLicenseTierAvailable(tier, licenseType);
            }
        }
        
        // Module not in registry - assume it's a custom module
        return license.features.includes('custom_modules');
    }
    
    isLicenseTierAvailable(tier, licenseType) {
        const tierHierarchy = ['core', 'basic', 'educational', 'commercial', 'enterprise'];
        const currentTierIndex = tierHierarchy.indexOf(licenseType);
        const requiredTierIndex = tierHierarchy.indexOf(tier);
        
        if (currentTierIndex === -1) return tier === 'core'; // Unknown license, only core
        if (requiredTierIndex === -1) return false; // Unknown tier
        
        return currentTierIndex >= requiredTierIndex;
    }
    
    /**
     * Get module path based on naming convention
     */
    getModulePath(moduleName) {
        // Determine module category and path
        if (this.moduleRegistry.core.includes(moduleName)) {
            return `js/engine/${moduleName}.js`;
        } else if (this.moduleRegistry.basic.includes(moduleName) || 
                   this.moduleRegistry.educational.includes(moduleName) ||
                   this.moduleRegistry.commercial.includes(moduleName) ||
                   this.moduleRegistry.enterprise.includes(moduleName)) {
            return `js/modules/${moduleName}.js`;
        } else if (moduleName.includes('Camera') || moduleName.includes('Interface') || moduleName.includes('Calibration')) {
            return `js/hardware/${moduleName}.js`;
        } else {
            return `js/modules/${moduleName}.js`;
        }
    }
    
    /**
     * Load script dynamically
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            const existingScript = document.querySelector(`script[src="${src}"]`);
            if (existingScript) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
            document.head.appendChild(script);
        });
    }
    
    /**
     * Get available modules for current license
     */
    getAvailableModules() {
        const license = this.core.config.license;
        const available = [];
        
        for (const [tier, modules] of Object.entries(this.moduleRegistry)) {
            if (this.isLicenseTierAvailable(tier, license.type)) {
                available.push(...modules);
            }
        }
        
        return available;
    }
    
    /**
     * Get module information
     */
    getModuleInfo(moduleName) {
        const module = this.modules.get(moduleName);
        if (!module) {
            return null;
        }
        
        return {
            name: moduleName,
            loaded: true,
            version: module.version || '1.0.0',
            description: module.description || 'No description available',
            dependencies: this.dependencies.get(moduleName) || [],
            config: this.moduleConfigs.get(moduleName) || {}
        };
    }
    
    /**
     * Export module manager state for debugging
     */
    exportState() {
        return {
            loadedModules: this.getLoadedModules(),
            availableModules: this.getAvailableModules(),
            dependencies: Array.from(this.dependencies.entries()),
            configs: Array.from(this.moduleConfigs.entries()),
            registry: this.moduleRegistry
        };
    }
}

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleManager;
} else {
    window.ModuleManager = ModuleManager;
}
