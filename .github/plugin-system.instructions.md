# Plugin System Architecture - Instructions

**This file contains the complete plugin system architecture documentation.**

Reference this when:
- Creating new game systems
- Converting existing systems to plugins
- Understanding event-driven communication
- Implementing plugin lifecycle methods

---

## Plugin System Architecture (UNIFIED)

**ALL GAME SYSTEMS ARE NOW PLUGINS.** The plugin system is the ONLY system architecture.

- `/src/core/plugins/` → All game systems as GameSystem plugins
- Event-driven communication via singleton EventBus
- Standardized lifecycle: initialize/update/shutdown/save_state/load_state
- Feature flags control optional systems
- SystemManager orchestrates all plugins

**MANDATORY:** All new systems must inherit from GameSystem and be registered in main.py.

---

## Registered Plugins

**ALL SYSTEMS CONVERTED TO PLUGINS:**

1. **IdlePlugin** (`idle_plugin.py`)
   - Idle mechanics and passive progression
   - Time-based resource generation
   - Offline progress simulation

2. **PrestigeSystem** (`prestige_plugin.py`)
   - Prestige progression and resets
   - Prestige point calculation
   - Prestige upgrade management

3. **AchievementSystem** (`achievement_plugin.py`)
   - Achievement tracking and unlocking
   - Progress monitoring
   - Reward distribution

4. **BurnoutPlugin** (`burnout_plugin.py`)
   - Specialist burnout tracking
   - Performance degradation mechanics
   - Recovery actions (rest, vacation, therapy)

5. **RelationshipsPlugin** (`relationships_plugin.py`)
   - Team relationship dynamics
   - Friendship and rivalry mechanics
   - Team synergy calculations

6. **DopaminePlugin** (`dopamine_plugin.py`)
   - Addictive gameplay mechanics
   - Combo tracking and rewards
   - Risk/reward contracts

7. **EquipmentPlugin** (`equipment_plugin.py`)
   - Equipment drops on incident completion
   - Inventory management
   - Stat bonus calculations

8. **AbilityPlugin** (`ability_plugin.py`)
   - Ability activation and cooldowns
   - Active effect tracking
   - Level-based ability unlocking

9. **PassiveIncomePlugin** (`passive_income_plugin.py`)
   - Retainer income from contracts
   - Investment management
   - Reputation-based income bonuses

10. **FacilityPlugin** (`facility_plugin.py`)
    - Facility upgrade management
    - Aggregate bonus calculations
    - Facility effect application

---

## GameSystem Base Class

Every plugin must inherit from `GameSystem` and implement these methods:

```python
from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from typing import Dict, Any, List

class MyPlugin(GameSystem):
    """Plugin description."""

    def __init__(self):
        """Initialize plugin."""
        super().__init__()
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "MyPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "my_feature"

    def initialize(self, game_state) -> None:
        """Initialize plugin with game state.
        
        Subscribe to events, load configuration, set up initial state.
        """
        self._subscription_ids = [
            self._event_bus.subscribe("event_name", self._on_event),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update plugin logic.
        
        Called every frame with time elapsed since last update.
        """
        pass

    def shutdown(self, game_state) -> None:
        """Shutdown plugin and cleanup resources.
        
        Unsubscribe from events, save state if needed.
        """
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save plugin state for persistence.
        
        Returns:
            Dictionary containing state data to save
        """
        return {
            "plugin_data": "value",
        }

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load plugin state from saved data.
        
        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        pass

    def _on_event(self, event: Event) -> None:
        """Handle subscribed event."""
        pass
```

---

## Event-Driven Communication

All plugins communicate through the singleton EventBus.

### Publishing Events

```python
from src.core.event_bus import get_event_bus

event_bus = get_event_bus()
event_bus.publish("event_name", {
    "key": "value",
    "data": data,
})
```

### Subscribing to Events

```python
# In initialize()
self._subscription_ids = [
    self._event_bus.subscribe("incident_completed", self._on_incident_completed),
    self._event_bus.subscribe("specialist_leveled_up", self._on_specialist_leveled_up),
]

def _on_incident_completed(self, event: Event) -> None:
    """Handle incident completion event."""
    incident_id = event.data.get("incident_id")
    specialist_id = event.data.get("specialist_id")
    # Process event...
```

### Unsubscribing from Events

```python
# In shutdown()
for subscription_id in self._subscription_ids:
    self._event_bus.unsubscribe(subscription_id)
self._subscription_ids.clear()
```

---

## Common Event Types

**Game Flow Events:**
- `game_started` - Game initialization complete
- `game_paused` - Game paused
- `game_resumed` - Game resumed
- `game_saved` - Game state saved
- `game_loaded` - Game state loaded

**Incident Events:**
- `incident_generated` - New incident created
- `incident_assigned` - Incident assigned to specialist
- `incident_completed` - Incident resolved
- `incident_failed` - Incident failed

