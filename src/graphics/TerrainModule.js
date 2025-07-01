/**
 * TerrainModule - Enhanced terrain system with procedural generation
 * Integrates with existing frontend/js/terrain.js and adds Noise.js capabilities
 */
import { Module } from '../core/Module.js'
import { EVENTS } from '../core/EventBus.js'
import { NoiseIntegration } from '../integrations/NoiseIntegration.js'

export class TerrainModule extends Module {
  constructor() {
    super('terrain', [])
    
    this.noiseIntegration = new NoiseIntegration()
    this.heightmap = null
    this.width = 512
    this.height = 512
    this.scale = 1
    this.heightScale = 100
    
    // Terrain generation parameters
    this.terrainParams = {
      noiseType: 'fractal',
      scale: 0.01,
      octaves: 4,
      persistence: 0.5,
      amplitude: 1,
      offsetX: 0,
      offsetY: 0,
      seed: Math.random() * 1000
    }
    
    // Terrain modification tracking
    this.modifications = []
    this.lastModificationTime = 0
  }

  /**
   * Initialize terrain module
   */
  async onInit() {
    this.log('info', 'Initializing terrain module...')
    
    try {
      // Initialize noise integration
      await this.noiseIntegration.init()
      
      // Get configuration
      this.width = this.getConfig('terrain.width', 512)
      this.height = this.getConfig('terrain.height', 512)
      this.scale = this.getConfig('terrain.scale', 1)
      this.heightScale = this.getConfig('terrain.heightScale', 100)
      
      // Override terrain params with config
      Object.assign(this.terrainParams, this.getConfig('terrain.generation', {}))
      
      // Generate initial terrain
      this.generateTerrain()
      
      // Setup event listeners
      this.setupEventListeners()
      
      this.log('info', 'Terrain module initialized successfully')
      
    } catch (error) {
      this.log('error', 'Failed to initialize terrain module', error)
      throw error
    }
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Listen for terrain modification requests
    this.on(EVENTS.TERRAIN_RESET, () => {
      this.generateTerrain()
    })
    
    this.on(EVENTS.HEIGHT_CHANGED, (data) => {
      this.modifyHeight(data.x, data.y, data.delta, data.radius)
    })
    
    // Listen for parameter changes
    this.on('terrain:params_changed', (params) => {
      Object.assign(this.terrainParams, params)
      this.generateTerrain()
    })
  }

  /**
   * Generate new terrain using noise
   */
  generateTerrain() {
    const startTime = performance.now()
    
    this.log('info', 'Generating terrain...', this.terrainParams)
    
    try {
      // Generate heightmap using noise integration
      this.heightmap = this.noiseIntegration.generateHeightmap(
        this.width,
        this.height,
        this.terrainParams
      )
      
      // Apply height scaling
      for (let i = 0; i < this.heightmap.length; i++) {
        this.heightmap[i] *= this.heightScale
      }
      
      const generationTime = performance.now() - startTime
      this.log('info', `Terrain generated in ${generationTime.toFixed(2)}ms`)
      
      // Emit terrain updated event
      this.emit(EVENTS.TERRAIN_UPDATED, {
        width: this.width,
        height: this.height,
        heightmap: this.heightmap,
        generationTime
      })
      
    } catch (error) {
      this.log('error', 'Failed to generate terrain', error)
    }
  }

