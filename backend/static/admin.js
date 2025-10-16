// Admin Dashboard JavaScript

const API_BASE = '/api';
let refreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initialized');
    checkConnection();
    refreshData();
    startAutoRefresh();
});

// Connection check
async function checkConnection() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateConnectionStatus('connected', 'Connected');
            logActivity('Connected to backend API', 'success');
        } else {
            updateConnectionStatus('error', 'Backend Error');
            logActivity('Backend returned unhealthy status', 'error');
        }
    } catch (error) {
        updateConnectionStatus('error', 'Connection Failed');
        logActivity(`Connection failed: ${error.message}`, 'error');
    }
}

function updateConnectionStatus(status, text) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

// Auto-refresh
function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(refreshData, 5000); // Refresh every 5 seconds
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

// Load game state
async function loadGameState() {
    try {
        const response = await fetch(`${API_BASE}/state/summary`);
        const data = await response.json();
        
        if (data.success) {
            const summary = data.data;
            document.getElementById('stat-money').textContent = `$${summary.money.toFixed(2)}`;
            document.getElementById('stat-incidents').textContent = summary.active_incidents;
            document.getElementById('stat-specialists').textContent = summary.total_specialists;
            document.getElementById('stat-sla').textContent = `${summary.sla_compliance_rate.toFixed(1)}%`;
        }
    } catch (error) {
        console.error('Failed to load game state:', error);
    }
}

// Load incidents
async function loadIncidents() {
    try {
        const response = await fetch(`${API_BASE}/incidents`);
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('incidents-list');
            
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
                            Difficulty: ${incident.difficulty} | 
                            SLA: ${Math.floor(incident.sla_remaining)}s | 
                            ${incident.specialty}
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
            
            container.innerHTML = data.data.map(spec => `
                <div class="list-item">
                    <div class="list-item-header">
                        <span>${spec.name}</span>
                        <span>Level ${spec.level}</span>
                    </div>
                    <div class="list-item-details">
                        ${spec.specialty} | 
                        Status: ${spec.status} | 
                        XP: ${spec.xp}
                    </div>
                </div>
            `).join('');
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
            
            container.innerHTML = data.data.map(client => `
                <div class="list-item">
                    <div class="list-item-header">
                        <span>${client.name}</span>
                        <span>Rep: ${client.reputation}</span>
                    </div>
                    <div class="list-item-details">
                        Rate: ${client.incident_rate_per_minute}/min | 
                        Contract: $${client.contract_value} | 
                        ${client.active ? 'Active' : 'Inactive'}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

// Game controls
async function pauseGame() {
    try {
        const response = await fetch(`${API_BASE}/time/pause`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logActivity('Game paused', 'success');
        } else {
            logActivity(`Failed to pause: ${data.message}`, 'error');
        }
    } catch (error) {
        logActivity(`Error pausing game: ${error.message}`, 'error');
    }
}

async function resumeGame() {
    try {
        const response = await fetch(`${API_BASE}/time/resume`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logActivity('Game resumed', 'success');
        } else {
            logActivity(`Failed to resume: ${data.message}`, 'error');
        }
    } catch (error) {
        logActivity(`Error resuming game: ${error.message}`, 'error');
    }
}

async function setGameSpeed(speed) {
    document.getElementById('speed-value').textContent = `${speed}x`;
    
    try {
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
        logActivity(`Error setting speed: ${error.message}`, 'error');
    }
}

async function fastForward() {
    const seconds = parseInt(document.getElementById('fast-forward-time').value);
    
    try {
        logActivity(`Fast-forwarding ${seconds} seconds...`, 'warning');
        const response = await fetch(`${API_BASE}/time/advance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seconds })
        });
        const data = await response.json();
        
        if (data.success) {
            logActivity(`Fast-forwarded ${seconds} seconds`, 'success');
            refreshData();
        }
    } catch (error) {
        logActivity(`Error fast-forwarding: ${error.message}`, 'error');
    }
}

// Money controls
async function adjustMoney(subtract = false) {
    const amount = parseInt(document.getElementById('money-amount').value);
    const finalAmount = subtract ? -amount : amount;
    
    try {
        const response = await fetch(`${API_BASE}/economy/money`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                amount: finalAmount,
                reason: 'Manual admin adjustment'
            })
        });
        const data = await response.json();
        
        if (data.success) {
            logActivity(`Money adjusted: ${finalAmount >= 0 ? '+' : ''}$${finalAmount}`, 'success');
            loadGameState();
        }
    } catch (error) {
        logActivity(`Error adjusting money: ${error.message}`, 'error');
    }
}

// Incident controls
async function spawnIncident() {
    try {
        const response = await fetch(`${API_BASE}/incidents/spawn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        
        if (data.success) {
            logActivity('Incident spawned', 'success');
            loadIncidents();
            loadGameState();
        }
    } catch (error) {
        logActivity(`Error spawning incident: ${error.message}`, 'error');
    }
}

async function batchSpawn(count) {
    try {
        logActivity(`Spawning ${count} incidents...`, 'warning');
        const response = await fetch(`${API_BASE}/incidents/batch-spawn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count })
        });
        const data = await response.json();
        
        if (data.success) {
            logActivity(`Spawned ${data.count} incidents`, 'success');
            loadIncidents();
            loadGameState();
        }
    } catch (error) {
        logActivity(`Error batch spawning: ${error.message}`, 'error');
    }
}

// Config management
async function reloadConfig() {
    try {
        logActivity('Reloading configuration...', 'warning');
        const response = await fetch(`${API_BASE}/config/reload`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logActivity('Configuration reloaded successfully', 'success');
            showConfigStatus('Configuration reloaded', 'success');
            refreshData();
        } else {
            logActivity(`Failed to reload: ${data.message}`, 'error');
            showConfigStatus(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        logActivity(`Error reloading config: ${error.message}`, 'error');
        showConfigStatus(`Error: ${error.message}`, 'error');
    }
}

async function resetGameState() {
    if (!confirm('Are you sure you want to reset the game state? This cannot be undone.')) {
        return;
    }
    
    try {
        logActivity('Resetting game state...', 'warning');
        const response = await fetch(`${API_BASE}/state/reset`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logActivity('Game state reset successfully', 'success');
            showConfigStatus('Game state reset', 'success');
            refreshData();
        }
    } catch (error) {
        logActivity(`Error resetting game: ${error.message}`, 'error');
        showConfigStatus(`Error: ${error.message}`, 'error');
    }
}

function showConfigStatus(message, type) {
    const statusDiv = document.getElementById('config-status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message show ${type}`;
    
    setTimeout(() => {
        statusDiv.className = 'status-message';
    }, 5000);
}

// Activity log
function logActivity(message, type = '') {
    const log = document.getElementById('activity-log');
    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement('p');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${timestamp}] ${message}`;
    
    log.insertBefore(entry, log.firstChild);
    
    // Keep only last 50 entries
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}
