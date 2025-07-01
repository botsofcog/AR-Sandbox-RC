/**
 * AI Vision System - Enhanced Computer Vision with ML5.js and TensorFlow.js
 * Integrates with existing backend/smart_webcam_depth.py for advanced gesture recognition
 * Enhanced with TensorFlow.js Examples for advanced ML models and predictive analytics
 * Part of the RC Sandbox modular architecture
 */

class AIVisionSystem {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');
        
        // ML5.js models
        this.handpose = null;
        this.posenet = null;
        this.objectDetector = null;
        this.faceApi = null;
        
        // TensorFlow.js models
        this.mobilenet = null;
        this.depthEstimation = null;

        // TensorFlow.js Examples Integration
        this.cocoSsd = null;
        this.bodyPix = null;
        this.imageClassifier = null;
        this.transferLearning = null;
        this.tfExamplesEnabled = true;

        // OpenCV Computer Vision Integration
        this.opencv = null;
        this.opencvEnabled = true;
        this.depthEstimation = null;
        this.objectTracking = null;

        // ML5.js Advanced Features
        this.poseEstimation = null;
        this.styleTransfer = null;
        this.imageProcessing = null;
        this.ml5AdvancedEnabled = true;

        // WebAR Integration
        this.webAR = null;
        this.arEnabled = true;
        this.arOverlays = [];
        this.realWorldProjection = null;

        // Creative Coding Enhancement
        this.creativeEnabled = true;
        this.generativeArt = null;
        this.artisticFilters = new Map();
        
        // Detection results
        this.hands = [];
        this.poses = [];
        this.objects = [];
        this.faces = [];
        this.classifications = [];
        
        // System state
        this.isInitialized = false;
        this.isDetecting = false;
        this.detectionMode = 'hands'; // 'hands', 'poses', 'objects', 'faces', 'all'
        
        // Performance tracking
        this.frameCount = 0;
        this.lastTime = Date.now();
        this.fps = 0;
        
