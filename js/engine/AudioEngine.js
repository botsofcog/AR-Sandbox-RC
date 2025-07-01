/**
 * Audio Engine - Professional audio system for AR Sandbox Pro
 */

class AudioEngine {
    constructor(core, config = {}) {
        this.core = core;
        this.config = {
            masterVolume: 0.7,
            enableSpatialAudio: true,
            maxSources: 32,
            ...config
        };
        
        this.audioContext = null;
        this.masterGain = null;
        this.sounds = new Map();
        this.activeSources = [];
        
        this.version = '2.0.0';
        this.description = 'Professional audio engine with spatial audio support';
    }
    
    async initialize() {
        console.log('🔊 Initializing Audio Engine...');
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = this.config.masterVolume;
            
            console.log('✅ Audio Engine initialized');
        } catch (error) {
            console.warn('⚠️ Audio Engine initialization failed:', error);
        }
    }
    
    async start() {
        console.log('🔊 Audio Engine started');
        
        if (this.audioContext && this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
    }
    
    update(deltaTime) {
        // Audio processing
        this.cleanupFinishedSources();
    }
    
    cleanupFinishedSources() {
        this.activeSources = this.activeSources.filter(source => {
            if (source.playbackState === 'finished') {
                return false;
            }
            return true;
        });
    }
    
    playSound(soundId, options = {}) {
        if (!this.audioContext) return;
        
        // Create oscillator for procedural sound
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.masterGain);
        
        // Configure sound based on type
        this.configureProcedualSound(oscillator, gainNode, soundId, options);
        
        oscillator.start();
        this.activeSources.push(oscillator);
        
        return oscillator;
    }
    
    configureProcedualSound(oscillator, gainNode, soundId, options) {
        const now = this.audioContext.currentTime;
        const volume = (options.volume || 1.0) * this.config.masterVolume;
        
        switch (soundId) {
            case 'terrain_sculpt':
                oscillator.frequency.setValueAtTime(200 + Math.random() * 100, now);
                oscillator.type = 'sawtooth';
                gainNode.gain.setValueAtTime(volume * 0.1, now);
                gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
                oscillator.stop(now + 0.1);
                break;
                
            case 'water_flow':
                oscillator.frequency.setValueAtTime(400 + Math.random() * 200, now);
                oscillator.type = 'sine';
                gainNode.gain.setValueAtTime(volume * 0.05, now);
                gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
                oscillator.stop(now + 0.3);
                break;
                
            case 'vehicle_engine':
                oscillator.frequency.setValueAtTime(80 + Math.random() * 40, now);
                oscillator.type = 'square';
                gainNode.gain.setValueAtTime(volume * 0.08, now);
                gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
                oscillator.stop(now + 0.5);
                break;
                
            default:
                oscillator.frequency.setValueAtTime(440, now);
                oscillator.type = 'sine';
                gainNode.gain.setValueAtTime(volume * 0.1, now);
                gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
                oscillator.stop(now + 0.2);
        }
    }
    
    setMasterVolume(volume) {
        this.config.masterVolume = Math.max(0, Math.min(1, volume));
        if (this.masterGain) {
            this.masterGain.gain.value = this.config.masterVolume;
        }
    }
    
    getMasterVolume() {
        return this.config.masterVolume;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioEngine;
} else {
    window.AudioEngine = AudioEngine;
}
