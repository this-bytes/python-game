# Main Menu and Startup Modes

This document describes the main menu system and extensible startup modes for the Cybersecurity Firm game.

## Overview

The game now features a main menu that appears on startup (by default) and supports multiple startup modes through command-line arguments. This provides flexibility for both normal gameplay and development/testing scenarios.

## Main Menu

The main menu provides the following options:

- **🎮 Start New Game**: Begin a fresh game with default settings
- **▶️ Continue**: Resume from the most recent auto-save (disabled if no save exists)
- **📚 Tutorial**: Start tutorial mode with guided gameplay for new players
- **⚙️ Settings**: Access game settings (placeholder for future implementation)
- **❌ Exit**: Close the game

### Keyboard Shortcuts

- **ENTER**: Quick start (continues if save exists, otherwise starts new game)
- **ESC**: Exit the game

## Command-Line Arguments

The game supports several command-line arguments for flexible startup:

### Startup Modes

```bash
# Show main menu (default)
python src/main.py
python src/main.py --menu

# Start a new game directly (skip menu)
python src/main.py --new-game

# Start tutorial mode for new players
python src/main.py --tutorial

# Continue from most recent save
python src/main.py --continue

# Load from specific save slot (0-9)
python src/main.py --load-slot 3
```

### Additional Options

```bash
# Enable debug mode
python src/main.py --debug

# Run headless (no UI, for testing/backend only)
python src/main.py --headless

# Skip intro animations
python src/main.py --skip-intro
```

### Combined Options

Arguments can be combined:

```bash
# Start new game in debug mode
python src/main.py --new-game --debug

# Continue with debug mode and skip intro
python src/main.py --continue --debug --skip-intro
```

## Architecture

### GameArgs System

The `GameArgs` class in `src/utils/game_args.py` provides an extensible parameter system for game startup:

```python
class GameArgs:
    """Parsed game arguments and configuration."""
    
    def __init__(
        self,
        mode: GameMode = GameMode.MENU,
        save_slot: Optional[int] = None,
        debug: bool = False,
        headless: bool = False,
        skip_intro: bool = False
    ):
        ...
```

### Game Modes

Available game modes (defined in `GameMode` enum):

- `MENU`: Show main menu (default)
- `NEW_GAME`: Start new game directly
- `TUTORIAL`: Start tutorial mode with guided gameplay
- `CONTINUE`: Continue from auto-save (slot 0)
- `LOAD_SLOT`: Load from specific save slot
- `LOAD_SLOT`: Load from specific save slot

### Main Menu UI

The `MainMenu` class in `src/ui/main_menu.py` handles the visual menu:

- Uses Pygame for rendering
- Integrates with the theme system
- Provides button-based navigation
- Checks save availability for the Continue option

## Auto-Save Feature

The game automatically saves to slot 0 when:

- The game is shut down normally
- The player exits from the main menu

This ensures that the "Continue" option is always available if you've played the game before.

## Extending the System

### Adding New Startup Modes

To add a new startup mode:

1. Add the mode to the `GameMode` enum in `src/utils/game_args.py`
2. Add the corresponding argument in `parse_game_args()`
3. Handle the mode in `Game.initialize()` in `src/main.py`

Example:

```python
# In GameMode enum
class GameMode(Enum):
    ...
    TUTORIAL = "tutorial"  # New mode

# In parse_game_args()
parser.add_argument(
    "--tutorial",
    action="store_true",
    help="Start tutorial mode"
)

# In Game.initialize()
elif self.args.mode == GameMode.TUTORIAL:
    return self._initialize_tutorial()
```

### Adding New Arguments

To add new command-line arguments:

1. Add the argument to `GameArgs.__init__()` parameters
2. Add the argument to `parse_game_args()` parser
3. Use the argument value in game initialization logic

Example:

```python
# In GameArgs.__init__()
def __init__(
    self,
    ...
    fast_start: bool = False  # New argument
):
    self.fast_start = fast_start

# In parse_game_args()
parser.add_argument(
    "--fast-start",
    action="store_true",
    help="Skip loading screens"
)

# Use in game code
if self.args.fast_start:
    self.skip_loading_screens()
```

## Testing

Tests are provided for both the argument system and main menu:

```bash
# Run all new tests
python -m pytest tests/test_game_args.py tests/test_main_menu.py -v

# Test argument parsing
python -m pytest tests/test_game_args.py -v

# Test main menu
python -m pytest tests/test_main_menu.py -v
```

## Future Enhancements

Planned improvements for the menu system:

1. **Settings Menu**: Full implementation with options for:
   - Audio settings (volume, music on/off)
   - Graphics settings (resolution, fullscreen, vsync)
   - Gameplay settings (difficulty, auto-save interval)
   - Control bindings

2. **Save Slot Selection**: Visual save slot browser showing:
   - Save metadata (timestamp, playtime, progress)
   - Screenshot thumbnails
   - Delete/rename save options

3. **Menu Animations**: Enhanced visual polish:
   - Smooth transitions between menu and game
   - Animated backgrounds
   - Sound effects for menu interactions

4. **Achievements Display**: Show recent achievements on the menu

5. **News/Updates**: Display patch notes or game news on startup
