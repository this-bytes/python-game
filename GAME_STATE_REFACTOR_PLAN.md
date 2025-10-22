# Game State Management Refactor Plan

## Executive Summary

**Current State**: GameState is a 1051-line monolithic class mixing entity storage, business logic, system coordination, and serialization. UI and plugins directly access internal state, creating tight coupling and maintenance issues.

**Target State**: Clean layered architecture with clear separation of concerns, safe state access patterns, and proper change notification system.

**Benefits**: Better maintainability, testability, UI/plugin decoupling, and architectural clarity.

---

## Current Architecture Problems

### 1. Monolithic GameState Class

- **Issue**: 1051 lines handling too many responsibilities
- **Impact**: Hard to understand, test, and maintain
- **Evidence**: Single class managing entities, systems, logic, and serialization

### 2. Mixed Concerns

- **Issue**: Entity storage, business logic, and system coordination all mixed together
- **Impact**: Changes in one area affect others, unclear boundaries
- **Evidence**: `update()` handles time mechanics, `assign_incident_to_specialist()` contains business logic

### 3. Tight UI/Plugin Coupling

- **Issue**: UI directly accesses `game_state.specialists`, `game_state.incidents`
- **Impact**: UI knows internal structure, can't refactor without breaking UI
- **Evidence**: UI components directly modify game state without validation

### 4. Inconsistent State Access

- **Issue**: Some state via properties, some via direct attributes
- **Impact**: Unclear API, inconsistent access patterns
- **Evidence**: `config` property vs direct `specialists` attribute access

### 5. Complex Serialization

- **Issue**: Massive `to_dict()`/`from_dict()` methods with error-prone logic
- **Impact**: Save/load bugs, hard to maintain, missing state on saves
- **Evidence**: 100+ line methods with hasattr() checks and try/except blocks

### 6. No Change Notification

- **Issue**: UI doesn't know when state changes
- **Impact**: UI can't react to state updates, stale data display
- **Evidence**: No observer pattern or event system for state changes

---

## Proposed Layered Architecture

### Layer 1: StateManager (Data Layer)
**Responsibility**: Pure entity storage and basic CRUD operations

```python
class StateManager:
    """Manages all game entity collections and basic operations."""

    def __init__(self):
        self._specialists: List[Specialist] = []
        self._incidents: List[Incident] = []
        self._clients: List[Client] = []
        self._contracts: List[Contract] = []
        self._facilities: List[Facility] = []

    # CRUD operations
    def add_specialist(self, specialist: Specialist) -> None:
        self._specialists.append(specialist)

    def get_specialist(self, specialist_id: str) -> Optional[Specialist]:
        return next((s for s in self._specialists if s.id == specialist_id), None)

    def remove_specialist(self, specialist_id: str) -> bool:
        # Implementation

    # Bulk operations
    def get_all_specialists(self) -> List[Specialist]:
        return self._specialists.copy()

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        return {
            "specialists": [s.to_dict() for s in self._specialists],
            "incidents": [i.to_dict() for i in self._incidents],
            # ... all entities
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self._specialists = [Specialist.from_dict(s) for s in data.get("specialists", [])]
        # ... load all entities
```

### Layer 2: GameLogic (Business Logic Layer)
**Responsibility**: Business rules, game mechanics, validation

```python
class GameLogic:
    """Handles all business logic and game rules."""

    def __init__(self, state_manager: StateManager, config: Dict[str, Any]):
        self._state = state_manager
        self._config = config

    def can_assign_incident(self, specialist: Specialist, incident: Incident) -> bool:
        """Business rule: Can this specialist be assigned to this incident?"""
        if specialist.specialty != incident.specialty_required:
            return False
        if specialist.current_incident is not None:
            return False
        return True

    def assign_incident_to_specialist(self, specialist_id: str, incident_id: str) -> bool:
        """Business logic for incident assignment."""
        specialist = self._state.get_specialist(specialist_id)
        incident = self._state.get_incident(incident_id)

        if not self.can_assign_incident(specialist, incident):
            return False

        specialist.assign_incident(incident)
        return True

    def calculate_xp_reward(self, incident: Incident, specialist: Specialist) -> int:
        """Business logic for XP calculation."""
        base_xp = incident.base_xp_reward
        specialty_bonus = 1.5 if specialist.specialty == incident.specialty_required else 1.0
        return int(base_xp * specialty_bonus)
```

