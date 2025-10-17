# 🎯 Backend Quick Start Guide

## TL;DR

```bash
# Start backend
cd backend && python run_backend.py

# Open admin panel
open http://localhost:5000/admin
```

**That's it. You're now a god.** 👑

## 5-Minute Tour

### 1. Start the Backend (30 seconds)

```bash
cd /path/to/python-game
python backend/run_backend.py
```

You should see:
```
[BACKEND] Backend API initialized with WebSocket support
[BACKEND] Starting server on 0.0.0.0:5000 (debug=True)
```

### 2. Open Admin Panel (10 seconds)

Navigate to: `http://localhost:5000/admin`

You'll see:
- 🔒 CYBERSECURITY FIRM - CONTROL CENTER header
- Green "CONNECTED [LIVE]" status
- Game state metrics (money, incidents, specialists, SLA)
- Multiple control panels

### 3. Test God Mode (4 minutes)

**Spawn Wave:**
1. Click "🌊 SPAWN WAVE (50)"
2. Watch incident counter jump to 50
3. See real-time event log update

**Complete All:**
1. Click "✅ COMPLETE ALL"
2. Watch incidents clear instantly
3. Money increases from rewards

**Level Up:**
1. Click "⬆️ LEVEL UP ALL"
2. Specialist levels increase by 1
3. Check specialist list for updated levels

**Max Stats:**
1. Click "⚡ MAX STATS"
2. All specialists get 100 speed, 100 accuracy
3. View specialist details to confirm

**Clear All:**
1. Spawn more incidents
2. Click "🧹 CLEAR ALL"
3. Incident queue empties

## Common Workflows

### Testing Incident Assignment

```bash
1. Open admin panel
2. Click "🚨 SPAWN SINGLE"
3. Watch live event feed
4. See which specialist gets assigned
5. Monitor SLA timer
```

### Balancing Economy

```bash
1. Edit data/clients.json
2. Change incident_rate_per_minute
3. Click "🔄 HOT RELOAD" in admin panel
4. Changes apply instantly
5. Spawn incidents to test new rate
```

### Stress Testing

```bash
1. Click "🚨🚨🚨 SPAWN 50"
2. Monitor SLA compliance metric
3. Watch specialists juggle incidents
4. Check for any failures
5. Adjust specialist stats if needed
```

### Time Manipulation

```bash
1. Drag speed slider to 5x
2. Game runs 5x faster
3. OR click "⏩ FAST FORWARD"
4. Enter 300 seconds (5 minutes)
5. Game simulates 5 minutes instantly
```

## Key Features

### Real-Time Updates

Admin panel updates **automatically** via WebSocket:
- Money changes appear instantly
- Incident spawns show immediately
- Specialist actions broadcast live
- No manual refresh needed

### Hot-Reload Everything

Edit any JSON file:
```json
// data/specialists.json
{
  "specialists": [
    {
      "id": "spec_001",
      "level": 10,  // Changed from 5
      "speed": 95   // Changed from 85
    }
  ]
}
```

Click "🔄 HOT RELOAD" → Changes apply without restart.

### Cyberpunk Aesthetic

**Visual Effects:**
- CRT scanlines across entire screen
- Neon borders pulse on hover
- Glitch effect on title
- Matrix-style scrolling log
- Color-coded status indicators

**Color Meanings:**
- 🟢 Green: Success, normal operations
- 🔵 Blue: Information, stats
- 🟡 Yellow: Warning, pending
- 🔴 Red: Danger, critical
- 🟣 Pink: Special actions

## API Examples

### Get Game Summary

```bash
curl http://localhost:5000/api/state/summary
```

```json
{
  "success": true,
  "data": {
    "current_money": 5000.0,
    "active_incidents": 3,
    "total_specialists": 2,
    "sla_compliance_rate": 100.0
  }
}
```

### Spawn Incident

```bash
curl -X POST http://localhost:5000/api/incidents/spawn \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Add Money

```bash
curl -X POST http://localhost:5000/api/economy/money \
  -H "Content-Type: application/json" \
  -d '{"amount": 10000, "reason": "Testing"}'
