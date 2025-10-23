"""Tab navigation component for screen-level separation.

Provides persistent tab navigation allowing quick switching between major
system areas (Dashboard, Operations, Incidents, Specialists, Analytics).
"""

import pygame
from typing import List, Callable, Optional
from dataclasses import dataclass

from src.utils.logger import GameLogger


@dataclass
class Tab:
    """Represents a single tab in the tab bar."""
    id: str
    label: str
    icon: Optional[str] = None  # Emoji icon or single char
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        return self.id == other.id


class TabBar:
    """Horizontal tab navigation bar for screen separation.
    
    Features:
    - Persistent tabs at top of screen
    - Active tab highlighting
    - Hover states
    - Click callbacks for tab switching
    - Auto-sizing based on content
    """

    # Style constants
    TAB_HEIGHT = 40
    TAB_MIN_WIDTH = 120
    TAB_PADDING = 15
    ICON_PADDING = 8
    
    BG_COLOR = (25, 25, 35)
    INACTIVE_COLOR = (70, 70, 90)
    ACTIVE_COLOR = (100, 150, 200)
    HOVER_COLOR = (120, 170, 220)
    BORDER_COLOR = (50, 50, 70)
    TEXT_COLOR = (220, 220, 230)
    ACTIVE_TEXT_COLOR = (255, 255, 255)

    def __init__(
        self,
        tabs: List[Tab],
        x: int = 0,
        y: int = 0,
        width: int = 1280,
        on_tab_selected: Optional[Callable[[str], None]] = None
    ):
        """Initialize tab bar.
        
        Args:
            tabs: List of Tab objects to display
            x: X position
            y: Y position
            width: Total width available for tabs
            on_tab_selected: Callback when tab is selected
        """
        self.logger = GameLogger("tab_bar")
        self.tabs = tabs
        self.x = x
        self.y = y
        self.width = width
        self.on_tab_selected = on_tab_selected
        
        self.active_tab_id = tabs[0].id if tabs else None
        self.hovered_tab_id: Optional[str] = None
        
        # Calculate tab positions
        self.tab_rects: dict[str, pygame.Rect] = {}
        self._calculate_tab_positions()
        
        # Font for tab labels
        self.font = pygame.font.SysFont('Arial', 13, bold=False)
        self.active_font = pygame.font.SysFont('Arial', 13, bold=True)
        
        self.logger.info(f"[TAB_BAR] Initialized with {len(tabs)} tabs")

    def _calculate_tab_positions(self) -> None:
        """Calculate positions of all tabs."""
        self.tab_rects.clear()
        
        # Calculate tab width (distributed evenly)
        available_width = self.width - (len(self.tabs) - 1) * 2  # Account for separators
        tab_width = max(self.TAB_MIN_WIDTH, available_width // len(self.tabs))
        
        x_offset = self.x
        for tab in self.tabs:
            self.tab_rects[tab.id] = pygame.Rect(
                x_offset,
                self.y,
                tab_width,
                self.TAB_HEIGHT
            )
            x_offset += tab_width + 2  # 2px separator
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check which tab was clicked
            for tab in self.tabs:
                if self.tab_rects[tab.id].collidepoint(event.pos):
                    self.select_tab(tab.id)
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hovered_tab_id = None
            for tab in self.tabs:
                if self.tab_rects[tab.id].collidepoint(event.pos):
                    self.hovered_tab_id = tab.id
                    break
        
        return False
    
    def select_tab(self, tab_id: str) -> None:
        """Select a specific tab.
        
        Args:
            tab_id: ID of tab to select
        """
        if tab_id == self.active_tab_id:
            return  # Already active
        
        self.active_tab_id = tab_id
        self.logger.debug(f"[TAB_BAR] Tab selected: {tab_id}")
        
        if self.on_tab_selected:
            self.on_tab_selected(tab_id)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the tab bar.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.TAB_HEIGHT)
        pygame.draw.rect(screen, self.BG_COLOR, bg_rect)
        pygame.draw.line(screen, self.BORDER_COLOR, 
                        (self.x, self.y + self.TAB_HEIGHT - 1),
                        (self.x + self.width, self.y + self.TAB_HEIGHT - 1), 2)
        
        # Draw each tab
        for tab in self.tabs:
            self._draw_tab(screen, tab)
    
    def _draw_tab(self, screen: pygame.Surface, tab: Tab) -> None:
        """Draw a single tab.
        
        Args:
            screen: Pygame surface to draw on
            tab: Tab to draw
        """
        rect = self.tab_rects[tab.id]
        is_active = tab.id == self.active_tab_id
        is_hovered = tab.id == self.hovered_tab_id
        
        # Draw tab background
        bg_color = self.ACTIVE_COLOR if is_active else (self.HOVER_COLOR if is_hovered else self.INACTIVE_COLOR)
        pygame.draw.rect(screen, bg_color, rect)
        
        # Draw tab border/separator
        if not is_active:
            pygame.draw.line(screen, self.BORDER_COLOR,
                            (rect.right, rect.top + 5),
                            (rect.right, rect.bottom - 5), 1)
        
        # Draw active indicator (bottom border)
        if is_active:
            pygame.draw.line(screen, (0, 180, 255),
                            (rect.left, rect.bottom - 2),
                            (rect.right, rect.bottom - 2), 3)
        
        # Draw text
        text_color = self.ACTIVE_TEXT_COLOR if is_active else self.TEXT_COLOR
        font = self.active_font if is_active else self.font
        
        # Construct label with icon if present
        label_text = f"{tab.icon} {tab.label}" if tab.icon else tab.label
        text_surface = font.render(label_text, True, text_color)
        
        # Center text in tab
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def get_active_tab(self) -> Optional[Tab]:
        """Get the currently active tab.
        
        Returns:
            Active Tab object or None
        """
        for tab in self.tabs:
            if tab.id == self.active_tab_id:
                return tab
        return None
    
    def get_content_area(self) -> pygame.Rect:
        """Get the rectangle for content area below tabs.
        
        Returns:
            Rect representing available space for tab content
        """
        return pygame.Rect(
            self.x,
            self.y + self.TAB_HEIGHT,
            self.width,
            720 - (self.y + self.TAB_HEIGHT)  # Assume 720 height
        )
