# Plugin System Refactor - Status & Recommendation

## What's Been Done ✅

### 1. PrestigePlugin - FULLY CONVERTED
**File**: `src/core/plugins/prestige_plugin.py`
**Changes**:
- ✅ Changed import from `plugin_system` to `game_system`
- ✅ Updated constructor: Removed `event_bus` parameter
- ✅ Added `get_name()` and `get_feature_id()` methods
- ✅ Updated all method signatures to include `game_state` parameter
- ✅ Switched from `event_bus.emit()` to `event_bus.publish()`
- ✅ Fixed subscriptions to store IDs for proper cleanup
- ✅ Renamed `get_state()` → `save_state()`, `set_state()` → `load_state()`
- ✅ Updated event handlers to use `event.data` instead of direct dict

### 2. Documentation Created
- ✅ `PLUGIN_REFACTOR_PLAN.md` - Complete migration guide with examples

## What Still Needs to Be Done 🔄

### Phase 1: Convert Remaining Plugins (6-8 hours)

1. **AchievementPlugin** (`src/core/plugins/achievement_plugin.py`)
   - Currently uses old API
   - High complexity (8+ event subscriptions)
   - Estimated time: 45 min

2. **BurnoutSystem → BurnoutPlugin**
   - Create `src/core/plugins/burnout_plugin.py`
   - Wrap existing BurnoutSystem in plugin interface
   - Estimated time: 45 min

3. **RelationshipsSystem → RelationshipsPlugin**
   - Create `src/core/plugins/relationships_plugin.py`
   - Estimated time: 45 min

4. **DopamineSystem → DopaminePlugin**
   - Create `src/core/plugins/dopamine_plugin.py`
   - Estimated time: 30 min

5. **EquipmentSystem → EquipmentPlugin**
   - Create `src/core/plugins/equipment_plugin.py`
   - Estimated time: 45 min

6. **AbilitySystem → AbilityPlugin**
   - Create `src/core/plugins/ability_plugin.py`
   - Estimated time: 30 min

7. **PassiveIncomeSystem → PassiveIncomePlugin**
   - Create `src/core/plugins/passive_income_plugin.py`
   - Estimated time: 30 min

8. **FacilitySystem → FacilityPlugin**
   - Create `src/core/plugins/facility_plugin.py`
   - Estimated time: 45 min

### Phase 2: Integration (1 hour)

9. **Register All Plugins in main.py**
   - Add imports for all 10 plugins
   - Register each in SystemManager
   - Estimated time: 30 min

10. **Deprecate plugin_system.py**
    - Add deprecation warning
    - Add migration guide reference
    - Estimated time: 15 min

### Phase 3: Documentation (2-3 hours)

11. **Update ARCHITECTURE.md**
    - Remove old plugin_system references
    - Document plugin-only architecture
    - Show SystemManager usage patterns
    - Estimated time: 45 min

12. **Update copilot-instructions.md** (CRITICAL)
    - Update Project Fundamentals section
    - Change all plugin references to modern API
    - Update separation of concerns
    - Add plugin creation checklist
    - Estimated time: 45 min

13. **Update COMMON_TASKS.md**
    - Add "Create a New Plugin" guide
    - Update system-related tasks
    - Estimated time: 30 min

14. **Update TESTING_STANDARDS.md**
    - Add plugin testing patterns
    - Document event bus mocking
    - Estimated time: 15 min

15. **Update Other Documentation**
    - ANTI_PATTERNS.md - Add plugin anti-patterns
    - CODE_STYLE.md - Add plugin style guide
    - Estimated time: 30 min

### Phase 4: Validation (1 hour)

16. **Run Full Test Suite**
    - Verify all 413 tests pass
    - Fix any regressions
    - Estimated time: 30 min

17. **Final Review**
    - Grep for old API usage
    - Verify no TODOs added
    - Check all documentation consistency
    - Estimated time: 30 min

## Total Estimated Time: 10-12 hours

## Recommendation: TWO APPROACHES

### Approach A: Complete Now (Autonomous)
**Pros**:
- Single cohesive refactor
- All documentation updated together
- No partial state in codebase

**Cons**:
- Very long session (10-12 hours of agent work)
- High token usage (~500K+ tokens)
- Risk of timeout/errors mid-refactor

**Process**:
1. I continue converting all 8 systems systematically
2. Update all documentation files
3. Run tests after each major change
4. Create comprehensive commit at end

### Approach B: Staged Refactor (Recommended)
**Pros**:
- Lower risk - can validate after each stage
- Better for debugging issues
- Can pause/resume between stages
- Lower token usage per session

**Cons**:
- Codebase temporarily has mixed APIs
- More commits to track

**Process**:
**Stage 1** (Now - 2-3 hours):
- Convert AchievementPlugin
- Convert 2-3 high-priority systems (Burnout, Relationships, Equipment)
- Register in main.py
- Update copilot-instructions.md partially
- Test (should still have 413 passing)
- COMMIT

**Stage 2** (Next session - 2-3 hours):
- Convert remaining systems
- Complete main.py registration
- Deprecate plugin_system.py
- Test
- COMMIT

**Stage 3** (Next session - 2-3 hours):
- Update all documentation comprehensively
- Final copilot-instructions.md sync
- Final testing
- COMMIT

## My Recommendation: Approach B (Staged)

**Reasons**:
1. We've already completed PrestigePlugin successfully - good stopping point
2. Each stage can be tested independently
3. Lower risk of breaking all 413 tests at once
4. copilot-instructions.md can be updated incrementally
5. Easier to debug issues if they arise
6. You can review progress between stages

## Immediate Next Step

If you agree with Staged approach:
1. I'll convert AchievementPlugin next (45 min)
2. Then convert BurnoutSystem → BurnoutPlugin (45 min)
3. Register both in main.py
4. Update copilot-instructions.md to mention plugin-first architecture
5. Run tests
6. Create commit message for "Stage 1: Convert PrestigePlugin, AchievementPlugin, BurnoutPlugin"

**Or** if you want me to continue with full refactor now, I'll proceed with all 8 conversions.

## Question for You

**Should I**:
A) Continue with full refactor now (10-12 hours, ~500K tokens)
B) Complete Stage 1 now (2-3 hours), commit, continue in next session
C) Stop here, you'll review and decide next steps

Please let me know your preference!
