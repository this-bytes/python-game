---
applyTo: "src/ui/**/*.py"

---

# UI Rendering Order - Instructions

This instruction file documents the required rendering contract for scrollable panels in the game UI and establishes a small regression test to ensure future agents and contributors keep the behavior.

Goal:
- Prevent scroll container backgrounds and scrollbars from over-drawing panel content (cards, lists, previews).
- Provide a concise, testable contract for rendering order used by all panels that embed a `ScrollContainer`.

Rendering contract (MANDATORY):

1. Panels must call `scroll_container.render_background(screen)` before rendering any content that should appear above the scroll background.
2. Panels must render their scrollable content while the Pygame clipping rect is set to the content area (use `screen.set_clip(content_rect)`), so the content clips correctly to the container.
3. After content is drawn and the clipping region reset (e.g. `screen.set_clip(None)`), panels must call `scroll_container.render_scrollbar(screen)` to draw the scrollbar and handle as an overlay on top of content.

Rationale:
- Separating background and scrollbar drawing prevents z-order issues where the scroll bar or background could be drawn on top of content, hiding it. This is particularly important for drag previews and semi-transparent overlays.

Code example:

```py
# In Panel.render_content(...):
self.scroll_container.position = (content_rect.x, content_rect.y)
self.scroll_container.size = (content_rect.width, content_rect.height)
self.scroll_container.set_content_height(total_content_height)

# 1) Draw background
self.scroll_container.render_background(screen)

# 2) Clip and draw content
screen.set_clip(content_rect)
# draw cards, lists, images ...
screen.set_clip(None)

# 3) Draw scrollbar overlay
self.scroll_container.render_scrollbar(screen)
```

Testing guidance (MANDATORY):
- Add unit tests that mock or spy on the `ScrollContainer` used by panels and verify that `render_background` is called before content rendering and `render_scrollbar` is called after.
- Integration tests should include a headless screenshot (if available) that asserts that the pixel area for cards is not fully identical to the background color (i.e., content is visible).

Acceptance criteria for changes:
- `SpecialistRosterPanel` and `IncidentQueuePanel` follow the contract (already updated in `src/ui/panels/`).
- - A regression test exists under `tests/test_ui_render_order.py` and passes.

---

# TAB-BASED UI ARCHITECTURE - Instructions

## Core Principle: Screen Separation of Concerns

Each tab is a distinct screen that renders ONE subsystem view. Only the active tab's content renders per frame.

### Tab Structure

| Tab | Purpose | Components | Data Source |
|-----|---------|-----------|-------------|
| Dashboard | System overview | UIProvider widgets from all plugins | `game_state + plugin UIProvider` |
| Operations | Specialist management | SpecialistRosterPanel with hire/fire | `game_state.specialists` |
| Incidents | Incident dispatch | IncidentQueuePanel with assignment | `game_state.incidents` (unassigned) |
| Specialists | Team view | Alternative specialist display | `game_state.specialists` |
| Analytics | Metrics/statistics | Economy stats, achievement progress | `game_state + economy_plugin` |

## Tab Rendering Pattern

```python
class GameUI:
    """Main UI manager - tab-based screen separation."""
    
    def render(self) -> None:
        """Render only current tab content."""
        # Background and always-visible elements
        self.screen.fill(self.bg_color)
        self.tab_bar.draw(self.screen)
        self.hud_overlay.draw(self.screen, self.game_state, self.active_tab.capitalize())
        
        # ONLY render active tab's content
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
        
        # Always-on-top elements (modals, notifications)
        self.quick_reference.render(self.screen)
        self.detail_panel_renderer.render(self.screen)  # If modal open
        self.notification_manager.draw(self.screen)
    
    def _render_dashboard_tab(self) -> None:
        """Render dashboard tab - overview from all system UIProviders."""
        if self.dashboard_panel and self.dashboard_manager:
            self.dashboard_panel.draw(self.screen, self.game_state)
    
    def _render_operations_tab(self) -> None:
        """Render operations tab - specialist management."""
        self.specialist_roster.draw(self.screen, self.game_state.specialists)
    
    def _render_incidents_tab(self) -> None:
        """Render incidents tab - incident dispatch."""
        unassigned = [i for i in self.game_state.incidents if not i.assigned_specialist_id]
        self.incident_queue.draw(self.screen, unassigned, self.game_state)
```

**Pattern Requirements**:
- ✅ One render method per tab
- ✅ Only ONE tab renders per frame
- ✅ Each method calls existing UI components (no rendering logic in GameUI)
- ✅ No component duplication across tabs
- ✅ Data from game_state (direct reads, no caching)

## Event-Driven Tab Updates

### Tab Click Publishing

When user clicks tab, publish event to EventBus:

```python
# In GameUI.handle_input():
if self.tab_bar.handle_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.active_tab = self.tab_bar.active_tab_id
        self.event_bus.publish("ui_tab_changed", {
            "tab_id": self.active_tab
        }, source="game_ui")
        self.logger.info(f"[GAME_UI] Tab changed to: {self.active_tab}")
    return
```

### Data Change Subscriptions

GameUI subscribes to important data changes:

```python
def __init__(self, game_state):
    # Subscribe to data changes
    self.event_bus.subscribe("specialist_hired", self._on_data_changed)
    self.event_bus.subscribe("specialist_fired", self._on_data_changed)
    self.event_bus.subscribe("incident_assigned", self._on_data_changed)
    self.event_bus.subscribe("incident_completed", self._on_data_changed)

def _on_data_changed(self, event) -> None:
    """Data changed. Next render() will read fresh game_state."""
    self.logger.debug(f"[GAME_UI] Data changed: {event.type}")
```

