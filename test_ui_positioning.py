#!/usr/bin/env python3
"""Quick UI test to verify panels are positioned and visible."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.game_ui import GameUI
from src.models.game_state import GameState
from src.ui.view_manager import ViewManager
from src.ui.layout_manager import LayoutManager
from src.ui.drag_drop_manager import DragDropManager

def test_ui_positioning():
    """Test that UI panels are properly positioned."""
    print("Testing UI positioning...")

    # Create minimal game state
    game_state = GameState()
    game_state.initialize_new_game()

    # Create UI components
    view_manager = ViewManager()
    layout_manager = LayoutManager()
    drag_drop_manager = DragDropManager()

    # Create game UI
    game_ui = GameUI(game_state, view_manager, layout_manager, drag_drop_manager)

    # Check that panels exist and have positions
    operations_panels = view_manager.get_panels_for_view("Operations")

    print(f"Found {len(operations_panels)} panels in Operations view:")

    for panel in operations_panels:
        print(f"  - {panel.title}: position={panel.position}, size={panel.size}, visible={panel.visible}")

        # Check positioning
        if "Specialist Roster" in panel.title:
            expected_x = 220  # navigation (200) + margin (20)
            if panel.position[0] == expected_x:
                print("    ✓ Specialist Roster positioned correctly")
            else:
                print(f"    ✗ Specialist Roster X position should be {expected_x}, got {panel.position[0]}")

        elif "Active Incidents" in panel.title:
            expected_x = 640  # navigation (200) + specialist panel (380) + margins (40) + gap (20)
            if panel.position[0] == expected_x:
                print("    ✓ Incident Queue positioned correctly")
            else:
                print(f"    ✗ Incident Queue X position should be {expected_x}, got {panel.position[0]}")

    print("UI positioning test complete!")

if __name__ == "__main__":
    test_ui_positioning()