"""Game User Interface using Pygame.

This module handles all visual rendering and user input for the game.
Following the architecture principle: Pygame renders, it doesn't think.
"""

import pygame
from typing import List, Optional, Any
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger


@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict


class GameUI:
    """Main UI class handling Pygame rendering and input."""

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    BLUE = (0, 100, 200)
    GREEN = (0, 200, 100)
    RED = (200, 50, 50)
    YELLOW = (200, 200, 0)

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

        # UI state
        self.selected_specialist = None
        self.selected_incident = None

        self.logger.logger.info("[GAME_UI] Game UI initialized")

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        """Process input events and return game actions.

        Args:
            events: List of Pygame events

        Returns:
            List of game actions to process
        """
        actions = []

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = self._handle_mouse_click(event.pos)
                if action:
                    actions.append(action)
            elif event.type == pygame.KEYDOWN:
                action = self._handle_key_press(event.key)
                if action:
                    actions.append(action)

        return actions

    def _handle_mouse_click(self, pos: tuple) -> Optional[GameAction]:
        """Handle mouse click at position.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Game action if click handled, None otherwise
        """
        x, y = pos

        # Check if click is in specialist panel
        if self._is_in_specialist_panel(x, y):
            specialist = self._get_specialist_at_pos(x, y)
            if specialist:
                self.selected_specialist = specialist
                return GameAction("select_specialist", {"specialist_id": specialist.id})

        # Check if click is in incident panel
        elif self._is_in_incident_panel(x, y):
            incident = self._get_incident_at_pos(x, y)
            if incident:
                self.selected_incident = incident
                return GameAction("select_incident", {"incident_id": incident.id})

        # Check if click is assign button
        elif self._is_in_assign_button(x, y) and self.selected_specialist and self.selected_incident:
            return GameAction("assign_incident", {
                "specialist_id": self.selected_specialist.id,
                "incident_id": self.selected_incident.id
            })

        return None

    def _handle_key_press(self, key: int) -> Optional[GameAction]:
        """Handle key press.

        Args:
            key: Pygame key code

        Returns:
            Game action if key handled, None otherwise
        """
        if key == pygame.K_ESCAPE:
            return GameAction("quit", {})
        elif key == pygame.K_SPACE:
            return GameAction("pause_toggle", {})

        return None

    def update(self, delta_time: float) -> None:
        """Update UI state.

        Args:
            delta_time: Time elapsed since last update
        """
        # Update any animations or UI state changes
        pass

    def render(self) -> None:
        """Render the game UI."""
        self.screen.fill(self.DARK_GRAY)

        # Render main panels
        self._render_header()
        self._render_specialist_panel()
        self._render_incident_panel()
        self._render_metrics_panel()
        self._render_controls()

        # Update display
        pygame.display.flip()

    def _render_header(self) -> None:
        """Render the game header with basic info."""
        header_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, 60)
        pygame.draw.rect(self.screen, self.BLUE, header_rect)

        # Title
        title_text = self.font.render("Cybersecurity Firm - Idle/Tycoon/RPG", True, self.WHITE)
        self.screen.blit(title_text, (20, 15))

        # Money and time
        money_text = self.font.render(f"Money: ${self.game_state.current_money:,.0f}", True, self.WHITE)
        self.screen.blit(money_text, (self.WINDOW_WIDTH - 300, 15))

        time_text = self.font.render(f"Time: {self.game_state.get_game_time_elapsed():.1f}s", True, self.WHITE)
        self.screen.blit(time_text, (self.WINDOW_WIDTH - 300, 35))

    def _render_specialist_panel(self) -> None:
        """Render the specialist roster panel."""
        panel_rect = pygame.Rect(20, 80, 400, 300)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect, 2)

        # Panel title
        title_text = self.font.render("Specialists", True, self.WHITE)
        self.screen.blit(title_text, (30, 85))

        # Render specialists
        y_offset = 110
        for i, specialist in enumerate(self.game_state.specialists[:8]):  # Show first 8
            color = self.GREEN if specialist.is_available() else self.RED
            if specialist == self.selected_specialist:
                color = self.YELLOW

            spec_text = self.small_font.render(
                f"{specialist.name} (Lv.{specialist.level}) - {specialist.status}",
                True, color
            )
            self.screen.blit(spec_text, (30, y_offset + i * 25))

    def _render_incident_panel(self) -> None:
        """Render the active incidents panel."""
        panel_rect = pygame.Rect(440, 80, 400, 300)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect, 2)

        # Panel title
        title_text = self.font.render("Active Incidents", True, self.WHITE)
        self.screen.blit(title_text, (450, 85))

        # Render incidents
        y_offset = 110
        for i, incident in enumerate(self.incidents[:8]):  # Show first 8
            color = self.YELLOW if incident.status == "pending" else self.RED
            if incident == self.selected_incident:
                color = self.BLUE

            inc_text = self.small_font.render(
                f"{incident.incident_type} (Diff:{incident.difficulty}) - {incident.status}",
                True, color
            )
            self.screen.blit(inc_text, (450, y_offset + i * 25))

    def _render_metrics_panel(self) -> None:
        """Render the game metrics panel."""
        panel_rect = pygame.Rect(860, 80, 400, 300)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect, 2)

        # Panel title
        title_text = self.font.render("Game Metrics", True, self.WHITE)
        self.screen.blit(title_text, (870, 85))

        # Render metrics
        metrics = [
            f"Incidents Handled: {self.game_state.metrics.total_incidents_handled}",
            f"Incidents Failed: {self.game_state.metrics.total_incidents_failed}",
            f"Total XP Awarded: {self.game_state.metrics.total_xp_awarded}",
            f"Specialist Utilization: {self.game_state.metrics.specialist_utilization_rate:.1f}%",
            f"Active Clients: {len([c for c in self.game_state.clients if c.active])}",
        ]

        y_offset = 110
        for i, metric in enumerate(metrics):
            metric_text = self.small_font.render(metric, True, self.WHITE)
            self.screen.blit(metric_text, (870, y_offset + i * 25))

    def _render_controls(self) -> None:
        """Render control buttons and instructions."""
        # Assign button
        assign_rect = pygame.Rect(20, 400, 200, 40)
        color = self.GREEN if (self.selected_specialist and self.selected_incident) else self.GRAY
        pygame.draw.rect(self.screen, color, assign_rect)

        assign_text = self.font.render("Assign Incident", True, self.BLACK)
        self.screen.blit(assign_text, (30, 405))

        # Instructions
        instructions = [
            "Click specialists and incidents to select them",
            "Press Assign to assign selected specialist to incident",
            "Space: Pause/Resume | ESC: Quit"
        ]

        y_offset = 460
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, self.WHITE)
            self.screen.blit(inst_text, (20, y_offset))
            y_offset += 20

    def _is_in_specialist_panel(self, x: int, y: int) -> bool:
        """Check if position is in specialist panel."""
        return 20 <= x <= 420 and 80 <= y <= 380

    def _is_in_incident_panel(self, x: int, y: int) -> bool:
        """Check if position is in incident panel."""
        return 440 <= x <= 840 and 80 <= y <= 380

    def _is_in_assign_button(self, x: int, y: int) -> bool:
        """Check if position is in assign button."""
        return 20 <= x <= 220 and 400 <= y <= 440

    def _get_specialist_at_pos(self, x: int, y: int) -> Optional[Any]:
        """Get specialist at mouse position."""
        if not self._is_in_specialist_panel(x, y):
            return None

        index = (y - 110) // 25
        if 0 <= index < len(self.game_state.specialists):
            return self.game_state.specialists[index]
        return None

    def _get_incident_at_pos(self, x: int, y: int) -> Optional[Any]:
        """Get incident at mouse position."""
        if not self._is_in_incident_panel(x, y):
            return None

        index = (y - 110) // 25
        if 0 <= index < len(self.incidents):
            return self.incidents[index]
        return None

    @property
    def incidents(self):
        """Get active incidents from game state."""
        return [inc for inc in self.game_state.incidents if inc.status in ["pending", "assigned"]]

    def shutdown(self) -> None:
        """Clean shutdown of UI systems."""
        self.logger.logger.info("[GAME_UI] Shutting down game UI")
