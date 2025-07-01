/**
 * WebSocket Manager - Handles real-time communication with backend services
 * Part of the RC Sandbox modular architecture
 */

class WebSocketManager {
    constructor() {
        this.depthSocket = null;
        this.telemetrySocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
        this.callbacks = {
            onDepthData: null,
            onTelemetryData: null,
            onConnectionChange: null
        };
        
        console.log('🔌 WebSocket Manager initialized');
    }
    
    async connect() {
        try {
            await Promise.all([
                this.connectDepthServer(),
                this.connectTelemetryServer()
            ]);
            
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            if (this.callbacks.onConnectionChange) {
                this.callbacks.onConnectionChange(true);
            }
            
            console.log('✅ All WebSocket connections established');
            
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.scheduleReconnect();
        }
    }
    
    async connectDepthServer() {
        return new Promise((resolve, reject) => {
            try {
                this.depthSocket = new WebSocket('ws://localhost:8765');
                
                this.depthSocket.onopen = () => {
                    console.log('🔍 Depth server connected');
                    resolve();
                };
                
                this.depthSocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (this.callbacks.onDepthData) {
                            this.callbacks.onDepthData(data);
                        }
                    } catch (error) {
                        console.error('❌ Depth data parse error:', error);
                    }
                };
                
                this.depthSocket.onclose = () => {
                    console.log('🔌 Depth server disconnected');
                    this.handleDisconnection();
                };
                
                this.depthSocket.onerror = (error) => {
                    console.error('❌ Depth server error:', error);
                    reject(error);
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    async connectTelemetryServer() {
        return new Promise((resolve, reject) => {
            try {
                this.telemetrySocket = new WebSocket('ws://localhost:8766');
                
                this.telemetrySocket.onopen = () => {
                    console.log('🚛 Telemetry server connected');
                    resolve();
                };
                
                this.telemetrySocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (this.callbacks.onTelemetryData) {
                            this.callbacks.onTelemetryData(data);
                        }
                    } catch (error) {
                        console.error('❌ Telemetry data parse error:', error);
                    }
                };
                
                this.telemetrySocket.onclose = () => {
                    console.log('🔌 Telemetry server disconnected');
                    this.handleDisconnection();
                };
                
                this.telemetrySocket.onerror = (error) => {
                    console.error('❌ Telemetry server error:', error);
                    reject(error);
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    handleDisconnection() {
        this.isConnected = false;
        
        if (this.callbacks.onConnectionChange) {
            this.callbacks.onConnectionChange(false);
        }
        
        this.scheduleReconnect();
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            
            console.log(`🔄 Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
            
            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 10000);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }
    
    sendVehicleCommand(command) {
        if (this.telemetrySocket && this.telemetrySocket.readyState === WebSocket.OPEN) {
            try {
                this.telemetrySocket.send(JSON.stringify(command));
                console.log('📤 Vehicle command sent:', command);
            } catch (error) {
                console.error('❌ Failed to send vehicle command:', error);
            }
        } else {
            console.warn('⚠️ Telemetry socket not connected');
        }
    }
    
    sendDepthCalibration(calibrationData) {
        if (this.depthSocket && this.depthSocket.readyState === WebSocket.OPEN) {
            try {
                const message = {
                    type: 'calibration',
                    data: calibrationData
                };
                this.depthSocket.send(JSON.stringify(message));
                console.log('📤 Depth calibration sent:', calibrationData);
            } catch (error) {
                console.error('❌ Failed to send depth calibration:', error);
            }
        } else {
            console.warn('⚠️ Depth socket not connected');
        }
    }
    
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks };
    }
    
    disconnect() {
        if (this.depthSocket) {
            this.depthSocket.close();
            this.depthSocket = null;
        }
        
        if (this.telemetrySocket) {
            this.telemetrySocket.close();
            this.telemetrySocket = null;
        }
        
        this.isConnected = false;
        console.log('🔌 WebSocket connections closed');
    }
    
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            depthConnected: this.depthSocket && this.depthSocket.readyState === WebSocket.OPEN,
            telemetryConnected: this.telemetrySocket && this.telemetrySocket.readyState === WebSocket.OPEN,
            reconnectAttempts: this.reconnectAttempts
        };
    }
}

// Initialize WebSocket manager and connect to backend services
let websocketManager;
let terrainEngine;
let uiController;
let video;

// FPS tracking
let lastFrameTime = 0;
let frameCount = 0;
let fps = 0;

function initializeApplication() {
    console.log('🚀 Initializing RC Sandbox Application');
    
    // Get video element and start webcam
    video = document.getElementById('video');
    startWebcam();
    
    // Initialize terrain engine
    const canvas = document.getElementById('canvas');
    terrainEngine = new TerrainEngine(canvas);
    
    // Initialize UI controller
    uiController = new UIController(terrainEngine);
    
    // Initialize WebSocket manager
    websocketManager = new WebSocketManager();
    
    // Set up WebSocket callbacks
    websocketManager.setCallbacks({
        onDepthData: handleDepthData,
        onTelemetryData: handleTelemetryData,
        onConnectionChange: handleConnectionChange
    });
    
    // Connect to backend services
    websocketManager.connect();
    
    // Start render loop
    requestAnimationFrame(renderLoop);
    
    // Make websocketManager globally available
    window.websocketManager = websocketManager;
    
    console.log('✅ Application initialized successfully');
}

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            console.log('📹 Webcam started');
        })
        .catch(error => {
            console.warn('⚠️ Webcam not available:', error);
            // Continue without webcam - terrain will still work
        });
}

function handleDepthData(data) {
    // Process depth data from backend
    console.log('📊 Depth data received:', data.format);
    
    // TODO: Integrate depth data with terrain engine
    // This would update the terrain based on real Kinect data
}

function handleTelemetryData(data) {
    // Process vehicle telemetry data
    if (data.vehicles) {
        uiController.updateVehicleData(data);
    }
}

function handleConnectionChange(isConnected) {
    const statusPanel = document.getElementById('status-panel');
    if (statusPanel) {
        const statusIndicator = statusPanel.querySelector('.status-value');
        if (statusIndicator) {
            statusIndicator.textContent = isConnected ? 'LIVE' : 'OFFLINE';
            statusIndicator.style.color = isConnected ? '#4CAF50' : '#ff4444';
        }
    }
    
    if (isConnected) {
        uiController.showNotification('🔗 Backend Connected', 'info');
    } else {
        uiController.showNotification('🔌 Backend Disconnected', 'error');
    }
}

function renderLoop(currentTime) {
    // Calculate FPS
    frameCount++;
    if (currentTime - lastFrameTime >= 1000) {
        fps = frameCount;
        frameCount = 0;
        lastFrameTime = currentTime;
        
        if (uiController) {
            uiController.updateFPS(fps);
        }
    }
    
    // Render terrain
    if (terrainEngine) {
        terrainEngine.render();
    }
    
    requestAnimationFrame(renderLoop);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApplication);

// Export for global access
window.WebSocketManager = WebSocketManager;
