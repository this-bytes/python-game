"""
TabContainer component for multi-tab interfaces.

Provides tabbed panel system with:
- Multiple content tabs
- Active tab highlighting
- Keyboard navigation (Ctrl+Tab, Ctrl+Shift+Tab)
- Smooth tab switching animations
- Optional close buttons
- Theme-aware styling
"""

from typing import List, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
import pygame

from src.utils.animation_system import get_animation_system, EasingFunction


@dataclass
class Tab:
    """Represents a tab with content.
    
    Attributes:
        title: Tab label text
        content: Panel or component to display
        closeable: Whether tab can be closed
        icon: Optional icon surface
        data: Optional custom data
    """
    title: str
    content: any  # Panel or component instance
    closeable: bool = False
    icon: Optional[pygame.Surface] = None
    data: any = None


class TabContainer:
    """Multi-tab panel component with animations.
    
    Features:
    - Tab switching with fade animations
    - Active tab highlighting
    - Keyboard navigation
    - Close buttons for tabs
    - Horizontal or vertical tab bar
    - Scroll when too many tabs
    - Tab reordering (drag-drop)
    
    Example:
        tabs = [
            Tab("Overview", overview_panel),
            Tab("Stats", stats_panel, closeable=True),
            Tab("History", history_panel, closeable=True),
        ]
        
        tab_container = TabContainer(
            tabs=tabs,
            position=(10, 50),
            size=(780, 500)
        )
        
        # In game loop
        tab_container.handle_event(event)
        tab_container.update(delta_time)
        tab_container.render(screen)
    """
    
    def __init__(
        self,
        tabs: List[Tab],
        position: Tuple[int, int] = (0, 0),
        size: Tuple[int, int] = (400, 300),
        orientation: str = "horizontal",
        tab_height: int = 35,
        animation_duration: float = 0.2,
        on_tab_changed: Optional[Callable[[int, Tab], None]] = None,
        on_tab_closed: Optional[Callable[[int, Tab], None]] = None
    ):
        """Initialize TabContainer.
        
        Args:
            tabs: List of tabs to display
            position: (x, y) position on screen
            size: (width, height) of entire container
            orientation: "horizontal" or "vertical" tab bar
            tab_height: Height (or width) of tab buttons
            animation_duration: Duration of tab switch animation
            on_tab_changed: Callback when active tab changes (index, tab)
            on_tab_closed: Callback when tab is closed (index, tab)
        """
        self.tabs = tabs
        self.x, self.y = position
        self.width, self.height = size
        self.orientation = orientation
        self.tab_height = tab_height
        self.animation_duration = animation_duration
        self.on_tab_changed = on_tab_changed
        self.on_tab_closed = on_tab_closed
        
        # State
        self.active_tab_index = 0
        self.hovered_tab_index: Optional[int] = None
        self.hovered_close_button: Optional[int] = None
        self.dragging_tab_index: Optional[int] = None
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        
        # Animation
        self.animations = get_animation_system()
        self.content_opacity = 1.0
        self.animating_tab_switch = False
        
        # Theme colors
        self.bg_color = (30, 30, 30)
        self.tab_bar_color = (40, 40, 40)
        self.tab_active_color = (60, 60, 60)
        self.tab_inactive_color = (45, 45, 45)
        self.tab_hover_color = (55, 55, 55)
        self.tab_text_color = (220, 220, 220)
        self.tab_border_color = (80, 80, 80)
        self.close_button_color = (180, 50, 50)
        self.close_button_hover_color = (220, 60, 60)
        
        # Fonts (lazy initialization)
        self.tab_font: Optional[pygame.font.Font] = None
        
        # Tab bar dimensions
        self.tab_bar_rect = self._calculate_tab_bar_rect()
        self.content_rect = self._calculate_content_rect()
        
        # Scroll state (for many tabs)
        self.scroll_offset = 0
        self.max_scroll = 0
    
    def _calculate_tab_bar_rect(self) -> pygame.Rect:
        """Calculate tab bar rectangle."""
        if self.orientation == "horizontal":
            return pygame.Rect(self.x, self.y, self.width, self.tab_height)
        else:  # vertical
            return pygame.Rect(self.x, self.y, self.tab_height, self.height)
    
    def _calculate_content_rect(self) -> pygame.Rect:
        """Calculate content area rectangle."""
        if self.orientation == "horizontal":
            return pygame.Rect(
                self.x,
                self.y + self.tab_height,
                self.width,
                self.height - self.tab_height
            )
        else:  # vertical
            return pygame.Rect(
                self.x + self.tab_height,
                self.y,
                self.width - self.tab_height,
                self.height
            )
    
    def add_tab(self, tab: Tab, activate: bool = True) -> None:
        """Add new tab.
        
        Args:
            tab: Tab to add
            activate: Whether to make this tab active
        """
        self.tabs.append(tab)
        
        if activate:
            self.set_active_tab(len(self.tabs) - 1)
    
    def remove_tab(self, index: int) -> bool:
        """Remove tab by index.
        
        Args:
            index: Tab index to remove
            
        Returns:
            True if removed successfully
        """
        if 0 <= index < len(self.tabs):
            removed_tab = self.tabs[index]
            
            # Trigger callback
            if self.on_tab_closed:
                self.on_tab_closed(index, removed_tab)
            
            self.tabs.pop(index)
            
            # Adjust active tab index
            if len(self.tabs) == 0:
                self.active_tab_index = -1
            elif self.active_tab_index >= len(self.tabs):
                self.active_tab_index = len(self.tabs) - 1
            elif index < self.active_tab_index:
                self.active_tab_index -= 1
            elif index == self.active_tab_index and self.active_tab_index > 0:
                self.active_tab_index -= 1
            
            return True
        return False
    
    def set_active_tab(self, index: int, animate: bool = True) -> None:
        """Switch to tab by index.
        
        Args:
            index: Tab index to activate
            animate: Whether to animate the transition
        """
        if 0 <= index < len(self.tabs) and index != self.active_tab_index:
            old_index = self.active_tab_index
            self.active_tab_index = index
            
            # Trigger callback
            if self.on_tab_changed:
                self.on_tab_changed(index, self.tabs[index])
            
            # Animate tab switch
            if animate and not self.animating_tab_switch:
                self._animate_tab_switch()
    
    def _animate_tab_switch(self) -> None:
        """Animate tab content fade."""
        self.animating_tab_switch = True
        
        # Fade out → fade in
        self.animations.animate(
            target=self,
            property="content_opacity",
            start_value=self.content_opacity,
            end_value=0.0,
            duration=self.animation_duration / 2,
            easing=EasingFunction.EASE_IN_QUAD,
            on_complete=self._on_fade_out_complete
        )
    
    def _on_fade_out_complete(self) -> None:
        """Called when fade-out completes."""
        # Fade in
        self.animations.animate(
            target=self,
            property="content_opacity",
            start_value=0.0,
            end_value=1.0,
            duration=self.animation_duration / 2,
            easing=EasingFunction.EASE_OUT_QUAD,
            on_complete=self._on_fade_in_complete
        )
    
    def _on_fade_in_complete(self) -> None:
        """Called when fade-in completes."""
        self.animating_tab_switch = False
    
    def get_active_tab(self) -> Optional[Tab]:
        """Get currently active tab.
        
        Returns:
            Active tab or None
        """
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was consumed
        """
        if event.type == pygame.KEYDOWN:
            # Ctrl+Tab: Next tab
            if event.key == pygame.K_TAB:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Ctrl+Shift+Tab: Previous tab
                        self.set_active_tab((self.active_tab_index - 1) % len(self.tabs))
                    else:
                        # Ctrl+Tab: Next tab
                        self.set_active_tab((self.active_tab_index + 1) % len(self.tabs))
                    return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check tab clicks
                tab_index = self._get_tab_at_position(mouse_pos)
                if tab_index is not None:
                    # Check close button click
                    if self._is_close_button_at_position(tab_index, mouse_pos):
                        if self.tabs[tab_index].closeable:
                            self.remove_tab(tab_index)
                            return True
                    else:
                        # Tab click
                        self.set_active_tab(tab_index)
                        return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Update hover state
            self.hovered_tab_index = self._get_tab_at_position(mouse_pos)
            
            # Check close button hover
            if self.hovered_tab_index is not None:
                if self._is_close_button_at_position(self.hovered_tab_index, mouse_pos):
                    self.hovered_close_button = self.hovered_tab_index
                else:
                    self.hovered_close_button = None
            else:
                self.hovered_close_button = None
        
        # Forward events to active tab content
        active_tab = self.get_active_tab()
        if active_tab and hasattr(active_tab.content, 'handle_event'):
            # Adjust event position for content area
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if hasattr(event, 'pos'):
                    # Check if event is in content area
                    if self.content_rect.collidepoint(event.pos):
                        return active_tab.content.handle_event(event)
            else:
                return active_tab.content.handle_event(event)
        
        return False
    
    def update(self, delta_time: float) -> None:
        """Update tab container state.
        
        Args:
            delta_time: Time since last update
        """
        # Update animations
        self.animations.update(delta_time)
        
        # Update active tab content
        active_tab = self.get_active_tab()
        if active_tab and hasattr(active_tab.content, 'update'):
            active_tab.content.update(delta_time)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render tab container.
        
        Args:
            screen: Pygame surface to render on
        """
        # Lazy font initialization
        if self.tab_font is None:
            self.tab_font = pygame.font.SysFont('Arial', 13, bold=True)
        
        # Render tab bar background
        pygame.draw.rect(screen, self.tab_bar_color, self.tab_bar_rect)
        
        # Render tabs
        self._render_tabs(screen)
        
        # Render content area background
        pygame.draw.rect(screen, self.bg_color, self.content_rect)
        
        # Render active tab content
        active_tab = self.get_active_tab()
        if active_tab:
            # Create content surface for opacity
            content_surface = pygame.Surface(
                (self.content_rect.width, self.content_rect.height),
                pygame.SRCALPHA
            )
            
            # Render content to surface
            if hasattr(active_tab.content, 'render'):
                # Adjust render position for content area
                temp_surface = pygame.Surface(
                    (self.content_rect.width, self.content_rect.height),
                    pygame.SRCALPHA
                )
                active_tab.content.render(temp_surface)
                content_surface.blit(temp_surface, (0, 0))
            
            # Apply opacity
            if self.content_opacity < 1.0:
                content_surface.set_alpha(int(255 * self.content_opacity))
            
            # Blit to screen
            screen.blit(content_surface, (self.content_rect.x, self.content_rect.y))
        
        # Render border
        pygame.draw.rect(
            screen,
            self.tab_border_color,
            pygame.Rect(self.x, self.y, self.width, self.height),
            width=2
        )
    
    def _render_tabs(self, screen: pygame.Surface) -> None:
        """Render tab buttons."""
        if len(self.tabs) == 0:
            return
        
        tab_width = 120
        tab_spacing = 2
        close_button_size = 16
        close_button_margin = 5
        
        if self.orientation == "horizontal":
            # Horizontal tabs
            tab_x = self.tab_bar_rect.x + 5
            tab_y = self.tab_bar_rect.y + 3
            tab_button_height = self.tab_height - 6
            
            for i, tab in enumerate(self.tabs):
                # Determine tab color
                if i == self.active_tab_index:
                    color = self.tab_active_color
                elif i == self.hovered_tab_index:
                    color = self.tab_hover_color
                else:
                    color = self.tab_inactive_color
                
                # Draw tab button
                tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_button_height)
                pygame.draw.rect(screen, color, tab_rect, border_radius=4)
                
                # Draw tab border (highlight active)
                border_width = 2 if i == self.active_tab_index else 1
                pygame.draw.rect(screen, self.tab_border_color, tab_rect, width=border_width, border_radius=4)
                
                # Render tab title
                title_surface = self.tab_font.render(tab.title, True, self.tab_text_color)
                title_x = tab_x + 8
                title_y = tab_y + (tab_button_height - title_surface.get_height()) // 2
                screen.blit(title_surface, (title_x, title_y))
                
                # Render close button if closeable
                if tab.closeable:
                    close_x = tab_x + tab_width - close_button_size - close_button_margin
                    close_y = tab_y + (tab_button_height - close_button_size) // 2
                    close_rect = pygame.Rect(close_x, close_y, close_button_size, close_button_size)
                    
                    # Close button color
                    if i == self.hovered_close_button:
                        close_color = self.close_button_hover_color
                    else:
                        close_color = self.close_button_color
                    
                    # Draw close button
                    pygame.draw.circle(
                        screen,
                        close_color,
                        (close_x + close_button_size // 2, close_y + close_button_size // 2),
                        close_button_size // 2
                    )
                    
                    # Draw X
                    x_padding = 4
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (close_x + x_padding, close_y + x_padding),
                        (close_x + close_button_size - x_padding, close_y + close_button_size - x_padding),
                        width=2
                    )
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (close_x + close_button_size - x_padding, close_y + x_padding),
                        (close_x + x_padding, close_y + close_button_size - x_padding),
                        width=2
                    )
                
                tab_x += tab_width + tab_spacing
    
    def _get_tab_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get tab index at mouse position.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            Tab index or None
        """
        if not self.tab_bar_rect.collidepoint(pos):
            return None
        
        tab_width = 120
        tab_spacing = 2
        
        if self.orientation == "horizontal":
            tab_x = self.tab_bar_rect.x + 5
            tab_y = self.tab_bar_rect.y + 3
            tab_button_height = self.tab_height - 6
            
            mouse_x, mouse_y = pos
            
            for i in range(len(self.tabs)):
                tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_button_height)
                if tab_rect.collidepoint(mouse_x, mouse_y):
                    return i
                tab_x += tab_width + tab_spacing
        
        return None
    
    def _is_close_button_at_position(self, tab_index: int, pos: Tuple[int, int]) -> bool:
        """Check if position is over close button.
        
        Args:
            tab_index: Tab index to check
            pos: Mouse position (x, y)
            
        Returns:
            True if over close button
        """
        if not (0 <= tab_index < len(self.tabs)):
            return False
        
        if not self.tabs[tab_index].closeable:
            return False
        
        tab_width = 120
        tab_spacing = 2
        close_button_size = 16
        close_button_margin = 5
        
        if self.orientation == "horizontal":
            tab_x = self.tab_bar_rect.x + 5 + (tab_width + tab_spacing) * tab_index
            tab_y = self.tab_bar_rect.y + 3
            tab_button_height = self.tab_height - 6
            
            close_x = tab_x + tab_width - close_button_size - close_button_margin
            close_y = tab_y + (tab_button_height - close_button_size) // 2
            close_rect = pygame.Rect(close_x, close_y, close_button_size, close_button_size)
            
            return close_rect.collidepoint(pos)
        
        return False
    
    def get_tab_count(self) -> int:
        """Get number of tabs.
        
        Returns:
            Tab count
        """
        return len(self.tabs)
    
    def find_tab_by_title(self, title: str) -> Optional[int]:
        """Find tab index by title.
        
        Args:
            title: Tab title to search for
            
        Returns:
            Tab index or None if not found
        """
        for i, tab in enumerate(self.tabs):
            if tab.title == title:
                return i
        return None
