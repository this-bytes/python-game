# Standalone Mode Documentation

**Version**: 1.0.0  
**Last Updated**: 2025-10-19

---

## Overview

The game supports three backend modes:

1. **No Backend** (Default) - Pure standalone, no admin panel
2. **Local Server** - Embedded backend in separate thread, enables admin panel
3. **Remote Server** - Connect to remote backend instance

All modes maintain feature parity - the game functions identically regardless of backend configuration.

---

## Command-Line Flags

### Backend Mode Selection

```bash
# No backend (default) - Pure standalone mode
python src/main.py

# Local embedded server - Starts backend in background thread
python src/main.py --local-server

# Remote server - Connect to existing backend instance
python src/main.py --remote-host 192.168.1.100

# Disable backend explicitly (same as default)
python src/main.py --no-server
```

### Backend Configuration

```bash
# Custom port (default: 5001)
python src/main.py --local-server --server-port 8080

# Admin authentication token
python src/main.py --local-server --admin-token "secret-token-123"

# Remote server with custom port
python src/main.py --remote-host game.example.com --server-port 9000
```

### Combined with Game Modes

```bash
# Local server + continue game
python src/main.py --local-server --continue

# Remote server + new game
python src/main.py --remote-host 192.168.1.100 --new-game

# Local server + debug mode
python src/main.py --local-server --debug

# Local server + headless (for testing)
python src/main.py --local-server --headless
```

---

## Backend Modes Comparison

| Feature | No Backend | Local Server | Remote Server |
|---------|-----------|--------------|---------------|
| **Game Functionality** | ✅ Full | ✅ Full | ✅ Full |
| **Save/Load** | ✅ Local files | ✅ Local files | ✅ Server files |
| **Admin Panel** | ❌ Not available | ✅ http://localhost:5001/control-panel | ✅ http://HOST:PORT/control-panel |
| **God Mode** | ❌ Not available | ✅ Available | ✅ Available (with token) |
| **Hot Config Reload** | ❌ Requires restart | ✅ Available | ✅ Available |
| **Real-time State View** | ❌ Not available | ✅ WebSocket updates | ✅ WebSocket updates |
| **Network Latency** | N/A | ~0ms (same process) | Variable (network dependent) |
| **Security Concerns** | None | Localhost only | Requires auth token |
| **Resource Usage** | Minimal | +Flask thread | Same as no backend |
| **Multiplayer Potential** | No | No | ✅ Yes (future) |

---

## Local Server Mode

### How It Works

```
┌────────────────────────────────────────┐
│         Main Process                    │
│  ┌──────────────┐  ┌─────────────────┐│
│  │              │  │                  ││
│  │  Game Loop   │  │  Backend Server ││
│  │  (Pygame UI) │  │  (Flask Thread) ││
│  │              │  │                  ││
│  └──────┬───────┘  └────────┬────────┘│
│         │                    │         │
│         └────────WebSocket───┘         │
└────────────────────────────────────────┘
```

### Starting Local Server

```python
# Automatic via CLI flag
python src/main.py --local-server

# Programmatic
from src.utils.game_args import GameArgs
args = GameArgs(local_server=True)
```

The local server:
- Runs in a separate daemon thread
- Starts during game initialization
- Binds to `localhost:5001` by default
- Terminates when game exits

### Accessing Admin Panel

Once local server starts, access at:
- **Control Panel**: http://localhost:5001/control-panel
- **API Base**: http://localhost:5001/api
- **Health Check**: http://localhost:5001/health

### Local Server Logs

```
[LOCAL_SERVER] Starting embedded backend server on port 5001...
[LOCAL_SERVER] Server thread running on port 5001
[LOCAL_SERVER] ✅ Embedded backend server started successfully
[LOCAL_SERVER] 🌐 Admin panel: http://localhost:5001/control-panel
[LOCAL_SERVER] 📡 API base: http://localhost:5001/api
```

---

## Remote Server Mode

### Use Cases

- **Development Team** - Central game instance for testing
- **Multiplayer Testing** - Multiple clients, one server
- **Live Operations** - Remote admin control of game servers
- **Web Client** - Browser-based UI connecting to game backend

### Setting Up Remote Server

#### 1. Start Backend Server (Separate Process)

```bash
cd backend
python run_backend.py --port 5001 --host 0.0.0.0
```

#### 2. Connect Game Client

```bash
# From another machine or same machine
python src/main.py --remote-host 192.168.1.100 --server-port 5001
```

### Security Considerations

**⚠️ IMPORTANT**: Remote server exposes game control endpoints

1. **Use Admin Tokens**
   ```bash
   python src/main.py --remote-host HOST --admin-token "secure-token-here"
   ```

2. **Firewall Configuration**
   - Only expose port to trusted network
   - Use VPN or SSH tunnel for internet access

3. **HTTPS Recommended** (for production)
   - Configure TLS certificates
   - Use reverse proxy (nginx/Apache)

### Network Requirements

- **Latency**: <100ms recommended for good experience
- **Bandwidth**: Minimal (~10KB/s for WebSocket events)
- **Ports**: 5001 (or custom) must be accessible
- **Protocols**: HTTP + WebSocket

---

