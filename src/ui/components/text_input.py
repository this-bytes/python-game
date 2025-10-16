"""Text input component for game UI."""

import pygame
from typing import Tuple, Optional, Any


class TextInput:
    """Single-line text input field."""

    def __init__(
        self,
        position: Tuple[int, int],
        width: int,
        placeholder: str = "",
        initial_text: str = "",
    ):
        """Initialize text input.

        Args:
            position: (x, y) position
            width: Width of input field
            placeholder: Placeholder text when empty
            initial_text: Initial text content
        """
        self.position = position
        self.width = width
        self.height = 30
        self.placeholder = placeholder
        self.text = initial_text

        self.focused = False
        self.cursor_pos = len(initial_text)
        self.cursor_visible = True
        self.cursor_timer = 0

        # Colors
        self.bg_color = (255, 255, 255)
        self.border_color = (150, 150, 150)
        self.focus_border_color = (0, 120, 215)
        self.text_color = (0, 0, 0)
        self.placeholder_color = (150, 150, 150)

        self.font = None

    def render(self, screen: pygame.Surface) -> None:
        """Render text input."""
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 14)

        rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)

        # Draw background
        pygame.draw.rect(screen, self.bg_color, rect, border_radius=2)

        # Draw border
        border_color = self.focus_border_color if self.focused else self.border_color
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=2)

        # Draw text or placeholder
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
        else:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)

        screen.blit(text_surface, (rect.x + 5, rect.y + (self.height - text_surface.get_height()) // 2))

        # Draw cursor if focused
        if self.focused and self.cursor_visible:
            cursor_x = rect.x + 5 + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(
                screen,
                self.text_color,
                (cursor_x, rect.y + 5),
                (cursor_x, rect.y + self.height - 5),
                2
            )

    def handle_event(self, event: Any) -> bool:
        """Handle keyboard/mouse events."""
        rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                self.focused = True
                return True
            else:
                self.focused = False
                return False

        if not self.focused:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                return True
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                return True
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                return True
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                return True
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                return True

        return False

    def update(self, delta_time: float) -> None:
        """Update cursor blink animation."""
        self.cursor_timer += delta_time
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def get_text(self) -> str:
        """Get current text."""
        return self.text

    def set_text(self, text: str) -> None:
        """Set text content."""
        self.text = text
        self.cursor_pos = len(text)
