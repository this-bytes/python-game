# UI ↔ Logic Boundary Audit

## Overview

This document audits the separation between UI (rendering) and game logic across the codebase. Following the principle: **"UI renders, game logic thinks"**.

**Status**: ✅ Generally compliant, some direct game state modification in UI panels

---

## Architectural Principles

1. **UI reads game state, doesn't modify it** - UI components query GameState for rendering
2. **UI returns actions, doesn't execute them** - User input creates action objects for game loop to process
3. **Game logic is backend-authoritative** - All state changes happen in src/models and src/core
4. **UI has no business logic** - No XP calculations, no incident generation, no state transitions

---

## Component Audit

### ✅ Compliant Components

#### Navigation Menu (`src/ui/components/navigation_menu.py`)
- **Status**: ✅ COMPLIANT
- **Reads**: Nothing (pure UI)
- **Modifies**: Nothing
- **Returns**: View change requests via callback

#### HUD Overlay (`src/ui/components/hud_overlay.py`)
- **Status**: ✅ COMPLIANT
- **Reads**: `game_state.current_money`, `game_state.current_time`, `game_state.metrics`
- **Modifies**: Nothing
- **Returns**: Nothing (pure rendering)

#### Theme Manager (`src/ui/theme_manager.py`)
- **Status**: ✅ COMPLIANT
- **Reads**: Nothing (manages UI colors only)
- **Modifies**: Nothing
- **Returns**: Color schemes

#### Layout System (`src/ui/layout_manager.py`, `src/ui/view_manager.py`)
- **Status**: ✅ COMPLIANT
- **Reads**: Panel positions/sizes
- **Modifies**: Panel layout only (not game state)
- **Returns**: Layout configurations

---

### ⚠️ Partially Compliant Components (Direct State Modification)

#### Incident Queue Panel (`src/ui/panels/incident_queue_panel.py`)
- **Status**: ⚠️ PARTIALLY COMPLIANT
- **Reads**: `game_state.incidents` (read-only - OK)
- **Modifies**: Calls `game_state.assign_incident_to_specialist()` directly
- **Issue**: Line 72-75 - direct method call instead of returning action
- **Recommendation**: Return `GameAction(action_type="assign_incident", data={...})` instead

```python
# Current (DIRECT):
def assign_selected_to_specialist(self, specialist_id: str) -> bool:
    return self.game_state.assign_incident_to_specialist(
        self.selected_incident.id,
        specialist_id
    )

# Should be (ACTION-BASED):
def get_assignment_action(self, specialist_id: str) -> Optional[GameAction]:
    if not self.selected_incident:
        return None
    return GameAction(
        action_type="assign_incident",
        data={
            "incident_id": self.selected_incident.id,
            "specialist_id": specialist_id
        }
    )
```

#### Specialist Roster Panel (`src/ui/panels/specialist_roster_panel.py`)
- **Status**: ✅ MOSTLY COMPLIANT
- **Reads**: `game_state.specialists` (read-only - OK)
- **Modifies**: Nothing directly
- **Returns**: Selection state

#### Equipment Shop Panel (`src/ui/panels/equipment_shop_panel.py`)
- **Status**: ⚠️ NEEDS AUDIT
- **Action Required**: Check for direct equipment purchase/equipping

#### Equipment Inventory Panel (`src/ui/panels/equipment_inventory_panel.py`)
- **Status**: ⚠️ NEEDS AUDIT
- **Action Required**: Check for direct inventory modifications

#### Metrics Panel (`src/ui/panels/metrics_panel.py`)
- **Status**: ✅ COMPLIANT (expected to be read-only)
- **Reads**: `game_state.metrics`
- **Modifies**: Nothing

---

### 🔍 Components Requiring Full Audit

The following components need detailed review:

1. **GameUI Main Loop** (`src/ui/game_ui.py`)
   - Check event handling - does it call game state methods directly?
   - Check drag-and-drop logic for incident assignment
   - Verify all user interactions return actions

2. **Main Menu** (`src/ui/main_menu.py`)
   - Check if it creates new game states directly
   - Verify save/load goes through proper channels

3. **Debug Overlay** (`src/ui/debug_overlay.py`)
   - Likely has god-mode modifications (acceptable for debug)
   - Should be disabled in production mode

---

## Critical Findings

### 🚨 High Priority

