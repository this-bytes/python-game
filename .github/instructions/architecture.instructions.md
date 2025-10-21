---
applyTo: "**"
---

# Architecture - Instructions

**This file contains project structure, design patterns, and architectural decisions.**

Reference this when:
- Understanding project organization
- Implementing new systems
- Making architectural decisions
- Understanding plugin system architecture

---

## PROJECT STRUCTURE

```
/src/models/          → Pure game logic (Specialist, Incident, Client, etc.)
/src/core/            → Game systems (generation, assignment, resolution, progression)
/src/ui/              → Pygame rendering ONLY (no game logic)
/backend/             → Flask/FastAPI CRUD API that provides game backend
/src/utils/           → Utility functions and helpers
/src/main.py          → Game entry point and initialization
/src/config.py        → Configuration management
/data/                → JSON configuration files (all game parameters)
/tests/               → Unit tests for all systems
```

**CRITICAL RULE:** Never put game logic in Pygame rendering code. Rendering reads state; it doesn't create it.

---

## STRICT SEPARATION OF CONCERNS

### Pure Game Logic (`/src/models/` and `/src/core/`)
- No knowledge of Pygame, UI, rendering
- No knowledge of HTTP requests or Flask
- Pure Python business logic
- Fully testable without UI
- Deterministic (same input = same output)

```python
# src/models/specialist.py
class Specialist:
    """Pure game logic - no UI dependencies."""
    
    def __init__(self, name: str, specialty: str, level: int = 1):
        self.name = name
        self.specialty = specialty
        self.level = level
        self.xp = 0
    
    def assign_to_incident(self, incident: "Incident") -> bool:
        """Assign incident to specialist if compatible."""
        if self.specialty != incident.specialty_required:
            return False
        if self.current_incident is not None:
            return False
        
        self.current_incident = incident
        return True
    
    def gain_xp(self, xp_amount: int) -> None:
        """Award XP to specialist."""
        self.xp += xp_amount
        
        # Check for level up
        xp_required = 100 * (self.level ** 1.5)
        if self.xp >= xp_required:
            self.level += 1
            self.xp -= int(xp_required)
```

### Pygame Rendering (`/src/ui/`)
- Reads game state, doesn't modify it
- Converts state to visual representation
- Handles user input (mouse clicks, key presses)
- Returns actions (not executing them)

```python
# src/ui/specialist_panel.py
class SpecialistPanel:
    """Pygame rendering - reads state, doesn't modify."""
    
    def render(self, specialist: Specialist, screen: pygame.Surface) -> None:
        """Render specialist panel. NO GAME LOGIC HERE."""
        # Draw background
        pygame.draw.rect(screen, PANEL_COLOR, self.rect)
        
        # Draw specialist info (read-only)
        name_text = self.font.render(specialist.name, True, TEXT_COLOR)
        level_text = self.font.render(f"Level {specialist.level}", True, TEXT_COLOR)
        xp_text = self.font.render(f"XP: {specialist.xp}", True, TEXT_COLOR)
        
        # Blit to screen
        screen.blit(name_text, (10, 10))
        screen.blit(level_text, (10, 30))
        screen.blit(xp_text, (10, 50))
    
    def handle_click(self, pos: tuple[int, int]) -> GameAction | None:
        """Convert mouse click to game action. Don't execute it."""
        if self.rect.collidepoint(pos):
            return AssignIncidentAction(specialist_id=self.specialist_id)
        return None
```

### Backend API (`/backend/`)
- CRUD operations on game state
- Live parameter editing for debugging
- No game logic (calls into `/src/core/`)
- Controls game state via API calls
- Hot-reload configuration

```python
# backend/routes/specialists.py
@app.put("/specialists/<specialist_id>")
def update_specialist(specialist_id: str):
    """Update specialist (for debugging/balancing)."""
    data = request.json
    
    # Get specialist from game state
    specialist = game_state.get_specialist(specialist_id)
    
    # Apply updates
    if "level" in data:
        specialist.level = data["level"]
    if "xp" in data:
        specialist.xp = data["xp"]
    
    logger.info(f"Updated specialist {specialist_id}")
    return {"success": True, "specialist": specialist.to_dict()}
```

---

