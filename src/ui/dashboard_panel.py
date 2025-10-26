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
    GOOD_COLOR = (76, 175, 80)
    WARN_COLOR = (255, 152, 0)
    DANGER_COLOR = (244, 67, 54)
    
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
            # Allow core_summary to have slightly larger widget to show sample client info
            h = self.WIDGET_HEIGHT
            if plugin_name == 'core_summary':
                h = self.WIDGET_HEIGHT + 56  # extra space for sample client lines

            widget_rect = pygame.Rect(self.rect.x, current_y, self.WIDGET_WIDTH, h)
            widget = DashboardWidget(rect=widget_rect, plugin_name=plugin_name, summary=summary)
            self.widgets.append(widget)

            self._render_widget(screen, widget)
            current_y += h + self.WIDGET_PADDING

    def _render_widget(self, screen: pygame.Surface, widget: DashboardWidget) -> None:
        summary = widget.summary
        rect = widget.rect
        
        border_color = self.BORDER_HOVER_COLOR if widget.hovered else self.BORDER_COLOR
        accent_color = summary.accent_color or (100, 150, 200)

        # Background and border (hover slightly brightens background)
        bg = tuple(min(255, c + (20 if widget.hovered else 0)) for c in self.BG_COLOR)
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, border_color, rect, width=2)

        accent_bar = pygame.Rect(rect.left, rect.top, 6, rect.height)
        pygame.draw.rect(screen, accent_color, accent_bar)

        title_text = self.font_title.render(f"{summary.icon} {summary.title}", True, self.TEXT_COLOR)
        screen.blit(title_text, (rect.left + 16, rect.top + 8))
        
        line_y = rect.top + 26
        # Render up to 2 summary lines
        for i, line in enumerate(summary.lines[:2]):
            if i >= 2:
                break
            line_text = self.font_data.render(line, True, self.TEXT_COLOR)
            screen.blit(line_text, (rect.left + 12, line_y))
            line_y += 18

        # If this is the core summary, render a short sample of clients with satisfaction bars and quick stats
        if widget.plugin_name == 'core_summary':
            try:
                gs = self.game_state

                # If no game_state is available, render a simple placeholder stats line
                if gs is None:
                    stats_text = "Budget: N/A  Clients: 0  Incidents: 0  Specialists: 0"
                    stats_surf = self.font_data.render(stats_text, True, self.TEXT_COLOR)
                    screen.blit(stats_surf, (rect.left + 16, line_y))
                    line_y += 22
                else:
                    money = None
                    pending_incidents = 0
                    clients = getattr(gs, 'clients', []) or []
                    incidents = getattr(gs, 'incidents', []) or []
                    specialists = getattr(gs, 'specialists', []) or []

                    # Safely attempt to use a summarized API if present
                    gsum = None
                    try:
                        if hasattr(gs, 'get_game_summary') and callable(getattr(gs, 'get_game_summary')):
                            gsum = gs.get_game_summary()
                    except Exception:
                        gsum = None

                    if isinstance(gsum, dict):
                        money = gsum.get('current_money', money)
                        pending_incidents = gsum.get('pending_incidents_count', pending_incidents)
                    else:
                        money = getattr(gs, 'current_money', money) or getattr(gs, 'money', money)
                        pending_incidents = sum(1 for i in incidents if getattr(i, 'status', '') in ('pending', 'open') or not getattr(i, 'assigned_specialist_id', None))

                    # Draw a compact stats line under title
                    stats_text = f"Budget: ${int(money) if isinstance(money, (int, float)) else 'N/A'}  " \
                                 f"Clients: {len(clients)}  Incidents: {pending_incidents}  Specialists: {len(specialists)}"
                    stats_surf = self.font_data.render(stats_text, True, self.TEXT_COLOR)
                    screen.blit(stats_surf, (rect.left + 16, line_y))
                    line_y += 22

                    sample = clients[:3]
                    # small font for client rows
                    client_font = pygame.font.SysFont('Arial', 11)
                    for c in sample:
                        name = getattr(c, 'company_name', getattr(c, 'name', str(getattr(c, 'client_id', 'client'))))
                        sat = getattr(c, 'satisfaction', None)
                        sat_text = f"{int(sat*100)}%" if isinstance(sat, float) else (str(sat) if sat is not None else "N/A")
                        text = f"{name} — {sat_text}"
                        client_line = client_font.render(text, True, self.TEXT_COLOR)
                        screen.blit(client_line, (rect.left + 16, line_y))

                        # draw a small satisfaction bar
                        bar_x = rect.left + 16
                        bar_y = line_y + 14
                        bar_w = rect.width - 40
                        bar_h = 8
                        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
                        if isinstance(sat, float):
                            fill_w = int(bar_w * max(0.0, min(1.0, sat)))
                            # Choose color based on thresholds
                            if sat >= 0.8:
                                col = self.GOOD_COLOR
                            elif sat >= 0.5:
                                col = self.WARN_COLOR
                            else:
                                col = self.DANGER_COLOR
                            pygame.draw.rect(screen, col, (bar_x, bar_y, fill_w, bar_h))

                        line_y += 26
            except Exception:
                # Defensive: don't crash dashboard rendering on bad client objects
                pass