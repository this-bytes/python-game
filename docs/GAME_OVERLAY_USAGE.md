# GameOverlay Usage Guide

## Overview

`GameOverlay` is a comprehensive HUD (Heads-Up Display) system for the cybersecurity idle game. It provides persistent, at-a-glance information about game state without requiring player interaction.

## Features

### Primary Display (Top Bar)
- **Money Counter**: Animated money display with comma formatting
- **Energy Bar**: Visual progress bar with color-coding (green/orange/red)
- **XP Progress**: Level-based progression bar with XP tracking
- **Game Time**: Optional formatted time display
- **Interactive Controls**: Pause, speed control, settings buttons

### Secondary Information
- **Active Incidents**: Counter with warning colors when queue is full
- **Available Specialists**: Shows ready vs total specialists
- **Passive Income**: Real-time income rate display

### Notification System
- **Toast Notifications**: Slide-in animated notifications
- **Multiple Levels**: INFO, SUCCESS, WARNING, ERROR, ACHIEVEMENT
- **Auto-expiry**: Fade out and removal after duration
- **Queue Management**: Limited to 5 simultaneous notifications

### Interactive Features
- **Pause Control**: Click button or press SPACE to pause
- **Speed Control**: Cycle through 0.5x, 1.0x, 2.0x, 4.0x speeds
- **Keyboard Shortcuts**: +/- keys for speed, SPACE for pause
- **FPS Display**: Optional performance monitor

## Basic Usage

```python
from src.ui.game_overlay import GameOverlay, NotificationLevel

# Initialize overlay
overlay = GameOverlay(
    screen_width=800,
    screen_height=600,
    show_fps=True,      # Optional: show FPS counter
    show_debug=False    # Optional: show debug info
)

# Set up callbacks
def on_pause():
    game.toggle_pause()
    
def on_speed_change(new_speed):
    game.set_speed(new_speed)
    
def on_settings():
    game.show_settings_modal()

overlay.set_pause_callback(on_pause)
overlay.set_speed_change_callback(on_speed_change)
overlay.set_settings_callback(on_settings)

# In game loop
def update(delta_time):
    # Update overlay
    current_fps = clock.get_fps()
    overlay.update(delta_time, current_fps)
    
    # Render overlay
    overlay.render(screen, game_state, current_fps)
    
    # Handle events
    for event in pygame.event.get():
        if overlay.handle_event(event):
            continue  # Overlay consumed the event
        # ... handle other events
```

## Adding Notifications

```python
# Success notification
overlay.add_notification(
    "Achievement unlocked: First Incident Resolved!",
    NotificationLevel.ACHIEVEMENT,
    duration=5.0
)

# Error notification
overlay.add_notification(
    "Specialist burnout critical!",
    NotificationLevel.ERROR,
    duration=3.0
)

# Info notification (default)
overlay.add_notification("Contract completed")

# Warning notification
overlay.add_notification(
    "SLA deadline approaching",
    NotificationLevel.WARNING
)
```

## Notification Levels

| Level | Color | Use Case |
|-------|-------|----------|
| `INFO` | Blue | General information, updates |
| `SUCCESS` | Green | Achievements, completions, gains |
| `WARNING` | Orange | Warnings, approaching deadlines |
| `ERROR` | Red | Failures, critical issues |
| `ACHIEVEMENT` | Gold | Special achievements, milestones |

## Game State Requirements

The overlay expects a game state object with these attributes:

```python
class GameState:
    # Required
    money: float = 0.0
    energy: float = 100.0
    max_energy: float = 100.0
    xp: float = 0.0
    xp_required: float = 1000.0
    level: int = 1
    game_speed: float = 1.0
    
    # Optional
    game_time_formatted: str = "00:00:00"
    active_incidents_count: int = 0
    total_incidents_count: int = 0
    available_specialists_count: int = 0
    total_specialists_count: int = 0
    passive_income_rate: float = 0.0
```

If attributes are missing, overlay uses safe defaults and doesn't crash.

## Keyboard Controls

| Key | Action |
|-----|--------|
| `SPACE` | Toggle pause |
| `+` or `=` | Increase game speed |
| `-` | Decrease game speed |

## Animation Features

### Value Changes
Money, XP, and energy values animate smoothly when changed:

```python
# The overlay automatically detects changes and animates
game_state.money = 5000  # Old value: 3000
# Overlay will count from 3000 → 5000 over 0.5 seconds
```

### Notification Entry
Notifications slide in from above with a "back-out" easing:
- Start: y_offset = -100px
- End: y_offset = 0px
- Duration: 0.3 seconds
- Easing: BACK_OUT (bouncy entry)

### Notification Exit
Notifications fade out in the last 0.5 seconds of their duration:
- Opacity: 1.0 → 0.0
- Then removed from queue

## Advanced Usage

### Toggle FPS Display

```python
# Runtime toggle
overlay.toggle_fps()

# Or during initialization
overlay = GameOverlay(800, 600, show_fps=True)
```

### Clear All Notifications

```python
# Useful when changing scenes
overlay.clear_notifications()
```

