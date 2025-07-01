/**
 * Event System - Professional event management for AR Sandbox Pro
 * Provides pub/sub pattern with advanced features for commercial use
 */

class EventSystem {
    constructor() {
        this.listeners = new Map();
        this.eventHistory = [];
        this.maxHistorySize = 1000;
        this.debugMode = false;
        this.analytics = {
            totalEvents: 0,
            eventCounts: new Map(),
            performanceMetrics: new Map()
        };
    }
    
    /**
     * Subscribe to an event
     * @param {string} eventName - Name of the event
     * @param {function} callback - Callback function
     * @param {object} options - Options (once, priority, context)
     * @returns {function} Unsubscribe function
     */
    on(eventName, callback, options = {}) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }
        
        const listener = {
            callback,
            once: options.once || false,
            priority: options.priority || 0,
            context: options.context || null,
            id: this.generateListenerId()
        };
        
        const listeners = this.listeners.get(eventName);
        listeners.push(listener);
        
        // Sort by priority (higher priority first)
        listeners.sort((a, b) => b.priority - a.priority);
        
        if (this.debugMode) {
            console.log(`📡 Event listener added: ${eventName}`, listener);
        }
        
        // Return unsubscribe function
        return () => this.off(eventName, listener.id);
    }
    
    /**
     * Subscribe to an event once
     */
    once(eventName, callback, options = {}) {
        return this.on(eventName, callback, { ...options, once: true });
    }
    
    /**
     * Unsubscribe from an event
     */
    off(eventName, listenerId) {
        if (!this.listeners.has(eventName)) return;
        
        const listeners = this.listeners.get(eventName);
        const index = listeners.findIndex(l => l.id === listenerId);
        
        if (index !== -1) {
            listeners.splice(index, 1);
            
            if (listeners.length === 0) {
                this.listeners.delete(eventName);
            }
            
            if (this.debugMode) {
                console.log(`📡 Event listener removed: ${eventName}`, listenerId);
            }
        }
    }
    
    /**
     * Emit an event
     */
    emit(eventName, data = {}) {
        const startTime = performance.now();
        
        // Update analytics
        this.analytics.totalEvents++;
        const count = this.analytics.eventCounts.get(eventName) || 0;
        this.analytics.eventCounts.set(eventName, count + 1);
        
        // Add to history
        const eventRecord = {
            name: eventName,
            data,
            timestamp: Date.now(),
            id: this.generateEventId()
        };
        
        this.eventHistory.push(eventRecord);
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.shift();
        }
        
        if (this.debugMode) {
            console.log(`📡 Event emitted: ${eventName}`, data);
        }
        
        // Execute listeners
        if (this.listeners.has(eventName)) {
            const listeners = [...this.listeners.get(eventName)]; // Copy to avoid modification during iteration
            
            for (const listener of listeners) {
                try {
                    if (listener.context) {
                        listener.callback.call(listener.context, data);
                    } else {
                        listener.callback(data);
                    }
                    
                    // Remove once listeners
                    if (listener.once) {
                        this.off(eventName, listener.id);
                    }
                } catch (error) {
                    console.error(`❌ Error in event listener for ${eventName}:`, error);
                }
            }
        }
        
        // Record performance metrics
        const duration = performance.now() - startTime;
        const metrics = this.analytics.performanceMetrics.get(eventName) || { total: 0, count: 0, avg: 0 };
        metrics.total += duration;
        metrics.count++;
        metrics.avg = metrics.total / metrics.count;
        this.analytics.performanceMetrics.set(eventName, metrics);
        
        return eventRecord;
    }
    
    /**
     * Emit an event asynchronously
     */
    async emitAsync(eventName, data = {}) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const result = this.emit(eventName, data);
                resolve(result);
            }, 0);
        });
    }
    
    /**
     * Remove all listeners for an event
     */
    removeAllListeners(eventName) {
        if (eventName) {
            this.listeners.delete(eventName);
        } else {
            this.listeners.clear();
        }
    }
    
    /**
     * Get event analytics
     */
    getAnalytics() {
        return {
            ...this.analytics,
            listenerCounts: Array.from(this.listeners.entries()).map(([name, listeners]) => ({
                event: name,
                count: listeners.length
            })),
            recentEvents: this.eventHistory.slice(-10)
        };
    }
    
    /**
     * Enable/disable debug mode
     */
    setDebugMode(enabled) {
        this.debugMode = enabled;
        console.log(`📡 Event system debug mode: ${enabled ? 'ON' : 'OFF'}`);
    }
    
    /**
     * Get event history
     */
    getEventHistory(eventName = null, limit = 100) {
        let history = this.eventHistory;
        
        if (eventName) {
            history = history.filter(event => event.name === eventName);
        }
        
        return history.slice(-limit);
    }
    
    /**
     * Wait for an event to be emitted
     */
    waitFor(eventName, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const timeoutId = setTimeout(() => {
                unsubscribe();
                reject(new Error(`Event ${eventName} not emitted within ${timeout}ms`));
            }, timeout);
            
            const unsubscribe = this.once(eventName, (data) => {
                clearTimeout(timeoutId);
                resolve(data);
            });
        });
    }
    
    /**
     * Create an event namespace
     */
    namespace(prefix) {
        return {
            on: (eventName, callback, options) => this.on(`${prefix}:${eventName}`, callback, options),
            once: (eventName, callback, options) => this.once(`${prefix}:${eventName}`, callback, options),
            off: (eventName, listenerId) => this.off(`${prefix}:${eventName}`, listenerId),
            emit: (eventName, data) => this.emit(`${prefix}:${eventName}`, data),
            emitAsync: (eventName, data) => this.emitAsync(`${prefix}:${eventName}`, data)
        };
    }
    
    /**
     * Batch emit multiple events
     */
    emitBatch(events) {
        const results = [];
        for (const { name, data } of events) {
            results.push(this.emit(name, data));
        }
        return results;
    }
    
    /**
     * Create event middleware
     */
    use(middleware) {
        // Middleware would intercept events before they're processed
        // Implementation would depend on specific needs
    }
    
    // Private methods
    generateListenerId() {
        return 'listener_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    generateEventId() {
        return 'event_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Export event system state for debugging
     */
    exportState() {
        return {
            listeners: Array.from(this.listeners.entries()).map(([name, listeners]) => ({
                event: name,
                listeners: listeners.map(l => ({
                    id: l.id,
                    priority: l.priority,
                    once: l.once,
                    hasContext: !!l.context
                }))
            })),
            analytics: this.getAnalytics(),
            history: this.eventHistory.slice(-50) // Last 50 events
        };
    }
}

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventSystem;
} else {
    window.EventSystem = EventSystem;
}
