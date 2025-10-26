# Cybersecurity Firm Idle/Tycoon/RPG Game

A Python-based idle/tycoon/RPG game where you manage a startup cybersecurity firm. Blend strategic resource allocation with automated progression as you build your security empire.

## 🎮 Game Concept

Manage a cybersecurity firm by triaging security incidents, assigning specialized agents, and growing your business. The game combines:

- **🔄 Idle Mechanics**: Continuous incident generation requiring triage
- **💰 Tycoon Mechanics**: Resource allocation and profit optimization  
- **⚡ RPG Mechanics**: Specialist leveling, XP progression, and skill unlocks

## 🏗️ Architecture Philosophy: "Vibe Coding"

This project prioritizes **iteration speed** over perfect architecture:

- **JSON-first design**: ALL game parameters in external files
- **Pygame as renderer only**: Visual dashboard, NOT game logic
- **Hot-reloadable**: Change balance without restarting
- **Backend-driven debugging**: Live manipulation via CRUD API

## 📁 Project Structure

```
/src/
  /models/       → Game entities (Specialist, Incident, Client)
  /core/         → Game systems (generation, assignment, resolution)
  /ui/           → Pygame rendering only
  /utils/        → JSON loading, logging, validation
/backend/        → Flask/FastAPI CRUD API
/data/           → JSON configuration files
/tests/          → Test suite
/docs/           → Documentation
/plan/           → Implementation plans
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip
- Modern web browser (for web UI)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd python-game

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-websockets.txt  # For web UI support
```

### Running the Game

**🌐 Web UI (Recommended)**
```bash
# Start game with embedded web server
python start_web_game.py

# Or manually:
python main.py --local-server --headless

# Then open browser to: http://localhost:8000
```

**Choose Your Interface:**
- 🚀 **Command Center**: Revolutionary desktop-style OS interface with windowing system, persistent HUD, and comprehensive entity management
- 📊 **Classic Interface**: Streamlined single-page view for quick gameplay

**🖥️ Desktop UI (Classic)**
```bash
# Terminal 1: Start the game (shows main menu)
python main.py

# Or with command-line options:
python main.py --continue        # Continue from last save
python main.py --new-game        # Start new game directly
python main.py --tutorial        # Start tutorial mode
python main.py --load-slot 3     # Load from save slot 3
python main.py --debug           # Enable debug mode

# See all options:
python main.py --help
```

### Main Menu

The game features multiple UI modes:

**🌐 Web UI (Modern)**
- Access through browser at http://localhost:8000
- **Command Center**: Revolutionary desktop OS-style interface with:
  - Desktop icons and windowing system
  - Persistent HUD with real-time stats
  - Multi-window workflow
  - Comprehensive entity management
  - Quick actions and detail views
- **Classic Interface**: Single-page streamlined view
- Real-time WebSocket-powered gameplay
- Works on any device with a modern browser
- See [Command Center Guide](docs/COMMAND_CENTER_GUIDE.md) for details

**🖥️ Desktop UI (Classic)**
- Native Pygame-based interface
- Main menu with options to:
  - 🎮 **Start New Game**: Begin a fresh game
  - ▶️ **Continue**: Resume from your last save
  - 📚 **Tutorial**: Learn the game with guided gameplay
  - ⚙️ **Settings**: Configure game options (coming soon)
  - ❌ **Exit**: Close the game

See [docs/MAIN_MENU.md](docs/MAIN_MENU.md) for detailed documentation on startup modes and command-line arguments.

### Backend Admin Dashboard

Access the live debugging dashboard at `http://localhost:5000/admin`

## 🎯 Core Game Loop

1. **Incidents Generate** → Security threats appear based on client contracts
2. **Triage & Assign** → Match specialists to incidents by specialty/difficulty
3. **Resolution** → Specialists resolve incidents, earn XP and rewards
4. **Level Up** → Unlock automation scripts that handle incidents automatically
5. **Scale Up** → Hire more specialists, take on bigger clients, optimize profits

## 🔧 Development

### Running Tests

```bash
pytest
pytest --cov=src tests/  # With coverage
```

### Hot-Reloading Configuration

1. Edit JSON files in `/data/`
2. Trigger reload: `curl -X POST http://localhost:5000/config/reload`
3. Changes reflect immediately in running game

### Adding New Content

- **New Specialist**: Edit `/data/specialists.json`
- **New Incident Type**: Edit `/data/incidents.json`
- **New Client**: Edit `/data/clients.json`
- **New Automation**: Edit `/data/automation_scripts.json`

## 📚 Documentation

- [WebSocket Architecture](docs/WEBSOCKET_ARCHITECTURE.md) - Web UI and real-time communication
- [Implementation Plan](plan/feature-cybersec-idle-game-1.md)
- [Copilot Instructions](.github/copilot-instructions.md)
- [Main Menu Guide](docs/MAIN_MENU.md)
- [Architecture Documentation](docs/architecture.md) *(coming soon)*
- [API Reference](docs/api_reference.md) *(coming soon)*

## 🤝 Contributing

See [Developer Guide](docs/developer_guide.md) for contribution guidelines.

## 📝 License

*(Add your license here)*

## 🎨 Tech Stack

- **Game Engine**: Pygame (desktop UI) / WebSocket + Alpine.js (web UI)
- **Backend**: Flask/FastAPI
- **Data Format**: JSON
- **Testing**: pytest
- **Type Checking**: mypy
- **Web Framework**: Alpine.js (lightweight reactive framework)
- **Real-time Communication**: WebSockets

---

**Status**: 🚧 In Development - Phase 1 (Project Scaffolding)
