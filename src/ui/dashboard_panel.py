"""Dashboard Panel - Renders UIProvider summaries as an overlay.

Displays all UI summaries from UIProvider plugins as clickable widgets.
Simple, clean, and extensible - any plugin implementing UIProvider automatically
gets a dashboard widget without modifying this code.
"""

import pygame
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass

from src.utils.logger import GameLogger
from src.ui.ui_provider import UISummaryItem


@dataclass
class DashboardWidget:
    """Represents a rendered dashboard widget on screen."""
    rect: pygame.Rect
    plugin_name: str
    summary: UISummaryItem
    hovered: bool = False


class DashboardPanel:
    """Minimal dashboard panel showing UIProvider summaries.
    
    This panel queries DashboardManager for all UI summaries and renders them
    as simple widgets. When clicked, widgets emit callback to open detail panel.
    
    Design:
    - Top-left corner, vertical stack of widgets
    - Each widget shows icon, title, and 2-3 key lines of data
    - Color-coded by accent_color from UIProvider
    - Click to open detail panel for that plugin
    
    Example:
        ```python
        dashboard = DashboardPanel(
            x=10, y=60,
            on_widget_clicked=lambda plugin_name: print(f"Clicked {plugin_name}")
        )
        dashboard.render(screen, dashboard_manager, game_state)
        ```
    """
    
    # Display settings
    WIDGET_WIDTH = 200
    WIDGET_HEIGHT = 80
    WIDGET_PADDING = 10
    FONT_SIZE_TITLE = 14
    FONT_SIZE_DATA = 11
    
    # Colors
    BG_COLOR = (25, 25, 35)
    BORDER_COLOR = (80, 80, 100)
    BORDER_HOVER_COLOR = (120, 120, 150)
    TEXT_COLOR = (220, 220, 230)
    
    def __init__(
        self,
        x: int = 10,
        y: int = 60,
        on_widget_clicked: Optional[Callable[[str], None]] = None
    ):
        """Initialize dashboard panel.
        
        Args:
            x: X coordinate for top-left corner
            y: Y coordinate for top-left corner
            on_widget_clicked: Callback when widget clicked (passes plugin_name)
        """
        self.x = x
        self.y = y
        self.on_widget_clicked = on_widget_clicked
        self.logger = GameLogger("dashboard_panel")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', self.FONT_SIZE_TITLE, bold=True)
        self.font_data = pygame.font.SysFont('Arial', self.FONT_SIZE_DATA)
        
        # Widget tracking
        self.widgets: List[DashboardWidget] = []
        self.hovered_widget: Optional[DashboardWidget] = None
        
        self.logger.debug("[DASHBOARD] Panel initialized")
    
    def render(self, screen: pygame.Surface, dashboard_manager, game_state) -> None:
        """Render all dashboard widgets.
        
        Args:
            screen: Pygame surface to render to
            dashboard_manager: DashboardManager with summaries
            game_state: Current game state
        """
        if not dashboard_manager:
            return
        
        # Get current dashboard layout with all summaries
        dashboard_state = dashboard_manager.get_dashboard_layout(game_state)
        summaries = dashboard_state.summaries  # List of (plugin_name, summary) tuples
        
        # Update widgets list
        self.widgets.clear()
        current_y = self.y
        
        for plugin_name, summary in summaries:
            widget_rect = pygame.Rect(
                self.x,
                current_y,
                self.WIDGET_WIDTH,
                self.WIDGET_HEIGHT
            )
            
            widget = DashboardWidget(
                rect=widget_rect,
                plugin_name=plugin_name,
                summary=summary,
                hovered=False
            )
            self.widgets.append(widget)
            
            # Render widget
            self._render_widget(screen, widget)
            
            current_y += self.WIDGET_HEIGHT + self.WIDGET_PADDING
    
    def _render_widget(self, screen: pygame.Surface, widget: DashboardWidget) -> None:
        """Render a single dashboard widget.
        
        Args:
            screen: Pygame surface to render to
            widget: Widget to render
        """
        summary = widget.summary
        rect = widget.rect
        
        # Determine colors
        border_color = (
            self.BORDER_HOVER_COLOR 
            if widget.hovered 
            else self.BORDER_COLOR
        )
        
        # Get accent color from summary (or use default)
        accent_color = summary.accent_color or (100, 150, 200)
        
        # Draw background with border
        pygame.draw.rect(screen, self.BG_COLOR, rect)
        pygame.draw.rect(screen, border_color, rect, width=2)
        
        # Draw accent bar on left
        accent_bar = pygame.Rect(rect.left, rect.top, 4, rect.height)
        pygame.draw.rect(screen, accent_color, accent_bar)
        
        # Draw icon and title
        title_text = self.font_title.render(
            f"{summary.icon} {summary.title}",
            True,
            self.TEXT_COLOR
        )
        screen.blit(title_text, (rect.left + 12, rect.top + 6))
        
        # Draw data lines
        line_y = rect.top + 26
        for i, line in enumerate(summary.lines[:2]):  # Show only first 2 lines
            if i >= 2:
                break
            
            line_text = self.font_data.render(
                line,
                True,
                self.TEXT_COLOR
            )
            screen.blit(line_text, (rect.left + 12, line_y))
            line_y += 18
    
    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        hovered = None
        
        for widget in self.widgets:
            if widget.rect.collidepoint(mouse_pos):
                hovered = widget
                break
        
        # Update all widgets' hover state
        for widget in self.widgets:
            widget.hovered = (widget == hovered)
        
        self.hovered_widget = hovered
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click on dashboard.
        
        Args:
            mouse_pos: Mouse position of click
            
        Returns:
            Plugin name of clicked widget, or None
        """
        for widget in self.widgets:
            if widget.rect.collidepoint(mouse_pos):
                self.logger.debug(f"[DASHBOARD] Widget clicked: {widget.plugin_name}")
                
                if self.on_widget_clicked:
                    self.on_widget_clicked(widget.plugin_name)
                
                return widget.plugin_name
        
        return None
