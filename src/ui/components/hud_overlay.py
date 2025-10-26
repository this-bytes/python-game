import pygame
from src.models.game_state import GameState
from src.ui.components.base import UIComponent

class HUDOverlay(UIComponent):
    """Clean HUD overlay for critical game information."""
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720, position: str = "top"):
        super().__init__(pygame.Rect(0, 0, screen_width, 60))
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.position = position
        
        self.bg_color = (0, 120, 200)
        self.bg_alpha = 230
        self.text_color = (255, 255, 255)
        self.text_secondary_color = (220, 220, 240)
        
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.value_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 14)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        self.money_display = 0.0
        self.money_target = 0.0
        self.animation_speed = 5000
    
    def update(self, delta_time: float, game_state: GameState) -> None:
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
    
    def draw(self, screen: pygame.Surface, game_state: GameState, current_view_title: str = "Dashboard") -> None:
        bar_height = 60
        bar_rect = pygame.Rect(0, 0, self.screen_width, bar_height)
        
        bar_surface = pygame.Surface((self.screen_width, bar_height))
        bar_surface.set_alpha(self.bg_alpha)
        bar_surface.fill(self.bg_color)
        screen.blit(bar_surface, (0, 0))
        
        border_color = (0, 140, 220)
        pygame.draw.line(screen, border_color, (0, bar_height - 1), (self.screen_width, bar_height - 1), 2)
        
        title_parts = ["Cybersecurity Firm"]
        if current_view_title:
            title_parts.append(f"› {current_view_title}")
        
        title_text = " ".join(title_parts)
        title_surface = self.title_font.render(title_text, True, self.text_color)
        screen.blit(title_surface, (20, 18))
        
        right_x = self.screen_width - 20
        
        money_text = f"${self.money_display:,.0f}"
        money_surface = self.value_font.render(money_text, True, (100, 255, 150))
        money_rect = money_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(money_surface, money_rect)
        
        money_label = self.small_font.render("Budget", True, self.text_secondary_color)
        money_label_rect = money_label.get_rect(right=right_x, bottom=money_rect.top - 2)
        screen.blit(money_label, money_label_rect)
        
        right_x = money_rect.left - 40
        
        time_text = f"{game_state.get_game_time_elapsed():.0f}s"
        time_surface = self.value_font.render(time_text, True, (150, 200, 255))
        time_rect = time_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(time_surface, time_rect)
        
        time_label = self.small_font.render("Time", True, self.text_secondary_color)
        time_label_rect = time_label.get_rect(right=right_x, bottom=time_rect.top - 2)
        screen.blit(time_label, time_label_rect)
        
        # Show simple counts: clients and pending incidents
        try:
            clients_count = len(getattr(game_state, 'clients', []) or [])
            pending_count = len(getattr(game_state, 'get_pending_incidents', lambda: [])() or [])
        except Exception:
            clients_count = 0
            pending_count = 0

        right_x = time_rect.left - 40
        clients_text = f"Clients: {clients_count}"
        clients_surface = self.label_font.render(clients_text, True, self.text_secondary_color)
        clients_rect = clients_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(clients_surface, clients_rect)

        right_x = clients_rect.left - 20
        pending_text = f"Incidents: {pending_count}"
        pending_surface = self.label_font.render(pending_text, True, (255, 180, 120) if pending_count > 0 else self.text_secondary_color)
        pending_rect = pending_surface.get_rect(right=right_x, centery=bar_height // 2)
        screen.blit(pending_surface, pending_rect)
        
        if game_state.is_paused:
            right_x = time_rect.left - 30
            pause_text = self.label_font.render("⏸ PAUSED", True, (255, 200, 100))
            pause_rect = pause_text.get_rect(right=right_x, centery=bar_height // 2)
            screen.blit(pause_text, pause_rect)