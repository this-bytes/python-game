"""Dropdown component for game UI."""

import pygame
from typing import Tuple, List, Optional, Callable, Any


class Dropdown:
    """Dropdown menu with selectable options."""

    def __init__(
        self,
        position: Tuple[int, int],
        width: int,
        options: List[str],
        selected_index: int = 0,
        on_select: Optional[Callable[[int, str], None]] = None,
    ):
        """Initialize dropdown."""
        self.position = position
        self.width = width
        self.height = 30
        self.options = options
        self.selected_index = selected_index
        self.on_select = on_select
        self.is_open = False

        self.bg_color = (255, 255, 255)
        self.border_color = (150, 150, 150)
        self.text_color = (0, 0, 0)
        self.hover_color = (230, 230, 230)

        self.font = None

    def render(self, screen: pygame.Surface) -> None:
        """Render dropdown."""
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 14)

        rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)

        # Draw main button
        pygame.draw.rect(screen, self.bg_color, rect, border_radius=2)
        pygame.draw.rect(screen, self.border_color, rect, 2, border_radius=2)

        # Draw selected option
        if self.selected_index < len(self.options):
            text = self.options[self.selected_index]
            text_surface = self.font.render(text, True, self.text_color)
            screen.blit(text_surface, (rect.x + 5, rect.y + (self.height - text_surface.get_height()) // 2))

        # Draw dropdown arrow
        arrow_points = [
            (rect.right - 20, rect.centery - 3),
            (rect.right - 10, rect.centery - 3),
            (rect.right - 15, rect.centery + 3),
        ]
        pygame.draw.polygon(screen, self.text_color, arrow_points)

        # Draw options if open
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    rect.x,
                    rect.y + self.height + i * self.height,
                    rect.width,
                    self.height
                )
                pygame.draw.rect(screen, self.bg_color, option_rect)
                pygame.draw.rect(screen, self.border_color, option_rect, 1)

                text_surface = self.font.render(option, True, self.text_color)
                screen.blit(text_surface, (option_rect.x + 5, option_rect.y + 7))

    def handle_event(self, event: Any) -> bool:
        """Handle mouse events."""
        rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            if self.is_open:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(
                        rect.x,
                        rect.y + self.height + i * self.height,
                        rect.width,
                        self.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        if self.on_select:
                            self.on_select(i, self.options[i])
                        self.is_open = False
                        return True

                self.is_open = False

        return False
