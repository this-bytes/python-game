"""Detail Panel Renderer - Displays expanded UIProvider data in modals.

This module renders detail panel data from UIProvider.get_detail_panel_data()
in a modal using ModalManager. Supports action buttons that emit events.
"""

import pygame
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from src.utils.logger import GameLogger
from src.ui.ui_provider import UISectionItem, UIPanelSection, UIAction
from src.core.event_bus import get_event_bus


@dataclass
class DetailPanelConfig:
    """Configuration for detail panel rendering."""
    width: int = 700
    height: int = 500
    padding: int = 20
    section_spacing: int = 20
    item_spacing: int = 10
    bg_color: tuple = (25, 25, 35)
    text_color: tuple = (220, 220, 230)
    title_color: tuple = (255, 255, 255)
    section_title_color: tuple = (200, 200, 255)
    border_color: tuple = (80, 80, 100)
    button_bg_color: tuple = (60, 120, 180)
    button_hover_color: tuple = (80, 140, 200)
    button_disabled_color: tuple = (60, 60, 70)


class DetailPanelRenderer:
    """Renders detail panel data in a modal overlay.
    
    Takes structured detail panel data from UIProvider and renders it
    as a scrollable modal with sections, items, and action buttons.
    
    Action buttons emit events on the EventBus when clicked.
    """
    
    def __init__(self, config: Optional[DetailPanelConfig] = None):
        """Initialize detail panel renderer.
        
        Args:
            config: Optional configuration override
        """
        self.config = config or DetailPanelConfig()
        self.logger = GameLogger("detail_panel")
        self.event_bus = get_event_bus()
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_section = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_text = pygame.font.SysFont('Arial', 14)
        self.font_small = pygame.font.SysFont('Arial', 12)
        
        # State
        self.scroll_offset = 0
        self.max_scroll = 0
        self.action_buttons: List[ActionButton] = []
        self.hovered_button: Optional[ActionButton] = None
        
        self.logger.debug("[DETAIL_PANEL] Renderer initialized")
    
    def render(
        self,
        surface: pygame.Surface,
        detail_data: Dict[str, Any],
        x: int,
        y: int,
        on_close: Optional[Callable] = None
    ) -> None:
        """Render detail panel on surface.
        
        Args:
            surface: Surface to render on
            detail_data: Detail panel data from UIProvider
            x: X position
            y: Y position
            on_close: Callback when panel should close
        """
        config = self.config
        
        # Create panel surface
        panel_surface = pygame.Surface((config.width, config.height))
        panel_surface.fill(config.bg_color)
        
        # Draw border
        pygame.draw.rect(
            panel_surface,
            config.border_color,
            panel_surface.get_rect(),
            width=2,
            border_radius=8
        )
        
        # Render title
        title = detail_data.get("title", "Details")
        title_surface = self.font_title.render(title, True, config.title_color)
        panel_surface.blit(title_surface, (config.padding, config.padding))
        
        # Calculate content area
        content_y = config.padding + 30
        content_height = config.height - content_y - config.padding - 60  # Leave space for buttons
        
        # Render sections
        current_y = content_y - self.scroll_offset
        sections = detail_data.get("sections", [])
        
        for section in sections:
            if isinstance(section, UIPanelSection):
                current_y = self._render_section(panel_surface, section, current_y, content_height)
            elif isinstance(section, dict):
                # Handle dict format
                section_obj = UIPanelSection(
                    title=section.get("title", ""),
                    items=[UISectionItem(**item) if isinstance(item, dict) else item 
                           for item in section.get("items", [])],
                    section_type=section.get("section_type", "list")
                )
                current_y = self._render_section(panel_surface, section_obj, current_y, content_height)
        
        # Update max scroll
        self.max_scroll = max(0, current_y - content_height - content_y + config.padding)
        
        # Render action buttons
        actions = detail_data.get("actions", [])
        if actions:
            self._render_action_buttons(panel_surface, actions)
        
        # Render close button
        self._render_close_button(panel_surface, on_close)
        
        # Blit to screen
        surface.blit(panel_surface, (x, y))
    
    def _render_section(
        self,
        surface: pygame.Surface,
        section: UIPanelSection,
        y: int,
        max_height: int
    ) -> int:
        """Render a section with items.
        
        Args:
            surface: Surface to render on
            section: Section to render
            y: Current Y position
            max_height: Maximum content height
            
        Returns:
            Updated Y position
        """
        config = self.config
        
        # Section title
        if y > 0 and y < surface.get_height():
            title_surface = self.font_section.render(
                section.title,
                True,
                config.section_title_color
            )
            surface.blit(title_surface, (config.padding, y))
        
        y += 25
        
        # Section items
        for item in section.items:
            if y > max_height + config.padding:
                break
            if y + 20 < 0:
                y += 20 + len(item.details) * 16
                continue
            
            # Item name
            name_surface = self.font_text.render(
                f"• {item.name}",
                True,
                config.text_color
            )
            surface.blit(name_surface, (config.padding + 10, y))
            y += 20
            
            # Item details
            for detail in item.details:
                if y > max_height + config.padding:
                    break
                if y + 16 >= 0:
                    detail_surface = self.font_small.render(
                        f"  {detail}",
                        True,
                        (180, 180, 190)
                    )
                    surface.blit(detail_surface, (config.padding + 20, y))
                y += 16
            
            y += config.item_spacing
        
        y += config.section_spacing
        return y
    
    def _render_action_buttons(
        self,
        surface: pygame.Surface,
        actions: List[Any]
    ) -> None:
        """Render action buttons at bottom of panel.
        
        Args:
            surface: Surface to render on
            actions: List of UIAction objects or dicts
        """
        config = self.config
        
        # Clear old buttons
        self.action_buttons.clear()
        
        # Calculate button positions
        button_y = surface.get_height() - 50
        button_x = config.padding
        button_width = 150
        button_height = 35
        button_spacing = 10
        
        for action in actions:
            # Convert dict to UIAction if needed
            if isinstance(action, dict):
                action = UIAction(
                    id=action.get("id", ""),
                    label=action.get("label", ""),
                    description=action.get("description", ""),
                    cost=action.get("cost", ""),
                    enabled=action.get("enabled", True),
                    requires_selection=action.get("requires_selection", False)
                )
            
            # Create button
            button = ActionButton(
                rect=pygame.Rect(button_x, button_y, button_width, button_height),
                action=action,
                hovered=False
            )
            self.action_buttons.append(button)
            
            # Render button
            self._render_button(surface, button)
            
            button_x += button_width + button_spacing
    
    def _render_button(self, surface: pygame.Surface, button: 'ActionButton') -> None:
        """Render an action button.
        
        Args:
            surface: Surface to render on
            button: Button to render
        """
        config = self.config
        action = button.action
        
        # Determine color
        if not action.enabled:
            bg_color = config.button_disabled_color
        elif button.hovered:
            bg_color = config.button_hover_color
        else:
            bg_color = config.button_bg_color
        
        # Draw button background
        pygame.draw.rect(
            surface,
            bg_color,
            button.rect,
            border_radius=6
        )
        pygame.draw.rect(
            surface,
            config.border_color,
            button.rect,
            width=1,
            border_radius=6
        )
        
        # Draw button text
        text_surface = self.font_text.render(
            action.label,
            True,
            config.text_color if action.enabled else (120, 120, 130)
        )
        text_rect = text_surface.get_rect(center=button.rect.center)
        surface.blit(text_surface, text_rect)
    
    def _render_close_button(
        self,
        surface: pygame.Surface,
        on_close: Optional[Callable]
    ) -> None:
        """Render close button in top-right corner.
        
        Args:
            surface: Surface to render on
            on_close: Close callback
        """
        config = self.config
        
        # Close button (X in top-right)
        close_x = surface.get_width() - 40
        close_y = 10
        close_size = 30
        
        pygame.draw.circle(
            surface,
            (180, 60, 60),
            (close_x + close_size // 2, close_y + close_size // 2),
            close_size // 2
        )
        
        # X mark
        x_font = pygame.font.SysFont('Arial', 18, bold=True)
        x_surface = x_font.render("✕", True, (255, 255, 255))
        x_rect = x_surface.get_rect(
            center=(close_x + close_size // 2, close_y + close_size // 2)
        )
        surface.blit(x_surface, x_rect)
    
    def handle_click(self, mouse_pos: tuple, panel_rect: pygame.Rect) -> bool:
        """Handle mouse click on detail panel.
        
        Args:
            mouse_pos: Mouse position
            panel_rect: Panel rectangle on screen
            
        Returns:
            True if click was handled
        """
        # Adjust mouse position relative to panel
        rel_x = mouse_pos[0] - panel_rect.x
        rel_y = mouse_pos[1] - panel_rect.y
        
        # Check action buttons
        for button in self.action_buttons:
            if button.rect.collidepoint((rel_x, rel_y)) and button.action.enabled:
                self._handle_action_click(button.action)
                return True
        
        # Check close button
        close_x = panel_rect.width - 40
        close_y = 10
        close_size = 30
        close_rect = pygame.Rect(close_x, close_y, close_size, close_size)
        
        if close_rect.collidepoint((rel_x, rel_y)):
            return True  # Close handled by caller
        
        return False
    
    def _handle_action_click(self, action: UIAction) -> None:
        """Handle action button click by emitting event.
        
        Args:
            action: Action that was clicked
        """
        event_type = f"action:{action.id}"
        event_data = action.data or {}
        # Ensure the action itself is part of the payload for context
        event_data['action'] = action

        self.logger.debug(f"[DETAIL_PANEL] Action clicked: {action.id}")
        
        # Publish event
        self.event_bus.publish(
            event_type,
            event_data,
            source="detail_panel"
        )
    
    def update_hover(self, mouse_pos: tuple, panel_rect: pygame.Rect) -> None:
        """Update button hover states.
        
        Args:
            mouse_pos: Mouse position
            panel_rect: Panel rectangle on screen
        """
        rel_x = mouse_pos[0] - panel_rect.x
        rel_y = mouse_pos[1] - panel_rect.y
        
        for button in self.action_buttons:
            button.hovered = button.rect.collidepoint((rel_x, rel_y))


@dataclass
class ActionButton:
    """Represents a rendered action button."""
    rect: pygame.Rect
    action: UIAction
    hovered: bool = False
