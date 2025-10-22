"""Game User Interface using Pygame - Dashboard Framework.

This module handles all visual rendering and user input for the game.
Uses the new Dashboard Framework with UIProvider architecture.
Legacy panel system has been removed.
"""

import pygame
from typing import List, Optional, Any, Tuple
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.notification_system import NotificationManager
from src.ui.hotkey_manager import HotkeyManager, HotkeyAction
from src.ui.modal_manager import ModalManager
from src.ui.dashboard_manager import DashboardManager
from src.ui.dashboard_panel import DashboardPanel
from src.ui.components.hud_overlay import HUDOverlay
from src.ui.components.quick_reference import QuickReference
from src.core.event_bus import get_event_bus


@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict


class GameUI:
    """Main UI class handling Pygame rendering and input.
    
    Uses Dashboard Framework with UIProvider plugins for extensible UI.
    All game systems that want to display information implement UIProvider.
    """

    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60

    def __init__(self, game_state: GameState, system_manager=None):
        """Initialize the game UI.

        Args:
            game_state: The game state to render (read-only)
            system_manager: SystemManager with registered plugins
        """
        self.logger = GameLogger("game_ui")
        self.game_state = game_state
        self.system_manager = system_manager
        self.event_bus = get_event_bus()

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.notification_manager = NotificationManager(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.hotkey_manager = HotkeyManager()
        
        # Initialize HUD overlay
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )
        
        # Initialize quick reference
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=5.0
        )
        
        # Initialize modal manager for detail panels
        self.modal_manager = ModalManager(
            self.screen,
            self.game_state,
            on_open=None,
            on_close=None
        )
        
        # Initialize dashboard manager and panel
        if self.system_manager:
            self.dashboard_manager = DashboardManager(self.system_manager)
            self.dashboard_panel = DashboardPanel(
                x=10,
                y=60,
                on_widget_clicked=self._on_dashboard_widget_clicked
            )
            self.logger.info("[GAME_UI] Dashboard initialized with system plugins")
        else:
            self.dashboard_manager = None
            self.dashboard_panel = None
            self.logger.warning("[GAME_UI] No system_manager provided - dashboard disabled")

        # Register hotkeys
        self._register_hotkey_callbacks()

        # UI state
        self.show_help_overlay = False
        self.running = True
        
        # Detail panel state
        self.detail_panel_modal = None

        self.logger.info("[GAME_UI] Game UI initialized (Dashboard Framework)")

    def _register_hotkey_callbacks(self) -> None:
        """Register hotkey callbacks."""
        self.hotkey_manager.register_callback(
            HotkeyAction.PAUSE_TOGGLE,
            lambda: self._toggle_pause()
        )

    def _toggle_pause(self) -> None:
        """Toggle game pause state."""
        self.game_state.is_paused = not self.game_state.is_paused
        status = "paused" if self.game_state.is_paused else "resumed"
        self.notification_manager.show_info("Game", f"Game {status}")

    def _on_dashboard_widget_clicked(self, plugin_name: str) -> None:
        """Handle dashboard widget click to open detail panel.
        
        Args:
            plugin_name: Name of the plugin that was clicked
        """
        if not self.dashboard_manager:
            return
        
        self.logger.debug(f"[GAME_UI] Dashboard widget clicked: {plugin_name}")
        
        # Get detail panel data from dashboard manager
        detail_data = self.dashboard_manager.get_detail_panel_data(
            plugin_name,
            self.game_state
        )
        
        if detail_data:
            # Open detail panel modal
            self._open_detail_panel(plugin_name, detail_data)
        else:
            self.logger.warning(f"[GAME_UI] No detail data for {plugin_name}")

    def _open_detail_panel(self, plugin_name: str, detail_data: dict) -> None:
        """Open a detail panel modal with plugin data.
        
        Args:
            plugin_name: Name of plugin
            detail_data: Detail panel data structure
        """
        self.logger.debug(f"[GAME_UI] Opening detail panel for {plugin_name}")
        
        # For now, just log the data - full modal rendering in next phase
        title = detail_data.get("title", plugin_name)
        sections = detail_data.get("sections", [])
        actions = detail_data.get("actions", [])
        
        self.logger.debug(f"[GAME_UI] Detail panel: {title}")
        self.logger.debug(f"[GAME_UI] Sections: {len(sections)}")
        self.logger.debug(f"[GAME_UI] Actions: {len(actions)}")
        
        # TODO: Implement full modal rendering with action buttons

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        """Process input events and return game actions.

        Args:
            events: List of Pygame events

        Returns:
            List of game actions to process
        """
        actions = []

        for event in events:
            # Modal manager gets first priority
            if self.modal_manager.handle_event(event):
                continue

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize((event.w, event.h))
                continue

            # Handle dashboard widget clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dashboard_panel:
                    clicked_plugin = self.dashboard_panel.handle_click(event.pos)
                    if clicked_plugin:
                        continue
            
            # Handle mouse movement for dashboard hover effects
            if event.type == pygame.MOUSEMOTION:
                if self.dashboard_panel:
                    self.dashboard_panel.update_hover(event.pos)

            # Handle hotkeys
            if self.hotkey_manager.handle_key_event(event):
                continue

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help_overlay = not self.show_help_overlay
                    if not self.show_help_overlay:
                        self.quick_reference.toggle()
                elif event.key == pygame.K_ESCAPE:
                    # Close modals or exit
                    if self.modal_manager.is_modal_open():
                        self.modal_manager.close_modal()
                    else:
                        self.running = False

        return actions

    def handle_resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize event.
        
        Args:
            new_size: New window size (width, height)
        """
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = new_size
        self.screen = pygame.display.set_mode(new_size)
        
        # Update HUD
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )
        
        # Update quick reference
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=5.0
        )

    def update(self, delta_time: float) -> None:
        """Update UI state.

        Args:
            delta_time: Time elapsed since last update
        """
        # Update HUD overlay
        self.hud_overlay.update(delta_time, self.game_state)
        
        # Update quick reference
        self.quick_reference.update(delta_time)
        
        # Update modal manager
        self.modal_manager.update(delta_time)
        
        # Update notification manager
        self.notification_manager.update(delta_time)

    def render(self) -> None:
        """Render the game UI."""
        # Get background color from theme
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        # Render HUD overlay
        self.hud_overlay.render(self.screen, self.game_state, "Dashboard")
        
        # Render dashboard panel (shows UIProvider summaries)
        if self.dashboard_panel and self.dashboard_manager:
            self.dashboard_panel.render(self.screen, self.dashboard_manager, self.game_state)
        
        # Render quick reference card
        self.quick_reference.render(self.screen)

        # Render modals on top of everything
        self.modal_manager.draw()

        # Render notifications (always on top)
        self.notification_manager.render(self.screen)

        # Render help overlay if active
        if self.show_help_overlay:
            self._render_help_overlay()

        # Update display
        pygame.display.flip()

    def _render_help_overlay(self) -> None:
        """Render help overlay with hotkeys."""
        # Semi-transparent overlay
        overlay = pygame.Surface((400, 300))
        overlay.set_alpha(220)
        overlay.fill((30, 30, 40))

        # Position in center
        overlay_x = (self.WINDOW_WIDTH - 400) // 2
        overlay_y = (self.WINDOW_HEIGHT - 300) // 2

        # Title
        title_font = pygame.font.SysFont('Arial', 18, bold=True)
        title_text = title_font.render("Hotkey Reference", True, (255, 255, 255))
        overlay.blit(title_text, (20, 20))

        # Hotkeys
        help_font = pygame.font.SysFont('Arial', 14)
        hotkeys = [
            ("H", "Toggle This Help"),
            ("ESC", "Close Modal / Exit"),
            ("SPACE", "Pause/Resume Game"),
            ("", ""),
            ("Dashboard:", ""),
            ("Click widget", "Open detail panel"),
            ("", ""),
            ("🏢 Clients plugin shows real data", ""),
        ]

        y_offset = 60
        for key, description in hotkeys:
            if key and description:
                text = help_font.render(f"{key:12s} - {description}", True, (220, 220, 220))
            elif description:
                text = help_font.render(description, True, (180, 180, 200))
            else:
                continue
            overlay.blit(text, (20, y_offset))
            y_offset += 22

        # Draw border
        pygame.draw.rect(overlay, (0, 180, 255), overlay.get_rect(), 2, border_radius=4)

        self.screen.blit(overlay, (overlay_x, overlay_y))

    def set_screenshot_utility(self, screenshot_utility) -> None:
        """Set the screenshot utility for hotkey callbacks.
        
        Args:
            screenshot_utility: The screenshot utility instance
        """
        self.screenshot_utility = screenshot_utility

    def shutdown(self) -> None:
        """Clean shutdown of UI systems."""
        self.logger.info("[GAME_UI] Shutting down game UI")
        pygame.quit()
