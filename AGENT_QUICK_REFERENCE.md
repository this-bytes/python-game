# AGENT IMPLEMENTATION QUICK REFERENCE

**Use this file during implementation of TAB_UI_IMPLEMENTATION_PLAN.md**

---

## QUICK LINKS

- **Main Plan**: `TAB_UI_IMPLEMENTATION_PLAN.md`
- **This Reference**: This file
- **Guidelines**: `.github/instructions/ui-rendering.instructions.md`
- **Code Example File**: `src/ui/game_ui.py` (lines 1-100 for structure)

---

## IMPLEMENTATION CHECKLIST

### Before You Start
- [ ] Read `TAB_UI_IMPLEMENTATION_PLAN.md` completely
- [ ] Understand tab content structure (Dashboard, Operations, Incidents, etc.)
- [ ] Understand event flow (user action → publish event → system handles)
- [ ] Reference `.github/instructions/ui-rendering.instructions.md`

### Step 1: Add Tab Render Methods

**File**: `src/ui/game_ui.py`

Required methods to add:
```python
def _render_dashboard_tab(self) -> None: ...
def _render_operations_tab(self) -> None: ...
def _render_incidents_tab(self) -> None: ...
def _render_specialists_tab(self) -> None: ...
def _render_analytics_tab(self) -> None: ...
```

**Each method**:
- ✅ Has docstring explaining what it renders
- ✅ Renders only that tab's content (no overlap)
- ✅ Uses existing UI components
- ✅ Reads from game_state directly

**Check**:
- [ ] All 5 methods created
- [ ] All have docstrings
- [ ] All have type hints (`-> None`)
- [ ] No hardcoded rendering logic (delegate to components)

### Step 2: Rewrite render() Method

**File**: `src/ui/game_ui.py`, lines ~430-500

**Current render()**: Hardcoded panels all render simultaneously

**New render()**: 
1. Fill screen and draw always-visible elements (TabBar, HUD)
2. Conditional rendering based on `self.active_tab`
3. Draw overlays (detail panels, modals, notifications)

**Template**:
```python
def render(self) -> None:
    """Render game UI with tab-based separation."""
    # Background
    self.screen.fill(self.bg_color)
    
    # Always visible
    self.tab_bar.draw(self.screen)
    self.hud_overlay.draw(...)
    
    # Conditional tab rendering
    if self.active_tab == "dashboard":
        self._render_dashboard_tab()
    elif self.active_tab == "operations":
        self._render_operations_tab()
    # ... etc
    
    # Always on top
    self.detail_panel_renderer.render(...)
    self.notification_manager.draw(...)
    
    pygame.display.flip()
```

**Check**:
- [ ] Background filled
- [ ] TabBar drawn
- [ ] Conditional rendering (if/elif for each tab)
- [ ] Modals and notifications on top
- [ ] pygame.display.flip() at end

### Step 3: Add Event Subscriptions

**File**: `src/ui/game_ui.py`, in `__init__()` after line ~100

**Add subscriptions for data changes**:
```python
self.event_bus.subscribe("specialist_hired", self._on_data_changed)
self.event_bus.subscribe("specialist_fired", self._on_data_changed)
self.event_bus.subscribe("incident_assigned", self._on_data_changed)
self.event_bus.subscribe("incident_completed", self._on_data_changed)
```

**Add handler method**:
```python
def _on_data_changed(self, event) -> None:
    """Handle data change events. Next render() reads fresh game_state."""
    self.logger.debug(f"[GAME_UI] Data changed: {event.type}")
```

**Check**:
- [ ] Subscriptions added for key events
- [ ] Handler method created with docstring
- [ ] Handler has type hints
- [ ] Logging present

### Step 4: Wire Modal Actions

**File**: `src/ui/game_ui.py`, find modal opening methods

**When opening specialist modal**:
```python
def _open_specialist_modal(self, specialist_id: str) -> None:
    """Open specialist modal and wire actions."""
    specialist = self.game_state.get_specialist(specialist_id)
    if not specialist:
        return
    
    modal = SpecialistModal(
        specialist,
        on_assign_clicked=lambda: self._publish_specialist_action("assign", specialist_id),
        on_promote_clicked=lambda: self._publish_specialist_action("promote", specialist_id),
    )
    self.tab_modal_manager.push_modal(modal)
```

**Add action publisher**:
```python
def _publish_specialist_action(self, action: str, specialist_id: str) -> None:
    """Publish specialist action event."""
    event_name = f"action:{action}_specialist"
    self.event_bus.publish(event_name, {
        "specialist_id": specialist_id
    }, source="game_ui")
    self.logger.info(f"[GAME_UI] Published {event_name} for {specialist_id}")
```

**Same pattern for incidents**:
- `_open_incident_modal()` with action callbacks
- `_publish_incident_action()` to publish events

**Check**:
- [ ] Modal action callbacks wired
- [ ] Action publisher method created
- [ ] All actions publish events
- [ ] Logging at INFO level
- [ ] Type hints and docstrings present

### Step 5: Verify Tab Click Publishing

**File**: `src/ui/game_ui.py`, in `handle_input()` method

**Should already be implemented, verify**:
```python
if self.tab_bar.handle_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.active_tab = self.tab_bar.active_tab_id
        self.event_bus.publish("ui_tab_changed", {
            "tab_id": self.active_tab
        }, source="game_ui")
        self.logger.info(f"[GAME_UI] Published ui_tab_changed: {self.active_tab}")
    return
```

**Check**:
- [ ] Tab click publishes event
- [ ] Event includes tab_id in data
- [ ] Logging present
- [ ] Source is "game_ui"

---

## TESTING DURING IMPLEMENTATION