### Layer 3: SystemCoordinator (System Management Layer)
**Responsibility**: Coordinates internal systems and time-based updates

```python
class SystemCoordinator:
    """Manages all internal game systems."""

    def __init__(self, state_manager: StateManager, game_logic: GameLogic):
        self._state = state_manager
        self._logic = game_logic

        # Initialize systems
        self._incident_generator = IncidentGenerator()
        self._automation_processor = AutomationProcessor()
        self._dopamine_system = DopamineSystem()

    def update(self, delta_time: float) -> None:
        """Update all systems."""
        self._incident_generator.update(self._state, delta_time)
        self._automation_processor.update(self._state, delta_time)
        self._dopamine_system.update(delta_time)

    def generate_incidents(self) -> List[Incident]:
        """Generate new incidents."""
        return self._incident_generator.generate_incidents(self._state)

    def process_automation(self) -> List[GameAction]:
        """Process automation scripts."""
        return self._automation_processor.process_scripts(self._state)
```

### Layer 4: GameState (Facade Layer)
**Responsibility**: Public API and coordination between layers

```python
class GameState:
    """Main game state facade with clean public API."""

    def __init__(self):
        self._state_manager = StateManager()
        self._game_logic = GameLogic(self._state_manager, self._config)
        self._system_coordinator = SystemCoordinator(self._state_manager, self._game_logic)

        # Observers for state change notifications
        self._observers: List[Callable] = []

    # Public API - delegates to appropriate layer
    def assign_incident_to_specialist(self, specialist_id: str, incident_id: str) -> bool:
        """Assign incident to specialist (delegates to GameLogic)."""
        result = self._game_logic.assign_incident_to_specialist(specialist_id, incident_id)
        if result:
            self._notify_observers("incident_assigned", {
                "specialist_id": specialist_id,
                "incident_id": incident_id
            })
        return result

    def update(self, delta_time: float) -> None:
        """Update game state (delegates to SystemCoordinator)."""
        self._system_coordinator.update(delta_time)

    # State access - safe read-only access
    def get_specialists(self) -> List[Specialist]:
        """Get all specialists (read-only)."""
        return self._state_manager.get_all_specialists()

    def get_specialist(self, specialist_id: str) -> Optional[Specialist]:
        """Get specific specialist."""
        return self._state_manager.get_specialist(specialist_id)

    # Observer pattern for UI updates
    def add_observer(self, callback: Callable) -> None:
        """Add observer for state change notifications."""
        self._observers.append(callback)

    def _notify_observers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of state changes."""
        for observer in self._observers:
            observer(event_type, data)
```

---

## State Access Patterns

### For UI Components (Read-Only Access)

```python
class SpecialistPanel(UIComponent):
    """UI component that displays specialists."""

    def update(self, game_state: GameState) -> None:
        """Update UI with current specialist data."""
        specialists = game_state.get_specialists()  # Safe read-only access

        for specialist in specialists:
            # Display specialist info
            self._update_specialist_display(specialist)

    def handle_click(self, pos: tuple[int, int], game_state: GameState) -> Optional[GameAction]:
        """Handle user interaction."""
        # UI can request actions, but not directly modify state
        specialist = self._get_specialist_at_position(pos)
        if specialist and specialist.is_available:
            return AssignIncidentAction(specialist.id, self._selected_incident_id)
        return None
```

### For Plugins (Validated Mutations)

```python
class IncidentPlugin(GameSystem):
    """Plugin that manages incidents."""

    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update incident logic."""
        # Read state safely
        active_incidents = game_state.get_active_incidents()

        # Request validated actions through game state
        for incident in active_incidents:
            if incident.is_overdue():
                game_state.resolve_incident(incident.id, "timeout")
```

### For Game Logic (Internal Mutations)

```python
# Internal game logic can mutate state directly through layers
def resolve_incident(self, incident_id: str, resolution_type: str) -> None:
    """Resolve an incident."""
    incident = self._state_manager.get_incident(incident_id)

    if resolution_type == "success":
        reward = self._game_logic.calculate_reward(incident)
        self._state_manager.add_money(reward)
        self._notify_observers("incident_resolved", {"incident_id": incident_id, "reward": reward})
    elif resolution_type == "timeout":
        penalty = self._game_logic.calculate_penalty(incident)
        self._state_manager.subtract_money(penalty)
        self._notify_observers("incident_failed", {"incident_id": incident_id, "penalty": penalty})

    # Remove incident from state
    self._state_manager.remove_incident(incident_id)
```

