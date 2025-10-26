# UI Directory

This directory contains all web-based user interfaces for the Cybersecurity Firm game.

## Structure

```
ui/
├── game/          # Main game web UI (player-facing)
│   ├── index.html # Landing page with server status check
│   └── game.html  # Main game interface (Alpine.js)
│
└── admin/         # Admin/control panel UI (development/debugging)
    ├── admin.html           # Admin dashboard
    ├── control-panel.html   # Control panel interface
    └── [supporting files]   # CSS, JS for admin interfaces
```

## Game UI (`ui/game/`)

The main player-facing web interface built with Alpine.js.

**Access**: http://localhost:8000 (when running with `--local-server`)

**Features**:
- Real-time game state via WebSocket
- Specialist roster management
- Incident queue and assignment
- Client satisfaction tracking
- Statistics dashboard

**Tech Stack**:
- Alpine.js 3.x (lightweight reactive framework)
- WebSocket for real-time communication
- Responsive CSS design

**Documentation**: See `docs/WEB_UI_USER_GUIDE.md`

## Admin UI (`ui/admin/`)

Developer/admin interfaces for debugging and game state manipulation.

**Access**: Served by backend on port 5001 (when backend is running)

**Features**:
- Live game state inspection
- Entity editing (specialists, incidents, clients)
- Batch operations
- Configuration hot-reload
- Real-time event monitoring

**Tech Stack**:
- Vanilla JavaScript
- REST API integration
- WebSocket for live updates

**Documentation**: See `backend/README.md` and `ui/admin/CONTROL_PANEL_README.md`

## Development

### Running Game UI

```bash
# Start game with embedded web server
python start_web_game.py

# Or manually
python main.py --local-server --headless
```

Opens browser to http://localhost:8000

### Running Admin UI

```bash
# Terminal 1: Start game
python main.py

# Terminal 2: Start backend
cd backend
python run_backend.py
```

Access admin panel at http://localhost:5001/admin

## File Organization

**Game UI** (`ui/game/`):
- Player-facing interfaces
- Production-ready for deployment
- Minimal dependencies (Alpine.js from CDN)
- Self-contained HTML files

**Admin UI** (`ui/admin/`):
- Development/debugging tools
- Backend-dependent (requires API server)
- Advanced features for developers
- Not intended for production deployment

## Adding New UI Components

### Game UI
Add components in `ui/game/game.html` using Alpine.js:
```html
<div x-data="{ count: 0 }">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

### Admin UI
Add new panels in `ui/admin/control-panel.html` or create new admin pages as needed.

## Backend Integration

The backend serves admin UI files from this directory:
```python
# backend/app.py
static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'admin')
```

## See Also

- `docs/WEBSOCKET_ARCHITECTURE.md` - Game UI architecture
- `docs/WEB_UI_USER_GUIDE.md` - Player guide
- `backend/README.md` - Backend API documentation
