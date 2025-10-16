"""Tooltip component for game UI."""

import pygame
from typing import Tuple, Optional


class Tooltip:
    """Hover tooltip with delay."""

    def __init__(self, text: str, delay: float = 0.5):
        """Initialize tooltip."""
        self.text = text
        self.delay = delay
        self.visible = False
        self.position = (0, 0)
        self.hover_time = 0

        self.bg_color = (40, 40, 40)
        self.text_color = (255, 255, 255)
        self.border_color = (200, 200, 200)

        self.font = None
        self.surface = None

    def update(self, delta_time: float, mouse_pos: Tuple[int, int], is_hovering: bool) -> None:
        """Update tooltip state."""
        if is_hovering:
            self.hover_time += delta_time
            if self.hover_time >= self.delay:
                self.visible = True
                self.position = (mouse_pos[0] + 10, mouse_pos[1] + 10)
        else:
            self.hover_time = 0
            self.visible = False

    def render(self, screen: pygame.Surface) -> None:
        """Render tooltip."""
        if not self.visible:
            return

        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 12)

        if self.surface is None:
            text_surface = self.font.render(self.text, True, self.text_color)
            self.surface = pygame.Surface((text_surface.get_width() + 16, text_surface.get_height() + 12))
            self.surface.fill(self.bg_color)
            self.surface.blit(text_surface, (8, 6))
            pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), 1)

        screen.blit(self.surface, self.position)
