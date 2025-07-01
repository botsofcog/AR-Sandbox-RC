/**
 * AR Sandbox Pro - Application Entry Point
 * Initializes and starts the commercial AR sandbox platform
 */

// Application configuration
const APP_CONFIG = {
    // Version and build info
    version: '2.0.0',
    buildDate: '2024-01-15',
    environment: 'development', // development, staging, production
    
    // Feature flags
    features: {
        betaFeatures: false,
        debugMode: false,
        telemetry: true,
        autoSave: true,
        cloudSync: false
    },
    
    // Performance settings
    performance: {
        targetFPS: 60,
        adaptiveQuality: true,
        memoryLimit: 512, // MB
        particleLimit: 5000
    },
    
    // Default user preferences
    defaults: {
        theme: 'professional',
        language: 'en',
        units: 'metric',
        autoSave: true,
        soundEnabled: true,
        hapticFeedback: true
    }
};

// Global application state
let app = null;
let startTime = Date.now();

/**
 * Application initialization
 */
async function initializeApplication() {
    try {
        console.log(`🚀 AR Sandbox Pro v${APP_CONFIG.version} - Starting initialization...`);

        // Hide loading screen immediately
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }

        // Check browser compatibility
        if (!checkBrowserCompatibility()) {
            showCompatibilityError();
            return;
        }
        
        // Initialize error handling
        setupErrorHandling();
        
        // Initialize telemetry (if enabled)
        if (APP_CONFIG.features.telemetry) {
            initializeTelemetry();
        }
        
        // Create core application instance
        app = new ARSandboxCore();
        
        // Apply configuration
        applyConfiguration(app);
        
        // Setup development tools (if in development mode)
        if (APP_CONFIG.environment === 'development') {
            setupDevelopmentTools();
        }
        
        // Initialize the core system
        await app.initialize();
        
        // Setup application-level event listeners
        setupApplicationEvents();
        
        // Load user preferences
        await loadUserPreferences();
        
        // Setup auto-save (if enabled)
        if (APP_CONFIG.features.autoSave) {
            setupAutoSave();
        }
        
        // Setup cloud sync (if enabled)
        if (APP_CONFIG.features.cloudSync) {
            await setupCloudSync();
        }
        
        // Mark application as ready
        markApplicationReady();
        
        console.log(`✅ AR Sandbox Pro initialized successfully in ${Date.now() - startTime}ms`);
        
    } catch (error) {
        console.error('❌ Application initialization failed:', error);
        showInitializationError(error);
    }
}

/**
 * Check browser compatibility
 */
function checkBrowserCompatibility() {
    const requirements = {
        webgl: !!window.WebGLRenderingContext,
        webgl2: !!window.WebGL2RenderingContext,
        webrtc: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        websockets: !!window.WebSocket,
        workers: !!window.Worker,
        indexeddb: !!window.indexedDB,
        fullscreen: !!(document.fullscreenEnabled || document.webkitFullscreenEnabled),
        pointerlock: !!(document.pointerLockElement !== undefined || document.mozPointerLockElement !== undefined)
    };
    
    const missing = Object.entries(requirements)
        .filter(([feature, supported]) => !supported)
        .map(([feature]) => feature);
    
    if (missing.length > 0) {
        console.warn('⚠️ Missing browser features:', missing);
        
        // Critical features that prevent operation
        const critical = ['webgl', 'websockets'];
        const criticalMissing = missing.filter(feature => critical.includes(feature));
        
        if (criticalMissing.length > 0) {
            console.error('❌ Critical browser features missing:', criticalMissing);
            return false;
        }
    }
    
    return true;
}

/**
 * Apply configuration to core system
 */
function applyConfiguration(core) {
    // Merge app config with core config
    Object.assign(core.config, {
        targetFPS: APP_CONFIG.performance.targetFPS,
        maxParticles: APP_CONFIG.performance.particleLimit,
        debugMode: APP_CONFIG.features.debugMode
    });
    
    // Set debug mode for event system
    if (APP_CONFIG.features.debugMode) {
        core.eventSystem.setDebugMode(true);
    }
}

/**
 * Setup global error handling
 */
function setupErrorHandling() {
    // Catch unhandled errors
    window.addEventListener('error', (event) => {
        console.error('❌ Unhandled error:', event.error);
        reportError('unhandled_error', event.error);
    });
    
    // Catch unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('❌ Unhandled promise rejection:', event.reason);
        reportError('unhandled_rejection', event.reason);
    });
    
    // WebGL context lost handling
    window.addEventListener('webglcontextlost', (event) => {
        console.warn('⚠️ WebGL context lost');
        event.preventDefault();
        // Attempt to restore context
        setTimeout(() => {
            if (app && app.getModule('RenderEngine')) {
                app.getModule('RenderEngine').restoreContext();
            }
        }, 1000);
    });
}

/**
 * Setup application-level event listeners
 */
function setupApplicationEvents() {
    if (!app) return;
    
    // Listen for core events
    app.eventSystem.on('core:initialized', () => {
        console.log('🎉 Core system initialized');
    });
    
    app.eventSystem.on('core:modeChanged', ({ mode }) => {
        console.log(`🔄 Mode changed to: ${mode}`);
        updateAnalytics('mode_change', { mode });
    });
    
    app.eventSystem.on('core:toolChanged', ({ tool }) => {
        console.log(`🛠️ Tool changed to: ${tool}`);
        updateAnalytics('tool_change', { tool });
    });
    
    // Performance monitoring
    app.eventSystem.on('performance:warning', ({ metric, value }) => {
        console.warn(`⚠️ Performance warning: ${metric} = ${value}`);
    });
    
    // User interaction tracking
    app.eventSystem.on('user:action', (data) => {
        updateAnalytics('user_action', data);
    });
    
    // Error reporting
    app.eventSystem.on('error', (error) => {
        reportError('application_error', error);
    });
}

