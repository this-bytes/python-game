# Backend API Server

This directory contains the Flask-based backend API server for live debugging and manipulation of the Cybersecurity Firm game.

## 🚀 Quick Start

### Start the Backend Server

```bash
# From project root
python backend/run_backend.py
```

The server will start on `http://localhost:5000` by default.

### Access the Admin Dashboard

Open your browser to:
- **Admin Dashboard**: http://localhost:5000/admin
- **API Health Check**: http://localhost:5000/health

## 📋 Features

### Real-Time Game Manipulation
- **Pause/Resume**: Control game flow
- **Time Controls**: Adjust game speed (0.1x - 10x) or fast-forward time
- **Money Management**: Add/subtract money instantly
- **Incident Spawning**: Manually spawn incidents (single or batch)
- **Specialist Management**: View, edit, and manage specialists
- **Client Control**: Adjust client parameters and reputation
- **Configuration Hot-Reload**: Reload JSON configs without restarting

### Admin Dashboard
- Live game state monitoring
- Interactive controls for all game systems
- Activity log showing all actions
- Real-time metrics display
- Incident queue visualization
- Specialist roster view
- Client list with reputation tracking

## 🛠️ API Endpoints

### Game State
- `GET /api/state` - Full game state snapshot
- `PUT /api/state` - Update game state
- `POST /api/state/reset` - Reset to initial state
- `GET /api/state/summary` - Lightweight summary
- `POST /api/state/save` - Save game state
- `POST /api/state/load` - Load game state

### Specialists
- `GET /api/specialists` - List all specialists
- `GET /api/specialists/{id}` - Get specific specialist
- `POST /api/specialists` - Create/hire specialist
- `PUT /api/specialists/{id}` - Update specialist stats
- `DELETE /api/specialists/{id}` - Remove specialist
- `POST /api/specialists/{id}/assign` - Assign to incident
- `GET /api/specialists/available` - Get available specialists

### Incidents
- `GET /api/incidents` - List all incidents (with filters)
- `GET /api/incidents/{id}` - Get specific incident
- `POST /api/incidents/spawn` - Spawn single incident
- `POST /api/incidents/batch-spawn` - Spawn multiple incidents
- `PUT /api/incidents/{id}` - Update incident
- `DELETE /api/incidents/{id}` - Remove incident

### Clients
- `GET /api/clients` - List all clients
- `GET /api/clients/{id}` - Get specific client
- `PUT /api/clients/{id}` - Update client parameters

### Economy
- `POST /api/economy/money` - Adjust money
- `GET /api/economy/metrics` - Get financial metrics
- `POST /api/economy/invest` - Make investment (low/medium/high risk)
- `POST /api/economy/withdraw` - Withdraw from investment
- `GET /api/economy/passive-income` - Get passive income breakdown

### Prestige & Rebirth
- `GET /api/prestige/calculate` - Calculate prestige points if reset now
- `POST /api/prestige/perform` - Perform prestige reset
- `GET /api/prestige/upgrades` - List all prestige upgrades
- `POST /api/prestige/upgrades/{id}/purchase` - Purchase prestige upgrade

### Offline Progress
- `GET /api/offline-progress` - Get offline progress report
- `POST /api/offline-progress/simulate` - Simulate offline time (testing)

### Save/Load
- `POST /api/state/save` - Save game to slot
- `POST /api/state/load` - Load game from slot
- `GET /api/saves` - List all save files with metadata
- `DELETE /api/saves/{slot}` - Delete save file

### Automation
- `GET /api/automation-scripts` - List automation scripts
- `GET /api/automation-scripts/{id}` - Get specific script
- `PUT /api/automation-scripts/{id}` - Update script parameters
- `POST /api/automation-scripts/{id}/upgrade` - Upgrade script to next level
- `PUT /api/automation-scripts/{id}/set-priority` - Change script priority
- `PUT /api/automation-scripts/{id}/set-cooldown` - Adjust cooldown (admin)
- `GET /api/automation-scripts/stats` - Get automation statistics

### Configuration
- `POST /api/config/reload` - Hot-reload all JSON configs
- `GET /api/config/files` - List config files
- `GET /api/config/files/{name}` - Get config file content
- `PUT /api/config/files/{name}` - Update config file

### Time Control
- `POST /api/time/pause` - Pause game
- `POST /api/time/resume` - Resume game
- `POST /api/time/speed` - Set game speed multiplier
- `POST /api/time/advance` - Fast-forward time
- `GET /api/time/status` - Get time status

## 📖 Usage Examples

### Using cURL

