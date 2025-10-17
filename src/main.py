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


class Game:
    """Main game class coordinating all systems."""

    def __init__(self):
        """Initialize the game."""
        self.logger = GameLogger("main")
        self.game_state: Optional[GameState] = None
        self.ui: Optional[GameUI] = None
        self.running = False

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

                # Update game state
                if self.game_state:
                    self.game_state.update(delta_time)

                # Update UI
                if self.ui:
                    actions = self.ui.handle_input(events)
                    self.ui.update(delta_time)

                    # Process any game actions from UI
                    for action in actions:
                        self._handle_game_action(action)

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