### User Action Event Publishing

All UI actions publish "action:" events:

```python
def _publish_specialist_action(self, action: str, specialist_id: str) -> None:
    """Publish specialist action event."""
    event_name = f"action:{action}_specialist"
    self.event_bus.publish(event_name, {
        "specialist_id": specialist_id
    }, source="game_ui")
    self.logger.info(f"[GAME_UI] Published {event_name} for {specialist_id}")
```

## Component Reuse Patterns

### Pattern 1: Same Component in Multiple Tabs

If a component appears in multiple tabs (e.g., SpecialistRosterPanel in Operations and Specialists):

```python
# RIGHT - Single instance, configured per-tab
def __init__(self):
    self.specialist_roster = SpecialistRosterPanel(...)  # Single instance

def _render_operations_tab(self) -> None:
    self.specialist_roster.set_mode("full")  # Hire/fire buttons visible
    self.specialist_roster.draw(...)

def _render_specialists_tab(self) -> None:
    self.specialist_roster.set_mode("team")  # Different layout
    self.specialist_roster.draw(...)
```

**Pattern**: Single instance, configured per-tab rendering call. No duplication.

### Pattern 2: Component Only in One Tab

Some components only appear in one tab:

```python
# OK - Dedicated component
def __init__(self):
    self.incident_queue = IncidentQueuePanel(...)  # Only in incidents tab

def _render_incidents_tab(self) -> None:
    self.incident_queue.draw(self.screen, unassigned_incidents, self.game_state)
```

**Pattern**: Component initialized, only rendered when active_tab matches.

### Pattern 3: Plugin-Provided Dashboard Widgets

Dashboard shows UIProvider widgets from all plugins:

```python
def _render_dashboard_tab(self) -> None:
    """Render overview from all system UIProviders."""
    if self.dashboard_panel and self.dashboard_manager:
        self.dashboard_panel.draw(self.screen, self.game_state)

# DashboardPanel queries all plugins for their widgets
class DashboardPanel:
    def draw(self, screen, game_state):
        for plugin in game_state.system_manager.get_all_plugins():
            if hasattr(plugin, 'get_dashboard_summary'):
                summary = plugin.get_dashboard_summary(game_state)
                self._draw_widget(screen, summary)
```

**Pattern**: Dashboard queries plugins, each provides its widget data via UIProvider.

## Anti-Patterns to Avoid

### ❌ Hardcoded Tab Content

```python
# WRONG - ALL tabs render simultaneously
def render(self):
    self.dashboard_panel.draw(...)
    self.specialist_roster.draw(...)
    self.incident_queue.draw(...)
```

Problem: Tabs aren't visually distinct. Fix: Use conditional rendering.

### ❌ Component Duplication

```python
# WRONG - Multiple instances of same component
def __init__(self):
    self.roster_ops = SpecialistRosterPanel(...)  # Copy 1
    self.roster_spec = SpecialistRosterPanel(...)  # Copy 2
```

Problem: Sync issues, memory waste. Fix: Single instance, configured per-tab.

### ❌ Direct Game Logic in UI

```python
# WRONG - UI modifies state directly
def _on_assign_button_clicked(self):
    specialist.assigned_incident_id = incident_id  # BAD
    specialist.burnout += 5
```

Problem: Game logic in UI. Fix: Publish event, let game system handle.

## Testing UI Rendering

### Test Tab Content Isolation

```python
def test_dashboard_tab_renders_only_dashboard():
    """Verify dashboard tab shows only dashboard content."""
    game_ui = GameUI(game_state)
    game_ui.active_tab = "dashboard"
    
    # Track which components render
    dashboard_called = []
    roster_called = []
    
    game_ui.dashboard_panel.draw = lambda *a: dashboard_called.append(True)
    game_ui.specialist_roster.draw = lambda *a: roster_called.append(True)
    
    game_ui.render()
    
    assert len(dashboard_called) == 1
    assert len(roster_called) == 0  # Should NOT render in dashboard
```

### Test Event Publishing

```python
def test_tab_click_publishes_event():
    """Verify tab click publishes ui_tab_changed event."""
    game_ui = GameUI(game_state)
    events = []
    
    game_ui.event_bus.subscribe("ui_tab_changed", lambda e: events.append(e))
    
    # Simulate tab click
    game_ui.tab_bar.active_tab_id = "operations"
    # (trigger handle_input with tab click event)
    
    assert len(events) == 1
    assert events[0].data["tab_id"] == "operations"
```

## Logging Requirements

All UI code must log important actions:

```python
# DEBUG: Flow tracking
logger.debug(f"[GAME_UI] Rendering tab: {self.active_tab}")

# INFO: Important events (user actions, state changes)
logger.info(f"[GAME_UI] Tab changed to: {self.active_tab}")
logger.info(f"[GAME_UI] Published action:assign_specialist")

# WARNING: Unexpected but recoverable
logger.warning(f"[GAME_UI] Specialist {id} not found")

# ERROR: Problems needing attention
logger.error(f"[GAME_UI] Failed to render incidents tab: {error}")
```

**Pattern**: Prefix with `[GAME_UI]`, use appropriate level, include context/IDs.

---

## See Also

- [architecture.instructions.md](architecture.instructions.md) - Plugin system and EventBus
- [code-style.instructions.md](code-style.instructions.md) - Type hints and docstrings
- [core-standards.instructions.md](core-standards.instructions.md) - Quality standards
- [TAB_UI_IMPLEMENTATION_PLAN.md](../../TAB_UI_IMPLEMENTATION_PLAN.md) - Detailed implementation guide

````

When you modify scroll behavior or panel drawing, update this instruction and add/adjust tests accordingly.
