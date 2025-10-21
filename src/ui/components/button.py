"""Modern button component for game UI with gradients and shadows."""

import pygame
from typing import Tuple, Callable, Optional, Any
from enum import Enum

from src.ui.theme_manager import ThemeManager
from src.ui.ui_enhancer import UIEnhancer


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
    ACCENT = "accent"


class ModernButton:
    """Modern button with gradients, shadows, and smooth animations."""

    def __init__(
        self,
        text: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        callback: Callable,
        style: ButtonStyle = ButtonStyle.PRIMARY,
        enabled: bool = True,
        corner_radius: int = 8,
    ):
        """Initialize modern button.

        Args:
            text: Button text
            position: (x, y) position
            size: (width, height) size
            callback: Function to call when clicked
            style: Button style
            enabled: Whether button is enabled
            corner_radius: Corner radius for rounded buttons
        """
        self.text = text
        self.position = position
        self.size = size
        self.callback = callback
        self.style = style
        self.enabled = enabled
        self.corner_radius = corner_radius

        self.state = ButtonState.NORMAL
        self.animation_progress = 0.0  # For smooth transitions
        self.theme_manager = ThemeManager()

        # Create surfaces for rendering
        self._create_surfaces()

        # Font cache
        self._font = None
        self._text_cache = {}

    def _create_surfaces(self) -> None:
        """Create button surfaces for rendering."""
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.shadow_surface = pygame.Surface((self.size[0] + 8, self.size[1] + 8), pygame.SRCALPHA)
        self.glow_surface = pygame.Surface(self.size, pygame.SRCALPHA)

    def _get_state_colors(self) -> dict:
        """Get colors for current button state."""
        theme = self.theme_manager.get_current_theme()
        if not theme:
            # Fallback colors
            return {
                'bg_start': (100, 100, 100),
                'bg_end': (120, 120, 120),
                'border': (150, 150, 150),
                'text': (255, 255, 255),
                'shadow': (0, 0, 0, 40)
            }

        # Base colors for style
        style_colors = {
            ButtonStyle.PRIMARY: {
                'normal': ('primary', 'primary_hover'),
                'hover': ('primary_hover', 'primary_pressed'),
                'pressed': ('primary_pressed', 'primary'),
                'disabled': ('text_muted', 'text_muted')
            },
            ButtonStyle.SECONDARY: {
                'normal': ('secondary', 'secondary_hover'),
                'hover': ('secondary_hover', 'secondary_pressed'),
                'pressed': ('secondary_pressed', 'secondary'),
                'disabled': ('text_muted', 'text_muted')
            },
            ButtonStyle.DANGER: {
                'normal': ('danger', 'danger_hover'),
                'hover': ('danger_hover', 'danger'),
                'pressed': ('danger', 'danger'),
                'disabled': ('text_muted', 'text_muted')
            },
            ButtonStyle.SUCCESS: {
                'normal': ('success', 'success_hover'),
                'hover': ('success_hover', 'success'),
                'pressed': ('success', 'success'),
                'disabled': ('text_muted', 'text_muted')
            },
            ButtonStyle.ACCENT: {
                'normal': ('accent', 'accent_hover'),
                'hover': ('accent_hover', 'accent'),
                'pressed': ('accent', 'accent'),
                'disabled': ('text_muted', 'text_muted')
            }
        }

        state_key = self.state.value
        if state_key not in style_colors[self.style]:
            state_key = 'normal'

        color_keys = style_colors[self.style][state_key]
        bg_start = theme.get_color(color_keys[0])
        bg_end = theme.get_color(color_keys[1])

        return {
            'bg_start': bg_start,
            'bg_end': bg_end,
            'border': theme.get_color('border_hover' if self.state == ButtonState.HOVER else 'border'),
            'text': theme.get_color('text' if self.enabled else 'text_muted'),
            'shadow': theme.get_rgba_color('shadow', (0, 0, 0, 40))
        }

    def _draw_gradient(self, surface: pygame.Surface, rect: pygame.Rect, start_color: Tuple[int, int, int], end_color: Tuple[int, int, int]) -> None:
        """Draw a vertical gradient on surface."""
        for y in range(rect.height):
            # Interpolate between start and end colors
            ratio = y / rect.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)

            pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

    def _draw_shadow(self, surface: pygame.Surface, rect: pygame.Rect, shadow_color: Tuple[int, int, int, int]) -> None:
        """Draw button shadow."""
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_surface.fill(shadow_color)

        # Apply gaussian-like blur effect (simple approximation)
        for i in range(3):
            expanded = pygame.Rect(shadow_rect.x - i, shadow_rect.y - i,
                                 shadow_rect.width + i*2, shadow_rect.height + i*2)
            alpha = int(shadow_color[3] * (1 - i/3))
            temp_surface = pygame.Surface((expanded.width, expanded.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*shadow_color[:3], alpha), temp_surface.get_rect(), border_radius=self.corner_radius + i)
            surface.blit(temp_surface, expanded, special_flags=pygame.BLEND_RGBA_ADD)

    def render(self, screen: pygame.Surface) -> None:
        """Render modern button with gradients and effects.

        Args:
            screen: Pygame surface to render on
        """
        # Get button rect
        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        # Get colors for current state
        colors = self._get_state_colors()

        # Clear surfaces
        self.surface.fill((0, 0, 0, 0))
        self.shadow_surface.fill((0, 0, 0, 0))
        self.glow_surface.fill((0, 0, 0, 0))

        # Draw shadow
        if self.enabled:
            self._draw_shadow(self.shadow_surface, rect, colors['shadow'])
            screen.blit(self.shadow_surface, (rect.x - 2, rect.y - 2))

        # Draw gradient background
        button_rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self._draw_gradient(self.surface, button_rect, colors['bg_start'], colors['bg_end'])

        # Draw border
        pygame.draw.rect(self.surface, colors['border'], button_rect, 1, border_radius=self.corner_radius)

        # Add glow effect for hover/press states
        if self.state in [ButtonState.HOVER, ButtonState.PRESSED] and self.enabled:
            glow_color = (*colors['bg_start'][:3], 30)
            pygame.draw.rect(self.glow_surface, glow_color, button_rect, border_radius=self.corner_radius)
            self.surface.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Draw text
        if self._font is None:
            self._font = self.theme_manager.get_font('body', bold=True)

        text_surface = self._font.render(self.text, True, colors['text'])
        text_rect = text_surface.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
        self.surface.blit(text_surface, text_rect)

        # Blit button surface
        screen.blit(self.surface, self.position)

    def handle_event(self, event: Any) -> bool:
        """Handle mouse events with smooth state transitions.

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
        elif self.state == ButtonState.DISABLED:
            self.state = ButtonState.NORMAL


# Legacy alias for backward compatibility
Button = ModernButton
