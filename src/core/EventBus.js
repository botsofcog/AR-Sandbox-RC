/**
 * EventBus - Central event management system for AR Sandbox RC
 * Handles communication between modules and external library integrations
 */
export class EventBus {
  constructor() {
    this.listeners = new Map()
    this.onceListeners = new Map()
    this.debugMode = false
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @param {Object} context - Optional context for callback
   */
  on(event, callback, context = null) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    
    this.listeners.get(event).push({
      callback,
      context
    })

    if (this.debugMode) {
      console.log(`📡 EventBus: Registered listener for '${event}'`)
    }
  }

  /**
   * Subscribe to an event once (auto-unsubscribe after first trigger)
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @param {Object} context - Optional context for callback
   */
  once(event, callback, context = null) {
    if (!this.onceListeners.has(event)) {
      this.onceListeners.set(event, [])
    }
    
    this.onceListeners.get(event).push({
      callback,
      context
    })

    if (this.debugMode) {
      console.log(`📡 EventBus: Registered one-time listener for '${event}'`)
    }
  }

  /**
   * Unsubscribe from an event
   * @param {string} event - Event name
   * @param {Function} callback - Callback function to remove
   */
  off(event, callback) {
    const listeners = this.listeners.get(event)
    if (listeners) {
      const index = listeners.findIndex(listener => listener.callback === callback)
      if (index !== -1) {
        listeners.splice(index, 1)
        if (this.debugMode) {
          console.log(`📡 EventBus: Removed listener for '${event}'`)
        }
      }
    }
  }

  /**
   * Emit an event to all subscribers
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data = null) {
    if (this.debugMode) {
      console.log(`📡 EventBus: Emitting '${event}'`, data)
    }

    // Handle regular listeners
    const listeners = this.listeners.get(event) || []
    listeners.forEach(({ callback, context }) => {
      try {
        if (context) {
          callback.call(context, data)
        } else {
          callback(data)
        }
      } catch (error) {
        console.error(`❌ EventBus: Error in listener for '${event}':`, error)
      }
    })

    // Handle one-time listeners
    const onceListeners = this.onceListeners.get(event) || []
    if (onceListeners.length > 0) {
      onceListeners.forEach(({ callback, context }) => {
        try {
          if (context) {
            callback.call(context, data)
          } else {
            callback(data)
          }
        } catch (error) {
          console.error(`❌ EventBus: Error in one-time listener for '${event}':`, error)
        }
      })
      // Clear one-time listeners
      this.onceListeners.delete(event)
    }
  }

  /**
   * Remove all listeners for an event
   * @param {string} event - Event name
   */
  removeAllListeners(event) {
    this.listeners.delete(event)
    this.onceListeners.delete(event)
    if (this.debugMode) {
      console.log(`📡 EventBus: Removed all listeners for '${event}'`)
    }
  }

  /**
   * Get list of all events with listeners
   * @returns {Array} Array of event names
   */
  getEvents() {
    const regularEvents = Array.from(this.listeners.keys())
    const onceEvents = Array.from(this.onceListeners.keys())
    return [...new Set([...regularEvents, ...onceEvents])]
  }

  /**
   * Get listener count for an event
   * @param {string} event - Event name
   * @returns {number} Number of listeners
   */
  getListenerCount(event) {
    const regular = this.listeners.get(event)?.length || 0
    const once = this.onceListeners.get(event)?.length || 0
    return regular + once
  }

  /**
   * Enable/disable debug mode
   * @param {boolean} enabled - Debug mode state
   */
  setDebugMode(enabled) {
    this.debugMode = enabled
    console.log(`📡 EventBus: Debug mode ${enabled ? 'enabled' : 'disabled'}`)
  }

  /**
   * Clear all listeners
   */
  clear() {
    this.listeners.clear()
    this.onceListeners.clear()
    if (this.debugMode) {
      console.log('📡 EventBus: Cleared all listeners')
    }
  }
}

// Common AR Sandbox events
export const EVENTS = {
  // Core system events
  SYSTEM_READY: 'system:ready',
  SYSTEM_ERROR: 'system:error',
  MODULE_LOADED: 'module:loaded',
  MODULE_ERROR: 'module:error',
  
  // Terrain events
  TERRAIN_UPDATED: 'terrain:updated',
  TERRAIN_RESET: 'terrain:reset',
  HEIGHT_CHANGED: 'terrain:height_changed',
  
  // Physics events
  PHYSICS_STEP: 'physics:step',
  COLLISION_DETECTED: 'physics:collision',
  MATERIAL_CHANGED: 'physics:material_changed',
  
  // Vehicle events
  VEHICLE_SPAWNED: 'vehicle:spawned',
  VEHICLE_MOVED: 'vehicle:moved',
  VEHICLE_DESTROYED: 'vehicle:destroyed',
  FLEET_COMMAND: 'vehicle:fleet_command',
  
  // User interaction events
  USER_INPUT: 'user:input',
  GESTURE_DETECTED: 'user:gesture',
  VOICE_COMMAND: 'user:voice',
  
  // AI events
  AI_DECISION: 'ai:decision',
  LEARNING_UPDATE: 'ai:learning',
  PREDICTION_MADE: 'ai:prediction',
  
  // Audio events
  AUDIO_TRIGGER: 'audio:trigger',
  SONIFICATION_UPDATE: 'audio:sonification',
  
  // Performance events
  PERFORMANCE_WARNING: 'performance:warning',
  FPS_UPDATE: 'performance:fps',
  
  // External library events
  LIBRARY_LOADED: 'external:loaded',
  LIBRARY_ERROR: 'external:error',
  INTEGRATION_COMPLETE: 'external:integration_complete'
}