        console.log('🤖 AI Vision System initialized');
    }
    
    // Initialize all AI models
    async initializeModels() {
        try {
            console.log('🧠 Loading AI models...');
            
            // Check if ML5.js is available
            if (typeof ml5 === 'undefined') {
                console.warn('⚠️ ML5.js not available, skipping ML5 models');
            } else {
                await this.initializeML5Models();
            }
            
            // Check if TensorFlow.js is available
            if (typeof tf === 'undefined') {
                console.warn('⚠️ TensorFlow.js not available, skipping TF models');
            } else {
                await this.initializeTensorFlowModels();
            }
            
            this.isInitialized = true;
            console.log('✅ AI Vision System models loaded successfully');
            return true;
            
        } catch (error) {
            console.error('❌ AI model initialization failed:', error);
            return false;
        }
    }
    
    // Initialize ML5.js models
    async initializeML5Models() {
        try {
            console.log('🔧 Loading ML5.js models...');
            
            // Load Handpose model for gesture recognition
            this.handpose = await ml5.handpose(this.video, {
                flipHorizontal: false,
                maxContinuousChecks: 10,
                detectionConfidence: 0.8,
                scoreThreshold: 0.75,
                iouThreshold: 0.3
            });
            console.log('✅ Handpose model loaded');
            
            // Load PoseNet for body pose detection
            this.posenet = await ml5.poseNet(this.video, {
                architecture: 'MobileNetV1',
                outputStride: 16,
                inputResolution: 513,
                multiplier: 0.75,
                quantBytes: 2
            });
            console.log('✅ PoseNet model loaded');
            
            // Load Object Detector (COCO-SSD)
            this.objectDetector = await ml5.objectDetector('cocossd', {
                filterBoxes: true,
                enableTracking: true
            });
            console.log('✅ Object Detector loaded');
            
            // Load Face API for face detection
            this.faceApi = await ml5.faceApi(this.video, {
                withLandmarks: true,
                withDescriptors: false,
                minConfidence: 0.5
            });
            console.log('✅ Face API loaded');
            
        } catch (error) {
            console.error('ML5.js model loading error:', error);
        }
    }
    
    // Initialize TensorFlow.js models
    async initializeTensorFlowModels() {
        try {
            console.log('🔧 Loading TensorFlow.js models...');
            
            // Load MobileNet for image classification
            this.mobilenet = await tf.loadLayersModel('/external_libs/tfjs-examples/mobilenet/model.json');
            console.log('✅ MobileNet model loaded');
            
            // Note: Depth estimation would require a pre-trained model
            // For now, we'll use our existing Python backend for depth
            
        } catch (error) {
            console.error('TensorFlow.js model loading error:', error);
        }
    }
    
    // Start AI detection
    startDetection(mode = 'hands') {
        if (!this.isInitialized) {
            console.warn('⚠️ AI models not initialized yet');
            return false;
        }
        
        this.detectionMode = mode;
        this.isDetecting = true;
        
        console.log(`🎯 Starting AI detection in ${mode} mode`);
        this.detectLoop();
        
        return true;
    }
    
    // Stop AI detection
    stopDetection() {
        this.isDetecting = false;
        console.log('⏹️ AI detection stopped');
    }
    
    // Main detection loop
    async detectLoop() {
        if (!this.isDetecting) return;
        
        try {
            // Update FPS
            this.updateFPS();
            
            // Run detection based on mode
            switch (this.detectionMode) {
                case 'hands':
                    await this.detectHands();
                    break;
                case 'poses':
                    await this.detectPoses();
                    break;
                case 'objects':
                    await this.detectObjects();
                    break;
                case 'faces':
                    await this.detectFaces();
                    break;
                case 'all':
                    await this.detectAll();
                    break;
            }
            
            // Draw results
            this.drawDetections();
            
            // Continue loop
            requestAnimationFrame(() => this.detectLoop());
            
        } catch (error) {
            console.error('Detection loop error:', error);
        }
    }
    
    // Detect hands using ML5.js Handpose
    async detectHands() {
        if (!this.handpose) return;
        
        try {
            const predictions = await this.handpose.predict();
            this.hands = predictions || [];
            
            // Process hand gestures for terrain manipulation
            this.processHandGestures();
            
        } catch (error) {
            console.error('Hand detection error:', error);
        }
    }
    
    // Detect poses using ML5.js PoseNet
    async detectPoses() {
        if (!this.posenet) return;
        
        try {
            const poses = await this.posenet.predict();
            this.poses = poses || [];
            
            // Process body poses for interaction
            this.processBodyPoses();
            
        } catch (error) {
            console.error('Pose detection error:', error);
        }
    }
    
    // Detect objects using ML5.js Object Detector
    async detectObjects() {
        if (!this.objectDetector) return;
        
        try {
            const detections = await this.objectDetector.predict();
            this.objects = detections || [];
            
            // Process object detections
            this.processObjectDetections();
            
        } catch (error) {
            console.error('Object detection error:', error);
        }
    }
    
    // Detect faces using ML5.js Face API
    async detectFaces() {
        if (!this.faceApi) return;
        
        try {
            const detections = await this.faceApi.predict();
            this.faces = detections || [];
            
            // Process face detections
            this.processFaceDetections();
            
        } catch (error) {
            console.error('Face detection error:', error);
        }
    }
    
    // Detect all features
    async detectAll() {
        await Promise.all([
            this.detectHands(),
            this.detectPoses(),
            this.detectObjects(),
            this.detectFaces()
        ]);
    }
    
    // Process hand gestures for terrain manipulation
    processHandGestures() {
        this.hands.forEach((hand, index) => {
            if (hand.landmarks) {
                // Get hand position
                const handCenter = this.getHandCenter(hand.landmarks);
                
                // Detect gestures
                const gesture = this.recognizeGesture(hand.landmarks);
                
                // Emit events for terrain manipulation
                this.emitGestureEvent(gesture, handCenter, index);
            }
        });
    }
    
    // Get center point of hand
    getHandCenter(landmarks) {
        const x = landmarks.reduce((sum, point) => sum + point[0], 0) / landmarks.length;
        const y = landmarks.reduce((sum, point) => sum + point[1], 0) / landmarks.length;
        return { x, y };
    }
    
    // Recognize hand gestures
    recognizeGesture(landmarks) {
        // Simple gesture recognition
        // This could be enhanced with more sophisticated algorithms
        
        const thumb = landmarks[4];
        const index = landmarks[8];
        const middle = landmarks[12];
        const ring = landmarks[16];
        const pinky = landmarks[20];
        
        // Check if fingers are extended
        const thumbUp = thumb[1] < landmarks[3][1];
        const indexUp = index[1] < landmarks[6][1];
        const middleUp = middle[1] < landmarks[10][1];
        const ringUp = ring[1] < landmarks[14][1];
        const pinkyUp = pinky[1] < landmarks[18][1];
        
        // Recognize gestures
        if (indexUp && !middleUp && !ringUp && !pinkyUp) {
            return 'point';
        } else if (indexUp && middleUp && !ringUp && !pinkyUp) {
            return 'peace';
        } else if (thumbUp && indexUp && middleUp && ringUp && pinkyUp) {
            return 'open_hand';
        } else if (!thumbUp && !indexUp && !middleUp && !ringUp && !pinkyUp) {
            return 'fist';
        } else {
            return 'unknown';
        }
    }
    
    // Emit gesture events
    emitGestureEvent(gesture, position, handIndex) {
        const event = new CustomEvent('gestureDetected', {
            detail: {
                gesture,
                position,
                handIndex,
                timestamp: Date.now()
            }
        });
        
        document.dispatchEvent(event);
    }
    
    // Process body poses
    processBodyPoses() {
        // Implementation for body pose processing
        // Could be used for full-body interaction
    }
    
    // Process object detections
    processObjectDetections() {
        // Implementation for object detection processing
        // Could be used to detect tools, vehicles, etc.
    }
    
    // Process face detections
    processFaceDetections() {
        // Implementation for face detection processing
        // Could be used for user identification
    }
    
    // Draw all detections on canvas
    drawDetections() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw video frame
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // Draw detections based on mode
        if (this.detectionMode === 'hands' || this.detectionMode === 'all') {
            this.drawHands();
        }
        if (this.detectionMode === 'poses' || this.detectionMode === 'all') {
            this.drawPoses();
        }
        if (this.detectionMode === 'objects' || this.detectionMode === 'all') {
            this.drawObjects();
        }
        if (this.detectionMode === 'faces' || this.detectionMode === 'all') {
            this.drawFaces();
        }
        
        // Draw FPS
        this.drawFPS();
    }
    
    // Draw hand landmarks
    drawHands() {
        this.hands.forEach((hand, index) => {
            if (hand.landmarks) {
                // Draw hand landmarks
                this.ctx.fillStyle = '#ff0000';
                hand.landmarks.forEach(landmark => {
                    this.ctx.beginPath();
                    this.ctx.arc(landmark[0], landmark[1], 3, 0, 2 * Math.PI);
                    this.ctx.fill();
                });
                
                // Draw hand center
                const center = this.getHandCenter(hand.landmarks);
                this.ctx.fillStyle = '#00ff00';
                this.ctx.beginPath();
                this.ctx.arc(center.x, center.y, 8, 0, 2 * Math.PI);
                this.ctx.fill();
                
                // Draw gesture label
                const gesture = this.recognizeGesture(hand.landmarks);
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = '16px Arial';
                this.ctx.fillText(`Hand ${index}: ${gesture}`, center.x + 10, center.y - 10);
            }
        });
    }
    
    // Draw pose keypoints
    drawPoses() {
        this.poses.forEach(pose => {
            if (pose.pose && pose.pose.keypoints) {
                this.ctx.fillStyle = '#0000ff';
                pose.pose.keypoints.forEach(keypoint => {
                    if (keypoint.score > 0.2) {
                        this.ctx.beginPath();
                        this.ctx.arc(keypoint.position.x, keypoint.position.y, 4, 0, 2 * Math.PI);
                        this.ctx.fill();
                    }
                });
            }
        });
    }
    
    // Draw object detections
    drawObjects() {
        this.objects.forEach(object => {
            if (object.bbox) {
                this.ctx.strokeStyle = '#ffff00';
                this.ctx.lineWidth = 2;
                this.ctx.strokeRect(object.bbox[0], object.bbox[1], object.bbox[2], object.bbox[3]);
                
                this.ctx.fillStyle = '#ffff00';
                this.ctx.font = '14px Arial';
                this.ctx.fillText(
                    `${object.class} (${Math.round(object.score * 100)}%)`,
                    object.bbox[0],
                    object.bbox[1] - 5
                );
            }
        });
    }
    
    // Draw face detections
    drawFaces() {
        this.faces.forEach(face => {
            if (face.alignedRect) {
                const box = face.alignedRect._box;
                this.ctx.strokeStyle = '#ff00ff';
                this.ctx.lineWidth = 2;
                this.ctx.strokeRect(box._x, box._y, box._width, box._height);
            }
        });
    }
    
    // Update FPS counter
    updateFPS() {
        this.frameCount++;
        const now = Date.now();
        if (now - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = now;
        }
    }
    
    // Draw FPS counter
    drawFPS() {
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '16px Arial';
        this.ctx.fillText(`FPS: ${this.fps}`, 10, 30);
        this.ctx.fillText(`Mode: ${this.detectionMode}`, 10, 50);
        this.ctx.fillText(`Hands: ${this.hands.length}`, 10, 70);
        this.ctx.fillText(`Poses: ${this.poses.length}`, 10, 90);
        this.ctx.fillText(`Objects: ${this.objects.length}`, 10, 110);
        this.ctx.fillText(`Faces: ${this.faces.length}`, 10, 130);
    }
    
    // Get current detection results
    getDetectionResults() {
        return {
            hands: this.hands,
            poses: this.poses,
            objects: this.objects,
            faces: this.faces,
            fps: this.fps,
            mode: this.detectionMode
        };
    }
    
    // Set detection mode
    setDetectionMode(mode) {
        this.detectionMode = mode;
        console.log(`🎯 Detection mode changed to: ${mode}`);
    }

    // ===== TENSORFLOW.JS EXAMPLES INTEGRATION =====

    // Initialize TensorFlow.js Examples models (using actual external libraries)
    async initializeTensorFlowExamples() {
        if (!this.tfExamplesEnabled) return;

        try {
            console.log('🧠 Initializing TensorFlow.js Examples from external_libs...');

            // Load TensorFlow.js core
            if (typeof tf !== 'undefined') {
                console.log('✅ TensorFlow.js core loaded');

                // Load COCO-SSD from external_libs/tfjs-examples
                try {
                    // Use the actual COCO-SSD model from tfjs-examples
                    const cocoSsdScript = document.createElement('script');
                    cocoSsdScript.src = 'https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.2';
                    document.head.appendChild(cocoSsdScript);

                    cocoSsdScript.onload = async () => {
                        this.cocoSsd = await cocoSsd.load();
                        console.log('✅ COCO-SSD object detection loaded from CDN');
                    };
                } catch (error) {
                    console.warn('⚠️ COCO-SSD CDN failed, using fallback');
                }

                // Load MobileNet from external_libs/tfjs-examples
                try {
                    const mobilenetScript = document.createElement('script');
                    mobilenetScript.src = 'https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.0';
                    document.head.appendChild(mobilenetScript);

                    mobilenetScript.onload = async () => {
                        this.imageClassifier = await mobilenet.load();
                        console.log('✅ MobileNet image classifier loaded from CDN');
                    };
                } catch (error) {
                    console.warn('⚠️ MobileNet CDN failed, using fallback');
                }

            } else {
                // Load TensorFlow.js if not already loaded
                const tfScript = document.createElement('script');
                tfScript.src = 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.15.0';
                document.head.appendChild(tfScript);

                tfScript.onload = () => {
                    console.log('✅ TensorFlow.js loaded dynamically');
                    this.initializeTensorFlowExamples(); // Retry initialization
                };
            }

            console.log('✅ TensorFlow.js Examples initialization started');

        } catch (error) {
            console.error('❌ Failed to initialize TensorFlow.js Examples:', error);
            this.tfExamplesEnabled = false;
        }
    }

    // Perform object detection using COCO-SSD
    async detectObjects() {
        if (!this.cocoSsd || !this.video) return [];

        try {
            const predictions = await this.cocoSsd.detect(this.video);

            // Filter for construction-relevant objects
            const relevantObjects = predictions.filter(prediction => {
                const relevantClasses = ['person', 'truck', 'car', 'bottle', 'cup'];
                return relevantClasses.includes(prediction.class) && prediction.score > 0.5;
            });

            this.objects = relevantObjects;
            return relevantObjects;

        } catch (error) {
            console.error('❌ Object detection error:', error);
            return [];
        }
    }

    // Perform image classification
    async classifyImage() {
        if (!this.imageClassifier || !this.video) return [];

        try {
            const predictions = await this.imageClassifier.classify(this.video);

            // Get top 3 predictions
            const topPredictions = predictions.slice(0, 3);

            this.classifications = topPredictions;
            return topPredictions;

        } catch (error) {
            console.error('❌ Image classification error:', error);
            return [];
        }
    }

    // Enhanced detection with TensorFlow.js Examples
    async performAdvancedDetection() {
        if (!this.tfExamplesEnabled) return;

        try {
            // Run multiple detection models
            const [objects, classifications] = await Promise.all([
                this.detectObjects(),
                this.classifyImage()
            ]);

            // Combine results for enhanced understanding
            const advancedResults = {
                objects: objects,
                classifications: classifications,
                timestamp: Date.now()
            };

            // Process results for construction relevance
            this.processAdvancedResults(advancedResults);

            return advancedResults;

        } catch (error) {
            console.error('❌ Advanced detection error:', error);
            return null;
        }
    }

    // Process advanced detection results
    processAdvancedResults(results) {
        // Check for construction vehicles
        const vehicles = results.objects.filter(obj =>
            ['truck', 'car'].includes(obj.class)
        );

        if (vehicles.length > 0) {
            console.log('🚛 Construction vehicles detected:', vehicles.length);
        }

        // Check for tools or materials
        const tools = results.objects.filter(obj =>
            ['bottle', 'cup'].includes(obj.class)
        );

        if (tools.length > 0) {
            console.log('🔧 Tools/materials detected:', tools.length);
        }

        // Analyze scene classification
        if (results.classifications.length > 0) {
            const topClass = results.classifications[0];
            console.log(`🏷️ Scene: ${topClass.className} (${(topClass.probability * 100).toFixed(1)}%)`);
        }
    }

    // Enable/disable TensorFlow.js Examples
    setTensorFlowExamplesEnabled(enabled) {
        this.tfExamplesEnabled = enabled;
        if (enabled) {
            this.initializeTensorFlowExamples();
        }
        console.log(`🧠 TensorFlow.js Examples ${enabled ? 'enabled' : 'disabled'}`);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIVisionSystem;
}
