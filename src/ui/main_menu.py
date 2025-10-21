"""Main menu UI for game startup.

This module provides the initial menu screen with options to start a new game,
continue from a save, access settings, or exit.
"""

import pygame
from typing import Optional, Tuple, List
from enum import Enum

from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.components.button import Button, ButtonStyle


class MenuAction(Enum):
    """Actions that can be triggered from the main menu."""
    NEW_GAME = "new_game"
    CONTINUE = "continue"
    TUTORIAL = "tutorial"
    SETTINGS = "settings"
    EXIT = "exit"
    LOAD_SLOT = "load_slot"


class MainMenu:
    """Main menu UI component.
    
    Displays menu options and handles user interaction.
    Uses Pygame for rendering but contains no game logic.
    """
    
    def __init__(self, width: int = 1280, height: int = 720):
        """Initialize the main menu.
        
        Args:
            width: Window width
            height: Window height
        """
        self.logger = GameLogger("main_menu")
        self.width = width
        self.height = height
        
        # Initialize Pygame (if not already initialized)
        if not pygame.get_init():
            pygame.init()
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cybersecurity Firm - Main Menu")
        
        # Clear any events generated during initialization (only if pygame initialized)
        if pygame.get_init():
            try:
                pygame.event.get()
            except Exception:
                # In test environments pygame may be mocked; ignore errors
                pass
        
        # Theme and styling
        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_current_theme()
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24)
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Menu state
        self.selected_action: Optional[MenuAction] = None
        self.selected_save_slot: Optional[int] = None
        self.continue_available = False  # Will be set based on save availability
        
        # Create menu buttons
        self._create_buttons()
        
        # Animation state
        self.pulse_offset = 0.0
        
        self.logger.info("[MAIN_MENU] Main menu initialized")
    
    def _create_buttons(self) -> None:
        """Create menu buttons."""
        button_width = 400
        button_height = 60
        button_spacing = 20
        
        # Center buttons vertically (5 buttons now)
        total_height = (5 * button_height) + (4 * button_spacing)
        start_y = (self.height - total_height) // 2 + 80
        
        center_x = self.width // 2
        button_x = center_x - (button_width // 2)
        
        # Create buttons
        self.new_game_button = Button(
            text="🎮 Start New Game",
            position=(button_x, start_y),
            size=(button_width, button_height),
            callback=lambda: None,  # Callback handled by handle_input
            style=ButtonStyle.PRIMARY
        )
        
        self.continue_button = Button(
            text="▶️ Continue",
            position=(button_x, start_y + button_height + button_spacing),
            size=(button_width, button_height),
            callback=lambda: None,
            style=ButtonStyle.SUCCESS,
            enabled=False  # Initially disabled until we check for saves
        )
        
        self.tutorial_button = Button(
            text="📚 Tutorial",
            position=(button_x, start_y + (2 * button_height) + (2 * button_spacing)),
            size=(button_width, button_height),
            callback=lambda: None,
            style=ButtonStyle.PRIMARY
        )
        
        self.settings_button = Button(
            text="⚙️ Settings",
            position=(button_x, start_y + (3 * button_height) + (3 * button_spacing)),
            size=(button_width, button_height),
            callback=lambda: None,
            style=ButtonStyle.SECONDARY
        )
        
        self.exit_button = Button(
            text="❌ Exit",
            position=(button_x, start_y + (4 * button_height) + (4 * button_spacing)),
            size=(button_width, button_height),
            callback=lambda: None,
            style=ButtonStyle.DANGER
        )
        
        self.buttons = [
            self.new_game_button,
            self.continue_button,
            self.tutorial_button,
            self.settings_button,
            self.exit_button
        ]
    
    def set_continue_available(self, available: bool) -> None:
        """Set whether the continue option is available.
        
        Args:
            available: True if a save exists to continue from
        """
        self.continue_available = available
        self.continue_button.set_enabled(available)
    
    def handle_input(self, events: List[pygame.event.Event]) -> Optional[MenuAction]:
        """Handle user input events.
        
        Args:
            events: List of pygame events
            
        Returns:
            MenuAction if a menu option was selected, None otherwise
        """
        for event in events:
            if event.type == pygame.QUIT:
                return MenuAction.EXIT
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MenuAction.EXIT
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Enter starts new game or continues
                    if self.continue_available:
                        return MenuAction.CONTINUE
                    return MenuAction.NEW_GAME
            
            # Handle button clicks only on mouse up events
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.new_game_button.handle_event(event):
                    self.logger.info("[MAIN_MENU] New game selected")
                    return MenuAction.NEW_GAME
                
                if self.continue_button.handle_event(event):
                    if self.continue_available:
                        self.logger.info("[MAIN_MENU] Continue selected")
                        return MenuAction.CONTINUE
                
                if self.tutorial_button.handle_event(event):
                    self.logger.info("[MAIN_MENU] Tutorial selected")
                    return MenuAction.TUTORIAL
                
                if self.settings_button.handle_event(event):
                    self.logger.info("[MAIN_MENU] Settings selected")
                    return MenuAction.SETTINGS
                
                if self.exit_button.handle_event(event):
                    self.logger.info("[MAIN_MENU] Exit selected")
                    return MenuAction.EXIT
            else:
                # Still handle mouse motion for hover effects
                self.new_game_button.handle_event(event)
                self.continue_button.handle_event(event)
                self.tutorial_button.handle_event(event)
                self.settings_button.handle_event(event)
                self.exit_button.handle_event(event)
        
        return None
    
    def update(self, delta_time: float) -> None:
        """Update menu animations.
        
        Args:
            delta_time: Time since last update in seconds
        """
        # Update pulse animation for title
        self.pulse_offset += delta_time * 2.0
    
    def render(self) -> None:
        """Render the main menu."""
        # Clear screen with dark background
        bg_color = (20, 20, 30)  # Default fallback
        if self.theme:
            bg_color = self.theme.get_color('background', (20, 20, 30))
        self.screen.fill(bg_color)
        
        # Render title with pulse effect
        title_text = "🔒 Cybersecurity Firm"
        pulse_scale = 1.0 + (0.02 * abs(pygame.math.Vector2(1, 0).rotate(self.pulse_offset * 50).x))
        
        # Create title with gradient effect
        title_surface = self.title_font.render(title_text, True, (100, 200, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Idle • Tycoon • RPG"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, (150, 150, 180))
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, 210))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Render buttons
        for button in self.buttons:
            button.render(self.screen)
        
        # Version info
        version_text = "v0.2.0"
        version_surface = self.small_font.render(version_text, True, (100, 100, 120))
        version_rect = version_surface.get_rect(bottomright=(self.width - 20, self.height - 10))
        self.screen.blit(version_surface, version_rect)
        
        # Hint text
        if self.continue_available:
            hint_text = "Press ENTER to continue your game"
        else:
            hint_text = "Press ENTER to start a new game"
        hint_surface = self.small_font.render(hint_text, True, (120, 120, 140))
        hint_rect = hint_surface.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(hint_surface, hint_rect)
        
        # Update display
        pygame.display.flip()
    
    def show_settings_menu(self) -> None:
        """Show settings menu (placeholder for future implementation).
        
        This is a placeholder that will be expanded in the future with
        actual settings options like audio, graphics, controls, etc.
        """
        self.logger.info("[MAIN_MENU] Settings menu - not yet implemented")
        # For now, just log that settings was accessed
        # Future: Create a SettingsMenu class similar to MainMenu
    
    def shutdown(self) -> None:
        """Clean up menu resources."""
        self.logger.info("[MAIN_MENU] Main menu shutdown")
