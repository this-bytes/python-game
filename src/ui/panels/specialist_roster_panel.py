"""Specialist Roster Panel - Shows team members and their current status.

This panel displays all specialists in a card-based layout showing:
- Name and specialty
- Current assignment (if any)
- Burnout level with visual bar
- Level and experience
- Status indicators (available, busy, resting)
"""

import pygame
from typing import List, Optional, Callable
from dataclasses import dataclass

from src.models.specialist import Specialist
from src.utils.logger import GameLogger


@dataclass
class SpecialistCard:
    """Visual representation of a specialist."""
    specialist: Specialist
    rect: pygame.Rect
    hovered: bool = False
    selected: bool = False


class SpecialistRosterPanel:
    """Panel showing the team of specialists."""
    
    # Layout constants
    CARD_WIDTH = 220
    CARD_HEIGHT = 120
    CARD_PADDING = 10
    CARDS_PER_ROW = 3
    
    # Colors
    BG_COLOR = (20, 25, 35)
    CARD_BG = (30, 35, 45)
    CARD_HOVER_BG = (40, 45, 60)
    CARD_SELECTED_BG = (50, 60, 80)
    BORDER_COLOR = (60, 70, 90)
    BORDER_HOVER = (80, 100, 130)
    TEXT_COLOR = (220, 220, 230)
    LABEL_COLOR = (140, 150, 170)
    
    # Status colors
    STATUS_AVAILABLE = (80, 200, 120)  # Green
    STATUS_BUSY = (255, 180, 50)  # Orange
    STATUS_RESTING = (100, 150, 255)  # Blue
    STATUS_CRITICAL = (220, 80, 80)  # Red
    
    # Burnout bar colors
    BURNOUT_LOW = (80, 200, 120)  # Green
    BURNOUT_MEDIUM = (255, 200, 50)  # Yellow
    BURNOUT_HIGH = (255, 150, 50)  # Orange
    BURNOUT_CRITICAL = (220, 80, 80)  # Red
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize specialist roster panel.
        
        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.logger = GameLogger("specialist_roster")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_name = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 11)
        self.font_value = pygame.font.SysFont('Arial', 11)
        
        self.cards: List[SpecialistCard] = []
        self.selected_specialist_id: Optional[str] = None
        self.on_specialist_selected: Optional[Callable[[str], None]] = None
    
    def set_selection_callback(self, callback: Callable[[str], None]):
        """Set callback for when a specialist is selected."""
        self.on_specialist_selected = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for specialist cards.
        
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEMOTION:
            for card in self.cards:
                card.hovered = card.rect.collidepoint(event.pos)
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                if card.rect.collidepoint(event.pos):
                    # Toggle selection
                    if self.selected_specialist_id == card.specialist.id:
                        self.selected_specialist_id = None
                    else:
                        self.selected_specialist_id = card.specialist.id
                        if self.on_specialist_selected:
                            self.on_specialist_selected(card.specialist.id)
                    
                    # Update all cards
                    for c in self.cards:
                        c.selected = (c.specialist.id == self.selected_specialist_id)
                    
                    return True
        
        return False
    
    def draw(self, screen: pygame.Surface, specialists: List[Specialist]):
        """Render the specialist roster panel.
        
        Args:
            screen: Pygame surface to draw on
            specialists: List of specialists to display
        """
        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        
        # Draw title
        title_text = self.font_title.render("Team Roster", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        # Draw specialist count
        count_text = self.font_label.render(
            f"{len(specialists)} specialists", 
            True, 
            self.LABEL_COLOR
        )
        screen.blit(count_text, (self.rect.x + self.rect.width - 120, self.rect.y + 12))
        
        # Calculate card positions
        self.cards.clear()
        start_x = self.rect.x + self.CARD_PADDING
        start_y = self.rect.y + 40
        
        for idx, specialist in enumerate(specialists):
            row = idx // self.CARDS_PER_ROW
            col = idx % self.CARDS_PER_ROW
            
            card_x = start_x + col * (self.CARD_WIDTH + self.CARD_PADDING)
            card_y = start_y + row * (self.CARD_HEIGHT + self.CARD_PADDING)
            
            card_rect = pygame.Rect(card_x, card_y, self.CARD_WIDTH, self.CARD_HEIGHT)
            
            # Check if this card is selected
            is_selected = (specialist.id == self.selected_specialist_id)
            
            card = SpecialistCard(
                specialist=specialist,
                rect=card_rect,
                hovered=card_rect.collidepoint(pygame.mouse.get_pos()),
                selected=is_selected
            )
            self.cards.append(card)
            
            self._draw_specialist_card(screen, card)
    
    def _draw_specialist_card(self, screen: pygame.Surface, card: SpecialistCard):
        """Draw a single specialist card.
        
        Args:
            screen: Pygame surface
            card: Specialist card to draw
        """
        specialist = card.specialist
        rect = card.rect
        
        # Determine background color based on state
        if card.selected:
            bg_color = self.CARD_SELECTED_BG
            border_color = self.STATUS_AVAILABLE
            border_width = 3
        elif card.hovered:
            bg_color = self.CARD_HOVER_BG
            border_color = self.BORDER_HOVER
            border_width = 2
        else:
            bg_color = self.CARD_BG
            border_color = self.BORDER_COLOR
            border_width = 1
        
        # Draw card background
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, width=border_width)
        
        # Status indicator (top-right corner dot)
        status_color = self._get_status_color(specialist)
        status_radius = 6
        status_pos = (rect.right - 15, rect.top + 15)
        pygame.draw.circle(screen, status_color, status_pos, status_radius)
        
        # Specialist name
        name_text = self.font_name.render(specialist.name, True, self.TEXT_COLOR)
        screen.blit(name_text, (rect.x + 10, rect.y + 8))
        
        # Specialty
        specialty_text = self.font_label.render(specialist.specialty, True, self.LABEL_COLOR)
        screen.blit(specialty_text, (rect.x + 10, rect.y + 28))
        
        # Level and XP
        level_text = self.font_value.render(
            f"Level {specialist.level}", 
            True, 
            self.TEXT_COLOR
        )
        screen.blit(level_text, (rect.x + 10, rect.y + 46))
        
        # Burnout bar
        burnout_label = self.font_label.render("Burnout:", True, self.LABEL_COLOR)
        screen.blit(burnout_label, (rect.x + 10, rect.y + 64))
        
        self._draw_burnout_bar(
            screen,
            rect.x + 70,
            rect.y + 66,
            130,
            12,
            specialist.burnout_level
        )
        
        # Current assignment status
        status_text = self._get_status_text(specialist)
        status_label = self.font_label.render(status_text, True, self.LABEL_COLOR)
        screen.blit(status_label, (rect.x + 10, rect.y + 84))
    
    def _draw_burnout_bar(self, screen: pygame.Surface, x: int, y: int, 
                          width: int, height: int, burnout_level: float):
        """Draw a burnout level bar.
        
        Args:
            screen: Pygame surface
            x, y: Bar position
            width, height: Bar dimensions
            burnout_level: Burnout percentage (0-100)
        """
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 50), bg_rect)
        pygame.draw.rect(screen, (80, 80, 90), bg_rect, width=1)
        
        # Fill bar based on burnout level
        if burnout_level > 0:
            fill_width = int((burnout_level / 100.0) * width)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            # Color based on burnout level
            if burnout_level < 30:
                color = self.BURNOUT_LOW
            elif burnout_level < 60:
                color = self.BURNOUT_MEDIUM
            elif burnout_level < 80:
                color = self.BURNOUT_HIGH
            else:
                color = self.BURNOUT_CRITICAL
            
            pygame.draw.rect(screen, color, fill_rect)
        
        # Percentage text
        percent_text = self.font_label.render(f"{burnout_level:.0f}%", True, self.TEXT_COLOR)
        text_x = x + width // 2 - percent_text.get_width() // 2
        text_y = y + height // 2 - percent_text.get_height() // 2
        screen.blit(percent_text, (text_x, text_y))
    
    def _get_status_color(self, specialist: Specialist) -> tuple:
        """Get status indicator color for specialist.
        
        Args:
            specialist: Specialist to check
            
        Returns:
            RGB color tuple
        """
        if specialist.burnout_level >= 80:
            return self.STATUS_CRITICAL
        elif hasattr(specialist, 'current_incident') and specialist.current_incident:
            return self.STATUS_BUSY
        elif hasattr(specialist, 'is_resting') and specialist.is_resting:
            return self.STATUS_RESTING
        else:
            return self.STATUS_AVAILABLE
    
    def _get_status_text(self, specialist: Specialist) -> str:
        """Get status text for specialist.
        
        Args:
            specialist: Specialist to check
            
        Returns:
            Status description string
        """
        if specialist.burnout_level >= 80:
            return "⚠️ Critical burnout!"
        elif hasattr(specialist, 'current_incident') and specialist.current_incident:
            return f"🔧 Working on incident"
        elif hasattr(specialist, 'is_resting') and specialist.is_resting:
            return "💤 Resting"
        else:
            return "✅ Available"
    
    def get_selected_specialist_id(self) -> Optional[str]:
        """Get the currently selected specialist ID.
        
        Returns:
            Selected specialist ID or None
        """
        return self.selected_specialist_id
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_specialist_id = None
        for card in self.cards:
            card.selected = False
