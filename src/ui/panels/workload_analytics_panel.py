"""Workload Analytics Panel - Visualizes team workload distribution and capacity.

This panel provides comprehensive workload management features:
- Team utilization percentage
- Workload distribution across specialists
- Capacity warnings and alerts
- Quick action buttons for load balancing
- Performance metrics visualization
"""

import pygame
from typing import List, Optional
from src.models.specialist import Specialist
from src.models.incident import Incident
from src.utils.logger import GameLogger


class WorkloadAnalyticsPanel:
    """Panel showing team workload and capacity analytics."""
    
    # Layout constants
    WIDGET_HEIGHT = 35
    WIDGET_PADDING = 5
    
    # Colors
    BG_COLOR = (20, 25, 35)
    WIDGET_BG = (30, 35, 45)
    WIDGET_HOVER_BG = (40, 45, 60)
    TEXT_COLOR = (220, 220, 230)
    LABEL_COLOR = (140, 150, 170)
    
    # Status colors
    CAPACITY_OK = (80, 200, 120)      # Green
    CAPACITY_CAUTION = (255, 200, 50)  # Yellow
    CAPACITY_WARNING = (255, 150, 50)  # Orange
    CAPACITY_CRITICAL = (220, 80, 80)  # Red
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize workload analytics panel.
        
        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.logger = GameLogger("workload_analytics")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_metric = pygame.font.SysFont('Arial', 12, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 10)
        self.font_value = pygame.font.SysFont('Arial', 11)
        
        self.hovered_widget: Optional[str] = None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events.
        
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered_widget = None
            for widget_name, widget_rect in self._get_widget_rects().items():
                if widget_rect.collidepoint(event.pos):
                    self.hovered_widget = widget_name
                    return True
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for widget_name, widget_rect in self._get_widget_rects().items():
                if widget_rect.collidepoint(event.pos):
                    self.logger.debug(f"Workload widget clicked: {widget_name}")
                    return True
        
        return False
    
    def _get_widget_rects(self) -> dict:
        """Get rectangles for all interactive widgets."""
        return {
            "rest_overworked": pygame.Rect(
                self.rect.x + 10,
                self.rect.y + 190,
                140,
                30
            ),
            "balance_load": pygame.Rect(
                self.rect.x + 160,
                self.rect.y + 190,
                140,
                30
            ),
        }
    
    def draw(self, screen: pygame.Surface, specialists: List[Specialist], 
             incidents: List[Incident]):
        """Render the workload analytics panel.
        
        Args:
            screen: Pygame surface to draw on
            specialists: List of specialists
            incidents: List of unassigned incidents
        """
        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, (60, 70, 90), self.rect, width=1)
        
        # Title
        title_text = self.font_title.render("Workload Analytics", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        y_offset = self.rect.y + 35
        
        # Team utilization metric
        utilization = self._calculate_team_utilization(specialists)
        self._draw_metric(
            screen,
            "Team Utilization",
            f"{utilization:.1f}%",
            y_offset,
            utilization
        )
        y_offset += 45
        
        # Average burnout
        avg_burnout = self._calculate_avg_burnout(specialists)
        self._draw_metric(
            screen,
            "Avg Burnout",
            f"{avg_burnout:.1f}%",
            y_offset,
            avg_burnout
        )
        y_offset += 45
        
        # Workload balance score
        balance_score = self._calculate_balance_score(specialists)
        self._draw_metric(
            screen,
            "Workload Balance",
            f"{balance_score:.1f}/10",
            y_offset,
            (balance_score / 10.0) * 100
        )
        y_offset += 45
        
        # Incident backlog
        backlog_text = self.font_metric.render(
            f"Incident Backlog: {len(incidents)} pending",
            True,
            self.TEXT_COLOR
        )
        screen.blit(backlog_text, (self.rect.x + 10, y_offset))
        y_offset += 35
        
        # Available specialists
        available = sum(1 for s in specialists if not hasattr(s, 'current_incident') 
                       or s.current_incident is None)
        available_text = self.font_metric.render(
            f"Available: {available}/{len(specialists)} specialists",
            True,
            self.TEXT_COLOR
        )
        screen.blit(available_text, (self.rect.x + 10, y_offset))
        
        # Quick action buttons
        self._draw_action_buttons(screen, specialists)
    
    def _draw_metric(self, screen: pygame.Surface, label: str, value: str, 
                     y: int, percentage: float):
        """Draw a metric with label, value, and progress bar.
        
        Args:
            screen: Pygame surface
            label: Metric label
            value: Metric value string
            y: Y position
            percentage: Percentage for bar (0-100)
        """
        # Label
        label_text = self.font_label.render(label, True, self.LABEL_COLOR)
        screen.blit(label_text, (self.rect.x + 10, y))
        
        # Value
        value_text = self.font_value.render(value, True, self.TEXT_COLOR)
        screen.blit(value_text, (self.rect.x + 280, y))
        
        # Progress bar
        bar_width = 250
        bar_height = 12
        bar_rect = pygame.Rect(
            self.rect.x + 10,
            y + 18,
            bar_width,
            bar_height
        )
        
        # Background
        pygame.draw.rect(screen, (40, 40, 50), bar_rect)
        pygame.draw.rect(screen, (80, 80, 90), bar_rect, width=1)
        
        # Fill based on percentage
        if percentage > 0:
            fill_width = int((percentage / 100.0) * bar_width)
            fill_rect = pygame.Rect(
                self.rect.x + 10,
                y + 18,
                fill_width,
                bar_height
            )
            
            # Color based on severity
            if percentage < 60:
                color = self.CAPACITY_OK
            elif percentage < 75:
                color = self.CAPACITY_CAUTION
            elif percentage < 90:
                color = self.CAPACITY_WARNING
            else:
                color = self.CAPACITY_CRITICAL
            
            pygame.draw.rect(screen, color, fill_rect)
    
    def _draw_action_buttons(self, screen: pygame.Surface, 
                             specialists: List[Specialist]):
        """Draw quick action buttons.
        
        Args:
            screen: Pygame surface
            specialists: List of specialists
        """
        button_y = self.rect.y + 190
        button_height = 30
        button_padding = 10
        
        # Rest overworked button
        rest_rect = pygame.Rect(
            self.rect.x + 10,
            button_y,
            140,
            button_height
        )
        
        is_hovered = self.hovered_widget == "rest_overworked"
        rest_color = (50, 120, 160) if is_hovered else (40, 100, 140)
        pygame.draw.rect(screen, rest_color, rest_rect)
        pygame.draw.rect(screen, (80, 150, 200) if is_hovered else (60, 120, 160), 
                        rest_rect, width=2)
        
        rest_text = self.font_label.render("Rest Overworked", True, self.TEXT_COLOR)
        text_rect = rest_text.get_rect(center=rest_rect.center)
        screen.blit(rest_text, text_rect)
        
        # Balance load button
        balance_rect = pygame.Rect(
            self.rect.x + 160,
            button_y,
            140,
            button_height
        )
        
        is_hovered = self.hovered_widget == "balance_load"
        balance_color = (50, 120, 160) if is_hovered else (40, 100, 140)
        pygame.draw.rect(screen, balance_color, balance_rect)
        pygame.draw.rect(screen, (80, 150, 200) if is_hovered else (60, 120, 160), 
                        balance_rect, width=2)
        
        balance_text = self.font_label.render("Balance Load", True, self.TEXT_COLOR)
        text_rect = balance_text.get_rect(center=balance_rect.center)
        screen.blit(balance_text, text_rect)
    
    def _calculate_team_utilization(self, specialists: List[Specialist]) -> float:
        """Calculate team utilization percentage.
        
        Args:
            specialists: List of specialists
            
        Returns:
            Utilization percentage (0-100)
        """
        if not specialists:
            return 0.0
        
        busy_count = sum(
            1 for s in specialists 
            if hasattr(s, 'current_incident') and s.current_incident is not None
        )
        return (busy_count / len(specialists)) * 100
    
    def _calculate_avg_burnout(self, specialists: List[Specialist]) -> float:
        """Calculate average burnout across team.
        
        Args:
            specialists: List of specialists
            
        Returns:
            Average burnout percentage
        """
        if not specialists:
            return 0.0
        
        total_burnout = sum(s.burnout_level for s in specialists)
        return total_burnout / len(specialists)
    
    def _calculate_balance_score(self, specialists: List[Specialist]) -> float:
        """Calculate workload balance score (1-10, 10 = perfectly balanced).
        
        Args:
            specialists: List of specialists
            
        Returns:
            Balance score (0-10)
        """
        if not specialists:
            return 10.0
        
        # Calculate workload variance
        workloads = []
        for s in specialists:
            has_incident = hasattr(s, 'current_incident') and s.current_incident
            workload = (s.burnout_level / 100.0) + (1.0 if has_incident else 0.0)
            workloads.append(workload)
        
        if not workloads:
            return 10.0
        
        # Calculate coefficient of variation
        avg_workload = sum(workloads) / len(workloads)
        if avg_workload == 0:
            return 10.0
        
        variance = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)
        std_dev = variance ** 0.5
        cv = std_dev / avg_workload if avg_workload > 0 else 0
        
        # Convert to 0-10 scale (lower CV = higher score)
        balance_score = max(0, min(10, 10 - (cv * 5)))
        return balance_score