```bash
# Check server health
curl http://localhost:5000/health

# Get game state summary
curl http://localhost:5000/api/state/summary

# Add $1000
curl -X POST http://localhost:5000/api/economy/money \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "reason": "Testing"}'

# Make an investment
curl -X POST http://localhost:5000/api/economy/invest \
  -H "Content-Type: application/json" \
  -d '{"investment_type": "medium_risk", "amount": 10000}'

# Upgrade automation script
curl -X POST http://localhost:5000/api/automation-scripts/auto_assign_network_low/upgrade

# Save game to slot 1
curl -X POST http://localhost:5000/api/state/save \
  -H "Content-Type: application/json" \
  -d '{"slot": 1}'

# List all saves
curl http://localhost:5000/api/saves

# Calculate prestige points
curl http://localhost:5000/api/prestige/calculate

# Purchase prestige upgrade
curl -X POST http://localhost:5000/api/prestige/upgrades/xp_boost_1/purchase

# Spawn an incident
curl -X POST http://localhost:5000/api/incidents/spawn \
  -H "Content-Type: application/json" \
  -d '{}'

# Spawn 50 incidents (stress test)
curl -X POST http://localhost:5000/api/incidents/batch-spawn \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'

# Pause the game
curl -X POST http://localhost:5000/api/time/pause

# Set game speed to 5x
curl -X POST http://localhost:5000/api/time/speed \
  -H "Content-Type: application/json" \
  -d '{"speed": 5.0}'

# Fast-forward 60 seconds
curl -X POST http://localhost:5000/api/time/advance \
  -H "Content-Type: application/json" \
  -d '{"seconds": 60}'

# Update a specialist's level
curl -X PUT http://localhost:5000/api/specialists/spec_001 \
  -H "Content-Type: application/json" \
  -d '{"level": 10, "xp": 5000}'

# Hot-reload all configurations
curl -X POST http://localhost:5000/api/config/reload
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Get game summary
response = requests.get(f"{BASE_URL}/state/summary")
print(response.json())

# Spawn incident
response = requests.post(f"{BASE_URL}/incidents/spawn", json={})
incident = response.json()['data']
print(f"Spawned: {incident['name']}")

# Add money
response = requests.post(f"{BASE_URL}/economy/money", json={
    "amount": 5000,
    "reason": "Investment funding"
})
print(response.json())
```

## ⚙️ Configuration

Configuration is loaded from environment variables. Create a `.env` file in the project root:

```env
# Backend settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
BACKEND_DEBUG=True
CORS_ORIGINS=*
```

## 🧪 Testing

Run the backend test suite:

```bash
python backend/test_backend.py
```

This will:
1. Initialize a GameState
2. Test all major API endpoints
3. Verify response formats
4. Report any errors

## 📁 Directory Structure

```
backend/
├── __init__.py              # Package initialization
├── app.py                   # Main Flask application
├── config.py                # Configuration management
├── run_backend.py          # Standalone server script
├── test_backend.py         # Backend test suite
├── routes/                  # API route blueprints
│   ├── __init__.py
│   ├── state.py            # Game state routes
│   ├── specialists.py      # Specialist management
│   ├── incidents.py        # Incident management
│   ├── clients.py          # Client & economy routes
│   ├── economy.py          # Economy routes (re-export)
│   ├── automation.py       # Automation scripts
│   ├── config_routes.py    # Configuration management
│   └── time.py             # Time control
└── static/                  # Admin dashboard files
    ├── admin.html          # Dashboard HTML
    ├── admin.css           # Dashboard styles
    └── admin.js            # Dashboard JavaScript
```

## 🎯 Use Cases

### Development Workflow
1. Start backend server: `python backend/run_backend.py`
2. Open admin dashboard in browser
3. Make code changes to game logic
4. Use dashboard to test changes instantly
5. Hot-reload configs as needed

### Debugging
- Spawn incidents to test specialist assignment
- Manipulate money to test economy features
- Fast-forward time to test progression systems
- Adjust client parameters to test difficulty scaling

### Balancing
- Tweak incident rates via client API
- Adjust reward multipliers in config files
- Hot-reload to test new balance instantly
- Monitor metrics in real-time

### Stress Testing
- Spawn 50-100 incidents at once
- Verify game handles high load
- Monitor performance metrics
- Test automation system under load

## 🔒 Security Note

**⚠️ This backend is for DEVELOPMENT ONLY**

- No authentication/authorization
- Allows arbitrary state manipulation
- Exposes internal game state
- Not suitable for production use

For a production deployment, you would need to add:
- API authentication (JWT tokens, API keys)
- Rate limiting
- Input validation and sanitization
- Role-based access control
- Audit logging

## 🐛 Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Verify Python virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### API returns 503 errors
- Backend started but GameState not initialized
- Check logs for initialization errors
- Verify data files exist in `data/` directory

### Hot-reload not working
- Ensure JSON files are in correct format
- Check file permissions
- Review logs for validation errors

### CORS errors in browser
- Check `CORS_ORIGINS` in configuration
- Verify browser allows localhost connections
- Update CORS settings if accessing from different domain

## 📚 Next Steps

After getting the backend running:

1. **Explore the Admin Dashboard** - Click around, spawn incidents, adjust money
2. **Try the API** - Use cURL or Postman to interact with endpoints
3. **Hot-Reload Configs** - Edit JSON files and reload via API
4. **Build Custom Tools** - Use the API to create your own debugging tools
5. **Integrate with Game** - Enable backend mode in main game loop

## 🤝 Contributing

The backend follows the project's "vibe coding" philosophy:
- All game data lives in JSON files
- Backend provides live manipulation
- Hot-reload everything possible
- Prioritize developer velocity

When adding new endpoints:
1. Create route in appropriate blueprint file
2. Follow existing error handling patterns
3. Return consistent JSON response format
4. Add example to this README
5. Test with `test_backend.py`

## 📄 License

Same as main project.
