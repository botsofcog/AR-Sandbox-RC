/**
 * Render Engine - Professional WebGL2 rendering system for AR Sandbox Pro
 * Optimized for commercial installations with high performance requirements
 */

class RenderEngine {
    constructor(core, config = {}) {
        this.core = core;
        this.config = {
            antialias: true,
            alpha: false,
            depth: true,
            stencil: false,
            preserveDrawingBuffer: false,
            powerPreference: 'high-performance',
            failIfMajorPerformanceCaveat: false,
            ...config
        };
        
        this.canvas = null;
        this.gl = null;
        this.programs = new Map();
        this.textures = new Map();
        this.buffers = new Map();
        this.framebuffers = new Map();
        
        this.stats = {
            frameCount: 0,
            fps: 0,
            drawCalls: 0,
            triangles: 0,
            lastFrameTime: 0
        };
        
        this.renderQueue = [];
        this.postProcessStack = [];
        
        this.version = '2.0.0';
        this.description = 'Professional WebGL2 rendering engine';
    }
    
    async initialize() {
        console.log('🎨 Initializing Render Engine...');
        
        // Get canvas
        this.canvas = document.getElementById('mainCanvas');
        if (!this.canvas) {
            throw new Error('Main canvas not found');
        }
        
        // Initialize WebGL2 context
        this.gl = this.canvas.getContext('webgl2', this.config);
        if (!this.gl) {
            // Fallback to WebGL1
            this.gl = this.canvas.getContext('webgl', this.config);
            if (!this.gl) {
                throw new Error('WebGL not supported');
            }
            console.warn('⚠️ Using WebGL1 fallback');
        }
        
        // Setup canvas
        this.setupCanvas();
        
        // Initialize WebGL state
        this.initializeWebGL();
        
        // Load shaders
        await this.loadShaders();
        
        // Setup render targets
        this.setupRenderTargets();
        
        // Initialize performance monitoring
        this.initializePerformanceMonitoring();
        
        console.log('✅ Render Engine initialized');
    }
    
    setupCanvas() {
        // Set canvas size
        this.resize();
        
        // Handle resize events
        window.addEventListener('resize', () => this.resize());
        
        // Handle context loss
        this.canvas.addEventListener('webglcontextlost', (e) => {
            e.preventDefault();
            console.warn('⚠️ WebGL context lost');
            this.core.eventSystem.emit('render:contextLost');
        });
        
        this.canvas.addEventListener('webglcontextrestored', () => {
            console.log('🔄 WebGL context restored');
            this.restoreContext();
        });
    }
    
    resize() {
        const rect = this.canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        
        if (this.gl) {
            this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        }
        
        this.core.eventSystem.emit('render:resize', {
            width: this.canvas.width,
            height: this.canvas.height,
            dpr
        });
    }
    
    initializeWebGL() {
        const gl = this.gl;
        
        // Enable depth testing
        gl.enable(gl.DEPTH_TEST);
        gl.depthFunc(gl.LEQUAL);
        
        // Enable blending for transparency
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
        
        // Enable culling
        gl.enable(gl.CULL_FACE);
        gl.cullFace(gl.BACK);
        
        // Set clear color
        gl.clearColor(0.1, 0.1, 0.1, 1.0);
        
        // Check for extensions
        this.checkExtensions();
    }
    
    checkExtensions() {
        const gl = this.gl;
        const extensions = [
            'OES_texture_float',
            'OES_texture_float_linear',
            'WEBGL_depth_texture',
            'EXT_texture_filter_anisotropic'
        ];
        
        this.extensions = {};
        
        for (const ext of extensions) {
            const extension = gl.getExtension(ext);
            if (extension) {
                this.extensions[ext] = extension;
                console.log(`✅ Extension loaded: ${ext}`);
            } else {
                console.warn(`⚠️ Extension not available: ${ext}`);
            }
        }
    }
    