---

## Change Notification System

### Observer Pattern Implementation

```python
from typing import Callable, Dict, Any, List

class StateChangeNotifier:
    """Handles state change notifications to observers."""

    def __init__(self):
        self._observers: List[Callable] = []

    def add_observer(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add observer callback."""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable) -> None:
        """Remove observer callback."""
        self._observers.remove(callback)

    def notify_state_change(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of state change."""
        for observer in self._observers:
            try:
                observer(event_type, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

# Usage in GameState
class GameState:
    def __init__(self):
        self._notifier = StateChangeNotifier()

    def add_state_observer(self, callback: Callable) -> None:
        """Add observer for state changes."""
        self._notifier.add_observer(callback)

    def _notify_state_change(self, event_type: str, data: Dict[str, Any]) -> None:
        """Internal method to notify state changes."""
        self._notifier.notify_state_change(event_type, data)
```

### UI Integration with Notifications

```python
class GameUI:
    """Main UI coordinator."""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.game_state.add_state_observer(self._on_state_change)

        # UI components
        self.specialist_panel = SpecialistPanel()
        self.incident_queue = IncidentQueue()

    def _on_state_change(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle state change notifications."""
        if event_type == "incident_assigned":
            specialist_id = data["specialist_id"]
            incident_id = data["incident_id"]
            self._update_assignment_display(specialist_id, incident_id)

        elif event_type == "incident_resolved":
            incident_id = data["incident_id"]
            reward = data["reward"]
            self._show_resolution_feedback(incident_id, reward)

        elif event_type == "specialist_hired":
            specialist = self.game_state.get_specialist(data["specialist_id"])
            self.specialist_panel.add_specialist(specialist)
```

---

## Serialization Strategy

### Clean Entity Serialization

```python
class StateManager:
    """Handles entity serialization cleanly."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all entities."""
        return {
            "specialists": [s.to_dict() for s in self._specialists],
            "incidents": [i.to_dict() for i in self._incidents],
            "clients": [c.to_dict() for c in self._clients],
            "contracts": [c.to_dict() for c in self._contracts],
            "facilities": [f.to_dict() for f in self._facilities],
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize all entities."""
        self._specialists = [Specialist.from_dict(s) for s in data.get("specialists", [])]
        self._incidents = [Incident.from_dict(i) for i in data.get("incidents", [])]
        self._clients = [Client.from_dict(c) for c in data.get("clients", [])]
        self._contracts = [Contract.from_dict(c) for c in data.get("contracts", [])]
        self._facilities = [Facility.from_dict(f) for f in data.get("facilities", [])]
```

### GameState Serialization (Metadata Only)

```python
class GameState:
    """GameState serializes metadata, delegates entity serialization."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize game state."""
        return {
            # Entity data (delegated to StateManager)
            **self._state_manager.to_dict(),

            # Game metadata
            "game_start_time": self.game_start_time,
            "current_time": self.current_time,
            "game_speed_multiplier": self.game_speed_multiplier,
            "is_paused": self.is_paused,
            "current_money": self.current_money,
            "total_money_earned": self.total_money_earned,

            # System state
            "last_save_time": self.last_save_time,
            "prestige_points": self.prestige_points,
            "prestige_upgrades": self.prestige_upgrades,
            "unlocked_achievements": self.unlocked_achievements,

            # Configuration
            "max_active_incidents": self.max_active_incidents,
            "max_specialists": self.max_specialists,
            "incident_generation_enabled": self.incident_generation_enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Deserialize game state."""
        instance = cls.__new__(cls)

        # Initialize layers
        instance._state_manager = StateManager()
        instance._game_logic = GameLogic(instance._state_manager, instance._config)
        instance._system_coordinator = SystemCoordinator(instance._state_manager, instance._game_logic)
        instance._notifier = StateChangeNotifier()

        # Load entity data
        instance._state_manager.from_dict(data)

        # Load metadata
        instance.game_start_time = data.get("game_start_time", time.time())
        instance.current_time = data.get("current_time", time.time())
        instance.game_speed_multiplier = data.get("game_speed_multiplier", 1.0)
        instance.is_paused = data.get("is_paused", False)
        instance.current_money = data.get("current_money", 5000.0)
        # ... load all metadata

        return instance
```

