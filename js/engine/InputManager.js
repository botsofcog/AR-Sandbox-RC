/**
 * Input Manager - Professional input handling for AR Sandbox Pro
 */

class InputManager {
    constructor(core, config = {}) {
        this.core = core;
        this.config = {
            touchEnabled: true,
            mouseEnabled: true,
            keyboardEnabled: true,
            ...config
        };
        
        this.inputState = {
            mouse: { x: 0, y: 0, buttons: 0 },
            touch: [],
            keys: new Set()
        };
        
        this.version = '2.0.0';
        this.description = 'Professional input management system';
    }
    
    async initialize() {
        console.log('🎮 Initializing Input Manager...');
        
        this.setupEventListeners();
        
        console.log('✅ Input Manager initialized');
    }
    
    setupEventListeners() {
        const canvas = document.getElementById('mainCanvas');
        
        if (this.config.mouseEnabled) {
            canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
            canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        }
        
        if (this.config.touchEnabled) {
            canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
            canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
            canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e));
        }
        
        if (this.config.keyboardEnabled) {
            document.addEventListener('keydown', (e) => this.handleKeyDown(e));
            document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        }
    }
    
    handleMouseDown(e) {
        this.inputState.mouse.buttons |= (1 << e.button);
        this.core.eventSystem.emit('input:mouseDown', { 
            x: e.clientX, 
            y: e.clientY, 
            button: e.button 
        });
    }
    
    handleMouseMove(e) {
        this.inputState.mouse.x = e.clientX;
        this.inputState.mouse.y = e.clientY;
        this.core.eventSystem.emit('input:mouseMove', { 
            x: e.clientX, 
            y: e.clientY 
        });
    }
    
    handleMouseUp(e) {
        this.inputState.mouse.buttons &= ~(1 << e.button);
        this.core.eventSystem.emit('input:mouseUp', { 
            x: e.clientX, 
            y: e.clientY, 
            button: e.button 
        });
    }
    
    handleTouchStart(e) {
        e.preventDefault();
        this.core.eventSystem.emit('input:touchStart', { 
            touches: Array.from(e.touches) 
        });
    }
    
    handleTouchMove(e) {
        e.preventDefault();
        this.core.eventSystem.emit('input:touchMove', { 
            touches: Array.from(e.touches) 
        });
    }
    
    handleTouchEnd(e) {
        e.preventDefault();
        this.core.eventSystem.emit('input:touchEnd', { 
            touches: Array.from(e.touches) 
        });
    }
    
    handleKeyDown(e) {
        this.inputState.keys.add(e.code);
        this.core.eventSystem.emit('input:keyDown', { 
            code: e.code, 
            key: e.key 
        });
    }
    
    handleKeyUp(e) {
        this.inputState.keys.delete(e.code);
        this.core.eventSystem.emit('input:keyUp', { 
            code: e.code, 
            key: e.key 
        });
    }
    
    async start() {
        console.log('🎮 Input Manager started');
    }
    
    update(deltaTime) {
        // Input processing
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = InputManager;
} else {
    window.InputManager = InputManager;
}
