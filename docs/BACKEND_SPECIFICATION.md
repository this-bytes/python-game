# 🎮 Backend Admin Panel - Complete Specification

## Overview

The Cybersecurity Firm game backend provides a **god-mode admin panel** for rapid development, testing, and debugging. Built with Flask, SocketIO, and a cyberpunk aesthetic, it offers real-time control over all game systems.

## 🚀 Quick Start

### Start the Backend Server

```bash
cd backend
python run_backend.py
```

Server starts on `http://localhost:5000`

### Access the Admin Panel

Open browser to: **http://localhost:5000/admin**

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Flask 3.0+ (Web framework)
- Flask-SocketIO (WebSocket support)
- Flask-CORS (Cross-origin requests)
- Pydantic 2.0+ (Data validation)
- Python-dotenv (Configuration)
- Watchdog (File monitoring)

**Frontend:**
- Vanilla JavaScript (No framework overhead)
- Socket.IO client (Real-time updates)
- Cyberpunk CSS theme (Neon effects, CRT simulation)

### Directory Structure

```
/backend/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── run_backend.py              # Server launcher
├── models/
│   ├── __init__.py
│   └── game_models.py          # Pydantic data models
├── routes/
│   ├── analytics.py            # Analytics endpoints
│   ├── godmode.py              # God mode commands
│   ├── state.py                # Game state management
│   ├── specialists.py          # Specialist CRUD
│   ├── incidents.py            # Incident management
│   ├── clients.py              # Client management
│   ├── economy.py              # Economy controls
│   ├── automation.py           # Automation scripts
│   ├── config_routes.py        # Config hot-reload
│   └── time.py                 # Time control
├── services/
│   ├── websocket_service.py    # WebSocket broadcasting
│   ├── analytics_service.py    # Metrics calculation
│   └── json_service.py         # JSON file operations
└── static/
    ├── admin.html              # Admin dashboard
    ├── admin.css               # Cyberpunk styling
    └── admin_enhanced.js       # Dashboard logic
```

## 📡 API Endpoints

### Core Endpoints

#### Game State
- `GET /api/state` - Full game state snapshot
- `GET /api/state/summary` - Lightweight summary
- `PUT /api/state` - Update game state
- `POST /api/state/reset` - Reset to initial state
- `POST /api/state/save` - Save game state
- `POST /api/state/load` - Load game state

#### Time Control
- `POST /api/time/pause` - Pause game
- `POST /api/time/resume` - Resume game
- `POST /api/time/speed` - Set game speed (0.1x - 10x)
- `POST /api/time/advance` - Fast-forward time
- `GET /api/time/status` - Get time status

#### Economy
- `POST /api/economy/money` - Adjust money
- `GET /api/economy/metrics` - Get financial metrics

### Analytics Endpoints

#### Performance Metrics
- `GET /api/analytics/summary` - Comprehensive analytics
- `GET /api/analytics/revenue` - Revenue metrics
- `GET /api/analytics/incidents` - Incident statistics
- `GET /api/analytics/specialists` - Specialist metrics
- `GET /api/analytics/sla` - SLA compliance
- `GET /api/analytics/history/{metric}` - Historical data

**Response Format:**
```json
{
  "success": true,
  "data": {
    "revenue": {
      "current_money": 15000.50,
      "total_earned": 50000,
      "total_spent": 35000,
      "net_profit": 15000
    },
    "incidents": {
      "total_incidents": 150,
      "active": 5,
      "completed": 140,
      "failed": 5,
      "success_rate": 93.3
    }
  },
  "timestamp": "2025-10-17T02:00:00Z"
}
```

### God Mode Endpoints

#### Powerful Testing Commands
- `POST /api/godmode/spawn-wave` - Spawn wave of incidents
- `POST /api/godmode/complete-all-incidents` - Instantly complete all
- `POST /api/godmode/level-up-all` - Level up all specialists
- `POST /api/godmode/max-all-stats` - Max out all stats
- `POST /api/godmode/set-money` - Set exact money amount
- `POST /api/godmode/clear-incidents` - Clear all incidents

