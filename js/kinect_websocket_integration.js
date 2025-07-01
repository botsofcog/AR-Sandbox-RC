/**
 * Kinect WebSocket Integration Module
 * Connects to the depth server and provides real-time topography data
 */

class KinectWebSocketIntegration {
    constructor(options = {}) {
        this.serverUrl = options.serverUrl || 'ws://localhost:8767'; // Triple Camera Fusion System port
        this.autoReconnect = options.autoReconnect !== false;
        this.reconnectDelay = options.reconnectDelay || 3000;
        this.requestInterval = options.requestInterval || 100; // 10 FPS

        this.websocket = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectTimer = null;
        this.requestTimer = null;

        // Callbacks
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onError = options.onError || (() => {});
        this.onFrameData = options.onFrameData || (() => {});
        this.onTopographyData = options.onTopographyData || (() => {});

        // Data storage
        this.lastFrameData = null;
        this.lastTopographyData = null;

        console.log('🔗 KinectWebSocketIntegration initialized');
    }

    async connect() {
        if (this.isConnected || this.isConnecting) {
            console.log('Already connected or connecting');
            return;
        }

        this.isConnecting = true;
        console.log(`🔗 Connecting to Kinect depth server: ${this.serverUrl}`);

        try {
            this.websocket = new WebSocket(this.serverUrl);

            this.websocket.onopen = () => {
                console.log('✅ Connected to Kinect depth server');
                this.isConnected = true;
                this.isConnecting = false;
                this.onConnect();
                this.startRequestLoop();
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            this.websocket.onclose = () => {
                console.log('❌ Disconnected from Kinect depth server');
                this.isConnected = false;
                this.isConnecting = false;
                this.stopRequestLoop();
                this.onDisconnect();

                if (this.autoReconnect) {
                    this.scheduleReconnect();
                }
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onError(error);
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.isConnecting = false;
            this.onError(error);

            if (this.autoReconnect) {
                this.scheduleReconnect();
            }
        }
    }
    
    async connect() {
        if (this.isConnected || this.isConnecting) {
            console.log('Already connected or connecting');
            return;
        }
        
        this.isConnecting = true;
        console.log(`🔗 Connecting to Kinect depth server: ${this.serverUrl}`);
        
        try {
            this.websocket = new WebSocket(this.serverUrl);
            
            this.websocket.onopen = () => {
                console.log('✅ Connected to Kinect depth server');
                this.isConnected = true;
                this.isConnecting = false;
                this.onConnect();
                this.startRequestLoop();
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('❌ Disconnected from Kinect depth server');
                this.isConnected = false;
                this.isConnecting = false;
                this.stopRequestLoop();
                this.onDisconnect();
                
                if (this.autoReconnect) {
                    this.scheduleReconnect();
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onError(error);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.isConnecting = false;
            this.onError(error);
            
            if (this.autoReconnect) {
                this.scheduleReconnect();
            }
        }
    }
    
    disconnect() {
        this.autoReconnect = false;
        this.stopRequestLoop();
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.isConnected = false;
        this.isConnecting = false;
    }
    
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        console.log(`🔄 Scheduling reconnect in ${this.reconnectDelay}ms`);
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
    }
    
    startRequestLoop() {
        if (this.requestTimer) {
            clearInterval(this.requestTimer);
        }
        
        this.requestTimer = setInterval(() => {
            this.requestFrameData();
        }, this.requestInterval);
    }
    
    stopRequestLoop() {
        if (this.requestTimer) {
            clearInterval(this.requestTimer);
            this.requestTimer = null;
        }
    }
    
    requestFrameData() {
        if (this.isConnected && this.websocket) {
            this.websocket.send(JSON.stringify({
                type: 'get_frame',
                include_topography: true
            }));
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'frame_data':
                this.lastFrameData = data;
                this.onFrameData(data);
                
                if (data.topography) {
                    this.lastTopographyData = data.topography;
                    this.onTopographyData(data.topography);
                }
                break;
                
            case 'pong':
                console.log('📡 Received pong from server');
                break;
                
            case 'error':
                console.error('Server error:', data.message);
                this.onError(new Error(data.message));
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    ping() {
        if (this.isConnected && this.websocket) {
            this.websocket.send(JSON.stringify({ type: 'ping' }));
        }
    }
    
    // Utility methods for terrain data
    getHeightMap() {
        if (this.lastFrameData && this.lastFrameData.mesh_data) {
            return {
                data: this.lastFrameData.mesh_data.data,
                width: this.lastFrameData.mesh_data.width || 100,
                height: this.lastFrameData.mesh_data.height || 75
            };
        }
        return null;
    }
    
    getAIAnalysis() {
        if (this.lastTopographyData && this.lastTopographyData.ai_metadata) {
            return this.lastTopographyData.ai_metadata;
        }
        return null;
    }
    
    getTerrainStats() {
        const ai = this.getAIAnalysis();
        return ai ? ai.terrain_stats : null;
    }
    
    getFeatureDetection() {
        const ai = this.getAIAnalysis();
        return ai ? ai.features : null;
    }
    
    getRecommendations() {
        const ai = this.getAIAnalysis();
        return ai ? ai.recommendations : null;
    }
}

// Global instance for easy access
window.KinectWebSocketIntegration = KinectWebSocketIntegration;

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🚀 KinectWebSocketIntegration module loaded');
    });
} else {
    console.log('🚀 KinectWebSocketIntegration module loaded');
}
