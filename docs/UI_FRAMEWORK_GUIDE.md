# Extensible UI Framework Guide

## Overview

The UI framework provides a plugin-based architecture for game systems to display dashboard summaries and detail panels. Built entirely on existing systems (EventBus, GameSystem, LayerManager, ModalManager), the framework enables zero-coupling between UI and game logic while allowing infinite extensibility.

**Core Principle**: "UI shows state, game logic sets state" - HARD architectural rule. UI is a **LISTENER**, not a **CONTROLLER**. Zero mixing of concerns allowed.

## Architecture

### Components

1. **UIProvider** (`src/ui/ui_provider.py`)
   - Abstract base class that game plugins can optionally implement
   - Two methods: `get_dashboard_summary()` and `get_detail_panel_data()`
   - Both are DISPLAY-ONLY - they read game_state but never mutate it

2. **DashboardManager** (`src/ui/dashboard_manager.py`)
   - Discovers all plugins that implement UIProvider
   - Collects dashboard summaries from all UIProviders every frame
   - Manages expanded detail panel state
   - Routes action button clicks to EventBus with "action:" prefix

3. **GameUI** (`src/ui/game_ui.py`)
   - Main Pygame rendering loop
   - Initialized with system_manager for dashboard integration
   - Renders dashboard overlay with all summaries
   - Handles dashboard widget clicks and opens modals

### Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Game Logic (Plugins)                                        │
│                                                             │
│ - Sets game state                                          │
│ - Publishes events on EventBus                             │
│ - Subscribes to action: events                             │
│ - Executes actions, publishes results back                 │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Publishes "action:" events
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ UI (Listeners Only)                                         │
│                                                             │
│ - Reads game_state (via UIProvider methods)                │
│ - Renders dashboard summaries                              │
│ - Renders detail panels from plugin data                   │
│ - User clicks button → publishes "action:" event           │
│ - UI never mutates game state directly                     │
└─────────────────────────────────────────────────────────────┘
```

## Using the UI Framework

### Step 1: Make Your Plugin Implement UIProvider

```python
from src.ui.ui_provider import UIProvider, UISummaryItem, UIPanelSection

class MyPlugin(GameSystem, UIProvider):
    """My game system with UI."""
    
    def __init__(self):
        super().__init__()
        self.name = "MyPlugin"
```

### Step 2: Implement get_dashboard_summary()

This method returns a dashboard widget - quick stats visible all the time.

```python
def get_dashboard_summary(self, game_state: GameState) -> UISummaryItem:
    """Get dashboard summary widget.
    
    Returns 4 lines of key metrics displayed on persistent overlay.
    """
    # Read game_state ONLY - never mutate
    active_count = len(self.get_active_items())
    total_value = sum(item.value for item in self.get_active_items())
    
    return UISummaryItem(
        title="My System",
        icon="⚙️",
        lines=[
            f"Active: {active_count}",
            f"Total: ${total_value:,.0f}",
            f"Status: OK",
        ],
        accent_color="green",
        data={"active": active_count, "total": total_value}
    )
```

**Key Points**:
- ✅ Return `UISummaryItem` with title, icon, lines (up to 4), and color
- ✅ Read game_state only, NEVER mutate it
- ✅ Include `data` dict with any extra info
- ❌ No business logic, no event publishing, no updates

### Step 3: Implement get_detail_panel_data()

This method returns detailed information for expanded modal view.

```python
def get_detail_panel_data(self, game_state: GameState) -> Dict[str, Any]:
    """Get detail panel data for expanded modal view.
    
    Returns structured data for rendering in modal with clickable items.
    """
    items = []
    for item in self.get_active_items():
        items.append(
            UISectionItem(
                name=item.name,
                details=[
                    f"Value: ${item.value:,.0f}",
                    f"Status: {item.status}",
                    f"Active: {item.is_active}",
                ],
                clickable=True,
                data={"item_id": item.id}
            )
        )
    
    return {
        "title": "My System Details",
        "sections": [
            UIPanelSection(
                title=f"Items ({len(items)})",
                items=items,
                section_type="list"
            )
        ]
    }
```

**Key Points**:
- ✅ Return dict with `title` and `sections`
- ✅ Create `UIPanelSection` for each logical group
- ✅ Add `UISectionItem` for each clickable item
- ✅ Include `clickable=True` if item can be interacted with
- ✅ Store `data` for identifying which item was clicked
- ❌ No rendering code, no Pygame calls

### Step 4: Subscribe to Action Events

Player clicks items → DashboardManager publishes "action:" events → your plugin listens.

```python
def initialize(self, game_state: GameState) -> None:
    """Initialize plugin."""
    super().initialize(game_state)
    
    # Subscribe to action events from detail panel clicks
    self.event_bus.subscribe(
        "action:my_system_item_selected",
        self._on_item_selected
    )

def _on_item_selected(self, event):
    """Handle player clicking an item in detail panel."""
    item_id = event.data.get("item_id")
    item = self.get_item_by_id(item_id)
    
    if item:
        logger.info(f"Player selected item: {item.name}")
        # Execute business logic
        self.activate_item(item)
