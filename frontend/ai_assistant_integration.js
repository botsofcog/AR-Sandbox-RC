/**
 * AI Construction Assistant Frontend Integration
 * Connects browser to AI backend for intelligent construction assistance
 */

class AIConstructionAssistant {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.aiSuggestions = [];
        this.currentAnalysis = null;
        
        this.init();
    }
    
    init() {
        this.connectToAI();
        this.setupUI();
        this.setupEventListeners();
    }
    
    connectToAI() {
        try {
            this.websocket = new WebSocket('ws://localhost:8767');
            
            this.websocket.onopen = () => {
                console.log('🤖 Connected to AI Construction Assistant');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.requestAIStatus();
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleAIResponse(data);
                } catch (error) {
                    console.error('❌ AI response parsing error:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🤖 AI Assistant disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ AI Assistant connection error:', error);
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('❌ Failed to connect to AI Assistant:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect to AI Assistant (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => this.connectToAI(), 3000 * this.reconnectAttempts);
        } else {
            console.log('❌ Max reconnection attempts reached for AI Assistant');
            this.showNotification('AI Assistant unavailable - using fallback mode', 'warning');
        }
    }
    
    setupUI() {
        // Create AI Assistant panel
        const aiPanel = document.createElement('div');
        aiPanel.id = 'ai-assistant-panel';
        aiPanel.className = 'glass-panel';
        aiPanel.style.cssText = `
            position: fixed;
            top: 20px;
            left: 370px;
            width: 350px;
            z-index: 1000;
            display: none;
        `;
        
        aiPanel.innerHTML = `
            <div class="panel-header">
                <div class="header-icon">🤖</div>
                <div class="header-content">
                    <h4 class="panel-title">AI Construction Assistant</h4>
                    <div class="panel-subtitle" id="ai-status">Connecting...</div>
                </div>
                <button class="close-button" onclick="toggleAIPanel()">&times;</button>
            </div>
            
            <div class="ai-chat-container">
                <div id="ai-chat-messages" class="ai-chat-messages"></div>
                <div class="ai-input-container">
                    <input type="text" id="ai-command-input" placeholder="Ask AI for construction advice..." class="ai-input">
                    <button onclick="sendAICommand()" class="ai-send-button">Send</button>
                </div>
            </div>
            
            <div class="ai-quick-actions">
                <button onclick="analyzeCurrentTerrain()" class="ai-action-button">📊 Analyze Terrain</button>
                <button onclick="getSuggestions('highway')" class="ai-action-button">🛣️ Highway Tips</button>
                <button onclick="getSuggestions('flood_defense')" class="ai-action-button">🌊 Flood Defense</button>
                <button onclick="validateStructure()" class="ai-action-button">🔧 Validate Structure</button>
            </div>
            
            <div id="ai-suggestions" class="ai-suggestions"></div>
        `;
        
        document.body.appendChild(aiPanel);
        
        // Add AI toggle button
        const aiToggle = document.createElement('button');
        aiToggle.className = 'glass-button';
        aiToggle.onclick = () => this.toggleAIPanel();
        aiToggle.innerHTML = '🤖 AI';
        aiToggle.title = 'Toggle AI Construction Assistant';
        
        // Add to existing button group
        const buttonGroup = document.querySelector('.buttons.has-addons.is-vertical');
        if (buttonGroup) {
            buttonGroup.appendChild(aiToggle);
        }
    }
    
    setupEventListeners() {
        // Enter key in AI input
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && document.activeElement.id === 'ai-command-input') {
                this.sendAICommand();
            }
        });
        
        // Voice command support (if available)
        if ('webkitSpeechRecognition' in window) {
            this.setupVoiceCommands();
        }
    }
    
    setupVoiceCommands() {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            const command = event.results[0][0].transcript;
            console.log('🎤 Voice command:', command);
            this.processNaturalLanguage(command);
        };
        
        // Add voice button
        const voiceButton = document.createElement('button');
        voiceButton.className = 'ai-voice-button';
        voiceButton.innerHTML = '🎤';
        voiceButton.onclick = () => recognition.start();
        voiceButton.title = 'Voice Command';
        
        const inputContainer = document.querySelector('.ai-input-container');
        if (inputContainer) {
            inputContainer.appendChild(voiceButton);
        }
    }
    
    sendAICommand() {
        const input = document.getElementById('ai-command-input');
        const command = input.value.trim();
        
        if (command && this.isConnected) {
            this.addChatMessage('user', command);
            this.processNaturalLanguage(command);
            input.value = '';
        } else if (!this.isConnected) {
            this.showNotification('AI Assistant not connected', 'warning');
        }
    }
    
    processNaturalLanguage(text) {
        if (!this.isConnected) {
            this.addChatMessage('ai', 'AI Assistant is not connected. Please check the connection.');
            return;
        }
        
        const request = {
            command: 'natural_language_command',
            text: text
        };
        
        this.websocket.send(JSON.stringify(request));
    }
    
    analyzeCurrentTerrain() {
        if (!this.isConnected) {
            this.showNotification('AI Assistant not connected', 'warning');
            return;
        }
        
        // Capture current terrain state
        const canvas = document.getElementById('canvas');
        if (canvas) {
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            const request = {
                command: 'analyze_terrain',
                image_data: imageData,
                terrain_data: this.getTerrainData()
            };
            
            this.websocket.send(JSON.stringify(request));
            this.addChatMessage('ai', '🔍 Analyzing terrain... Please wait.');
        }
    }
    
    getSuggestions(projectType) {
        if (!this.isConnected) {
            this.showNotification('AI Assistant not connected', 'warning');
            return;
        }
        
        const request = {
            command: 'suggest_construction',
            project_type: projectType,
            constraints: this.getProjectConstraints()
        };
        
        this.websocket.send(JSON.stringify(request));
        this.addChatMessage('ai', `🏗️ Getting ${projectType} construction suggestions...`);
    }
    
    validateStructure() {
        if (!this.isConnected) {
            this.showNotification('AI Assistant not connected', 'warning');
            return;
        }
        
        const request = {
            command: 'validate_structure',
            structure_data: this.getCurrentStructureData()
        };
        
        this.websocket.send(JSON.stringify(request));
        this.addChatMessage('ai', '🔧 Validating current structure...');
    }
    
    requestAIStatus() {
        if (this.isConnected) {
            this.websocket.send(JSON.stringify({ command: 'get_ai_status' }));
        }
    }
    
    handleAIResponse(data) {
        switch (data.type) {
            case 'terrain_analysis':
                this.handleTerrainAnalysis(data);
                break;
            case 'construction_suggestions':
                this.handleConstructionSuggestions(data);
                break;
            case 'structure_validation':
                this.handleStructureValidation(data);
                break;
            case 'natural_language_response':
                this.handleNaturalLanguageResponse(data);
                break;
            case 'ai_status':
                this.handleAIStatus(data);
                break;
            case 'error':
                this.addChatMessage('ai', `❌ Error: ${data.message}`);
                break;
            default:
                console.log('🤖 Unknown AI response type:', data.type);
        }
    }
    
    handleTerrainAnalysis(data) {
        this.currentAnalysis = data;
        this.addChatMessage('ai', `📊 Terrain Analysis Complete:\n${data.analysis}`);
        
        if (data.suggestions && data.suggestions.length > 0) {
            this.displaySuggestions(data.suggestions, 'Terrain Analysis Suggestions');
        }
    }
    
    handleConstructionSuggestions(data) {
        this.addChatMessage('ai', `🏗️ ${data.project_type.toUpperCase()} Construction Suggestions:`);
        this.displaySuggestions(data.suggestions, `${data.project_type} Project`);
        
        if (data.estimated_timeline) {
            this.addChatMessage('ai', `⏱️ Estimated Timeline: ${data.estimated_timeline}`);
        }
    }
    
    handleStructureValidation(data) {
        const validation = data.validation;
        const status = validation.structural_integrity === 'PASS' ? '✅' : '❌';
        
        this.addChatMessage('ai', `${status} Structure Validation: ${validation.structural_integrity}`);
        this.addChatMessage('ai', `🔧 Safety Compliance: ${validation.safety_compliance}`);
        
        if (validation.recommendations) {
            this.displaySuggestions(validation.recommendations, 'Engineering Recommendations');
        }
    }
    
    handleNaturalLanguageResponse(data) {
        this.addChatMessage('ai', data.response);
        
        if (data.understood && data.action) {
            // Execute the understood command
            this.executeAICommand(data.action, data.tool);
        }
    }
    
    handleAIStatus(data) {
        const statusElement = document.getElementById('ai-status');
        if (statusElement) {
            statusElement.textContent = `${data.status} • ${data.capabilities.length} capabilities`;
        }
    }
    
    executeAICommand(action, tool) {
        // Execute AI-suggested actions in the sandbox
        switch (action) {
            case 'add_water':
                if (typeof addWater === 'function') addWater();
                break;
            case 'reset':
                if (typeof resetSandbox === 'function') resetSandbox();
                break;
            case 'raise_terrain':
                this.addChatMessage('ai', '🏔️ Use the excavate tool to raise terrain');
                break;
            case 'level_terrain':
                this.addChatMessage('ai', '📏 Use the grade tool to level terrain');
                break;
            case 'change_mission':
                this.addChatMessage('ai', '🎯 Use the mission selector to change missions');
                break;
            default:
                this.addChatMessage('ai', `🔧 Please use the ${tool} tool for this action`);
        }
    }
    
    addChatMessage(sender, message) {
        const chatMessages = document.getElementById('ai-chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ai-message-${sender}`;
        messageDiv.innerHTML = `
            <div class="ai-message-content">${message.replace(/\n/g, '<br>')}</div>
            <div class="ai-message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    displaySuggestions(suggestions, title) {
        const suggestionsContainer = document.getElementById('ai-suggestions');
        if (!suggestionsContainer) return;
        
        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'ai-suggestion-group';
        suggestionDiv.innerHTML = `
            <h5 class="ai-suggestion-title">${title}</h5>
            <ul class="ai-suggestion-list">
                ${suggestions.map(s => `<li class="ai-suggestion-item">${s}</li>`).join('')}
            </ul>
        `;
        
        suggestionsContainer.appendChild(suggestionDiv);
    }
    
    toggleAIPanel() {
        const panel = document.getElementById('ai-assistant-panel');
        if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('ai-status');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.style.color = connected ? '#00ff88' : '#ff6b6b';
        }
    }
    
    getTerrainData() {
        // Get current terrain state for AI analysis
        if (window.terrain) {
            return {
                heightMap: window.terrain.heightMap,
                dimensions: {
                    cols: window.terrain.cols,
                    rows: window.terrain.rows
                },
                settings: window.terrain.settings
            };
        }
        return null;
    }
    
    getProjectConstraints() {
        return {
            budget: 'medium',
            timeline: 'standard',
            environmental_impact: 'low',
            terrain_difficulty: 'moderate'
        };
    }
    
    getCurrentStructureData() {
        return {
            type: 'terrain_modification',
            complexity: 'medium',
            materials: ['earth', 'water'],
            load_requirements: 'light'
        };
    }
    
    showNotification(message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Global functions for button integration
function toggleAIPanel() {
    if (window.aiAssistant) {
        window.aiAssistant.toggleAIPanel();
    }
}

function sendAICommand() {
    if (window.aiAssistant) {
        window.aiAssistant.sendAICommand();
    }
}

function analyzeCurrentTerrain() {
    if (window.aiAssistant) {
        window.aiAssistant.analyzeCurrentTerrain();
    }
}

function getSuggestions(projectType) {
    if (window.aiAssistant) {
        window.aiAssistant.getSuggestions(projectType);
    }
}

function validateStructure() {
    if (window.aiAssistant) {
        window.aiAssistant.validateStructure();
    }
}

// Initialize AI Assistant when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aiAssistant = new AIConstructionAssistant();
    console.log('🤖 AI Construction Assistant initialized');
});

// CSS Styles for AI Assistant
const aiStyles = `
    .ai-chat-messages {
        height: 200px;
        overflow-y: auto;
        padding: 10px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .ai-message {
        margin-bottom: 10px;
        padding: 8px;
        border-radius: 6px;
    }
    
    .ai-message-user {
        background: rgba(0, 212, 255, 0.2);
        text-align: right;
    }
    
    .ai-message-ai {
        background: rgba(0, 255, 136, 0.2);
    }
    
    .ai-message-content {
        font-size: 14px;
        line-height: 1.4;
    }
    
    .ai-message-time {
        font-size: 10px;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    .ai-input-container {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
    }
    
    .ai-input {
        flex: 1;
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        background: rgba(0, 0, 0, 0.3);
        color: white;
    }
    
    .ai-send-button, .ai-voice-button {
        padding: 8px 12px;
        background: rgba(0, 212, 255, 0.8);
        border: none;
        border-radius: 4px;
        color: white;
        cursor: pointer;
    }
    
    .ai-quick-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 10px;
    }
    
    .ai-action-button {
        padding: 8px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        color: white;
        cursor: pointer;
        font-size: 12px;
    }
    
    .ai-action-button:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .ai-suggestions {
        max-height: 150px;
        overflow-y: auto;
    }
    
    .ai-suggestion-group {
        margin-bottom: 10px;
        padding: 8px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
    }
    
    .ai-suggestion-title {
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
        color: #00ff88;
    }
    
    .ai-suggestion-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .ai-suggestion-item {
        font-size: 11px;
        padding: 2px 0;
        border-left: 2px solid #00ff88;
        padding-left: 8px;
        margin-bottom: 2px;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = aiStyles;
document.head.appendChild(styleSheet);