**Example: Spawn Wave**
```bash
curl -X POST http://localhost:5000/api/godmode/spawn-wave \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'
```

**Response:**
```json
{
  "success": true,
  "message": "Spawned 50 incidents",
  "data": {
    "count": 50,
    "incidents": [...]
  }
}
```

### Configuration Management
- `POST /api/config/reload` - Hot-reload all JSON configs
- `GET /api/config/files` - List config files
- `GET /api/config/files/{name}` - Get config file content
- `PUT /api/config/files/{name}` - Update config file

## 🎨 Admin Panel Features

### Real-Time Dashboard

**Live Metrics:**
- Current money (updates instantly)
- Active incidents count
- Specialist availability
- SLA compliance rate

**WebSocket Events:**
- Game state updates
- Incident spawned/completed
- Specialist actions
- Money changes
- Level ups

### God Mode Controls

**5 Powerful Commands:**
1. **Spawn Wave** - Create 50 incidents instantly
2. **Complete All** - Finish all active incidents
3. **Level Up All** - Boost all specialists
4. **Max Stats** - Set all stats to 100
5. **Clear All** - Remove all incidents

### Time Manipulation

**Controls:**
- Pause/Resume game
- Adjust speed (0.1x to 5x)
- Fast-forward by seconds
- Precise time control

### Economy Controls

**Money Management:**
- Add/subtract any amount
- Instant balance updates
- Real-time visual feedback

### Cyberpunk Aesthetic

**Visual Effects:**
- CRT screen scanlines
- Neon green/blue/pink borders
- Glitch animations on hover
- Pulsing status indicators
- Matrix-style activity log
- Monospace fonts throughout

**Color Scheme:**
```css
--cyber-black: #000000
--cyber-green: #00ff00  (primary)
--cyber-blue: #00ffff   (secondary)
--cyber-pink: #ff00ff   (accents)
--cyber-red: #ff0000    (warnings)
--cyber-yellow: #ffff00 (caution)
```

## 🔧 Services

### WebSocket Service

**Broadcasts:**
- `game_state_update` - Full state changes
- `incident_spawned` - New incident created
- `specialist_action` - Specialist events
- `money_change` - Balance updates
- `wave_spawned` - Batch incidents
- `incidents_completed` - Mass completion
- `specialists_leveled` - Level up events

**Event Format:**
```javascript
{
  type: "incident_spawned",
  data: {
    incident: {...},
    message: "Incident spawned: DDoS Attack"
  },
  timestamp: "2025-10-17T02:00:00Z"
}
```

### Analytics Service

**Metrics Tracked:**
- Revenue (current, earned, spent, profit)
- Incidents (total, active, completed, failed, success rate)
- Specialists (total, available, busy, avg level)
- SLA (compliance rate, violations)

**Historical Data:**
- Configurable time ranges (1h, 24h, 7d)
- Up to 1000 data points per metric
- Automatic cleanup of old data

### JSON Service

**Features:**
- Safe read/write operations
- Automatic backups before changes
- Backup retention (last 10)
- Schema validation
- Restore from backup
- List all config files

**Backup Structure:**
```
/data/backups/
├── specialists_20251017_020000.json
├── specialists_20251017_010000.json
├── incidents_20251017_020000.json
└── ...
```

## 🎯 Use Cases

### Development Workflow

1. Start backend: `python backend/run_backend.py`
2. Open admin panel in browser
3. Make code changes to game logic
4. Use dashboard to test changes instantly
5. Hot-reload configs as needed

### Rapid Testing

**Scenario: Test specialist assignment system**
```
1. Click "Spawn Wave" (50 incidents)
2. Watch specialists get assigned
3. Monitor SLA compliance
4. Adjust specialist stats via god mode
5. Test again with different parameters
```

### Game Balancing

