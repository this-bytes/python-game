# Fix Game Loop Crashes and EventBus Shutdown Error

## Summary
Fixed two critical bugs preventing the game from running when loading from save: EventBus unsubscribe signature mismatch and missing system initializations in GameState.from_dict().

## Problems Fixed

### Issue #1: EventBus.unsubscribe() Signature Mismatch
**Error**: `EventBus.unsubscribe() takes 2 positional arguments but 3 were given`

**Root Cause**: idle_plugin.shutdown() was calling `unsubscribe(event_type, callback)` but EventBus.unsubscribe() only accepts `subscription_id` as a parameter.

**Impact**: Game could not shut down properly - idle_core plugin failed during cleanup.

### Issue #2: Game Loop Crash on Load
**Error**: `'NoneType' object has no attribute 'update'`
**Traceback**:
```
File "src/main.py", line 438, in _run_game
    self.game_state.update(delta_time)
File "src/models/game_state.py", line 346, in update
    self._dopamine_system.update(effective_delta)
AttributeError: 'NoneType' object has no attribute 'update'
```

**Root Cause**: GameState.from_dict() was using `cls.__new__(cls)` which bypasses `__post_init__()`. This meant the following systems were NEVER initialized when loading from save:
- `_dopamine_system` → None
- `_burnout_system` → None  
- `_relationships_system` → None
- `_idle_core` → None
- `_equipment_system` → None

Additionally, two dataclass fields were not being restored:
- `dopamine_feedback_queue` → missing
- `active_risk_contracts` → missing

**Impact**: Game crashed immediately after loading save file. Could not continue saved games.

## Solutions Implemented

### Fix #1: idle_plugin EventBus Subscription Management

**File**: `src/core/plugins/idle_plugin.py`

**Changes**:
1. Added `_subscription_ids: list` to store subscription IDs returned by EventBus.subscribe()
2. Modified `initialize()` to capture and store subscription IDs:
   ```python
   self._subscription_ids = [
       self._event_bus.subscribe("incident_generated", self._on_incident_generated),
       self._event_bus.subscribe("specialist_available", self._on_specialist_available),
       self._event_bus.subscribe("game_state_updated", self._on_game_state_updated)
   ]
   ```
3. Modified `shutdown()` to unsubscribe using stored IDs:
   ```python
   for subscription_id in self._subscription_ids:
       self._event_bus.unsubscribe(subscription_id)
   self._subscription_ids.clear()
   ```

**Result**: idle_plugin now properly cleans up event subscriptions without errors.

### Fix #2: GameState System Initialization on Load

**File**: `src/models/game_state.py`

**Changes in from_dict() method**:

1. **Added missing dataclass field initialization**:
   ```python
   instance.dopamine_feedback_queue = data.get("dopamine_feedback_queue", []).copy()
   instance.active_risk_contracts = data.get("active_risk_contracts", {}).copy()
   ```

2. **Added system initialization** (previously only in `__post_init__`):
   ```python
   # Initialize systems that are normally created in __post_init__
   from src.core.dopamine_system import DopamineSystem
   from src.core.idle_core import IdleCore
   from src.core.equipment_system import EquipmentSystem
   
   instance._dopamine_system = DopamineSystem()
   instance._burnout_system = BurnoutSystem()
   instance._idle_core = IdleCore()
   
   try:
       game_config = instance._json_loader.load_data("game_config.json")
       instance._relationships_system = RelationshipsSystem(game_config)
   except Exception:
       instance._relationships_system = RelationshipsSystem({})
   
   try:
       equipment_config = instance._json_loader.load_data("equipment.json")
       instance._equipment_system = EquipmentSystem(equipment_config)
   except Exception:
       instance._equipment_system = EquipmentSystem({})
   ```

**Result**: All systems are now properly initialized when loading from save, matching the state created by `__post_init__()` for new games.

### Fix #3: Enhanced Error Logging

**File**: `src/main.py`

**Changes**:
1. Added traceback logging to game loop exception handler:
   ```python
   except Exception as e:
       import traceback
       self.logger.logger.error(f"[GAME] Unexpected error in game loop: {e}")
       self.logger.logger.error(f"[GAME] Traceback:\n{traceback.format_exc()}")
   ```

