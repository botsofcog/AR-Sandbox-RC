/**
 * Advanced Camera System for AR Sandbox Pro
 * Handles depth sensing, hand tracking, gesture recognition, and calibration systems
 */

class AdvancedCameraSystem {
    constructor(core) {
        this.core = core;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.stream = null;
        
        // Camera state
        this.isActive = false;
        this.isCalibrated = false;
        this.cameraType = 'webcam'; // webcam, kinect, realsense
        
        // Depth sensing
        this.depthData = null;
        this.depthCanvas = null;
        this.depthCtx = null;
        this.depthRange = { min: 0.5, max: 2.0 };
        
        // Hand tracking
        this.handTracker = null;
        this.hands = [];
        this.gestures = [];
        
        // Calibration data
        this.calibration = {
            corners: [],
            transform: null,
            scale: 1.0,
            offset: { x: 0, y: 0 }
        };
        
        // Performance settings
        this.processEveryNthFrame = 2;
        this.frameCounter = 0;
    }
    
    async initialize() {
        console.log('📷 Initializing Advanced Camera System...');
        
        // Create video element
        this.createVideoElement();
        
        // Create depth canvas
        this.createDepthCanvas();
        
        // Initialize camera based on type
        await this.initializeCamera();
        
        // Initialize hand tracking
        await this.initializeHandTracking();
        
        // Setup gesture recognition
        this.setupGestureRecognition();
        
        // Load calibration if available
        this.loadCalibration();
        
        console.log('✅ Advanced Camera System initialized');
    }
    
    createVideoElement() {
        // Remove existing video if any
        const existingVideo = document.getElementById('camera-video');
        if (existingVideo) existingVideo.remove();
        
        this.video = document.createElement('video');
        this.video.id = 'camera-video';
        this.video.width = 640;
        this.video.height = 480;
        this.video.autoplay = true;
        this.video.muted = true;
        this.video.style.position = 'absolute';
        this.video.style.top = '0';
        this.video.style.left = '0';
        this.video.style.zIndex = '1';
        this.video.style.opacity = '0.8';
        document.body.appendChild(this.video);
        
        // Create processing canvas
        this.canvas = document.createElement('canvas');
        this.canvas.width = 640;
        this.canvas.height = 480;
        this.ctx = this.canvas.getContext('2d');
    }
    
    createDepthCanvas() {
        this.depthCanvas = document.createElement('canvas');
        this.depthCanvas.id = 'depth-canvas';
        this.depthCanvas.width = 640;
        this.depthCanvas.height = 480;
        this.depthCanvas.style.position = 'absolute';
        this.depthCanvas.style.top = '0';
        this.depthCanvas.style.left = '0';
        this.depthCanvas.style.zIndex = '5';
        this.depthCanvas.style.pointerEvents = 'none';
        this.depthCanvas.style.opacity = '0.3';
        document.body.appendChild(this.depthCanvas);
        
        this.depthCtx = this.depthCanvas.getContext('2d');
    }
    
    async initializeCamera() {
        try {
            switch (this.cameraType) {
                case 'webcam':
                    await this.initializeWebcam();
                    break;
                case 'kinect':
                    await this.initializeKinect();
                    break;
                case 'realsense':
                    await this.initializeRealSense();
                    break;
            }
            
            this.isActive = true;
            this.startProcessing();
            
        } catch (error) {
            console.error('Failed to initialize camera:', error);
            this.core.uiSystem?.showNotification('Camera initialization failed', 'error');
        }
    }
    
