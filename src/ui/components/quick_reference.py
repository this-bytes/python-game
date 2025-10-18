"""
Quick Reference Card component.

Shows a compact keyboard shortcuts reference in the corner of the screen.
Can be toggled on/off and positioned in different corners.
"""

from typing import List, Tuple
import pygame


class QuickReference:
    """Quick reference card for keyboard shortcuts.
    
    Features:
    - Compact display in corner
    - Toggle visibility
    - Semi-transparent background
    - Grouped shortcuts
    - Auto-hide after delay
    
    Example:
        quick_ref = QuickReference()
        
        # In render loop
        if quick_ref.visible:
            quick_ref.render(screen)
    """
    
    def __init__(
        self,
        position: str = "bottom-right",
        auto_hide_delay: float = 10.0
    ):
        """Initialize quick reference.
        
        Args:
            position: Corner position ("top-left", "top-right", "bottom-left", "bottom-right")
            auto_hide_delay: Seconds before auto-hiding (0 = no auto-hide)
        """
        self.position = position
        self.auto_hide_delay = auto_hide_delay
        self.visible = True
        self.time_visible = 0.0
        
        # Styling
        self.bg_color = (20, 20, 30)
        self.bg_alpha = 220
        self.border_color = (0, 120, 200)
        self.text_color = (220, 220, 230)
        self.key_color = (100, 200, 255)
        self.section_color = (0, 180, 255)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 13, bold=True)
        self.key_font = pygame.font.SysFont('Arial', 11, bold=True)
        self.desc_font = pygame.font.SysFont('Arial', 11)
        
        # Shortcuts grouped by category
        self.shortcuts = [
            ("Navigation", [
                ("F1", "Overview"),
                ("F2", "Operations"),
                ("F3", "Management"),
                ("F4", "Analytics"),
                ("ESC", "Go Back"),
            ]),
            ("Actions", [
                ("A", "Assign"),
                ("S", "Synergy"),
                ("H", "Help"),
                ("SPACE", "Pause"),
            ]),
        ]
    
    def toggle(self) -> None:
        """Toggle visibility."""
        self.visible = not self.visible
        self.time_visible = 0.0
    
    def show(self) -> None:
        """Show the reference card."""
        self.visible = True
        self.time_visible = 0.0
    
    def hide(self) -> None:
        """Hide the reference card."""
        self.visible = False
    
    def update(self, delta_time: float) -> None:
        """Update reference card state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if not self.visible:
            return
        
        # Auto-hide after delay
        if self.auto_hide_delay > 0:
            self.time_visible += delta_time
            if self.time_visible >= self.auto_hide_delay:
                self.visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the quick reference card.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Calculate dimensions
        padding = 15
        line_height = 18
        section_spacing = 10
        
        # Calculate total height
        total_height = padding * 2
        for section_title, shortcuts in self.shortcuts:
            total_height += 20  # Section title
            total_height += len(shortcuts) * line_height
            total_height += section_spacing
        
        # Calculate width (based on longest line)
        max_width = 200
        card_width = max_width + padding * 2
        card_height = total_height
        
        # Position based on corner
        if self.position == "bottom-right":
            card_x = screen_width - card_width - 15
            card_y = screen_height - card_height - 15
        elif self.position == "bottom-left":
            card_x = 15
            card_y = screen_height - card_height - 15
        elif self.position == "top-right":
            card_x = screen_width - card_width - 15
            card_y = 75
        else:  # top-left
            card_x = 15
            card_y = 75
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        
        # Background
        bg_surface = pygame.Surface((card_width, card_height))
        bg_surface.set_alpha(self.bg_alpha)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (card_x, card_y))
        
        # Border
        pygame.draw.rect(screen, self.border_color, card_rect, 2, border_radius=8)
        
        # Title
        title_text = self.title_font.render("Quick Reference", True, self.section_color)
        screen.blit(title_text, (card_x + padding, card_y + padding))
        
        # Render shortcuts by section
        y_offset = card_y + padding + 25
        
        for section_title, shortcuts in self.shortcuts:
            # Section title
            section_surface = self.title_font.render(section_title, True, self.section_color)
            screen.blit(section_surface, (card_x + padding, y_offset))
            y_offset += 20
            
            # Shortcuts in section
            for key, description in shortcuts:
                # Key
                key_surface = self.key_font.render(key, True, self.key_color)
                screen.blit(key_surface, (card_x + padding + 5, y_offset))
                
                # Description
                desc_surface = self.desc_font.render(description, True, self.text_color)
                screen.blit(desc_surface, (card_x + padding + 60, y_offset))
                
                y_offset += line_height
            
            y_offset += section_spacing
        
        # Add subtle hint at bottom
        if self.auto_hide_delay > 0:
            time_left = max(0, self.auto_hide_delay - self.time_visible)
            hint_text = f"Press H to toggle | Auto-hide in {time_left:.0f}s"
            hint_surface = self.desc_font.render(hint_text, True, (120, 120, 140))
            hint_rect = hint_surface.get_rect(centerx=card_rect.centerx, bottom=card_rect.bottom - 8)
            screen.blit(hint_surface, hint_rect)
