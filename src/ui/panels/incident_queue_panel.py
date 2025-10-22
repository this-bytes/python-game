"""Incident Queue Panel - Shows pending incidents ready for assignment.

This panel displays all unassigned incidents in a list format showing:
- Incident type and severity
- Client information
- SLA timer (countdown)
- Specialty required
- Difficulty level
- Click to select for assignment
"""

import pygame
from typing import List, Optional, Callable
from dataclasses import dataclass
import time

from src.models.incident import Incident
from src.utils.logger import GameLogger


@dataclass
class IncidentRow:
    """Visual representation of an incident in the queue."""
    incident: Incident
    rect: pygame.Rect
    hovered: bool = False
    selected: bool = False


class IncidentQueuePanel:
    """Panel showing pending incidents waiting for assignment."""
    
    # Layout constants
    ROW_HEIGHT = 60
    ROW_PADDING = 2
    
    # Colors
    BG_COLOR = (20, 25, 35)
    ROW_BG = (30, 35, 45)
    ROW_HOVER_BG = (40, 45, 60)
    ROW_SELECTED_BG = (50, 60, 80)
    BORDER_COLOR = (60, 70, 90)
    TEXT_COLOR = (220, 220, 230)
    LABEL_COLOR = (140, 150, 170)
    
    # Severity colors
    SEVERITY_LOW = (80, 200, 120)  # Green
    SEVERITY_MEDIUM = (255, 200, 50)  # Yellow
    SEVERITY_HIGH = (255, 150, 50)  # Orange
    SEVERITY_CRITICAL = (220, 80, 80)  # Red
    
    # SLA urgency colors
    SLA_OK = (80, 200, 120)  # Green
    SLA_WARNING = (255, 200, 50)  # Yellow
    SLA_URGENT = (255, 150, 50)  # Orange
    SLA_OVERDUE = (220, 80, 80)  # Red
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize incident queue panel.
        
        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.logger = GameLogger("incident_queue")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_type = pygame.font.SysFont('Arial', 13, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 11)
        self.font_value = pygame.font.SysFont('Arial', 11, bold=True)
        self.font_timer = pygame.font.SysFont('Courier New', 12, bold=True)
        
        self.rows: List[IncidentRow] = []
        self.selected_incident_id: Optional[str] = None
        self.on_incident_selected: Optional[Callable[[str], None]] = None
        self.scroll_offset = 0
    
    def set_selection_callback(self, callback: Callable[[str], None]):
        """Set callback for when an incident is selected."""
        self.on_incident_selected = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for incident rows.
        
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEMOTION:
            for row in self.rows:
                row.hovered = row.rect.collidepoint(event.pos)
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row in self.rows:
                if row.rect.collidepoint(event.pos):
                    # Toggle selection
                    if self.selected_incident_id == row.incident.id:
                        self.selected_incident_id = None
                    else:
                        self.selected_incident_id = row.incident.id
                        if self.on_incident_selected:
                            self.on_incident_selected(row.incident.id)
                    
                    # Update all rows
                    for r in self.rows:
                        r.selected = (r.incident.id == self.selected_incident_id)
                    
                    return True
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll support
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, self.scroll_offset)
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface, incidents: List[Incident], game_state):
        """Render the incident queue panel.
        
        Args:
            screen: Pygame surface to draw on
            incidents: List of pending incidents
            game_state: Game state for additional info
        """
        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        
        # Draw title
        title_text = self.font_title.render("Incident Queue", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        # Draw incident count
        count_text = self.font_label.render(
            f"{len(incidents)} pending", 
            True, 
            self.LABEL_COLOR
        )
        screen.blit(count_text, (self.rect.x + self.rect.width - 100, self.rect.y + 12))
        
        # Calculate row positions (with scrolling)
        self.rows.clear()
        start_y = self.rect.y + 40 - self.scroll_offset
        
        # Set clipping region for scrollable content
        content_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + 40,
            self.rect.width,
            self.rect.height - 40
        )
        screen.set_clip(content_rect)
        
        for idx, incident in enumerate(incidents):
            row_y = start_y + idx * (self.ROW_HEIGHT + self.ROW_PADDING)
            
            # Skip if row is outside visible area
            if row_y + self.ROW_HEIGHT < self.rect.y + 40:
                continue
            if row_y > self.rect.bottom:
                break
            
            row_rect = pygame.Rect(
                self.rect.x + 5,
                row_y,
                self.rect.width - 10,
                self.ROW_HEIGHT
            )
            
            # Check if this row is selected
            is_selected = (incident.id == self.selected_incident_id)
            
            row = IncidentRow(
                incident=incident,
                rect=row_rect,
                hovered=row_rect.collidepoint(pygame.mouse.get_pos()),
                selected=is_selected
            )
            self.rows.append(row)
            
            self._draw_incident_row(screen, row, game_state)
        
        # Reset clipping
        screen.set_clip(None)
        
        # Draw scrollbar if needed
        if len(incidents) * (self.ROW_HEIGHT + self.ROW_PADDING) > content_rect.height:
            self._draw_scrollbar(screen, len(incidents))
    
    def _draw_incident_row(self, screen: pygame.Surface, row: IncidentRow, game_state):
        """Draw a single incident row.
        
        Args:
            screen: Pygame surface
            row: Incident row to draw
            game_state: Game state for context
        """
        incident = row.incident
        rect = row.rect
        
        # Determine background color based on state
        if row.selected:
            bg_color = self.ROW_SELECTED_BG
            border_width = 2
            border_color = self.SEVERITY_HIGH
        elif row.hovered:
            bg_color = self.ROW_HOVER_BG
            border_width = 1
            border_color = self.BORDER_COLOR
        else:
            bg_color = self.ROW_BG
            border_width = 1
            border_color = self.BORDER_COLOR
        
        # Draw row background
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, width=border_width)
        
        # Severity indicator (left bar)
        severity_color = self._get_severity_color(incident)
        severity_bar = pygame.Rect(rect.left, rect.top, 4, rect.height)
        pygame.draw.rect(screen, severity_color, severity_bar)
        
        # Incident type (main text)
        type_text = self.font_type.render(incident.incident_type, True, self.TEXT_COLOR)
        screen.blit(type_text, (rect.x + 12, rect.y + 8))
        
        # Client name
        client_text = self.font_label.render(
            f"Client: {incident.client_id[:15]}{'...' if len(incident.client_id) > 15 else ''}", 
            True, 
            self.LABEL_COLOR
        )
        screen.blit(client_text, (rect.x + 12, rect.y + 26))
        
        # Specialty required
        specialty_text = self.font_label.render(
            f"📋 {incident.specialty_required}", 
            True, 
            self.TEXT_COLOR
        )
        screen.blit(specialty_text, (rect.x + 12, rect.y + 42))
        
        # Difficulty indicator (right side)
        difficulty_text = self.font_value.render(
            f"Difficulty: {incident.difficulty}/5",
            True,
            self.TEXT_COLOR
        )
        screen.blit(difficulty_text, (rect.x + 220, rect.y + 8))
        
        # SLA timer (right side, prominent)
        sla_time_remaining = self._get_sla_time_remaining(incident, game_state)
        sla_color = self._get_sla_urgency_color(sla_time_remaining, incident.sla_seconds)
        
        timer_text = self.font_timer.render(
            self._format_time(sla_time_remaining),
            True,
            sla_color
        )
        screen.blit(timer_text, (rect.x + 220, rect.y + 28))
        
        # SLA label
        sla_label = self.font_label.render("SLA:", True, self.LABEL_COLOR)
        screen.blit(sla_label, (rect.x + 220, rect.y + 44))
    
    def _draw_scrollbar(self, screen: pygame.Surface, incident_count: int):
        """Draw scrollbar for the incident list.
        
        Args:
            screen: Pygame surface
            incident_count: Total number of incidents
        """
        scrollbar_x = self.rect.right - 8
        scrollbar_y = self.rect.y + 40
        scrollbar_height = self.rect.height - 40
        
        # Background
        pygame.draw.rect(
            screen,
            (40, 40, 50),
            pygame.Rect(scrollbar_x, scrollbar_y, 6, scrollbar_height)
        )
        
        # Calculate thumb size and position
        content_height = incident_count * (self.ROW_HEIGHT + self.ROW_PADDING)
        visible_ratio = scrollbar_height / content_height
        thumb_height = max(20, int(scrollbar_height * visible_ratio))
        
        scroll_ratio = self.scroll_offset / max(1, content_height - scrollbar_height)
        thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
        
        # Thumb
        pygame.draw.rect(
            screen,
            (100, 110, 130),
            pygame.Rect(scrollbar_x, thumb_y, 6, thumb_height)
        )
    
    def _get_severity_color(self, incident: Incident) -> tuple:
        """Get color based on incident difficulty.
        
        Args:
            incident: Incident to check
            
        Returns:
            RGB color tuple
        """
        if incident.difficulty <= 1:
            return self.SEVERITY_LOW
        elif incident.difficulty <= 2:
            return self.SEVERITY_MEDIUM
        elif incident.difficulty <= 4:
            return self.SEVERITY_HIGH
        else:
            return self.SEVERITY_CRITICAL
    
    def _get_sla_time_remaining(self, incident: Incident, game_state) -> float:
        """Calculate SLA time remaining for an incident.
        
        Args:
            incident: Incident to check
            game_state: Game state for current time
            
        Returns:
            Seconds remaining (negative if overdue)
        """
        # Get current game time
        current_time = getattr(game_state, 'game_time', time.time())
        
        # Calculate time since spawn
        if hasattr(incident, 'spawn_time'):
            elapsed = current_time - incident.spawn_time
        else:
            elapsed = 0
        
        return incident.sla_seconds - elapsed
    
    def _get_sla_urgency_color(self, time_remaining: float, sla_seconds: float) -> tuple:
        """Get color based on SLA urgency.
        
        Args:
            time_remaining: Seconds remaining
            sla_seconds: Total SLA seconds
            
        Returns:
            RGB color tuple
        """
        if time_remaining < 0:
            return self.SLA_OVERDUE
        
        ratio = time_remaining / sla_seconds
        if ratio > 0.5:
            return self.SLA_OK
        elif ratio > 0.25:
            return self.SLA_WARNING
        else:
            return self.SLA_URGENT
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 0:
            # Overdue
            abs_seconds = abs(int(seconds))
            minutes = abs_seconds // 60
            secs = abs_seconds % 60
            return f"-{minutes:02d}:{secs:02d}"
        else:
            int_seconds = int(seconds)
            minutes = int_seconds // 60
            secs = int_seconds % 60
            return f"{minutes:02d}:{secs:02d}"
    
    def get_selected_incident_id(self) -> Optional[str]:
        """Get the currently selected incident ID.
        
        Returns:
            Selected incident ID or None
        """
        return self.selected_incident_id
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_incident_id = None
        for row in self.rows:
            row.selected = False
