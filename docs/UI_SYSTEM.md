# UI Component System Documentation

## Overview

This document describes the new professional UI system implemented for the Cybersecurity Firm game. The system provides a rich, interactive interface with draggable panels, themes, notifications, and keyboard shortcuts.

## Architecture

### Component Hierarchy

```
GameUI (Main UI Controller)
├── ThemeManager (Singleton)
├── NotificationManager
├── HotkeyManager
└── Panels[]
    ├── SpecialistRosterPanel
    ├── IncidentQueuePanel
    └── MetricsPanel
```

### Key Design Principles

1. **Separation of Concerns**: UI components only render - they don't contain game logic
2. **Theme-Driven**: All colors and fonts come from the theme system
3. **Event-Driven**: User interactions generate events that are handled by the game loop
4. **Reusable Components**: All UI components can be used across different panels
5. **Z-Order Management**: Panels can be brought to front by clicking

## Components

### Base Components (`src/ui/components/`)

#### Panel
Base class for all window panels. Provides:
- Draggable title bar
- Minimize/maximize/close buttons
- Border and styling
- Content area for subclasses

**Usage:**
```python
from src.ui.components.panel import Panel

class MyPanel(Panel):
    def __init__(self):
        super().__init__(
            title="My Panel",
            position=(100, 100),
            size=(400, 300),
            draggable=True,
            minimizable=True,
            closeable=True
        )
    
    def render_content(self, screen, content_rect):
        # Render your content here
        pass
```

#### Button
Interactive button with multiple states and styles.

**Usage:**
```python
from src.ui.components.button import Button, ButtonStyle

button = Button(
    text="Click Me",
    position=(10, 10),
    size=(120, 40),
    callback=lambda: print("Clicked!"),
    style=ButtonStyle.PRIMARY
)

# In render loop
button.render(screen)

# In event loop
button.handle_event(event)
```

#### ProgressBar
Displays progress with optional label.

**Usage:**
```python
from src.ui.components.progress_bar import ProgressBar

progress = ProgressBar(
    position=(10, 10),
    size=(200, 20),
    value=75,
    max_value=100,
    show_label=True
)

progress.render(screen)
progress.set_value(50)  # Update progress
```

#### ScrollContainer
Scrollable content area with scroll bars.

**Usage:**
```python
from src.ui.components.scroll_container import ScrollContainer

scroll = ScrollContainer(
    position=(0, 0),
    size=(400, 500),
    content_height=1000  # Total content height
)

scroll.handle_event(event)  # Handle mouse wheel
offset = scroll.get_scroll_offset()  # Get scroll position
```

## Game Panels (`src/ui/panels/`)

### SpecialistRosterPanel
Displays all specialists in scrollable cards.

**Features:**
- Scrollable list of specialist cards
- Shows name, level, specialty, status, XP bar
- Click to select specialist
- Color-coded status (available/working/resting)

### IncidentQueuePanel
Displays active incidents with urgency indicators.

**Features:**
- Scrollable list of incident cards
- Shows type, difficulty, specialty, SLA, reward
- Color-coded urgency (green/yellow/red based on SLA)
- Click to select incident

### MetricsPanel
Displays game statistics and KPIs.

**Features:**
- 2x2 grid of KPI cards
- Large numbers with labels
- Additional metrics list
- Color-coded values

## Systems

### Theme System

**ThemeManager** (`src/ui/theme_manager.py`)
- Singleton pattern
- Loads themes from `data/themes.json`
- Provides color and font management
- Caches fonts for performance

**Creating a New Theme:**

Edit `data/themes.json`:
```json
{
  "themes": {
    "my_theme": {
      "name": "My Theme",
      "colors": {
        "primary": [0, 120, 215],
        "background": [20, 20, 30],
        "panel_bg": [30, 30, 45],
        "text": [220, 220, 230],
        "success": [0, 200, 100],
        "warning": [255, 200, 0],
        "danger": [255, 50, 50],
        "border": [60, 60, 80]
      },
      "fonts": {
        "title": 24,
        "normal": 14,
        "small": 10
      }
    }
  }
}
```

**Using Themes in Code:**
```python
theme_mgr = ThemeManager()
theme_mgr.load_theme("my_theme")

# Get colors
bg_color = theme_mgr.get_color("background")
text_color = theme_mgr.get_color("text")

# Get fonts
title_font = theme_mgr.get_font("title", bold=True)
normal_font = theme_mgr.get_font("normal")
```

### Notification System

**NotificationManager** (`src/ui/notification_system.py`)
- Toast-style notifications
- 4 types: info, success, warning, error
- Auto-dismiss with fade-out
- Stack management

