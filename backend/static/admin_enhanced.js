// Admin Dashboard JavaScript - Cyberpunk Edition with WebSocket Support

const API_BASE = '/api';
let refreshInterval = null;
let socket = null;
let eventLog = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔒 Cybersecurity Firm Admin - INITIALIZING...');
    initializeWebSocket();
    checkConnection();
    refreshData();
    startAutoRefresh();
});

// WebSocket Connection
function initializeWebSocket() {
    try {
        // Connect to SocketIO
        socket = io();
        
        socket.on('connect', () => {
            console.log('WebSocket connected');
            updateConnectionStatus('connected', 'CONNECTED [LIVE]');
            logActivity('WebSocket connection established', 'success');
        });
        
        socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus('error', 'DISCONNECTED');
            logActivity('WebSocket connection lost', 'error');
        });
        
        socket.on('game_event', (event) => {
            handleGameEvent(event);
        });
        
    } catch (error) {
        console.error('WebSocket initialization failed:', error);
        logActivity('WebSocket not available, using polling', 'warning');
    }
}

// Handle incoming game events
function handleGameEvent(event) {
    console.log('Game event received:', event);
    
    // Add to event log
    eventLog.unshift(event);
    if (eventLog.length > 100) {
        eventLog.pop();
    }
    
    // Update UI based on event type
    switch(event.type) {
        case 'game_state_update':
            updateGameStateDisplay(event.data);
            break;
        case 'incident_spawned':
            logActivity(event.data.message, 'warning');
            refreshIncidents();
            break;
        case 'specialist_action':
            logActivity(event.data.message, 'success');
            refreshSpecialists();
            break;
        case 'money_change':
            logActivity(event.data.message, 'success');
            updateMoneyDisplay(event.data.new_money);
            break;
        case 'wave_spawned':
            logActivity(event.data.message, 'warning');
            refreshIncidents();
            break;
        case 'incidents_completed':
            logActivity(event.data.message, 'success');
            refreshIncidents();
            break;
        case 'specialists_leveled':
            logActivity(event.data.message, 'success');
            refreshSpecialists();
            break;
        case 'incidents_cleared':
            logActivity(event.data.message, 'warning');
            refreshIncidents();
            break;
        case 'stats_maxed':
            logActivity(event.data.message, 'success');
            refreshSpecialists();
            break;
    }
}

// Connection check
async function checkConnection() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            if (!socket || !socket.connected) {
                updateConnectionStatus('connected', 'CONNECTED');
            }
            logActivity('Backend API online', 'success');
        } else {
            updateConnectionStatus('error', 'Backend Error');
            logActivity('Backend returned unhealthy status', 'error');
        }
    } catch (error) {
        updateConnectionStatus('error', 'CONNECTION FAILED');
        logActivity(`Connection failed: ${error.message}`, 'error');
    }
}

function updateConnectionStatus(status, text) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (statusDot && statusText) {
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = text;
    }
}

// Auto-refresh (less frequent with WebSocket, but still useful as fallback)
function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(refreshData, 10000); // Every 10 seconds (reduced from 5)
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Refresh all data
async function refreshData() {
    await Promise.all([
        loadGameState(),
        loadIncidents(),
        loadSpecialists(),
        loadClients()
    ]);
}

// Individual refresh functions
async function refreshIncidents() {
    await loadIncidents();
}

async function refreshSpecialists() {
    await loadSpecialists();
}

// Load game state
async function loadGameState() {
    try {
        const response = await fetch(`${API_BASE}/state/summary`);
        const data = await response.json();
        
        if (data.success) {
            updateGameStateDisplay(data.data);
        }
    } catch (error) {
        console.error('Failed to load game state:', error);
    }
}

