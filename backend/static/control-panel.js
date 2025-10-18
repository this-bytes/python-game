/**
 * Ultimate Game Control Panel - Main Controller
 * 
 * This module provides a comprehensive game management interface with:
 * - Real-time game state synchronization
 * - Advanced entity editors for all game types
 * - Visual level/incident editor
 * - Batch operations and templates
 * - Entity relationship visualization
 * - Timeline debugging and playback
 */

const API_BASE = '/api';

class ControlPanel {
    constructor() {
        this.socket = null;
        this.currentView = 'dashboard';
        this.gameState = null;
        this.entities = {
            incidents: [],
            specialists: [],
            equipment: [],
            facilities: [],
            clients: [],
            automation: [],
            achievements: []
        };
        this.eventHistory = [];
        this.undoStack = [];
        this.redoStack = [];
        
        this.init();
    }
    
    async init() {
        console.log('🎮 Initializing Control Panel...');
        
        // Setup navigation
        this.setupNavigation();
        
        // Initialize WebSocket
        this.initWebSocket();
        
        // Load initial data
        await this.loadAllData();
        
        // Show default view
        this.showView('dashboard');
        
        console.log('✅ Control Panel Ready');
    }
    
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                this.showView(view);
                
                // Update active state
                navButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }
    
    initWebSocket() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.updateConnectionStatus(true);
                this.showToast('Connected', 'WebSocket connection established', 'success');
            });
            
            this.socket.on('disconnect', () => {
                this.updateConnectionStatus(false);
                this.showToast('Disconnected', 'WebSocket connection lost', 'warning');
            });
            
            // Listen for game events
            this.socket.on('game_event', (data) => {
                this.handleGameEvent(data);
            });
            
            this.socket.on('state_update', (data) => {
                this.gameState = data;
                this.refreshCurrentView();
            });
            
        } catch (error) {
            console.warn('WebSocket not available, using polling fallback');
            this.updateConnectionStatus(false);
            // Fallback to polling
            setInterval(() => this.pollGameState(), 5000);
        }
    }
    
    updateConnectionStatus(connected) {
        const dot = document.getElementById('connection-dot');
        const status = document.getElementById('connection-status');
        
        if (connected) {
            dot.className = 'dot connected';
            status.textContent = 'Connected';
        } else {
            dot.className = 'dot disconnected';
            status.textContent = 'Disconnected';
        }
    }
    
    async loadAllData() {
        try {
            // Load game state
            const stateRes = await fetch(`${API_BASE}/state`);
            const stateData = await stateRes.json();
            if (stateData.success) {
                this.gameState = stateData.data;
            }
            
            // Load all config files
            const configRes = await fetch(`${API_BASE}/config/files`);
            const configData = await configRes.json();
            if (configData.success) {
                // Load each config file
                for (const file of configData.data) {
                    await this.loadConfigFile(file.name);
                }
            }
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showToast('Error', 'Failed to load game data', 'error');
        }
    }
    
    async loadConfigFile(filename) {
        try {
            const res = await fetch(`${API_BASE}/config/files/${filename}`);
            const data = await res.json();
            if (data.success) {
                const key = filename.replace('.json', '');
                this.entities[key] = data.data.content;
            }
        } catch (error) {
            console.error(`Failed to load ${filename}:`, error);
        }
    }
    
    async pollGameState() {
        try {
            const res = await fetch(`${API_BASE}/state/summary`);
            const data = await res.json();
            if (data.success) {
                this.gameState = data.data;
                this.refreshCurrentView();
            }
        } catch (error) {
            console.error('Failed to poll game state:', error);
        }
    }
    
    handleGameEvent(event) {
        // Add to event history
        this.eventHistory.unshift({
            ...event,
            timestamp: Date.now()
        });
        
        // Keep only last 1000 events
        if (this.eventHistory.length > 1000) {
            this.eventHistory.pop();
        }
        
        // Update current view if showing timeline
        if (this.currentView === 'timeline') {
            this.refreshCurrentView();
        }
    }
    
    showView(viewName) {
        this.currentView = viewName;
        const container = document.getElementById('view-container');
        
        switch(viewName) {
            case 'dashboard':
                container.innerHTML = this.renderDashboard();
                break;
            case 'live-state':
                container.innerHTML = this.renderLiveState();
                break;
            case 'incidents':
                container.innerHTML = this.renderEntityEditor('incidents', 'Incident Types');
                break;
            case 'specialists':
                container.innerHTML = this.renderEntityEditor('specialist_templates', 'Specialist Templates');
                break;
            case 'equipment':
                container.innerHTML = this.renderEntityEditor('equipment', 'Equipment Items');
                break;
            case 'facilities':
                container.innerHTML = this.renderEntityEditor('facilities', 'Facilities');
                break;
            case 'clients':
                container.innerHTML = this.renderEntityEditor('clients', 'Clients');
                break;
            case 'automation':
                container.innerHTML = this.renderEntityEditor('automation_scripts', 'Automation Scripts');
                break;
            case 'achievements':
                container.innerHTML = this.renderEntityEditor('achievements', 'Achievements');
                break;
            case 'level-editor':
                container.innerHTML = this.renderLevelEditor();
                break;
            case 'batch-ops':
                container.innerHTML = this.renderBatchOperations();
                break;
            case 'timeline':
                container.innerHTML = this.renderTimeline();
                break;
            case 'visualizer':
                container.innerHTML = this.renderEntityGraph();
                break;
            case 'godmode':
                container.innerHTML = this.renderGodMode();
                break;
            default:
                container.innerHTML = '<h2>View not found</h2>';
        }
        
        // Attach event listeners for the new view
        this.attachViewEventListeners(viewName);
    }
    
    refreshCurrentView() {
        this.showView(this.currentView);
    }
    
    renderDashboard() {
        const state = this.gameState || {};
        
        return `
            <div class="view-header">
                <h2>📈 Dashboard</h2>
                <p>Game overview and real-time metrics</p>
            </div>
            
            <div class="grid grid-4">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">💰 Money</div>
                    </div>
                    <div class="card-content">
                        <div style="font-size: 28px; font-weight: bold; color: var(--accent-primary);">
                            $${(state.current_money || 0).toFixed(2)}
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">🚨 Active Incidents</div>
                    </div>
                    <div class="card-content">
                        <div style="font-size: 28px; font-weight: bold; color: var(--accent-secondary);">
                            ${state.active_incidents || 0}
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">👥 Specialists</div>
                    </div>
                    <div class="card-content">
                        <div style="font-size: 28px; font-weight: bold; color: var(--accent-primary);">
                            ${state.total_specialists || 0}
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">📊 SLA Compliance</div>
                    </div>
                    <div class="card-content">
                        <div style="font-size: 28px; font-weight: bold; color: var(--accent-primary);">
                            ${(state.sla_compliance_rate || 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>🎯 Quick Actions</h3>
                </div>
                <div class="grid grid-3">
                    <button class="btn btn-primary" onclick="controlPanel.spawnIncident()">
                        🚨 Spawn Incident
                    </button>
                    <button class="btn btn-success" onclick="controlPanel.addMoney(1000)">
                        💰 Add $1000
                    </button>
                    <button class="btn btn-warning" onclick="controlPanel.reloadConfig()">
                        🔄 Reload Config
                    </button>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>📡 Recent Events</h3>
                </div>
                <div id="recent-events">
                    ${this.renderRecentEvents()}
                </div>
            </div>
        `;
    }
    
    renderRecentEvents() {
        if (this.eventHistory.length === 0) {
            return '<p style="color: var(--text-secondary);">No events yet...</p>';
        }
        
        return this.eventHistory.slice(0, 10).map(event => {
            const time = new Date(event.timestamp).toLocaleTimeString();
            return `
                <div style="padding: 8px; border-bottom: 1px solid var(--border-color);">
                    <span style="color: var(--text-secondary); font-size: 12px;">[${time}]</span>
                    <span>${event.message || JSON.stringify(event)}</span>
                </div>
            `;
        }).join('');
    }
    
    renderLiveState() {
        return `
            <div class="view-header">
                <h2>🎯 Live Game State</h2>
                <p>Real-time game state viewer and editor</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>Current State</h3>
                    <div class="panel-actions">
                        <button class="btn btn-secondary btn-sm" onclick="controlPanel.refreshState()">
                            🔄 Refresh
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="controlPanel.saveState()">
                            💾 Save State
                        </button>
                    </div>
                </div>
                <pre style="background: var(--bg-tertiary); padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 12px;">
${JSON.stringify(this.gameState, null, 2)}
                </pre>
            </div>
        `;
    }
    
    renderEntityEditor(entityType, title) {
        const data = this.entities[entityType] || {};
        let entities = [];
        
        // Extract entities array from different structures
        if (Array.isArray(data)) {
            entities = data;
        } else if (data.incident_types) {
            entities = data.incident_types;
        } else if (data.specialist_archetypes) {
            entities = data.specialist_archetypes;
        } else if (data.equipment) {
            entities = data.equipment;
        } else if (data.facilities) {
            entities = data.facilities;
        } else if (data.clients) {
            entities = data.clients;
        } else if (data.automation_scripts) {
            entities = data.automation_scripts;
        } else if (data.achievements) {
            entities = data.achievements;
        }
        
        return `
            <div class="view-header">
                <h2>✏️ ${title}</h2>
                <p>Create, edit, and manage ${title.toLowerCase()}</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>All ${title}</h3>
                    <div class="panel-actions">
                        <button class="btn btn-primary btn-sm" onclick="controlPanel.createEntity('${entityType}')">
                            ➕ Create New
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="batchOperations.showBatchEditor('${entityType}')">
                            ⚡ Batch Edit
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="controlPanel.importEntities('${entityType}')">
                            📥 Import
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="controlPanel.exportEntities('${entityType}')">
                            📤 Export
                        </button>
                    </div>
                </div>
                
                <div class="entity-list">
                    ${this.renderEntityCards(entities, entityType)}
                </div>
            </div>
        `;
    }
    
    renderEntityCards(entities, entityType) {
        if (!entities || entities.length === 0) {
            return '<p style="color: var(--text-secondary); padding: 20px;">No entities found. Create one to get started.</p>';
        }
        
        return entities.map((entity, index) => {
            const name = entity.name || entity.id || `Entity ${index}`;
            const description = entity.description || '';
            const rarity = entity.rarity || 'common';
            
            return `
                <div class="entity-card">
                    <div class="card-header">
                        <div class="card-title">${name}</div>
                        ${entity.rarity ? `<div class="card-badge badge-${rarity}">${rarity}</div>` : ''}
                    </div>
                    <div class="card-content">
                        ${description}
                    </div>
                    <div class="entity-actions">
                        <button class="btn btn-secondary btn-sm" onclick="controlPanel.editEntity('${entityType}', ${index})">
                            ✏️ Edit
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="controlPanel.duplicateEntity('${entityType}', ${index})">
                            📋 Duplicate
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="controlPanel.deleteEntity('${entityType}', ${index})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderLevelEditor() {
        return `
            <div class="view-header">
                <h2>🎨 Level Editor</h2>
                <p>Create and edit incident waves and game scenarios</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>Wave Designer</h3>
                    <button class="btn btn-primary btn-sm" onclick="controlPanel.createWave()">
                        ➕ New Wave
                    </button>
                </div>
                <div id="wave-editor">
                    <p style="color: var(--text-secondary);">Wave editor coming soon...</p>
                </div>
            </div>
        `;
    }
    
    renderBatchOperations() {
        return `
            <div class="view-header">
                <h2>⚡ Batch Operations</h2>
                <p>Perform bulk operations on game entities</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>Batch Actions</h3>
                </div>
                <div class="grid grid-2">
                    <button class="btn btn-primary" onclick="controlPanel.batchLevelUp()">
                        ⬆️ Level Up All Specialists
                    </button>
                    <button class="btn btn-primary" onclick="controlPanel.batchSpawnIncidents()">
                        🚨 Spawn Incident Wave
                    </button>
                    <button class="btn btn-warning" onclick="controlPanel.batchModifyStats()">
                        📊 Modify All Stats
                    </button>
                    <button class="btn btn-danger" onclick="controlPanel.batchClearIncidents()">
                        🧹 Clear All Incidents
                    </button>
                </div>
            </div>
        `;
    }
    
    renderTimeline() {
        return `
            <div class="view-header">
                <h2>📅 Event Timeline</h2>
                <p>View and debug game events chronologically</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>Event History</h3>
                    <button class="btn btn-danger btn-sm" onclick="controlPanel.clearEventHistory()">
                        🗑️ Clear History
                    </button>
                </div>
                <div id="timeline-view">
                    ${this.renderTimelineEvents()}
                </div>
            </div>
        `;
    }
    
    renderTimelineEvents() {
        if (this.eventHistory.length === 0) {
            return '<p style="color: var(--text-secondary); padding: 20px;">No events recorded yet...</p>';
        }
        
        return `
            <table class="table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Event</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.eventHistory.map(event => `
                        <tr>
                            <td>${new Date(event.timestamp).toLocaleTimeString()}</td>
                            <td>${event.type || 'Unknown'}</td>
                            <td style="font-size: 12px;">${event.message || JSON.stringify(event)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    renderEntityGraph() {
        return `
            <div class="view-header">
                <h2>🔗 Entity Relationship Graph</h2>
                <p>Visualize connections between game entities</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>Entity Graph</h3>
                </div>
                <div id="graph-container" style="height: 600px; background: var(--bg-tertiary); border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <p style="color: var(--text-secondary);">Graph visualization coming soon...</p>
                </div>
            </div>
        `;
    }
    
    renderGodMode() {
        return `
            <div class="view-header">
                <h2>👑 God Mode Controls</h2>
                <p>Powerful testing and debugging commands</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>⚡ Power Commands</h3>
                </div>
                <div class="grid grid-3">
                    <button class="btn btn-warning" onclick="controlPanel.godSpawnWave(50)">
                        🌊 Spawn Wave (50)
                    </button>
                    <button class="btn btn-success" onclick="controlPanel.godCompleteAll()">
                        ✅ Complete All
                    </button>
                    <button class="btn btn-primary" onclick="controlPanel.godLevelUpAll()">
                        ⬆️ Level Up All
                    </button>
                    <button class="btn btn-primary" onclick="controlPanel.godMaxStats()">
                        ⚡ Max All Stats
                    </button>
                    <button class="btn btn-danger" onclick="controlPanel.godClearAll()">
                        🧹 Clear All Incidents
                    </button>
                    <button class="btn btn-success" onclick="controlPanel.godSetMoney(1000000)">
                        💰 Set Money to $1M
                    </button>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <h3>⏱️ Time Control</h3>
                </div>
                <div class="form-group">
                    <label>Game Speed Multiplier</label>
                    <input type="range" id="speed-slider" class="form-control" min="0.1" max="10" step="0.1" value="1.0" 
                           onchange="controlPanel.setGameSpeed(this.value)">
                    <div style="text-align: center; margin-top: 8px;">
                        <span id="speed-display">1.0x</span>
                    </div>
                </div>
                <div class="form-group">
                    <label>Fast Forward (seconds)</label>
                    <div style="display: flex; gap: 10px;">
                        <input type="number" id="ff-seconds" class="form-control" value="60" min="1" max="3600">
                        <button class="btn btn-primary" onclick="controlPanel.fastForward()">
                            ⏩ Fast Forward
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachViewEventListeners(viewName) {
        // Attach any dynamic event listeners based on view
        if (viewName === 'godmode') {
            const speedSlider = document.getElementById('speed-slider');
            if (speedSlider) {
                speedSlider.addEventListener('input', (e) => {
                    document.getElementById('speed-display').textContent = `${e.target.value}x`;
                });
            }
        }
    }
    
    // API Methods
    async spawnIncident() {
        try {
            const res = await fetch(`${API_BASE}/incidents/spawn`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'Incident spawned', 'success');
                await this.loadAllData();
                this.refreshCurrentView();
            }
        } catch (error) {
            this.showToast('Error', 'Failed to spawn incident', 'error');
        }
    }
    
    async addMoney(amount) {
        try {
            const res = await fetch(`${API_BASE}/economy/money`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount, reason: 'Control Panel' })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', `Added $${amount}`, 'success');
                await this.loadAllData();
                this.refreshCurrentView();
            }
        } catch (error) {
            this.showToast('Error', 'Failed to add money', 'error');
        }
    }
    
    async reloadConfig() {
        try {
            const res = await fetch(`${API_BASE}/config/reload`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'Configuration reloaded', 'success');
                await this.loadAllData();
                this.refreshCurrentView();
            }
        } catch (error) {
            this.showToast('Error', 'Failed to reload config', 'error');
        }
    }
    
    async refreshState() {
        await this.loadAllData();
        this.refreshCurrentView();
        this.showToast('Success', 'State refreshed', 'success');
    }
    
    async saveState() {
        try {
            const res = await fetch(`${API_BASE}/state/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slot: 'control_panel_backup' })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'State saved', 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to save state', 'error');
        }
    }
    
    // Entity Management Methods
    async createEntity(entityType) {
        try {
            // Try to load schema and generate template from it
            const schemaRes = await fetch(`${API_BASE}/schemas/${entityType}`);
            const schemaData = await schemaRes.json();
            
            if (schemaData.success && entityEditorModal) {
                const template = entityEditorModal.generateTemplateFromSchema(schemaData.data);
                if (template) {
                    await entityEditorModal.show(entityType, template, null, 'create');
                    return;
                }
            }
        } catch (error) {
            console.warn('Could not generate template from schema:', error);
        }
        
        // Fallback: Get hardcoded template for entity type
        try {
            const res = await fetch(`${API_BASE}/entities/templates/${entityType}`);
            const data = await res.json();
            
            if (data.success) {
                await entityEditorModal.show(entityType, data.data, null, 'create');
            } else {
                this.showToast('Error', 'Failed to load template', 'error');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to load template: ' + error.message, 'error');
        }
    }
    
    editEntity(entityType, index) {
        // Load entity data
        const data = this.entities[entityType] || {};
        let entities = [];
        
        // Extract entities array from different structures
        if (Array.isArray(data)) {
            entities = data;
        } else if (data.incident_types) {
            entities = data.incident_types;
        } else if (data.specialist_archetypes) {
            entities = data.specialist_archetypes;
        } else if (data.equipment) {
            entities = data.equipment;
        } else if (data.facilities) {
            entities = data.facilities;
        } else if (data.clients) {
            entities = data.clients;
        } else if (data.automation_scripts) {
            entities = data.automation_scripts;
        } else if (data.achievements) {
            entities = data.achievements;
        }
        
        if (entities[index]) {
            entityEditorModal.show(entityType, entities[index], index, 'edit');
        } else {
            this.showToast('Error', 'Entity not found', 'error');
        }
    }
    
    duplicateEntity(entityType, index) {
        // Load entity data
        const data = this.entities[entityType] || {};
        let entities = [];
        
        // Extract entities array from different structures
        if (Array.isArray(data)) {
            entities = data;
        } else if (data.incident_types) {
            entities = data.incident_types;
        } else if (data.specialist_archetypes) {
            entities = data.specialist_archetypes;
        } else if (data.equipment) {
            entities = data.equipment;
        } else if (data.facilities) {
            entities = data.facilities;
        } else if (data.clients) {
            entities = data.clients;
        } else if (data.automation_scripts) {
            entities = data.automation_scripts;
        } else if (data.achievements) {
            entities = data.achievements;
        }
        
        if (entities[index]) {
            const duplicated = JSON.parse(JSON.stringify(entities[index]));
            // Update ID and name for duplicate
            if (duplicated.id) {
                duplicated.id = duplicated.id + '_copy';
            }
            if (duplicated.name) {
                duplicated.name = duplicated.name + ' (Copy)';
            }
            entityEditorModal.show(entityType, duplicated, null, 'duplicate');
        } else {
            this.showToast('Error', 'Entity not found', 'error');
        }
    }
    
    async deleteEntity(entityType, index) {
        if (!confirm('Are you sure you want to delete this entity?')) return;
        
        this.showToast('Info', 'Entity deletion coming soon', 'warning');
    }
    
    importEntities(entityType) {
        this.showToast('Info', 'Import functionality coming soon', 'warning');
    }
    
    exportEntities(entityType) {
        const data = this.entities[entityType];
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${entityType}_export.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast('Success', 'Entities exported', 'success');
    }
    
    // God Mode Methods
    async godSpawnWave(count) {
        try {
            const res = await fetch(`${API_BASE}/godmode/spawn-wave`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', `Spawned ${count} incidents`, 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to spawn wave', 'error');
        }
    }
    
    async godCompleteAll() {
        try {
            const res = await fetch(`${API_BASE}/godmode/complete-all-incidents`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'All incidents completed', 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to complete incidents', 'error');
        }
    }
    
    async godLevelUpAll() {
        try {
            const res = await fetch(`${API_BASE}/godmode/level-up-all`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'All specialists leveled up', 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to level up', 'error');
        }
    }
    
    async godMaxStats() {
        try {
            const res = await fetch(`${API_BASE}/godmode/max-all-stats`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'All stats maxed', 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to max stats', 'error');
        }
    }
    
    async godClearAll() {
        try {
            const res = await fetch(`${API_BASE}/godmode/clear-incidents`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', 'All incidents cleared', 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to clear incidents', 'error');
        }
    }
    
    async godSetMoney(amount) {
        try {
            const res = await fetch(`${API_BASE}/godmode/set-money`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', `Money set to $${amount}`, 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to set money', 'error');
        }
    }
    
    async setGameSpeed(speed) {
        try {
            const res = await fetch(`${API_BASE}/time/speed`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ speed: parseFloat(speed) })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', `Game speed set to ${speed}x`, 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to set speed', 'error');
        }
    }
    
    async fastForward() {
        const seconds = document.getElementById('ff-seconds').value;
        try {
            const res = await fetch(`${API_BASE}/time/advance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ seconds: parseInt(seconds) })
            });
            const data = await res.json();
            if (data.success) {
                this.showToast('Success', `Fast forwarded ${seconds} seconds`, 'success');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to fast forward', 'error');
        }
    }
    
    clearEventHistory() {
        this.eventHistory = [];
        this.refreshCurrentView();
        this.showToast('Success', 'Event history cleared', 'success');
    }
    
    // Batch Operations
    batchLevelUp() {
        this.godLevelUpAll();
    }
    
    batchSpawnIncidents() {
        const count = prompt('How many incidents to spawn?', '10');
        if (count) {
            this.godSpawnWave(parseInt(count));
        }
    }
    
    batchModifyStats() {
        this.showToast('Info', 'Batch stat modification coming soon', 'warning');
    }
    
    batchClearIncidents() {
        if (confirm('Clear all incidents?')) {
            this.godClearAll();
        }
    }
    
    createWave() {
        this.showToast('Info', 'Wave creation coming soon', 'warning');
    }
    
    // Toast Notifications
    showToast(title, message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-header">
                <div class="toast-title">${title}</div>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="toast-message">${message}</div>
        `;
        container.appendChild(toast);
        
        setTimeout(() => toast.remove(), 5000);
    }
}

// Initialize Control Panel
let controlPanel;
document.addEventListener('DOMContentLoaded', () => {
    controlPanel = new ControlPanel();
});
