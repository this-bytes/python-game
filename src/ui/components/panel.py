"""Panel component for game UI.

Draggable, resizable window panel with title bar and control buttons.
"""

import pygame
from typing import Tuple, Optional, Any
from enum import Enum


class PanelState(Enum):
    """Panel display state."""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"


class Panel:
    """Draggable, resizable window panel."""

    # Default styling
    TITLE_BAR_HEIGHT = 30
    BORDER_WIDTH = 2
    BUTTON_SIZE = 20
    BUTTON_MARGIN = 5
    MIN_WIDTH = 200
    MIN_HEIGHT = 100

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
    ):
        """Initialize panel.

        Args:
            title: Panel title displayed in title bar
            position: Initial (x, y) position
            size: Initial (width, height) size
            closeable: Whether panel can be closed
            minimizable: Whether panel can be minimized
            maximizable: Whether panel can be maximized
            draggable: Whether panel can be dragged
            resizable: Whether panel can be resized
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

        # Colors (will be overridden by theme)
        self.bg_color = (25, 25, 40)
        self.title_bg_color = (0, 180, 255)
        self.border_color = (50, 50, 80)
        self.text_color = (220, 220, 230)
        self.button_color = (200, 200, 200)
        self.button_hover_color = (255, 255, 255)
        self.close_button_color = (255, 50, 50)

        # Font (will be created on first render)
        self.font = None

    def render(self, screen: pygame.Surface) -> None:
        """Render panel to screen.

        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 14)

        if self.state == PanelState.MINIMIZED:
            self._render_minimized(screen)
            return

        # Get panel rect
        rect = self.get_rect()

        # Draw panel background
        pygame.draw.rect(screen, self.bg_color, rect, border_radius=4)

        # Draw border
        pygame.draw.rect(screen, self.border_color, rect, self.BORDER_WIDTH, border_radius=4)

        # Draw title bar
        title_rect = pygame.Rect(
            rect.x, rect.y, rect.width, self.TITLE_BAR_HEIGHT
        )
        pygame.draw.rect(screen, self.title_bg_color, title_rect, border_top_left_radius=4, border_top_right_radius=4)

        # Draw title text
        title_text = self.font.render(self.title, True, self.text_color)
        screen.blit(
            title_text,
            (rect.x + 10, rect.y + (self.TITLE_BAR_HEIGHT - title_text.get_height()) // 2)
        )

        # Draw control buttons
        self._render_control_buttons(screen, rect)

        # Render content area (to be overridden by subclasses)
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
        rect = pygame.Rect(self.position[0], self.position[1], 200, self.TITLE_BAR_HEIGHT)

        # Draw title bar
        pygame.draw.rect(screen, self.title_bg_color, rect, border_radius=4)

        # Draw title text
        title_text = self.font.render(self.title, True, self.text_color)
        screen.blit(
            title_text,
            (rect.x + 10, rect.y + (self.TITLE_BAR_HEIGHT - title_text.get_height()) // 2)
        )

        # Draw restore button
        button_x = rect.x + rect.width - self.BUTTON_SIZE - self.BUTTON_MARGIN
        button_rect = pygame.Rect(button_x, rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
        pygame.draw.rect(screen, self.button_color, button_rect, border_radius=2)
        pygame.draw.rect(screen, self.text_color, button_rect, 1, border_radius=2)

    def _render_control_buttons(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Render minimize, maximize, close buttons."""
        button_x = panel_rect.x + panel_rect.width - self.BUTTON_SIZE - self.BUTTON_MARGIN

        # Close button
        if self.closeable:
            close_rect = pygame.Rect(button_x, panel_rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(screen, self.close_button_color, close_rect, border_radius=2)
            # Draw X
            pygame.draw.line(screen, self.text_color, 
                           (close_rect.x + 5, close_rect.y + 5),
                           (close_rect.x + 15, close_rect.y + 15), 2)
            pygame.draw.line(screen, self.text_color,
                           (close_rect.x + 15, close_rect.y + 5),
                           (close_rect.x + 5, close_rect.y + 15), 2)
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Maximize button
        if self.maximizable:
            max_rect = pygame.Rect(button_x, panel_rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(screen, self.button_color, max_rect, border_radius=2)
            pygame.draw.rect(screen, self.text_color, max_rect, 1, border_radius=2)
            button_x -= self.BUTTON_SIZE + self.BUTTON_MARGIN

        # Minimize button
        if self.minimizable:
            min_rect = pygame.Rect(button_x, panel_rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE)
            pygame.draw.rect(screen, self.button_color, min_rect, border_radius=2)
            pygame.draw.line(screen, self.text_color,
                           (min_rect.x + 5, min_rect.y + 10),
                           (min_rect.x + 15, min_rect.y + 10), 2)

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

    def set_theme_colors(self, theme: dict) -> None:
        """Apply theme colors to panel.

        Args:
            theme: Theme dictionary with color definitions
        """
        colors = theme.get("colors", {})
        self.bg_color = colors.get("panel_bg", self.bg_color)
        self.title_bg_color = colors.get("primary", self.title_bg_color)
        self.border_color = colors.get("border", self.border_color)
        self.text_color = colors.get("text", self.text_color)
