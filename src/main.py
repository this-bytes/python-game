"""Main entry point for the Cybersecurity Firm Game.

This module initializes and runs the game, coordinating between the game logic,
user interface, and optional backend services.
"""

import sys
import time
import pygame
import os
from typing import Optional

# Add parent directory to path so src imports work
sys.path.insert(0, '/home/localadmin/code/python-game')

# Change to project root directory so relative paths work
# os.chdir('/home/localadmin/code/python-game')

from src.models.game_state import GameState
from src.ui.game_ui import GameUI
from src.ui.main_menu import MainMenu, MenuAction
from src.utils.logger import GameLogger
from src.utils.json_loader import load_game_data
from src.utils.rich_parameter_system import get_parameter_system
from src.utils.screenshot import initialize_screenshot_utility
from src.utils.backend_integration import initialize_backend_integration, connect_to_backend
from src.utils.game_args import parse_game_args, GameMode, GameArgs
from src.core.save_manager import SaveManager
from src.core.system_manager import SystemManager
from src.core.plugins.idle_plugin import IdlePlugin
from src.core.plugins.prestige_plugin import PrestigeSystem
from src.core.plugins.achievement_plugin import AchievementSystem
from src.core.plugins.burnout_plugin import BurnoutPlugin
from src.core.plugins.relationships_plugin import RelationshipsPlugin
from src.core.plugins.dopamine_plugin import DopaminePlugin
from src.core.plugins.equipment_plugin import EquipmentPlugin
from src.core.plugins.ability_plugin import AbilityPlugin
from src.core.plugins.passive_income_plugin import PassiveIncomePlugin
from src.core.plugins.facility_plugin import FacilityPlugin


