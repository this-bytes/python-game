"""Assignment Workflow Panel - Streamlines specialist-to-incident assignment.

This panel provides a guided workflow for:
- Selecting specialists by specialty
- Viewing incident requirements
- Suggesting best matches
- Confirming assignments
- Showing assignment success/failure reasons
"""

import pygame
from typing import List, Optional, Callable, Tuple
from src.models.specialist import Specialist
from src.models.incident import Incident
from src.utils.logger import GameLogger


class AssignmentWorkflowPanel:
    """Panel managing the assignment workflow between specialists and incidents."""
    
    # States
    STATE_SELECT_SPECIALIST = "select_specialist"
    STATE_SELECT_INCIDENT = "select_incident"
    STATE_CONFIRM = "confirm"
    STATE_RESULT = "result"
    
    # Layout
    PADDING = 10
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 30
    
    # Colors
    BG_COLOR = (20, 25, 35)
    SECTION_BG = (30, 35, 45)
    SECTION_HOVER = (40, 45, 60)
    TEXT_COLOR = (220, 220, 230)
    LABEL_COLOR = (140, 150, 170)
    SUCCESS_COLOR = (80, 200, 120)
    WARNING_COLOR = (255, 200, 50)
    ERROR_COLOR = (220, 80, 80)
    NEUTRAL_COLOR = (100, 150, 200)
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize assignment workflow panel.
        
        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.logger = GameLogger("assignment_workflow")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 11)
        self.font_value = pygame.font.SysFont('Arial', 11, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 9)
        
        # Workflow state
        self.current_state = self.STATE_SELECT_SPECIALIST
        self.selected_specialist: Optional[Specialist] = None
        self.selected_incident: Optional[Incident] = None
        self.assignment_result: Optional[str] = None
        
        # Buttons
        self.confirm_button: Optional[pygame.Rect] = None
        self.cancel_button: Optional[pygame.Rect] = None
        self.reset_button: Optional[pygame.Rect] = None
        
        self.on_assignment_confirm: Optional[Callable[[str, str], None]] = None
    
    def set_assignment_callback(self, callback: Callable[[str, str], None]):
        """Set callback for confirmed assignments."""
        self.on_assignment_confirm = callback
    
    def set_selection(self, specialist_id: Optional[str], incident_id: Optional[str],
                     specialists: List[Specialist], incidents: List[Incident]):
        """Update selected specialist and incident.
        
        Args:
            specialist_id: Selected specialist ID or None
            incident_id: Selected incident ID or None
            specialists: List of all specialists
            incidents: List of all incidents
        """
        self.selected_specialist = next(
            (s for s in specialists if s.id == specialist_id), 
            None
        )
        self.selected_incident = next(
            (i for i in incidents if i.id == incident_id), 
            None
        )
        
        # Update state based on selections
        if self.selected_specialist and self.selected_incident:
            self.current_state = self.STATE_CONFIRM
        else:
            self.current_state = self.STATE_SELECT_SPECIALIST
    
    def confirm_assignment(self):
        """Confirm the current assignment."""
        if self.selected_specialist and self.selected_incident:
            if self.on_assignment_confirm:
                self.on_assignment_confirm(
                    self.selected_specialist.id,
                    self.selected_incident.id
                )
            
            # Check if assignment is valid
            is_valid = self._validate_assignment()
            if is_valid:
                self.assignment_result = f"✓ Assigned to {self.selected_specialist.name}"
                self.current_state = self.STATE_RESULT
            else:
                self.assignment_result = "✗ Assignment failed - check compatibility"
                self.current_state = self.STATE_RESULT
            
            self.logger.info(f"Assignment confirmed: {self.assignment_result}")
    
    def reset_workflow(self):
        """Reset the workflow to initial state."""
        self.selected_specialist = None
        self.selected_incident = None
        self.assignment_result = None
        self.current_state = self.STATE_SELECT_SPECIALIST
        self.logger.debug("Workflow reset")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events.
        
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.confirm_button and self.confirm_button.collidepoint(event.pos):
                self.confirm_assignment()
                return True
            
            if self.reset_button and self.reset_button.collidepoint(event.pos):
                self.reset_workflow()
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Render the assignment workflow panel.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, (60, 70, 90), self.rect, width=1)
        
        # Title
        title_text = self.font_title.render("Assignment Workflow", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        y_offset = self.rect.y + 35
        
        if self.current_state == self.STATE_SELECT_SPECIALIST:
            self._draw_select_specialist_state(screen, y_offset)
        elif self.current_state == self.STATE_SELECT_INCIDENT:
            self._draw_select_incident_state(screen, y_offset)
        elif self.current_state == self.STATE_CONFIRM:
            self._draw_confirm_state(screen, y_offset)
        elif self.current_state == self.STATE_RESULT:
            self._draw_result_state(screen, y_offset)
    
    def _draw_select_specialist_state(self, screen: pygame.Surface, y_offset: int):
        """Draw specialist selection state."""
        instruction_text = self.font_label.render(
            "1. Select a specialist from the roster",
            True,
            self.LABEL_COLOR
        )
        screen.blit(instruction_text, (self.rect.x + 10, y_offset))
        
        status_text = self.font_value.render(
            "⏳ Awaiting specialist selection...",
            True,
            self.NEUTRAL_COLOR
        )
        screen.blit(status_text, (self.rect.x + 10, y_offset + 30))
    
    def _draw_select_incident_state(self, screen: pygame.Surface, y_offset: int):
        """Draw incident selection state."""
        if self.selected_specialist:
            spec_text = self.font_label.render(
                f"Specialist: {self.selected_specialist.name}",
                True,
                self.TEXT_COLOR
            )
            screen.blit(spec_text, (self.rect.x + 10, y_offset))
        
        instruction_text = self.font_label.render(
            "2. Select an incident from the queue",
            True,
            self.LABEL_COLOR
        )
        screen.blit(instruction_text, (self.rect.x + 10, y_offset + 30))
    
    def _draw_confirm_state(self, screen: pygame.Surface, y_offset: int):
        """Draw confirmation state showing match analysis."""
        # Specialist info
        spec_label = self.font_label.render("Specialist:", True, self.LABEL_COLOR)
        screen.blit(spec_label, (self.rect.x + 10, y_offset))
        
        if self.selected_specialist:
            spec_text = self.font_value.render(
                f"{self.selected_specialist.name} (Level {self.selected_specialist.level})",
                True,
                self.TEXT_COLOR
            )
            screen.blit(spec_text, (self.rect.x + 120, y_offset))
            
            spec_specialty = self.font_label.render(
                f"Specialty: {self.selected_specialist.specialty}",
                True,
                self.LABEL_COLOR
            )
            screen.blit(spec_specialty, (self.rect.x + 10, y_offset + 25))
        
        y_offset += 55
        
        # Incident info
        inc_label = self.font_label.render("Incident:", True, self.LABEL_COLOR)
        screen.blit(inc_label, (self.rect.x + 10, y_offset))
        
        if self.selected_incident:
            inc_text = self.font_value.render(
                f"{self.selected_incident.incident_type}",
                True,
                self.TEXT_COLOR
            )
            screen.blit(inc_text, (self.rect.x + 120, y_offset))
            
            inc_spec = self.font_label.render(
                f"Required: {self.selected_incident.specialty_required}",
                True,
                self.LABEL_COLOR
            )
            screen.blit(inc_spec, (self.rect.x + 10, y_offset + 25))
        
        y_offset += 55
        
        # Match analysis
        match_color, match_text = self._get_match_analysis()
        match_label = self.font_value.render("Compatibility:", True, self.LABEL_COLOR)
        screen.blit(match_label, (self.rect.x + 10, y_offset))
        
        match_value = self.font_value.render(match_text, True, match_color)
        screen.blit(match_value, (self.rect.x + 150, y_offset))
        
        # Buttons
        button_y = self.rect.y + self.rect.height - 45
        
        self.confirm_button = pygame.Rect(
            self.rect.x + 10,
            button_y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        
        self.reset_button = pygame.Rect(
            self.rect.x + 100,
            button_y,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        
        pygame.draw.rect(screen, self.SUCCESS_COLOR, self.confirm_button)
        pygame.draw.rect(screen, self.ERROR_COLOR, self.reset_button)
        
        confirm_text = self.font_label.render("Confirm", True, self.BG_COLOR)
        reset_text = self.font_label.render("Reset", True, self.BG_COLOR)
        
        confirm_rect = confirm_text.get_rect(center=self.confirm_button.center)
        reset_rect = reset_text.get_rect(center=self.reset_button.center)
        
        screen.blit(confirm_text, confirm_rect)
        screen.blit(reset_text, reset_rect)
    
    def _draw_result_state(self, screen: pygame.Surface, y_offset: int):
        """Draw result state showing assignment outcome."""
        if self.assignment_result:
            if "✓" in self.assignment_result:
                color = self.SUCCESS_COLOR
            else:
                color = self.ERROR_COLOR
            
            result_text = self.font_value.render(self.assignment_result, True, color)
            screen.blit(result_text, (self.rect.x + 10, y_offset))
        
        # Reset button
        self.reset_button = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + self.rect.height - 45,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        
        pygame.draw.rect(screen, self.NEUTRAL_COLOR, self.reset_button)
        reset_text = self.font_label.render("Reset", True, self.BG_COLOR)
        reset_rect = reset_text.get_rect(center=self.reset_button.center)
        screen.blit(reset_text, reset_rect)
    
    def _get_match_analysis(self) -> Tuple[Tuple[int, int, int], str]:
        """Analyze specialist-incident match quality.
        
        Returns:
            Tuple of (color, text)
        """
        if not self.selected_specialist or not self.selected_incident:
            return (self.NEUTRAL_COLOR, "N/A")
        
        is_valid = self._validate_assignment()
        specialty_match = (self.selected_specialist.specialty == 
                          self.selected_incident.specialty_required)
        level_adequate = (self.selected_specialist.level >= 
                         getattr(self.selected_incident, 'min_level', 1))
        
        if specialty_match and level_adequate:
            return (self.SUCCESS_COLOR, "✓ Excellent Match")
        elif specialty_match:
            return (self.WARNING_COLOR, "⚠ Level Mismatch")
        else:
            return (self.ERROR_COLOR, "✗ Incompatible")
    
    def _validate_assignment(self) -> bool:
        """Validate if assignment is possible.
        
        Returns:
            True if assignment is valid
        """
        if not self.selected_specialist or not self.selected_incident:
            return False
        
        # Check specialty match
        if (self.selected_specialist.specialty != 
            self.selected_incident.specialty_required):
            return False
        
        # Check availability
        if hasattr(self.selected_specialist, 'current_incident'):
            if self.selected_specialist.current_incident is not None:
                return False
        
        return True
