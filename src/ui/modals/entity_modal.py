"""Base class for entity-focused modals with consistent layout and styling.

Provides standard structure for modals that inspect/interact with a single entity
(specialist, incident, client, etc.).

Structure:
- Header: Entity name/title with close button
- Body: Sections with stats, attributes, relationships
- Footer: Action buttons
"""

import pygame
from typing import List, Callable, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.utils.logger import GameLogger


@dataclass
class ActionButton:
    """Represents an action button in the modal footer."""
    id: str
    label: str
    color: tuple = (100, 150, 200)
    on_click: Optional[Callable[[], None]] = None
    enabled: bool = True


class EntityModal(ABC):
    """Base class for entity-focused modals.
    
    Provides consistent structure:
    - Header with entity name and close button
    - Body with stats/details in sections
    - Footer with action buttons
    """

    # Style constants
    WIDTH = 500
    MIN_HEIGHT = 300
    MAX_HEIGHT = 650
    
    HEADER_HEIGHT = 50
    FOOTER_HEIGHT = 60
    PADDING = 15
    SPACING = 10
    
    BG_COLOR = (30, 30, 40)
    HEADER_COLOR = (40, 40, 55)
    FOOTER_COLOR = (35, 35, 50)
    BORDER_COLOR = (100, 100, 120)
    TEXT_COLOR = (220, 220, 230)
    ACCENT_COLOR = (0, 180, 255)
    
    HEADER_FONT_SIZE = 18
    SECTION_FONT_SIZE = 14
    BODY_FONT_SIZE = 12

    def __init__(self, entity_id: str, entity_name: str):
        """Initialize entity modal.
        
        Args:
            entity_id: Unique ID of the entity
            entity_name: Display name of the entity
        """
        self.logger = GameLogger("entity_modal")
        self.entity_id = entity_id
        self.entity_name = entity_name
        
        # Position (centered, will be updated in set_position)
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.MIN_HEIGHT)
        
        # Fonts
        self.header_font = pygame.font.SysFont('Arial', self.HEADER_FONT_SIZE, bold=True)
        self.section_font = pygame.font.SysFont('Arial', self.SECTION_FONT_SIZE, bold=True)
        self.body_font = pygame.font.SysFont('Arial', self.BODY_FONT_SIZE)
        
        # Action buttons (subclass populates)
        self.action_buttons: List[ActionButton] = []
        
        # Interaction state
        self.close_button_rect: Optional[pygame.Rect] = None
        self.button_rects: dict[str, pygame.Rect] = {}
        
        self.logger.info(f"[ENTITY_MODAL] Initialized: {entity_name} ({entity_id})")
    
    def set_position(self, screen_width: int, screen_height: int) -> None:
        """Center modal on screen.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.rect.centerx = screen_width // 2
        self.rect.centery = screen_height // 2
        self.logger.debug(f"[ENTITY_MODAL] Position set: ({self.rect.x}, {self.rect.y})")
    
    @abstractmethod
    def get_body_sections(self) -> List[dict[str, Any]]:
        """Get body sections for this entity.
        
        Should return list of dicts with structure:
        {
            "title": "Section Title",
            "items": [
                {"label": "Stat Name", "value": "123"},
                {"label": "Status", "value": "Active"},
            ]
        }
        
        Returns:
            List of section dicts
        """
        pass
    
    @abstractmethod
    def get_action_buttons(self) -> List[ActionButton]:
        """Get action buttons available for this entity.
        
        Returns:
            List of ActionButton objects
        """
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False if should close modal
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check close button
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                return False  # Signal to close modal
            
            # Check action buttons
            for button in self.action_buttons:
                if button.id in self.button_rects:
                    rect = self.button_rects[button.id]
                    if rect.collidepoint(event.pos) and button.enabled:
                        if button.on_click:
                            button.on_click()
                        return True  # Keep modal open
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover states for buttons
            pass
        
        return True  # Keep modal open for other events
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the modal.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect, border_radius=8)
        
        # Draw border
        pygame.draw.rect(screen, self.BORDER_COLOR, self.rect, width=2, border_radius=8)
        
        # Draw header
        self._draw_header(screen)
        
        # Draw body
        self._draw_body(screen)
        
        # Draw footer
        self._draw_footer(screen)
    
    def _draw_header(self, screen: pygame.Surface) -> None:
        """Draw modal header with title and close button.
        
        Args:
            screen: Pygame surface to draw on
        """
        header_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.HEADER_HEIGHT
        )
        
        # Background
        pygame.draw.rect(screen, self.HEADER_COLOR, header_rect, border_radius=8)
        
        # Title
        title_surface = self.header_font.render(self.entity_name, True, self.ACCENT_COLOR)
        title_x = self.rect.x + self.PADDING
        title_y = self.rect.y + (self.HEADER_HEIGHT - title_surface.get_height()) // 2
        screen.blit(title_surface, (title_x, title_y))
        
        # Close button (X in top-right)
        close_size = 24
        close_x = self.rect.x + self.rect.width - close_size - 10
        close_y = self.rect.y + (self.HEADER_HEIGHT - close_size) // 2
        self.close_button_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        
        # Draw close button
        pygame.draw.rect(screen, (100, 50, 50), self.close_button_rect, border_radius=2)
        close_text = pygame.font.SysFont('Arial', 16, bold=True).render("✕", True, (200, 100, 100))
        close_text_x = close_x + (close_size - close_text.get_width()) // 2
        close_text_y = close_y + (close_size - close_text.get_height()) // 2
        screen.blit(close_text, (close_text_x, close_text_y))
    
    def _draw_body(self, screen: pygame.Surface) -> None:
        """Draw modal body with entity details.
        
        Args:
            screen: Pygame surface to draw on
        """
        body_y = self.rect.y + self.HEADER_HEIGHT + self.PADDING
        body_x = self.rect.x + self.PADDING
        body_width = self.rect.width - (self.PADDING * 2)
        
        # Get sections from subclass
        sections = self.get_body_sections()
        
        # Draw each section
        for section in sections:
            # Section title
            title_surface = self.section_font.render(section["title"], True, self.ACCENT_COLOR)
            screen.blit(title_surface, (body_x, body_y))
            body_y += title_surface.get_height() + 5
            
            # Section items
            for item in section.get("items", []):
                label = item.get("label", "")
                value = item.get("value", "")
                
                # Format: "Label: Value"
                text = f"{label}: {value}"
                item_surface = self.body_font.render(text, True, self.TEXT_COLOR)
                screen.blit(item_surface, (body_x + 15, body_y))
                body_y += item_surface.get_height() + 3
            
            body_y += self.SPACING  # Space between sections
            
            # Stop if we've used too much space
            if body_y > self.rect.y + self.rect.height - self.FOOTER_HEIGHT - self.PADDING:
                break
    
    def _draw_footer(self, screen: pygame.Surface) -> None:
        """Draw modal footer with action buttons.
        
        Args:
            screen: Pygame surface to draw on
        """
        footer_y = self.rect.y + self.rect.height - self.FOOTER_HEIGHT
        footer_rect = pygame.Rect(
            self.rect.x,
            footer_y,
            self.rect.width,
            self.FOOTER_HEIGHT
        )
        
        # Background
        pygame.draw.rect(screen, self.FOOTER_COLOR, footer_rect, border_radius=8)
        
        # Draw buttons (refresh button list)
        self.action_buttons = self.get_action_buttons()
        self.button_rects.clear()
        
        button_width = 100
        button_height = 30
        buttons_width = len(self.action_buttons) * (button_width + 10) - 10
        start_x = self.rect.x + (self.rect.width - buttons_width) // 2
        
        for i, button in enumerate(self.action_buttons):
            button_x = start_x + i * (button_width + 10)
            button_y = footer_y + (self.FOOTER_HEIGHT - button_height) // 2
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            self.button_rects[button.id] = button_rect
            
            # Draw button background (darker if disabled)
            bg_color = button.color if button.enabled else (80, 80, 100)
            pygame.draw.rect(screen, bg_color, button_rect, border_radius=4)
            
            # Draw button text
            text_color = (255, 255, 255) if button.enabled else (150, 150, 150)
            text_surface = self.body_font.render(button.label, True, text_color)
            text_x = button_x + (button_width - text_surface.get_width()) // 2
            text_y = button_y + (button_height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