    async loadShaders() {
        // Basic terrain shader
        await this.createShaderProgram('terrain', {
            vertex: `#version 300 es
                precision highp float;
                
                in vec3 a_position;
                in vec3 a_normal;
                in vec2 a_texCoord;
                in float a_height;
                
                uniform mat4 u_modelViewMatrix;
                uniform mat4 u_projectionMatrix;
                uniform mat3 u_normalMatrix;
                uniform float u_time;
                
                out vec3 v_normal;
                out vec2 v_texCoord;
                out float v_height;
                out vec3 v_worldPos;
                
                void main() {
                    vec4 worldPos = u_modelViewMatrix * vec4(a_position, 1.0);
                    v_worldPos = worldPos.xyz;
                    v_normal = u_normalMatrix * a_normal;
                    v_texCoord = a_texCoord;
                    v_height = a_height;
                    
                    gl_Position = u_projectionMatrix * worldPos;
                }
            `,
            fragment: `#version 300 es
                precision highp float;
                
                in vec3 v_normal;
                in vec2 v_texCoord;
                in float v_height;
                in vec3 v_worldPos;
                
                uniform sampler2D u_heightTexture;
                uniform sampler2D u_normalTexture;
                uniform vec3 u_lightDirection;
                uniform vec3 u_lightColor;
                uniform float u_time;
                
                out vec4 fragColor;
                
                vec3 getTerrainColor(float height) {
                    if (height < 0.2) return vec3(0.4, 0.3, 0.2); // Dark soil
                    if (height < 0.4) return vec3(0.7, 0.6, 0.4); // Sand
                    if (height < 0.7) return vec3(0.8, 0.7, 0.5); // Light sand
                    return vec3(0.6, 0.6, 0.6); // Rock
                }
                
                void main() {
                    vec3 normal = normalize(v_normal);
                    vec3 lightDir = normalize(-u_lightDirection);
                    
                    float diffuse = max(dot(normal, lightDir), 0.0);
                    vec3 baseColor = getTerrainColor(v_height);
                    
                    vec3 color = baseColor * (0.3 + 0.7 * diffuse);
                    
                    fragColor = vec4(color, 1.0);
                }
            `
        });
        
        // Water shader
        await this.createShaderProgram('water', {
            vertex: `#version 300 es
                precision highp float;
                
                in vec3 a_position;
                in vec2 a_texCoord;
                
                uniform mat4 u_modelViewMatrix;
                uniform mat4 u_projectionMatrix;
                uniform float u_time;
                
                out vec2 v_texCoord;
                out vec3 v_worldPos;
                
                void main() {
                    vec4 worldPos = u_modelViewMatrix * vec4(a_position, 1.0);
                    v_worldPos = worldPos.xyz;
                    v_texCoord = a_texCoord;
                    
                    gl_Position = u_projectionMatrix * worldPos;
                }
            `,
            fragment: `#version 300 es
                precision highp float;
                
                in vec2 v_texCoord;
                in vec3 v_worldPos;
                
                uniform float u_time;
                uniform vec3 u_lightDirection;
                
                out vec4 fragColor;
                
                void main() {
                    vec2 uv = v_texCoord + sin(u_time * 0.001 + v_worldPos.xy * 0.1) * 0.01;
                    
                    vec3 waterColor = vec3(0.2, 0.6, 0.8);
                    float alpha = 0.7;
                    
                    // Simple wave effect
                    float wave = sin(u_time * 0.002 + v_worldPos.x * 0.05) * 0.1 + 0.9;
                    waterColor *= wave;
                    
                    fragColor = vec4(waterColor, alpha);
                }
            `
        });
        
        // Particle shader
        await this.createShaderProgram('particles', {
            vertex: `#version 300 es
                precision highp float;
                
                in vec3 a_position;
                in vec4 a_color;
                in float a_size;
                
                uniform mat4 u_modelViewMatrix;
                uniform mat4 u_projectionMatrix;
                
                out vec4 v_color;
                
                void main() {
                    vec4 worldPos = u_modelViewMatrix * vec4(a_position, 1.0);
                    v_color = a_color;
                    
                    gl_Position = u_projectionMatrix * worldPos;
                    gl_PointSize = a_size;
                }
            `,
            fragment: `#version 300 es
                precision highp float;
                
                in vec4 v_color;
                
                out vec4 fragColor;
                
                void main() {
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float dist = length(coord);
                    
                    if (dist > 0.5) discard;
                    
                    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
                    fragColor = vec4(v_color.rgb, v_color.a * alpha);
                }
            `
        });
    }
    
