/**
 * SandboxCore - Central management system for AR Sandbox RC
 * Coordinates all modules and external library integrations
 */
import { EventBus, EVENTS } from './EventBus.js'
import { Module } from './Module.js'

export class SandboxCore {
  constructor(config = {}) {
    this.config = {
      debug: false,
      performance: {
        targetFPS: 60,
        maxUpdateTime: 16.67, // 60fps = 16.67ms per frame
        performanceWarningThreshold: 20
      },
      modules: {},
      ...config
    }
    
    this.eventBus = new EventBus()
    this.modules = new Map()
    this.updateLoop = null
    this.lastUpdateTime = 0
    this.deltaTime = 0
    this.fps = 0
    this.frameCount = 0
    this.running = false
    
    // Performance monitoring
    this.performance = {
      frameTime: 0,
      updateTime: 0,
      renderTime: 0,
      totalTime: 0,
      warnings: []
    }
    
    // Setup debug mode
    if (this.config.debug) {
      this.eventBus.setDebugMode(true)
      console.log('🔧 SandboxCore: Debug mode enabled')
    }
    
    // Setup performance monitoring
    this.setupPerformanceMonitoring()
  }

  /**
   * Initialize the AR Sandbox system
   */
  async init() {
    console.log('🚀 SandboxCore: Initializing AR Sandbox RC system...')
    
    try {
      // Initialize all registered modules
      await this.initializeModules()
      
      // Start the update loop
      this.start()
      
      this.eventBus.emit(EVENTS.SYSTEM_READY, {
        moduleCount: this.modules.size,
        config: this.config
      })
      
      console.log('✅ SandboxCore: System initialization complete!')
      
    } catch (error) {
      console.error('❌ SandboxCore: System initialization failed:', error)
      this.eventBus.emit(EVENTS.SYSTEM_ERROR, { error: error.message })
      throw error
    }
  }

  /**
   * Register a module with the system
   * @param {Module} module - Module instance
   */
  registerModule(module) {
    if (!(module instanceof Module)) {
      throw new Error('Module must extend the Module base class')
    }
    
    if (this.modules.has(module.name)) {
      console.warn(`⚠️ SandboxCore: Module '${module.name}' already registered, replacing...`)
    }
    
    this.modules.set(module.name, module)
    console.log(`📦 SandboxCore: Registered module '${module.name}'`)
  }

  /**
   * Get a module by name
   * @param {string} name - Module name
   * @returns {Module|null} Module instance or null
   */
  getModule(name) {
    return this.modules.get(name) || null
  }

  /**
   * Initialize all registered modules
   */
  async initializeModules() {
    const moduleArray = Array.from(this.modules.values())
    
    // Sort modules by dependencies (simple dependency resolution)
    const sortedModules = this.resolveDependencies(moduleArray)
    
    for (const module of sortedModules) {
      const moduleConfig = this.config.modules[module.name] || {}
      await module.init(this.eventBus, moduleConfig)
    }
  }

  /**
   * Simple dependency resolution for modules
   * @param {Array} modules - Array of modules
   * @returns {Array} Sorted modules
   */
  resolveDependencies(modules) {
    const resolved = []
    const unresolved = [...modules]
    
    while (unresolved.length > 0) {
      const module = unresolved.shift()
      
      // Check if all dependencies are resolved
      const dependenciesResolved = module.dependencies.every(dep => 
        resolved.some(resolvedModule => resolvedModule.name === dep) ||
        this.isDependencyExternal(dep)
      )
      
      if (dependenciesResolved) {
        resolved.push(module)
      } else {
        // Put back at end of queue
        unresolved.push(module)
        
        // Prevent infinite loop
        if (unresolved.length > 100) {
          console.warn('⚠️ SandboxCore: Possible circular dependency detected')
          break
        }
      }
    }
    
    return resolved
  }

  /**
   * Check if dependency is external (like Three.js, etc.)
   * @param {string} dependency - Dependency name
   * @returns {boolean} True if external
   */
  isDependencyExternal(dependency) {
    const externalDeps = ['three', 'cannon', 'matter', 'tone', 'ml5', 'tensorflow']
    return externalDeps.includes(dependency)
  }

