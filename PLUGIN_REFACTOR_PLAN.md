# Plugin System 100% Refactor - Execution Plan

## Objective
Convert ALL systems to use the modern GameSystem API from `game_system.py`, eliminating the old `plugin_system.py` entirely. Make the plugin system the ONLY system architecture.

## Modern API Requirements

### From Old API → New API

**Old (plugin_system.py):**
```python
from src.core.plugin_system import GameSystem

class MySystem(GameSystem):
    def __init__(self, event_bus):
        super().__init__(event_bus, "my_system")
    
    def initialize(self) -> None:
        self.event_bus.subscribe("event", self.handler)
    
    def update(self, dt: float) -> None:
        pass
    
    def shutdown(self) -> None:
        self.event_bus.unsubscribe("event", self.handler)
    
    def get_state(self) -> Dict:
        return {}
    
    def set_state(self, state: Dict) -> None:
        pass
```

**New (game_system.py):**
```python
from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus
from src.models.game_state import GameState
from typing import Dict, Any, Optional, List

class MySystem(GameSystem):
    def __init__(self):
        super().__init__()
        self._event_bus = None
        self._subscription_ids: List[str] = []
    
    def get_name(self) -> str:
        return "my_system"
    
    def get_feature_id(self) -> Optional[str]:
        return "my_system"  # or None for always-enabled
    
    def initialize(self, game_state: GameState) -> None:
        self._event_bus = get_event_bus()
        sub_id = self._event_bus.subscribe("event", self.handler)
        self._subscription_ids.append(sub_id)
    
    def update(self, game_state: GameState, delta_time: float) -> None:
        pass
    
    def shutdown(self, game_state: GameState) -> None:
        if self._event_bus:
            for sub_id in self._subscription_ids:
                self._event_bus.unsubscribe(sub_id)
            self._subscription_ids.clear()
    
    def save_state(self, game_state: GameState) -> Dict[str, Any]:
        return {}
    
    def load_state(self, game_state: GameState, state_data: Dict[str, Any]) -> None:
        pass
```

### Key Changes
1. **Constructor**: Remove `event_bus` parameter, call `super().__init__()` with no args
2. **Add methods**: `get_name()`, `get_feature_id()`
3. **Update signatures**: All lifecycle methods take `game_state: GameState` parameter
4. **Event bus access**: Use `get_event_bus()` singleton instead of injected instance
5. **Event bus API**: Use `publish()` not `emit()`, store subscription IDs for unsubscribe
6. **Rename methods**: `get_state()` → `save_state()`, `set_state()` → `load_state()`
7. **Event handlers**: Accept `event` object, access data via `event.data` not direct dict

## Systems to Convert

### Already Converted ✅
- [x] IdlePlugin (src/core/plugins/idle_plugin.py) - DONE
- [x] PrestigePlugin (src/core/plugins/prestige_plugin.py) - DONE in this session

### Need Conversion 🔄

#### 1. AchievementPlugin
**File**: `src/core/plugins/achievement_plugin.py`
**Status**: Uses old API
**Complexity**: High (many event subscriptions)

#### 2. BurnoutSystem → BurnoutPlugin
**File**: `src/core/burnout_system.py` → move to `src/core/plugins/burnout_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Medium

#### 3. RelationshipsSystem → RelationshipsPlugin
**File**: `src/core/relationships_system.py` → move to `src/core/plugins/relationships_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Medium

#### 4. DopamineSystem → DopaminePlugin
**File**: `src/core/dopamine_system.py` → move to `src/core/plugins/dopamine_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Low

#### 5. EquipmentSystem → EquipmentPlugin
**File**: `src/core/equipment_system.py` → move to `src/core/plugins/equipment_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Medium

#### 6. AbilitySystem → AbilityPlugin
**File**: `src/core/ability_system.py` → move to `src/core/plugins/ability_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Low

#### 7. PassiveIncomeSystem → PassiveIncomePlugin
**File**: `src/core/passive_income_system.py` → move to `src/core/plugins/passive_income_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Low

#### 8. FacilitySystem → FacilityPlugin
**File**: `src/core/facility_system.py` → move to `src/core/plugins/facility_plugin.py`
**Status**: Not yet a plugin
**Complexity**: Medium

## Registration in main.py

After conversion, ALL plugins must be registered in `src/main.py`:

