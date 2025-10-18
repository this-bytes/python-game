"""
Navigation Menu component for main game navigation.

Provides a sidebar or top menu for switching between major game sections.
Inspired by modern game UIs with clean, accessible navigation.
"""

from typing import List, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
import pygame


class MenuPosition(Enum):
    """Menu position on screen."""
    LEFT = "left"
    TOP = "top"
    RIGHT = "right"


@dataclass
class MenuItem:
    """Represents a menu item with icon and label.
    
    Attributes:
        id: Unique identifier for the menu item
        label: Display text
        icon: Optional icon character or emoji
        tooltip: Optional tooltip text
        hotkey: Optional keyboard shortcut
        badge: Optional badge text (e.g., notification count)
    """
    id: str
    label: str
    icon: str = ""
    tooltip: str = ""
    hotkey: Optional[int] = None  # pygame key constant
    badge: str = ""


class NavigationMenu:
    """Main navigation menu component.
    
    Features:
    - Clean, modern design
    - Icon + label items
    - Active item highlighting
    - Keyboard shortcuts
    - Notification badges
    - Smooth hover effects
    - Collapsible (minimize to icons only)
    
    Example:
        menu_items = [
            MenuItem("overview", "Overview", "📊", "Game dashboard", pygame.K_F1),
            MenuItem("operations", "Operations", "⚡", "Incidents & Specialists", pygame.K_F2),
            MenuItem("management", "Management", "🏢", "Equipment & Facilities", pygame.K_F3),
            MenuItem("analytics", "Analytics", "📈", "Metrics & Achievements", pygame.K_F4),
        ]
        
        menu = NavigationMenu(
            items=menu_items,
            position=MenuPosition.LEFT,
            on_item_selected=lambda item_id: print(f"Selected: {item_id}")
        )
    """
    
    def __init__(
        self,
        items: List[MenuItem],
        position: MenuPosition = MenuPosition.LEFT,
        width: int = 200,
        collapsed_width: int = 60,
        on_item_selected: Optional[Callable[[str], None]] = None,
        collapsed: bool = False
    ):
        """Initialize NavigationMenu.
        
        Args:
            items: List of menu items
            position: Menu position on screen
            width: Width when expanded
            collapsed_width: Width when collapsed
            on_item_selected: Callback when item is selected (item_id)
            collapsed: Start collapsed (icons only)
        """
        self.items = items
        self.position = position
        self.width = width
        self.collapsed_width = collapsed_width
        self.on_item_selected = on_item_selected
        self.collapsed = collapsed
        
        # State
        self.active_item_id: Optional[str] = items[0].id if items else None
        self.hovered_item_id: Optional[str] = None
        
        # Styling
        self.bg_color = (25, 25, 35)
        self.item_bg_color = (35, 35, 50)
        self.item_hover_color = (45, 45, 65)
        self.item_active_color = (0, 120, 200)
        self.text_color = (220, 220, 230)
        self.text_active_color = (255, 255, 255)
        self.badge_color = (255, 80, 80)
        
        # Fonts
        self.label_font = pygame.font.SysFont('Arial', 14)
        self.icon_font = pygame.font.SysFont('Arial', 20)
        self.badge_font = pygame.font.SysFont('Arial', 10, bold=True)
        
        # Animation
        self.current_width = self.collapsed_width if collapsed else self.width
        self.target_width = self.current_width
        self.animation_speed = 800  # pixels per second
    
    def get_rect(self, screen_width: int, screen_height: int) -> pygame.Rect:
        """Get menu rectangle based on position.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            Rectangle for menu area
        """
        if self.position == MenuPosition.LEFT:
            return pygame.Rect(0, 60, int(self.current_width), screen_height - 60)
        elif self.position == MenuPosition.TOP:
            return pygame.Rect(0, 60, screen_width, 50)
        elif self.position == MenuPosition.RIGHT:
            return pygame.Rect(screen_width - int(self.current_width), 60, int(self.current_width), screen_height - 60)
        
        return pygame.Rect(0, 60, int(self.current_width), screen_height - 60)
    
    def set_active_item(self, item_id: str) -> None:
        """Set the active menu item.
        
        Args:
            item_id: ID of item to activate
        """
        if any(item.id == item_id for item in self.items):
            self.active_item_id = item_id
            if self.on_item_selected:
                self.on_item_selected(item_id)
    
    def toggle_collapsed(self) -> None:
        """Toggle between collapsed and expanded states."""
        self.collapsed = not self.collapsed
        self.target_width = self.collapsed_width if self.collapsed else self.width
    
    def handle_event(self, event: pygame.event.Event, screen_width: int, screen_height: int) -> bool:
        """Handle input events.
        
        Args:
            event: Pygame event
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            True if event was handled
        """
        menu_rect = self.get_rect(screen_width, screen_height)
        
        # Mouse hover
        if event.type == pygame.MOUSEMOTION:
            if menu_rect.collidepoint(event.pos):
                # Find hovered item
                self.hovered_item_id = self._get_item_at_pos(event.pos, menu_rect)
            else:
                self.hovered_item_id = None
        
        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if menu_rect.collidepoint(event.pos):
                item_id = self._get_item_at_pos(event.pos, menu_rect)
                if item_id:
                    self.set_active_item(item_id)
                    return True
        
        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            # Toggle collapse with Tab key
            if event.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.toggle_collapsed()
                return True
            
            for item in self.items:
                if item.hotkey and event.key == item.hotkey:
                    self.set_active_item(item.id)
                    return True
        
        return False
    
    def _get_item_at_pos(self, pos: Tuple[int, int], menu_rect: pygame.Rect) -> Optional[str]:
        """Get menu item ID at mouse position.
        
        Args:
            pos: Mouse position
            menu_rect: Menu rectangle
            
        Returns:
            Item ID if found, None otherwise
        """
        item_height = 60
        item_spacing = 5
        y_offset = menu_rect.y + 10
        
        for item in self.items:
            item_rect = pygame.Rect(
                menu_rect.x + 5,
                y_offset,
                menu_rect.width - 10,
                item_height
            )
            
            if item_rect.collidepoint(pos):
                return item.id
            
            y_offset += item_height + item_spacing
        
        return None
    
    def update(self, delta_time: float) -> None:
        """Update menu state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Animate width change
        if abs(self.current_width - self.target_width) > 1:
            diff = self.target_width - self.current_width
            change = self.animation_speed * delta_time
            
            if abs(diff) < change:
                self.current_width = self.target_width
            else:
                self.current_width += change if diff > 0 else -change
    
    def render(self, screen: pygame.Surface, screen_width: int, screen_height: int) -> None:
        """Render the navigation menu.
        
        Args:
            screen: Pygame surface to render on
            screen_width: Screen width
            screen_height: Screen height
        """
        menu_rect = self.get_rect(screen_width, screen_height)
        
        # Background with subtle gradient effect
        pygame.draw.rect(screen, self.bg_color, menu_rect)
        
        # Subtle overlay for depth
        overlay_color = (30, 30, 40)
        overlay_rect = pygame.Rect(menu_rect.x, menu_rect.y, menu_rect.width, 5)
        pygame.draw.rect(screen, overlay_color, overlay_rect)
        
        # Border
        border_color = (50, 50, 70)
        if self.position == MenuPosition.LEFT:
            pygame.draw.line(screen, border_color, 
                           (menu_rect.right - 1, menu_rect.top),
                           (menu_rect.right - 1, menu_rect.bottom), 2)
        elif self.position == MenuPosition.RIGHT:
            pygame.draw.line(screen, border_color,
                           (menu_rect.left, menu_rect.top),
                           (menu_rect.left, menu_rect.bottom), 2)
        
        # Render collapse button at bottom
        self._render_collapse_button(screen, menu_rect)
        
        # Render items
        item_height = 60
        item_spacing = 5
        y_offset = menu_rect.y + 10
        
        for item in self.items:
            self._render_item(screen, item, menu_rect, y_offset, item_height)
            y_offset += item_height + item_spacing
    
    def _render_collapse_button(self, screen: pygame.Surface, menu_rect: pygame.Rect) -> None:
        """Render collapse/expand button at bottom of menu.
        
        Args:
            screen: Pygame surface
            menu_rect: Menu rectangle
        """
        button_height = 30
        button_rect = pygame.Rect(
            menu_rect.x + 5,
            menu_rect.bottom - button_height - 5,
            menu_rect.width - 10,
            button_height
        )
        
        # Background
        bg_color = (40, 40, 55)
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=4)
        
        # Icon
        icon = "◀" if not self.collapsed else "▶"
        icon_text = self.icon_font.render(icon, True, (180, 180, 200))
        icon_x = button_rect.centerx - icon_text.get_width() // 2
        icon_y = button_rect.centery - icon_text.get_height() // 2
        screen.blit(icon_text, (icon_x, icon_y))
    
    def _render_item(
        self,
        screen: pygame.Surface,
        item: MenuItem,
        menu_rect: pygame.Rect,
        y_offset: int,
        item_height: int
    ) -> None:
        """Render individual menu item.
        
        Args:
            screen: Pygame surface
            item: Menu item to render
            menu_rect: Menu rectangle
            y_offset: Y position for item
            item_height: Height of item
        """
        item_rect = pygame.Rect(
            menu_rect.x + 5,
            y_offset,
            menu_rect.width - 10,
            item_height
        )
        
        # Background
        is_active = item.id == self.active_item_id
        is_hovered = item.id == self.hovered_item_id
        
        if is_active:
            bg_color = self.item_active_color
        elif is_hovered:
            bg_color = self.item_hover_color
        else:
            bg_color = self.item_bg_color
        
        pygame.draw.rect(screen, bg_color, item_rect, border_radius=6)
        
        # Icon
        icon_text = self.icon_font.render(item.icon, True, 
                                         self.text_active_color if is_active else self.text_color)
        icon_x = item_rect.x + 15
        icon_y = item_rect.centery - icon_text.get_height() // 2
        screen.blit(icon_text, (icon_x, icon_y))
        
        # Label (only if not collapsed)
        if not self.collapsed:
            label_text = self.label_font.render(item.label, True,
                                               self.text_active_color if is_active else self.text_color)
            label_x = icon_x + 35
            label_y = item_rect.centery - label_text.get_height() // 2
            screen.blit(label_text, (label_x, label_y))
            
            # Badge (if present)
            if item.badge:
                badge_text = self.badge_font.render(item.badge, True, (255, 255, 255))
                badge_width = badge_text.get_width() + 8
                badge_height = 16
                badge_x = item_rect.right - badge_width - 10
                badge_y = item_rect.centery - badge_height // 2
                
                badge_rect = pygame.Rect(badge_x, badge_y, badge_width, badge_height)
                pygame.draw.rect(screen, self.badge_color, badge_rect, border_radius=8)
                screen.blit(badge_text, (badge_x + 4, badge_y + 2))
