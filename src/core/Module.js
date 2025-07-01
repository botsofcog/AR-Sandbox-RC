/**
 * Module - Base class for all AR Sandbox RC modules
 * Provides standardized interface for external library integration
 */
export class Module {
  constructor(name, dependencies = []) {
    this.name = name
    this.dependencies = dependencies
    this.initialized = false
    this.enabled = true
    this.eventBus = null
    this.config = null
    this.performance = {
      initTime: 0,
      lastUpdateTime: 0,
      updateCount: 0,
      averageUpdateTime: 0
    }
  }

  /**
   * Initialize the module
   * @param {EventBus} eventBus - Central event bus
   * @param {Object} config - Module configuration
   */
  async init(eventBus, config) {
    const startTime = performance.now()
    
    this.eventBus = eventBus
    this.config = config
    
    try {
      // Check dependencies
      await this.checkDependencies()
      
      // Initialize module-specific functionality
      await this.onInit()
      
      this.initialized = true
      this.performance.initTime = performance.now() - startTime
      
      this.eventBus.emit('module:loaded', {
        name: this.name,
        initTime: this.performance.initTime
      })
      
      console.log(`✅ Module '${this.name}' initialized in ${this.performance.initTime.toFixed(2)}ms`)
      
    } catch (error) {
      console.error(`❌ Failed to initialize module '${this.name}':`, error)
      this.eventBus.emit('module:error', {
        name: this.name,
        error: error.message
      })
      throw error
    }
  }

  /**
   * Check if all dependencies are available
   */
  async checkDependencies() {
    for (const dependency of this.dependencies) {
      if (!this.isDependencyAvailable(dependency)) {
        throw new Error(`Dependency '${dependency}' not available for module '${this.name}'`)
      }
    }
  }

  /**
   * Check if a specific dependency is available
   * @param {string} dependency - Dependency name
   * @returns {boolean} True if available
   */
  isDependencyAvailable(dependency) {
    // Check for common dependencies
    switch (dependency) {
      case 'three':
        return typeof THREE !== 'undefined'
      case 'cannon':
        return typeof CANNON !== 'undefined'
      case 'matter':
        return typeof Matter !== 'undefined'
      case 'tone':
        return typeof Tone !== 'undefined'
      case 'ml5':
        return typeof ml5 !== 'undefined'
      case 'tensorflow':
        return typeof tf !== 'undefined'
      default:
        return true // Assume available for custom dependencies
    }
  }

  /**
   * Module-specific initialization (override in subclasses)
   */
  async onInit() {
    // Override in subclasses
  }

  /**
   * Update module (called each frame)
   * @param {number} deltaTime - Time since last update
   */
  update(deltaTime) {
    if (!this.initialized || !this.enabled) {
      return
    }

    const startTime = performance.now()
    
    try {
      this.onUpdate(deltaTime)
      
      // Update performance metrics
      const updateTime = performance.now() - startTime
      this.performance.lastUpdateTime = updateTime
      this.performance.updateCount++
      this.performance.averageUpdateTime = 
        (this.performance.averageUpdateTime * (this.performance.updateCount - 1) + updateTime) / 
        this.performance.updateCount
        
    } catch (error) {
      console.error(`❌ Error updating module '${this.name}':`, error)
    }
  }

  /**
   * Module-specific update logic (override in subclasses)
   * @param {number} deltaTime - Time since last update
   */
  onUpdate(deltaTime) {
    // Override in subclasses
  }

  /**
   * Destroy module and clean up resources
   */
  destroy() {
    try {
      this.onDestroy()
      this.initialized = false
      this.enabled = false
      
      console.log(`🗑️ Module '${this.name}' destroyed`)
      
    } catch (error) {
      console.error(`❌ Error destroying module '${this.name}':`, error)
    }
  }

  /**
   * Module-specific cleanup (override in subclasses)
   */
  onDestroy() {
    // Override in subclasses
  }

  /**
   * Enable/disable module
   * @param {boolean} enabled - Module state
   */
  setEnabled(enabled) {
    this.enabled = enabled
    console.log(`${enabled ? '▶️' : '⏸️'} Module '${this.name}' ${enabled ? 'enabled' : 'disabled'}`)
  }

  /**
   * Get module status
   * @returns {Object} Module status information
   */
  getStatus() {
    return {
      name: this.name,
      initialized: this.initialized,
      enabled: this.enabled,
      dependencies: this.dependencies,
      performance: { ...this.performance }
    }
  }

  /**
   * Emit event through the event bus
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (this.eventBus) {
      this.eventBus.emit(event, data)
    }
  }

  /**
   * Subscribe to event through the event bus
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (this.eventBus) {
      this.eventBus.on(event, callback, this)
    }
  }

  /**
   * Subscribe to event once through the event bus
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  once(event, callback) {
    if (this.eventBus) {
      this.eventBus.once(event, callback, this)
    }
  }

  /**
   * Get configuration value
   * @param {string} key - Configuration key
   * @param {*} defaultValue - Default value if key not found
   * @returns {*} Configuration value
   */
  getConfig(key, defaultValue = null) {
    if (!this.config) {
      return defaultValue
    }
    
    const keys = key.split('.')
    let value = this.config
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return defaultValue
      }
    }
    
    return value
  }

  /**
   * Log message with module context
   * @param {string} level - Log level (info, warn, error)
   * @param {string} message - Log message
   * @param {*} data - Additional data
   */
  log(level, message, data = null) {
    const prefix = `[${this.name}]`
    
    switch (level) {
      case 'info':
        console.log(`ℹ️ ${prefix} ${message}`, data || '')
        break
      case 'warn':
        console.warn(`⚠️ ${prefix} ${message}`, data || '')
        break
      case 'error':
        console.error(`❌ ${prefix} ${message}`, data || '')
        break
      default:
        console.log(`${prefix} ${message}`, data || '')
    }
  }
}
