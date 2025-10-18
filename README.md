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
```

### Running the Game

```bash
# Terminal 1: Start the game (shows main menu)
python src/main.py

# Or with command-line options:
python src/main.py --continue        # Continue from last save
python src/main.py --new-game        # Start new game directly
python src/main.py --tutorial        # Start tutorial mode
python src/main.py --load-slot 3     # Load from save slot 3
python src/main.py --debug           # Enable debug mode

# See all options:
python src/main.py --help

# Terminal 2: Start the backend server (optional but recommended)
cd backend
python app.py
```

### Main Menu

The game now features a main menu with options to:
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

- [Implementation Plan](plan/feature-cybersec-idle-game-1.md)
- [Copilot Instructions](.github/copilot-instructions.md)
- [Architecture Documentation](docs/architecture.md) *(coming soon)*
- [API Reference](docs/api_reference.md) *(coming soon)*

## 🤝 Contributing

See [Developer Guide](docs/developer_guide.md) for contribution guidelines.

## 📝 License

*(Add your license here)*

## 🎨 Tech Stack

- **Game Engine**: Pygame
- **Backend**: Flask/FastAPI
- **Data Format**: JSON
- **Testing**: pytest
- **Type Checking**: mypy

---

**Status**: 🚧 In Development - Phase 1 (Project Scaffolding)