class Game:
    """Main game class coordinating all systems.
    
    Supports both UI and headless modes through optional UI initialization.
    Backend integration is optional and enables live debugging/manipulation.
    """

    def __init__(self, args: GameArgs):
        """Initialize the game.
        
        Args:
            args: Parsed game arguments for initialization
        """
        self.logger = GameLogger("main")
        self.args = args
        self.game_state: Optional[GameState] = None
        self.ui: Optional[GameUI] = None
        self.main_menu: Optional[MainMenu] = None
        self.system_manager: Optional[SystemManager] = None
        self.save_manager: Optional[SaveManager] = None
        self.running = False

        # Development systems
        self.parameter_system = None
        self.screenshot_utility = None
        self.backend_integration = None

        # Game timing
        self.last_update = time.time()
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        
        # Menu state
        self.in_menu = args.should_show_menu()
        self.menu_action: Optional[MenuAction] = None

    def initialize(self) -> bool:
        """Initialize all game systems.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.logger.info("[GAME] Initializing Cybersecurity Firm Game...")

            # Initialize save manager first
            self.logger.logger.info("[GAME] Initializing save manager...")
            self.save_manager = SaveManager()
            
            # Check if we should show menu or load game directly
            if self.args.should_show_menu():
                self.logger.logger.info("[GAME] Starting in menu mode...")
                self._initialize_menu()
                return True
            elif self.args.should_load_game():
                self.logger.logger.info("[GAME] Loading saved game...")
                return self._initialize_from_save()
            else:
                # New game
                self.logger.logger.info("[GAME] Starting new game...")
                return self._initialize_new_game()

        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize game: {e}")
            return False
    
    def _initialize_menu(self) -> bool:
        """Initialize the main menu.
        
        Returns:
            True if menu initialized successfully
        """
        try:
            # Initialize Pygame if not already done
            if not pygame.get_init():
                pygame.init()
            
            # Create main menu
            self.main_menu = MainMenu()
            
            # Check if continue is available (slot 0 = auto-save)
            saves = self.save_manager.list_saves()
            auto_save = saves[0] if saves else None
            continue_available = auto_save and auto_save.get('exists', False)
            
            self.main_menu.set_continue_available(continue_available)
            
            self.in_menu = True
            self.running = True
            
            self.logger.logger.info("[GAME] Main menu initialized")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize menu: {e}")
            return False
    
    def _initialize_from_save(self) -> bool:
        """Initialize game from a saved state.
        
        Returns:
            True if load successful
        """
        try:
            # Determine which slot to load
            if self.args.mode == GameMode.CONTINUE:
                # Load most recent save (auto-save slot 0)
                slot = 0
            else:
                # Load specific slot
                slot = self.args.save_slot
            
            self.logger.logger.info(f"[GAME] Loading game from slot {slot}...")
            
            # Load game state
            self.game_state = self.save_manager.load_game(slot)
            
            # Initialize UI and systems with loaded state
            return self._initialize_game_systems()
            
        except FileNotFoundError:
            self.logger.logger.error("[GAME] Save file not found")
            # Fall back to new game
            self.logger.logger.info("[GAME] Starting new game instead...")
            return self._initialize_new_game()
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to load save: {e}")
            return False
    
    def _initialize_new_game(self) -> bool:
        """Initialize a new game.
        
        Returns:
            True if initialization successful
        """
        try:
            # Load game data
            self.logger.logger.info("[GAME] Loading game configuration...")
            game_data = load_game_data()

            # Initialize game state with default values
            self.logger.logger.info("[GAME] Initializing game state...")
            self.game_state = GameState()
            
            # Initialize UI and systems
            return self._initialize_game_systems()
            
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize new game: {e}")
            return False
    
    def _initialize_game_systems(self) -> bool:
        """Initialize UI and game systems (common for both new and loaded games).
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize UI
            self.logger.logger.info("[GAME] Initializing user interface...")
            self.ui = GameUI(self.game_state)

            # Initialize plugin architecture (SystemManager)
            self.logger.logger.info("[GAME] Initializing plugin architecture...")
            self.system_manager = SystemManager()
            
            # Register game systems as plugins
            self.logger.logger.info("[GAME] Registering game systems...")
            self.system_manager.register_system(IdlePlugin())
            self.system_manager.register_system(PrestigeSystem())
            self.system_manager.register_system(AchievementSystem())
            self.system_manager.register_system(BurnoutPlugin())
            self.system_manager.register_system(RelationshipsPlugin())
            self.system_manager.register_system(DopaminePlugin())
            self.system_manager.register_system(EquipmentPlugin())
            self.system_manager.register_system(AbilityPlugin())
            self.system_manager.register_system(PassiveIncomePlugin())
            self.system_manager.register_system(FacilityPlugin())
            
            # Initialize all registered systems
            self.logger.logger.info("[GAME] Initializing all systems...")
            self.system_manager.initialize_all(self.game_state)

            # Initialize development systems
            self.logger.logger.info("[GAME] Initializing development systems...")
            self.parameter_system = get_parameter_system()
            self.parameter_system.set_logger(self.logger)

            if self.ui and self.game_state:
                self.screenshot_utility = initialize_screenshot_utility(
                    self.ui, self.game_state, self.logger
                )

            # Initialize backend integration
            self.logger.logger.info("[GAME] Initializing backend integration...")
            self.backend_integration = initialize_backend_integration(logger=self.logger)

            # Try to connect to backend if available
            if self.game_state and self.backend_integration:
                backend_connected = connect_to_backend(self.game_state)
                if backend_connected:
                    self.logger.logger.info("[GAME] Backend integration connected")
                else:
                    self.logger.logger.info("[GAME] Backend not available, running standalone")

            # Start the game
            self.running = True
            self.in_menu = False
            self.logger.logger.info("[GAME] Game systems initialization complete!")

            return True
            
        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize game systems: {e}")
            return False

    def run(self) -> None:
        """Run the main game loop."""
        if not self.initialize():
            self.logger.logger.error("[GAME] Game initialization failed. Exiting.")
            sys.exit(1)

        self.logger.logger.info("[GAME] Starting main game loop...")

        try:
            while self.running:
                current_time = time.time()
                delta_time = current_time - self.last_update

                # Limit frame rate
                if delta_time < self.frame_time:
                    time.sleep(self.frame_time - delta_time)
                    continue

                self.last_update = current_time

                # Handle events
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                        break

                # Handle menu or game
                if self.in_menu:
                    self._run_menu(events, delta_time)
                else:
                    self._run_game(events, delta_time)

        except KeyboardInterrupt:
            self.logger.logger.info("[GAME] Game interrupted by user")
        except Exception as e:
            self.logger.logger.error(f"[GAME] Unexpected error in game loop: {e}")
        finally:
            self.shutdown()
    
    def _run_menu(self, events, delta_time: float) -> None:
        """Run the menu loop.
        
        Args:
            events: Pygame events
            delta_time: Time since last update
        """
        if not self.main_menu:
            return
        
        # Handle menu input
        action = self.main_menu.handle_input(events)
        
        if action == MenuAction.EXIT:
            self.running = False
            return
        elif action == MenuAction.NEW_GAME:
            self.logger.logger.info("[GAME] Starting new game from menu...")
            if self._initialize_new_game():
                self.in_menu = False
        elif action == MenuAction.CONTINUE:
            self.logger.logger.info("[GAME] Continuing game from menu...")
            if self._initialize_from_save():
                self.in_menu = False
        elif action == MenuAction.SETTINGS:
            self.main_menu.show_settings_menu()
        
        # Update and render menu
        self.main_menu.update(delta_time)
        self.main_menu.render()
    
    def _run_game(self, events, delta_time: float) -> None:
        """Run the game loop.
        
        Args:
            events: Pygame events
            delta_time: Time since last update
        """
        # Update game state and plugins
        if self.game_state:
            self.game_state.update(delta_time)
            
            # Update all registered plugins/systems
            if self.system_manager:
                self.system_manager.update_all(self.game_state, delta_time)

        # Update UI
        if self.ui:
            actions = self.ui.handle_input(events)
            self.ui.update(delta_time)

            # Process any game actions from UI
            for action in actions:
                self._handle_game_action(action)

        # Update development systems
        if self.screenshot_utility:
            self.screenshot_utility.update(delta_time)

        # Update backend integration
        # Backend integration runs in background thread, no per-frame update needed

        # Render
        if self.ui:
            self.ui.render()

        pygame.display.flip()

    def _handle_game_action(self, action) -> None:
        """Handle game actions from the UI.

        Args:
            action: The action to process
        """
        # This will be expanded as we implement more UI interactions
        # For now, just log the action
        self.logger.logger.debug(f"[GAME] Processing action: {action}")

    def shutdown(self) -> None:
        """Clean shutdown of all systems."""
        self.logger.logger.info("[GAME] Shutting down...")
        
        # Auto-save before shutdown (if we have a game state)
        if self.game_state and self.save_manager and not self.in_menu:
            try:
                self.logger.logger.info("[GAME] Auto-saving game...")
                self.save_manager.auto_save(self.game_state)
            except Exception as e:
                self.logger.logger.error(f"[GAME] Auto-save failed: {e}")

        # Shutdown plugins/systems first
        if self.system_manager and self.game_state:
            self.logger.logger.info("[GAME] Shutting down all game systems...")
            self.system_manager.shutdown_all(self.game_state)

        if self.backend_integration:
            self.backend_integration.disconnect()
        
        if self.main_menu:
            self.main_menu.shutdown()

        if self.ui:
            self.ui.shutdown()

        pygame.quit()
        self.logger.logger.info("[GAME] Game shutdown complete")


def main():
    """Main entry point."""
    # Parse command-line arguments
    args = parse_game_args()
    
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")

    # Create and run game
    game = Game(args)
    game.run()


if __name__ == "__main__":
    main()