```python
from src.core.system_manager import SystemManager
from src.core.plugins.idle_plugin import IdlePlugin
from src.core.plugins.prestige_plugin import PrestigeSystem
from src.core.plugins.achievement_plugin import AchievementSystem
from src.core.plugins.burnout_plugin import BurnoutPlugin
from src.core.plugins.relationships_plugin import RelationshipsPlugin
from src.core.plugins.dopamine_plugin import DopaminePlugin
from src.core.plugins.equipment_plugin import EquipmentPlugin
from src.core.plugins.ability_plugin import AbilityPlugin
from src.core.plugins.passive_income_plugin import PassiveIncomePlugin
from src.core.plugins.facility_plugin import FacilityPlugin

# In Game.__init__:
self.system_manager: Optional[SystemManager] = None

# In Game.initialize:
self.system_manager = SystemManager()

# Register ALL plugins
self.system_manager.register_system(IdlePlugin())
self.system_manager.register_system(PrestigeSystem())
self.system_manager.register_system(AchievementSystem())
self.system_manager.register_system(BurnoutPlugin())
self.system_manager.register_system(RelationshipsPlugin())
self.system_manager.register_system(DopaminePlugin())
self.system_manager.register_system(EquipmentPlugin())
self.system_manager.register_system(AbilityPlugin())
self.system_manager.register_system(PassiveIncomePlugin())
self.system_manager.register_system(FacilityPlugin())

# Initialize all
self.system_manager.initialize_all(self.game_state)

# In Game.run (game loop):
if self.system_manager:
    self.system_manager.update_all(self.game_state, delta_time)

# In Game.shutdown:
if self.system_manager:
    self.system_manager.shutdown_all(self.game_state)
```

## Deprecation Strategy

### plugin_system.py
**Action**: Add deprecation warning at top:

```python
"""DEPRECATED - Use game_system.py instead.

This module contains the OLD plugin system API and should not be used for new code.
All systems should inherit from src.core.game_system.GameSystem instead.

Migration Guide:
1. Change import: from src.core.game_system import GameSystem
2. Update constructor: Remove event_bus parameter
3. Add methods: get_name(), get_feature_id()
4. Update signatures: All methods take game_state parameter
5. Use event bus singleton: get_event_bus()
6. Store subscription IDs for proper cleanup
7. Rename: get_state() → save_state(), set_state() → load_state()

See PLUGIN_REFACTOR_PLAN.md for detailed migration instructions.
"""
```

## Documentation Updates

### 1. ARCHITECTURE.md
**Changes**:
- Remove all references to old plugin_system.py
- Document plugin-only architecture
- Explain SystemManager lifecycle
- Show plugin creation template
- Document event-driven communication

### 2. copilot-instructions.md
**Changes**:
- Update "Project Fundamentals" section
- Change plugin references to modern API
- Add plugin creation checklist
- Update separation of concerns to emphasize plugins
- Remove references to standalone systems

### 3. COMMON_TASKS.md
**Changes**:
- Add "Create a New Plugin" task with step-by-step
- Update all system-related tasks to reference plugins
- Add plugin debugging/testing guide

### 4. TESTING_STANDARDS.md
**Changes**:
- Add plugin testing patterns
- Show how to test lifecycle methods
- Document event bus mocking

## Testing Strategy

All 413 tests must pass after refactor:
1. Run tests after each plugin conversion
2. Verify no regressions
3. Check for proper cleanup (no memory leaks)
4. Validate event subscriptions

## Success Criteria

- [ ] All systems converted to GameSystem plugins
- [ ] All plugins registered in main.py
- [ ] Old plugin_system.py marked as deprecated
- [ ] All documentation updated
- [ ] copilot-instructions.md reflects new architecture
- [ ] All 413 tests passing
- [ ] No references to old API in active code
- [ ] Plugin creation guide in documentation

## Timeline Estimate

- AchievementPlugin conversion: 30 min
- 7 system → plugin conversions: 3-4 hours
- Registration in main.py: 30 min
- Documentation updates: 1-2 hours
- Testing and validation: 1 hour
- **Total: 6-8 hours of focused work**

## Next Steps

1. Convert AchievementPlugin to modern API
2. Convert BurnoutSystem → BurnoutPlugin (as example for others)
3. Convert remaining 6 systems using BurnoutPlugin as template
4. Register all in main.py
5. Deprecate plugin_system.py
6. Update all documentation
7. Run full test suite
8. Create commit
