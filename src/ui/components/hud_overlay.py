"""
HUD Overlay component for displaying critical game information.

Provides a clean, minimalist heads-up display showing only essential
real-time information without cluttering the screen.
"""

from typing import Optional, Tuple
import pygame
from src.models.game_state import GameState


class HUDOverlay:
    """Clean HUD overlay for critical game information.
    
    Features:
    - Minimalist design
    - Semi-transparent background
    - Essential metrics only (money, time)
    - Auto-play status indicator
    - Pause indicator
    - Smooth value transitions
    
    Example:
        hud = HUDOverlay(screen_width=1280, screen_height=720)
        
        # In render loop
        hud.render(screen, game_state)
    """
    
    def __init__(
        self,
        screen_width: int = 1280,
        screen_height: int = 720,
        position: str = "top"
    ):
        """Initialize HUD overlay.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
            position: HUD position ("top", "bottom", "corners")
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.position = position
        
        # Styling
        self.bg_color = (0, 120, 200)
        self.bg_alpha = 230
        self.text_color = (255, 255, 255)
        self.text_secondary_color = (220, 220, 240)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.value_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 14)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Animation state
        self.money_display = 0.0
        self.money_target = 0.0
        self.animation_speed = 5000  # dollars per second
    
    def update(self, delta_time: float, game_state: GameState) -> None:
        """Update HUD state.
        
        Args:
            delta_time: Time elapsed since last update
            game_state: Current game state
        """
        # Smooth money animation
        self.money_target = game_state.current_money
        
        if abs(self.money_display - self.money_target) > 1:
            diff = self.money_target - self.money_display
            change = self.animation_speed * delta_time
            
            if abs(diff) < change:
                self.money_display = self.money_target
            else:
                self.money_display += change if diff > 0 else -change
        else:
            self.money_display = self.money_target
    
    def render(self, screen: pygame.Surface, game_state: GameState, current_view_title: str = "") -> None:
        """Render the HUD overlay.
        
        Args:
            screen: Pygame surface to render on
            game_state: Current game state
            current_view_title: Title of current view to display
        """
        if self.position == "top":
            self._render_top_hud(screen, game_state, current_view_title)
        elif self.position == "corners":
            self._render_corner_hud(screen, game_state)
    
    def _render_top_hud(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        current_view_title: str
    ) -> None:
        """Render top HUD bar.
        
        Args:
            screen: Pygame surface
            game_state: Current game state
            current_view_title: Current view title
        """
        bar_height = 60
        bar_rect = pygame.Rect(0, 0, self.screen_width, bar_height)
        
        # Background
        bar_surface = pygame.Surface((self.screen_width, bar_height))
        bar_surface.set_alpha(self.bg_alpha)
        bar_surface.fill(self.bg_color)
        screen.blit(bar_surface, (0, 0))
        
        # Subtle bottom border
        border_color = (0, 140, 220)
        pygame.draw.line(screen, border_color, (0, bar_height - 1), (self.screen_width, bar_height - 1), 2)
        
        # Game title + current view
        title_parts = ["Cybersecurity Firm"]
        if current_view_title:
            title_parts.append(f"› {current_view_title}")
        
        title_text = " ".join(title_parts)
        title_surface = self.title_font.render(title_text, True, self.text_color)
        screen.blit(title_surface, (20, 18))
        
        # Right side metrics
        right_x = self.screen_width - 20
        
        # Money
        money_text = f"${self.money_display:,.0f}"
        money_surface = self.value_font.render(money_text, True, (100, 255, 150))
        money_rect = money_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(money_surface, money_rect)
        
        # Money label
        money_label = self.small_font.render("Budget", True, self.text_secondary_color)
        money_label_rect = money_label.get_rect(right=right_x, bottom=money_rect.top - 2)
        screen.blit(money_label, money_label_rect)
        
        right_x = money_rect.left - 40
        
        # Game time
        time_text = f"{game_state.get_game_time_elapsed():.0f}s"
        time_surface = self.value_font.render(time_text, True, (150, 200, 255))
        time_rect = time_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(time_surface, time_rect)
        
        # Time label
        time_label = self.small_font.render("Time", True, self.text_secondary_color)
        time_label_rect = time_label.get_rect(right=right_x, bottom=time_rect.top - 2)
        screen.blit(time_label, time_label_rect)
        
        # Pause indicator
        if game_state.is_paused:
            right_x = time_rect.left - 30
            pause_text = self.label_font.render("⏸ PAUSED", True, (255, 200, 100))
            pause_rect = pause_text.get_rect(right=right_x, centery=bar_height // 2)
            screen.blit(pause_text, pause_rect)
    
    def _render_corner_hud(self, screen: pygame.Surface, game_state: GameState) -> None:
        """Render HUD in screen corners.
        
        Args:
            screen: Pygame surface
            game_state: Current game state
        """
        padding = 15
        
        # Top-right: Money
        money_text = f"${self.money_display:,.0f}"
        money_surface = self.value_font.render(money_text, True, (100, 255, 150))
        
        # Semi-transparent background
        bg_width = money_surface.get_width() + 30
        bg_height = money_surface.get_height() + 20
        bg_rect = pygame.Rect(
            self.screen_width - bg_width - padding,
            padding,
            bg_width,
            bg_height
        )
        
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(200)
        bg_surface.fill((20, 20, 30))
        screen.blit(bg_surface, bg_rect.topleft)
        
        pygame.draw.rect(screen, (0, 180, 255), bg_rect, 2, border_radius=6)
        
        money_rect = money_surface.get_rect(center=bg_rect.center)
        screen.blit(money_surface, money_rect)
        
        # Top-left: Time
        time_text = f"⏱ {game_state.get_game_time_elapsed():.0f}s"
        time_surface = self.label_font.render(time_text, True, (200, 200, 220))
        
        time_bg_width = time_surface.get_width() + 20
        time_bg_height = time_surface.get_height() + 16
        time_bg_rect = pygame.Rect(padding, padding, time_bg_width, time_bg_height)
        
        time_bg_surface = pygame.Surface((time_bg_width, time_bg_height))
        time_bg_surface.set_alpha(180)
        time_bg_surface.fill((20, 20, 30))
        screen.blit(time_bg_surface, time_bg_rect.topleft)
        
        pygame.draw.rect(screen, (60, 60, 80), time_bg_rect, 1, border_radius=4)
        
        time_rect = time_surface.get_rect(center=time_bg_rect.center)
        screen.blit(time_surface, time_rect)
