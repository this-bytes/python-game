# TAB UI IMPLEMENTATION PLAN - Ready for Coding Agent Delegation

**Status**: READY FOR IMPLEMENTATION  
**Priority**: HIGH - Game UI requires functional tabs  
**Complexity**: Medium  
**Estimated Time**: 2-3 hours  

---

## EXECUTIVE SUMMARY

Implement proper tab-based UI navigation where each tab displays DIFFERENT content using EXISTING UI components. Currently all tabs show the same hardcoded dashboard panels. This breaks tab separation of concerns.

**The Fix**: Make each tab show only its relevant content by controlling component visibility and layout based on `active_tab`.

---

## ARCHITECTURAL UNDERSTANDING (Foundation)

### Core Principles
1. **Tabs are screen-level separation of concerns** - Each tab is a distinct view into a subsystem
2. **Reuse existing components** - Don't create new panels; configure existing ones per tab
3. **EventBus for all actions** - User clicks button → publish event → system handles → UI reflects result
4. **Direct game_state reads** - Tabs render from game_state, not separate caches
5. **Reactive updates** - Events signal "something changed", next frame re-reads game_state

### Tab Content Design
- **Dashboard**: Summary widgets from UIProvider plugins (all systems at a glance)
- **Operations**: Specialist management - full roster, hire/fire, click to detail
- **Incidents**: Incident queue - unassigned incidents, click to assign
- **Specialists**: Alternative specialist view (same roster, different focus)
- **Analytics**: Statistics and metrics from systems

---

## CURRENT PROBLEM (What's Broken)

### File: `/home/localadmin/python-game/src/ui/game_ui.py`

**Lines 430-500 (render method)**:
```python
# WRONG - ALL tabs show the same content
if self.active_tab == "dashboard":
    self.dashboard_panel.draw(self.screen, self.game_state)
    self.specialist_roster.draw(self.screen, self.game_state.specialists)
    self.incident_queue.draw(self.screen, unassigned_incidents, self.game_state)
    
elif self.active_tab == "operations":
    # ALSO shows specialist_roster + incident_queue (REDUNDANT)
    self.specialist_roster.draw(self.screen, self.game_state.specialists)
    self.incident_queue.draw(self.screen, ...)
    
elif self.active_tab == "incidents":
    # ALSO shows incident_queue (REDUNDANT)
    self.incident_queue.draw(self.screen, ...)
```

**Problem**: 
- Tabs aren't visually separated
- Same components appear in multiple tabs
- No clear tab-specific content
- Player can't distinguish between tabs by content

---

## EXACT REQUIREMENTS

### Requirement 1: Tab Content Separation

Each tab MUST show ONLY its relevant content:

| Tab | Content Component | Data Source | Purpose |
|-----|------------------|-------------|---------|
| Dashboard | `dashboard_panel` | UIProvider plugins | System overview |
| Operations | `specialist_roster` | `game_state.specialists` | Specialist management |
| Incidents | `incident_queue` | `game_state.incidents` (unassigned) | Incident queue |
| Specialists | `specialist_roster` (alt layout) | `game_state.specialists` | Team view |
| Analytics | (NEW) Analytics panel | Economy/analytics plugins | Metrics |

### Requirement 2: Conditional Rendering

Only one tab's content renders per frame based on `self.active_tab`:

```python
if self.active_tab == "dashboard":
    self._render_dashboard_tab()
elif self.active_tab == "operations":
    self._render_operations_tab()
elif self.active_tab == "incidents":
    self._render_incidents_tab()
elif self.active_tab == "specialists":
    self._render_specialists_tab()
elif self.active_tab == "analytics":
    self._render_analytics_tab()
```