/**
 * Load user preferences
 */
async function loadUserPreferences() {
    try {
        const preferences = localStorage.getItem('arsandbox_preferences');
        if (preferences) {
            const parsed = JSON.parse(preferences);
            applyUserPreferences(parsed);
        } else {
            // Apply defaults
            applyUserPreferences(APP_CONFIG.defaults);
        }
    } catch (error) {
        console.warn('⚠️ Failed to load user preferences:', error);
        applyUserPreferences(APP_CONFIG.defaults);
    }
}

/**
 * Apply user preferences
 */
function applyUserPreferences(preferences) {
    // Apply theme
    if (preferences.theme) {
        document.body.setAttribute('data-theme', preferences.theme);
    }
    
    // Apply language
    if (preferences.language) {
        document.documentElement.lang = preferences.language;
    }
    
    // Apply other preferences
    if (app) {
        app.config.soundEnabled = preferences.soundEnabled !== false;
        app.config.autoSave = preferences.autoSave !== false;
    }
}

/**
 * Setup auto-save functionality
 */
function setupAutoSave() {
    if (!app) return;
    
    let autoSaveInterval;
    
    const startAutoSave = () => {
        autoSaveInterval = setInterval(() => {
            if (app.state.session.actions > 0) {
                saveApplicationState();
            }
        }, 30000); // Auto-save every 30 seconds
    };
    
    const stopAutoSave = () => {
        if (autoSaveInterval) {
            clearInterval(autoSaveInterval);
        }
    };
    
    // Start auto-save when user becomes active
    app.eventSystem.on('user:active', startAutoSave);
    app.eventSystem.on('user:inactive', stopAutoSave);
    
    // Save on page unload
    window.addEventListener('beforeunload', () => {
        saveApplicationState();
    });
    
    startAutoSave();
}

/**
 * Save application state
 */
function saveApplicationState() {
    try {
        const state = {
            version: APP_CONFIG.version,
            timestamp: Date.now(),
            session: app.state.session,
            mode: app.state.currentMode,
            tool: app.state.activeTool,
            // Additional state would be gathered from modules
        };
        
        localStorage.setItem('arsandbox_autosave', JSON.stringify(state));
        console.log('💾 Application state auto-saved');
    } catch (error) {
        console.warn('⚠️ Failed to auto-save application state:', error);
    }
}

/**
 * Initialize telemetry
 */
function initializeTelemetry() {
    // In a real commercial product, this would connect to analytics service
    console.log('📊 Telemetry initialized');
}

/**
 * Update analytics
 */
function updateAnalytics(event, data) {
    if (!APP_CONFIG.features.telemetry) return;
    
    // In a real product, this would send to analytics service
    console.log(`📊 Analytics: ${event}`, data);
}

/**
 * Report error
 */
function reportError(type, error) {
    if (!APP_CONFIG.features.telemetry) return;
    
    // In a real product, this would send to error reporting service
    console.log(`🐛 Error reported: ${type}`, error);
}

/**
 * Setup development tools
 */
function setupDevelopmentTools() {
    // Add global references for debugging
    window.app = app;
    window.APP_CONFIG = APP_CONFIG;
    
    // Add development shortcuts
    window.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey) {
            switch (e.key) {
                case 'D':
                    e.preventDefault();
                    toggleDebugMode();
                    break;
                case 'R':
                    e.preventDefault();
                    reloadApplication();
                    break;
                case 'C':
                    e.preventDefault();
                    console.log('App State:', app.exportState());
                    break;
            }
        }
    });
    
    console.log('🔧 Development tools enabled');
}

/**
 * Toggle debug mode
 */
function toggleDebugMode() {
    APP_CONFIG.features.debugMode = !APP_CONFIG.features.debugMode;
    if (app) {
        app.eventSystem.setDebugMode(APP_CONFIG.features.debugMode);
    }
    console.log(`🐛 Debug mode: ${APP_CONFIG.features.debugMode ? 'ON' : 'OFF'}`);
}

/**
 * Reload application
 */
function reloadApplication() {
    console.log('🔄 Reloading application...');
    window.location.reload();
}

/**
 * Mark application as ready
 */
function markApplicationReady() {
    document.body.classList.add('app-ready');
    
    // Dispatch ready event
    window.dispatchEvent(new CustomEvent('arsandbox:ready', {
        detail: { app, config: APP_CONFIG }
    }));
}

/**
 * Show compatibility error
 */
function showCompatibilityError() {
    document.body.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #f8fafc; font-family: Arial, sans-serif;">
            <div style="text-align: center; max-width: 500px; padding: 2rem;">
                <h1 style="color: #dc2626; margin-bottom: 1rem;">Browser Not Supported</h1>
                <p style="color: #64748b; margin-bottom: 2rem;">
                    AR Sandbox Pro requires a modern browser with WebGL support. 
                    Please update your browser or try a different one.
                </p>
                <p style="font-size: 0.875rem; color: #94a3b8;">
                    Recommended browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
                </p>
            </div>
        </div>
    `;
}

/**
 * Show initialization error
 */
function showInitializationError(error) {
    console.error('Initialization error details:', error);
    
    document.getElementById('loadingText').textContent = 'Initialization failed';
    document.getElementById('loadingProgress').style.backgroundColor = '#dc2626';
    
    setTimeout(() => {
        alert(`Failed to initialize AR Sandbox Pro:\n\n${error.message}\n\nPlease refresh the page and try again.`);
    }, 1000);
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApplication);
} else {
    initializeApplication();
}
