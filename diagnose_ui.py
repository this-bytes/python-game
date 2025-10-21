#!/usr/bin/env python3
"""Comprehensive UI diagnosis and screenshot capture tool."""

import sys
import os
import time
sys.path.insert(0, '/home/localadmin/code/python-game')

from src.models.game_state import GameState
from src.ui.game_ui import GameUI
from src.utils.logger import GameLogger
from src.utils.screenshot import initialize_screenshot_utility
import pygame

def take_diagnostic_screenshots():
    """Take screenshots of different UI states and analyze the layout."""
    print("=" * 80)
    print("DIAGNOSTIC UI ANALYSIS - TAKING SCREENSHOTS")
    print("=" * 80)

    # Create minimal game state
    game_state = GameState()

    # Create UI
    ui = GameUI(game_state)

    # Initialize screenshot utility
    logger = GameLogger("ui_diagnosis")
    screenshot_utility = initialize_screenshot_utility(ui, game_state, logger)
    ui.set_screenshot_utility(screenshot_utility)

    print("\n[1/5] Initial UI State - Default view")
    ui._take_screenshot()
    time.sleep(0.5)

    print("\n[2/5] Checking Panel Positions...")
    analyze_ui_layout(ui)

    print("\n[3/5] Toggling Specialist Panel")
    ui._toggle_panel(ui.specialist_roster_panel)
    ui._take_screenshot()
    time.sleep(0.5)

    print("\n[4/5] Toggling Incident Panel")
    ui._toggle_panel(ui.incident_queue_panel)
    ui._take_screenshot()
    time.sleep(0.5)

    print("\n[5/5] Toggling Metrics Panel")
    ui._toggle_panel(ui.metrics_panel)
    ui._take_screenshot()
    
    print("\n" + "=" * 80)
    print("SCREENSHOT ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nScreenshots saved to: /home/localadmin/code/python-game/screenshots/")
    print("\nUI Issues Identified:")
    report_ui_issues(ui)

def analyze_ui_layout(ui):
    """Analyze and report on the UI layout structure."""
    print("\n--- UI Layout Analysis ---")
    print(f"Screen Size: {ui.WINDOW_WIDTH}x{ui.WINDOW_HEIGHT}")
    print(f"Navigation Menu: {'Enabled' if ui.navigation_menu else 'Disabled'}")
    print(f"HUD Overlay: {'Enabled' if ui.hud_overlay else 'Disabled'}")
    print(f"Quick Reference: {'Enabled' if ui.quick_reference else 'Disabled'}")
    
    print("\nPanel States:")
    panels = [
        ("Specialist Roster", ui.specialist_roster_panel),
        ("Incident Queue", ui.incident_queue_panel),
        ("Metrics", ui.metrics_panel),
        ("Equipment Shop", ui.equipment_shop_panel),
        ("Equipment Inventory", ui.equipment_inventory_panel),
    ]
    
    for name, panel in panels:
        if hasattr(panel, 'visible'):
            print(f"  {name}: {'Visible' if panel.visible else 'Hidden'}")
        if hasattr(panel, 'rect'):
            print(f"    Position: ({panel.rect.x}, {panel.rect.y}) | Size: {panel.rect.width}x{panel.rect.height}")

def report_ui_issues(ui):
    """Report identified UI issues and provide recommendations."""
    issues = []
    
    # Check for overlapping panels
    visible_panels = []
    for panel in ui.panels:
        if hasattr(panel, 'visible') and panel.visible and hasattr(panel, 'rect'):
            visible_panels.append((panel.__class__.__name__, panel.rect))
    
    # Check overlaps
    for i, (name1, rect1) in enumerate(visible_panels):
        for name2, rect2 in visible_panels[i+1:]:
            if rect1.colliderect(rect2):
                issues.append(f"⚠️  OVERLAP: {name1} overlaps with {name2}")
    
    # Check for panels outside screen bounds
    for name, rect in visible_panels:
        if (rect.x < 0 or rect.y < 0 or 
            rect.x + rect.width > ui.WINDOW_WIDTH or 
            rect.y + rect.height > ui.WINDOW_HEIGHT):
            issues.append(f"⚠️  OUT OF BOUNDS: {name} partially outside screen")
    
    # Check for panels that are too large
    for name, rect in visible_panels:
        if rect.width > ui.WINDOW_WIDTH * 0.95 or rect.height > ui.WINDOW_HEIGHT * 0.95:
            issues.append(f"⚠️  TOO LARGE: {name} takes up too much screen space")
    
    # Check for missing visual feedback
    if not hasattr(ui, 'dopamine_overlay') or not ui.dopamine_overlay:
        issues.append("⚠️  MISSING: Dopamine feedback overlay not initialized")
    
    if not hasattr(ui, 'synergy_overlay') or not ui.synergy_overlay:
        issues.append("⚠️  MISSING: Synergy suggestion overlay not initialized")
    
    if not issues:
        issues.append("✅ No major layout issues detected")
    
    for issue in issues:
        print(f"  {issue}")

if __name__ == "__main__":
    try:
        take_diagnostic_screenshots()
        print("\n✅ Diagnostic analysis complete!")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)