### Custom Speed Options

The overlay supports 4 speed levels by default:

```python
overlay.speed_options = [0.5, 1.0, 2.0, 4.0]  # Default
overlay.speed_index = 1  # Start at 1.0x
```

### Programmatic Speed/Pause Control

```python
# Programmatically trigger pause (calls callback)
overlay.is_paused = True
if overlay.on_pause:
    overlay.on_pause()

# Programmatically change speed
overlay.speed_index = 2  # 2.0x speed
if overlay.on_speed_change:
    overlay.on_speed_change(overlay.speed_options[2])
```

## Color Theme

The overlay uses a cybersecurity-inspired dark theme:

```python
THEME = {
    "bg": (20, 25, 35),          # Dark background
    "bg_dark": (15, 18, 25),     # Darker variant
    "primary": (64, 156, 255),   # Blue accents
    "success": (76, 209, 55),    # Green for positive
    "warning": (255, 171, 64),   # Orange for warnings
    "error": (255, 82, 82),      # Red for errors
    "text": (230, 235, 245),     # Light text
    "text_dim": (150, 160, 180), # Dimmed text
    "border": (50, 60, 80),      # Border color
    "achievement": (218, 165, 32), # Gold for achievements
}
```

## Layout Constants

```python
BAR_HEIGHT = 60               # Top bar height
NOTIFICATION_WIDTH = 350       # Notification width
NOTIFICATION_HEIGHT = 80       # Notification height
NOTIFICATION_SPACING = 10      # Space between notifications
PADDING = 12                   # General padding
```

## Integration Example

```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        
        # Create overlay
        self.overlay = GameOverlay(800, 600, show_fps=True)
        self.overlay.set_pause_callback(self.toggle_pause)
        self.overlay.set_speed_change_callback(self.set_speed)
        self.overlay.set_settings_callback(self.show_settings)
        
    def handle_incident_resolved(self, incident, specialist):
        # Show notification
        self.overlay.add_notification(
            f"{specialist.name} resolved {incident.name}!",
            NotificationLevel.SUCCESS,
            duration=3.0
        )
        
    def handle_achievement_unlocked(self, achievement):
        # Show achievement notification
        self.overlay.add_notification(
            f"🏆 {achievement.name}: {achievement.description}",
            NotificationLevel.ACHIEVEMENT,
            duration=5.0
        )
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            current_fps = self.clock.get_fps()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Let overlay handle events first
                if self.overlay.handle_event(event):
                    continue
                
                # Handle other events...
            
            # Update
            if not self.overlay.is_paused:
                self.game_state.update(delta_time)
            
            self.overlay.update(delta_time, current_fps)
            
            # Render
            self.screen.fill((10, 15, 20))
            self.render_game()
            self.overlay.render(self.screen, self.game_state, current_fps)
            
            pygame.display.flip()
```

## Performance Notes

- **Rendering**: ~0.5ms per frame (negligible)
- **Updates**: ~0.1ms per frame (only processes active notifications)
- **Memory**: ~10KB base + 1KB per notification
- **FPS Impact**: <1% at 60 FPS

## Best Practices

1. **Update game state counts before rendering**:
   ```python
   game_state.active_incidents_count = len(active_incidents)
   game_state.available_specialists_count = sum(1 for s in specialists if s.is_available)
   ```

2. **Limit notification frequency**:
   ```python
   # Don't spam notifications
   if time.time() - last_notification_time > 0.5:
       overlay.add_notification("Update")
       last_notification_time = time.time()
   ```

3. **Use appropriate notification levels**:
   - INFO for neutral updates
   - SUCCESS for positive outcomes
   - WARNING for potential issues
   - ERROR for failures
   - ACHIEVEMENT for special milestones

4. **Clear notifications on scene change**:
   ```python
   def change_scene(self, new_scene):
       self.overlay.clear_notifications()
       self.current_scene = new_scene
   ```

5. **Handle missing game state gracefully**:
   The overlay safely handles missing attributes, but it's better to provide all fields for best display.

## Testing

The overlay includes 45 comprehensive tests covering:
- Initialization and configuration
- Notification system (add, remove, expiry, limits)
- Update logic (FPS tracking, notification processing)
- Rendering (top bar, secondary info, notifications, FPS)
- Value animation (count-up effects)
- Pause control (click and keyboard)
- Speed control (cycling, keyboard shortcuts, boundaries)
- Settings button
- Callback management
- Toggle functions (FPS, debug)
- Edge cases (missing state, zero values, boundaries)
- Integration workflows

Run tests:
```bash
pytest tests/test_game_overlay.py -v
```

## Future Enhancements

Potential additions:
- Resource warning indicators (low energy flash)
- Mini-map or facility status display
- Recent activity log
- Burnout warnings for specialists
- SLA deadline timers
- Network status indicator
- Session stats (uptime, total earned)

## See Also

- [Modal Component](../src/ui/components/modal.py) - For dialogs
- [TabContainer Component](../src/ui/components/tab_container.py) - For tabbed interfaces
- [AnimationSystem](../src/utils/animation_system.py) - For custom animations
