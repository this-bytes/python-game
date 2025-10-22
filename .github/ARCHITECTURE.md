# ARCHITECTURE & PROJECT STRUCTURE

Reference: See [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) for core standards.

---

## PROJECT STRUCTURE

```
/src/models/          → Pure game logic (Specialist, Incident, Client, etc.)
/src/core/            → Game systems (generation, assignment, resolution, progression)
/src/ui/              → Pygame rendering ONLY (no game logic)
/backend/             → Flask/FastAPI CRUD API for live debugging
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
    
    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load plugin state from saved data."""
        pass
```

#### Event-Driven Communication

```python
# In plugin initialization
self._event_bus = get_event_bus()
self._subscription_ids = [
    self._event_bus.subscribe("incident_completed", self._on_incident_completed),
    self._event_bus.subscribe("specialist_leveled_up", self._on_specialist_leveled_up),
]

# In plugin shutdown
for subscription_id in self._subscription_ids:
    self._event_bus.unsubscribe(subscription_id)
```

### Registered Plugins

**ALL SYSTEMS CONVERTED TO PLUGINS:**
- **IdlePlugin** (idle mechanics)
- **PrestigeSystem** (prestige progression)
- **AchievementSystem** (achievement tracking)
- **BurnoutPlugin** (specialist burnout)
- **RelationshipsPlugin** (team relationships)
- **DopaminePlugin** (addictive mechanics)
- **EquipmentPlugin** (equipment system)
- **AbilityPlugin** (ability activation)
- **PassiveIncomePlugin** (passive income)
- **FacilityPlugin** (facility upgrades)

---

## DATA-DRIVEN EVERYTHING

All game parameters live in JSON, not hardcoded in Python.

### Specialists Configuration (`/data/specialists.json`)
```json
{
  "specialists": [
    {
      "id": "spec_001",
      "name": "Alice Chen",
      "specialty": "Network Security",
      "level": 5,
      "xp": 2340,
      "stats": {
        "speed": 85,
        "accuracy": 90,
        "experience_bonus": 1.2
      }
    }
  ]
}
```

### Incident Types (`/data/incidents.json`)
```json
{
  "incident_types": [
    {
      "id": "inc_type_001",
      "name": "DDoS Attack",
      "specialty_required": "Network Security",
      "difficulty_range": [1, 5],
      "base_sla_seconds": 300,
      "base_reward": 500,
      "xp_reward": 100
    }
  ]
}
```

### Game Configuration (`/data/game_config.json`)
```json
{
  "game_settings": {
    "starting_specialists": 2,
    "starting_money": 5000,
    "time_scale": 1.0,
    "max_active_incidents": 50
  },
  "xp_curve": {
    "base_xp": 100,
    "exponent": 1.5,
    "level_cap": 20
  },
  "economy": {
    "sla_failure_penalty_multiplier": 0.5,
    "perfect_completion_bonus": 1.2,
    "specialist_hiring_cost_base": 2000
  }
}
```

---

## DESIGN PATTERNS

### Event-Driven Architecture (via Global EventBus)

**CRITICAL:** All cross-system communication **MUST** use the global EventBus singleton.
This ensures systems are decoupled and can be added, removed, or feature-flagged
without breaking other systems.

- **Source:** `src/core/event_bus.py`
- **Access:** `get_event_bus()`

**DO NOT** use direct method calls between systems.
**DO NOT** use any other observer pattern (like one on GameState). The EventBus is the *only* way.

```python
from src.core.event_bus import get_event_bus, EventPriority, Event

# --- System A (e.g., Resolution System) ---

class ResolutionSystem(GameSystem):
    def __init__(self):
        self.event_bus = get_event_bus()

    def complete_incident(self, incident: Incident, specialist: Specialist) -> None:
        reward = self.calculate_reward(incident, specialist)
        
        # Publish an event to notify all other systems
        self.event_bus.publish(
            "incident_resolved",
            {
                "incident_id": incident.id,
                "specialist_id": specialist.id,
                "reward": reward
            },
            source="resolution_system"
        )

# --- System B (e.g., UI or Achievement System) ---

class AchievementSystem(GameSystem):
    def initialize(self, game_state):
        self.event_bus = get_event_bus()
        self.event_bus.subscribe(
            "incident_resolved", 
            self.on_incident_resolved,
            EventPriority.NORMAL
        )
    
    def on_incident_resolved(self, event: "Event"):
        """Listen for events from other systems."""
        reward = event.data["reward"]
        self.check_for_high_roller_achievement(reward)
```

### Factory Pattern for Entity Creation

```python
class SpecialistFactory:
    """Create Specialist instances from JSON data."""
    
    @staticmethod
    def create_from_json(specialist_data: dict, game_config: GameConfig) -> Specialist:
        """Create Specialist instance from JSON data."""
        specialist = Specialist(
            id=specialist_data['id'],
            name=specialist_data['name'],
            specialty=specialist_data['specialty'],
            level=specialist_data.get('level', 1),
            xp=specialist_data.get('xp', 0)
        )
        
        # Load stats from JSON
        if 'stats' in specialist_data:
            specialist.speed = specialist_data['stats'].get('speed', 100)
            specialist.accuracy = specialist_data['stats'].get('accuracy', 100)
            specialist.xp_bonus = specialist_data['stats'].get('experience_bonus', 1.0)
        
        return specialist
```

### Strategy Pattern for Different Behaviors

```python
class IncidentResolutionStrategy(ABC):
    """Base strategy for resolving incidents."""
    
    @abstractmethod
    def resolve(self, incident: Incident, specialist: Specialist) -> float:
        """Resolve incident, return time taken."""
        pass

class StandardResolution(IncidentResolutionStrategy):
    """Standard resolution with synergy bonus."""
    
    def resolve(self, incident: Incident, specialist: Specialist) -> float:
        if specialist.specialty == incident.specialty_required:
            multiplier = 1.5  # Synergy bonus
        else:
            multiplier = 1.0
        
        return incident.base_time / multiplier

class QuickFixResolution(IncidentResolutionStrategy):
    """Quick fix with lower accuracy."""
    
    def resolve(self, incident: Incident, specialist: Specialist) -> float:
        return incident.base_time * 0.5  # 50% faster
```

---

## ERROR HANDLING ARCHITECTURE

### Custom Exceptions

```python
# src/core/exceptions.py
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

- [ABSOLUTE_STANDARDS.md](ABSOLUTE_STANDARDS.md) - Core standards
- [CODE_STYLE.md](CODE_STYLE.md) - Naming and formatting
- [TESTING_STANDARDS.md](TESTING_STANDARDS.md) - Testing requirements
