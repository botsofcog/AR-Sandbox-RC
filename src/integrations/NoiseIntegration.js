/**
 * NoiseIntegration - Integration wrapper for Noise.js library
 * Provides procedural terrain generation capabilities
 */
import { libraryLoader, LIBRARY_CONFIGS } from '../utils/ExternalLibraryLoader.js'

export class NoiseIntegration {
  constructor() {
    this.noise = null
    this.initialized = false
    this.generators = new Map()
    this.seeds = new Map()
  }

  /**
   * Initialize Noise.js integration
   * @returns {Promise<boolean>} Success status
   */
  async init() {
    try {
      console.log('🌊 Initializing Noise.js integration...')
      
      // Load Noise.js library
      this.noise = await libraryLoader.loadLibrary(
        LIBRARY_CONFIGS.noise.name,
        LIBRARY_CONFIGS.noise.path,
        LIBRARY_CONFIGS.noise.options
      )
      
      if (!this.noise || !this.noise.noise) {
        throw new Error('Noise.js library not properly loaded')
      }
      
      // Setup default generators
      this.setupDefaultGenerators()
      
      this.initialized = true
      console.log('✅ Noise.js integration initialized successfully')
      
      return true
      
    } catch (error) {
      console.error('❌ Failed to initialize Noise.js integration:', error)
      
      // Setup fallback noise generators
      this.setupFallbackGenerators()
      this.initialized = true
      
      console.log('🔄 Using fallback noise generators')
      return false
    }
  }

  /**
   * Setup default noise generators using Noise.js
   */
  setupDefaultGenerators() {
    // Perlin noise generator
    this.generators.set('perlin', (x, y, z = 0) => {
      return this.noise.noise.perlin3(x, y, z)
    })
    
    // Simplex noise generator
    this.generators.set('simplex', (x, y, z = 0) => {
      return this.noise.noise.simplex3(x, y, z)
    })
    
    // Perlin noise 2D
    this.generators.set('perlin2d', (x, y) => {
      return this.noise.noise.perlin2(x, y)
    })
    
    // Simplex noise 2D
    this.generators.set('simplex2d', (x, y) => {
      return this.noise.noise.simplex2(x, y)
    })
    
    // Fractal noise (multiple octaves)
    this.generators.set('fractal', (x, y, octaves = 4, persistence = 0.5, scale = 1) => {
      let value = 0
      let amplitude = 1
      let frequency = scale
      let maxValue = 0
      
      for (let i = 0; i < octaves; i++) {
        value += this.noise.noise.perlin2(x * frequency, y * frequency) * amplitude
        maxValue += amplitude
        amplitude *= persistence
        frequency *= 2
      }
      
      return value / maxValue
    })
    
    // Ridge noise (inverted fractal)
    this.generators.set('ridge', (x, y, octaves = 4, persistence = 0.5, scale = 1) => {
      let value = 0
      let amplitude = 1
      let frequency = scale
      let maxValue = 0
      
      for (let i = 0; i < octaves; i++) {
        const sample = Math.abs(this.noise.noise.perlin2(x * frequency, y * frequency))
        value += (1 - sample) * amplitude
        maxValue += amplitude
        amplitude *= persistence
        frequency *= 2
      }
      
      return value / maxValue
    })
    
    // Turbulence noise
    this.generators.set('turbulence', (x, y, octaves = 4, scale = 1) => {
      let value = 0
      let frequency = scale
      
      for (let i = 0; i < octaves; i++) {
        value += Math.abs(this.noise.noise.perlin2(x * frequency, y * frequency)) / frequency
        frequency *= 2
      }
      
      return value
    })
  }

  /**
   * Setup fallback noise generators (simple implementations)
   */
  setupFallbackGenerators() {
    console.log('🔄 Setting up fallback noise generators...')
    
    // Simple pseudo-random noise
    this.generators.set('perlin', (x, y, z = 0) => {
      return this.simpleNoise(x, y, z)
    })
    
    this.generators.set('simplex', (x, y, z = 0) => {
      return this.simpleNoise(x, y, z)
    })
    
    this.generators.set('perlin2d', (x, y) => {
      return this.simpleNoise(x, y, 0)
    })
    
    this.generators.set('simplex2d', (x, y) => {
      return this.simpleNoise(x, y, 0)
    })
    
    this.generators.set('fractal', (x, y, octaves = 4, persistence = 0.5, scale = 1) => {
      let value = 0
      let amplitude = 1
      let frequency = scale
      
      for (let i = 0; i < octaves; i++) {
        value += this.simpleNoise(x * frequency, y * frequency, 0) * amplitude
        amplitude *= persistence
        frequency *= 2
      }
      
      return value
    })
  }

