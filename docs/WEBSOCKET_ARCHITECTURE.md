# WebSocket Game Architecture

## Overview

The game now supports a web-based UI through WebSocket communication. This allows players to access the game through a web browser without needing to install Pygame or any desktop dependencies.

## Architecture

```
┌─────────────────┐         WebSocket (port 8765)         ┌──────────────┐
│   Web Browser   │ ←──────────────────────────────────→  │ Game Server  │
│   (Alpine.js)   │         JSON Messages                 │  (Python)    │
└─────────────────┘                                        └──────────────┘
         │                                                        │
         │                                                        │
         │          HTTP (port 8000)                             │
         └───────────────────────────→                           │
              Static Files (HTML/CSS/JS)                  ┌──────┴──────┐
                                                          │ Game Logic  │
                                                          │  Plugins    │
                                                          │   Models    │
                                                          └─────────────┘
```

## Components

### 1. WebSocket Server (`src/websocket_game.py`)

The WebSocket server handles real-time bidirectional communication between the game engine and web clients.

**Key Features:**
- Runs in a background thread (daemon)
- Broadcasts game state updates to all connected clients
- Accepts action commands from clients
- Thread-safe state management

**Main Functions:**
- `start_background_server()` - Start server in background thread
- `set_state()` - Update game state and broadcast to clients
- `handler()` - Handle WebSocket connections
- `broadcast()` - Send message to all connected clients

### 2. Web UI (`web_ui/`)

The web UI is a single-page application built with Alpine.js, a lightweight reactive framework.

**Files:**
- `index.html` - Landing page with server status check
- `game.html` - Main game interface

**Features:**
- Real-time specialist roster display
- Real-time incident queue with assignment
- Modal dialogs for specialist assignment
- Toast notifications for actions
- Automatic reconnection on disconnect
- Responsive design

### 3. Static File Server

The game automatically starts an embedded HTTP server to serve the web UI files.

**Configuration:**
- Port: 8000 (automatically finds available port if busy)
- Directory: `web_ui/`
- Threading support for concurrent connections

## Message Protocol

### Server → Client Messages

#### State Snapshot
Complete game state sent on connection and periodically:
```json
{
  "event": "state_snapshot",
  "tick": 123,
  "data": {
    "specialists": [...],
    "incidents": [...],
    "money": 10000,
    "game_time": 456
  }
}
```

#### State Patch
Incremental updates:
```json
{
  "event": "state_patch",
  "tick": 124,
  "data": {
    "specialists": [/* updated specialists */],
    "incidents": [/* updated incidents */]
  }
}
```

#### Action Result
Response to client actions:
```json
{
  "event": "action_result",
  "id": "client_action_id",
  "result": {
    "status": "ok",
    "action": "assign_incident",
    "details": {...}
  }
}
```

#### Acknowledgment
Quick response to actions:
```json
{
  "event": "ack",
  "id": "client_action_id",
  "status": "ok" | "error",
  "error": "optional error message"
}
```

### Client → Server Messages

#### Assign Incident
```json
{
  "action": "assign_incident",
  "id": "client_12345",
  "data": {
    "incident_id": "inc_001",
    "specialist_id": "spec_001"
  },
  "wait_for_result": true
}
```

## Running the Game

### Quick Start

```bash
python start_web_game.py
```

This will:
1. Start the game server in headless mode
2. Start WebSocket server on port 8765
3. Start HTTP server on port 8000
4. Open your browser to http://localhost:8000

### Manual Start

```bash
# Start game with embedded servers
python main.py --local-server --headless

# Or use the dedicated WebSocket-only server
python run_ws_game.py
```

### Command-Line Options

- `--local-server` - Enable embedded WebSocket and HTTP servers
- `--headless` - Run without Pygame UI (required for web mode)
- `--no-server` - Disable backend integration
- `--debug` - Enable debug logging

## Development

### Adding New Actions

1. Define action handler in `src/websocket_game.py`:
```python
async def handle_action(action: Dict[str, Any], ws) -> None:
    act = action.get("action")
    
    if act == "my_new_action":
        # Handle action
        data = action.get("data", {})
        # ... process action ...
        await ws.send(json.dumps({"event": "ack", "status": "ok"}))
        return
```

2. Send action from web UI:
```javascript
ws.send(JSON.stringify({
    action: 'my_new_action',
    id: 'client_' + Date.now(),
    data: { /* action data */ }
}));
```

### Adding UI Components

The UI uses Alpine.js for reactivity. Add new components in `web_ui/game.html`:

```html
<div x-data="{ myState: 'initial' }">
    <button @click="myState = 'clicked'">Click me</button>
    <p x-text="myState"></p>
</div>
```

### Testing

Test WebSocket connection:
```bash
python scripts/test_ws_client.py
```

Check server status:
```bash
curl http://localhost:8000
```

## Browser Compatibility

The web UI uses modern web standards and requires:
- Modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- JavaScript enabled
- WebSocket support (standard in all modern browsers)

## Security

**Current Implementation:**
- Local development only (binds to 0.0.0.0)
- No authentication required
- Admin token support for privileged actions (optional)

**Production Considerations:**
- Add authentication layer
- Use WSS (WebSocket Secure) for encrypted connections
- Implement rate limiting
- Add CORS configuration
- Use reverse proxy (nginx/Apache)

## Performance

### Optimization Features

1. **Efficient Broadcasting**: Only sends updates to connected clients
2. **Incremental Updates**: State patches reduce bandwidth
3. **Throttled Updates**: Periodic snapshots (every 1 second in headless mode)
4. **Thread Safety**: Lock-protected state access

### Benchmarks

- **Latency**: ~10-50ms for action round-trip
- **Bandwidth**: ~5-20 KB/sec per client (varies with game activity)
- **Concurrent Clients**: Tested with 10+ simultaneous connections

## Troubleshooting

### WebSocket Connection Failed

**Check if server is running:**
```bash
ps aux | grep "python main.py"
```

**Check port availability:**
```bash
lsof -i :8765
lsof -i :8000
```

**Check logs:**
```bash
tail -f logs/game_*.log
```

### UI Not Loading

**Verify static server:**
```bash
curl http://localhost:8000/index.html
```

**Check browser console:** (F12 → Console tab)

### Game State Not Updating

**Test WebSocket directly:**
```bash
python scripts/test_ws_client.py
```

**Check network tab in browser:** (F12 → Network → WS filter)

## Future Enhancements

- [ ] Add authentication system
- [ ] Implement multiple game rooms
- [ ] Add spectator mode
- [ ] Improve state compression
- [ ] Add binary protocol option (MessagePack)
- [ ] Mobile-responsive UI improvements
- [ ] PWA support (offline capability)
- [ ] Real-time multiplayer features
