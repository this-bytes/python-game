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
from src.utils.logger import GameLogger
from src.utils.json_loader import load_game_data
from src.utils.rich_parameter_system import get_parameter_system
from src.utils.screenshot import initialize_screenshot_utility
from src.utils.backend_integration import initialize_backend_integration, connect_to_backend
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

    def __init__(self):
        """Initialize the game."""
        self.logger = GameLogger("main")
        self.game_state: Optional[GameState] = None
        self.ui: Optional[GameUI] = None
        self.system_manager: Optional[SystemManager] = None
        self.running = False

        # Development systems
        self.parameter_system = None
        self.screenshot_utility = None
        self.backend_integration = None

        # Game timing
        self.last_update = time.time()
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps

    def initialize(self) -> bool:
        """Initialize all game systems.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.logger.info("[GAME] Initializing Cybersecurity Firm Game...")

            # Load game data
            self.logger.logger.info("[GAME] Loading game configuration...")
            game_data = load_game_data()

            # Initialize game state with default values (will load initial data automatically)
            self.logger.logger.info("[GAME] Initializing game state...")
            self.game_state = GameState()

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
            self.logger.logger.info("[GAME] Game initialization complete!")

            return True

        except Exception as e:
            self.logger.logger.error(f"[GAME] Failed to initialize game: {e}")
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

        except KeyboardInterrupt:
            self.logger.logger.info("[GAME] Game interrupted by user")
        except Exception as e:
            self.logger.logger.error(f"[GAME] Unexpected error in game loop: {e}")
        finally:
            self.shutdown()

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

        # Shutdown plugins/systems first
        if self.system_manager and self.game_state:
            self.logger.logger.info("[GAME] Shutting down all game systems...")
            self.system_manager.shutdown_all(self.game_state)

        if self.backend_integration:
            self.backend_integration.disconnect()

        if self.ui:
            self.ui.shutdown()

        pygame.quit()
        self.logger.logger.info("[GAME] Game shutdown complete")


def main():
    """Main entry point."""
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")

    # Create and run game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
