"""Progressive difficulty UI panel.

Displays current difficulty level, progress towards next milestone,
and performance metrics that affect difficulty scaling.
"""

import pygame
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from src.ui.components.panel import ModernPanel
from src.models.game_state import GameState
from src.core.plugins.progressive_difficulty_plugin import ProgressiveDifficultyPlugin
from src.utils.logger import GameLogger


@dataclass
class DifficultyDisplayData:
    """Data structure for difficulty display information."""

    current_level: int
    difficulty_multiplier: float
    milestone_name: str
    milestone_description: str
    performance_score: float
    progression_score: float
    next_milestone_requirements: Dict[str, Any]
    metrics: Dict[str, Any]

    @classmethod
    def from_plugin(cls, plugin: ProgressiveDifficultyPlugin) -> 'DifficultyDisplayData':
        """Create display data from progressive difficulty plugin.

        Args:
            plugin: The progressive difficulty plugin

        Returns:
            DifficultyDisplayData instance
        """
        info = plugin.get_difficulty_info()

        return cls(
            current_level=info.get("current_level", 1),
            difficulty_multiplier=info.get("difficulty_multiplier", 1.0),
            milestone_name=info.get("milestone_name", "Unknown"),
            milestone_description=info.get("milestone_description", ""),
            performance_score=0.0,  # Will be calculated
            progression_score=0.0,  # Will be calculated
            next_milestone_requirements=info.get("next_milestone_requirements", {}),
            metrics=info.get("metrics", {}),
        )


