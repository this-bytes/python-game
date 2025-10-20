"""Incident Queue Panel for displaying active incidents."""

import pygame
from typing import Optional, Any
from src.ui.components.panel import Panel
from src.ui.components.scroll_container import ScrollContainer
from src.models.game_state import GameState
from src.models.incident import Incident
from src.ui.drag_drop_manager import get_drag_drop_manager


class IncidentQueuePanel(Panel):
    """Display all incidents with urgency indicators."""

    def __init__(self, game_state: GameState):
        """Initialize incident queue panel.

        Args:
            game_state: Game state reference
        """
        # Position accounts for navigation menu (200px) + specialist panel (380px) + margins (40px)
        super().__init__(
            title="Active Incidents",
            position=(640, 80),
            size=(400, 500),
            closeable=True,
            minimizable=True,
            draggable=True,
        )
        self.game_state = game_state
        self.scroll_container = ScrollContainer(
            position=(0, 0),
            size=(400, 468),
            content_height=0
        )
        self.selected_incident: Optional[Incident] = None
        self.drag_drop_manager = get_drag_drop_manager()

        # Card styling
        self.card_height = 70
        self.card_margin = 5

        # Urgency colors (based on SLA remaining)
        self.urgency_colors = {
            "critical": (255, 50, 50),    # <20% SLA
            "warning": (255, 200, 0),     # 20-50% SLA
            "normal": (0, 200, 100),      # >50% SLA
        }

        # Assignment status colors
        self.assignment_colors = {
            "assigned": (0, 150, 255),    # Blue for assigned
            "pending": (100, 100, 100),   # Gray for unassigned
        }

        # Fonts
        self.card_font = None
        self.small_font = None

    def assign_selected_to_specialist(self, specialist_id: str) -> bool:
        """Assign selected incident to a specialist.

        Args:
            specialist_id: ID of specialist to assign to

        Returns:
            True if assignment successful
        """
        if not self.selected_incident:
            return False

        return self.game_state.assign_incident_to_specialist(
            self.selected_incident.id,
            specialist_id
        )

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render incident queue content.

        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Initialize fonts if needed
        if self.card_font is None:
            self.card_font = pygame.font.SysFont('Arial', 14, bold=True)
            self.small_font = pygame.font.SysFont('Arial', 11)

        # Get active incidents
        incidents = [inc for inc in self.game_state.incidents if inc.status in ["pending", "assigned"]]

        # Update scroll container
        self.scroll_container.set_content_height(len(incidents) * (self.card_height + self.card_margin))
        self.scroll_container.position = (content_rect.x, content_rect.y)
        self.scroll_container.size = (content_rect.width, content_rect.height)

        # Create clipping region for scrolling
        screen.set_clip(content_rect)

        # Render incidents
        y_offset = content_rect.y - self.scroll_container.get_scroll_offset()

        for incident in incidents:
            card_rect = pygame.Rect(
                content_rect.x + self.card_margin,
                y_offset,
                content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                self.card_height
            )

            # Skip if not visible
            if card_rect.bottom < content_rect.top or card_rect.top > content_rect.bottom:
                y_offset += self.card_height + self.card_margin
                continue

            self._render_incident_card(screen, incident, card_rect)
            y_offset += self.card_height + self.card_margin

        # Reset clipping
        screen.set_clip(None)

        # Render scroll container
        self.scroll_container.render(screen)

        # Render dragged incident if any
        if self.drag_drop_manager.is_incident_being_dragged():
            self._render_dragged_incident(screen)

    def _render_dragged_incident(self, screen: pygame.Surface) -> None:
        """Render dragged incident at mouse position.

        Args:
            screen: Pygame surface to render on
        """
        dragged_incident = self.drag_drop_manager.get_dragged_incident()
        if not dragged_incident:
            return

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drag_offset = self.drag_drop_manager.get_drag_offset()
        
        # Calculate dragged card position (offset from mouse)
        drag_x = mouse_x - drag_offset[0]
        drag_y = mouse_y - drag_offset[1]
        
        # Create semi-transparent dragged card
        dragged_rect = pygame.Rect(drag_x, drag_y, self.card_height * 1.2, self.card_height)  # Slightly wider for visibility
        
        # Semi-transparent background
        drag_surface = pygame.Surface((dragged_rect.width, dragged_rect.height))
        drag_surface.set_alpha(200)
        drag_surface.fill((40, 60, 80))
        
        # Border
        pygame.draw.rect(drag_surface, (0, 180, 255), drag_surface.get_rect(), 3, border_radius=4)
        
        # Incident type (simplified for drag preview)
        if self.card_font:
            type_text = self.card_font.render(dragged_incident.incident_type, True, (255, 255, 255))
            drag_surface.blit(type_text, (10, 10))
        
        # Specialty
        if self.small_font:
            specialty_text = self.small_font.render(dragged_incident.specialty_required, True, (150, 150, 200))
            drag_surface.blit(specialty_text, (10, 35))
        
        # Render to screen
        screen.blit(drag_surface, (drag_x, drag_y))

    def _render_incident_card(self, screen: pygame.Surface, incident: Incident, rect: pygame.Rect) -> None:
        """Render individual incident card.

        Args:
            screen: Pygame surface to render on
            incident: Incident to render
            rect: Rectangle for card
        """
        # Determine urgency
        sla_percentage = (incident.time_remaining / incident.sla_time) * 100 if incident.sla_time > 0 else 0

        if sla_percentage < 20:
            urgency = "critical"
        elif sla_percentage < 50:
            urgency = "warning"
        else:
            urgency = "normal"

        urgency_color = self.urgency_colors[urgency]

        # Card background - color coded by assignment status
        if incident.status == "assigned":
            bg_color = (40, 60, 80)  # Blue-tinted for assigned
        else:
            bg_color = (45, 45, 60) if incident != self.selected_incident else (60, 60, 80)
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)

        # Border (color-coded by urgency)
        if incident == self.selected_incident:
            border_color = (0, 180, 255)
        else:
            border_color = urgency_color
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)

        # Urgency indicator bar (left side)
        indicator_rect = pygame.Rect(rect.x + 2, rect.y + 2, 4, rect.height - 4)
        pygame.draw.rect(screen, urgency_color, indicator_rect, border_radius=2)

        # Incident type
        type_text = self.card_font.render(incident.incident_type, True, self.text_color)
        screen.blit(type_text, (rect.x + 15, rect.y + 5))

        # Difficulty (stars)
        diff_text = self.small_font.render(f"Difficulty: {'★' * incident.difficulty}", True, (255, 200, 0))
        screen.blit(diff_text, (rect.x + 15, rect.y + 25))

        # Specialty required
        specialty_text = self.small_font.render(incident.specialty_required, True, (150, 150, 200))
        screen.blit(specialty_text, (rect.x + 15, rect.y + 42))

        # Status - more prominent for assignment status
        if incident.status == "assigned":
            status_color = self.assignment_colors["assigned"]
            status_text_content = "ASSIGNED ✓"
        else:
            status_color = self.assignment_colors["pending"]
            status_text_content = "PENDING"
        
        status_text = self.small_font.render(status_text_content, True, status_color)
        screen.blit(status_text, (rect.right - 100, rect.y + 5))

        # Assignment indicator bar (right side)
        assignment_rect = pygame.Rect(rect.right - 6, rect.y + 2, 4, rect.height - 4)
        assignment_color = self.assignment_colors[incident.status]
        pygame.draw.rect(screen, assignment_color, assignment_rect, border_radius=2)

        # SLA countdown
        sla_minutes = int(incident.time_remaining // 60)
        sla_seconds = int(incident.time_remaining % 60)
        sla_text = self.small_font.render(f"SLA: {sla_minutes:02d}:{sla_seconds:02d}", True, urgency_color)
        screen.blit(sla_text, (rect.right - 80, rect.y + 42))

        # Reward
        reward_text = self.small_font.render(f"${incident.base_reward:,.0f}", True, (0, 255, 100))
        screen.blit(reward_text, (rect.right - 80, rect.y + 54))

    def handle_event(self, event: Any) -> bool:
        """Handle events for incident queue panel.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed, False otherwise
        """
        # Handle panel events first
        if super().handle_event(event):
            return True

        # Handle scroll container events
        if self.scroll_container.handle_event(event):
            return True

        # Handle incident selection and drag start
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rect = self.get_rect()
            content_rect = pygame.Rect(
                rect.x + self.BORDER_WIDTH,
                rect.y + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
                rect.width - 2 * self.BORDER_WIDTH,
                rect.height - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
            )

            if content_rect.collidepoint(event.pos):
                incidents = [inc for inc in self.game_state.incidents if inc.status in ["pending", "assigned"]]
                y_offset = content_rect.y - self.scroll_container.get_scroll_offset()

                for incident in incidents:
                    card_rect = pygame.Rect(
                        content_rect.x + self.card_margin,
                        y_offset,
                        content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                        self.card_height
                    )

                    if card_rect.collidepoint(event.pos):
                        self.selected_incident = incident
                        # Start drag operation using drag drop manager
                        self.drag_drop_manager.start_drag(incident, event.pos, card_rect)
                        return True

                    y_offset += self.card_height + self.card_margin

        # Handle drag end (mouse button up)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag_drop_manager.is_incident_being_dragged():
                # End drag operation
                self.drag_drop_manager.end_drag()
                return True

        return False

    def get_selected_incident(self) -> Optional[Incident]:
        """Get currently selected incident.

        Returns:
            Selected incident or None
        """
        return self.selected_incident
