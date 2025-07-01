module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true
  },
  extends: [
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module'
  },
  rules: {
    // Error prevention
    'no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-alert': 'error',
    
    // Code quality
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': ['error', 'always'],
    'curly': ['error', 'all'],
    
    // Style consistency
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'never'],
    'comma-dangle': ['error', 'never'],
    'object-curly-spacing': ['error', 'always'],
    'array-bracket-spacing': ['error', 'never'],
    
    // Performance
    'no-loop-func': 'error',
    'no-inner-declarations': 'error',
    
    // Best practices for AR Sandbox
    'no-global-assign': 'error',
    'no-implicit-globals': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error'
  },
  globals: {
    // Three.js globals
    'THREE': 'readonly',
    
    // Physics engine globals
    'CANNON': 'readonly',
    'Matter': 'readonly',
    
    // AI/ML globals
    'tf': 'readonly',
    'ml5': 'readonly',
    
    // Audio globals
    'Tone': 'readonly',
    
    // AR Sandbox specific globals
    'SandboxCore': 'readonly',
    'TerrainEngine': 'readonly',
    'VehicleFleet': 'readonly',
    'PhysicsEngine': 'readonly',
    
    // Development globals
    '__DEV__': 'readonly',
    '__VERSION__': 'readonly'
  },
  overrides: [
    {
      files: ['tests/**/*.js'],
      env: {
        jest: true
      },
      globals: {
        'vi': 'readonly',
        'describe': 'readonly',
        'it': 'readonly',
        'expect': 'readonly',
        'beforeEach': 'readonly',
        'afterEach': 'readonly'
      }
    },
    {
      files: ['scripts/**/*.js'],
      env: {
        node: true
      },
      rules: {
        'no-console': 'off'
      }
    },
    {
      files: ['external_libs/**/*.js'],
      rules: {
        // Relax rules for external libraries
        'no-unused-vars': 'off',
        'no-console': 'off',
        'prefer-const': 'off'
      }
    }
  ]
}