```

### God Mode: Spawn Wave

```bash
curl -X POST http://localhost:5000/api/godmode/spawn-wave \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'
```

### Analytics

```bash
curl http://localhost:5000/api/analytics/summary
```

```json
{
  "success": true,
  "data": {
    "revenue": {
      "current_money": 15000,
      "total_earned": 50000,
      "net_profit": 15000
    },
    "incidents": {
      "total_incidents": 150,
      "completed": 140,
      "success_rate": 93.3
    },
    "specialists": {
      "total_specialists": 5,
      "average_level": 7.2
    }
  }
}
```

## Troubleshooting

### "Connection Failed" in Admin Panel

**Check if backend is running:**
```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy"}`

### WebSocket Not Connecting

**Check browser console:**
1. Open DevTools (F12)
2. Look for Socket.IO connection messages
3. Should see: "WebSocket connected"

**If not:**
```bash
# Restart backend
python backend/run_backend.py

# Refresh browser
Cmd+R / Ctrl+R
```

### API Returns 503

**Cause:** Game state not initialized

**When it happens:**
- Backend running standalone (not integrated with game)
- Normal for testing backend only

**Fix:**
- Some endpoints work without game state (config, health)
- Others require game to be running

### "Module Not Found" Error

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask
- flask-cors
- flask-socketio
- pydantic
- python-dotenv
- watchdog

## Pro Tips

### 1. Keep Admin Panel Open

Run backend in one terminal, game in another:
```bash
# Terminal 1
python backend/run_backend.py

# Terminal 2  
python src/main.py
```

Admin panel shows real-time game state from both!

### 2. Use Keyboard Shortcuts

Browser shortcuts work:
- `Cmd+R` / `Ctrl+R`: Refresh dashboard
- `Cmd+Shift+R`: Hard refresh (clear cache)
- `Cmd+Option+I`: Open DevTools

### 3. Monitor Live Event Feed

Bottom panel shows everything:
- Every incident spawned
- Every specialist action
- Money changes
- Level ups
- God mode commands

Keep an eye on it while testing!

### 4. Combine God Mode Commands

**Ultimate power combo:**
```
1. Click "🌊 SPAWN WAVE (50)"   // Create chaos
2. Click "⬆️ LEVEL UP ALL"      // Boost team
3. Click "⚡ MAX STATS"          // Maximize power
4. Watch them obliterate queue  // Profit
```

### 5. Time Travel for Testing

**Fast progression:**
```
1. Set speed to 5x
2. Click "⏩ FAST FORWARD"
3. Enter 3600 (1 hour)
4. See what happens after 5 hours of gameplay
```

## Configuration

### Environment Variables

Create `.env` file:
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
BACKEND_DEBUG=True
CORS_ORIGINS=*
```

### Default Settings

```python
# backend/config.py
HOST = "0.0.0.0"           # Listen on all interfaces
PORT = 5000                # Default port
DEBUG = True               # Enable debug mode
CORS_ORIGINS = "*"         # Allow all origins (dev only!)
```

## What's Next?

### Explore More Endpoints

Check the full API documentation:
- `/docs/BACKEND_SPECIFICATION.md`
- Complete list of all endpoints
- Request/response examples
- Error handling patterns

### Build Custom Tools

Use the API to create your own tools:
```python
import requests

# Your custom automation
def auto_balance_game():
    response = requests.get('http://localhost:5000/api/analytics/summary')
    data = response.json()['data']
    
    if data['incidents']['success_rate'] < 80:
        # Level up specialists
        requests.post('http://localhost:5000/api/godmode/level-up-all')
```

### Integrate with Game

Add backend to game loop:
```python
# src/main.py
from backend.app import BackendApp
from threading import Thread

backend = BackendApp(game_state)
Thread(target=backend.run, daemon=True).start()
```

## Getting Help

**Check logs:**
```bash
# Backend terminal shows all requests
[BACKEND] GET /api/state/summary - 200
[BACKEND] POST /api/godmode/spawn-wave - 200
```

**Check browser console:**
```javascript
// Should see
WebSocket connected
Game event received: {type: "incident_spawned", ...}
```

**Still stuck?**
- Read `docs/BACKEND_SPECIFICATION.md` for details
- Check `backend/README.md` for more examples
- Review existing tests in `backend/test_backend.py`

---

**You're now ready to rule your game with an iron fist.** 👑

*Remember: With great power comes great fun.*