**Usage:**
```python
notif_mgr = NotificationManager(screen_width, screen_height)

# Show notifications
notif_mgr.show_info("Title", "Message")
notif_mgr.show_success("Success!", "Operation completed")
notif_mgr.show_warning("Warning", "Check this")
notif_mgr.show_error("Error", "Something failed")

# In game loop
notif_mgr.update(delta_time)
notif_mgr.render(screen)
```

### Hotkey System

**HotkeyManager** (`src/ui/hotkey_manager.py`)
- Configurable keyboard shortcuts
- Action-based callbacks
- Rebindable keys

**Default Bindings:**
- `1-6`: Toggle panels
- `SPACE`: Pause/Resume
- `+/-`: Speed control
- `H`: Help overlay
- `ESC`: Close panels

**Usage:**
```python
hotkey_mgr = HotkeyManager()

# Register callback
hotkey_mgr.register_callback(
    HotkeyAction.PAUSE_TOGGLE,
    lambda: toggle_pause()
)

# Rebind key
hotkey_mgr.rebind_hotkey(
    HotkeyAction.PAUSE_TOGGLE,
    pygame.K_p  # Change pause to 'P' key
)

# In event loop
hotkey_mgr.handle_key_event(event)
```

## Integration Guide

### Adding a New Panel

1. **Create Panel Class:**
```python
# src/ui/panels/my_panel.py
from src.ui.components.panel import Panel

class MyPanel(Panel):
    def __init__(self, game_state):
        super().__init__(
            title="My Panel",
            position=(100, 100),
            size=(400, 300)
        )
        self.game_state = game_state
    
    def render_content(self, screen, content_rect):
        # Render your content
        pass
    
    def handle_event(self, event):
        # Handle events first in parent
        if super().handle_event(event):
            return True
        
        # Your event handling
        return False
```

2. **Add to Main UI:**
```python
# In GameUI.__init__()
self.my_panel = MyPanel(self.game_state)
self.panels.append(self.my_panel)

# Register hotkey
self.hotkey_manager.register_callback(
    HotkeyAction.TOGGLE_MY_PANEL,
    lambda: self._toggle_panel(self.my_panel)
)
```

### Adding a New Component

1. **Create Component File:**
```python
# src/ui/components/my_component.py
import pygame
from typing import Any

class MyComponent:
    def __init__(self, position, size):
        self.position = position
        self.size = size
    
    def render(self, screen: pygame.Surface):
        # Render component
        pass
    
    def handle_event(self, event: Any) -> bool:
        # Handle events
        return False
```

2. **Export in `__init__.py`:**
```python
# src/ui/components/__init__.py
from src.ui.components.my_component import MyComponent

__all__ = [..., "MyComponent"]
```

## Best Practices

### Rendering
- Always use theme colors instead of hardcoded values
- Use content_rect for positioning within panels
- Respect clipping regions when scrolling
- Cache surfaces when possible

### Event Handling
- Return True if event was consumed
- Handle events in reverse z-order (front panels first)
- Check visibility before processing events

### Performance
- Initialize fonts once, not every frame
- Use dirty rect updates when possible
- Limit number of visible panels
- Cache rendered surfaces for static content

### Theming
- Always use ThemeManager for colors
- Provide default values when getting colors
- Support all theme colors in custom components

## Troubleshooting

### Panel Not Visible
- Check `panel.visible` is True
- Ensure panel is in the `panels` list
- Verify position is within screen bounds

### Events Not Working
- Ensure event handler returns True when consumed
- Check z-order (front panels handle events first)
- Verify event type matches (MOUSEBUTTONDOWN, etc.)

### Theme Colors Not Applying
- Call `panel.set_theme_colors(theme_dict)` after theme change
- Ensure theme is loaded before creating panels
- Check theme JSON has all required color keys

### Performance Issues
- Reduce number of visible panels
- Use clipping regions for large lists
- Cache font objects
- Limit particles/animations

## Future Enhancements

Planned additions:
- Animation system with easing functions
- Particle effects system
- Audio system
- Tutorial system
- More panel types (Client, Automation, Shop)
- Layout manager for auto-positioning
- Drag-and-drop between panels
- Context menus
- Dialog boxes
- Tree views
- Tabs within panels

## Examples

### Complete Panel Example

See `src/ui/panels/specialist_roster_panel.py` for a complete example including:
- Scrollable content
- Click selection
- Progress bars
- Theme integration
- Event handling

### Complete Component Example

See `src/ui/components/button.py` for a complete example including:
- State management
- Multiple styles
- Callbacks
- Theme integration
- Event handling

## API Reference

See individual component files for detailed API documentation. All public methods include comprehensive docstrings.