---

## Migration Strategy

### Phase 1: Extract StateManager (Low Risk)
1. Create `StateManager` class
2. Move entity collections and basic CRUD operations
3. Update GameState to use StateManager internally
4. Test serialization still works

### Phase 2: Extract GameLogic (Medium Risk)
1. Create `GameLogic` class
2. Move business logic methods to GameLogic
3. Update GameState to delegate to GameLogic
4. Update tests to use new API

### Phase 3: Extract SystemCoordinator (Medium Risk)
1. Create `SystemCoordinator` class
2. Move internal systems management
3. Update GameState update() method
4. Test time-based mechanics still work

### Phase 4: Add Change Notifications (Low Risk)
1. Add observer pattern to GameState
2. Update key methods to notify observers
3. Update UI to use notifications
4. Test UI updates correctly

### Phase 5: Clean Public API (Low Risk)
1. Review public methods on GameState
2. Ensure consistent naming and patterns
3. Add comprehensive docstrings
4. Update all callers

---

## Testing Strategy

### Unit Tests for Each Layer

```python
# Test StateManager
def test_state_manager_add_specialist():
    manager = StateManager()
    specialist = create_test_specialist()

    manager.add_specialist(specialist)
    assert len(manager.get_all_specialists()) == 1

# Test GameLogic
def test_game_logic_assignment_validation():
    state_manager = StateManager()
    logic = GameLogic(state_manager, {})

    specialist = create_specialist(specialty="Network")
    incident = create_incident(specialty_required="Network")

    assert logic.can_assign_incident(specialist, incident)

# Test SystemCoordinator
def test_system_coordinator_update():
    state_manager = StateManager()
    logic = GameLogic(state_manager, {})
    coordinator = SystemCoordinator(state_manager, logic)

    coordinator.update(1.0)  # Should not crash
```

### Integration Tests

```python
def test_game_state_full_lifecycle():
    """Test complete game state lifecycle."""
    game_state = GameState()

    # Add entities
    specialist = create_specialist()
    game_state.hire_specialist(specialist)

    incident = create_incident()
    game_state.add_incident(incident)

    # Perform actions
    game_state.assign_incident_to_specialist(specialist.id, incident.id)

    # Update state
    game_state.update(60.0)  # 1 minute

    # Verify state
    assert len(game_state.get_specialists()) == 1
    assert len(game_state.get_incidents()) == 0  # Should be resolved

    # Test serialization
    data = game_state.to_dict()
    loaded_state = GameState.from_dict(data)

    assert len(loaded_state.get_specialists()) == 1
```

---

## Benefits of New Architecture

### 1. Clear Separation of Concerns
- **StateManager**: Data storage only
- **GameLogic**: Business rules only
- **SystemCoordinator**: System management only
- **GameState**: Public API only

### 2. Better Testability
- Each layer can be tested in isolation
- Mock dependencies easily
- Unit tests for business logic
- Integration tests for full workflows

### 3. UI/Plugin Decoupling
- UI uses observer pattern for updates
- Plugins use command pattern for mutations
- State access is read-only for UI
- Changes go through validated APIs

### 4. Easier Maintenance
- Changes in one layer don't affect others
- Clear boundaries prevent coupling
- Easier to add new features
- Easier to refactor internals

### 5. Better Serialization
- Entity serialization separated from metadata
- Each layer handles its own serialization
- Less error-prone save/load logic
- Easier to add new serializable state

---

## Implementation Priority

1. **StateManager** - Foundation, low risk
2. **GameLogic** - Business rules, medium risk
3. **SystemCoordinator** - System management, medium risk
4. **Change Notifications** - UI decoupling, low risk
5. **Clean Public API** - Final polish, low risk

---

## Success Criteria

- [ ] GameState class reduced from 1051 to ~200 lines
- [ ] Clear layer separation (State, Logic, Systems, API)
- [ ] UI uses observer pattern for state updates
- [ ] Plugins use command pattern for state mutations
- [ ] Serialization works correctly for all state
- [ ] All existing functionality preserved
- [ ] Comprehensive test coverage for all layers
- [ ] No breaking changes to external APIs