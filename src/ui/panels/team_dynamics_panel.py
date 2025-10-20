"""Team dynamics UI panel for displaying relationships and morale.

This panel shows specialist relationships, morale levels, and team synergy
information to help players understand team dynamics.
"""

import pygame
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

from src.ui.components.panel import ModernPanel
from src.core.plugins.relationships_plugin import RelationshipsPlugin
from src.models.specialist import Specialist


@dataclass
class RelationshipDisplay:
    """Data for displaying a relationship in the UI."""
    specialist_a: str
    specialist_b: str
    relationship_type: str
    strength: float
    color: Tuple[int, int, int]


@dataclass
class MoraleDisplay:
    """Data for displaying morale in the UI."""
    specialist_id: str
    specialist_name: str
    current_morale: float
    base_morale: float
    relationship_impact: float
    workload_impact: float
    success_impact: float


class TeamDynamicsPanel(ModernPanel):
    """Panel for displaying team dynamics information."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize team dynamics panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
        """
        super().__init__(
            "Team Dynamics",
            (x, y),
            (width, height)
        )
        self._relationships_plugin: Optional[RelationshipsPlugin] = None
        self._relationships: List[RelationshipDisplay] = []
        self._morale_states: List[MoraleDisplay] = []
        self._selected_specialist: Optional[str] = None

        # Layout constants
        self._relationship_height = 40
        self._morale_height = 60
        self._padding = 10

        # Colors
        self._colors = {
            'friendship': (0, 200, 100),
            'rivalry': (200, 100, 0),
            'mentorship': (100, 150, 255),
            'neutral': (150, 150, 150),
            'high_morale': (0, 200, 100),
            'medium_morale': (200, 200, 0),
            'low_morale': (200, 100, 100),
            'text': (255, 255, 255),
            'background': (25, 25, 40),
            'panel_bg': (40, 40, 60),
            'border': (100, 100, 150),
        }

    def set_relationships_plugin(self, plugin: RelationshipsPlugin) -> None:
        """Set the relationships plugin reference.

        Args:
            plugin: Relationships plugin instance
        """
        self._relationships_plugin = plugin
        self._update_display_data()

    def _update_display_data(self) -> None:
        """Update display data from the plugin."""
        if not self._relationships_plugin:
            return

        # Get relationships data from the plugin
        self._relationships = []
        if hasattr(self._relationships_plugin, 'get_specialist_relationships_summary'):
            # For now, we'll show summary data since detailed relationship data
            # isn't directly exposed. This can be enhanced later.
            pass

        # Update morale states (placeholder for now)
        self._morale_states = []

    def render(self, screen: pygame.Surface) -> None:
        """Render the team dynamics panel.

        Args:
            screen: The surface to render to
        """
        # Call parent render
        super().render(screen)

        if not self._relationships_plugin:
            self._render_no_plugin_message(screen)
            return

        # Get content area
        content_rect = pygame.Rect(
            self.position[0] + 5,
            self.position[1] + 35,  # Account for title bar
            self.size[0] - 10,
            self.size[1] - 40
        )

        # Render relationships section
        self._render_relationships_section(screen, content_rect)

        # Render morale section
        morale_rect = pygame.Rect(
            content_rect.x,
            content_rect.y + content_rect.height // 2,
            content_rect.width,
            content_rect.height // 2
        )
        self._render_morale_section(screen, morale_rect)

    def _render_no_plugin_message(self, screen: pygame.Surface) -> None:
        """Render message when plugin is not available.

        Args:
            screen: The surface to render to
        """
        font = pygame.font.Font(None, 24)
        text = font.render("Team dynamics system not available", True, self._colors['text'])
        text_rect = text.get_rect(center=(
            self.position[0] + self.size[0] // 2,
            self.position[1] + self.size[1] // 2
        ))
        screen.blit(text, text_rect)

    def _render_relationships_section(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the relationships section.

        Args:
            screen: The surface to render to
            rect: Rectangle for the relationships section
        """
        # Section title
        font = pygame.font.Font(None, 20)
        title = font.render("Specialist Relationships", True, self._colors['text'])
        screen.blit(title, (rect.x + 5, rect.y + 5))

        # Show relationship summary if plugin is available
        if self._relationships_plugin:
            summary_font = pygame.font.Font(None, 16)
            summary_text = "Relationships system active - detailed view coming soon"
            summary_surface = summary_font.render(summary_text, True, self._colors['text'])
            screen.blit(summary_surface, (rect.x + 10, rect.y + 35))
        else:
            # Fallback message
            font = pygame.font.Font(None, 16)
            text = "Relationships data will be displayed here"
            text_surface = font.render(text, True, self._colors['text'])
            screen.blit(text_surface, (rect.x + 10, rect.y + 35))

    def _render_relationship(self, screen: pygame.Surface, rect: pygame.Rect,
                           relationship: RelationshipDisplay, y_offset: int) -> None:
        """Render a single relationship.

        Args:
            screen: The surface to render to
            rect: Section rectangle
            relationship: Relationship to render
            y_offset: Y offset within section
        """
        x = rect.x + 10
        y = rect.y + y_offset

        # Background
        bg_rect = pygame.Rect(x - 5, y - 2, rect.width - 20, self._relationship_height - 5)
        pygame.draw.rect(screen, self._colors['panel_bg'], bg_rect)
        pygame.draw.rect(screen, relationship.color, bg_rect, 2)

        # Relationship info
        font = pygame.font.Font(None, 16)
        text = f"{relationship.specialist_a} ↔ {relationship.specialist_b}: {relationship.relationship_type.title()}"
        text_surface = font.render(text, True, self._colors['text'])
        screen.blit(text_surface, (x, y + 5))

        # Strength indicator
        strength_text = f"Strength: {relationship.strength:.1f}"
        strength_surface = font.render(strength_text, True, self._colors['text'])
        screen.blit(strength_surface, (x, y + 22))

    def _render_morale_section(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the morale section.

        Args:
            screen: The surface to render to
            rect: Rectangle for the morale section
        """
        # Section title
        font = pygame.font.Font(None, 20)
        title = font.render("Team Morale", True, self._colors['text'])
        screen.blit(title, (rect.x + 5, rect.y + 5))

        # Placeholder for morale display
        font = pygame.font.Font(None, 16)
        placeholder = font.render("Morale data will be displayed here", True, self._colors['text'])
        screen.blit(placeholder, (rect.x + 10, rect.y + 35))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.

        Args:
            event: The event to handle

        Returns:
            True if event was handled, False otherwise
        """
        # Call parent event handling
        if super().handle_event(event):
            return True

        # Handle panel-specific events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            panel_rect = self.get_rect()
            if panel_rect.collidepoint(event.pos):
                # Handle clicks within the panel
                return True

        return False

    def update_panel(self, game_state: Any) -> None:
        """Update the panel with current game state.

        Args:
            game_state: Current game state
        """
        # Find the relationships plugin if not already found
        if not self._relationships_plugin:
            if hasattr(game_state, '_systems'):
                for system in game_state._systems.values():
                    if isinstance(system, RelationshipsPlugin):
                        self._relationships_plugin = system
                        break

        self._update_display_data()