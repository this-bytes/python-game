"""Progress bar component for game UI."""

import pygame
from typing import Tuple, Optional


class ProgressBar:
    """Horizontal/vertical progress bar with labels."""

    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        value: float = 0.0,
        max_value: float = 100.0,
        show_label: bool = True,
        vertical: bool = False,
    ):
        """Initialize progress bar."""
        self.position = position
        self.size = size
        self.value = value
        self.max_value = max_value
        self.show_label = show_label
        self.vertical = vertical

        self.bg_color = (100, 100, 100)
        self.fill_color = (0, 200, 100)
        self.border_color = (50, 50, 50)
        self.text_color = (255, 255, 255)

        self.font = None

    def render(self, screen: pygame.Surface) -> None:
        """Render progress bar."""
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 12)

        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        # Draw background
        pygame.draw.rect(screen, self.bg_color, rect, border_radius=2)

        # Draw progress
        progress = min(1.0, self.value / self.max_value) if self.max_value > 0 else 0

        if not self.vertical:
            fill_width = int(rect.width * progress)
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        else:
            fill_height = int(rect.height * progress)
            fill_rect = pygame.Rect(rect.x, rect.y + rect.height - fill_height, rect.width, fill_height)

        pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=2)

        # Draw border
        pygame.draw.rect(screen, self.border_color, rect, 1, border_radius=2)

        # Draw label
        if self.show_label:
            label_text = f"{int(self.value)}/{int(self.max_value)}"
            text_surface = self.font.render(label_text, True, self.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

    def set_value(self, value: float) -> None:
        """Set progress value."""
        self.value = max(0, min(self.max_value, value))

    def set_max_value(self, max_value: float) -> None:
        """Set maximum value."""
        self.max_value = max(0, max_value)