function updateGameStateDisplay(summary) {
    const moneyEl = document.getElementById('stat-money');
    const incidentsEl = document.getElementById('stat-incidents');
    const specialistsEl = document.getElementById('stat-specialists');
    const slaEl = document.getElementById('stat-sla');
    
    if (moneyEl) moneyEl.textContent = `$${summary.current_money.toFixed(2)}`;
    if (incidentsEl) incidentsEl.textContent = summary.active_incidents;
    if (specialistsEl) specialistsEl.textContent = summary.total_specialists;
    if (slaEl) slaEl.textContent = `${summary.sla_compliance_rate.toFixed(1)}%`;
}

function updateMoneyDisplay(money) {
    const moneyEl = document.getElementById('stat-money');
    if (moneyEl) {
        moneyEl.textContent = `$${money.toFixed(2)}`;
    }
}

// Load incidents
async function loadIncidents() {
    try {
        const response = await fetch(`${API_BASE}/incidents`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('incidents-list');
            if (!container) return;
            
            if (data.data.length === 0) {
                container.innerHTML = '<p class="loading">No active incidents</p>';
            } else {
                container.innerHTML = data.data.slice(0, 10).map(incident => `
                    <div class="list-item ${incident.sla_remaining < 60 ? 'urgent' : ''}">
                        <div class="list-item-header">
                            <span>${incident.name}</span>
                            <span>${incident.status}</span>
                        </div>
                        <div class="list-item-details">
                            Difficulty: ${incident.difficulty} | SLA: ${incident.sla_remaining}s | Client: ${incident.client_name}
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load incidents:', error);
    }
}

// Load specialists
async function loadSpecialists() {
    try {
        const response = await fetch(`${API_BASE}/specialists`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('specialists-list');
            if (!container) return;
            
            if (data.data.length === 0) {
                container.innerHTML = '<p class="loading">No specialists</p>';
            } else {
                container.innerHTML = data.data.map(spec => `
                    <div class="list-item">
                        <div class="list-item-header">
                            <span>${spec.name}</span>
                            <span>Lv ${spec.level}</span>
                        </div>
                        <div class="list-item-details">
                            ${spec.specialty} | Status: ${spec.status} | XP: ${spec.xp}
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load specialists:', error);
    }
}

// Load clients
async function loadClients() {
    try {
        const response = await fetch(`${API_BASE}/clients`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('clients-list');
            if (!container) return;
            
            if (data.data.length === 0) {
                container.innerHTML = '<p class="loading">No clients</p>';
            } else {
                container.innerHTML = data.data.map(client => `
                    <div class="list-item">
                        <div class="list-item-header">
                            <span>${client.name}</span>
                            <span>Rep: ${client.reputation}%</span>
                        </div>
                        <div class="list-item-details">
                            Contract: $${client.contract_value} | Incident Rate: ${client.incident_rate_per_minute}/min
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

// Game control functions
async function pauseGame() {
    try {
        const response = await fetch(`${API_BASE}/time/pause`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            logActivity('Game paused', 'warning');
        }
    } catch (error) {
        logActivity('Failed to pause game', 'error');
    }
}

async function resumeGame() {
    try {
        const response = await fetch(`${API_BASE}/time/resume`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            logActivity('Game resumed', 'success');
        }
    } catch (error) {
        logActivity('Failed to resume game', 'error');
    }
}

async function setGameSpeed(speed) {
    try {
        document.getElementById('speed-value').textContent = `${speed}x`;
        const response = await fetch(`${API_BASE}/time/speed`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speed: parseFloat(speed) })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`Game speed set to ${speed}x`, 'success');
        }
    } catch (error) {
        logActivity('Failed to set game speed', 'error');
    }
}

async function fastForward() {
    try {
        const seconds = parseInt(document.getElementById('fast-forward-time').value);
        const response = await fetch(`${API_BASE}/time/advance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seconds })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`Fast-forwarded ${seconds} seconds`, 'success');
        }
    } catch (error) {
        logActivity('Failed to fast-forward', 'error');
    }
}

async function adjustMoney(subtract = false) {
    try {
        let amount = parseFloat(document.getElementById('money-amount').value);
        if (subtract) amount = -amount;
        
        const response = await fetch(`${API_BASE}/economy/money`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: Math.abs(amount), reason: subtract ? 'Admin deduction' : 'Admin addition' })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`${subtract ? 'Subtracted' : 'Added'} $${Math.abs(amount)}`, 'success');
            await loadGameState();
        }
    } catch (error) {
        logActivity('Failed to adjust money', 'error');
    }
}