2. Added null checks in `_run_game()` with early exit:
   ```python
   if not self.game_state:
       self.logger.logger.error("[GAME] game_state is None in _run_game!")
       self.running = False
       return
   
   if not self.ui:
       self.logger.logger.error("[GAME] ui is None in _run_game!")
       self.running = False
       return
   ```

**Result**: Better debugging information when errors occur. Early detection of critical missing objects.

## Testing

### Manual Testing
✅ **Continue Mode**: Game loads from save and runs without crashes
```bash
timeout 5 python3 src/main.py --continue
# Result: Game runs successfully for 5 seconds, no errors
```

✅ **New Game Mode**: Game initializes correctly
```bash
timeout 5 python3 src/main.py --new-game  
# Result: Game initializes and runs successfully
```

✅ **Shutdown**: idle_plugin shuts down cleanly
```
INFO | src.core.plugins.idle_plugin | Idle Core Plugin shut down
INFO | system_manager | [SYSTEM_MANAGER] Shutdown: idle_core
# No errors during shutdown
```

### Automated Testing
✅ **All 727 tests pass** in 4.19 seconds

```bash
python3 -m pytest tests/ -x --tb=short -q
# 727 passed in 4.19s
```

## Files Modified

1. **src/core/plugins/idle_plugin.py**
   - Added `_subscription_ids` list to track subscriptions
   - Modified `initialize()` to store subscription IDs
   - Modified `shutdown()` to use stored IDs

2. **src/models/game_state.py**
   - Added `dopamine_feedback_queue` and `active_risk_contracts` initialization in `from_dict()`
   - Added `_dopamine_system`, `_burnout_system`, `_relationships_system`, `_idle_core`, and `_equipment_system` initialization in `from_dict()`

3. **src/main.py**
   - Added traceback logging to exception handler
   - Added null checks in `_run_game()` with graceful failure

## Impact

### Before Fix
- ❌ Game crashed immediately when loading from save
- ❌ idle_plugin threw errors during shutdown
- ❌ No visibility into what was failing
- ❌ Could not continue saved games

### After Fix
- ✅ Game loads from save successfully
- ✅ All systems initialized correctly
- ✅ idle_plugin shuts down cleanly
- ✅ Detailed error logging with tracebacks
- ✅ Graceful handling of missing objects
- ✅ All 727 tests passing

## Architecture Notes

### EventBus Subscription Pattern
All plugins that subscribe to events must follow this pattern:
```python
class MyPlugin(GameSystem):
    def __init__(self):
        self._subscription_ids = []  # REQUIRED
    
    def initialize(self, game_state):
        self._subscription_ids = [
            event_bus.subscribe("event_name", callback),
            # Store all subscription IDs
        ]
    
    def shutdown(self, game_state):
        for subscription_id in self._subscription_ids:
            event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()
```

### GameState Initialization Duality
GameState has TWO initialization paths that MUST be kept in sync:
1. **`__post_init__()`** - Called for new games created with `GameState()`
2. **`from_dict()`** - Called when loading saved games

**CRITICAL**: Any system initialized in `__post_init__()` MUST also be initialized in `from_dict()`. Otherwise, loaded games will have `None` for those systems and crash.

## Lessons Learned

1. **EventBus API Mismatch**: When wrapping event-driven systems, always store subscription IDs for proper cleanup.

2. **Dataclass Initialization**: Using `cls.__new__(cls)` bypasses `__post_init__()`. Must manually initialize all fields and systems in `from_dict()`.

3. **Missing Field Initialization**: Dataclass fields with `field(default_factory=list)` are NOT automatically initialized when using `__new__()`.

4. **Comprehensive Error Logging**: Adding tracebacks to exception handlers is CRITICAL for debugging complex initialization flows.

5. **Test Coverage**: While we have 727 tests, none caught the save/load initialization bug. This suggests we need more integration tests for the save/load cycle.

## Future Improvements

1. **Refactor GameState initialization** - Consider using a factory method to ensure both paths are identical
2. **Add save/load integration tests** - Test that loaded games have all systems initialized
3. **EventBus subscription helper** - Create a mixin or base class that handles subscription ID tracking automatically
4. **Validate system initialization** - Add assertions in GameState to verify all systems are initialized before allowing game loop to run

---

**Result**: Game is now fully functional with save/load working correctly and proper plugin cleanup! 🎉
