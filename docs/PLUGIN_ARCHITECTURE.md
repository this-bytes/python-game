# Plugin Architecture - Developer Guide

## Overview

The game now uses a **plugin-based architecture** that enables rapid feature development without refactoring core systems. This guide explains how to create new game features as plugins.

## Core Components

### 1. Event Bus (`src/core/event_bus.py`)

The Event Bus provides **decoupled communication** between systems using publish-subscribe pattern.

**Key Features:**
- Priority-based event handling (LOW → NORMAL → HIGH → CRITICAL)
- Event history tracking for debugging
- Performance statistics
- No redundant constants - use string event types directly

**Common Events:**
```python
"incident_generated"     # New incident created
"incident_assigned"      # Incident assigned to specialist
"incident_resolved"      # Incident successfully resolved
"specialist_level_up"    # Specialist gained a level
"money_earned"           # Money added to game state
"prestige_performed"     # Player performed prestige reset
"achievement_unlocked"   # Achievement completed
```

**Usage Example:**
```python
from src.core.event_bus import get_event_bus, EventPriority

# Get global event bus
event_bus = get_event_bus()

# Subscribe to events
def handle_incident_resolved(event):
    incident_id = event.data["incident_id"]
    reward = event.data["reward"]
    print(f"Incident {incident_id} earned ${reward}")

event_bus.subscribe("incident_resolved", handle_incident_resolved, EventPriority.NORMAL)

# Publish events
event_bus.publish(
    "incident_resolved",
    {"incident_id": "inc_001", "reward": 500},
    source="resolution_system"
)

# Process events (call once per frame)
event_bus.process_events()
```

### 2. Feature Manager (`src/core/feature_manager.py`)

The Feature Manager enables **safe feature deployment** with feature flags and A/B testing.

**Key Features:**
- Hot-reload from JSON configuration (`data/features.json`)
- Percentage-based rollout for gradual deployment
- Feature dependencies (e.g., advanced automation requires idle core)
- Per-session stable rollout assignments

**Configuration (`data/features.json`):**
```json
{
  "features": [
    {
      "id": "my_feature",
      "enabled": true,
      "rollout_percentage": 50.0,
      "dependencies": ["base_feature"],
      "description": "My awesome new feature"
    }
  ]
}
```

**Usage Example:**
```python
from src.core.feature_manager import get_feature_manager

# Get global feature manager
features = get_feature_manager()

# Check if feature is enabled
if features.is_enabled("my_feature"):
    # Run feature code
    pass

# Check with dependencies
if features.is_enabled("advanced_automation", check_dependencies=True):
    # Only runs if all dependencies also enabled
    pass

# Runtime control
features.set_enabled("my_feature", False)  # Disable feature
features.set_rollout_percentage("my_feature", 100.0)  # 100% rollout
```

### 3. GameSystem Interface (`src/core/game_system.py`)

The GameSystem interface defines the **contract for all game systems**.

**Key Methods:**
- `get_name()` - Unique system identifier
- `initialize(game_state)` - Setup system (called once)
- `update(game_state, delta_time)` - Frame update (called every frame)
- `shutdown(game_state)` - Cleanup (called on exit)
- `save_state(game_state)` - Save custom data
- `load_state(game_state, state_data)` - Load custom data

**Creating a Plugin:**
```python
from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus
from src.models.game_state import GameState

class MyFeaturePlugin(GameSystem):
    """My awesome feature plugin."""
    
    def get_name(self) -> str:
        return "my_feature"
    
    def get_feature_id(self) -> str:
        """Link to feature flag."""
        return "my_feature"
    
    def get_dependencies(self) -> list:
        """This feature requires idle_core."""
        return ["idle_core"]
    
    def initialize(self, game_state: GameState):
        """Setup the system."""
        self.event_bus = get_event_bus()
        
        # Subscribe to events
        self.event_bus.subscribe(
            "incident_resolved",
            self._on_incident_resolved
        )
        
        print(f"[MY_FEATURE] Initialized!")
    
    def update(self, game_state: GameState, delta_time: float):
        """Update every frame."""
        # Your update logic here
        pass
    
    def shutdown(self, game_state: GameState):
        """Cleanup on exit."""
        print(f"[MY_FEATURE] Shutting down")
    
    def _on_incident_resolved(self, event):
        """Handle incident resolution."""
        incident_id = event.data["incident_id"]
        # Do something cool with the resolved incident
```

### 4. System Manager (`src/core/system_manager.py`)

