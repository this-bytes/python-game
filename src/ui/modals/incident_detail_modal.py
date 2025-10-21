"""Incident Detail Modal - Shows full incident information and actions."""

import pygame
from typing import Optional
from utils.logger import Logger

from src.models.incident import Incident
from src.ui.components.panel import ModernPanel
from src.ui.components.button import ModernButton, ButtonStyle
from src.ui import event_types


class IncidentDetailModal(ModernPanel):
    """Modal that displays detailed incident information."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state,
        incident_id: str,
        **kwargs,
    ):
        """Initialize incident detail modal.
        
        Args:
            screen: The main display surface.
            game_state: Game state reference.
            incident_id: ID of the incident to display.
            **kwargs: Additional arguments (ignored).
        """
        self.incident = game_state.get_incident_by_id(incident_id)
        if not self.incident:
            raise ValueError(f"Incident with ID {incident_id} not found.")

        # Center on screen
        super().__init__(
            title=f"Incident: {self.incident.incident_type}",
            position=(
                (screen.get_width() - 520) // 2,
                (screen.get_height() - 400) // 2
            ),
            size=(520, 400),
            closeable=True,
            minimizable=False,
            draggable=True,
        )
        
        self.screen = screen
        self.game_state = game_state
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.normal_font = pygame.font.SysFont('Arial', 14)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Colors
        self.text_color = (220, 220, 220)
        self.label_color = (150, 150, 200)
        self.value_color = (100, 200, 255)
        
        # Buttons
        self.assign_button = ModernButton(
            text="Assign Specialist",
            position=(0, 0),  # Repositioned in render_content
            size=(150, 35),
            callback=self._on_assign_clicked,
            style=ButtonStyle.PRIMARY,
        )
        
        self.close_button_action = ModernButton(
            text="Close",
            position=(0, 0),  # Repositioned in render_content
            size=(150, 35),
            callback=self._on_close_clicked,
            style=ButtonStyle.SECONDARY,
        )

    def _on_assign_clicked(self):
        """Handle assign button click."""
        # This would ideally open a specialist selection view or modal
        
        print(f"Assign button clicked for incident {self.incident.id}")
        self._on_close_clicked()

    def _on_close_clicked(self):
        """Handle close button click."""
        pygame.event.post(pygame.event.Event(event_types.HIDE_MODAL))
        
    def handle_event(self, event: pygame.event.Event):
        """Handle events for the modal."""
        super().handle_event(event)
        self.assign_button.handle_event(event)
        self.close_button_action.handle_event(event)
        return True # Consume all events
        
    def update(self, delta_time: float):
        """Update modal state."""
        pass
        
    def draw(self):
        """Draw the modal."""
        super().render(self.screen)

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render the content of the modal."""
        y_offset = content_rect.y + 10

        # Incident Details
        # Compute SLA timer using the Incident API (time_remaining property)
        try:
            sla_remaining = float(self.incident.time_remaining)
        except Exception:
            # Fallback to 0 if unexpected
            sla_remaining = 0.0

        details = {
            "Client": self.incident.client_id,
            "Difficulty": str(self.incident.difficulty),
            "Specialty Required": self.incident.specialty_required,
            "Status": self.incident.status.capitalize(),
            "SLA Timer": f"{max(0.0, sla_remaining):.0f}s remaining",
        }

        for label, value in details.items():
            self._draw_detail_row(screen, content_rect.x, y_offset, label, value)
            y_offset += 25
            
        y_offset += 10
        
        # Description (not all Incident instances include a description field)
        incident_description = getattr(self.incident, 'description', None)
        if not incident_description:
            # Fallback to incident type as a brief description
            incident_description = f"{self.incident.incident_type} incident"

        self._draw_text_box(
            screen,
            content_rect.x,
            y_offset,
            content_rect.width,
            "Description",
            incident_description
        )
        y_offset += 80

        # Buttons
        self.assign_button.position = (content_rect.x + 10, content_rect.bottom - 45)
        self.close_button_action.position = (content_rect.right - 160, content_rect.bottom - 45)
        self.assign_button.render(screen)
        self.close_button_action.render(screen)

    def _draw_detail_row(self, screen, x, y, label, value):
        """Draw a label-value pair."""
        label_text = self.normal_font.render(f"{label}:", True, self.label_color)
        screen.blit(label_text, (x + 10, y))
        
        value_text = self.normal_font.render(value, True, self.text_color)
        screen.blit(value_text, (x + 180, y))

    def _draw_text_box(self, screen, x, y, width, title, text):
        """Draw a titled text box for descriptions."""
        # Title
        title_text = self.title_font.render(title, True, self.label_color)
        screen.blit(title_text, (x + 10, y))
        y += 25

        # Text content (wrapped)
        box_rect = pygame.Rect(x + 10, y, width - 20, 60)
        pygame.draw.rect(screen, (20, 20, 30), box_rect, border_radius=3)
        pygame.draw.rect(screen, (50, 50, 60), box_rect, 1, border_radius=3)
        
        self._render_text_wrapped(screen, text, box_rect.inflate(-10, -10))

    def _render_text_wrapped(self, surface, text, rect):
        """Render text with word wrapping."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.small_font.size(test_line)[0] < rect.width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        y = rect.y
        for line in lines:
            if y + self.small_font.get_height() > rect.bottom:
                break
            line_surface = self.small_font.render(line, True, self.text_color)
            surface.blit(line_surface, (rect.x, y))
            y += self.small_font.get_height()