class ProgressiveDifficultyPanel(ModernPanel):
    """UI panel displaying progressive difficulty information."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize the progressive difficulty panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
        """
        super().__init__(
            "Progressive Difficulty",
            (x, y),
            (width, height)
        )
        self._logger = GameLogger("progressive_difficulty_panel")

        # Panel state
        self._display_data: Optional[DifficultyDisplayData] = None
        self._plugin: Optional[ProgressiveDifficultyPlugin] = None

        # UI elements
        self._title_font = None
        self._normal_font = None
        self._small_font = None

        # Colors
        self._colors = {
            'background': (26, 26, 46),
            'panel_bg': (22, 33, 62),
            'text': (238, 245, 255),
            'accent': (0, 173, 181),
            'success': (76, 175, 80),
            'warning': (255, 152, 0),
            'danger': (244, 67, 54),
            'progress_bg': (55, 71, 79),
            'progress_fill': (0, 173, 181),
        }

        # Layout constants
        self._margin = 20
        self._line_spacing = 25
        self._section_spacing = 15

    def initialize(self, game_state: GameState) -> None:
        """Initialize the panel with game state.

        Args:
            game_state: Current game state
        """

        # Get progressive difficulty plugin
        if hasattr(game_state, '_progressive_difficulty_plugin'):
            self._plugin = game_state._progressive_difficulty_plugin
        else:
            # Find plugin in system manager
            from src.core.system_manager import SystemManager
            system_manager = getattr(game_state, '_system_manager', None)
            if system_manager:
                for system in system_manager._systems:
                    if isinstance(system, ProgressiveDifficultyPlugin):
                        self._plugin = system
                        break

        # Initialize fonts
        self._initialize_fonts()

        # Update display data
        self._update_display_data()

    def _initialize_fonts(self) -> None:
        """Initialize fonts for the panel."""
        try:
            pygame.font.init()
            self._title_font = pygame.font.SysFont('Arial', 18, bold=True)
            self._normal_font = pygame.font.SysFont('Arial', 14)
            self._small_font = pygame.font.SysFont('Arial', 12)
        except Exception as e:
            self._logger.logger.warning(f"Failed to initialize fonts: {e}")

    def _update_display_data(self) -> None:
        """Update the display data from the plugin."""
        if self._plugin:
            try:
                self._display_data = DifficultyDisplayData.from_plugin(self._plugin)
            except Exception as e:
                self._logger.logger.error(f"Failed to update difficulty display data: {e}")
                self._display_data = None
        else:
            self._display_data = None

    def render(self, screen: pygame.Surface) -> None:
        """Render the progressive difficulty panel.

        Args:
            screen: Pygame surface to render to
        """
        # Render base panel
        super().render(screen)

        if not self._display_data:
            self._render_no_data_message(screen)
            return

        # Update display data periodically
        self._update_display_data()

        # Render difficulty information
        self._render_current_difficulty(screen)
        self._render_milestone_progress(screen)
        self._render_performance_metrics(screen)
        self._render_next_milestone(screen)

    def _render_no_data_message(self, screen: pygame.Surface) -> None:
        """Render message when no difficulty data is available.

        Args:
            screen: Pygame surface to render to
        """
        if not self._normal_font:
            return

        center_x = self.rect.centerx
        center_y = self.rect.centery

        text = self._normal_font.render("Progressive Difficulty System Not Available", True, self._colors['warning'])
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect)

    def _render_current_difficulty(self, screen: pygame.Surface) -> None:
        """Render current difficulty level and multiplier.

        Args:
            screen: Pygame surface to render to
        """
        if not self._title_font or not self._normal_font or not self._display_data:
            return

        x = self.rect.left + self._margin
        y = self.rect.top + self._margin + 30  # Account for title

        # Current difficulty level
        level_text = f"Difficulty Level: {self._display_data.current_level}"
        level_surface = self._title_font.render(level_text, True, self._colors['accent'])
        screen.blit(level_surface, (x, y))
        y += self._line_spacing + 5

        # Milestone name
        milestone_text = f"Milestone: {self._display_data.milestone_name}"
        milestone_surface = self._normal_font.render(milestone_text, True, self._colors['text'])
        screen.blit(milestone_surface, (x, y))
        y += self._line_spacing

        # Description
        desc_text = self._display_data.milestone_description
        desc_surface = self._small_font.render(desc_text, True, self._colors['text'])
        screen.blit(desc_surface, (x, y))
        y += self._line_spacing

        # Difficulty multiplier
        multiplier_text = f"Difficulty Multiplier: {self._display_data.difficulty_multiplier:.2f}x"
        multiplier_surface = self._normal_font.render(multiplier_text, True, self._colors['warning'])
        screen.blit(multiplier_surface, (x, y))

    def _render_milestone_progress(self, screen: pygame.Surface) -> None:
        """Render progress towards next milestone.

        Args:
            screen: Pygame surface to render to
        """
        if not self._normal_font or not self._display_data:
            return

        x = self.rect.left + self._margin
        y = self.rect.top + 150

        # Next milestone header
        next_req = self._display_data.next_milestone_requirements
        if next_req.get("message") == "Maximum difficulty reached":
            max_text = "Maximum Difficulty Reached!"
            max_surface = self._normal_font.render(max_text, True, self._colors['success'])
            screen.blit(max_surface, (x, y))
            return

        next_level = next_req.get("next_level", self._display_data.current_level + 1)
        progress_text = f"Progress to Level {next_level}:"
        progress_surface = self._normal_font.render(progress_text, True, self._colors['text'])
        screen.blit(progress_surface, (x, y))
        y += self._line_spacing

        # Progress bar
        bar_width = self.rect.width - 2 * self._margin
        bar_height = 20
        bar_x = x
        bar_y = y

        # Background
        pygame.draw.rect(screen, self._colors['progress_bg'], (bar_x, bar_y, bar_width, bar_height))

        # Fill
        progress_pct = next_req.get("progress_percentage", 0.0)
        fill_width = int(bar_width * (progress_pct / 100.0))
        if fill_width > 0:
            pygame.draw.rect(screen, self._colors['progress_fill'], (bar_x, bar_y, fill_width, bar_height))

        # Progress text
        progress_str = f"{progress_pct:.1f}%"
        progress_num_surface = self._small_font.render(progress_str, True, self._colors['text'])
        progress_rect = progress_num_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        screen.blit(progress_num_surface, progress_rect)

    def _render_performance_metrics(self, screen: pygame.Surface) -> None:
        """Render key performance metrics.

        Args:
            screen: Pygame surface to render to
        """
        if not self._normal_font or not self._small_font or not self._display_data:
            return

        x = self.rect.left + self._margin
        y = self.rect.top + 220

        # Header
        header_text = "Performance Metrics:"
        header_surface = self._normal_font.render(header_text, True, self._colors['accent'])
        screen.blit(header_surface, (x, y))
        y += self._line_spacing

        metrics = self._display_data.metrics

        # SLA Compliance
        sla_rate = metrics.get("recent_sla_compliance", 0.0)
        sla_color = self._get_metric_color(sla_rate, 90.0, 75.0)
        sla_text = f"SLA Compliance: {sla_rate:.1f}%"
        sla_surface = self._small_font.render(sla_text, True, sla_color)
        screen.blit(sla_surface, (x, y))
        y += self._line_spacing - 5

        # Success Rate
        success_rate = metrics.get("recent_success_rate", 0.0)
        success_color = self._get_metric_color(success_rate, 85.0, 70.0)
        success_text = f"Success Rate: {success_rate:.1f}%"
        success_surface = self._small_font.render(success_text, True, success_color)
        screen.blit(success_surface, (x, y))
        y += self._line_spacing - 5

        # Average Resolution Time
        avg_time = metrics.get("recent_average_resolution_time", 0.0)
        time_text = f"Avg Resolution: {avg_time:.1f}s"
        time_surface = self._small_font.render(time_text, True, self._colors['text'])
        screen.blit(time_surface, (x, y))
        y += self._line_spacing - 5

        # Incidents Handled
        incidents = metrics.get("total_incidents_handled", 0)
        incidents_text = f"Total Incidents: {incidents}"
        incidents_surface = self._small_font.render(incidents_text, True, self._colors['text'])
        screen.blit(incidents_surface, (x, y))

    def _render_next_milestone(self, screen: pygame.Surface) -> None:
        """Render information about the next milestone.

        Args:
            screen: Pygame surface to render to
        """
        if not self._normal_font or not self._small_font or not self._display_data:
            return

        x = self.rect.left + self._margin
        y = self.rect.bottom - 80

        next_req = self._display_data.next_milestone_requirements

        if next_req.get("message") == "Maximum difficulty reached":
            return

        next_level = next_req.get("next_level", self._display_data.current_level + 1)
        milestone_name = next_req.get("milestone_name", "Unknown")

        # Next milestone info
        next_text = f"Next: Level {next_level} - {milestone_name}"
        next_surface = self._normal_font.render(next_text, True, self._colors['accent'])
        screen.blit(next_surface, (x, y))
        y += self._line_spacing

        # Requirements hint
        hint_text = "Improve performance and handle more incidents"
        hint_surface = self._small_font.render(hint_text, True, self._colors['text'])
        screen.blit(hint_surface, (x, y))

    def _get_metric_color(self, value: float, good_threshold: float, poor_threshold: float) -> Tuple[int, int, int]:
        """Get color for metric value based on thresholds.

        Args:
            value: Metric value
            good_threshold: Threshold for good performance
            poor_threshold: Threshold for poor performance

        Returns:
            RGB color tuple
        """
        if value >= good_threshold:
            return self._colors['success']
        elif value >= poor_threshold:
            return self._colors['warning']
        else:
            return self._colors['danger']

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the panel.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        # Handle base panel events
        if super().handle_event(event):
            return True

        # Panel-specific event handling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    # Could add interactive elements here
                    pass

        return False

    def update(self, delta_time: float) -> None:
        """Update the panel state.

        Args:
            delta_time: Time elapsed since last update
        """

        # Update display data periodically
        self._update_display_data()