## No Backend Mode (Default)

### Characteristics

- **Simplest Mode**: Just run the game, no additional setup
- **Fully Functional**: All gameplay features work
- **No Admin Tools**: Cannot use god mode or admin panel
- **Local Save Files**: Saves stored in `saves/` directory
- **Minimal Resources**: No Flask server overhead

### When to Use

- **Normal Gameplay**: Players just want to play
- **Offline Play**: No network required
- **Privacy**: No network communication
- **Production Builds**: Distributed to players

### Starting No Backend Mode

```bash
# Explicit
python src/main.py --no-server

# Implicit (default)
python src/main.py
```

---

## Feature Parity Matrix

All backend modes support identical gameplay features:

| Feature | Implementation Notes |
|---------|---------------------|
| **Incident Assignment** | Direct GameState calls (no backend) or via action endpoint |
| **Specialist Management** | Local or via API |
| **Save/Load** | Local SaveManager or via `/api/save`, `/api/load` |
| **Equipment System** | Local or via action endpoint |
| **Ability System** | Local or via action endpoint |
| **Prestige System** | Local or via action endpoint |
| **Achievement System** | Local plugin or backend plugin |
| **Burnout System** | Local plugin or backend plugin |
| **Relationships System** | Local plugin or backend plugin |

### Differences (Admin Features Only)

Features **only available with backend**:

- God mode commands (add money, spawn incidents, modify specialists)
- Hot config reload (without restarting game)
- Real-time state inspection via admin panel
- WebSocket event monitoring
- Analytics dashboard
- Multi-client state synchronization (future)

---

## Troubleshooting

### Local Server Won't Start

**Problem**: `[LOCAL_SERVER] Server failed to start within timeout`

**Solutions**:
1. Check if port 5001 is already in use:
   ```bash
   lsof -i :5001
   # or on Windows:
   netstat -ano | findstr :5001
   ```
2. Use different port:
   ```bash
   python src/main.py --local-server --server-port 8080
   ```
3. Check firewall blocking localhost connections

### Can't Connect to Remote Server

**Problem**: Connection timeout or refused

**Solutions**:
1. Verify server is running:
   ```bash
   curl http://HOST:PORT/health
   ```
2. Check firewall rules on server
3. Verify network connectivity:
   ```bash
   ping HOST
   ```
4. Confirm port is correct

### WebSocket Disconnects

**Problem**: Frequent WebSocket disconnections

**Solutions**:
1. Check network stability
2. Increase reconnection attempts in `net_client.py`
3. Use wired connection instead of WiFi
4. Check server logs for errors

### Admin Panel Shows 503 Error

**Problem**: Backend returns "Game state not initialized"

**Solutions**:
1. Ensure game is running with backend enabled
2. Wait for game initialization to complete
3. Refresh admin panel page
4. Check backend logs for errors

---

## Performance Considerations

### Local Server Mode

- **CPU**: +5-10% overhead for Flask thread
- **Memory**: +50MB for Flask/SocketIO
- **Startup**: +0.5-1 second for server initialization
- **No FPS Impact**: Backend runs in separate thread

### Remote Server Mode

- **Network Latency**: Actions require round-trip to server
- **UI Responsiveness**: Maintain local state cache to prevent lag
- **Bandwidth**: ~10KB/s for typical gameplay
- **Packet Loss**: Auto-reconnect and state resync

### Optimization Tips

1. **Reduce Snapshot Frequency**
   - Default: 2 seconds
   - Can increase to 5 seconds for lower bandwidth

2. **Use Incremental Updates**
   - Backend can send deltas instead of full state
   - Reduces WebSocket traffic

3. **Local State Cache**
   - UI maintains read-only cache
   - Reduces API calls for rendering

---

## Development Guidelines

### Adding New Actions

When adding new player actions:

1. Define action in `data/ws_protocol.json`
2. Implement handler in `backend/routes/actions.py`
3. Add action type to `src/ui/net_client.py` (if needed)
4. Update this documentation

### Testing All Modes

```bash
# Test no backend mode
pytest tests/test_no_backend_mode.py

# Test local server mode
pytest tests/test_local_server_mode.py

# Test remote server mode
pytest tests/test_remote_server_mode.py

# Test mode parity
pytest tests/test_backend_mode_parity.py
```

---

## Migration Guide

### Existing Code → Backend-Aware

**Before (Direct GameState access)**:
```python
# In UI code
game_state.assign_incident_to_specialist(incident_id, specialist_id)
```

**After (Action-based)**:
```python
# In UI code
result = net_client.submit_action('assign_incident', {
    'incident_id': incident_id,
    'specialist_id': specialist_id
})
if result.success:
    # Action succeeded
else:
    # Show error to user
    print(result.error['message'])
```

---

## See Also

- **[WS_PROTOCOL.md](./WS_PROTOCOL.md)** - Complete protocol specification
- **[RENDERING_AUDIT.md](./RENDERING_AUDIT.md)** - UI/logic separation audit
- **[BACKEND_SPECIFICATION.md](./BACKEND_SPECIFICATION.md)** - Backend API reference

---

**Last Review**: 2025-10-19  
**Next Review**: After Phase D implementation