    async initializeWebcam() {
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                frameRate: { ideal: 30 }
            }
        };
        
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);
        this.video.srcObject = this.stream;
        
        return new Promise((resolve) => {
            this.video.onloadedmetadata = () => {
                this.video.play();
                resolve();
            };
        });
    }
    
    async initializeKinect() {
        // Kinect integration would require native bindings or WebUSB
        console.log('Kinect initialization - would require native integration');
        // For now, fall back to webcam
        await this.initializeWebcam();
    }
    
    async initializeRealSense() {
        // RealSense integration would require Intel RealSense SDK
        console.log('RealSense initialization - would require Intel SDK');
        // For now, fall back to webcam
        await this.initializeWebcam();
    }
    
    async initializeHandTracking() {
        try {
            // Using MediaPipe Hands (would need to be loaded)
            if (typeof Hands !== 'undefined') {
                this.handTracker = new Hands({
                    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
                });
                
                this.handTracker.setOptions({
                    maxNumHands: 2,
                    modelComplexity: 1,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.5
                });
                
                this.handTracker.onResults((results) => {
                    this.processHandResults(results);
                });
                
                await this.handTracker.initialize();
            }
        } catch (error) {
            console.warn('Hand tracking not available:', error);
        }
    }
    
    setupGestureRecognition() {
        this.gestureRecognizer = {
            recognizeGesture: (landmarks) => {
                if (!landmarks || landmarks.length === 0) return null;
                
                // Simple gesture recognition
                const hand = landmarks[0];
                
                // Check for pointing gesture
                if (this.isPointingGesture(hand)) {
                    return { type: 'point', confidence: 0.8 };
                }
                
                // Check for grab gesture
                if (this.isGrabGesture(hand)) {
                    return { type: 'grab', confidence: 0.8 };
                }
                
                // Check for open palm
                if (this.isOpenPalmGesture(hand)) {
                    return { type: 'open', confidence: 0.8 };
                }
                
                return null;
            }
        };
    }
    
    isPointingGesture(hand) {
        // Simple pointing detection based on finger positions
        const indexTip = hand[8];
        const indexPip = hand[6];
        const middleTip = hand[12];
        const middlePip = hand[10];
        
        // Index finger extended, middle finger bent
        const indexExtended = indexTip.y < indexPip.y;
        const middleBent = middleTip.y > middlePip.y;
        
        return indexExtended && middleBent;
    }
    
    isGrabGesture(hand) {
        // All fingers bent towards palm
        const fingerTips = [8, 12, 16, 20]; // Index, middle, ring, pinky tips
        const fingerPips = [6, 10, 14, 18]; // Corresponding PIPs
        
        let bentFingers = 0;
        for (let i = 0; i < fingerTips.length; i++) {
            if (hand[fingerTips[i]].y > hand[fingerPips[i]].y) {
                bentFingers++;
            }
        }
        
        return bentFingers >= 3;
    }
    
    isOpenPalmGesture(hand) {
        // All fingers extended
        const fingerTips = [8, 12, 16, 20];
        const fingerPips = [6, 10, 14, 18];
        
        let extendedFingers = 0;
        for (let i = 0; i < fingerTips.length; i++) {
            if (hand[fingerTips[i]].y < hand[fingerPips[i]].y) {
                extendedFingers++;
            }
        }
        
        return extendedFingers >= 3;
    }
    
    startProcessing() {
        const processFrame = () => {
            if (!this.isActive) return;
            
            this.frameCounter++;
            
            // Process every nth frame for performance
            if (this.frameCounter % this.processEveryNthFrame === 0) {
                this.processFrame();
            }
            
            requestAnimationFrame(processFrame);
        };
        
        requestAnimationFrame(processFrame);
    }
    
    processFrame() {
        if (!this.video || this.video.readyState !== 4) return;
        
        // Draw video frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // Get image data for processing
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        
        // Process depth information
        this.processDepthData(imageData);
        
        // Process hand tracking
        if (this.handTracker) {
            this.handTracker.send({ image: this.canvas });
        }
        
        // Update terrain based on depth data
        this.updateTerrainFromDepth();
    }
    
    processDepthData(imageData) {
        // Simple depth estimation from color/brightness
        // In a real implementation, this would use actual depth sensors
        
        const data = imageData.data;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        if (!this.depthData) {
            this.depthData = new Float32Array(width * height);
        }
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const index = (y * width + x) * 4;
                const r = data[index];
                const g = data[index + 1];
                const b = data[index + 2];
                
                // Simple brightness-based depth estimation
                const brightness = (r + g + b) / 3;
                const depth = this.depthRange.min + (1 - brightness / 255) * (this.depthRange.max - this.depthRange.min);
                
                this.depthData[y * width + x] = depth;
            }
        }
        
        // Visualize depth data
        this.visualizeDepthData();
    }
    
    visualizeDepthData() {
        if (!this.depthData) return;
        
        const imageData = this.depthCtx.createImageData(this.depthCanvas.width, this.depthCanvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < this.depthData.length; i++) {
            const depth = this.depthData[i];
            const normalizedDepth = (depth - this.depthRange.min) / (this.depthRange.max - this.depthRange.min);
            const intensity = Math.floor((1 - normalizedDepth) * 255);
            
            const pixelIndex = i * 4;
            data[pixelIndex] = intensity;     // R
            data[pixelIndex + 1] = intensity; // G
            data[pixelIndex + 2] = intensity; // B
            data[pixelIndex + 3] = 128;       // A (semi-transparent)
        }
        
        this.depthCtx.putImageData(imageData, 0, 0);
    }
    
    processHandResults(results) {
        this.hands = results.multiHandLandmarks || [];
        
        // Process gestures
        this.gestures = [];
        for (const hand of this.hands) {
            const gesture = this.gestureRecognizer.recognizeGesture(hand);
            if (gesture) {
                this.gestures.push({
                    ...gesture,
                    landmarks: hand,
                    position: this.getHandPosition(hand)
                });
            }
        }
        
        // Apply gestures to terrain
        this.applyGesturesToTerrain();
    }
    
    getHandPosition(landmarks) {
        // Get center of hand (palm)
        const palmBase = landmarks[0];
        
        // Convert to screen coordinates
        const x = palmBase.x * this.canvas.width;
        const y = palmBase.y * this.canvas.height;
        
        // Apply calibration transform if available
        if (this.isCalibrated && this.calibration.transform) {
            // Apply transformation matrix
            return this.applyCalibrationTransform(x, y);
        }
        
        return { x, y };
    }
    
    applyGesturesToTerrain() {
        if (!this.core.terrainEngine) return;
        
        for (const gesture of this.gestures) {
            const terrainX = Math.floor(gesture.position.x / 4);
            const terrainY = Math.floor(gesture.position.y / 4);
            
            switch (gesture.type) {
                case 'point':
                    // Point gesture - precise editing
                    this.core.terrainEngine.modifyTerrain(terrainX, terrainY);
                    break;
                    
                case 'grab':
                    // Grab gesture - move terrain
                    this.core.state.tool = 'raise';
                    this.core.terrainEngine.modifyTerrain(terrainX, terrainY);
                    break;
                    
                case 'open':
                    // Open palm - smooth terrain
                    this.core.state.tool = 'smooth';
                    this.core.terrainEngine.modifyTerrain(terrainX, terrainY);
                    break;
            }
        }
    }
    
    updateTerrainFromDepth() {
        if (!this.core.terrainEngine || !this.depthData || !this.isCalibrated) return;
        
        // Map depth data to terrain height
        const terrain = this.core.terrainEngine;
        const scaleX = terrain.width / this.canvas.width;
        const scaleY = terrain.height / this.canvas.height;
        
        for (let y = 0; y < terrain.height; y++) {
            for (let x = 0; x < terrain.width; x++) {
                const depthX = Math.floor(x / scaleX);
                const depthY = Math.floor(y / scaleY);
                const depthIndex = depthY * this.canvas.width + depthX;
                
                if (depthIndex >= 0 && depthIndex < this.depthData.length) {
                    const depth = this.depthData[depthIndex];
                    const normalizedHeight = 1 - ((depth - this.depthRange.min) / (this.depthRange.max - this.depthRange.min));
                    const terrainIndex = y * terrain.width + x;
                    
                    // Smooth transition to avoid jitter
                    const currentHeight = terrain.heightMap[terrainIndex];
                    const targetHeight = Math.max(0, Math.min(1, normalizedHeight));
                    terrain.heightMap[terrainIndex] = currentHeight * 0.9 + targetHeight * 0.1;
                    
                    // Update terrain type
                    terrain.updateTerrainType(terrainIndex);
                }
            }
        }
    }
    
    calibrate() {
        // Start calibration process
        this.core.uiSystem?.showNotification('Starting calibration - place markers at corners', 'info');
        
        // Reset calibration data
        this.calibration.corners = [];
        this.isCalibrated = false;
        
        // Set up click handlers for corner selection
        this.setupCalibrationClickHandlers();
    }
    
    setupCalibrationClickHandlers() {
        const clickHandler = (e) => {
            const rect = this.video.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.calibration.corners.push({ x, y });
            
            if (this.calibration.corners.length === 4) {
                this.completeCalibration();
                this.video.removeEventListener('click', clickHandler);
            } else {
                this.core.uiSystem?.showNotification(
                    `Corner ${this.calibration.corners.length}/4 marked`, 
                    'info'
                );
            }
        };
        
        this.video.addEventListener('click', clickHandler);
    }
    
    completeCalibration() {
        // Calculate transformation matrix from corners
        this.calculateCalibrationTransform();
        this.isCalibrated = true;
        
        this.core.uiSystem?.showNotification('Calibration complete!', 'success');
        
        // Save calibration
        this.saveCalibration();
    }
    
    calculateCalibrationTransform() {
        // Simple 4-point perspective transform
        // In a real implementation, this would use proper homography calculation
        const corners = this.calibration.corners;
        
        if (corners.length === 4) {
            // Calculate bounding box
            const minX = Math.min(...corners.map(c => c.x));
            const maxX = Math.max(...corners.map(c => c.x));
            const minY = Math.min(...corners.map(c => c.y));
            const maxY = Math.max(...corners.map(c => c.y));
            
            this.calibration.transform = {
                minX, maxX, minY, maxY,
                scaleX: this.canvas.width / (maxX - minX),
                scaleY: this.canvas.height / (maxY - minY)
            };
        }
    }
    
    applyCalibrationTransform(x, y) {
        if (!this.calibration.transform) return { x, y };
        
        const transform = this.calibration.transform;
        
        // Apply perspective correction
        const normalizedX = (x - transform.minX) * transform.scaleX;
        const normalizedY = (y - transform.minY) * transform.scaleY;
        
        return {
            x: normalizedX + this.calibration.offset.x,
            y: normalizedY + this.calibration.offset.y
        };
    }
    
    saveCalibration() {
        localStorage.setItem('ar-sandbox-calibration', JSON.stringify(this.calibration));
    }
    
    loadCalibration() {
        try {
            const saved = localStorage.getItem('ar-sandbox-calibration');
            if (saved) {
                this.calibration = JSON.parse(saved);
                this.isCalibrated = !!this.calibration.transform;
                
                if (this.isCalibrated) {
                    this.core.uiSystem?.showNotification('Calibration loaded', 'success');
                }
            }
        } catch (error) {
            console.warn('Failed to load calibration:', error);
        }
    }
    
    update(deltaTime) {
        // Update camera system
        if (this.isActive) {
            // Update any time-based processing
        }
    }
    
    setDepthRange(min, max) {
        this.depthRange.min = min;
        this.depthRange.max = max;
    }
    
    setCameraType(type) {
        this.cameraType = type;
        // Reinitialize camera with new type
        this.initializeCamera();
    }
    
    destroy() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        
        if (this.video) {
            this.video.remove();
        }
        
        if (this.depthCanvas) {
            this.depthCanvas.remove();
        }
        
        this.isActive = false;
    }
}
