import pygame
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass

from src.utils.logger import GameLogger
from src.ui.ui_provider import UISummaryItem
from src.ui.components.base import UIComponent

@dataclass
class DashboardWidget:
    rect: pygame.Rect
    plugin_name: str
    summary: UISummaryItem
    hovered: bool = False

class DashboardPanel(UIComponent):
    WIDGET_WIDTH = 200
    WIDGET_HEIGHT = 80
    WIDGET_PADDING = 10
    FONT_SIZE_TITLE = 14
    FONT_SIZE_DATA = 11
    
    BG_COLOR = (25, 25, 35)
    BORDER_COLOR = (80, 80, 100)
    BORDER_HOVER_COLOR = (120, 120, 150)
    TEXT_COLOR = (220, 220, 230)
    
    def __init__(self, x: int, y: int, on_widget_clicked: Optional[Callable[[str], None]] = None):
        super().__init__(pygame.Rect(x, y, self.WIDGET_WIDTH, 1000)) # Height is dynamic
        self.on_widget_clicked = on_widget_clicked
        self.logger = GameLogger("dashboard_panel")
        
        self.font_title = pygame.font.SysFont('Arial', self.FONT_SIZE_TITLE, bold=True)
        self.font_data = pygame.font.SysFont('Arial', self.FONT_SIZE_DATA)
        
        self.widgets: List[DashboardWidget] = []
        self.dashboard_manager = None
        self.game_state = None

    def set_managers(self, dashboard_manager, game_state):
        self.dashboard_manager = dashboard_manager
        self.game_state = game_state

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for widget in self.widgets:
                if widget.rect.collidepoint(event.pos):
                    if self.on_widget_clicked:
                        self.on_widget_clicked(widget.plugin_name)
                    return True
        elif event.type == pygame.MOUSEMOTION:
            for widget in self.widgets:
                widget.hovered = widget.rect.collidepoint(event.pos)
        return False

    def update_hover(self) -> None:
        for widget in self.widgets:
            widget.hovered = widget.rect.collidepoint(pygame.mouse.get_pos())
    def draw(self, screen: pygame.Surface, game_state) -> None:
        if not self.dashboard_manager or not self.game_state:
            return

        dashboard_state = self.dashboard_manager.get_dashboard_layout(self.game_state)
        summaries = dashboard_state.summaries
        
        self.widgets.clear()
        current_y = self.rect.y
        
        for plugin_name, summary in summaries:
            widget_rect = pygame.Rect(self.rect.x, current_y, self.WIDGET_WIDTH, self.WIDGET_HEIGHT)
            widget = DashboardWidget(rect=widget_rect, plugin_name=plugin_name, summary=summary)
            self.widgets.append(widget)
            
            self._render_widget(screen, widget)
            current_y += self.WIDGET_HEIGHT + self.WIDGET_PADDING

    def _render_widget(self, screen: pygame.Surface, widget: DashboardWidget) -> None:
        summary = widget.summary
        rect = widget.rect
        
        border_color = self.BORDER_HOVER_COLOR if widget.hovered else self.BORDER_COLOR
        accent_color = summary.accent_color or (100, 150, 200)
        
        pygame.draw.rect(screen, self.BG_COLOR, rect)
        pygame.draw.rect(screen, border_color, rect, width=2)
        
        accent_bar = pygame.Rect(rect.left, rect.top, 4, rect.height)
        pygame.draw.rect(screen, accent_color, accent_bar)
        
        title_text = self.font_title.render(f"{summary.icon} {summary.title}", True, self.TEXT_COLOR)
        screen.blit(title_text, (rect.left + 12, rect.top + 6))
        
        line_y = rect.top + 26
        for i, line in enumerate(summary.lines[:2]):
            if i >= 2:
                break
            line_text = self.font_data.render(line, True, self.TEXT_COLOR)
            screen.blit(line_text, (rect.left + 12, line_y))
            line_y += 18