## PLUGIN SYSTEM ARCHITECTURE (UNIFIED)

**ALL GAME SYSTEMS ARE NOW PLUGINS.** The plugin system is the ONLY system architecture.

- `/src/core/plugins/` → All game systems as GameSystem plugins
- Event-driven communication via singleton EventBus
- Standardized lifecycle: initialize/update/shutdown/save_state/load_state
- Feature flags control optional systems
- SystemManager orchestrates all plugins

**MANDATORY:** All new systems must inherit from GameSystem and be registered in main.py.

### Plugin Architecture Patterns

#### GameSystem Base Class

```python
class GameSystem:
    """Base class for all game systems (plugins)."""
    
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        pass
    
    def initialize(self, game_state) -> None:
        """Initialize plugin with game state."""
        pass
    
    def update(self, game_state, delta_time: float) -> None:
        """Update plugin logic."""
        pass
    
    def shutdown(self, game_state) -> None:
        """Shutdown plugin and cleanup resources."""
        pass
    
    def save_state(self, game_state) -> Dict[str, Any]:
        """Save plugin state for persistence."""
        pass
    
    def load_state(self, game_state, state: Dict[str, Any]) -> None:
        """Load plugin state from persistence.
        
        Args:
            game_state: The current game state object.
            state (Dict[str, Any]): Dictionary containing the plugin's persisted state as returned by save_state.
        """
        pass
```

#### Event-Driven Communication

```python
from src.core.event_bus import EventBus

class IncidentPlugin(GameSystem):
    """Plugin that manages incidents."""
    
    def initialize(self, game_state) -> None:
        """Subscribe to events."""
        EventBus.subscribe("specialist_assigned", self._on_specialist_assigned)
        EventBus.subscribe("incident_resolved", self._on_incident_resolved)
    
    def _on_specialist_assigned(self, event_data: dict) -> None:
        """Handle specialist assignment event."""
        specialist_id = event_data["specialist_id"]
        incident_id = event_data["incident_id"]
        logger.info(f"Incident {incident_id} assigned to {specialist_id}")
    
    def update(self, game_state, delta_time: float) -> None:
        """Generate new incidents if needed."""
        if self._should_generate_incident(game_state):
            incident = self._generate_incident()
            game_state.add_incident(incident)
            
            # Emit event
            EventBus.emit("incident_generated", {
                "incident_id": incident.id,
                "type": incident.type
            })
```

#### Plugin Registration

```python
# src/main.py
from src.core.system_manager import SystemManager
from src.core.plugins.incident_plugin import IncidentPlugin
from src.core.plugins.specialist_plugin import SpecialistPlugin
from src.core.plugins.burnout_plugin import BurnoutPlugin

# Register plugins
system_manager = SystemManager()
system_manager.register_plugin(IncidentPlugin())
system_manager.register_plugin(SpecialistPlugin())
system_manager.register_plugin(BurnoutPlugin())

# Initialize all plugins
system_manager.initialize(game_state)

# Game loop
while running:
    delta_time = clock.tick(60) / 1000.0
    system_manager.update(game_state, delta_time)
```

---

## DATA-DRIVEN DESIGN

**ALL GAME PARAMETERS MUST BE IN JSON FILES.**

Never hardcode game balance values in Python. Everything that affects gameplay must be configurable through JSON files in `/data/`.

### Configuration Structure

```
/data/
  game_config.json              → Core game settings (tick rates, XP curves)
  specialist_templates.json     → Specialist types and starting stats
  incidents.json                → Incident types and parameters
  clients.json                  → Client contracts and payouts
  automation_scripts.json       → Automation parameters
  burnout_config.json           → Burnout thresholds and recovery
```

### Example Configuration

```json
// data/game_config.json
{
  "game_settings": {
    "tick_rate_seconds": 1.0,
    "max_specialists": 10,
    "max_incidents": 20,
    "starting_cash": 10000
  },
  "xp_curve": {
    "base_xp": 100,
    "exponent": 1.5,
    "incident_xp_multiplier": 1.2
  },
  "economy": {
    "specialist_hire_cost": 5000,
    "incident_base_payout": 500,
    "automation_unlock_cost": 10000
  }
}
```

---

## ERROR HANDLING

