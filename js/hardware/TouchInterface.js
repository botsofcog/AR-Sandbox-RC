/**
 * Touch Interface - Professional multi-touch support for AR Sandbox Pro
 */

class TouchInterface {
    constructor(core, config = {}) {
        this.core = core;
        this.config = {
            maxTouches: 10,
            gestureRecognition: true,
            touchRadius: 20,
            ...config
        };
        
        this.activeTouches = new Map();
        this.gestures = new Map();
        
        this.version = '2.0.0';
        this.description = 'Professional multi-touch interface system';
    }
    
    async initialize() {
        console.log('👆 Initializing Touch Interface...');
        
        this.setupGestureRecognition();
        this.bindTouchEvents();
        
        console.log('✅ Touch Interface initialized');
    }
    
    setupGestureRecognition() {
        // Setup gesture recognition patterns
        this.gestures.set('pinch', {
            minTouches: 2,
            maxTouches: 2,
            pattern: 'pinch'
        });
        
        this.gestures.set('rotate', {
            minTouches: 2,
            maxTouches: 2,
            pattern: 'rotate'
        });
        
        this.gestures.set('pan', {
            minTouches: 1,
            maxTouches: 3,
            pattern: 'pan'
        });
    }
    
    bindTouchEvents() {
        // Listen to input events from InputManager
        this.core.eventSystem.on('input:touchStart', (data) => {
            this.handleTouchStart(data.touches);
        });
        
        this.core.eventSystem.on('input:touchMove', (data) => {
            this.handleTouchMove(data.touches);
        });
        
        this.core.eventSystem.on('input:touchEnd', (data) => {
            this.handleTouchEnd(data.touches);
        });
    }
    
    handleTouchStart(touches) {
        for (const touch of touches) {
            if (this.activeTouches.size >= this.config.maxTouches) break;
            
            this.activeTouches.set(touch.identifier, {
                id: touch.identifier,
                startX: touch.clientX,
                startY: touch.clientY,
                currentX: touch.clientX,
                currentY: touch.clientY,
                startTime: Date.now()
            });
        }
        
        this.recognizeGestures();
        this.core.eventSystem.emit('touch:start', {
            touches: Array.from(this.activeTouches.values())
        });
    }
    
    handleTouchMove(touches) {
        for (const touch of touches) {
            const activeTouch = this.activeTouches.get(touch.identifier);
            if (activeTouch) {
                activeTouch.currentX = touch.clientX;
                activeTouch.currentY = touch.clientY;
            }
        }
        
        this.recognizeGestures();
        this.core.eventSystem.emit('touch:move', {
            touches: Array.from(this.activeTouches.values())
        });
    }
    
    handleTouchEnd(touches) {
        for (const touch of touches) {
            this.activeTouches.delete(touch.identifier);
        }
        
        this.core.eventSystem.emit('touch:end', {
            touches: Array.from(this.activeTouches.values())
        });
    }
    
    recognizeGestures() {
        if (!this.config.gestureRecognition) return;
        
        const touchCount = this.activeTouches.size;
        const touches = Array.from(this.activeTouches.values());
        
        if (touchCount === 2) {
            this.recognizePinchGesture(touches);
            this.recognizeRotateGesture(touches);
        }
        
        if (touchCount >= 1) {
            this.recognizePanGesture(touches);
        }
    }
    
    recognizePinchGesture(touches) {
        if (touches.length !== 2) return;
        
        const [touch1, touch2] = touches;
        
        const startDistance = Math.sqrt(
            Math.pow(touch1.startX - touch2.startX, 2) +
            Math.pow(touch1.startY - touch2.startY, 2)
        );
        
        const currentDistance = Math.sqrt(
            Math.pow(touch1.currentX - touch2.currentX, 2) +
            Math.pow(touch1.currentY - touch2.currentY, 2)
        );
        
        const scale = currentDistance / startDistance;
        
        if (Math.abs(scale - 1.0) > 0.1) {
            this.core.eventSystem.emit('gesture:pinch', {
                scale,
                centerX: (touch1.currentX + touch2.currentX) / 2,
                centerY: (touch1.currentY + touch2.currentY) / 2
            });
        }
    }
    
    recognizeRotateGesture(touches) {
        if (touches.length !== 2) return;
        
        const [touch1, touch2] = touches;
        
        const startAngle = Math.atan2(
            touch2.startY - touch1.startY,
            touch2.startX - touch1.startX
        );
        
        const currentAngle = Math.atan2(
            touch2.currentY - touch1.currentY,
            touch2.currentX - touch1.currentX
        );
        
        const rotation = currentAngle - startAngle;
        
        if (Math.abs(rotation) > 0.1) {
            this.core.eventSystem.emit('gesture:rotate', {
                rotation,
                centerX: (touch1.currentX + touch2.currentX) / 2,
                centerY: (touch1.currentY + touch2.currentY) / 2
            });
        }
    }
    
    recognizePanGesture(touches) {
        if (touches.length === 0) return;
        
        // Calculate average movement
        let totalDeltaX = 0;
        let totalDeltaY = 0;
        
        for (const touch of touches) {
            totalDeltaX += touch.currentX - touch.startX;
            totalDeltaY += touch.currentY - touch.startY;
        }
        
        const avgDeltaX = totalDeltaX / touches.length;
        const avgDeltaY = totalDeltaY / touches.length;
        
        if (Math.abs(avgDeltaX) > 5 || Math.abs(avgDeltaY) > 5) {
            this.core.eventSystem.emit('gesture:pan', {
                deltaX: avgDeltaX,
                deltaY: avgDeltaY,
                touchCount: touches.length
            });
        }
    }
    
    async start() {
        console.log('👆 Touch Interface started');
    }
    
    update(deltaTime) {
        // Touch processing
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = TouchInterface;
} else {
    window.TouchInterface = TouchInterface;
}
