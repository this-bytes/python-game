"""Button component for game UI.

Interactive button with multiple states and styles.
"""

import pygame
from typing import Tuple, Callable, Optional
from enum import Enum


class ButtonState(Enum):
    """Button interaction state."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


class ButtonStyle(Enum):
    """Button visual style."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    SUCCESS = "success"


class Button:
    """Interactive button with states."""

    def __init__(
        self,
        text: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        callback: Callable,
        style: ButtonStyle = ButtonStyle.PRIMARY,
        enabled: bool = True,
    ):
        """Initialize button.

        Args:
            text: Button text
            position: (x, y) position
            size: (width, height) size
            callback: Function to call when clicked
            style: Button style
            enabled: Whether button is enabled
        """
        self.text = text
        self.position = position
        self.size = size
        self.callback = callback
        self.style = style
        self.enabled = enabled

        self.state = ButtonState.NORMAL

        # Style colors (will be overridden by theme)
        self.colors = {
            ButtonStyle.PRIMARY: {
                ButtonState.NORMAL: (0, 120, 215),
                ButtonState.HOVER: (0, 150, 255),
                ButtonState.PRESSED: (0, 90, 180),
                ButtonState.DISABLED: (100, 100, 100),
            },
            ButtonStyle.SECONDARY: {
                ButtonState.NORMAL: (100, 100, 100),
                ButtonState.HOVER: (130, 130, 130),
                ButtonState.PRESSED: (70, 70, 70),
                ButtonState.DISABLED: (100, 100, 100),
            },
            ButtonStyle.DANGER: {
                ButtonState.NORMAL: (200, 0, 0),
                ButtonState.HOVER: (255, 50, 50),
                ButtonState.PRESSED: (150, 0, 0),
                ButtonState.DISABLED: (100, 100, 100),
            },
            ButtonStyle.SUCCESS: {
                ButtonState.NORMAL: (0, 150, 0),
                ButtonState.HOVER: (0, 200, 0),
                ButtonState.PRESSED: (0, 100, 0),
                ButtonState.DISABLED: (100, 100, 100),
            },
        }

        self.text_color = (255, 255, 255)
        self.disabled_text_color = (150, 150, 150)

        # Font
        self.font = None

    def render(self, screen: pygame.Surface) -> None:
        """Render button.

        Args:
            screen: Pygame surface to render on
        """
        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 14)

        # Get button rect
        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        # Get button color based on state
        state = ButtonState.DISABLED if not self.enabled else self.state
        color = self.colors[self.style][state]

        # Draw button
        pygame.draw.rect(screen, color, rect, border_radius=4)

        # Draw border
        border_color = (200, 200, 200) if self.enabled else (100, 100, 100)
        pygame.draw.rect(screen, border_color, rect, 1, border_radius=4)

        # Draw text
        text_color = self.text_color if self.enabled else self.disabled_text_color
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.Event) -> bool:
        """Handle mouse events.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed, False otherwise
        """
        if not self.enabled:
            return False

        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        if event.type == pygame.MOUSEMOTION:
            if rect.collidepoint(event.pos):
                if self.state != ButtonState.PRESSED:
                    self.state = ButtonState.HOVER
                return True
            else:
                if self.state != ButtonState.PRESSED:
                    self.state = ButtonState.NORMAL
                return False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                self.state = ButtonState.PRESSED
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self.state == ButtonState.PRESSED
                if rect.collidepoint(event.pos):
                    self.state = ButtonState.HOVER
                    if was_pressed and self.callback:
                        self.callback()
                        return True
                else:
                    self.state = ButtonState.NORMAL
                return was_pressed

        return False

    def set_enabled(self, enabled: bool) -> None:
        """Set button enabled state.

        Args:
            enabled: Whether button is enabled
        """
        self.enabled = enabled
        if not enabled:
            self.state = ButtonState.DISABLED
        else:
            self.state = ButtonState.NORMAL