### Exception Hierarchy

```python
class GameError(Exception):
    """Base exception for all game errors."""
    pass

class SpecialistError(GameError):
    """Base exception for specialist-related errors."""
    pass

class SpecialistNotFoundError(SpecialistError):
    """Specialist not found."""
    pass

class SpecialistUnavailableError(SpecialistError):
    """Specialist is not available for assignment."""
    pass

class IncidentError(GameError):
    """Base exception for incident-related errors."""
    pass

class AssignmentError(GameError):
    """Assignment validation failed."""
    pass

class SpecialtyMismatchError(AssignmentError):
    """Specialist specialty doesn't match incident requirement."""
    pass
```

### Validation

```python
class AssignmentValidator:
    """Validate incident assignments."""
    
    @staticmethod
    def validate_assignment(
        specialist: Specialist,
        incident: Incident
    ) -> None:
        """Validate assignment. Raises specific exceptions if invalid."""
        if specialist.specialty != incident.specialty_required:
            raise SpecialtyMismatchError(
                f"Specialist {specialist.name} ({specialist.specialty}) "
                f"cannot handle {incident.name} ({incident.specialty_required})"
            )
        
        if specialist.current_incident is not None:
            raise SpecialistUnavailableError(
                f"Specialist {specialist.name} is already assigned"
            )
        
        if specialist.level < incident.min_level_required:
            raise AssignmentError(
                f"Specialist level {specialist.level} < required {incident.min_level_required}"
            )
```

---

## CONFIGURATION MANAGEMENT

### Loading Configuration

```python
class GameConfig:
    """Load and manage game configuration."""
    
    @staticmethod
    def load_from_json(config_path: str = "data/game_config.json") -> "GameConfig":
        """Load configuration from JSON file."""
        with open(config_path) as f:
            data = json.load(f)
        
        # Validate schema
        if not GameConfig._validate_schema(data):
            raise ValueError(f"Invalid configuration in {config_path}")
        
        config = GameConfig()
        config.game_settings = data.get("game_settings", {})
        config.xp_curve = data.get("xp_curve", {})
        config.economy = data.get("economy", {})
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
    
    @staticmethod
    def _validate_schema(data: dict) -> bool:
        """Validate configuration schema."""
        required_keys = ["game_settings", "xp_curve", "economy"]
        return all(key in data for key in required_keys)
```

---

## LOGGING ARCHITECTURE

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/game.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage in game logic
logger.debug(f"Checking specialist {specialist_id} availability")
logger.info(f"Incident {incident_id} assigned to {specialist_id}")
logger.warning(f"Specialist {specialist_id} burnout at {burnout}%")
logger.error(f"Failed to load specialist {specialist_id}: {error}")
```

---

## TESTING ARCHITECTURE

Tests should mirror structure:

```
/tests/
  test_specialist.py          → Unit tests for Specialist
  test_incident.py            → Unit tests for Incident
  test_assignment_system.py   → Integration tests
  test_api.py                 → API endpoint tests
  conftest.py                 → Shared fixtures
```

```python
# tests/conftest.py - Shared fixtures
import pytest
from src.models.specialist import Specialist
from src.models.incident import Incident

@pytest.fixture
def game_config():
    """Provide test configuration."""
    return GameConfig.load_from_json("data/game_config.json")

@pytest.fixture
def specialist():
    """Provide test specialist."""
    return Specialist(
        id="test_001",
        name="Test Specialist",
        specialty="Network Security",
        level=1
    )

@pytest.fixture
def incident():
    """Provide test incident."""
    return Incident(
        id="inc_001",
        name="Test DDoS",
        specialty_required="Network Security",
        difficulty=2
    )
```

---

## See Also

- **[copilot-instructions.md](../copilot-instructions.md)** - Main instructions and overview
- **[plugin-system.instructions.md](plugin-system.instructions.md)** - Plugin architecture details
- **[core-standards.instructions.md](core-standards.instructions.md)** - Absolute standards
- **[code-style.instructions.md](code-style.instructions.md)** - Code style and anti-patterns
- **[testing.instructions.md](testing.instructions.md)** - Testing requirements
- **[workflows.instructions.md](workflows.instructions.md)** - Common development tasks