  /**
   * Start the update loop
   */
  start() {
    if (this.running) {
      return
    }
    
    this.running = true
    this.lastUpdateTime = performance.now()
    this.updateLoop = requestAnimationFrame(this.update.bind(this))
    
    console.log('▶️ SandboxCore: Update loop started')
  }

  /**
   * Stop the update loop
   */
  stop() {
    if (!this.running) {
      return
    }
    
    this.running = false
    if (this.updateLoop) {
      cancelAnimationFrame(this.updateLoop)
      this.updateLoop = null
    }
    
    console.log('⏹️ SandboxCore: Update loop stopped')
  }

  /**
   * Main update loop
   */
  update() {
    if (!this.running) {
      return
    }
    
    const currentTime = performance.now()
    this.deltaTime = currentTime - this.lastUpdateTime
    this.lastUpdateTime = currentTime
    
    // Update FPS
    this.frameCount++
    if (this.frameCount % 60 === 0) {
      this.fps = Math.round(1000 / this.deltaTime)
      this.eventBus.emit(EVENTS.FPS_UPDATE, { fps: this.fps })
    }
    
    // Performance monitoring start
    const updateStartTime = performance.now()
    
    try {
      // Update all modules
      for (const module of this.modules.values()) {
        module.update(this.deltaTime)
      }
      
      // Performance monitoring end
      this.performance.updateTime = performance.now() - updateStartTime
      this.performance.frameTime = this.deltaTime
      
      // Check for performance warnings
      this.checkPerformance()
      
    } catch (error) {
      console.error('❌ SandboxCore: Error in update loop:', error)
      this.eventBus.emit(EVENTS.SYSTEM_ERROR, { error: error.message })
    }
    
    // Schedule next update
    this.updateLoop = requestAnimationFrame(this.update.bind(this))
  }

  /**
   * Setup performance monitoring
   */
  setupPerformanceMonitoring() {
    this.eventBus.on(EVENTS.PERFORMANCE_WARNING, (data) => {
      this.performance.warnings.push({
        timestamp: Date.now(),
        ...data
      })
      
      // Keep only last 100 warnings
      if (this.performance.warnings.length > 100) {
        this.performance.warnings = this.performance.warnings.slice(-100)
      }
    })
  }

  /**
   * Check performance and emit warnings if needed
   */
  checkPerformance() {
    const threshold = this.config.performance.performanceWarningThreshold
    
    if (this.performance.updateTime > threshold) {
      this.eventBus.emit(EVENTS.PERFORMANCE_WARNING, {
        type: 'update_time',
        value: this.performance.updateTime,
        threshold: threshold
      })
    }
    
    if (this.fps < 30 && this.frameCount > 60) {
      this.eventBus.emit(EVENTS.PERFORMANCE_WARNING, {
        type: 'low_fps',
        value: this.fps,
        threshold: 30
      })
    }
  }

  /**
   * Get system status
   * @returns {Object} System status
   */
  getStatus() {
    const moduleStatuses = {}
    for (const [name, module] of this.modules) {
      moduleStatuses[name] = module.getStatus()
    }
    
    return {
      running: this.running,
      fps: this.fps,
      deltaTime: this.deltaTime,
      performance: { ...this.performance },
      modules: moduleStatuses,
      eventBus: {
        events: this.eventBus.getEvents(),
        totalListeners: this.eventBus.getEvents().reduce((total, event) => 
          total + this.eventBus.getListenerCount(event), 0)
      }
    }
  }

  /**
   * Destroy the system and clean up resources
   */
  destroy() {
    console.log('🗑️ SandboxCore: Destroying system...')
    
    this.stop()
    
    // Destroy all modules
    for (const module of this.modules.values()) {
      module.destroy()
    }
    
    this.modules.clear()
    this.eventBus.clear()
    
    console.log('✅ SandboxCore: System destroyed')
  }
}