### Test 1: Startup
```bash
timeout 5 python main.py --local-server
# Expected: Game starts, no errors, TabBar visible
```

### Test 2: Tab Switching
```bash
# In game, click each tab
# Expected: Content changes, no other tabs render
# Check game.log:
tail -50 logs/game.log | grep "Tab changed"
```

### Test 3: Event Publishing
```bash
# Check logs for events
tail -100 logs/game.log | grep "Published"
# Expected: Tab changed event, action events when modals used
```

### Test 4: Component Rendering
```bash
# Verify only one tab renders per frame
grep -c "_render_.*_tab" src/ui/game_ui.py
# Expected: 5 methods, only 1 called per render()
```

---

## COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Rendering all components
```python
# WRONG
def render(self):
    self.dashboard_panel.draw(...)
    self.specialist_roster.draw(...)  # ALSO renders - WRONG
    self.incident_queue.draw(...)      # ALSO renders - WRONG
```

**Fix**: Use conditional rendering based on active_tab

### ❌ Mistake 2: Duplicate component instances
```python
# WRONG
self.roster_dashboard = SpecialistRosterPanel(...)
self.roster_operations = SpecialistRosterPanel(...)  # Duplicate - WRONG
```

**Fix**: Single instance `self.specialist_roster`, configure in render methods

### ❌ Mistake 3: Missing type hints
```python
# WRONG
def _render_dashboard_tab():  # No type hints
    pass

# RIGHT
def _render_dashboard_tab(self) -> None:
    pass
```

**Fix**: Add `-> None` for all render methods, type all parameters

### ❌ Mistake 4: Missing docstrings
```python
# WRONG
def _on_data_changed(self, event):
    self.logger.debug(...)

# RIGHT
def _on_data_changed(self, event) -> None:
    """Handle data change events. Next render() reads fresh game_state."""
    self.logger.debug(f"[GAME_UI] Data changed: {event.type}")
```

**Fix**: Add docstrings to ALL methods

### ❌ Mistake 5: Modifying state in UI
```python
# WRONG
def _on_assign_clicked():
    specialist.available = False  # Modifying state - WRONG
    specialist.xp += 50

# RIGHT
def _on_assign_clicked():
    self.event_bus.publish("action:assign_specialist", ...)  # Event only
```

**Fix**: Publish events, let game systems handle logic

### ❌ Mistake 6: No logging
```python
# WRONG
def render(self):
    # No logging of what's happening
    self._render_dashboard_tab()

# RIGHT
def render(self):
    self.logger.debug(f"[GAME_UI] Rendering tab: {self.active_tab}")
    self._render_dashboard_tab()
```

**Fix**: Add logging at DEBUG (flow) and INFO (important events) levels

---

## CODE PATTERNS TO COPY

### Pattern 1: Render Method

```python
def _render_dashboard_tab(self) -> None:
    """Render dashboard tab - overview from all system UIProviders.
    
    Displays summary widgets from each plugin. One widget per system.
    """
    if self.dashboard_panel and self.dashboard_manager:
        self.dashboard_panel.draw(self.screen, self.game_state)
        self.logger.debug(f"[GAME_UI] Rendered dashboard tab")
```

### Pattern 2: Event Subscription

```python
def __init__(self, game_state):
    # ... existing code ...
    
    # Subscribe to data changes
    self.event_bus.subscribe("specialist_hired", self._on_data_changed)
    self.event_bus.subscribe("incident_assigned", self._on_data_changed)
    
    self.logger.info("[GAME_UI] Subscribed to data change events")
```

### Pattern 3: Event Publishing

```python
def _publish_specialist_action(self, action: str, specialist_id: str) -> None:
    """Publish specialist action event.
    
    Informs game systems that user took action on specialist.
    Game system handles the logic; UI reflects result next frame.
    """
    event_name = f"action:{action}_specialist"
    self.event_bus.publish(event_name, {
        "specialist_id": specialist_id
    }, source="game_ui")
    self.logger.info(f"[GAME_UI] Published {event_name} for specialist {specialist_id}")
```

---

## SUCCESS CRITERIA CHECK

Before declaring complete:

- [ ] **Tab Content Separation**: Each tab shows ONLY its content (test each tab)
- [ ] **No Duplication**: Same component not in multiple tabs (search code)
- [ ] **Event Publishing**: All actions publish events (check game.log)
- [ ] **Type Hints**: All methods have complete type hints (run type checker)
- [ ] **Docstrings**: All public methods have docstrings (check each method)
- [ ] **Logging**: Important events logged at INFO level (check game.log)
- [ ] **No Debug Code**: No print(), no TODO, no commented-out lines
- [ ] **Game Starts**: No errors on startup (run game, wait 5 seconds)
- [ ] **Quality Gate**: Pass 15-point gate (see core-standards.instructions.md)

---

## IF YOU GET STUCK

1. **Read the plan again**: `TAB_UI_IMPLEMENTATION_PLAN.md` section relevant to your current step
2. **Check guidelines**: `.github/instructions/ui-rendering.instructions.md`
3. **Look at existing code**: How do other methods in GameUI follow the patterns?
4. **Check game.log**: What errors are showing? Run `tail -50 logs/game.log`
5. **Verify syntax**: `python3 -m py_compile src/ui/game_ui.py`

---

## WHEN COMPLETE

1. Verify all success criteria met
2. Run full test: `python main.py --local-server` (wait 5 seconds, should see no errors)
3. Check game.log for proper logging
4. Verify tab switching works visually
5. Mark TAB_UI_IMPLEMENTATION_PLAN.md as COMPLETE

The game will have functional, properly separated tabs with event-driven architecture. 🎮