**Specialist Events:**
- `specialist_hired` - New specialist added
- `specialist_leveled_up` - Specialist gained level
- `specialist_assigned` - Specialist assigned to incident
- `specialist_available` - Specialist completed assignment

**System-Specific Events:**
- `burnout_updated` - Specialist burnout changed
- `relationship_changed` - Specialist relationship updated
- `equipment_dropped` - Equipment item dropped
- `ability_activated` - Ability used
- `achievement_unlocked` - Achievement earned

---

## Plugin Registration

Register plugins in `src/main.py` during initialization:

```python
from src.core.system_manager import SystemManager
from src.core.plugins.my_plugin import MyPlugin

# In Game.initialize()
self.system_manager = SystemManager()
self.system_manager.register_system(MyPlugin())
self.system_manager.initialize_all(self.game_state)
```

---

## Feature Flags

Control plugin activation via feature flags in `/data/features.json`:

```json
{
  "features": [
    {
      "id": "my_feature",
      "name": "My Feature",
      "enabled": true,
      "description": "Enable my plugin",
      "rollout_percentage": 100
    }
  ]
}
```

Check feature status in plugin:

```python
def get_feature_id(self) -> str:
    """Get feature flag ID."""
    return "my_feature"  # Must match features.json
```

---

## State Persistence

Plugins must implement save_state/load_state for persistence:

```python
def save_state(self, game_state) -> Dict[str, Any]:
    """Save plugin state."""
    return {
        "statistics": self._statistics,
        "active_effects": [effect.to_dict() for effect in self._active_effects],
        "last_update_time": self._last_update_time,
    }

def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
    """Load plugin state."""
    self._statistics = state_data.get("statistics", {})
    self._active_effects = [
        Effect.from_dict(e) for e in state_data.get("active_effects", [])
    ]
    self._last_update_time = state_data.get("last_update_time", 0.0)
```

---

## Testing Plugins

Every plugin must have comprehensive tests:

```python
import pytest
from src.core.plugins.my_plugin import MyPlugin
from src.models.game_state import GameState

class TestMyPlugin:
    """Test suite for MyPlugin."""

    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return MyPlugin()

    @pytest.fixture
    def game_state(self):
        """Create test game state."""
        return GameState()

    def test_initialization(self, plugin, game_state):
        """Test plugin initializes correctly."""
        plugin.initialize(game_state)
        assert plugin.get_name() == "MyPlugin"

    def test_event_handling(self, plugin, game_state):
        """Test plugin handles events correctly."""
        plugin.initialize(game_state)
        # Trigger event and verify handling
        # ...
```

---

## Plugin Development Checklist

Before submitting a new plugin:

- [ ] Inherits from GameSystem
- [ ] Implements all required methods (get_name, get_feature_id, initialize, update, shutdown, save_state, load_state)
- [ ] Uses event bus for communication (no direct system coupling)
- [ ] Properly subscribes and unsubscribes from events
- [ ] Implements state persistence
- [ ] Has comprehensive test coverage (>80%)
- [ ] Registered in main.py SystemManager
- [ ] Feature flag configured in features.json
- [ ] Documentation includes plugin purpose and events
- [ ] No magic numbers (all configuration in JSON)
- [ ] Type hints on all methods
- [ ] Docstrings explain WHY, not just WHAT

---

## Common Patterns

### Time-Based Updates

```python
def update(self, game_state, delta_time: float) -> None:
    """Update plugin with time-based logic."""
    current_time = getattr(game_state, 'game_time', 0.0)
    
    if not hasattr(self, '_last_update'):
        self._last_update = current_time
    
    elapsed = current_time - self._last_update
    
    if elapsed >= 60.0:  # Update every 60 seconds
        self._perform_update(game_state)
        self._last_update = current_time
```

### Wrapping Existing Systems

```python
from src.core.existing_system import ExistingSystem

class ExistingSystemPlugin(GameSystem):
    """Plugin wrapper for ExistingSystem."""

    def __init__(self):
        super().__init__()
        self._system = None

    def initialize(self, game_state) -> None:
        """Initialize wrapped system."""
        game_config = getattr(game_state, 'config', {})
        self._system = ExistingSystem(game_config)
        # Subscribe to events...

    # Expose public API
    def public_method(self, *args, **kwargs):
        """Delegate to wrapped system."""
        if self._system:
            return self._system.public_method(*args, **kwargs)
```

### Conditional Updates

```python
def update(self, game_state, delta_time: float) -> None:
    """Update only if feature is active."""
    if not self._is_feature_enabled(game_state):
        return
    
    # Perform update logic...
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall project architecture
- [CODE_STYLE.md](CODE_STYLE.md) - Code style requirements
- [TESTING_STANDARDS.md](TESTING_STANDARDS.md) - Testing requirements
- [copilot-instructions.md](copilot-instructions.md) - Main instructions
