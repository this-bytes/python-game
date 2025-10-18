# Backend-Game Integration Guide

This document explains how the backend control panel integrates with the running Pygame game to provide real-time control and manipulation.

## Architecture Overview

The integration uses a **command queue system** to communicate between the backend (Flask server) and the game (Pygame application):

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Control Panel  │         │  Backend Server  │         │   Pygame Game    │
│   (Browser UI)   │ ◄────► │   (Flask API)    │ ◄────► │  (Game Client)   │
└──────────────────┘         └──────────────────┘         └──────────────────┘
       HTTP                      Command Queue                 HTTP Polling
     Requests                    & State Sync                  & Commands
```

### Key Components

1. **Backend Server** (`backend/app.py`)
   - Flask API server that hosts the control panel UI
   - Maintains a command queue for game commands
   - Receives state updates from the game

2. **Game Integration Routes** (`backend/routes/game_integration.py`)
   - `/api/game/register` - Game announces it's ready for control
   - `/api/game/commands` - Game polls for pending commands
   - `/api/game/state-update` - Game pushes its current state
   - `/api/game/command` - Control panel queues commands

3. **Backend Integration Client** (`src/utils/backend_integration.py`)
   - Runs in the game process
   - Connects to backend on game startup
   - Polls for commands every second
   - Executes commands on the game state
   - Pushes state updates to backend

## How It Works

### 1. Game Startup with Backend Integration

When you start the game, it automatically tries to connect to the backend:

```python
# In src/main.py
self.backend_integration = initialize_backend_integration(logger=self.logger)
backend_connected = connect_to_backend(self.game_state)
```

The backend integration:
1. Checks if backend is running (`GET /health`)
2. Registers with backend (`POST /api/game/register`)
3. Starts a background thread that:
   - Polls for commands every 1 second
   - Executes commands on the game state
   - Pushes state updates to backend

### 2. Control Panel Issues Commands

When you click a button in the control panel (e.g., "Set Money to $1M"):

1. Browser sends HTTP request to backend: `POST /api/godmode/set-money`
2. Backend queues command: `POST /api/game/command` with `{type: 'set_money', params: {amount: 1000000}}`
3. Command sits in queue waiting for game

### 3. Game Executes Commands

In the game's background thread:

1. Polls backend: `GET /api/game/commands`
2. Receives pending commands
3. Executes each command on the game state:
   ```python
   if cmd_type == 'set_money':
       game_state.current_money = amount
   ```
4. Command takes effect immediately in the running game

### 4. State Synchronization

The game continuously pushes its state to the backend:

```python
state_data = {
    'current_money': game_state.current_money,
    'active_incidents': len([i for i in game_state.incidents if i.status == 'active']),
    'total_specialists': len(game_state.specialists)
}
requests.post('/api/game/state-update', json=state_data)
```

The control panel can then display live game metrics.

## Supported Commands

The integration supports the following commands:

| Command | Description | Parameters |
|---------|-------------|------------|
| `set_money` | Set money to exact amount | `amount`: Number |
| `spawn_incident` | Spawn a single incident | None |
| `complete_all_incidents` | Complete all active incidents | None |
| `level_up_specialists` | Level up all specialists | `levels`: Number (default 1) |
| `reload_config` | Reload JSON configuration files | None |

### Adding New Commands

To add a new command:

1. **Add command handler in `src/utils/backend_integration.py`**:
   ```python
   elif cmd_type == 'my_new_command':
       # Execute command on game_state
       self.logger.logger.info(f"[BACKEND_INTEGRATION] Executed my_new_command")
   ```

2. **Add API endpoint in `backend/routes/godmode.py` or create new route**:
   ```python
   @bp.route('/godmode/my-command', methods=['POST'])
   def my_command():
       http_requests.post(
           'http://localhost:5001/api/game/command',
           json={'type': 'my_new_command', 'params': {}},
           timeout=2
       )
       return jsonify({"success": True})
   ```

3. **Add UI button in control panel** (`backend/static/control-panel.js`)

## Running Modes

### Integrated Mode (Recommended)

**Terminal 1 - Backend:**
```bash
python backend/run_backend.py
```

**Terminal 2 - Game:**
```bash
python src/main.py
```

When the game starts, it will automatically connect to the backend. You'll see:
```
[BACKEND_INTEGRATION] Connected to backend server
[BACKEND_INTEGRATION] ✅ Game registered with backend control panel
[BACKEND_INTEGRATION] 🌐 Control panel: http://localhost:5001/control-panel
```

Now open http://localhost:5001/control-panel and you can control the running game!

### Standalone Mode (Testing Only)

For testing the control panel without a game:
```bash
python backend/run_backend.py --standalone
```

This creates a separate GameState in the backend. **Commands will not affect a running game.**

## Integration Flow Diagram

```
User clicks "Set Money" in Control Panel
                ↓
        POST /api/godmode/set-money
                ↓
    Backend queues command in memory
                ↓
    Game polls: GET /api/game/commands
                ↓
    Game receives {type: 'set_money', params: {amount: 1000000}}
                ↓
    Game executes: game_state.current_money = 1000000
                ↓
    Game pushes update: POST /api/game/state-update
                ↓
    Control Panel sees updated money in real-time
