"""Game User Interface using Pygame.

This module handles all visual rendering and user input for the game.
Following the architecture principle: Pygame renders, it doesn't think.
"""

import pygame
from typing import List, Optional, Any
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.notification_system import NotificationManager
from src.ui.hotkey_manager import HotkeyManager, HotkeyAction
from src.ui.panels.specialist_roster_panel import SpecialistRosterPanel
from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.ui.panels.metrics_panel import MetricsPanel
from src.ui.components.button import Button, ButtonStyle


@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict


class GameUI:
    """Main UI class handling Pygame rendering and input."""

    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60

    def __init__(self, game_state: GameState):
        """Initialize the game UI.

        Args:
            game_state: The game state to render
        """
        self.logger = GameLogger("game_ui")
        self.game_state = game_state

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.notification_manager = NotificationManager(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.hotkey_manager = HotkeyManager()

        # Register hotkey callbacks
        self._register_hotkey_callbacks()

        # Initialize panels
        self.specialist_roster_panel = SpecialistRosterPanel(self.game_state)
        self.incident_queue_panel = IncidentQueuePanel(self.game_state)
        self.metrics_panel = MetricsPanel(self.game_state)

        # Apply theme to panels
        self._apply_theme_to_panels()

        # Panels list for z-order management
        self.panels = [
            self.specialist_roster_panel,
            self.incident_queue_panel,
            self.metrics_panel,
        ]

        # Create assign button
        self.assign_button = Button(
            text="Assign Specialist",
            position=(20, 600),
            size=(200, 40),
            callback=self._handle_assign_button,
            style=ButtonStyle.PRIMARY,
            enabled=False,
        )

        # UI state
        self.show_help_overlay = False

        self.logger.logger.info("[GAME_UI] Game UI initialized with new panel system")

    def _register_hotkey_callbacks(self) -> None:
        """Register hotkey callbacks."""
        self.hotkey_manager.register_callback(
            HotkeyAction.PAUSE_TOGGLE,
            lambda: self._toggle_pause()
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_SPECIALIST_PANEL,
            lambda: self._toggle_panel(self.specialist_roster_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_INCIDENT_PANEL,
            lambda: self._toggle_panel(self.incident_queue_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_METRICS_PANEL,
            lambda: self._toggle_panel(self.metrics_panel)
        )

    def _apply_theme_to_panels(self) -> None:
        """Apply current theme to all panels."""
        theme = self.theme_manager.get_current_theme()
        if theme:
            theme_dict = {"colors": theme.colors}
            self.specialist_roster_panel.set_theme_colors(theme_dict)
            self.incident_queue_panel.set_theme_colors(theme_dict)
            self.metrics_panel.set_theme_colors(theme_dict)

    def _toggle_pause(self) -> None:
        """Toggle game pause state."""
        self.game_state.is_paused = not self.game_state.is_paused
        status = "paused" if self.game_state.is_paused else "resumed"
        self.notification_manager.show_info("Game", f"Game {status}")

    def _toggle_panel(self, panel) -> None:
        """Toggle panel visibility."""
        panel.visible = not panel.visible

    def _handle_assign_button(self) -> None:
        """Handle assign button click."""
        specialist = self.specialist_roster_panel.get_selected_specialist()
        incident = self.incident_queue_panel.get_selected_incident()

        if specialist and incident:
            # Try to assign
            success = self.game_state.assign_incident_to_specialist(incident.id, specialist.id)
            if success:
                self.notification_manager.show_success(
                    "Assignment",
                    f"{specialist.name} assigned to {incident.incident_type}"
                )
            else:
                self.notification_manager.show_error(
                    "Assignment Failed",
                    "Could not assign specialist to incident"
                )

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        """Process input events and return game actions.

        Args:
            events: List of Pygame events

        Returns:
            List of game actions to process
        """
        actions = []

        for event in events:
            # Handle hotkeys first
            if self.hotkey_manager.handle_key_event(event):
                continue

            # Handle panel events (in reverse z-order)
            event_consumed = False
            for panel in reversed(self.panels):
                if panel.handle_event(event):
                    # Bring panel to front if clicked
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.panels.remove(panel)
                        self.panels.append(panel)
                    event_consumed = True
                    break

            if event_consumed:
                continue

            # Handle button events
            if self.assign_button.handle_event(event):
                continue

            # Handle other inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help_overlay = not self.show_help_overlay

        return actions

    def update(self, delta_time: float) -> None:
        """Update UI state.

        Args:
            delta_time: Time elapsed since last update
        """
        # Update notification manager
        self.notification_manager.update(delta_time)

        # Update button enabled state
        specialist = self.specialist_roster_panel.get_selected_specialist()
        incident = self.incident_queue_panel.get_selected_incident()
        self.assign_button.set_enabled(specialist is not None and incident is not None)

    def render(self) -> None:
        """Render the game UI."""
        # Get background color from theme
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        # Render main panels
        self._render_header()

        # Render all panels (in z-order)
        for panel in self.panels:
            panel.render(self.screen)

        # Render controls
        self._render_controls()

        # Render notifications (always on top)
        self.notification_manager.render(self.screen)

        # Render help overlay if active
        if self.show_help_overlay:
            self._render_help_overlay()

        # Update display
        pygame.display.flip()

    def _render_header(self) -> None:
        """Render the game header with basic info."""
        header_height = 60
        header_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, header_height)
        
        # Get colors from theme
        primary_color = self.theme_manager.get_color("primary", (0, 180, 255))
        text_color = self.theme_manager.get_color("text", (220, 220, 230))
        
        pygame.draw.rect(self.screen, primary_color, header_rect)

        # Title
        title_text = self.font.render("Cybersecurity Firm - Idle/Tycoon/RPG", True, text_color)
        self.screen.blit(title_text, (20, 15))

        # Money
        money_text = self.font.render(f"Money: ${self.game_state.current_money:,.0f}", True, text_color)
        self.screen.blit(money_text, (self.WINDOW_WIDTH - 300, 15))

        # Time and pause status
        time_text = f"Time: {self.game_state.get_game_time_elapsed():.1f}s"
        if self.game_state.is_paused:
            time_text += " [PAUSED]"
        time_surface = self.font.render(time_text, True, text_color)
        self.screen.blit(time_surface, (self.WINDOW_WIDTH - 300, 35))

    def _render_controls(self) -> None:
        """Render control buttons and instructions."""
        # Render assign button
        self.assign_button.render(self.screen)

        # Instructions
        text_color = self.theme_manager.get_color("text", (220, 220, 230))
        
        instructions = [
            "Hotkeys: 1-6: Toggle Panels | SPACE: Pause | H: Help | +/-: Speed",
            "Click specialists and incidents in panels to select them",
            "Press Assign button to assign selected specialist to incident",
        ]

        y_offset = 650
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, text_color)
            self.screen.blit(inst_text, (240, y_offset))
            y_offset += 20

    def _render_help_overlay(self) -> None:
        """Render help overlay with all hotkeys."""
        # Semi-transparent overlay
        overlay = pygame.Surface((400, 400))
        overlay.set_alpha(220)
        overlay.fill((30, 30, 40))

        # Position in center
        overlay_x = (self.WINDOW_WIDTH - 400) // 2
        overlay_y = (self.WINDOW_HEIGHT - 400) // 2

        # Title
        title_font = pygame.font.SysFont('Arial', 18, bold=True)
        title_text = title_font.render("Hotkey Reference", True, (255, 255, 255))
        overlay.blit(title_text, (20, 20))

        # Hotkeys
        help_font = pygame.font.SysFont('Arial', 14)
        hotkeys = [
            ("1", "Toggle Specialist Roster"),
            ("2", "Toggle Incident Queue"),
            ("3", "Toggle Metrics Panel"),
            ("SPACE", "Pause/Resume Game"),
            ("+", "Increase Game Speed"),
            ("-", "Decrease Game Speed"),
            ("H", "Toggle This Help"),
            ("ESC", "Close Panels"),
        ]

        y_offset = 60
        for key, description in hotkeys:
            key_text = help_font.render(f"{key:10s} - {description}", True, (220, 220, 220))
            overlay.blit(key_text, (20, y_offset))
            y_offset += 25

        # Draw border
        pygame.draw.rect(overlay, (0, 180, 255), overlay.get_rect(), 2, border_radius=4)

        self.screen.blit(overlay, (overlay_x, overlay_y))

    def shutdown(self) -> None:
        """Clean shutdown of UI systems."""
        self.logger.logger.info("[GAME_UI] Shutting down game UI")
