import pygame
from typing import Dict, Any, Callable, Optional

from src.ui.components.base import UIComponent
from src.ui.theme_manager import ThemeManager
from src.ui.detail_panel_renderer import DetailPanelRenderer

class DetailPanel(UIComponent):
    """A UI component that displays detailed information in a modal-like panel."""

    def __init__(self, rect: pygame.Rect, data: Dict[str, Any], on_close: Callable[[], None]):
        super().__init__(rect)
        self.data = data
        self.on_close = on_close
        self.theme = ThemeManager()
        self.renderer = DetailPanelRenderer()

        self.close_button_rect = pygame.Rect(self.rect.right - 35, self.rect.top + 5, 30, 30)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handles events for the detail panel."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                self.on_close()
                return True
            if self.rect.collidepoint(event.pos):
                # The click was inside the panel, so we "handle" it to prevent
                # it from propagating to components underneath.
                return True
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_close()
            return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the detail panel and its contents."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Render the panel itself
        self.renderer.render(screen, self.data, self.rect.x, self.rect.y, self.on_close)

        # Draw a close button over the top
        close_text = pygame.font.SysFont('Arial', 20).render('X', True, self.theme.get_color('text'))
        pygame.draw.rect(screen, self.theme.get_color('danger'), self.close_button_rect, border_radius=5)
        screen.blit(close_text, (self.close_button_rect.x + 9, self.close_button_rect.y + 5))