    async createShaderProgram(name, shaders) {
        const gl = this.gl;
        
        // Compile vertex shader
        const vertexShader = this.compileShader(gl.VERTEX_SHADER, shaders.vertex);
        
        // Compile fragment shader
        const fragmentShader = this.compileShader(gl.FRAGMENT_SHADER, shaders.fragment);
        
        // Create program
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            const error = gl.getProgramInfoLog(program);
            gl.deleteProgram(program);
            throw new Error(`Shader program linking failed: ${error}`);
        }
        
        // Get attribute and uniform locations
        const programInfo = {
            program,
            attributes: {},
            uniforms: {}
        };
        
        // Get attributes
        const numAttributes = gl.getProgramParameter(program, gl.ACTIVE_ATTRIBUTES);
        for (let i = 0; i < numAttributes; i++) {
            const attribute = gl.getActiveAttrib(program, i);
            programInfo.attributes[attribute.name] = gl.getAttribLocation(program, attribute.name);
        }
        
        // Get uniforms
        const numUniforms = gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS);
        for (let i = 0; i < numUniforms; i++) {
            const uniform = gl.getActiveUniform(program, i);
            programInfo.uniforms[uniform.name] = gl.getUniformLocation(program, uniform.name);
        }
        
        this.programs.set(name, programInfo);
        
        // Clean up shaders
        gl.deleteShader(vertexShader);
        gl.deleteShader(fragmentShader);
        
        console.log(`✅ Shader program created: ${name}`);
    }
    
    compileShader(type, source) {
        const gl = this.gl;
        const shader = gl.createShader(type);
        
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            const error = gl.getShaderInfoLog(shader);
            gl.deleteShader(shader);
            throw new Error(`Shader compilation failed: ${error}`);
        }
        
        return shader;
    }
    
    setupRenderTargets() {
        // Main render target setup would go here
        // For now, rendering directly to canvas
    }
    
    initializePerformanceMonitoring() {
        setInterval(() => {
            this.updateFPS();
        }, 1000);
    }
    
    updateFPS() {
        this.stats.fps = this.stats.frameCount;
        this.stats.frameCount = 0;
        
        // Update UI
        const fpsElement = document.getElementById('fpsCounter');
        if (fpsElement) {
            fpsElement.textContent = this.stats.fps;
        }
        
        // Emit performance event
        this.core.eventSystem.emit('render:performance', this.stats);
    }
    
    async start() {
        console.log('🎨 Render Engine started');
    }
    
    render() {
        const gl = this.gl;
        const now = performance.now();
        
        // Clear buffers
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        
        // Reset stats
        this.stats.drawCalls = 0;
        this.stats.triangles = 0;
        
        // Process render queue
        this.processRenderQueue();
        
        // Update stats
        this.stats.frameCount++;
        this.stats.lastFrameTime = now;
    }
    
    processRenderQueue() {
        // Render queue processing would go here
        // For now, just a placeholder
    }
    
    restoreContext() {
        // Context restoration logic
        console.log('🔄 Restoring WebGL context...');
        // Would need to recreate all WebGL resources
    }
    
    // Public API methods
    addToRenderQueue(item) {
        this.renderQueue.push(item);
    }
    
    getProgram(name) {
        return this.programs.get(name);
    }
    
    createTexture(name, data, options = {}) {
        // Texture creation logic
    }
    
    createBuffer(name, data, usage = this.gl.STATIC_DRAW) {
        // Buffer creation logic
    }
    
    getStats() {
        return { ...this.stats };
    }
}

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RenderEngine;
} else {
    window.RenderEngine = RenderEngine;
}
