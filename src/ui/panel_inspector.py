"""
Panel Inspector for UI development.

Displays information about the currently selected panel (from the layout manager or
debug overlay): name, position, size, constraints, mode, and simple properties.
"""

import pygame
from typing import Optional


class PanelInspector:
    """Simple panel inspector overlay."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enabled = False
        self.font = pygame.font.SysFont('monospace', 14)
        self.small_font = pygame.font.SysFont('monospace', 12)
        self.background_color = (10, 10, 12, 220)
        self.text_color = (230, 230, 230)
        self.padding = 8
        self.width = 360
        self.height = 200

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def render(self, screen: pygame.Surface, panel_info: Optional[dict]) -> None:
        """Render inspector overlay with given panel info.

        Args:
            screen: Pygame surface
            panel_info: Dictionary returned from debug_overlay.get_panel_info()
        """
        if not self.enabled:
            return

        # Position top-right
        x = self.screen_width - self.width - 10
        y = 10

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.background_color)

        title = "Panel Inspector"
        title_surf = self.font.render(title, True, self.text_color)
        overlay.blit(title_surf, (self.padding, self.padding))

        if not panel_info:
            hint = "No panel selected. Click a panel in Debug Overlay to inspect."
            hint_surf = self.small_font.render(hint, True, self.text_color)
            overlay.blit(hint_surf, (self.padding, self.padding + 30))
        else:
            y_off = self.padding + 30
            for key in ("name", "mode", "position", "size", "constraints", "layer"):
                value = panel_info.get(key, "-")
                line = f"{key.capitalize():10s}: {value}"
                surf = self.small_font.render(line, True, self.text_color)
                overlay.blit(surf, (self.padding, y_off))
                y_off += 20

        screen.blit(overlay, (x, y))
