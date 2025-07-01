/**
 * ExternalLibraryLoader - Safe loading and integration of external libraries
 * Handles dynamic loading with fallbacks and error handling
 */
export class ExternalLibraryLoader {
  constructor() {
    this.loadedLibraries = new Map()
    this.loadingPromises = new Map()
    this.basePath = './external_libs'
  }

  /**
   * Load an external library safely
   * @param {string} libraryName - Name of the library
   * @param {string} scriptPath - Path to the main script
   * @param {Object} options - Loading options
   * @returns {Promise} Loading promise
   */
  async loadLibrary(libraryName, scriptPath, options = {}) {
    const {
      globalName = null,
      fallback = null,
      timeout = 10000,
      dependencies = []
    } = options

    // Check if already loaded
    if (this.loadedLibraries.has(libraryName)) {
      return this.loadedLibraries.get(libraryName)
    }

    // Check if currently loading
    if (this.loadingPromises.has(libraryName)) {
      return this.loadingPromises.get(libraryName)
    }

    console.log(`📦 Loading external library: ${libraryName}`)

    const loadingPromise = this.performLoad(libraryName, scriptPath, {
      globalName,
      fallback,
      timeout,
      dependencies
    })

    this.loadingPromises.set(libraryName, loadingPromise)

    try {
      const result = await loadingPromise
      this.loadedLibraries.set(libraryName, result)
      this.loadingPromises.delete(libraryName)
      
      console.log(`✅ Successfully loaded: ${libraryName}`)
      return result
      
    } catch (error) {
      this.loadingPromises.delete(libraryName)
      console.error(`❌ Failed to load ${libraryName}:`, error)
      
      if (fallback) {
        console.log(`🔄 Attempting fallback for ${libraryName}`)
        return this.loadFallback(libraryName, fallback)
      }
      
      throw error
    }
  }

  /**
   * Perform the actual library loading
   */
  async performLoad(libraryName, scriptPath, options) {
    const { globalName, timeout, dependencies } = options

    // Load dependencies first
    for (const dep of dependencies) {
      if (!this.isLibraryLoaded(dep)) {
        throw new Error(`Dependency ${dep} not loaded for ${libraryName}`)
      }
    }

    // Create full path
    const fullPath = `${this.basePath}/${scriptPath}`

    // Check if it's a module or script
    if (scriptPath.endsWith('.js') && !scriptPath.includes('node_modules')) {
      // Try to load as ES module first
      try {
        const module = await import(fullPath)
        return module
      } catch (moduleError) {
        console.warn(`⚠️ Failed to load as module, trying as script: ${libraryName}`)
        // Fall back to script loading
      }
    }

    // Load as script
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = fullPath
      script.async = true

      const timeoutId = setTimeout(() => {
        reject(new Error(`Timeout loading ${libraryName}`))
      }, timeout)

      script.onload = () => {
        clearTimeout(timeoutId)
        
        if (globalName) {
          const global = window[globalName]
          if (global) {
            resolve(global)
          } else {
            reject(new Error(`Global ${globalName} not found after loading ${libraryName}`))
          }
        } else {
          resolve(true)
        }
      }

      script.onerror = () => {
        clearTimeout(timeoutId)
        reject(new Error(`Failed to load script: ${fullPath}`))
      }

      document.head.appendChild(script)
    })
  }

  /**
   * Load fallback implementation
   */
  async loadFallback(libraryName, fallback) {
    if (typeof fallback === 'function') {
      const result = fallback()
      this.loadedLibraries.set(libraryName, result)
      return result
    } else if (typeof fallback === 'string') {
      return this.loadLibrary(`${libraryName}-fallback`, fallback)
    } else {
      this.loadedLibraries.set(libraryName, fallback)
      return fallback
    }
  }

  /**
   * Check if library is loaded
   * @param {string} libraryName - Library name
   * @returns {boolean} True if loaded
   */
  isLibraryLoaded(libraryName) {
    return this.loadedLibraries.has(libraryName)
  }

  /**
   * Get loaded library
   * @param {string} libraryName - Library name
   * @returns {*} Library object or null
   */
  getLibrary(libraryName) {
    return this.loadedLibraries.get(libraryName) || null
  }

  /**
   * Preload multiple libraries
   * @param {Array} libraries - Array of library configurations
   * @returns {Promise} Promise that resolves when all are loaded
   */
  async preloadLibraries(libraries) {
    const promises = libraries.map(lib => 
      this.loadLibrary(lib.name, lib.path, lib.options || {})
    )
    
    return Promise.allSettled(promises)
  }

  /**
   * Get loading status
   * @returns {Object} Status information
   */
  getStatus() {
    return {
      loaded: Array.from(this.loadedLibraries.keys()),
      loading: Array.from(this.loadingPromises.keys()),
      totalLoaded: this.loadedLibraries.size
    }
  }
}

// Singleton instance
export const libraryLoader = new ExternalLibraryLoader()

// Common library configurations
export const LIBRARY_CONFIGS = {
  noise: {
    name: 'noise',
    path: 'noisejs/perlin.js',
    options: {
      globalName: 'noise',
      timeout: 5000
    }
  },
  
  lilGui: {
    name: 'lil-gui',
    path: 'lil-gui/dist/lil-gui.esm.js',
    options: {
      timeout: 5000
    }
  },
  
  tone: {
    name: 'tone',
    path: 'tone.js/build/Tone.js',
    options: {
      globalName: 'Tone',
      timeout: 10000
    }
  },
  
  matter: {
    name: 'matter',
    path: 'matter-js/build/matter.js',
    options: {
      globalName: 'Matter',
      timeout: 10000
    }
  },
  
  three: {
    name: 'three',
    path: 'three.js/build/three.module.js',
    options: {
      timeout: 15000
    }
  },
  
  sandboxels: {
    name: 'sandboxels',
    path: 'sandboxels/scripts/elements.js',
    options: {
      globalName: 'elements',
      timeout: 10000
    }
  },
  
  cannon: {
    name: 'cannon',
    path: 'cannon.js/build/cannon.js',
    options: {
      globalName: 'CANNON',
      timeout: 10000
    }
  },
  
  ml5: {
    name: 'ml5',
    path: 'ml5-library/dist/ml5.js',
    options: {
      globalName: 'ml5',
      timeout: 15000,
      dependencies: ['tensorflow']
    }
  },
  
  tensorflow: {
    name: 'tensorflow',
    path: 'tfjs-examples/node_modules/@tensorflow/tfjs/dist/tf.js',
    options: {
      globalName: 'tf',
      timeout: 20000
    }
  }
}