**Adjust in real-time:**
- Incident difficulty
- SLA timers
- Reward multipliers
- Specialist stats
- Client parameters

**Process:**
1. Edit JSON file
2. Click "Hot Reload" in admin panel
3. Changes apply instantly
4. Test balance
5. Iterate

### Stress Testing

**Load Testing:**
```javascript
// Spawn 50 incidents
POST /api/godmode/spawn-wave { "count": 50 }

// Monitor performance
GET /api/analytics/summary

// Check SLA compliance
GET /api/analytics/sla
```

### Debugging

**Common Scenarios:**

**Issue: Specialists not assigning**
1. Check specialist list in admin panel
2. Verify statuses (available vs busy)
3. Spawn single incident
4. Watch real-time event log
5. Diagnose assignment logic

**Issue: Money not increasing**
1. Complete some incidents manually
2. Check analytics revenue metrics
3. Review economy settings
4. Test with god mode money injection

## 🔐 Security Note

**⚠️ DEVELOPMENT ONLY**

This backend is designed for local development and testing. It includes:
- No authentication
- No authorization
- Arbitrary state manipulation
- Full god mode access

**Do NOT use in production without:**
- API authentication (JWT, API keys)
- Rate limiting
- Input validation and sanitization
- Role-based access control
- Audit logging
- HTTPS encryption

## 🐛 Troubleshooting

### Server won't start

**Check:**
```bash
# Port already in use?
lsof -i :5000

# Dependencies installed?
pip install -r requirements.txt

# Python version correct?
python --version  # Should be 3.12+
```

### WebSocket not connecting

**Check:**
```javascript
// Browser console
console.log(io);  // Should be defined

// Network tab
// Look for /socket.io/ requests

// Try manual connection
const socket = io();
socket.on('connect', () => console.log('Connected!'));
```

### API returns 503

**Cause:** Game state not initialized

**Solution:**
- Backend started but game not running
- OR backend running standalone
- Check logs for initialization errors

### Hot-reload not working

**Check:**
```bash
# JSON file syntax
python -m json.tool data/specialists.json

# File permissions
ls -la data/

# Backup creation
ls -la data/backups/
```

### CORS errors

**Fix:**
```python
# backend/config.py
CORS_ORIGINS = "*"  # Development

# OR specific origin
CORS_ORIGINS = "http://localhost:3000"
```

## 📊 Performance

**Benchmarks:**
- WebSocket latency: <50ms
- API response time: <100ms
- Dashboard refresh: 5-10 seconds (configurable)
- Hot-reload time: <1 second

**Optimization:**
- WebSocket reduces polling overhead
- Efficient JSON serialization
- Minimal JavaScript framework weight
- CSS animations hardware-accelerated

## 🚀 Future Enhancements

### Planned Features
- [ ] Visual JSON editor (Monaco Editor)
- [ ] Analytics charts (Chart.js integration)
- [ ] Feature flag management UI
- [ ] Live operations scheduling
- [ ] Swagger/OpenAPI docs
- [ ] Multiple backend instances
- [ ] Distributed game state
- [ ] A/B testing framework
- [ ] Performance profiling
- [ ] Automated stress tests

### Potential Improvements
- WebGL visualizations
- 3D incident/specialist views
- Audio alerts for critical events
- Mobile-responsive design
- Dark/light theme toggle
- Keyboard shortcuts
- Command palette (Cmd+K)
- Export analytics as CSV
- Shareable dashboard links

## 📚 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Socket.IO Documentation**: https://socket.io/docs/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Cyberpunk Design**: Inspired by Cyberpunk 2077 UI

## 🤝 Contributing

When adding new endpoints:
1. Create route in appropriate blueprint file
2. Add Pydantic model for validation
3. Follow existing error handling patterns
4. Return consistent JSON response format
5. Add example to README
6. Update admin panel if UI needed

## 📄 License

Same as main project.

---

**Built with 🔒 by the Cybersecurity Firm Dev Team**

*Making game development feel like hacking the mainframe.*