  /**
   * Modify terrain height at specific location
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @param {number} delta - Height change
   * @param {number} radius - Modification radius
   */
  modifyHeight(x, y, delta, radius = 5) {
    if (!this.heightmap) {
      return
    }
    
    const centerX = Math.floor(x)
    const centerY = Math.floor(y)
    
    // Apply modification in circular area
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        const px = centerX + dx
        const py = centerY + dy
        
        // Check bounds
        if (px < 0 || px >= this.width || py < 0 || py >= this.height) {
          continue
        }
        
        // Calculate distance from center
        const distance = Math.sqrt(dx * dx + dy * dy)
        if (distance > radius) {
          continue
        }
        
        // Calculate falloff
        const falloff = 1 - (distance / radius)
        const modification = delta * falloff
        
        // Apply modification
        const index = py * this.width + px
        this.heightmap[index] += modification
        
        // Clamp to reasonable bounds
        this.heightmap[index] = Math.max(0, Math.min(this.heightScale * 2, this.heightmap[index]))
      }
    }
    
    // Track modification
    this.modifications.push({
      x: centerX,
      y: centerY,
      delta,
      radius,
      timestamp: Date.now()
    })
    
    // Limit modification history
    if (this.modifications.length > 1000) {
      this.modifications = this.modifications.slice(-1000)
    }
    
    this.lastModificationTime = Date.now()
    
    // Emit height changed event
    this.emit(EVENTS.TERRAIN_UPDATED, {
      type: 'modification',
      x: centerX,
      y: centerY,
      delta,
      radius
    })
  }

  /**
   * Get height at specific coordinates
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @returns {number} Height value
   */
  getHeight(x, y) {
    if (!this.heightmap) {
      return 0
    }
    
    const px = Math.floor(x)
    const py = Math.floor(y)
    
    if (px < 0 || px >= this.width || py < 0 || py >= this.height) {
      return 0
    }
    
    return this.heightmap[py * this.width + px]
  }

  /**
   * Get interpolated height at fractional coordinates
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @returns {number} Interpolated height value
   */
  getHeightInterpolated(x, y) {
    if (!this.heightmap) {
      return 0
    }
    
    const x1 = Math.floor(x)
    const y1 = Math.floor(y)
    const x2 = x1 + 1
    const y2 = y1 + 1
    
    const fx = x - x1
    const fy = y - y1
    
    const h11 = this.getHeight(x1, y1)
    const h21 = this.getHeight(x2, y1)
    const h12 = this.getHeight(x1, y2)
    const h22 = this.getHeight(x2, y2)
    
    // Bilinear interpolation
    const h1 = h11 * (1 - fx) + h21 * fx
    const h2 = h12 * (1 - fx) + h22 * fx
    
    return h1 * (1 - fy) + h2 * fy
  }

  /**
   * Get terrain normal at coordinates
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @returns {Object} Normal vector {x, y, z}
   */
  getNormal(x, y) {
    const offset = 1
    
    const hL = this.getHeight(x - offset, y)
    const hR = this.getHeight(x + offset, y)
    const hD = this.getHeight(x, y - offset)
    const hU = this.getHeight(x, y + offset)
    
    const nx = (hL - hR) / (2 * offset)
    const ny = (hD - hU) / (2 * offset)
    const nz = 1
    
    // Normalize
    const length = Math.sqrt(nx * nx + ny * ny + nz * nz)
    
    return {
      x: nx / length,
      y: ny / length,
      z: nz / length
    }
  }

  /**
   * Update terrain parameters
   * @param {Object} params - New parameters
   */
  updateParameters(params) {
    Object.assign(this.terrainParams, params)
    this.generateTerrain()
    
    this.log('info', 'Terrain parameters updated', params)
  }

  /**
   * Export heightmap data
   * @returns {Object} Heightmap export data
   */
  exportHeightmap() {
    return {
      width: this.width,
      height: this.height,
      heightmap: Array.from(this.heightmap),
      parameters: { ...this.terrainParams },
      modifications: [...this.modifications]
    }
  }

  /**
   * Import heightmap data
   * @param {Object} data - Heightmap import data
   */
  importHeightmap(data) {
    this.width = data.width
    this.height = data.height
    this.heightmap = new Float32Array(data.heightmap)
    this.terrainParams = { ...data.parameters }
    this.modifications = [...(data.modifications || [])]
    
    this.emit(EVENTS.TERRAIN_UPDATED, {
      type: 'import',
      width: this.width,
      height: this.height
    })
    
    this.log('info', 'Heightmap imported successfully')
  }

  /**
   * Get terrain statistics
   * @returns {Object} Terrain statistics
   */
  getStatistics() {
    if (!this.heightmap) {
      return null
    }
    
    let min = Infinity
    let max = -Infinity
    let sum = 0
    
    for (let i = 0; i < this.heightmap.length; i++) {
      const height = this.heightmap[i]
      min = Math.min(min, height)
      max = Math.max(max, height)
      sum += height
    }
    
    const average = sum / this.heightmap.length
    
    return {
      min,
      max,
      average,
      range: max - min,
      totalPoints: this.heightmap.length,
      modifications: this.modifications.length,
      lastModified: this.lastModificationTime
    }
  }

  /**
   * Module update (called each frame)
   */
  onUpdate(deltaTime) {
    // Terrain module doesn't need frequent updates
    // Could add erosion simulation or other dynamic effects here
  }

  /**
   * Get module status
   */
  getStatus() {
    const baseStatus = super.getStatus()
    
    return {
      ...baseStatus,
      terrain: {
        dimensions: { width: this.width, height: this.height },
        parameters: { ...this.terrainParams },
        statistics: this.getStatistics(),
        noiseIntegration: this.noiseIntegration.getStatus()
      }
    }
  }
}