1. **Incident Assignment in UI** - `IncidentQueuePanel.assign_selected_to_specialist()` calls game state directly
   - **Risk**: Cannot be intercepted by network layer
   - **Fix**: Refactor to action-based pattern

2. **Equipment System** - Needs audit for direct purchases/equipping
   - **Risk**: May bypass server validation in remote mode
   - **Fix**: All equipment operations must be actions

### ⚠️ Medium Priority

3. **Drag-and-Drop State** - UI maintains selection state
   - **Current**: OK for UI state (which incident/specialist is selected)
   - **Risk**: If selection triggers game logic changes
   - **Fix**: Ensure selection is purely visual until action submitted

---

## Action-Based Pattern (Standard)

All UI interactions should follow this pattern:

```python
# In UI Panel
def handle_user_click(self, ...):
    """Handle user click and return action."""
    # Validate user input (UI-level validation only)
    if not self.validate_selection():
        return None
    
    # Return action for game loop to process
    return GameAction(
        action_type="assign_incident",
        data={
            "incident_id": self.selected_incident.id,
            "specialist_id": specialist_id,
            "timestamp": time.time()
        }
    )

# In Game Loop (main.py)
def process_ui_action(self, action: GameAction):
    """Process action from UI."""
    if action.action_type == "assign_incident":
        # This is where game logic lives
        self.game_state.assign_incident_to_specialist(
            action.data["incident_id"],
            action.data["specialist_id"]
        )
```

---

## Backend Integration Points

### Current State
- Backend exists: `backend/app.py` with Flask + SocketIO
- Backend routes: REST endpoints in `backend/routes/`
- WebSocket service: `backend/services/websocket_service.py`
- Integration layer: `src/utils/backend_integration.py`

### Required for Dual-Mode
1. **Local Server Mode**: Launch backend in same process as UI
2. **Remote Server Mode**: Connect UI to remote backend via HTTP/WS
3. **Action Interception**: All UI actions route through network client
4. **State Sync**: Game state updates broadcast via WebSocket

---

## Testing Requirements

### UI Isolation Tests
- [ ] UI can render with read-only game state snapshot
- [ ] UI actions return action objects (not executing logic)
- [ ] UI doesn't crash when game state is None (disconnected mode)

### Network Client Tests
- [ ] All UI actions can be serialized to JSON
- [ ] Round-trip: UI → Action → Network → Server → State → UI
- [ ] Latency tolerance: UI remains responsive with 100ms network delay

### Mode Parity Tests
- [ ] Local mode behaves identically to remote mode
- [ ] Save/load works in both modes
- [ ] No features exclusive to either mode

---

## Compliance Status Summary

| Component | Status | Issues | Priority |
|-----------|--------|--------|----------|
| Navigation Menu | ✅ Compliant | None | - |
| HUD Overlay | ✅ Compliant | None | - |
| Theme Manager | ✅ Compliant | None | - |
| Layout System | ✅ Compliant | None | - |
| Specialist Roster | ✅ Compliant | None | - |
| Metrics Panel | ✅ Compliant | None | - |
| Incident Queue | ⚠️ Partial | Direct assignment | High |
| Equipment Shop | 🔍 Needs Audit | Unknown | Medium |
| Equipment Inventory | 🔍 Needs Audit | Unknown | Medium |
| GameUI Main Loop | 🔍 Needs Audit | Unknown | High |
| Main Menu | 🔍 Needs Audit | Save/load | Medium |

---

## Remediation Plan

### Phase 1: High Priority Fixes
1. Refactor `IncidentQueuePanel.assign_selected_to_specialist()` to action-based
2. Audit `GameUI` main loop for direct game state calls
3. Implement action queue in `GameUI`

### Phase 2: Equipment System Audit
1. Review equipment shop for direct purchases
2. Review inventory for direct equipping/unequipping
3. Convert to action-based pattern

### Phase 3: Validation
1. Add tests verifying UI doesn't modify game state
2. Run UI with read-only game state proxy
3. Test local vs remote mode parity

---

## Maintenance

**This document must be updated whenever:**
- A new UI component is added
- A UI component is modified to interact with game state
- Backend endpoints are added/changed
- Action types are added/removed

**Review Frequency**: Every PR that touches `src/ui/` or `src/models/`

---

**Last Updated**: 2025-10-19  
**Next Review**: When dual-mode backend is fully implemented
