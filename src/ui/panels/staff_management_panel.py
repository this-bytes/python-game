"""Staff Management Actions Panel - Quick actions for managing team.

This panel provides quick-access management actions:
- Hire new specialists
- Fire or reassign specialists
- Manage rest/recovery
- View specialist details
- Bulk actions for workload management
"""

import pygame
from typing import List, Optional, Callable
from src.models.specialist import Specialist
from src.utils.logger import GameLogger


class Action:
    """Represents a management action."""
    def __init__(self, name: str, description: str, icon: str, enabled: bool = True):
        self.name = name
        self.description = description
        self.icon = icon
        self.enabled = enabled
        self.rect: Optional[pygame.Rect] = None
        self.hovered = False


class StaffManagementPanel:
    """Panel for quick staff management actions."""
    
    # Layout constants
    ACTION_WIDTH = 160
    ACTION_HEIGHT = 50
    ACTIONS_PER_ROW = 2
    PADDING = 10
    
    # Colors
    BG_COLOR = (20, 25, 35)
    ACTION_BG = (35, 45, 60)
    ACTION_HOVER = (50, 70, 100)
    ACTION_DISABLED = (30, 30, 35)
    BORDER_COLOR = (60, 70, 90)
    TEXT_COLOR = (220, 220, 230)
    LABEL_COLOR = (140, 150, 170)
    DISABLED_TEXT = (80, 80, 90)
    
    # Action categories
    HIRING = "👤 Hire"
    MANAGEMENT = "⚙️ Manage"
    RECOVERY = "💤 Recovery"
    INFO = "ℹ️ Info"
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize staff management panel.
        
        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.logger = GameLogger("staff_management")
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_action = pygame.font.SysFont('Arial', 11, bold=True)
        self.font_label = pygame.font.SysFont('Arial', 9)
        
        self.actions: List[Action] = self._create_default_actions()
        self.on_action_selected: Optional[Callable[[str], None]] = None
        self.selected_action: Optional[str] = None
    
    def set_action_callback(self, callback: Callable[[str], None]):
        """Set callback for when an action is selected."""
        self.on_action_selected = callback
    
    def _create_default_actions(self) -> List[Action]:
        """Create default management actions."""
        return [
            Action("hire_entry", "Hire Entry Level", "👤", enabled=True),
            Action("hire_mid", "Hire Mid-Level", "👥", enabled=True),
            Action("rest_all", "Rest All Available", "🛌", enabled=True),
            Action("promote", "Promote Specialist", "⬆️", enabled=True),
            Action("fire", "Fire Specialist", "🚪", enabled=True),
            Action("details", "View Details", "📊", enabled=True),
        ]
    
    def update_action_state(self, specialists: List[Specialist], budget: float):
        """Update availability of actions based on game state.
        
        Args:
            specialists: List of specialists
            budget: Current budget
        """
        # Enable/disable hiring based on budget
        hire_entry = next((a for a in self.actions if a.name == "hire_entry"), None)
        if hire_entry:
            hire_entry.enabled = budget >= 2000  # Assumed hiring cost
        
        hire_mid = next((a for a in self.actions if a.name == "hire_mid"), None)
        if hire_mid:
            hire_mid.enabled = budget >= 4000
        
        # Enable rest if there are overworked specialists
        rest_all = next((a for a in self.actions if a.name == "rest_all"), None)
        if rest_all:
            has_overworked = any(s.burnout_level > 70 for s in specialists)
            rest_all.enabled = has_overworked
        
        # Enable promote if there are levelable specialists
        promote = next((a for a in self.actions if a.name == "promote"), None)
        if promote:
            has_promotable = any(s.level < 10 for s in specialists)
            promote.enabled = has_promotable
        
        # Enable fire if there are specialists
        fire_action = next((a for a in self.actions if a.name == "fire"), None)
        if fire_action:
            fire_action.enabled = len(specialists) > 1
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events.
        
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEMOTION:
            for action in self.actions:
                if action.rect and action.rect.collidepoint(event.pos):
                    action.hovered = True
                else:
                    action.hovered = False
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action in self.actions:
                if action.rect and action.rect.collidepoint(event.pos) and action.enabled:
                    self.selected_action = action.name
                    if self.on_action_selected:
                        self.on_action_selected(action.name)
                    self.logger.info(f"Staff action selected: {action.name}")
                    return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Render the staff management panel.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, (60, 70, 90), self.rect, width=1)
        
        # Title
        title_text = self.font_title.render("Team Management", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        # Draw actions in grid
        y_offset = self.rect.y + 35
        
        for idx, action in enumerate(self.actions):
            row = idx // self.ACTIONS_PER_ROW
            col = idx % self.ACTIONS_PER_ROW
            
            action_x = self.rect.x + self.PADDING + col * (self.ACTION_WIDTH + self.PADDING)
            action_y = y_offset + row * (self.ACTION_HEIGHT + self.PADDING)
            
            action.rect = pygame.Rect(action_x, action_y, self.ACTION_WIDTH, self.ACTION_HEIGHT)
            
            self._draw_action_button(screen, action)
    
    def _draw_action_button(self, screen: pygame.Surface, action: Action):
        """Draw a single action button.
        
        Args:
            screen: Pygame surface
            action: Action to draw
        """
        if not action.rect:
            return
        
        # Determine colors
        if not action.enabled:
            bg_color = self.ACTION_DISABLED
            text_color = self.DISABLED_TEXT
            border_color = (40, 40, 45)
            border_width = 1
        elif action.hovered:
            bg_color = self.ACTION_HOVER
            text_color = self.TEXT_COLOR
            border_color = (100, 150, 200)
            border_width = 2
        else:
            bg_color = self.ACTION_BG
            text_color = self.TEXT_COLOR
            border_color = self.BORDER_COLOR
            border_width = 1
        
        # Draw background
        pygame.draw.rect(screen, bg_color, action.rect)
        pygame.draw.rect(screen, border_color, action.rect, width=border_width)
        
        # Draw icon and name
        icon_text = self.font_action.render(action.icon, True, text_color)
        name_text = self.font_action.render(action.name.replace("_", " ").title(), True, text_color)
        
        # Center content
        icon_rect = icon_text.get_rect(
            center=(action.rect.centerx, action.rect.y + 15)
        )
        name_rect = name_text.get_rect(
            center=(action.rect.centerx, action.rect.y + 30)
        )
        
        screen.blit(icon_text, icon_rect)
        screen.blit(name_text, name_rect)