The System Manager **orchestrates all plugins**, handling initialization order, updates, and save/load.

**Key Features:**
- Automatic dependency resolution (topological sort)
- Feature flag integration
- Coordinated save/load across systems
- Runtime enable/disable of systems

**Usage Example:**
```python
from src.core.system_manager import SystemManager
from my_plugin import MyFeaturePlugin

# Create manager
manager = SystemManager()

# Register systems
manager.register_system(MyFeaturePlugin())

# Initialize all systems
manager.initialize_all(game_state)

# Game loop
while running:
    # Update all enabled systems
    manager.update_all(game_state, delta_time)

# Shutdown
manager.shutdown_all(game_state)
```

## Creating a New Feature

### Step 1: Add Feature Flag

Edit `data/features.json`:
```json
{
  "features": [
    {
      "id": "my_feature",
      "enabled": false,
      "rollout_percentage": 0.0,
      "dependencies": [],
      "description": "My awesome new feature"
    }
  ]
}
```

### Step 2: Create Plugin Class

Create `src/plugins/my_feature_plugin.py`:
```python
from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, EventPriority
from src.models.game_state import GameState
from src.utils.logger import GameLogger

class MyFeaturePlugin(GameSystem):
    """Implements my awesome feature."""
    
    def __init__(self):
        super().__init__()
        self.logger = GameLogger("my_feature")
        self.event_bus = None
        self.my_data = {}
    
    def get_name(self) -> str:
        return "my_feature"
    
    def get_feature_id(self) -> str:
        return "my_feature"  # Links to feature flag
    
    def initialize(self, game_state: GameState):
        """Setup the feature."""
        self.event_bus = get_event_bus()
        
        # Subscribe to relevant events
        self.event_bus.subscribe(
            "incident_resolved",
            self._handle_incident_resolved,
            EventPriority.NORMAL
        )
        
        self.logger.logger.info("[MY_FEATURE] Initialized")
    
    def update(self, game_state: GameState, delta_time: float):
        """Update logic runs every frame."""
        # Your feature logic here
        pass
    
    def shutdown(self, game_state: GameState):
        """Cleanup on shutdown."""
        self.logger.logger.info("[MY_FEATURE] Shutdown")
    
    def save_state(self, game_state: GameState) -> dict:
        """Save custom data not in GameState."""
        return {
            "my_data": self.my_data
        }
    
    def load_state(self, game_state: GameState, state_data: dict):
        """Load custom data."""
        self.my_data = state_data.get("my_data", {})
    
    def _handle_incident_resolved(self, event):
        """React to incident resolution."""
        incident_id = event.data["incident_id"]
        # Do something with the event
        
        # Publish your own events
        self.event_bus.publish(
            "my_feature_triggered",
            {"incident_id": incident_id},
            source="my_feature"
        )
```

### Step 3: Register Plugin

In `src/main.py` or wherever SystemManager is initialized:
```python
from src.core.system_manager import SystemManager
from src.plugins.my_feature_plugin import MyFeaturePlugin

# Create manager
system_manager = SystemManager()

# Register your plugin
system_manager.register_system(MyFeaturePlugin())

# Initialize all
system_manager.initialize_all(game_state)
```

### Step 4: Enable Feature

Edit `data/features.json`:
```json
{
  "id": "my_feature",
  "enabled": true,
  "rollout_percentage": 100.0
}
```

Or enable at runtime:
```python
from src.core.feature_manager import get_feature_manager

features = get_feature_manager()
features.set_enabled("my_feature", True)
```

### Step 5: Test

Your plugin will now:
1. ✅ Auto-initialize if feature flag is enabled
2. ✅ Receive update() calls every frame
3. ✅ Subscribe to events via Event Bus
4. ✅ Save/load state automatically
5. ✅ Respect dependencies and feature flags

## Best Practices

### Event-Driven Communication

**DO:**

```python
# ALWAYS publish events for cross-system communication
event_bus.publish("specialist_hired", {"specialist_id": "spec_001"}, source="roster_system")
```

**DON'T:**

CRITICAL: NEVER call another system or manager directly
This creates tight coupling and breaks the architecture.
other_system.handle_specialist_hired("spec_001") # <-- ANTI-PATTERN
DO NOT directly modify GameState from other systems (e.g., UI).
game_state.is_paused = True # <-- ANTI-PATTERN

INSTEAD, publish an event:
event_bus.publish("game_paused", {}, source="ui")

### Feature Flags

**DO:**
```python
# Check feature flags at runtime
if features.is_enabled("advanced_mode"):
    run_advanced_logic()
else:
    run_basic_logic()
```