  /**
   * Simple noise implementation for fallback
   */
  simpleNoise(x, y, z) {
    // Simple pseudo-random noise based on coordinates
    const seed = Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453
    return (seed - Math.floor(seed)) * 2 - 1
  }

  /**
   * Generate noise value
   * @param {string} type - Noise type
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @param {number} z - Z coordinate (optional)
   * @param {Object} options - Additional options
   * @returns {number} Noise value
   */
  generate(type, x, y, z = 0, options = {}) {
    if (!this.initialized) {
      console.warn('⚠️ NoiseIntegration not initialized')
      return 0
    }
    
    const generator = this.generators.get(type)
    if (!generator) {
      console.warn(`⚠️ Unknown noise type: ${type}`)
      return 0
    }
    
    try {
      return generator(x, y, z, ...Object.values(options))
    } catch (error) {
      console.error(`❌ Error generating ${type} noise:`, error)
      return 0
    }
  }

  /**
   * Generate terrain heightmap
   * @param {number} width - Width of heightmap
   * @param {number} height - Height of heightmap
   * @param {Object} options - Generation options
   * @returns {Float32Array} Heightmap data
   */
  generateHeightmap(width, height, options = {}) {
    const {
      scale = 0.01,
      octaves = 4,
      persistence = 0.5,
      amplitude = 1,
      offsetX = 0,
      offsetY = 0,
      type = 'fractal'
    } = options
    
    const heightmap = new Float32Array(width * height)
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const noiseX = (x + offsetX) * scale
        const noiseY = (y + offsetY) * scale
        
        let value = this.generate(type, noiseX, noiseY, 0, { octaves, persistence, scale: 1 })
        value = (value + 1) * 0.5 * amplitude // Normalize to 0-1 and apply amplitude
        
        heightmap[y * width + x] = value
      }
    }
    
    return heightmap
  }

  /**
   * Generate texture data
   * @param {number} width - Texture width
   * @param {number} height - Texture height
   * @param {Object} options - Generation options
   * @returns {Uint8Array} Texture data (RGBA)
   */
  generateTexture(width, height, options = {}) {
    const {
      scale = 0.01,
      colorMap = null,
      type = 'perlin'
    } = options
    
    const textureData = new Uint8Array(width * height * 4)
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const noiseValue = this.generate(type, x * scale, y * scale)
        const normalizedValue = (noiseValue + 1) * 0.5 // Normalize to 0-1
        
        const index = (y * width + x) * 4
        
        if (colorMap) {
          const color = colorMap(normalizedValue)
          textureData[index] = color.r
          textureData[index + 1] = color.g
          textureData[index + 2] = color.b
          textureData[index + 3] = color.a || 255
        } else {
          const gray = Math.floor(normalizedValue * 255)
          textureData[index] = gray
          textureData[index + 1] = gray
          textureData[index + 2] = gray
          textureData[index + 3] = 255
        }
      }
    }
    
    return textureData
  }

  /**
   * Set seed for noise generation
   * @param {string} type - Noise type
   * @param {number} seed - Seed value
   */
  setSeed(type, seed) {
    if (this.noise && this.noise.noise && this.noise.noise.seed) {
      this.noise.noise.seed(seed)
      this.seeds.set(type, seed)
      console.log(`🌱 Set seed ${seed} for ${type} noise`)
    }
  }

  /**
   * Get available noise types
   * @returns {Array} Array of noise type names
   */
  getAvailableTypes() {
    return Array.from(this.generators.keys())
  }

  /**
   * Get integration status
   * @returns {Object} Status information
   */
  getStatus() {
    return {
      initialized: this.initialized,
      libraryLoaded: !!this.noise,
      availableTypes: this.getAvailableTypes(),
      seeds: Object.fromEntries(this.seeds)
    }
  }
}