```

## Debugging Integration

### Check if Backend is Running
```bash
curl http://localhost:5001/health
```

Should return:
```json
{
  "status": "healthy",
  "game_state_loaded": false
}
```

### Check if Game is Connected
```bash
curl http://localhost:5001/api/game/status
```

Should return:
```json
{
  "success": true,
  "game_connected": true,
  "latest_state": { ... },
  "pending_commands": 0
}
```

### View Game Logs

In the game terminal, you'll see:
```
[BACKEND_INTEGRATION] Polling for commands...
[BACKEND_INTEGRATION] Received command: set_money
[BACKEND_INTEGRATION] Money set to $1000000
```

### Common Issues

**"Failed to connect to backend"**
- Make sure backend is running on port 5001
- Check firewall settings
- Verify backend/config.py has correct HOST and PORT

**"Commands not executing"**
- Check game logs for errors in command execution
- Verify command type matches in both backend and game
- Check that game's background thread is running

**"State not updating in control panel"**
- Check browser console for WebSocket/polling errors
- Verify game is pushing state updates
- Check network tab in browser dev tools

## Performance Considerations

- **Polling Interval**: Game polls for commands every 1 second (configurable in `BackendIntegration.sync_interval`)
- **State Push Rate**: Game pushes state updates every 1 second
- **Command Queue**: Unlimited size (consider adding max size if needed)
- **Thread Safety**: All operations are thread-safe using locks

## Security Notes

⚠️ **This integration is for DEVELOPMENT ONLY**

- No authentication
- Commands can modify game state arbitrarily
- Backend must run on localhost
- Do not expose port 5001 to the internet

For production, you would need:
- API key authentication
- Rate limiting
- Command validation
- Encrypted communication (HTTPS)
- Role-based permissions

## Future Enhancements

Planned improvements:

1. **WebSocket Support**: Replace polling with WebSocket for instant command delivery
2. **Undo System**: Track and reverse commands
3. **Command History**: Log all executed commands
4. **State Snapshots**: Save/restore game state at any point
5. **Remote Control**: Secure remote access for team members
6. **Multi-Game Support**: Control multiple game instances

## API Reference

### Game Registration
```
POST /api/game/register
```
Registers game client with backend.

### Get Pending Commands
```
GET /api/game/commands
```
Returns: `{ success: true, commands: [...], count: N }`

### Queue Command
```
POST /api/game/command
Body: { type: "command_type", params: {...} }
```
Returns: `{ success: true, message: "Command queued" }`

### Push State Update
```
POST /api/game/state-update
Body: { current_money: 5000, active_incidents: 10, ... }
```
Returns: `{ success: true }`

### Get Game Status
```
GET /api/game/status
```
Returns: `{ success: true, game_connected: true, latest_state: {...} }`

## Code Examples

### Execute Custom Command from Python

```python
import requests

# Queue a custom command
requests.post('http://localhost:5001/api/game/command', json={
    'type': 'set_money',
    'params': {'amount': 999999}
})
```

### Check Game Connection Status

```python
import requests

response = requests.get('http://localhost:5001/api/game/status')
data = response.json()

if data['game_connected']:
    print("Game is connected!")
    print(f"Money: ${data['latest_state']['current_money']}")
else:
    print("No game connected")
```

### Monitor Live Game State

```python
import requests
import time

while True:
    response = requests.get('http://localhost:5001/api/game/status')
    state = response.json()['latest_state']
    
    print(f"Money: ${state.get('current_money', 0):.2f}")
    print(f"Incidents: {state.get('active_incidents', 0)}")
    
    time.sleep(1)
```

## Conclusion

The backend-game integration provides a powerful real-time control system that makes debugging, testing, and balancing your game much easier. By using a command queue architecture, we achieve loose coupling between the backend and game while maintaining real-time responsiveness.

For questions or issues, check the game logs and backend logs for detailed error messages.
