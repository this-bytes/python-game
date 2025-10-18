"""Modal dialog component for game UI.

Blocking modal dialogs with backdrop, animations, and configurable buttons.
Integrates with AnimationSystem for smooth fade + scale animations.
"""

import pygame
from typing import Tuple, Callable, Optional, List, Any
from enum import Enum
from dataclasses import dataclass

from src.utils.animation_system import get_animation_system, EasingFunction


class ModalResult(Enum):
    """Modal dialog result."""
    OK = "ok"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"
    CUSTOM = "custom"
    CLOSED = "closed"  # Closed via ESC or backdrop


class ModalType(Enum):
    """Pre-configured modal types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CONFIRM = "confirm"
    CUSTOM = "custom"


@dataclass
class ModalButton:
    """Configuration for modal button."""
    text: str
    result: ModalResult
    style: str = "primary"  # primary, secondary, danger
    callback: Optional[Callable[[], None]] = None


class Modal:
    """Blocking modal dialog with backdrop and animations.
    
    Features:
    - Backdrop overlay (darkened background)
    - Smooth fade + scale animations
    - Configurable buttons (OK, Cancel, Yes/No, custom)
    - Keyboard support (ESC to close, Enter for default action)
    - Result callbacks
    - Theme-aware styling
    
    Usage:
        modal = Modal(
            title="Confirm Action",
            message="Are you sure you want to delete this specialist?",
            modal_type=ModalType.CONFIRM,
            on_result=lambda result: handle_deletion(result)
        )
        modal.show(screen)
    """
    
    def __init__(
        self,
        title: str,
        message: str,
        modal_type: ModalType = ModalType.INFO,
        buttons: Optional[List[ModalButton]] = None,
        on_result: Optional[Callable[[ModalResult], None]] = None,
        backdrop_alpha: int = 180,
        width: int = 400,
        height: int = 200,
    ):
        """Initialize modal dialog.
        
        Args:
            title: Modal title text
            message: Modal body message
            modal_type: Pre-configured modal type (INFO, WARNING, ERROR, CONFIRM, CUSTOM)
            buttons: Custom buttons (if None, uses type defaults)
            on_result: Callback when modal closes with result
            backdrop_alpha: Backdrop darkness (0-255, higher = darker)
            width: Modal width in pixels
            height: Modal height in pixels
        """
        self.title = title
        self.message = message
        self.modal_type = modal_type
        self.on_result = on_result
        self.backdrop_alpha = backdrop_alpha
        self.width = width
        self.height = height
        
        # Configure buttons based on type
        if buttons is None:
            self.buttons = self._get_default_buttons(modal_type)
        else:
            self.buttons = buttons
        
        # State
        self.visible = False
        self.result: Optional[ModalResult] = None
        self.opacity = 0.0  # For fade animation
        self.scale = 0.8    # For scale animation
        
        # Screen dimensions (set on show)
        self.screen_width = 0
        self.screen_height = 0
        
        # Position (centered)
        self.x = 0
        self.y = 0
        
        # Fonts
        self.title_font = None
        self.message_font = None
        
        # Colors (theme-aware)
        self.backdrop_color = (0, 0, 0)
        self.modal_bg_color = (40, 40, 40)
        self.title_color = (255, 255, 255)
        self.message_color = (200, 200, 200)
        self.border_color = (80, 80, 80)
        
        # Type-specific colors
        self.type_colors = {
            ModalType.INFO: (0, 120, 215),
            ModalType.WARNING: (255, 165, 0),
            ModalType.ERROR: (200, 0, 0),
            ModalType.CONFIRM: (0, 150, 0),
        }
        
        # Animation system
        self.animations = get_animation_system()
        
        # Button states
        self.hovered_button_index: Optional[int] = None
        self.pressed_button_index: Optional[int] = None
    
    def _get_default_buttons(self, modal_type: ModalType) -> List[ModalButton]:
        """Get default buttons for modal type.
        
        Args:
            modal_type: Modal type
            
        Returns:
            List of default buttons
        """
        if modal_type == ModalType.INFO:
            return [ModalButton("OK", ModalResult.OK, "primary")]
        elif modal_type == ModalType.WARNING:
            return [ModalButton("OK", ModalResult.OK, "primary")]
        elif modal_type == ModalType.ERROR:
            return [ModalButton("OK", ModalResult.OK, "danger")]
        elif modal_type == ModalType.CONFIRM:
            return [
                ModalButton("Yes", ModalResult.YES, "primary"),
                ModalButton("No", ModalResult.NO, "secondary"),
            ]
        else:  # CUSTOM
            return [ModalButton("OK", ModalResult.OK, "primary")]
    
    def show(self, screen: pygame.Surface) -> None:
        """Show modal with fade + scale animation.
        
        Args:
            screen: Pygame surface for dimensions
        """
        self.visible = True
        self.result = None
        
        # Get screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Center modal
        self.x = (self.screen_width - self.width) // 2
        self.y = (self.screen_height - self.height) // 2
        
        # Initialize fonts
        if self.title_font is None:
            self.title_font = pygame.font.SysFont('Arial', 18, bold=True)
        if self.message_font is None:
            self.message_font = pygame.font.SysFont('Arial', 14)
        
        # Animate in (fade + scale)
        self.opacity = 0.0
        self.scale = 0.8
        
        self.animations.animate(
            self, "opacity",
            0.0, 1.0,
            duration=0.2,
            easing=EasingFunction.EASE_OUT_QUAD
        )
        
        self.animations.animate(
            self, "scale",
            0.8, 1.0,
            duration=0.3,
            easing=EasingFunction.ELASTIC_OUT
        )
    
    def close(self, result: ModalResult) -> None:
        """Close modal with fade-out animation.
        
        Args:
            result: Modal result
        """
        self.result = result
        
        # Animate out (fade only, fast)
        self.animations.animate(
            self, "opacity",
            1.0, 0.0,
            duration=0.15,
            easing=EasingFunction.EASE_IN_QUAD,
            on_complete=self._on_close_complete
        )
    
    def _on_close_complete(self) -> None:
        """Called when close animation completes."""
        self.visible = False
        
        # Trigger result callback
        if self.on_result and self.result:
            self.on_result(self.result)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was consumed
        """
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC closes modal
                self.close(ModalResult.CLOSED)
                return True
            elif event.key == pygame.K_RETURN:
                # Enter triggers first button (default action)
                if self.buttons:
                    button = self.buttons[0]
                    if button.callback:
                        button.callback()
                    self.close(button.result)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos  # Use event position, not actual mouse
                
                # Check button clicks
                button_index = self._get_button_at_position(mouse_pos)
                if button_index is not None:
                    self.pressed_button_index = button_index
                    return True
                
                # Check backdrop click (close modal)
                if not self._is_point_in_modal(mouse_pos):
                    self.close(ModalResult.CLOSED)
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed_button_index is not None:
                mouse_pos = event.pos  # Use event position, not actual mouse
                button_index = self._get_button_at_position(mouse_pos)
                
                # Button clicked
                if button_index == self.pressed_button_index:
                    button = self.buttons[button_index]
                    if button.callback:
                        button.callback()
                    self.close(button.result)
                
                self.pressed_button_index = None
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos  # Use event position, not actual mouse
            self.hovered_button_index = self._get_button_at_position(mouse_pos)
        
        return True  # Modal consumes all events
    
    def render(self, screen: pygame.Surface) -> None:
        """Render modal dialog.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return
        
        # Apply opacity to all rendering
        if self.opacity <= 0:
            return
        
        # Render backdrop
        backdrop = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        backdrop_alpha = int(self.backdrop_alpha * self.opacity)
        backdrop.fill((*self.backdrop_color, backdrop_alpha))
        screen.blit(backdrop, (0, 0))
        
        # Apply scale transformation
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = self.y + (self.height - scaled_height) // 2
        
        # Create modal surface
        modal_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Render modal background
        pygame.draw.rect(
            modal_surface,
            self.modal_bg_color,
            (0, 0, self.width, self.height),
            border_radius=8
        )
        
        # Render border
        border_color = self.type_colors.get(self.modal_type, self.border_color)
        pygame.draw.rect(
            modal_surface,
            border_color,
            (0, 0, self.width, self.height),
            width=3,
            border_radius=8
        )
        
        # Render title
        title_surface = self.title_font.render(self.title, True, self.title_color)
        title_x = (self.width - title_surface.get_width()) // 2
        modal_surface.blit(title_surface, (title_x, 20))
        
        # Render message (multi-line support)
        message_y = 60
        message_lines = self._wrap_text(self.message, self.width - 40)
        for line in message_lines:
            line_surface = self.message_font.render(line, True, self.message_color)
            line_x = (self.width - line_surface.get_width()) // 2
            modal_surface.blit(line_surface, (line_x, message_y))
            message_y += 25
        
        # Render buttons
        self._render_buttons(modal_surface)
        
        # Scale modal surface
        if self.scale != 1.0:
            modal_surface = pygame.transform.smoothscale(
                modal_surface,
                (scaled_width, scaled_height)
            )
        
        # Apply opacity
        if self.opacity < 1.0:
            modal_surface.set_alpha(int(255 * self.opacity))
        
        # Blit to screen
        screen.blit(modal_surface, (scaled_x, scaled_y))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within width.
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.message_font.render(test_line, True, self.message_color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _render_buttons(self, surface: pygame.Surface) -> None:
        """Render buttons on modal surface.
        
        Args:
            surface: Surface to render buttons on
        """
        button_width = 100
        button_height = 35
        button_spacing = 15
        
        total_width = (button_width * len(self.buttons)) + (button_spacing * (len(self.buttons) - 1))
        button_y = self.height - button_height - 20
        button_x = (self.width - total_width) // 2
        
        button_colors = {
            "primary": (0, 120, 215),
            "secondary": (100, 100, 100),
            "danger": (200, 0, 0),
        }
        
        button_hover_colors = {
            "primary": (0, 150, 255),
            "secondary": (130, 130, 130),
            "danger": (255, 50, 50),
        }
        
        for i, button in enumerate(self.buttons):
            is_hovered = i == self.hovered_button_index
            is_pressed = i == self.pressed_button_index
            
            # Button color
            if is_pressed:
                color = tuple(max(0, c - 40) for c in button_colors[button.style])
            elif is_hovered:
                color = button_hover_colors[button.style]
            else:
                color = button_colors[button.style]
            
            # Draw button
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(surface, color, button_rect, border_radius=4)
            
            # Draw button text
            button_font = pygame.font.SysFont('Arial', 14, bold=True)
            button_text = button_font.render(button.text, True, (255, 255, 255))
            text_x = button_x + (button_width - button_text.get_width()) // 2
            text_y = button_y + (button_height - button_text.get_height()) // 2
            surface.blit(button_text, (text_x, text_y))
            
            button_x += button_width + button_spacing
    
    def _get_button_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get button index at mouse position.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            Button index or None
        """
        # Account for scale transformation
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = self.y + (self.height - scaled_height) // 2
        
        # Check if point is in scaled modal bounds
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        if not scaled_rect.collidepoint(pos):
            return None
        
        # Convert mouse position to modal-local coordinates (accounting for scale)
        mouse_x, mouse_y = pos
        local_x = (mouse_x - scaled_x) / self.scale
        local_y = (mouse_y - scaled_y) / self.scale
        
        # Calculate button positions (in modal-local coordinates)
        button_width = 100
        button_height = 35
        button_spacing = 15
        
        total_width = (button_width * len(self.buttons)) + (button_spacing * (len(self.buttons) - 1))
        button_y = self.height - button_height - 20
        button_x = (self.width - total_width) // 2
        
        # Check each button
        for i in range(len(self.buttons)):
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(local_x, local_y):
                return i
            button_x += button_width + button_spacing
        
        return None
    
    def _is_point_in_modal(self, pos: Tuple[int, int]) -> bool:
        """Check if point is inside modal bounds (accounting for scale).
        
        Args:
            pos: Point position (x, y)
            
        Returns:
            True if point is in modal
        """
        # Account for scale transformation
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = self.y + (self.height - scaled_height) // 2
        
        modal_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        return modal_rect.collidepoint(pos)
    
    def is_visible(self) -> bool:
        """Check if modal is visible.
        
        Returns:
            True if modal is visible
        """
        return self.visible