```

**Event Pattern**: `"action:{action_id}"`
- When player clicks item in detail panel with `data={"item_id": "123"}`
- DashboardManager publishes: `"action:my_system_item_selected"` with that data
- Your plugin listens and executes logic

## Real Example: ClientPlugin

See `src/core/plugins/client_plugin.py` for full working example.

**Dashboard Summary**:
```
🏢 Clients
Active: 5
Revenue: $125,000/month
Avg Satisfaction: 85%
```

**Detail Panel**:
- List of all active clients
- Each shows: company name, industry, contract value, satisfaction bar
- Clickable items with `client_id` in data
- Plugin subscribes to `action:client_selected` events

## Key Rules

### ✅ DO

1. **Read Game State Only** in UIProvider methods
   - Both methods have `game_state` parameter
   - Use it to calculate display data
   - Never call `game_state.modify()` or similar

2. **Return Structured Data**
   - UISummaryItem for dashboard widget
   - Dict with sections/items for detail panel
   - Always include descriptive text and icons

3. **Use Existing Systems**
   - EventBus for action events (already initialized)
   - ModalManager renders detail panel (no new code needed)
   - LayerManager handles z-ordering (automatic)

4. **Subscribe to Action Events**
   - Pattern: `"action:{my_action_id}"`
   - Execute business logic in event handler
   - Publish results back on EventBus for UI feedback

### ❌ DON'T

1. **Never Mutate Game State in UI Methods**
   - get_dashboard_summary() is read-only
   - get_detail_panel_data() is read-only
   - Mutations must happen in event handlers

2. **Never Import Pygame in Game Logic**
   - Game plugins stay in `/src/core/plugins/`
   - UI stays in `/src/ui/`
   - Never mix the two

3. **Never Create New Systems**
   - Use EventBus for communication (exists)
   - Use existing GameSystem base (exists)
   - Extend only what's already there

4. **Never Hardcode UI Strings**
   - All text should come from game data
   - All icons should be configurable emojis
   - All colors should be named (green, yellow, red)

## Testing

### Unit Test Example

```python
def test_get_dashboard_summary():
    """Test dashboard summary display-only."""
    plugin = MyPlugin()
    game_state = create_test_game_state()
    
    summary = plugin.get_dashboard_summary(game_state)
    
    # Verify structure
    assert summary.title == "My System"
    assert len(summary.lines) <= 4
    assert summary.icon == "⚙️"
    
    # Verify game_state unchanged
    original_state = game_state.to_dict()
    plugin.get_dashboard_summary(game_state)
    assert game_state.to_dict() == original_state  # No mutations
```

### Integration Test Example

```python
def test_action_event_handling():
    """Test action events from detail panel."""
    plugin = MyPlugin()
    game_state = create_test_game_state()
    plugin.initialize(game_state)
    
    # Simulate player clicking item in detail panel
    event_bus = get_event_bus()
    event_bus.publish(
        "action:my_system_item_selected",
        {"item_id": "test_item"}
    )
    
    # Verify plugin handled action
    assert plugin.last_selected_item_id == "test_item"
```

## Adding a New Game System with UI

1. Create plugin in `/src/core/plugins/my_plugin.py`
2. Make it inherit from `GameSystem, UIProvider`
3. Implement `get_dashboard_summary()` - returns key metrics
4. Implement `get_detail_panel_data()` - returns detailed list
5. Subscribe to action events in `initialize()`
6. Handle clicks, update game state, publish results
7. Profit! 🎉

The dashboard automatically discovers your plugin and adds widget on next frame. No GameUI changes needed. No rendering code needed. Pure data-driven extensibility.

## FAQ

**Q: Can I have more than 4 lines in dashboard summary?**
A: No - keep it to key metrics only. If you need more, use detail panel.

**Q: Can I render custom graphics in UIProvider methods?**
A: No - return data structures only. Rendering happens in GameUI.

**Q: What if I want to show different data per game mode?**
A: Check game_state mode in get_dashboard_summary() and return different UISummaryItem.

**Q: Can I have nested sections in detail panel?**
A: Not yet - currently single level of sections with items. Can extend later.

**Q: What if plugin doesn't implement UIProvider?**
A: That's OK - not all plugins need UI. Just leave it off.

**Q: How do I debug UI display issues?**
A: Add logger.debug() calls to UIProvider methods. DashboardManager logs all errors.

## Performance Notes

- DashboardManager queries all UIProviders every frame
- Each `get_dashboard_summary()` call should be <1ms
- Detail panels only computed when expanded (lazy load)
- All data is garbage-collected after each frame (no memory leaks)

## See Also

- `src/ui/ui_provider.py` - UIProvider abstract base class
- `src/ui/dashboard_manager.py` - Dashboard aggregator and event router
- `src/core/plugins/client_plugin.py` - Working example implementation
- `src/ui/game_ui.py` - Main rendering loop integration (search for dashboard_manager)