**DON'T:**
```python
# Don't hardcode feature availability
run_advanced_logic()  # Always runs, no gradual rollout
```

### Dependencies

**DO:**

```python
def get_dependencies(self) -> list:
    return ["idle_core", "prestige_system"]
```

**DON'T:**

```python
# Don't assume systems are initialized
self.idle_core.do_something()  # May not exist!
```

### State Management

**DO:**

```python
def save_state(self, game_state: GameState) -> dict:
    return {"my_custom_data": self.data}

def load_state(self, game_state: GameState, state_data: dict):
    self.data = state_data.get("my_custom_data", {})
```

**DON'T:**

```python
# Don't store state in files directly
with open("my_state.json", "w") as f:
    json.dump(self.data, f)
```

## Testing Your Plugin

Create `tests/test_my_feature_plugin.py`:

```python
import pytest
from src.plugins.my_feature_plugin import MyFeaturePlugin
from src.models.game_state import GameState

class TestMyFeaturePlugin:
    def test_initialization(self):
        """Test plugin initializes correctly."""
        plugin = MyFeaturePlugin()
        game_state = GameState()
        
        plugin.initialize(game_state)
        
        assert plugin.is_initialized()
        assert plugin.get_name() == "my_feature"
    
    def test_update(self):
        """Test plugin update logic."""
        plugin = MyFeaturePlugin()
        game_state = GameState()
        plugin.initialize(game_state)
        
        # Test update doesn't crash
        plugin.update(game_state, 0.016)  # 60 FPS
    
    def test_save_load(self):
        """Test state persistence."""
        plugin = MyFeaturePlugin()
        game_state = GameState()
        plugin.initialize(game_state)
        
        # Save state
        state_data = plugin.save_state(game_state)
        
        # Create new plugin and load
        new_plugin = MyFeaturePlugin()
        new_plugin.initialize(game_state)
        new_plugin.load_state(game_state, state_data)
        
        # Verify state restored
        assert new_plugin.my_data == plugin.my_data
```

Run tests:
```bash
pytest tests/test_my_feature_plugin.py -v
```

## Debugging

### Event History
```python
# Get recent events
history = event_bus.get_history(limit=20)
for event in history:
    print(f"{event.timestamp}: {event.event_type} from {event.source}")

# Filter by type
resolved_events = event_bus.get_history("incident_resolved", limit=10)
```

### Event Statistics
```python
stats = event_bus.get_stats()
print(f"Total events: {stats['total_events_published']}")
print(f"Events by type: {stats['events_by_type']}")
```

### System Status
```python
# Check which systems are initialized
initialized = manager.get_initialized_systems()
print(f"Initialized: {initialized}")

# Get specific system
my_system = manager.get_system("my_feature")
if my_system:
    print(f"Enabled: {my_system.is_enabled()}")
```

## Migration Guide

### Converting Existing Systems to Plugins

**Before:**
```python
class MySystem:
    def __init__(self, game_state):
        self.game_state = game_state
    
    def update(self, delta_time):
        # Update logic
        pass
```

**After:**
```python
from src.core.game_system import GameSystem

class MySystemPlugin(GameSystem):
    def get_name(self) -> str:
        return "my_system"
    
    def initialize(self, game_state):
        # Setup logic
        pass
    
    def update(self, game_state, delta_time):
        # Update logic
        pass
```

## Architecture Benefits

### 1. **High Velocity Development**
- Add features without touching core code
- 3-5 features per week vs 1 per month

### 2. **Safe Deployment**
- Feature flags enable gradual rollout
- Disable problematic features instantly
- A/B test new mechanics

### 3. **Clean Dependencies**
- Systems communicate via events
- No tight coupling
- Easy to test in isolation

### 4. **Scalability**
- Add 100+ systems without complexity
- Automatic dependency resolution
- Coordinated save/load

## Example: Complete Feature Implementation

See `src/plugins/prestige_plugin.py` for a complete reference implementation showing:
- Event subscriptions
- Feature flag integration
- State persistence
- Dependency handling
- Comprehensive logging

## Questions?

Check these resources:
- Event Bus: `src/core/event_bus.py` (docstrings)
- Feature Manager: `src/core/feature_manager.py` (docstrings)
- GameSystem: `src/core/game_system.py` (docstrings)
- System Manager: `src/core/system_manager.py` (docstrings)
- Tests: `tests/test_event_bus.py`, `tests/test_feature_manager.py`