Each render method:
- ✅ Renders ONLY that tab's content
- ✅ No other tabs render simultaneously
- ✅ Uses existing UI components where available
- ✅ Delegates to components (don't duplicate drawing code)

### Requirement 3: Reuse Existing Components

- **`SpecialistRosterPanel`**: Use in both Operations and Specialists tabs
  - Operations: Full view with hire/fire buttons
  - Specialists: Maybe filtered view or different layout
- **`IncidentQueuePanel`**: Use in Incidents tab
  - Shows unassigned incidents only
  - Click to open incident modal
- **`DashboardPanel`**: Use in Dashboard tab
  - Shows all UIProvider widgets
- **`DetailPanelRenderer`**: Already exists for modals
  - Reuse for displaying clicked entity details

### Requirement 4: Event Publishing (Action Flow)

All user actions from tabs MUST publish events:

**Specialist Modal Actions**:
- Assign specialist → Publish `"action:assign_specialist"`
- Promote specialist → Publish `"action:promote_specialist"`
- Deactivate specialist → Publish `"action:deactivate_specialist"`
- Rest specialist → Publish `"action:rest_specialist"`

**Incident Modal Actions**:
- Assign incident → Publish `"action:assign_incident"`
- Cancel → Close modal

**Roster Panel Actions**:
- Hire specialist → Publish `"action:hire_specialist"`
- Fire specialist → Publish `"action:fire_specialist"`
- Click specialist → Open detail modal

**Pattern**:
```python
# In GameUI._on_specialist_modal_action():
def _on_specialist_modal_assign(self, specialist_id: str) -> None:
    """Publish action event when user clicks Assign button."""
    self.event_bus.publish("action:assign_specialist", {
        "specialist_id": specialist_id
    }, source="game_ui")
    self.logger.info(f"[GAME_UI] Published action:assign_specialist for {specialist_id}")
```

### Requirement 5: Event Subscriptions

GameUI MUST subscribe to data update events to know when to redraw:

```python
def __init__(self, game_state, system_manager=None):
    # ... existing code ...
    
    # Subscribe to data changes
    self.event_bus.subscribe("specialist_hired", self._on_data_changed)
    self.event_bus.subscribe("specialist_fired", self._on_data_changed)
    self.event_bus.subscribe("incident_generated", self._on_data_changed)
    self.event_bus.subscribe("incident_assigned", self._on_data_changed)
    self.event_bus.subscribe("incident_completed", self._on_data_changed)

def _on_data_changed(self, event) -> None:
    """Flag that data changed. Next render() will read fresh game_state."""
    self.logger.debug(f"[GAME_UI] Data changed: {event.type}")
    # No caching needed - render() reads game_state directly next frame
```

### Requirement 6: Tab Click Publishing

When user clicks tab, publish event (already partially done):

```python
# In GameUI.handle_input():
if self.tab_bar.handle_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.active_tab = self.tab_bar.active_tab_id
        self.event_bus.publish("ui_tab_changed", {
            "tab_id": self.active_tab
        }, source="game_ui")
        self.logger.info(f"[GAME_UI] Tab changed to: {self.active_tab}")
    continue
```

Game systems CAN listen if they care:
```python
# Example: Analytics plugin resets when switching to analytics tab
self.event_bus.subscribe("ui_tab_changed", self._on_tab_changed)

def _on_tab_changed(self, event):
    if event.data.get("tab_id") == "analytics":
        self._refresh_metrics()
```

---

## IMPLEMENTATION STEPS

### Step 1: Create Tab Render Methods

**File**: `src/ui/game_ui.py`

Add these methods to GameUI class:

```python
def _render_dashboard_tab(self) -> None:
    """Render dashboard tab - overview of all systems."""
    if self.dashboard_panel and self.dashboard_manager:
        self.dashboard_panel.draw(self.screen, self.game_state)

def _render_operations_tab(self) -> None:
    """Render operations tab - specialist management."""
    self.specialist_roster.draw(self.screen, self.game_state.specialists)

def _render_incidents_tab(self) -> None:
    """Render incidents tab - incident queue."""
    unassigned_incidents = [
        inc for inc in self.game_state.incidents 
        if not hasattr(inc, 'assigned_specialist_id') or inc.assigned_specialist_id is None
    ]
    self.incident_queue.draw(self.screen, unassigned_incidents, self.game_state)

def _render_specialists_tab(self) -> None:
    """Render specialists tab - team view (alternative specialist display)."""
    # Can reuse specialist_roster or create filtered view
    self.specialist_roster.draw(self.screen, self.game_state.specialists)

def _render_analytics_tab(self) -> None:
    """Render analytics tab - metrics and statistics."""
    # For now: placeholder text saying "Analytics Coming Soon"
    # TODO: Create analytics panel or delegate to economy_plugin
    self._render_empty_tab("📈 Analytics - Coming Soon")

def _render_empty_tab(self, message: str) -> None:
    """Render empty tab placeholder."""
    font = pygame.font.SysFont('Arial', 24)
    text = font.render(message, True, (200, 200, 200))
    text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
    self.screen.blit(text, text_rect)
```

**Requirements**:
- ✅ Each method renders ONE tab's content only
- ✅ Reuse existing UI components
- ✅ Use game_state as data source (direct reads)
- ✅ No hardcoded UI components in multiple methods

### Step 2: Rewrite render() Method

**File**: `src/ui/game_ui.py`, lines 430-500

Replace entire render method with:

```python
def render(self) -> None:
    """Render the game UI with tab-based separation."""
    # Get background color from theme
    bg_color = self.theme_manager.get_color("background", (15, 15, 25))
    self.screen.fill(bg_color)

    # Render HUD overlay (always visible)
    self.hud_overlay.draw(self.screen, self.game_state, self.active_tab.capitalize())
    
    # Render TabBar (always visible at top)
    self.tab_bar.draw(self.screen)
    
    # Render ONLY current tab content
    if self.active_tab == "dashboard":
        self._render_dashboard_tab()
    elif self.active_tab == "operations":
        self._render_operations_tab()
    elif self.active_tab == "incidents":
        self._render_incidents_tab()
    elif self.active_tab == "specialists":
        self._render_specialists_tab()
    elif self.active_tab == "analytics":
        self._render_analytics_tab()
    else:
        self.logger.warning(f"[GAME_UI] Unknown tab: {self.active_tab}")
    
    # Render quick reference card (always visible)
    self.quick_reference.render(self.screen)
    
    # Render detail panel if open (modal - always on top)
    if self.detail_panel_open and self.detail_panel_data:
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        self.detail_panel_renderer.render(
            self.screen,
            self.detail_panel_data,
            self.detail_panel_rect.x,
            self.detail_panel_rect.y,
            on_close=self._on_detail_panel_close
        )

    # Render Tab + Modal system on top
    if self.tab_modal_manager.has_active_modal():
        self.tab_modal_manager.draw(self.screen)

    # Render legacy modals on top (for backward compatibility)
    self.modal_manager.draw()

    # Render notifications (always on top)
    self.notification_manager.draw(self.screen, self.game_state)

    # Render help overlay if active
    if self.show_help_overlay:
        self._render_help_overlay()

    # Update display
    pygame.display.flip()
```

**Key Changes**:
- ✅ Removed hardcoded panel rendering
- ✅ Added conditional tab rendering
- ✅ Each tab gets only its content
- ✅ Kept overlay systems (detail panel, modals, notifications)

### Step 3: Add Event Subscriptions

**File**: `src/ui/game_ui.py`, in `__init__()` method

Add after line 100 (after modal_manager initialization):

```python
# Subscribe to data change events so we know when to redraw
self.event_bus.subscribe("specialist_hired", self._on_data_changed)
self.event_bus.subscribe("specialist_fired", self._on_data_changed)
self.event_bus.subscribe("specialist_leveled_up", self._on_data_changed)
self.event_bus.subscribe("incident_generated", self._on_data_changed)
self.event_bus.subscribe("incident_assigned", self._on_data_changed)
self.event_bus.subscribe("incident_completed", self._on_data_changed)

self.logger.info("[GAME_UI] Subscribed to data change events")
```

Add handler method:

```python
def _on_data_changed(self, event) -> None:
    """Handle any data change event.
    
    No action needed - render() will read fresh game_state next frame.
    Just log for debugging.
    """
    self.logger.debug(f"[GAME_UI] Data changed event: {event.type}")
```

### Step 4: Wire Modal Actions to EventBus

**File**: `src/ui/game_ui.py`

When opening specialist modal:

```python
def _open_specialist_modal(self, specialist_id: str) -> None:
    """Open specialist detail modal and publish events for actions."""
    specialist = self.game_state.get_specialist(specialist_id)
    if not specialist:
        return
    
    modal = SpecialistModal(
        specialist,
        on_assign_clicked=lambda: self._publish_specialist_action("assign", specialist_id),
        on_promote_clicked=lambda: self._publish_specialist_action("promote", specialist_id),
        on_deactivate_clicked=lambda: self._publish_specialist_action("deactivate", specialist_id)
    )
    modal.set_position(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
    self.tab_modal_manager.push_modal(modal)

def _publish_specialist_action(self, action: str, specialist_id: str) -> None:
    """Publish specialist action event."""
    event_name = f"action:{action}_specialist"
    self.event_bus.publish(event_name, {
        "specialist_id": specialist_id
    }, source="game_ui")
    self.logger.info(f"[GAME_UI] Published {event_name} for specialist {specialist_id}")
```

**Same pattern for incident modals**:

```python
def _open_incident_modal(self, incident_id: str) -> None:
    """Open incident detail modal and publish events for actions."""
    incident = self.game_state.get_incident(incident_id)
    if not incident:
        return
    
    modal = IncidentModal(
        incident,
        on_assign_clicked=lambda specialist_id: self._publish_incident_action("assign", incident_id, specialist_id),
        on_cancel_clicked=lambda: self.tab_modal_manager.pop_modal()
    )
    modal.set_position(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
    self.tab_modal_manager.push_modal(modal)

def _publish_incident_action(self, action: str, incident_id: str, specialist_id: str = None) -> None:
    """Publish incident action event."""
    event_name = f"action:{action}_incident"
    data = {"incident_id": incident_id}
    if specialist_id:
        data["specialist_id"] = specialist_id
    
    self.event_bus.publish(event_name, data, source="game_ui")
    self.logger.info(f"[GAME_UI] Published {event_name} for incident {incident_id}")
```

### Step 5: Update handle_input() Event Publishing

**File**: `src/ui/game_ui.py`, in `handle_input()` method

Verify tab click publishes event (should already be done):

```python
# Handle tab bar clicks (before modal manager)
if self.tab_bar.handle_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.active_tab = self.tab_bar.active_tab_id
        self.event_bus.publish("ui_tab_changed", {
            "tab_id": self.active_tab
        }, source="game_ui")
        self.logger.info(f"[GAME_UI] Published ui_tab_changed: {self.active_tab}")
    continue
```

---

## SUCCESS CRITERIA (Acceptance Tests)

### Criterion 1: Tab Content Separation
- [ ] Start game, click Dashboard tab → See only dashboard widgets
- [ ] Click Operations tab → See only specialist roster
- [ ] Click Incidents tab → See only incident queue
- [ ] Click Specialists tab → See specialist roster (alternative view)
- [ ] Click Analytics tab → See placeholder "Coming Soon" message
- [ ] Tabs visually switch content (no overlap)

### Criterion 2: No Content Duplication
- [ ] Specialist roster does NOT appear in multiple tabs simultaneously
- [ ] Incident queue does NOT appear in multiple tabs simultaneously
- [ ] Dashboard widgets do NOT appear in Operations/Incidents tabs
- [ ] Each tab renders exactly ONE set of components

### Criterion 3: Event Publishing
- [ ] When tab clicked, "ui_tab_changed" event published to EventBus
- [ ] When specialist modal "Assign" clicked, "action:assign_specialist" event published
- [ ] When incident "Assign" clicked, "action:assign_incident" event published
- [ ] Events logged in game.log with proper context

### Criterion 4: Game Startup
- [ ] Game starts without errors
- [ ] No AttributeError or TypeError
- [ ] Game.log shows tab initialization
- [ ] Tabs visible and clickable

### Criterion 5: Data Reactivity
- [ ] When specialist hired, Operations tab updates without manual refresh
- [ ] When incident created, Incidents tab updates without manual refresh
- [ ] Clicking specialist in roster opens detail modal
- [ ] Clicking incident in queue opens detail modal

### Criterion 6: Code Quality
- [ ] All render methods have docstrings (PURPOSE, not WHAT)
- [ ] All methods have type hints
- [ ] No magic numbers (use config)
- [ ] No commented-out code
- [ ] Logging at INFO level for important actions
- [ ] No hardcoded strings (use constants or config)

---

## FILES TO MODIFY

| File | Changes | Lines | Complexity |
|------|---------|-------|------------|
| `src/ui/game_ui.py` | render() rewrite, add tab methods, add subscriptions, wire modals | 430-550 | High |
| `.github/instructions/ui-rendering.instructions.md` | Document tab architecture pattern | NEW | Medium |
| `TAB_MODAL_INTEGRATION_COMPLETE.md` | DELETE - superseded by this plan | - | - |
| `ACCOUNTABILITY_REPORT.md` | DELETE - superseded by this plan | - | - |
| `CLARIFICATION_NEEDED.md` | DELETE - requirements now clear | - | - |
| `TAB_ARCHITECTURE_FIX.md` | DELETE - superseded by this plan | - | - |

---

## ARCHITECTURAL REFERENCES

**Follow these guidelines EXACTLY**:
- `.github/instructions/architecture.instructions.md` - Separation of concerns
- `.github/instructions/core-standards.instructions.md` - 15-point gate, type hints, docstrings
- `.github/instructions/code-style.instructions.md` - Naming conventions, anti-patterns
- `.github/instructions/plugin-system.instructions.md` - EventBus pattern

**Do NOT**:
- ❌ Hardcode content in render method
- ❌ Create duplicate component instances
- ❌ Modify game logic from UI
- ❌ Skip type hints or docstrings
- ❌ Leave debug prints or TODO comments
- ❌ Make changes without logging

**DO**:
- ✅ Publish all actions via EventBus
- ✅ Subscribe to data changes
- ✅ Read from game_state directly (no caching)
- ✅ Reuse existing UI components
- ✅ Add comprehensive logging
- ✅ Follow 15-point gate before commit

---

## READY FOR DELEGATION

This plan is:
- ✅ Clear on objectives
- ✅ Specific on implementation
- ✅ Lists exact code changes
- ✅ Defines success criteria
- ✅ References guidelines
- ✅ No ambiguity

**Pass this plan to the coding agent.**
**Agent should be able to implement end-to-end without additional back-and-forth.**

---

## RELATED DOCUMENTATION

Once implementation complete, update:
1. `.github/instructions/ui-rendering.instructions.md` - Tab architecture pattern
2. `docs/UI_SYSTEM.md` - Tab implementation example
3. `docs/UI_FRAMEWORK_GUIDE.md` - Tab usage guide

