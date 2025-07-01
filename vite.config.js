import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: '.',
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // Main AR Sandbox implementations
        main: resolve(__dirname, 'index.html'),
        'rc-sandbox-clean': resolve(__dirname, 'rc_sandbox_clean/index.html'),
        'frontend': resolve(__dirname, 'frontend/index.html'),
        'working-sandbox-game': resolve(__dirname, 'working_sandbox_game.html'),
        'ar-sandbox-pro': resolve(__dirname, 'ar_sandbox_pro.html'),
        'realistic-sandbox-game': resolve(__dirname, 'realistic_sandbox_game.html'),
        'ultimate-ar-sandbox': resolve(__dirname, 'ultimate-ar-sandbox.html'),
        
        // Specialized implementations
        'smart-webcam-demo': resolve(__dirname, 'smart_webcam_demo.html'),
        'kinect-ar-sandbox': resolve(__dirname, 'kinect_ar_sandbox.html'),
        'physics-ar-sandbox': resolve(__dirname, 'physics-ar-sandbox.html'),
        'topology-ar-sandbox': resolve(__dirname, 'topology-ar-sandbox.html')
      },
      external: [
        // External libraries will be loaded dynamically
        /^\/external_libs\/.*/
      ]
    },
    target: 'es2020',
    minify: 'terser',
    sourcemap: true
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    open: true,
    cors: true,
    proxy: {
      // Python backend services
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/depth': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '/telemetry': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/streaming': {
        target: 'http://localhost:8003',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@core': resolve(__dirname, 'src/core'),
      '@physics': resolve(__dirname, 'src/physics'),
      '@graphics': resolve(__dirname, 'src/graphics'),
      '@ai': resolve(__dirname, 'src/ai'),
      '@vehicles': resolve(__dirname, 'src/vehicles'),
      '@audio': resolve(__dirname, 'src/audio'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@external': resolve(__dirname, 'external_libs'),
      '@assets': resolve(__dirname, 'assets'),
      '@frontend': resolve(__dirname, 'frontend'),
      '@backend': resolve(__dirname, 'backend')
    }
  },
  optimizeDeps: {
    include: [
      'three',
      'cannon-es',
      'matter-js',
      'tone',
      'lil-gui'
    ],
    exclude: [
      // External libraries loaded dynamically
      '@external/sandboxels',
      '@external/three.js',
      '@external/divine-voxel-engine'
    ]
  },
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
    __VERSION__: JSON.stringify(process.env.npm_package_version)
  },
  css: {
    devSourcemap: true
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js']
  }
})