async function spawnIncident() {
    try {
        const response = await fetch(`${API_BASE}/incidents/spawn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        if (data.success) {
            logActivity('Incident spawned', 'warning');
            await loadIncidents();
            await loadGameState();
        }
    } catch (error) {
        logActivity('Failed to spawn incident', 'error');
    }
}

async function batchSpawn(count) {
    try {
        const response = await fetch(`${API_BASE}/incidents/batch-spawn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`Spawned ${count} incidents`, 'warning');
            await loadIncidents();
            await loadGameState();
        }
    } catch (error) {
        logActivity(`Failed to spawn ${count} incidents`, 'error');
    }
}

// God Mode functions
async function spawnWave(count) {
    try {
        const response = await fetch(`${API_BASE}/godmode/spawn-wave`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`GOD MODE: Spawned wave of ${count} incidents`, 'warning');
            await loadIncidents();
            await loadGameState();
        }
    } catch (error) {
        logActivity('GOD MODE: Failed to spawn wave', 'error');
    }
}

async function completeAll() {
    try {
        const response = await fetch(`${API_BASE}/godmode/complete-all-incidents`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`GOD MODE: Completed ${data.data.count} incidents`, 'success');
            await loadIncidents();
            await loadGameState();
        }
    } catch (error) {
        logActivity('GOD MODE: Failed to complete all', 'error');
    }
}

async function levelUpAll() {
    try {
        const response = await fetch(`${API_BASE}/godmode/level-up-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ levels: 1 })
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`GOD MODE: Leveled up all specialists`, 'success');
            await loadSpecialists();
        }
    } catch (error) {
        logActivity('GOD MODE: Failed to level up all', 'error');
    }
}

async function maxStats() {
    try {
        const response = await fetch(`${API_BASE}/godmode/max-all-stats`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`GOD MODE: Maxed all specialist stats`, 'success');
            await loadSpecialists();
        }
    } catch (error) {
        logActivity('GOD MODE: Failed to max stats', 'error');
    }
}

async function clearIncidents() {
    try {
        const response = await fetch(`${API_BASE}/godmode/clear-incidents`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            logActivity(`GOD MODE: Cleared ${data.data.count} incidents`, 'warning');
            await loadIncidents();
            await loadGameState();
        }
    } catch (error) {
        logActivity('GOD MODE: Failed to clear incidents', 'error');
    }
}

async function reloadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config/reload`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            logActivity('Configuration reloaded successfully', 'success');
        }
    } catch (error) {
        logActivity('Failed to reload configuration', 'error');
    }
}

async function resetGameState() {
    if (!confirm('Are you sure you want to reset the game state? This cannot be undone!')) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE}/state/reset`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            logActivity('Game state reset', 'warning');
            await refreshData();
        }
    } catch (error) {
        logActivity('Failed to reset game state', 'error');
    }
}

// Activity logging
function logActivity(message, type = 'info') {
    const logContainer = document.getElementById('activity-log');
    if (!logContainer) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.insertBefore(logEntry, logContainer.firstChild);
    
    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// Export functions for HTML onclick handlers
window.pauseGame = pauseGame;
window.resumeGame = resumeGame;
window.setGameSpeed = setGameSpeed;
window.fastForward = fastForward;
window.adjustMoney = adjustMoney;
window.spawnIncident = spawnIncident;
window.batchSpawn = batchSpawn;
window.refreshData = refreshData;
window.spawnWave = spawnWave;
window.completeAll = completeAll;
window.levelUpAll = levelUpAll;
window.maxStats = maxStats;
window.clearIncidents = clearIncidents;
window.reloadConfig = reloadConfig;
window.resetGameState = resetGameState;

console.log('🔒 Admin Dashboard READY');
