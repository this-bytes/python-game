"""Synergy Suggestion Overlay - Strategic intervention hints for idle gameplay.

This overlay shows players WHEN to manually intervene for synergy bonuses,
creating the strategic depth of Balatro where you CAN auto-play but manual
intervention gives significant bonuses.
"""

import pygame
from typing import List, Dict
import time


class SynergySuggestionOverlay:
    """Overlay that suggests strategic manual assignments for synergy bonuses."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        # Suggestion panel
        self.panel_width = 350
        self.panel_height = 500
        self.panel_x = self.screen_width - self.panel_width - 20
        self.panel_y = 150
        
        # Visibility
        self.visible = True
        self.suggestions = []
        
        # Colors
        self.bg_color = (25, 25, 40, 230)
        self.border_color = (100, 200, 255)
        self.synergy_color = (255, 200, 50)
        self.high_priority_color = (255, 100, 100)
        self.medium_priority_color = (255, 200, 100)
    
    def update_suggestions(self, idle_core, game_state):
        """Update synergy suggestions from idle core.
        
        Args:
            idle_core: IdleCore system
            game_state: Current game state
        """
        if not idle_core or not game_state:
            self.suggestions = []
            return
        
        # Get suggestions from idle core
        raw_suggestions = idle_core.suggest_manual_intervention(game_state)
        
        # Sort by priority and limit to top 5
        self.suggestions = sorted(
            raw_suggestions,
            key=lambda x: (
                0 if x["priority"] == "high" else 1,
                -(x["bonuses"]["xp_mult"] + x["bonuses"]["reward_mult"])
            )
        )[:5]
    
    def toggle_visibility(self):
        """Toggle panel visibility."""
        self.visible = not self.visible
    
    def render(self, screen):
        """Render the synergy suggestion panel.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.visible or not self.suggestions:
            return
        
        # Background panel with transparency
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(230)
        panel_surface.fill((25, 25, 40))
        screen.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Border
        pygame.draw.rect(
            screen,
            self.border_color,
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
            3,
            border_radius=8
        )
        
        # Title
        title_text = self.title_font.render("⚡ SYNERGY OPPORTUNITIES", True, self.synergy_color)
        title_rect = title_text.get_rect(centerx=self.panel_x + self.panel_width // 2, y=self.panel_y + 10)
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = "Manual assignment for bonuses:"
        subtitle_text = self.small_font.render(subtitle, True, (180, 180, 200))
        subtitle_rect = subtitle_text.get_rect(centerx=self.panel_x + self.panel_width // 2, y=self.panel_y + 40)
        screen.blit(subtitle_text, subtitle_rect)
        
        # Render each suggestion
        y_offset = self.panel_y + 70
        
        for i, suggestion in enumerate(self.suggestions):
            incident = suggestion["incident"]
            specialist = suggestion["specialist"]
            synergy = suggestion["synergy"]
            bonuses = suggestion["bonuses"]
            priority = suggestion["priority"]
            
            # Suggestion box
            box_height = 85
            box_y = y_offset + (i * (box_height + 10))
            
            # Priority indicator color
            priority_color = self.high_priority_color if priority == "high" else self.medium_priority_color
            
            # Background
            box_rect = pygame.Rect(
                self.panel_x + 10,
                box_y,
                self.panel_width - 20,
                box_height
            )
            pygame.draw.rect(screen, (40, 40, 60), box_rect, border_radius=5)
            pygame.draw.rect(screen, priority_color, box_rect, 2, border_radius=5)
            
            # Priority badge
            priority_badge = "🔥 URGENT" if priority == "high" else "⚡ GOOD"
            badge_text = self.small_font.render(priority_badge, True, priority_color)
            screen.blit(badge_text, (box_rect.x + 5, box_rect.y + 5))
            
            # Incident type
            incident_text = self.text_font.render(
                f"Incident: {incident.incident_type[:20]}...",
                True,
                (220, 220, 230)
            )
            screen.blit(incident_text, (box_rect.x + 5, box_rect.y + 25))
            
            # Specialist name
            spec_text = self.small_font.render(
                f"→ {specialist.name}",
                True,
                (150, 220, 255)
            )
            screen.blit(spec_text, (box_rect.x + 5, box_rect.y + 45))
            
            # Synergy bonuses
            bonus_str = f"💎 {bonuses['xp_mult']}x XP | {bonuses['reward_mult']}x $"
            bonus_text = self.small_font.render(bonus_str, True, self.synergy_color)
            screen.blit(bonus_text, (box_rect.x + 5, box_rect.y + 65))
        
        # Stats footer
        footer_y = self.panel_y + self.panel_height - 25
        stats_text = f"Auto-play ON | {len(self.suggestions)} synergies available"
        footer = self.small_font.render(stats_text, True, (150, 150, 160))
        footer_rect = footer.get_rect(centerx=self.panel_x + self.panel_width // 2, y=footer_y)
        screen.blit(footer, footer_rect)
    
    def render_compact_indicator(self, screen, num_suggestions: int):
        """Render a compact indicator when panel is hidden but suggestions exist.
        
        Args:
            screen: Pygame surface
            num_suggestions: Number of available suggestions
        """
        if self.visible or num_suggestions == 0:
            return
        
        # Small indicator in top-right
        indicator_x = self.screen_width - 200
        indicator_y = 80
        
        # Background
        indicator_rect = pygame.Rect(indicator_x, indicator_y, 180, 40)
        pygame.draw.rect(screen, (40, 40, 60, 200), indicator_rect, border_radius=5)
        pygame.draw.rect(screen, self.synergy_color, indicator_rect, 2, border_radius=5)
        
        # Text
        text = f"⚡ {num_suggestions} Synergies"
        text_surface = self.text_font.render(text, True, self.synergy_color)
        text_rect = text_surface.get_rect(center=indicator_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Hint
        hint = "(Press S to view)"
        hint_surface = self.small_font.render(hint, True, (150, 150, 160))
        hint_rect = hint_surface.get_rect(centerx=indicator_rect.centerx, y=indicator_rect.bottom - 15)
        screen.blit(hint_surface, hint_rect)


class AutoPlayIndicator:
    """Simple indicator showing auto-play is active."""
    
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def render(self, screen, idle_core, screen_width):
        """Render auto-play status indicator.
        
        Args:
            screen: Pygame surface
            idle_core: IdleCore system
            screen_width: Screen width
        """
        if not idle_core:
            return
        
        # Position in top-right
        x = screen_width - 250
        y = 20
        
        # Status
        if idle_core.config.enabled:
            status_text = "✓ AUTO-PLAY ACTIVE"
            status_color = (100, 255, 100)
            bg_color = (20, 60, 20, 200)
        else:
            status_text = "✗ AUTO-PLAY OFF"
            status_color = (255, 100, 100)
            bg_color = (60, 20, 20, 200)
        
        # Background
        bg_rect = pygame.Rect(x, y, 230, 50)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(200)
        bg_surface.fill((bg_color[0], bg_color[1], bg_color[2]))
        screen.blit(bg_surface, bg_rect)
        
        # Border
        pygame.draw.rect(screen, status_color, bg_rect, 2, border_radius=5)
        
        # Status text
        text_surface = self.font.render(status_text, True, status_color)
        text_rect = text_surface.get_rect(centerx=x + 115, y=y + 5)
        screen.blit(text_surface, text_rect)
        
        # Stats
        stats_text = f"Threshold: Difficulty ≤{idle_core.config.difficulty_threshold}"
        stats_surface = self.small_font.render(stats_text, True, (200, 200, 210))
        stats_rect = stats_surface.get_rect(centerx=x + 115, y=y + 28)
        screen.blit(stats_surface, stats_rect)
        
        # Hint
        hint = "(Press A to toggle)"
        hint_surface = self.small_font.render(hint, True, (150, 150, 160))
        hint_rect = hint_surface.get_rect(centerx=x + 115, y=y + 45)
        screen.blit(hint_surface, hint_rect)
