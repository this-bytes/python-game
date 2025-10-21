"""UI Enhancement system - Professional visual improvements for all UI components."""

import pygame
from typing import Tuple, Optional, List
from enum import Enum


class ShadowQuality(Enum):
    """Shadow rendering quality levels."""
    NONE = 0
    SOFT = 1
    MEDIUM = 2
    HARD = 3


class UIEnhancer:
    """Professional UI enhancement utilities."""

    # Shadow presets (offset_x, offset_y, blur_radius, alpha)
    SHADOW_PRESETS = {
        'subtle': (1, 2, 4, 30),
        'soft': (2, 4, 8, 40),
        'medium': (3, 6, 12, 50),
        'hard': (4, 8, 16, 60),
        'dialog': (0, 8, 24, 80),
    }

    @staticmethod
    def draw_rounded_rect_with_shadow(
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: Tuple[int, int, int],
        radius: int = 8,
        shadow_quality: str = 'medium',
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 1,
    ) -> None:
        """Draw a rounded rectangle with professional shadow effect.

        Args:
            surface: Target surface to draw on
            rect: Rectangle bounds
            color: Fill color (RGB)
            radius: Corner radius
            shadow_quality: Shadow quality preset ('subtle', 'soft', 'medium', 'hard', 'dialog')
            border_color: Optional border color
            border_width: Border thickness
        """
        if shadow_quality in UIEnhancer.SHADOW_PRESETS:
            offset_x, offset_y, blur, alpha = UIEnhancer.SHADOW_PRESETS[shadow_quality]
            UIEnhancer._draw_drop_shadow(
                surface, rect, radius, blur, alpha, offset_x, offset_y
            )

        # Draw main rectangle
        pygame.draw.rect(surface, color, rect, border_radius=radius)

        # Draw border if specified
        if border_color:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)

    @staticmethod
    def _draw_drop_shadow(
        surface: pygame.Surface,
        rect: pygame.Rect,
        radius: int,
        blur_radius: int,
        alpha: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Draw a drop shadow effect.

        Args:
            surface: Target surface
            rect: Rectangle to shadow
            radius: Corner radius
            blur_radius: Blur amount
            alpha: Shadow alpha
            offset_x: Horizontal offset
            offset_y: Vertical offset
        """
        shadow_color = (0, 0, 0, min(alpha, 255))

        # Create shadow surface
        shadow_size = (rect.width + blur_radius * 2, rect.height + blur_radius * 2)
        shadow_surf = pygame.Surface(shadow_size, pygame.SRCALPHA)

        # Draw shadow shape
        shadow_rect = pygame.Rect(blur_radius, blur_radius, rect.width, rect.height)
        pygame.draw.rect(shadow_surf, shadow_color, shadow_rect, border_radius=radius)

        # Simple blur approximation (multi-pass)
        for _ in range(max(1, blur_radius // 2)):
            pygame.transform.smoothscale(shadow_surf, shadow_size, shadow_surf)

        # Blit shadow to target
        shadow_pos = (rect.x - blur_radius + offset_x, rect.y - blur_radius + offset_y)
        surface.blit(shadow_surf, shadow_pos, special_flags=pygame.BLEND_RGBA_MULT)

    @staticmethod
    def draw_gradient_rect(
        surface: pygame.Surface,
        rect: pygame.Rect,
        color_start: Tuple[int, int, int],
        color_end: Tuple[int, int, int],
        horizontal: bool = False,
        radius: int = 0,
    ) -> None:
        """Draw a gradient-filled rectangle.

        Args:
            surface: Target surface
            rect: Rectangle bounds
            color_start: Start color (RGB)
            color_end: End color (RGB)
            horizontal: If True, gradient goes left-to-right; else top-to-bottom
            radius: Corner radius for rounded rectangle (0 = square)
        """
        if horizontal:
            for x in range(rect.width):
                ratio = x / max(rect.width, 1)
                r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
                pygame.draw.line(
                    surface, (r, g, b),
                    (rect.x + x, rect.y),
                    (rect.x + x, rect.y + rect.height)
                )
        else:
            for y in range(rect.height):
                ratio = y / max(rect.height, 1)
                r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
                pygame.draw.line(
                    surface, (r, g, b),
                    (rect.x, rect.y + y),
                    (rect.x + rect.width, rect.y + y)
                )

    @staticmethod
    def draw_glow_effect(
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: Tuple[int, int, int],
        intensity: float = 0.3,
        radius: int = 8,
    ) -> None:
        """Draw a subtle glow effect around a rectangle.

        Args:
            surface: Target surface
            rect: Rectangle bounds
            color: Glow color (RGB)
            intensity: Glow intensity (0.0-1.0)
            radius: Glow radius in pixels
        """
        alpha = int(255 * intensity)
        glow_surf = pygame.Surface(
            (rect.width + radius * 2, rect.height + radius * 2),
            pygame.SRCALPHA
        )

        glow_rect = pygame.Rect(radius, radius, rect.width, rect.height)
        pygame.draw.rect(
            glow_surf,
            (*color, alpha),
            glow_rect,
            border_radius=radius // 2
        )

        # Multi-pass blur effect
        for _ in range(2):
            glow_surf = pygame.transform.smoothscale(
                glow_surf,
                (glow_surf.get_width(), glow_surf.get_height())
            )

        surface.blit(
            glow_surf,
            (rect.x - radius, rect.y - radius),
            special_flags=pygame.BLEND_RGBA_ADD
        )

    @staticmethod
    def draw_text_with_shadow(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        pos: Tuple[int, int],
        color: Tuple[int, int, int],
        shadow_color: Tuple[int, int, int] = (0, 0, 0),
        shadow_offset: Tuple[int, int] = (1, 1),
    ) -> pygame.Rect:
        """Draw text with a drop shadow for better contrast.

        Args:
            surface: Target surface
            text: Text to render
            font: Pygame font object
            pos: Position (x, y)
            color: Text color (RGB)
            shadow_color: Shadow color (RGB)
            shadow_offset: Shadow offset (x, y)

        Returns:
            Rect of rendered text
        """
        # Draw shadow
        shadow_surf = font.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect()
        shadow_rect.topleft = (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1])
        surface.blit(shadow_surf, shadow_rect)

        # Draw text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        text_rect.topleft = pos
        surface.blit(text_surf, text_rect)

        return text_rect

    @staticmethod
    def draw_progress_bar(
        surface: pygame.Surface,
        rect: pygame.Rect,
        value: float,  # 0.0 to 1.0
        bg_color: Tuple[int, int, int] = (40, 40, 40),
        fg_color_start: Tuple[int, int, int] = (0, 200, 100),
        fg_color_end: Tuple[int, int, int] = (0, 150, 80),
        border_color: Tuple[int, int, int] = (100, 100, 100),
        border_width: int = 1,
        radius: int = 4,
    ) -> None:
        """Draw a modern progress bar with gradient fill.

        Args:
            surface: Target surface
            rect: Progress bar bounds
            value: Fill percentage (0.0 to 1.0)
            bg_color: Background color (RGB)
            fg_color_start: Foreground start color (RGB)
            fg_color_end: Foreground end color (RGB)
            border_color: Border color (RGB)
            border_width: Border thickness
            radius: Corner radius
        """
        # Draw background
        pygame.draw.rect(surface, bg_color, rect, border_radius=radius)

        # Draw filled portion with gradient
        if value > 0:
            fill_width = int(rect.width * min(max(value, 0.0), 1.0))
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)

            UIEnhancer.draw_gradient_rect(
                surface, fill_rect, fg_color_start, fg_color_end, horizontal=True, radius=radius
            )

        # Draw border
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)

    @staticmethod
    def draw_panel_background(
        surface: pygame.Surface,
        rect: pygame.Rect,
        color_start: Tuple[int, int, int] = (30, 35, 42),
        color_end: Tuple[int, int, int] = (25, 30, 37),
        border_color: Tuple[int, int, int] = (48, 54, 61),
        radius: int = 8,
    ) -> None:
        """Draw a professional panel background.

        Args:
            surface: Target surface
            rect: Panel bounds
            color_start: Background start color
            color_end: Background end color
            border_color: Border color
            radius: Corner radius
        """
        # Draw shadow first (below panel)
        UIEnhancer.draw_rounded_rect_with_shadow(
            surface, rect, color_start, radius, 'medium', border_color, 2
        )

        # Draw gradient background
        UIEnhancer.draw_gradient_rect(surface, rect, color_start, color_end, radius=radius)

        # Draw border
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=radius)

    @staticmethod
    def create_button_surface(
        width: int,
        height: int,
        color_start: Tuple[int, int, int],
        color_end: Tuple[int, int, int],
        border_color: Tuple[int, int, int],
        radius: int = 8,
    ) -> pygame.Surface:
        """Create a pre-rendered button surface for performance.

        Args:
            width: Button width
            height: Button height
            color_start: Gradient start color
            color_end: Gradient end color
            border_color: Border color
            radius: Corner radius

        Returns:
            Pre-rendered pygame Surface
        """
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw background with gradient
        rect = pygame.Rect(0, 0, width, height)
        UIEnhancer.draw_gradient_rect(surf, rect, color_start, color_end, radius=radius)

        # Draw border
        pygame.draw.rect(surf, border_color, rect, 2, border_radius=radius)

        return surf


# Convenience functions
def enhance_button_visuals(button_instance) -> None:
    """Enhance a button instance with professional styling.

    Args:
        button_instance: ModernButton instance to enhance
    """
    # This is a utility function for batch-enhancing buttons
    # Buttons already have modern rendering, so this is mostly for future extensibility
    pass


def enhance_panel_visuals(panel_instance) -> None:
    """Enhance a panel instance with professional styling.

    Args:
        panel_instance: ModernPanel instance to enhance
    """
    # Panels already have gradient support, add future enhancements here
    pass
