"""Game User Interface using Pygame - Refactored with UIManager.

This module handles the main window and orchestrates UI components through a UIManager.
"""

import pygame
from typing import List, Optional, Any, Tuple
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.notification_system import NotificationManager
from src.ui.hotkey_manager import HotkeyManager, HotkeyAction
from src.ui.dashboard_manager import DashboardManager
from src.ui.dashboard_panel import DashboardPanel
from src.ui.components.hud_overlay import HUDOverlay
from src.ui.ui_manager import UIManager
from src.ui.components.detail_panel import DetailPanel
from src.core.event_bus import get_event_bus

@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict

class GameUI:
    """Main UI class handling Pygame rendering and input via a UIManager."""

    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720

    def __init__(self, game_state: GameState, system_manager=None):
        self.logger = GameLogger("game_ui")
        self.game_state = game_state
        self.system_manager = system_manager
        self.event_bus = get_event_bus()

        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")
        self.clock = pygame.time.Clock()

        self.theme_manager = ThemeManager()
        self.hotkey_manager = HotkeyManager()
        self.ui_manager = UIManager()

        # Screenshot utility (set by main.py)
        self.screenshot_utility = None

        if self.system_manager:
            self.dashboard_manager = DashboardManager(self.system_manager)
        else:
            self.dashboard_manager = None

        self._initialize_components()
        self._register_hotkey_callbacks()

        self.running = True
        self.logger.info("[GAME_UI] Game UI initialized (UIManager Framework)")

    def set_screenshot_utility(self, screenshot_utility):
        """Set the screenshot utility for hotkey callbacks.
        
        Args:
            screenshot_utility: ScreenshotUtility instance
        """
        self.screenshot_utility = screenshot_utility
        # Register screenshot callback now that utility is available
        if screenshot_utility:
            self.hotkey_manager.register_callback(HotkeyAction.TAKE_SCREENSHOT, self._take_screenshot)

    def _initialize_components(self):
        """Create and register all the base UI components."""
        # HUD
        hud = HUDOverlay(screen_width=self.WINDOW_WIDTH, screen_height=self.WINDOW_HEIGHT)
        self.ui_manager.push(hud)

        # Dashboard Panel
        if self.dashboard_manager:
            dashboard = DashboardPanel(x=10, y=70, on_widget_clicked=self._on_dashboard_widget_clicked)
            dashboard.set_managers(self.dashboard_manager, self.game_state)
            self.ui_manager.push(dashboard)
        
        # Notification Manager should be drawn on top of everything
        self.notification_manager = NotificationManager(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.ui_manager.push(self.notification_manager)

    def _register_hotkey_callbacks(self):
        self.hotkey_manager.register_callback(HotkeyAction.PAUSE_TOGGLE, self._toggle_pause)

    def _toggle_pause(self):
        self.game_state.is_paused = not self.game_state.is_paused
        status = "paused" if self.game_state.is_paused else "resumed"
        self.notification_manager.show_info("Game", f"Game {status}")

    def _take_screenshot(self):
        """Take a screenshot using the screenshot utility."""
        if self.screenshot_utility:
            filename = self.screenshot_utility.capture_screenshot()
            self.notification_manager.show_info("Screenshot", f"Saved: {filename}")
        else:
            self.logger.warning("[GAME_UI] Screenshot utility not available")

    def _on_dashboard_widget_clicked(self, plugin_name: str):
        if not self.dashboard_manager:
            return

        detail_data = self.dashboard_manager.get_detail_panel_data(plugin_name, self.game_state)
        if detail_data:
            panel_rect = pygame.Rect((self.WINDOW_WIDTH - 700) // 2, (self.WINDOW_HEIGHT - 500) // 2, 700, 500)
            detail_panel = DetailPanel(panel_rect, detail_data, on_close=self._on_detail_panel_close)
            self.ui_manager.push(detail_panel)
            self.dashboard_manager.set_expanded_panel(plugin_name)

    def _on_detail_panel_close(self):
        self.ui_manager.pop() # Pop the detail panel
        if self.dashboard_manager:
            self.dashboard_manager.close_panel()

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        actions = []
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                continue
            
            if self.hotkey_manager.handle_key_event(event):
                continue

            # The UIManager handles the rest of the events for the component stack
            self.ui_manager.handle_event(event)

        return actions

    def update(self, delta_time: float, game_state):
        """Update UI components.
        
        Args:
            delta_time: Time elapsed since last update
            game_state: Current game state
        """
        self.ui_manager.update(delta_time, game_state)

    def render(self, game_state):
        """Render the UI to screen.
        
        Args:
            game_state: Current game state
        """
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        self.ui_manager.draw(self.screen, game_state)

        pygame.display.flip()

    def shutdown(self):
        self.logger.info("[GAME_UI] Shutting down game UI")
        pygame.quit()