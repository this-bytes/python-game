"""Game Overlay - HUD displaying game state and metrics.

Provides a persistent UI overlay showing:
- Resources (money, energy)
- Progression (XP, level)
- Game speed control
- Active incidents and specialists
- Notification system for events
- Warning indicators
"""

import pygame
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from src.utils.animation_system import get_animation_system, EasingFunction


class NotificationLevel(Enum):
    """Notification importance level."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACHIEVEMENT = "achievement"


@dataclass
class Notification:
    """A notification to display in the overlay."""
    message: str
    level: NotificationLevel = NotificationLevel.INFO
    duration: float = 3.0
    icon: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    opacity: float = 1.0
    y_offset: float = 0.0


class GameOverlay:
    """Game overlay displaying key metrics and notifications.
    
    Features:
    - Resource display (money, energy)
    - Progression bar (XP/level)
    - Game speed controls
    - Active incidents counter
    - Available specialists counter
    - Notification toast system
    - Warning indicators
    - Pause/settings access
    
    The overlay is non-intrusive and provides at-a-glance information
    about game state without requiring player interaction.
    """
    
    # Theme colors
    THEME = {
        "bg": (20, 25, 35),
        "bg_dark": (15, 18, 25),
        "primary": (64, 156, 255),
        "success": (76, 209, 55),
        "warning": (255, 171, 64),
        "error": (255, 82, 82),
        "text": (230, 235, 245),
        "text_dim": (150, 160, 180),
        "border": (50, 60, 80),
        "achievement": (218, 165, 32),
    }
    
    # Layout constants
    BAR_HEIGHT = 60
    NOTIFICATION_WIDTH = 350
    NOTIFICATION_HEIGHT = 80
    NOTIFICATION_SPACING = 10
    PADDING = 12
    
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        show_fps: bool = False,
        show_debug: bool = False
    ):
        """Initialize game overlay.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            show_fps: Whether to show FPS counter
            show_debug: Whether to show debug information
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.show_fps = show_fps
        self.show_debug = show_debug
        
        # Animation system
        self.animations = get_animation_system()
        
        # Fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Notification queue
        self.notifications: list[Notification] = []
        self.max_notifications = 5
        
        # State tracking for animations
        self.money_display = 0
        self.xp_display = 0
        self.energy_display = 0
        
        # Game speed control
        self.speed_options = [0.5, 1.0, 2.0, 4.0]
        self.speed_index = 1  # Default to 1.0x
        
        # Pause state
        self.is_paused = False
        
        # FPS tracking
        self.fps_history: list[float] = []
        self.fps_max_samples = 60
        
        # Interaction rects
        self.pause_button_rect = pygame.Rect(
            screen_width - 120, 10, 50, 40
        )
        self.speed_button_rect = pygame.Rect(
            screen_width - 180, 10, 50, 40
        )
        self.settings_button_rect = pygame.Rect(
            screen_width - 60, 10, 50, 40
        )
        
        # Callbacks
        self.on_pause: Optional[Callable[[], None]] = None
        self.on_speed_change: Optional[Callable[[float], None]] = None
        self.on_settings: Optional[Callable[[], None]] = None
        
    def update(self, delta_time: float, current_fps: float) -> None:
        """Update overlay animations and notifications.
        
        Args:
            delta_time: Time elapsed since last update
            current_fps: Current frames per second
        """
        # Update FPS history
        if self.show_fps:
            self.fps_history.append(current_fps)
            if len(self.fps_history) > self.fps_max_samples:
                self.fps_history.pop(0)
        
        # Update notifications
        current_time = time.time()
        for notification in self.notifications[:]:
            age = current_time - notification.timestamp
            
            # Fade out in last 0.5 seconds
            if age > notification.duration - 0.5:
                fade_progress = (age - (notification.duration - 0.5)) / 0.5
                notification.opacity = 1.0 - fade_progress
            
            # Remove expired notifications
            if age > notification.duration:
                self.notifications.remove(notification)
    
    def add_notification(
        self,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        duration: float = 3.0,
        icon: Optional[str] = None
    ) -> None:
        """Add a notification to the overlay.
        
        Args:
            message: Notification message
            level: Importance level
            duration: How long to display (seconds)
            icon: Optional icon name
        """
        notification = Notification(
            message=message,
            level=level,
            duration=duration,
            icon=icon
        )
        
        self.notifications.append(notification)
        
        # Limit notification count
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        
        # Animate notification entry
        self.animations.animate(
            target=notification,
            property="y_offset",
            start_value=-100.0,
            end_value=0.0,
            duration=0.3,
            easing=EasingFunction.BACK_OUT
        )
    
    def animate_value_change(
        self,
        current: float,
        target: float,
        property_name: str
    ) -> None:
        """Animate a value change with count-up effect.
        
        Args:
            current: Current displayed value
            target: Target value
            property_name: Name of property to animate
        """
        if abs(current - target) > 0.1:
            self.animations.animate(
                target=self,
                property=property_name,
                start_value=current,
                end_value=target,
                duration=0.5,
                easing=EasingFunction.EASE_OUT_QUAD
            )
    
    def render_top_bar(
        self,
        screen: pygame.Surface,
        money: float,
        energy: float,
        max_energy: float,
        xp: float,
        xp_required: float,
        level: int,
        game_speed: float,
        game_time: Optional[str] = None
    ) -> None:
        """Render the top information bar.
        
        Args:
            screen: Surface to render to
            money: Current money
            energy: Current energy
            max_energy: Maximum energy
            xp: Current XP
            xp_required: XP needed for next level
            level: Current level
            game_speed: Current game speed multiplier
            game_time: Optional formatted game time string
        """
        # Animate value changes
        self.animate_value_change(self.money_display, money, "money_display")
        self.animate_value_change(self.xp_display, xp, "xp_display")
        self.animate_value_change(self.energy_display, energy, "energy_display")
        
        # Background bar
        bar_rect = pygame.Rect(0, 0, self.screen_width, self.BAR_HEIGHT)
        pygame.draw.rect(screen, self.THEME["bg"], bar_rect)
        pygame.draw.line(
            screen,
            self.THEME["border"],
            (0, self.BAR_HEIGHT - 1),
            (self.screen_width, self.BAR_HEIGHT - 1),
            2
        )
        
        x_offset = self.PADDING
        
        # Money display
        money_text = f"${int(self.money_display):,}"
        money_surface = self.font_large.render(money_text, True, self.THEME["success"])
        money_label = self.font_small.render("FUNDS", True, self.THEME["text_dim"])
        screen.blit(money_label, (x_offset, 8))
        screen.blit(money_surface, (x_offset, 26))
        x_offset += 160
        
        # Energy bar
        energy_label = self.font_small.render("ENERGY", True, self.THEME["text_dim"])
        screen.blit(energy_label, (x_offset, 8))
        
        energy_bar_rect = pygame.Rect(x_offset, 28, 140, 20)
        pygame.draw.rect(screen, self.THEME["bg_dark"], energy_bar_rect)
        
        energy_percent = self.energy_display / max_energy if max_energy > 0 else 0
        filled_width = int(energy_bar_rect.width * energy_percent)
        
        if filled_width > 0:
            fill_rect = pygame.Rect(
                energy_bar_rect.x,
                energy_bar_rect.y,
                filled_width,
                energy_bar_rect.height
            )
            
            # Color based on energy level
            if energy_percent > 0.7:
                color = self.THEME["success"]
            elif energy_percent > 0.3:
                color = self.THEME["warning"]
            else:
                color = self.THEME["error"]
            
            pygame.draw.rect(screen, color, fill_rect)
        
        pygame.draw.rect(screen, self.THEME["border"], energy_bar_rect, 2)
        
        # Energy text
        energy_text = f"{int(self.energy_display)}/{int(max_energy)}"
        energy_text_surface = self.font_small.render(
            energy_text, True, self.THEME["text"]
        )
        text_rect = energy_text_surface.get_rect(center=energy_bar_rect.center)
        screen.blit(energy_text_surface, text_rect)
        
        x_offset += 160
        
        # XP Progress bar
        xp_label = self.font_small.render(
            f"LEVEL {level}", True, self.THEME["text_dim"]
        )
        screen.blit(xp_label, (x_offset, 8))
        
        xp_bar_rect = pygame.Rect(x_offset, 28, 200, 20)
        pygame.draw.rect(screen, self.THEME["bg_dark"], xp_bar_rect)
        
        xp_percent = self.xp_display / xp_required if xp_required > 0 else 0
        xp_filled_width = int(xp_bar_rect.width * xp_percent)
        
        if xp_filled_width > 0:
            xp_fill_rect = pygame.Rect(
                xp_bar_rect.x,
                xp_bar_rect.y,
                xp_filled_width,
                xp_bar_rect.height
            )
            pygame.draw.rect(screen, self.THEME["primary"], xp_fill_rect)
        
        pygame.draw.rect(screen, self.THEME["border"], xp_bar_rect, 2)
        
        # XP text
        xp_text = f"{int(self.xp_display)}/{int(xp_required)}"
        xp_text_surface = self.font_small.render(xp_text, True, self.THEME["text"])
        xp_text_rect = xp_text_surface.get_rect(center=xp_bar_rect.center)
        screen.blit(xp_text_surface, xp_text_rect)
        
        x_offset += 220
        
        # Game time (if provided)
        if game_time:
            time_label = self.font_small.render("TIME", True, self.THEME["text_dim"])
            screen.blit(time_label, (x_offset, 8))
            
            time_surface = self.font_medium.render(
                game_time, True, self.THEME["text"]
            )
            screen.blit(time_surface, (x_offset, 28))
        
        # Right side controls
        self._render_controls(screen, game_speed)
    
    def _render_controls(self, screen: pygame.Surface, game_speed: float) -> None:
        """Render control buttons (pause, speed, settings).
        
        Args:
            screen: Surface to render to
            game_speed: Current game speed multiplier
        """
        # Settings button
        pygame.draw.rect(
            screen,
            self.THEME["bg_dark"],
            self.settings_button_rect,
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            self.THEME["border"],
            self.settings_button_rect,
            2,
            border_radius=4
        )
        settings_text = self.font_medium.render("⚙", True, self.THEME["text"])
        text_rect = settings_text.get_rect(center=self.settings_button_rect.center)
        screen.blit(settings_text, text_rect)
        
        # Speed button
        pygame.draw.rect(
            screen,
            self.THEME["bg_dark"],
            self.speed_button_rect,
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            self.THEME["border"],
            self.speed_button_rect,
            2,
            border_radius=4
        )
        speed_text = self.font_small.render(
            f"{game_speed:.1f}x", True, self.THEME["primary"]
        )
        text_rect = speed_text.get_rect(center=self.speed_button_rect.center)
        screen.blit(speed_text, text_rect)
        
        # Pause button
        pause_color = self.THEME["warning"] if self.is_paused else self.THEME["border"]
        pygame.draw.rect(
            screen,
            self.THEME["bg_dark"],
            self.pause_button_rect,
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            pause_color,
            self.pause_button_rect,
            2,
            border_radius=4
        )
        pause_symbol = "▶" if self.is_paused else "⏸"
        pause_text = self.font_medium.render(pause_symbol, True, self.THEME["text"])
        text_rect = pause_text.get_rect(center=self.pause_button_rect.center)
        screen.blit(pause_text, text_rect)
    
    def render_secondary_info(
        self,
        screen: pygame.Surface,
        active_incidents: int,
        total_incidents: int,
        available_specialists: int,
        total_specialists: int,
        passive_income: float = 0.0
    ) -> None:
        """Render secondary information panel.
        
        Args:
            screen: Surface to render to
            active_incidents: Number of active incidents
            total_incidents: Total incidents in queue
            available_specialists: Number of available specialists
            total_specialists: Total specialists
            passive_income: Passive income per second
        """
        y_start = self.BAR_HEIGHT + 10
        x_offset = 10
        
        # Incidents counter
        incidents_text = f"📋 {active_incidents}/{total_incidents}"
        incidents_color = (
            self.THEME["error"] if active_incidents > total_incidents * 0.8
            else self.THEME["warning"] if active_incidents > total_incidents * 0.5
            else self.THEME["text"]
        )
        incidents_surface = self.font_small.render(
            incidents_text, True, incidents_color
        )
        
        # Background for info
        info_rect = pygame.Rect(x_offset - 5, y_start - 2, 150, 24)
        pygame.draw.rect(screen, self.THEME["bg"], info_rect, border_radius=4)
        pygame.draw.rect(screen, self.THEME["border"], info_rect, 1, border_radius=4)
        
        screen.blit(incidents_surface, (x_offset, y_start))
        
        x_offset += 160
        
        # Specialists counter
        specialists_text = f"👤 {available_specialists}/{total_specialists}"
        specialists_color = (
            self.THEME["error"] if available_specialists == 0
            else self.THEME["success"]
        )
        specialists_surface = self.font_small.render(
            specialists_text, True, specialists_color
        )
        
        info_rect = pygame.Rect(x_offset - 5, y_start - 2, 150, 24)
        pygame.draw.rect(screen, self.THEME["bg"], info_rect, border_radius=4)
        pygame.draw.rect(screen, self.THEME["border"], info_rect, 1, border_radius=4)
        
        screen.blit(specialists_surface, (x_offset, y_start))
        
        # Passive income (if > 0)
        if passive_income > 0:
            x_offset += 160
            income_text = f"💰 +${passive_income:.1f}/s"
            income_surface = self.font_small.render(
                income_text, True, self.THEME["success"]
            )
            
            info_rect = pygame.Rect(x_offset - 5, y_start - 2, 150, 24)
            pygame.draw.rect(screen, self.THEME["bg"], info_rect, border_radius=4)
            pygame.draw.rect(screen, self.THEME["border"], info_rect, 1, border_radius=4)
            
            screen.blit(income_surface, (x_offset, y_start))
    
    def render_notifications(self, screen: pygame.Surface) -> None:
        """Render notification toasts.
        
        Args:
            screen: Surface to render to
        """
        x_pos = self.screen_width - self.NOTIFICATION_WIDTH - 20
        y_start = self.BAR_HEIGHT + 50
        
        for i, notification in enumerate(self.notifications):
            y_pos = y_start + i * (self.NOTIFICATION_HEIGHT + self.NOTIFICATION_SPACING)
            y_pos += notification.y_offset
            
            # Background
            notif_rect = pygame.Rect(
                x_pos,
                int(y_pos),
                self.NOTIFICATION_WIDTH,
                self.NOTIFICATION_HEIGHT
            )
            
            # Create surface with alpha for fade effect
            notif_surface = pygame.Surface(
                (self.NOTIFICATION_WIDTH, self.NOTIFICATION_HEIGHT),
                pygame.SRCALPHA
            )
            
            # Background color based on level
            bg_color = self.THEME["bg"]
            border_color = {
                NotificationLevel.INFO: self.THEME["primary"],
                NotificationLevel.SUCCESS: self.THEME["success"],
                NotificationLevel.WARNING: self.THEME["warning"],
                NotificationLevel.ERROR: self.THEME["error"],
                NotificationLevel.ACHIEVEMENT: self.THEME["achievement"],
            }[notification.level]
            
            # Apply opacity
            bg_with_alpha = (*bg_color, int(255 * notification.opacity))
            border_with_alpha = (*border_color, int(255 * notification.opacity))
            text_with_alpha = (*self.THEME["text"], int(255 * notification.opacity))
            
            pygame.draw.rect(
                notif_surface,
                bg_with_alpha,
                (0, 0, self.NOTIFICATION_WIDTH, self.NOTIFICATION_HEIGHT),
                border_radius=8
            )
            pygame.draw.rect(
                notif_surface,
                border_with_alpha,
                (0, 0, self.NOTIFICATION_WIDTH, self.NOTIFICATION_HEIGHT),
                3,
                border_radius=8
            )
            
            # Message text (word wrap)
            words = notification.message.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = " ".join(current_line + [word])
                test_surface = self.font_small.render(test_line, True, self.THEME["text"])
                if test_surface.get_width() < self.NOTIFICATION_WIDTH - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(" ".join(current_line))
            
            # Render lines
            text_y = 15
            for line in lines[:3]:  # Max 3 lines
                text_surface = self.font_small.render(line, True, text_with_alpha)
                notif_surface.blit(text_surface, (15, text_y))
                text_y += 20
            
            screen.blit(notif_surface, notif_rect)
    
    def render_fps(self, screen: pygame.Surface) -> None:
        """Render FPS counter.
        
        Args:
            screen: Surface to render to
        """
        if not self.show_fps or not self.fps_history:
            return
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        fps_text = f"FPS: {int(avg_fps)}"
        
        fps_color = (
            self.THEME["success"] if avg_fps >= 55
            else self.THEME["warning"] if avg_fps >= 30
            else self.THEME["error"]
        )
        
        fps_surface = self.font_small.render(fps_text, True, fps_color)
        screen.blit(fps_surface, (10, self.screen_height - 25))
    
    def render(
        self,
        screen: pygame.Surface,
        game_state: Any,
        current_fps: float = 60.0
    ) -> None:
        """Render the complete overlay.
        
        Args:
            screen: Surface to render to
            game_state: Game state object with required attributes
            current_fps: Current frames per second
        """
        # Extract game state (with safe defaults)
        money = getattr(game_state, "money", 0)
        energy = getattr(game_state, "energy", 100)
        max_energy = getattr(game_state, "max_energy", 100)
        xp = getattr(game_state, "xp", 0)
        xp_required = getattr(game_state, "xp_required", 100)
        level = getattr(game_state, "level", 1)
        game_speed = getattr(game_state, "game_speed", 1.0)
        game_time = getattr(game_state, "game_time_formatted", None)
        
        active_incidents = getattr(game_state, "active_incidents_count", 0)
        total_incidents = getattr(game_state, "total_incidents_count", 0)
        available_specialists = getattr(game_state, "available_specialists_count", 0)
        total_specialists = getattr(game_state, "total_specialists_count", 0)
        passive_income = getattr(game_state, "passive_income_rate", 0.0)
        
        # Render components
        self.render_top_bar(
            screen, money, energy, max_energy, xp, xp_required,
            level, game_speed, game_time
        )
        self.render_secondary_info(
            screen, active_incidents, total_incidents,
            available_specialists, total_specialists, passive_income
        )
        self.render_notifications(screen)
        
        if self.show_fps:
            self.render_fps(screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Pause button
            if self.pause_button_rect.collidepoint(mouse_pos):
                self.is_paused = not self.is_paused
                if self.on_pause:
                    self.on_pause()
                return True
            
            # Speed button
            if self.speed_button_rect.collidepoint(mouse_pos):
                self.speed_index = (self.speed_index + 1) % len(self.speed_options)
                new_speed = self.speed_options[self.speed_index]
                if self.on_speed_change:
                    self.on_speed_change(new_speed)
                return True
            
            # Settings button
            if self.settings_button_rect.collidepoint(mouse_pos):
                if self.on_settings:
                    self.on_settings()
                return True
        
        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
                if self.on_pause:
                    self.on_pause()
                return True
            
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                # Speed up
                if self.speed_index < len(self.speed_options) - 1:
                    self.speed_index += 1
                    new_speed = self.speed_options[self.speed_index]
                    if self.on_speed_change:
                        self.on_speed_change(new_speed)
                return True
            
            if event.key == pygame.K_MINUS:
                # Slow down
                if self.speed_index > 0:
                    self.speed_index -= 1
                    new_speed = self.speed_options[self.speed_index]
                    if self.on_speed_change:
                        self.on_speed_change(new_speed)
                return True
        
        return False
    
    def set_pause_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for pause button.
        
        Args:
            callback: Function to call when paused
        """
        self.on_pause = callback
    
    def set_speed_change_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback for speed changes.
        
        Args:
            callback: Function to call with new speed
        """
        self.on_speed_change = callback
    
    def set_settings_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for settings button.
        
        Args:
            callback: Function to call when settings clicked
        """
        self.on_settings = callback
    
    def toggle_fps(self) -> None:
        """Toggle FPS display."""
        self.show_fps = not self.show_fps
    
    def toggle_debug(self) -> None:
        """Toggle debug information."""
        self.show_debug = not self.show_debug
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()
