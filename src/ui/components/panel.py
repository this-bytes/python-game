"""Modern panel component for game UI with gradients and shadows."""

import pygame
from typing import Tuple, Optional, Any, Union
from enum import Enum

from src.ui.theme_manager import ThemeManager


class PanelState(Enum):
    """Panel display state."""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"


class ModernPanel:
    """Modern draggable, resizable window panel with gradients and shadows."""

    # Default styling
    TITLE_BAR_HEIGHT = 32
    BORDER_WIDTH = 1
    BUTTON_SIZE = 20
    BUTTON_MARGIN = 6
    MIN_WIDTH = 200
    MIN_HEIGHT = 100
    CORNER_RADIUS = 8

    def __init__(
        self,
        title: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        closeable: bool = True,
        minimizable: bool = True,
        maximizable: bool = False,
        draggable: bool = True,
        resizable: bool = False,
        # Layout system integration (optional)
        layout_mode: Optional[str] = None,
        layout_constraints: Optional[Any] = None,
        layer: int = 10,  # UILayer.PANELS
        responsive: bool = True,
        collision_behavior: Optional[str] = None,
    ):
        """Initialize modern panel.

        Args:
            title: Panel title displayed in title bar
            position: Initial (x, y) position
            size: Initial (width, height) size
            closeable: Whether panel can be closed
            minimizable: Whether panel can be minimized
            maximizable: Whether panel can be maximized
            draggable: Whether panel can be dragged
            resizable: Whether panel can be resized
            layout_mode: Layout mode (grid, anchored, floating, fixed)
            layout_constraints: Layout constraints object
            layer: Rendering layer (higher = on top)
            responsive: Whether panel responds to window resize
            collision_behavior: How to handle collisions (overlap, push, block, resize)
        """
        self.title = title
        self.position = list(position)
        self.size = list(size)
        self.closeable = closeable
        self.minimizable = minimizable
        self.maximizable = maximizable
        self.draggable = draggable
        self.resizable = resizable

        self.state = PanelState.NORMAL
        self.visible = True
        self.z_order = 0

        # Layout system integration
        self.layout_mode = layout_mode
        self.layout_constraints = layout_constraints
        self.layer = layer
        self.responsive = responsive
        self.collision_behavior = collision_behavior or "overlap"
        self._managed_by_layout = layout_mode is not None

        # Drag state
        self.is_dragging = False
        self.drag_offset = (0, 0)

        # Resize state
        self.is_resizing = False
        self.resize_start_pos = (0, 0)
        self.resize_start_size = (0, 0)

        # Saved state for maximize/restore
        self.saved_position = None
        self.saved_size = None

        # Theme integration
        self.theme_manager = ThemeManager()

        # Create surfaces for advanced rendering
        self._create_surfaces()

        # Font cache
        self._font = None
        self._title_font = None

    def _create_surfaces(self) -> None:
        """Create surfaces for advanced rendering effects."""
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.shadow_surface = pygame.Surface((self.size[0] + 16, self.size[1] + 16), pygame.SRCALPHA)
        self.title_surface = pygame.Surface((self.size[0], self.TITLE_BAR_HEIGHT), pygame.SRCALPHA)

    def _get_panel_colors(self) -> dict:
        """Get colors for panel rendering from theme."""
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return {
                'bg_start': (30, 35, 42),
                'bg_end': (25, 30, 37),
                'title_start': (0, 122, 255),
                'title_end': (0, 100, 220),
                'border': (48, 54, 61),
                'text': (201, 209, 217),
                'button': (139, 148, 158),
                'button_hover': (201, 209, 217),
                'close_button': (248, 81, 73),
                'shadow': (0, 0, 0, 60)
            }

        return {
            'bg_start': theme.get_color('panel_bg'),
            'bg_end': theme.get_color('panel_bg_hover'),
            'title_start': theme.get_color('primary'),
            'title_end': theme.get_color('primary_hover'),
            'border': theme.get_color('border'),
            'text': theme.get_color('text'),
            'button': theme.get_color('text_secondary'),
            'button_hover': theme.get_color('text'),
            'close_button': theme.get_color('danger'),
            'shadow': theme.get_rgba_color('shadow', (0, 0, 0, 60))
        }

    def _draw_gradient(self, surface: pygame.Surface, rect: pygame.Rect, start_color: Tuple[int, int, int], end_color: Tuple[int, int, int]) -> None:
        """Draw a vertical gradient on surface."""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

    def _draw_shadow(self, surface: pygame.Surface, rect: pygame.Rect, shadow_color: Tuple[int, int, int, int]) -> None:
        """Draw panel shadow with blur effect."""
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)

        # Multi-layer shadow for depth
        for i in range(4):
            expanded = pygame.Rect(
                shadow_rect.x - i, shadow_rect.y - i,
                shadow_rect.width + i*2, shadow_rect.height + i*2
            )
            alpha = int(shadow_color[3] * (1 - i/4))
            temp_surface = pygame.Surface((expanded.width, expanded.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*shadow_color[:3], alpha), temp_surface.get_rect(), border_radius=self.CORNER_RADIUS + i)
            surface.blit(temp_surface, expanded, special_flags=pygame.BLEND_RGBA_ADD)

    def render(self, screen: pygame.Surface) -> None:
        """Render modern panel with gradients and shadows.

        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return

        # Initialize fonts if needed
        if self._font is None:
            self._font = self.theme_manager.get_font('body')
        if self._title_font is None:
            self._title_font = self.theme_manager.get_font('heading', bold=True)

        if self.state == PanelState.MINIMIZED:
            self._render_minimized(screen)
            return

        # Get panel rect and colors
        rect = self.get_rect()
        colors = self._get_panel_colors()

        # Clear surfaces
        self.surface.fill((0, 0, 0, 0))
        self.shadow_surface.fill((0, 0, 0, 0))
        self.title_surface.fill((0, 0, 0, 0))

        # Draw shadow
        self._draw_shadow(self.shadow_surface, rect, colors['shadow'])
        screen.blit(self.shadow_surface, (rect.x - 4, rect.y - 4))

        # Draw panel background gradient
        panel_rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self._draw_gradient(self.surface, panel_rect, colors['bg_start'], colors['bg_end'])

        # Draw border
        pygame.draw.rect(self.surface, colors['border'], panel_rect, self.BORDER_WIDTH, border_radius=self.CORNER_RADIUS)

        # Draw title bar gradient
        title_rect = pygame.Rect(0, 0, self.size[0], self.TITLE_BAR_HEIGHT)
        self._draw_gradient(self.title_surface, title_rect, colors['title_start'], colors['title_end'])

        # Draw title bar border
        pygame.draw.rect(self.title_surface, colors['border'], title_rect, 1, border_radius=self.CORNER_RADIUS)

        # Draw title text
        title_text = self._title_font.render(self.title, True, colors['text'])
        text_y = (self.TITLE_BAR_HEIGHT - title_text.get_height()) // 2
        self.title_surface.blit(title_text, (12, text_y))

        # Draw control buttons
        self._render_control_buttons(self.title_surface, colors)

        # Composite surfaces
        self.surface.blit(self.title_surface, (0, 0))

        # Blit to screen
        screen.blit(self.surface, self.position)

        # Render content area
        content_rect = pygame.Rect(
            rect.x + self.BORDER_WIDTH,
            rect.y + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
            rect.width - 2 * self.BORDER_WIDTH,
            rect.height - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
        )
        self.render_content(screen, content_rect)

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render panel content. Override in subclasses.

        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Default implementation - empty panel
        pass

    def _render_minimized(self, screen: pygame.Surface) -> None:
        """Render minimized panel (title bar only)."""
        colors = self._get_panel_colors()
        rect = pygame.Rect(self.position[0], self.position[1], 200, self.TITLE_BAR_HEIGHT)

        # Draw shadow
        shadow_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        self._draw_shadow(shadow_surface, rect, colors['shadow'])
        screen.blit(shadow_surface, (rect.x - 4, rect.y - 4))

        # Draw title bar
        pygame.draw.rect(screen, colors['title_start'], rect, border_radius=self.CORNER_RADIUS)

        # Draw title text
        title_text = self._title_font.render(self.title, True, colors['text'])
        text_y = (self.TITLE_BAR_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (rect.x + 12, rect.y + text_y))

        # Draw restore button
        button_x = rect.x + rect.width - self.BUTTON_SIZE - self.BUTTON_MARGIN
        button_rect = pygame.Rect(button_x, rect.y + 6, self.BUTTON_SIZE, self.BUTTON_SIZE)
        pygame.draw.rect(screen, colors['button'], button_rect, border_radius=3)
        pygame.draw.rect(screen, colors['border'], button_rect, 1, border_radius=3)

    def _render_control_buttons(self, surface: pygame.Surface, colors: dict) -> None:
        """Render minimize, maximize, close buttons."""
        button_x = self.size[0] - self.BUTTON_SIZE - self.BUTTON_MARGIN

        # Close button
        if self.closeable:
            close_rect = pygame.Rect(button_x, 6, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(surface, colors['close_button'], close_rect, border_radius=3)
            pygame.draw.rect(surface, colors['border'], close_rect, 1, border_radius=3)
            button_x -= self.BUTTON_SIZE + 2

        # Maximize button
        if self.maximizable:
            max_rect = pygame.Rect(button_x, 6, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(surface, colors['button'], max_rect, border_radius=3)
            pygame.draw.rect(surface, colors['border'], max_rect, 1, border_radius=3)
            button_x -= self.BUTTON_SIZE + 2

        # Minimize button
        if self.minimizable:
            min_rect = pygame.Rect(button_x, 6, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(surface, colors['button'], min_rect, border_radius=3)
            pygame.draw.rect(surface, colors['border'], min_rect, 1, border_radius=3)

    def handle_event(self, event: Any) -> bool:
        """Handle mouse events.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)

        return False

    def _handle_mouse_down(self, event: Any) -> bool:
        """Handle mouse button down event."""
        if event.button != 1:  # Left click only
            return False

        pos = event.pos
        rect = self.get_rect()

        if self.state == PanelState.MINIMIZED:
            # Check restore button
            button_rect = pygame.Rect(
                rect.x + 200 - self.BUTTON_SIZE - self.BUTTON_MARGIN,
                rect.y + 5,
                self.BUTTON_SIZE,
                self.BUTTON_SIZE
            )
            if button_rect.collidepoint(pos):
                self.restore()
                return True
            return False

        # Check if click is in panel
        if not rect.collidepoint(pos):
            return False

        # Check control buttons
        if self._check_control_button_click(pos, rect):
            return True

        # Check title bar for dragging
        title_rect = pygame.Rect(rect.x, rect.y, rect.width, self.TITLE_BAR_HEIGHT)
        if title_rect.collidepoint(pos) and self.draggable:
            self.is_dragging = True
            self.drag_offset = (pos[0] - self.position[0], pos[1] - self.position[1])
            self.bring_to_front()
            return True

        # Check resize handle (bottom-right corner)
        if self.resizable:
            resize_rect = pygame.Rect(
                rect.x + rect.width - 20,
                rect.y + rect.height - 20,
                20,
                20
            )
            if resize_rect.collidepoint(pos):
                self.is_resizing = True
                self.resize_start_pos = pos
                self.resize_start_size = self.size.copy()
                return True

        # Event consumed by panel (click inside)
        return True

    def _handle_mouse_up(self, event: Any) -> bool:
        """Handle mouse button up event."""
        if event.button != 1:
            return False

        was_dragging = self.is_dragging
        was_resizing = self.is_resizing

        self.is_dragging = False
        self.is_resizing = False

        return was_dragging or was_resizing

    def _handle_mouse_motion(self, event: Any) -> bool:
        """Handle mouse motion event."""
        if self.is_dragging:
            self.position[0] = event.pos[0] - self.drag_offset[0]
            self.position[1] = event.pos[1] - self.drag_offset[1]
            return True

        if self.is_resizing:
            delta_x = event.pos[0] - self.resize_start_pos[0]
            delta_y = event.pos[1] - self.resize_start_pos[1]
            self.size[0] = max(self.MIN_WIDTH, self.resize_start_size[0] + delta_x)
            self.size[1] = max(self.MIN_HEIGHT, self.resize_start_size[1] + delta_y)
            return True

        return False

    def _check_control_button_click(self, pos: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Check if control button was clicked."""
        button_x = rect.x + rect.width - self.BUTTON_SIZE - self.BUTTON_MARGIN

        # Close button
        if self.closeable:
            close_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if close_rect.collidepoint(pos):
                self.close()
                return True
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Maximize button
        if self.maximizable:
            max_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if max_rect.collidepoint(pos):
                if self.state == PanelState.MAXIMIZED:
                    self.restore()
                else:
                    self.maximize()
                return True
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Minimize button
        if self.minimizable:
            min_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if min_rect.collidepoint(pos):
                self.minimize()
                return True

        return False

    def get_rect(self) -> pygame.Rect:
        """Get panel rectangle."""
        if self.state == PanelState.MINIMIZED:
            return pygame.Rect(self.position[0], self.position[1], 200, self.TITLE_BAR_HEIGHT)
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    @property
    def rect(self) -> pygame.Rect:
        """Get panel rectangle as property."""
        return self.get_rect()

    def bring_to_front(self) -> None:
        """Bring panel to front (z-order management handled by parent)."""
        pass

    def close(self) -> None:
        """Close panel."""
        self.visible = False

    def minimize(self) -> None:
        """Minimize panel."""
        if self.state != PanelState.MINIMIZED:
            self.state = PanelState.MINIMIZED

    def maximize(self) -> None:
        """Maximize panel."""
        if self.state != PanelState.MAXIMIZED:
            self.saved_position = self.position.copy()
            self.saved_size = self.size.copy()
            self.state = PanelState.MAXIMIZED
            # Position and size will be set by parent based on screen size

    def restore(self) -> None:
        """Restore panel to normal state."""
        if self.state == PanelState.MAXIMIZED and self.saved_position and self.saved_size:
            self.position = self.saved_position
            self.size = self.saved_size
        self.state = PanelState.NORMAL

    def set_position(self, x: int, y: int) -> None:
        """Set panel position.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.position = [x, y]

    def set_size(self, width: int, height: int) -> None:
        """Set panel size.

        Args:
            width: Panel width
            height: Panel height
        """
        self.size = [max(width, self.MIN_WIDTH), max(height, self.MIN_HEIGHT)]

    def get_bounds(self) -> pygame.Rect:
        """Get panel bounds for collision detection.

        Returns:
            Rectangle representing panel bounds
        """
        return self.get_rect()

    def check_collision(self, other: 'ModernPanel') -> bool:
        """Check if this panel collides with another.

        Args:
            other: Other panel to check

        Returns:
            True if panels overlap
        """
        return self.get_bounds().colliderect(other.get_bounds())

    def set_layout_constraints(self, constraints: Any, layout_mode: str) -> None:
        """Set layout constraints for this panel.

        Args:
            constraints: Layout constraints object (GridConstraints, AnchorConstraints, etc.)
            layout_mode: Layout mode string ('grid', 'anchored', 'floating', 'fixed')
        """
        self.layout_constraints = constraints
        self.layout_mode = layout_mode
        self._managed_by_layout = True

    def set_theme_colors(self, theme: dict) -> None:
        """Apply theme colors to panel.

        Args:
            theme: Theme dictionary with color definitions
        """
        # Theme colors are handled automatically through ThemeManager
        pass

        # Check resize handle (bottom-right corner)
        if self.resizable:
            resize_rect = pygame.Rect(
                rect.x + rect.width - 20,
                rect.y + rect.height - 20,
                20,
                20
            )
            if resize_rect.collidepoint(pos):
                self.is_resizing = True
                self.resize_start_pos = pos
                self.resize_start_size = self.size.copy()
                return True

        # Event consumed by panel (click inside)
        return True

    def _handle_mouse_up(self, event: Any) -> bool:
        """Handle mouse button up event."""
        if event.button != 1:
            return False

        was_dragging = self.is_dragging
        was_resizing = self.is_resizing

        self.is_dragging = False
        self.is_resizing = False

        return was_dragging or was_resizing

    def _handle_mouse_motion(self, event: Any) -> bool:
        """Handle mouse motion event."""
        if self.is_dragging:
            self.position[0] = event.pos[0] - self.drag_offset[0]
            self.position[1] = event.pos[1] - self.drag_offset[1]
            return True

        if self.is_resizing:
            delta_x = event.pos[0] - self.resize_start_pos[0]
            delta_y = event.pos[1] - self.resize_start_pos[1]
            self.size[0] = max(self.MIN_WIDTH, self.resize_start_size[0] + delta_x)
            self.size[1] = max(self.MIN_HEIGHT, self.resize_start_size[1] + delta_y)
            return True

        return False

    def _check_control_button_click(self, pos: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Check if control button was clicked."""
        button_x = rect.x + rect.width - self.BUTTON_SIZE - self.BUTTON_MARGIN

        # Close button
        if self.closeable:
            close_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if close_rect.collidepoint(pos):
                self.close()
                return True
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Maximize button
        if self.maximizable:
            max_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if max_rect.collidepoint(pos):
                if self.state == PanelState.MAXIMIZED:
                    self.restore()
                else:
                    self.maximize()
                return True
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Minimize button
        if self.minimizable:
            min_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            if min_rect.collidepoint(pos):
                self.minimize()
                return True

        return False

    def get_rect(self) -> pygame.Rect:
        """Get panel rectangle."""
        if self.state == PanelState.MINIMIZED:
            return pygame.Rect(self.position[0], self.position[1], 200, self.TITLE_BAR_HEIGHT)
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    @property
    def rect(self) -> pygame.Rect:
        """Get panel rectangle as property."""
        return self.get_rect()

    def bring_to_front(self) -> None:
        """Bring panel to front (z-order management handled by parent)."""
        pass

    def close(self) -> None:
        """Close panel."""
        self.visible = False

    def minimize(self) -> None:
        """Minimize panel."""
        if self.state != PanelState.MINIMIZED:
            self.state = PanelState.MINIMIZED

    def maximize(self) -> None:
        """Maximize panel."""
        if self.state != PanelState.MAXIMIZED:
            self.saved_position = self.position.copy()
            self.saved_size = self.size.copy()
            self.state = PanelState.MAXIMIZED
            # Position and size will be set by parent based on screen size

    def restore(self) -> None:
        """Restore panel to normal state."""
        if self.state == PanelState.MAXIMIZED and self.saved_position and self.saved_size:
            self.position = self.saved_position
            self.size = self.saved_size
        self.state = PanelState.NORMAL

    def set_position(self, x: int, y: int) -> None:
        """Set panel position.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.position = [x, y]

    def set_size(self, width: int, height: int) -> None:
        """Set panel size.

        Args:
            width: Panel width
            height: Panel height
        """
        self.size = [max(width, self.MIN_WIDTH), max(height, self.MIN_HEIGHT)]

    def get_bounds(self) -> pygame.Rect:
        """Get panel bounds for collision detection.

        Returns:
            Rectangle representing panel bounds
        """
        return self.get_rect()

    def check_collision(self, other: 'ModernPanel') -> bool:
        """Check if this panel collides with another.

        Args:
            other: Other panel to check

        Returns:
            True if panels overlap
        """
        return self.get_bounds().colliderect(other.get_bounds())

    def set_layout_constraints(self, constraints: Any, layout_mode: str) -> None:
        """Set layout constraints for this panel.

        Args:
            constraints: Layout constraints object (GridConstraints, AnchorConstraints, etc.)
            layout_mode: Layout mode string ('grid', 'anchored', 'floating', 'fixed')
        """
        self.layout_constraints = constraints
        self.layout_mode = layout_mode
        self._managed_by_layout = True

    def set_theme_colors(self, theme: dict) -> None:
        """Apply theme colors to panel.

        Args:
            theme: Theme dictionary with color definitions
        """
        # Theme colors are handled automatically through ThemeManager
        pass