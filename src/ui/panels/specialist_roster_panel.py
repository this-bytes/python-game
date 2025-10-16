"""Specialist Roster Panel for displaying all specialists."""

import pygame
from typing import Optional, Any
from src.ui.components.panel import Panel
from src.ui.components.progress_bar import ProgressBar
from src.ui.components.scroll_container import ScrollContainer
from src.models.game_state import GameState
from src.models.specialist import Specialist


class SpecialistRosterPanel(Panel):
    """Display all specialists with filters and sorting."""

    def __init__(self, game_state: GameState):
        """Initialize specialist roster panel.

        Args:
            game_state: Game state reference
        """
        super().__init__(
            title="Specialist Roster",
            position=(20, 80),
            size=(380, 500),
            closeable=True,
            minimizable=True,
            draggable=True,
        )
        self.game_state = game_state
        self.scroll_container = ScrollContainer(
            position=(0, 0),
            size=(380, 468),
            content_height=0
        )
        self.selected_specialist: Optional[Specialist] = None

        # Card styling
        self.card_height = 80
        self.card_margin = 5

        # Status colors
        self.status_colors = {
            "available": (0, 200, 100),
            "working": (255, 200, 0),
            "resting": (100, 100, 200),
        }

        # Fonts
        self.card_font = None
        self.small_font = None

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render specialist roster content.

        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Initialize fonts if needed
        if self.card_font is None:
            self.card_font = pygame.font.SysFont('Arial', 14, bold=True)
            self.small_font = pygame.font.SysFont('Arial', 11)

        # Update scroll container
        specialists = self.game_state.specialists
        self.scroll_container.set_content_height(len(specialists) * (self.card_height + self.card_margin))
        self.scroll_container.position = (content_rect.x, content_rect.y)
        self.scroll_container.size = (content_rect.width, content_rect.height)

        # Create clipping region for scrolling
        screen.set_clip(content_rect)

        # Render specialists
        y_offset = content_rect.y - self.scroll_container.get_scroll_offset()

        for specialist in specialists:
            card_rect = pygame.Rect(
                content_rect.x + self.card_margin,
                y_offset,
                content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                self.card_height
            )

            # Skip if not visible
            if card_rect.bottom < content_rect.top or card_rect.top > content_rect.bottom:
                y_offset += self.card_height + self.card_margin
                continue

            self._render_specialist_card(screen, specialist, card_rect)
            y_offset += self.card_height + self.card_margin

        # Reset clipping
        screen.set_clip(None)

        # Render scroll container
        self.scroll_container.render(screen)

    def _render_specialist_card(self, screen: pygame.Surface, specialist: Specialist, rect: pygame.Rect) -> None:
        """Render individual specialist card.

        Args:
            screen: Pygame surface to render on
            specialist: Specialist to render
            rect: Rectangle for card
        """
        # Card background
        bg_color = (45, 45, 60) if specialist != self.selected_specialist else (60, 60, 80)
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)

        # Border
        border_color = (80, 80, 100)
        if specialist == self.selected_specialist:
            border_color = (0, 180, 255)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)

        # Specialist name
        name_text = self.card_font.render(specialist.name, True, self.text_color)
        screen.blit(name_text, (rect.x + 10, rect.y + 5))

        # Level
        level_text = self.small_font.render(f"Lv.{specialist.level}", True, (200, 200, 0))
        screen.blit(level_text, (rect.x + 10, rect.y + 25))

        # Specialty
        specialty_text = self.small_font.render(specialist.specialty, True, (150, 150, 200))
        screen.blit(specialty_text, (rect.x + 60, rect.y + 25))

        # Status
        status = specialist.status
        status_color = self.status_colors.get(status, (150, 150, 150))
        status_text = self.small_font.render(status.upper(), True, status_color)
        screen.blit(status_text, (rect.right - 80, rect.y + 5))

        # XP Progress bar
        xp_rect = pygame.Rect(rect.x + 10, rect.y + 45, rect.width - 20, 20)
        xp_bar = ProgressBar(
            position=(xp_rect.x, xp_rect.y),
            size=(xp_rect.width, xp_rect.height),
            value=specialist.xp,
            max_value=specialist.calculate_xp_for_next_level(),
            show_label=True,
        )
        xp_bar.fill_color = (0, 150, 255)
        xp_bar.render(screen)

    def handle_event(self, event: Any) -> bool:
        """Handle events for specialist roster panel.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed, False otherwise
        """
        # Handle panel events first
        if super().handle_event(event):
            return True

        # Handle scroll container events
        if self.scroll_container.handle_event(event):
            return True

        # Handle specialist selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rect = self.get_rect()
            content_rect = pygame.Rect(
                rect.x + self.BORDER_WIDTH,
                rect.y + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
                rect.width - 2 * self.BORDER_WIDTH,
                rect.height - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
            )

            if content_rect.collidepoint(event.pos):
                # Calculate which specialist was clicked
                y_offset = content_rect.y - self.scroll_container.get_scroll_offset()
                for specialist in self.game_state.specialists:
                    card_rect = pygame.Rect(
                        content_rect.x + self.card_margin,
                        y_offset,
                        content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                        self.card_height
                    )

                    if card_rect.collidepoint(event.pos):
                        self.selected_specialist = specialist
                        return True

                    y_offset += self.card_height + self.card_margin

        return False

    def get_selected_specialist(self) -> Optional[Specialist]:
        """Get currently selected specialist.

        Returns:
            Selected specialist or None
        """
        return self.selected_specialist
